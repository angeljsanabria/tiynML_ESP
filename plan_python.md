# Plan Python — copia reducida de tiynML_ESP

Copia de trabajo de [plan.md](plan.md). Recorre en la PC la cadena del clasificador y deja, en cada etapa, un archivo o un parámetro que el plan original consume tal cual.

El firmware, la placa, FreeRTOS, I2S, DMA y PSRAM se implementan en [plan.md](plan.md). Esta copia descubre las librerías del proyecto completo, fija las que producen los artefactos de entrenamiento y anota la contraparte que después corre en el ESP32-P4.

**Aplicación:** clasificar eventos acústicos con el mismo contrato de datos del sistema embebido.  
**Audio:** PCM mono, 16 bits con signo, little-endian, 16 000 Hz.  
**Entorno:** conda, nombre `tinyml`, Python 3.12.  
**Clases iniciales:** palmas, golpes sobre una mesa y ruido ambiente.

El trabajo avanza por etapas. Cada etapa produce un resultado verificable. Una librería entra en el entorno si su salida es un archivo que [plan.md](plan.md) va a leer, o si queda marcada como herramienta solo de PC y el contrato que viaja es ese archivo.

---

## 1. Objetivo

Probar en Python el recorrido desde una grabación hasta una etiqueta con confianza, con las mismas cifras que después usa el firmware:

1. Crear el entorno conda `tinyml` con Python 3.12, y fijar ahí las versiones y el rol de cada librería.
2. Grabar PCM y definir el comando de duración en un layout que una struct C puede copiar.
3. Decidir si la toma sirve.
4. Armar el dataset y una línea de base que se queda en la PC.
5. Elegir la representación con operaciones que `esp-dsp` y unas tablas estáticas pueden repetir.
6. Entrenar el modelo que se puede exportar.
7. Cuantizarlo al archivo que el runtime del ESP32 va a cargar.
8. Clasificar por ventanas, en cantidades de muestras, con los contadores del plan completo.
9. Medir el conjunto de prueba y listar los archivos que pasan a [plan.md](plan.md).

## 2. Librerías del proyecto completo

La etapa 0 escribe la versión real de cada una. Esta tabla fija el rol, para descubrirlas con un destino y no como una pila paralela.

| Librería | Dónde corre | Qué produce para el plan original | Contraparte en el ESP32-P4 |
| --- | --- | --- | --- |
| NumPy | PC | Ventana de Hann, FFT, espectro de potencia, banco Mel o DCT, y los vectores de cada paso | `esp-dsp` para la ventana de Hann y la FFT. El banco Mel y la DCT viajan como tablas estáticas |
| TensorFlow / Keras | PC | Modelo entrenado, conversión y el `.tflite` cuantizado a enteros de 8 bits | El runtime que cierra la etapa 7 de [plan.md](plan.md): ESP-TFLite-Micro, o el camino de código C con `esp-nn` |
| scikit-learn | PC | Regresión logística o SVM de referencia | Ninguna. El número de esa línea de base se compara; el archivo no se carga en el microcontrolador |
| SoundFile y SoundDevice | PC | WAV y `.raw` int16, y la grabación desde el micrófono de la PC | El I2S/PDM de la placa produce el mismo PCM int16 |
| Matplotlib | PC | Figuras para aceptar o rechazar tomas | En el plan completo la revisión visual sigue en Audacity y en el espectrograma ASCII |
| ESP-IDF, FreeRTOS, `esp-dsp`, `esp-nn`, ESP-TFLite-Micro | Firmware | No se instalan en esta copia | Se anotan en la etapa 0 con el rol que ya les da [plan.md](plan.md), para reconocerlas cuando se abra el firmware |

NumPy es la implementación de referencia de las características. La etapa 4 guarda sus salidas, y la etapa 8 de [plan.md](plan.md) compara el C contra esos vectores. Otra librería de audio puede usarse para mirar una figura, y esa comparación se anota aparte. Los vectores que el firmware tiene que reproducir son los de NumPy.

El intérprete de TensorFlow Lite en la PC ejecuta el mismo `.tflite` que después se enlaza en el proyecto ESP-IDF. Sirve para medir el archivo, no para reemplazar el runtime de la placa.

## 3. Contrato que el firmware reutiliza

Estos son los resultados que tienen que salir de Python con el formato indicado. Si una etapa cambia un número de esta lista, se actualiza el archivo y se anota la etapa de [plan.md](plan.md) que lo lee.

| Resultado | Formato | Lo lee |
| --- | --- | --- |
| Entorno conda `tinyml` con Python 3.12, y las versiones de las librerías de la tabla | `python/docs/environment.md` | Etapa 0 de [plan.md](plan.md), como la mitad Python de `docs/environment.md` |
| Audio de una toma | `.raw` PCM mono, int16, little-endian, 16 000 Hz, y el WAV equivalente | Etapas 2 y 3 de [plan.md](plan.md). El tamaño del bloque es `16000 * 2 * X` bytes, el mismo cálculo del búfer en PSRAM |
| Comando de grabación | Layout escrito en `python/docs/command_layout.md` y volcado en una struct C empaquetada, little-endian, con anchos explícitos | Etapa 1 de [plan.md](plan.md): el parser UART usa esa struct |
| Tomas y particiones | Grabaciones etiquetadas. Las ventanas de una misma toma quedan en una sola partición | Etapas 4 y 11 de [plan.md](plan.md) |
| Parámetros de características | Frecuencia, muestras por ventana, muestras de salto, longitud de FFT, bandas, fórmula de int16 a float y normalización | Etapas 5 y 8 de [plan.md](plan.md) |
| Tablas de Mel y, si aplica, de DCT | `.npy` y un `.h` con arreglos `float` en orden de fila | Etapa 8 de [plan.md](plan.md): el C multiplica por esas tablas |
| Vectores de prueba | PCM en `.raw` int16 y la salida de cada paso en un `.h` | Etapa 8 de [plan.md](plan.md) |
| Modelo | Archivo Keras en float y `.tflite` int8, con forma, escala y cero de la entrada y de la salida | Etapa 7 de [plan.md](plan.md) |
| Métricas de la PC | Informe con el conjunto de prueba, float y cuantizado por separado | Etapa 11 de [plan.md](plan.md), como la columna de referencia antes de medir la placa |

La longitud de la FFT es potencia de 2. `esp-dsp` calcula la FFT radix-2, y 30 ms a 16 000 Hz son 480 muestras, que no lo son. La etapa 4 parte de una ventana de análisis de 30 ms y elige la potencia de 2 con la que esa ventana entra a la FFT (por ejemplo, 512 con relleno de ceros). Quedan anotadas las dos cifras: muestras de la ventana y longitud de la FFT. El nombre de la función de `esp-dsp` se confirma con la versión de la librería cuando arranque el firmware.

El salto y la ventana se guardan en muestras, además de en milisegundos. El firmware cuenta muestras.

La fórmula que pasa de int16 a float se escribe una sola vez en los parámetros. El entrenamiento, la cuantización y el C de la etapa 8 de [plan.md](plan.md) usan esa fórmula.

## 4. Correspondencia con el plan completo

| Etapa Python | Etapas de plan.md | Qué queda listo |
| --- | --- | --- |
| 0 | 0 | Entorno conda `tinyml` con Python 3.12, versiones y rol de cada librería |
| 1 | 1 y 2 | Struct del comando y PCM de `16000 * 2 * X` bytes |
| 2 | 3 | Criterio de aceptación y tomas válidas |
| 3 | 4 | Dataset, particiones y métrica de la línea de base |
| 4 | 5 y la referencia de la 8 | Representación, tablas y vectores |
| 5 | 6 | Modelo Keras elegido, dentro del conjunto de operadores exportable |
| 6 | 7, parte de PC | `.tflite` int8 medido en la PC |
| 7 | 8, 9 y 10, parte lógica | Lazo por ventanas, tamaño de bloque en muestras y contadores |
| 8 | 11, parte de PC | Métricas del conjunto de prueba y lista de archivos |

La meta de precisión superior al 85 % se mide en la etapa 8, sobre el conjunto de prueba. Los tiempos de la PC se guardan como referencia de esta máquina. La meta de inferencia por debajo de 30 ms se mide en la FireBeetle, en la etapa 11 de [plan.md](plan.md).

## 5. Principios

1. Comprender la teoría de la etapa antes de implementar.
2. Escribir la hipótesis antes del experimento.
3. Separar entrenamiento, validación y prueba. Las ventanas de una misma grabación permanecen en una sola partición.
4. Guardar configuración, semilla, versiones y métricas de cada experimento.
5. Validar cada etapa con entradas y salidas conocidas.
6. Volver a medir el modelo después de cuantizarlo.
7. Medir antes de cambiar el modelo o los parámetros. Cada cambio se evalúa solo, contra el mismo protocolo.
8. Documentar el resultado obtenido y la meta por separado.
9. Cerrar cada etapa con el archivo de la sección 3 que le corresponde. El firmware lee ese archivo, no el script.

## 6. Metodología

Cada etapa cierra con cuatro piezas:

- **Teoría:** lo que hay que poder explicar.
- **Ejemplo:** una operación matemática o una toma corta, vista completa.
- **Práctica:** script reproducible.
- **Validación:** prueba, métrica y nota de lo observado.

El criterio de salida es una comprobación sobre datos, con el script y el archivo de la sección 3 guardados.

## 7. Secuencia

| Etapa | Trabajo | Depende de |
| --- | --- | --- |
| 0 | Entorno conda `tinyml` con Python 3.12, versiones y rol de cada librería | — |
| 1 | Comando de grabación y PCM de X segundos | 0 |
| 2 | Inspección de la toma y criterio de aceptación | 1 |
| 3 | Tres clases, particiones y línea de base | 2 |
| 4 | Características, tablas y vectores | 3 |
| 5 | Línea de base, MLP y CNN; modelo exportable | 4 |
| 6 | Cuantización int8 y comparación de predicciones | 5 |
| 7 | Bucle por ventanas, búfer y contadores | 4, 6 |
| 8 | Evaluación del conjunto de prueba e informe | 7 |

## 8. Etapas

### Etapa 0. Entorno y librerías

**Trabajo.**

0. Crear el entorno conda `tinyml` con Python 3.12 y activarlo. Todo lo que sigue de esta copia corre dentro de ese entorno.

```text
conda create -n tinyml python=3.12
conda activate tinyml
python --version
```

`python --version` tiene que informar 3.12. Anotar en `python/docs/environment.md` el nombre del entorno, el gestor (conda) y la versión de Python.

1. Instalar en `tinyml` NumPy, Matplotlib, SoundFile, SoundDevice, scikit-learn y TensorFlow. Fijar las versiones en `python/docs/environment.md`. Para cada librería, anotar la versión, el archivo que produce y la fila que le corresponde en la sección 2. En el mismo archivo, anotar el rol de ESP-IDF, FreeRTOS, `esp-dsp`, `esp-nn` y ESP-TFLite-Micro, con la versión en blanco hasta que la etapa 0 de [plan.md](plan.md) la complete.
2. Comprobar que un script mínimo, ejecutado con el `python` de `tinyml`, lee un WAV y muestra su frecuencia de muestreo, el número de canales y la cantidad de muestras.

**Teoría.**

- El entrenamiento y esta inferencia de prueba ocurren en la PC. El microcontrolador ejecutará después la inferencia con los parámetros ya aprendidos.
- Cadena que esta copia reproduce: muestras PCM, búfer, preprocesamiento, modelo, etiqueta y confianza.
- Una ventana de audio es el ejemplo que ve el modelo. La grabación completa es la fuente de esas ventanas.
- SoundDevice y Matplotlib no viajan al microcontrolador. Viajan el `.raw` y el criterio con el que la toma fue aceptada.

**Criterio de salida.** Con `tinyml` activado, `python --version` informa 3.12 y el script lee un WAV. `python/docs/environment.md` tiene el nombre del entorno, Python 3.12 y las versiones y los roles de las librerías.

### Etapa 1. Comando y captura

Equivale al disparo de grabación y al formato de la captura. El comando se empaqueta en Python con el mismo layout que la struct C de la etapa 1 de [plan.md](plan.md). El micrófono de la PC, o un WAV ya grabado, ocupa el lugar del micrófono PDM.

**Teoría.**

- Frecuencia de muestreo, cuantización, rango dinámico, clipping, Nyquist y aliasing.
- Relación entre duración, frecuencia de muestreo y cantidad de muestras: `16000 * X` muestras y `16000 * 2 * X` bytes.
- PCM con signo de 16 bits guarda cada muestra en dos bytes, little-endian, en el rango −32768 a 32767.
- El reloj PDM de la placa y esta frecuencia PCM son magnitudes distintas. Aquí solo existe la frecuencia PCM.

**Trabajo.**

1. Definir el comando con dos campos: identificador de orden y duración de la grabación. Elegir anchos enteros sin signo. Documentar orden, tamaño y endianness en `python/docs/command_layout.md`. Incluir en ese documento la struct C empaquetada equivalente. Un script empaqueta los bytes y otro los recupera. La duración recuperada es la que dispara la grabación.
2. Grabar X segundos desde el micrófono de la PC, o aceptar un WAV externo y convertirlo al contrato.
3. Guardar dos archivos de la misma toma: WAV y `.raw` PCM crudo, mono, 16 bits con signo, little-endian, 16 000 Hz.
4. Comprobar la frecuencia, el número de canales, la duración y que la cantidad de bytes del `.raw` coincida con `16000 * 2 * X`.

**Validación.** Para una duración conocida, el número de muestras leídas es el esperado. Un seno corto generado por NumPy, guardado y vuelto a leer, coincide con el seno original dentro de la resolución de 16 bits. El empaquetado del comando, leído con la struct documentada, devuelve la misma orden y la misma duración.

**Criterio de salida.** Hay al menos una toma real en WAV y en RAW, y `command_layout.md` tiene la struct que el parser UART va a copiar.

### Etapa 2. Firma acústica

**Trabajo.**

1. Graficar la forma de onda y el histograma de amplitudes.
2. Contar muestras en clipping y la fracción de silencio.
3. Calcular y graficar un espectrograma.
4. Reproducir la toma.

**Lectura de validación.**

- Un golpe o una palmada se reconoce al escuchar. Estática continua deja la toma fuera del conjunto de entrenamiento.
- El silencio se ve uniforme en el espectrograma. Una palmada o un golpe aparece como una barra vertical breve. El ruido ambiente se ve estable a lo largo del tiempo.

**Entregables.** `python/docs/audio_capture.md`, las figuras y la lista de tomas aceptadas y rechazadas, con el motivo. Esa lista es la que la etapa 3 de [plan.md](plan.md) puede volver a escuchar en Audacity sobre los mismos `.raw`.

**Criterio de salida.** Queda un criterio escrito de aceptación y un grupo de tomas que lo cumple.

### Etapa 3. Dataset y línea de base

**Teoría.**

- Clasificación supervisada: \(f_\theta(x) \rightarrow y\). \(x\) son las características, \(y\) la clase y \(\theta\) los parámetros aprendidos.
- Ejemplo, característica y etiqueta. Particiones de entrenamiento, validación y prueba.
- Sobreajuste, subajuste y fuga entre particiones.
- Accuracy, precision, recall, F1 y matriz de confusión. La métrica principal depende del costo de cada error.

**Conjunto.** Tres clases: palmas, golpes sobre una mesa y ruido ambiente. El conjunto queda cerrado por escrito antes de etiquetar. El tecleo y otros sonidos de escucha permanecen fuera de estas tres clases hasta que se reabra el conjunto y se rehacen las particiones.

**Práctica.**

1. Etiquetar cada grabación aceptada con una sola clase.
2. Partir por grabación, de modo que todas las ventanas de una toma caigan en la misma partición.
3. Entrenar con scikit-learn una regresión logística o un SVM. Ese modelo es la línea de base. Su métrica se guarda. Su archivo no sigue hacia la cuantización ni hacia el firmware.
4. Revisar los errores de validación uno por uno.

**Entregables.** `python/data/`, descripción del dataset, manifiesto de particiones y un informe corto de la línea de base.

**Criterio de salida.** Hay una métrica de referencia y una explicación de los errores. La partición de prueba queda sin usar hasta la etapa 8. El manifiesto de particiones identifica cada grabación, así el firmware y la PC evalúan las mismas tomas.

### Etapa 4. Características

**Teoría.**

- La FFT calcula la DFT. La resolución frecuencial, la ventana y la fuga espectral salen de esa elección de parámetros.
- La STFT muestra cómo cambia el espectro. Longitud de ventana, solape, salto, ventana de Hann, magnitud, potencia y escala logarítmica.
- PCM crudo, magnitudes espectrales, espectrograma, espectrograma Mel y MFCC son representaciones distintas. MFCC agrega pasos sobre el log-Mel, entre ellos la DCT.
- En el ESP32, `esp-dsp` resuelve la ventana de Hann y la FFT radix-2. El banco Mel, y la DCT si la representación es MFCC, son matrices fijas. Por eso esta etapa las calcula una vez y las exporta.

**Práctica.**

1. Implementar con NumPy la ventana de Hann, la FFT, el espectro de potencia y el banco Mel. Implementar la DCT si MFCC entra en la comparación.
2. Partir de una ventana de análisis de 30 ms con solape. Elegir una longitud de FFT potencia de 2 y anotar cómo entra la ventana en esa FFT. Guardar ventana, salto y FFT en muestras.
3. Escribir la fórmula de int16 a float y la normalización en el archivo de parámetros.
4. Graficar la señal, su espectro y los espectrogramas de las tres clases.
5. Entrenar la línea de base de la etapa 3 con cada representación y anotar calidad y tiempo de cálculo.
6. Exportar el banco Mel y, si aplica, la DCT, en `.npy` y en un `.h` de arreglos `float`.
7. Guardar ventanas de prueba: el PCM int16 en `.raw` y la salida de cada paso en un `.h`. Incluir silencio y un caso en el límite de amplitud.

**Entregables.** `python/features/`, figuras, tabla de comparación, `python/features/params.md`, tablas y vectores.

**Criterio de salida.** La representación y sus parámetros quedan justificados por la tabla. Un script vuelve a leer los vectores y obtiene la misma salida. La longitud de FFT es potencia de 2.

### Etapa 5. Modelos

**Teoría.**

- Neurona: \(z = Wx + b\), \(a = \phi(z)\).
- Forward, pérdida, gradiente, épocas, tamaño de lote y tasa de aprendizaje.
- Curvas de aprendizaje, regularización, dropout y aumento de datos. Dropout actúa en el entrenamiento. El modelo exportado lleva la inferencia sin esa capa.
- Convolución, filtros, stride, padding y pooling. Sobre un espectrograma, una CNN pequeña ve patrones locales en tiempo y frecuencia.

**Práctica.** Con el mismo protocolo y la representación de la etapa 4:

1. Repetir la línea de base de scikit-learn sobre las características ya elegidas y guardar su métrica de validación.
2. Entrenar una MLP pequeña en Keras.
3. Entrenar una CNN pequeña en Keras.

El modelo que puede seguir a la etapa 6 usa capas cuya conversión a TensorFlow Lite es directa: convolución, convolución en profundidad, pooling, densa, reshape, ReLU y softmax. Si aparece otra capa, se anota en el registro como un punto que la etapa 7 de [plan.md](plan.md) tiene que comprobar contra el runtime de la placa.

Registrar cantidad de parámetros, métricas de validación, tiempo de entrenamiento y bytes del archivo. Elegir el modelo Keras por generalización en validación y por ese tamaño. La métrica de scikit-learn queda al lado, como piso de comparación.

**Entregables.** Scripts, modelo Keras elegido, matriz de confusión de validación, curvas, lista de capas y registro de experimentos.

**Criterio de salida.** Hay un modelo Keras elegido, con la lista de capas y las métricas de validación. La partición de prueba sigue sin usarse.

### Etapa 6. Cuantización

**Teoría.**

- El modelo entrenado, el `.tflite` y el programa que ejecuta ese archivo son piezas distintas. En la PC el programa es el intérprete de TensorFlow Lite. En la placa es el runtime de la etapa 7 de [plan.md](plan.md).
- La cuantización a enteros de 8 bits es la que ese runtime puede acelerar: \(x_{\mathrm{real}} \approx s(q - z)\), con \(q\) el entero, \(s\) la escala y \(z\) el cero.
- El conjunto representativo sale de ventanas de la partición de entrenamiento, ya pasadas por la etapa 4. Se guarda junto al script para poder repetir la conversión.
- La conversión puede cambiar la predicción. El `.tflite` se mide otra vez.

**Práctica.**

1. Guardar el modelo Keras en float.
2. Convertirlo a TensorFlow Lite con cuantización de enteros de 8 bits.
3. Ejecutar el intérprete en la PC sobre el conjunto de validación.
4. Comparar tamaño del archivo, métricas y predicciones caso a caso contra el modelo en float.
5. Anotar forma, tipo, escala y cero de la entrada y de la salida. Anotar la lista de operadores del `.tflite`.

**Entregables.** El archivo Keras, el `.tflite`, el conjunto representativo, el script de conversión y el informe anterior y posterior a la cuantización.

**Criterio de salida.** El intérprete en la PC ejecuta el `.tflite`, y la diferencia contra el modelo en float está medida. El informe lista los operadores que la etapa 7 de [plan.md](plan.md) va a buscar en el runtime de la FireBeetle.

### Etapa 7. Inferencia por ventanas

Esta etapa junta el preprocesamiento, el `.tflite` y el avance en muestras. Es el ensayo del lazo que en el firmware será captura, características e inferencia.

**Trabajo.**

1. Una función recibe un bloque PCM int16 y devuelve la etiqueta y la confianza. Las características son el código de la etapa 4. El modelo es el `.tflite` de la etapa 6.
2. El formato de salida es el del plan completo: `[CLASE: PALMAS] [CONFIANZA: 0.94]`. Los nombres son los del conjunto cerrado en la etapa 3.
3. Sobre una grabación larga, avanzar de a `hop_samples`. El búfer se mide en muestras. Contar ventanas recibidas, procesadas y descartadas. El descarte ocurre cuando el procesamiento de una ventana supera el tiempo que ocupa el salto a 16 000 Hz.
4. Imprimir la matriz de características en texto: un símbolo denso donde hay energía y espacio donde hay silencio.
5. Medir en la PC el tiempo de características y el tiempo del intérprete, por separado. Esos tiempos quedan rotulados como tiempos de PC.

**Validación.** Las ventanas de referencia de la etapa 4 producen la misma matriz. Para esas ventanas, la etiqueta del bucle coincide con la del intérprete llamado de forma directa.

**Criterio de salida.** Una grabación completa se clasifica ventana a ventana. Los contadores y los tamaños en muestras quedan escritos con los nombres que la etapa 10 de [plan.md](plan.md) va a usar: recibidas, procesadas y perdidas.

### Etapa 8. Evaluación

**Trabajo.**

1. Correr el bucle de la etapa 7 sobre el conjunto de prueba, una sola vez.
2. Calcular matriz de confusión, precision, recall, F1 y accuracy, para el modelo en float y para el `.tflite`.
3. Separar errores por clase y escuchar las tomas mal clasificadas.
4. Poner al lado de la accuracy la meta del plan original: superior al 85 %.
5. Si hace falta un cambio, se hace uno por vez, se regeneran los archivos de la sección 3 que ese cambio toque, y se repite este protocolo.

**Informe.** Dataset y protocolo, parámetros de la representación, arquitectura y operadores, métricas float y cuantizado, tiempos de PC, limitaciones y la tabla de la sección 3 con la ruta real de cada archivo.

**Criterio de salida.** El informe muestra cómo clasifica el sistema en la PC, con el conjunto de prueba, y cada archivo de la sección 3 existe en la ruta que el informe indica.

## 9. Árbol

```text
python/
├── docs/
│   ├── environment.md
│   ├── command_layout.md
│   └── audio_capture.md
├── data/
│   ├── wav/
│   ├── raw/
│   └── splits/
├── features/
│   ├── params.md
│   ├── tables/
│   └── vectors/
├── training/
├── evaluation/
├── models/
└── src/
    ├── command.py
    ├── capture.py
    ├── inspect_audio.py
    ├── dataset.py
    ├── features.py
    ├── train.py
    ├── convert_model.py
    ├── infer.py
    └── evaluate.py
```

`features/tables/` guarda el `.npy` y el `.h` del banco Mel o de la DCT. `features/vectors/` guarda el PCM de prueba y las salidas esperadas. `models/` guarda el Keras en float y el `.tflite`.

## 10. Decisiones que se cierran en la etapa indicada

| Decisión | Cuándo | Mientras tanto |
| --- | --- | --- |
| Intérprete de esta copia | Etapa 0, paso 0 | Conda, entorno `tinyml`, Python 3.12 |
| Versiones y rol de cada librería | Etapa 0 | La sección 2 es la lista. Una librería nueva se instala en `tinyml` y se agrega ahí antes de usarla |
| Layout del comando y duración de una toma | Etapa 1 | El PCM ya es mono, int16, little-endian, 16 000 Hz |
| Conjunto de clases | Etapa 3 | Palmas, golpe de mesa, ruido ambiente |
| Representación, muestras de ventana, salto y longitud de FFT | Etapa 4 | Ventana de análisis de 30 ms con solape, FFT en una potencia de 2 |
| Modelo que se cuantiza | Etapa 5 | La línea de base es scikit-learn. El archivo que sigue es un modelo Keras del conjunto de capas de esa etapa |
| Tolerancia entre float y cuantizado, y lista de operadores | Etapa 6 | Se escribe antes de comparar predicciones |

## 11. Cierre

La copia Python termina cuando el informe de la etapa 8 muestra la cadena desde el PCM hasta la etiqueta, y los archivos de la sección 3 están en las rutas que ese informe indica. Con esos archivos arrancan las etapas 1, 4, 5, 7, 8 y 11 de [plan.md](plan.md).
