# Plan de trabajo y aprendizaje — tiynML_ESP

Plan único del clasificador acústico embebido. Une el plan de ingeniería del [README](README.md) con la ruta de aprendizaje de `noGit/tiynML_ESP_plan_aprendizaje.md`.

El trabajo avanza por etapas. Cada etapa produce un resultado verificable. No se pasa a la siguiente porque el código compile.

**Hardware:** DFRobot FireBeetle 2 ESP32-P4 AI Vision Board (DFR1172).  
**Aplicación:** detección y clasificación de eventos acústicos en el propio microcontrolador.  
**Stack de trabajo:** ESP-IDF, FreeRTOS, UART, I2S/PDM, DMA, PSRAM, `esp-dsp`, inferencia local, C embebido.  
**Stack de aprendizaje y entrenamiento:** Python, NumPy, scikit-learn, TensorFlow/Keras, análisis en Audacity y terminal serial.  
**Runtime de inferencia:** se cierra en la etapa 7, con un ejemplo que compile en esta placa. El README prevé código C/C++ exportado y `esp-nn`. La ruta de aprendizaje prevé ESP-TFLite-Micro. Las dos opciones quedan abiertas hasta esa comprobación.

Antes de integrar periféricos o bibliotecas, se confirma la revisión de la DFR1172 y se fijan las versiones de ESP-IDF y del resto de herramientas. Un ejemplo publicado para ESP32-P4 se adapta al micrófono integrado de esta placa; no se da por compatible por el nombre de la biblioteca.

---

## 1. Objetivo

Desarrollar un sistema que capture audio con el micrófono MEMS PDM integrado, lo procese en el ESP32-P4 y clasifique el evento en el dispositivo.

El recorrido que hay que poder explicar y medir es este:

1. Adquisición de la señal y análisis de los datos.
2. Fundamentos de aprendizaje supervisado.
3. Dataset, características y entrenamiento en la PC.
4. Evaluación y selección del modelo.
5. El mismo preprocesamiento, en Python y en C.
6. Conversión, cuantización y despliegue.
7. Integración con ESP-IDF y FreeRTOS.
8. Medición de latencia, memoria y calidad, y una optimización por vez.

El entrenamiento ajusta los parámetros en la computadora. En el microcontrolador corre la inferencia.

## 2. Qué fija cada fuente

El README define el sistema de ingeniería y sus cinco fases de implementación:

1. Arquitectura multitarea y canal UART.
2. Captura I2S, DMA y PSRAM.
3. Volcado binario y lectura de la firma acústica.
4. DSP en el chip y extracción de características.
5. Inferencia local y reporte de clase y confianza.

La ruta de aprendizaje agrega el ciclo que el firmware solo no cubre, y las condiciones para dar por válida cada etapa:

- Entorno reproducible y versiones fijadas.
- Teoría de muestreo, PDM/PCM, FFT, espectrogramas, Mel y MFCC.
- Dataset etiquetado, particiones y un modelo de referencia antes de la red.
- Entrenamiento comparado (modelo lineal o SVM, MLP, CNN pequeña).
- Cuantización y validación numérica del modelo convertido.
- Equivalencia del preprocesamiento entre Python y C.
- Captura continua, pérdidas de bloques y evaluación con datos no usados para entrenar ni para elegir el modelo.
- Registro de resultados medidos, separados de las metas de diseño.

## 3. Metas de diseño

Estas cifras son metas. La etapa 11 las mide y el informe distingue el valor obtenido del valor buscado.

- Pipeline completo: captura, características, inferencia local y salida por UART.
- Captura con DMA y el bloque de audio en PSRAM (`MALLOC_CAP_SPIRAM`), sin apoyar ese búfer en la SRAM interna.
- Audio de referencia: PCM mono, 16 bits con signo, little-endian, 16 000 Hz.
- Comando de grabación por UART a 921 600 baudios, parseado en una tarea bloqueada y entregado por cola a la tarea de audio.
- Latencia de inferencia menor a 30 ms.
- Precisión superior al 85 % en el protocolo de evaluación de la etapa 11.
- Clasificación continua sin pérdidas de captura fuera de lo contado y registrado.

## 4. Principios de trabajo

1. Comprender la teoría de la etapa antes de implementar.
2. Escribir la hipótesis antes del experimento.
3. Separar entrenamiento, validación y prueba. Las ventanas de una misma grabación permanecen en una sola partición.
4. Guardar configuración, semilla, versiones y métricas de cada experimento.
5. Validar cada etapa con entradas y salidas conocidas.
6. Volver a medir el modelo después de convertirlo y cuantizarlo.
7. Medir antes de optimizar. Cada optimización se evalúa sola, contra el mismo protocolo.
8. Documentar el resultado obtenido y la meta por separado.
9. Agregar una tarea de FreeRTOS cuando el plazo o el bloqueo lo justifiquen.

## 5. Metodología de cada etapa

Cada etapa cierra con cuatro piezas:

- **Teoría:** lo que hay que poder explicar.
- **Ejemplo:** una operación matemática o un ejemplo de la placa, visto completo.
- **Práctica:** implementación guiada.
- **Validación:** prueba, métrica y nota de lo observado.

El criterio de salida es una comprobación, no un compilado exitoso.

## 6. Secuencia

El orden sigue la dependencia real del sistema. El canal de comando queda temprano porque el resto del firmware se dispara con él. El estudio del modelo y el entrenamiento ocurren en la PC antes de portar DSP e inferencia. La clasificación continua cierra cuando las tres etapas (captura, características, inferencia) ya funcionan por separado.

| Etapa | Trabajo | Aprendizaje que la sostiene | Depende de |
| --- | --- | --- | --- |
| 0 | Entorno reproducible y mapa del sistema | TinyML, bloques del pipeline, herramientas | — |
| 1 | `Task_UART_Parser`, comando binario, cola, `Task_Audio_Manager` | Tareas, bloqueo, colas, thread safety | 0 |
| 2 | I2S PDM, DMA, búfer en PSRAM, captura de X segundos | Muestreo, Nyquist, PDM/PCM, DMA | 0, 1 |
| 3 | Volcado RAW, escucha y espectrograma; análisis en Python | RAW frente a WAV, lectura visual de la firma | 2 |
| 4 | Dataset de tres clases, particiones, clasificador de referencia | Supervisado, generalización, métricas | 3 |
| 5 | Espectrograma, Mel y MFCC en Python; elección de representación | DFT/FFT, STFT, ventana de Hann, Mel y MFCC | 4 |
| 6 | SVM o regresión logística, MLP y CNN; selección del modelo | Capas, pérdida, gradiente, convolución | 5 |
| 7 | Conversión, cuantización y elección del runtime | Inferencia, operadores, escala y cero | 6 |
| 8 | El mismo preprocesamiento en C, con `esp-dsp` y vectores de prueba | Error numérico, búferes, equivalencia train/infer | 5, 7 |
| 9 | Inferencia en la FireBeetle y log de clase y confianza | Runtime, tensores, RAM interna y PSRAM | 8 |
| 10 | Captura continua, contadores de bloques, diagrama de tareas | Latencia, jitter, DMA circular, prioridades | 1, 9 |
| 11 | Evaluación en dispositivo, cuellos de botella, informe | Matriz de confusión, compromisos de diseño | 10 |

## 7. Etapas

### Etapa 0. Entorno y arquitectura

**Trabajo.** Dejar un proyecto ESP-IDF para ESP32-P4 que compile, se programe y arranque con un firmware mínimo. Crear el entorno virtual de Python. Anotar en `docs/environment.md` la revisión de la placa, ESP-IDF, Python, las bibliotecas y los comandos usados.

**Teoría.**

- TinyML: el entrenamiento ocurre en la PC; la inferencia puede correr en el microcontrolador.
- Restricciones de RAM, Flash, tiempo de CPU y consumo.
- Cadena del sistema: micrófono PDM, I2S y conversión a PCM, búfer, preprocesamiento, modelo, postprocesado, UART.
- Responsabilidad de cada herramienta: Python (datos y entrenamiento), ESP-IDF (firmware y periféricos), `esp-dsp` (DSP), el runtime elegido en la etapa 7 (inferencia), Git (experimentos reproducibles).

**Criterio de salida.** Compilar, grabar y ejecutar el firmware de prueba con versiones conocidas, sin depender de una configuración que no esté escrita.

### Etapa 1. Canal de comando (UART y FreeRTOS)

Corresponde a la fase 1 del README. En esta etapa existen dos tareas porque una espera bytes de la UART y la otra espera una orden de grabación. El diagrama completo de tareas se cierra en la etapa 10.

**Trabajo.**

1. Crear `Task_UART_Parser` con prioridad media. La tarea permanece en estado Blocked y despierta con las API de interrupción de UART de ESP-IDF cuando entran bytes. Velocidad del puerto: 921 600 baudios.
2. Definir un comando de estructura fija en bytes. Al recibirlo, la tarea extrae la orden y la duración de la grabación.
3. Empaquetar ese contenido en una estructura C y enviarlo por una cola (`QueueHandle_t`).
4. Crear `Task_Audio_Manager` con prioridad alta, bloqueada en la cola.

**Teoría.** Ciclo de vida de una tarea, estado Blocked, colas, paso de mensajes entre hilos y flujo binario por interrupción.

**Validación.** Al enviar el comando desde la PC, un `ESP_LOGI` indica que el mensaje se recibió, se parseó y cruzó la cola. El procesador no queda en un bucle de espera activa.

**Criterio de salida.** El comando de duración llega intacto a `Task_Audio_Manager`.

### Etapa 2. Captura: teoría, ejemplo de la placa e I2S

Corresponde a la fase 2 del README y al módulo de adquisición. Primero se obtiene audio válido con el ejemplo de grabación de DFRobot y se inspecciona en Python. Después se reproduce esa captura en el firmware del proyecto.

**Teoría.**

- Frecuencia de muestreo, cuantización, rango dinámico, clipping, Nyquist, aliasing y filtro antialiasing.
- Relación entre duración, frecuencia de muestreo y cantidad de muestras.
- PDM (densidad de pulsos) y PCM (muestras). El reloj PDM y la frecuencia PCM de 16 000 Hz son magnitudes distintas.
- En la DFR1172 el micrófono integrado entrega PDM. El I2S del ESP32-P4 puede recibirlo y convertirlo a PCM en hardware.
- Tamaño de bloque, latencia de adquisición, DMA, desbordamiento y pérdida de muestras.
- Esta etapa graba un intervalo finito. La escucha continua queda para la etapa 10.

**Trabajo de firmware.**

1. Configurar I2S en recepción PDM (`i2s_pdm.h`) con los controladores actuales de ESP-IDF. GPIO12 es CLK y GPIO9 es DATA. Formato: 16 000 Hz, PCM mono de 16 bits.
2. Asignar descriptores DMA y sus búferes internos. El DMA junta las muestras sin intervención continua de la CPU.
3. Al llegar la orden por la cola, reservar el bloque exacto: `16000 muestras * 2 bytes * X segundos`.
4. Alojar ese bloque con `heap_caps_malloc` y `MALLOC_CAP_SPIRAM`, en la PSRAM de 32 MB de la FireBeetle.
5. Vaciar los búferes DMA en ese bloque hasta completar el conteo. Al terminar, deshabilitar el canal I2S.

**Práctica previa al firmware propio.** Ejecutar el ejemplo de grabación de DFRobot, guardar WAV, graficar la forma de onda y el histograma de amplitudes, y comprobar frecuencia, duración, saturación y que las muestras no estén vacías.

**Validación.** `ESP_LOGD` imprime la dirección del búfer. Esa dirección cae en el mapa de la PSRAM externa. El WAV o el RAW de referencia se abre con los parámetros de la etapa 3.

**Criterio de salida.** Audio reproducible, con formato conocido y sin fallas evidentes de captura (desbordamiento, silencio digital, saturación permanente).

### Etapa 3. Firma acústica

Corresponde a la fase 3 del README. El objetivo es decidir, con oído y con espectrograma, si el audio sirve para entrenar.

**Trabajo.**

1. Volcar el bloque de PSRAM por UART en binario crudo, de una sola vez, sin codificarlo como texto.
2. Registrar ese flujo en un archivo `.raw` con un terminal que acepte binario.
3. Importar en Audacity: PCM con signo de 16 bits, little-endian, mono, 16 000 Hz.
4. Pasar la vista de forma de onda a espectrograma.
5. Repetir la inspección en Python: forma de onda, distribución de amplitudes, clipping y espectro.

**Lectura de validación.**

- Al reproducir, un golpe o un tecleo se reconoce. Estática continua indica que hay que corregir la ganancia del micrófono PDM en el firmware.
- El silencio de la sala se ve oscuro y uniforme. Un tecleo aparece como línea vertical breve de alta frecuencia. Un golpe de madera aparece como una barra vertical ancha en frecuencias medias y bajas.

**Entregables.** `docs/audio_capture.md`, grabaciones de referencia y el script de visualización.

**Criterio de salida.** Un conjunto de tomas de referencia aceptadas para etiquetar, y notas de las tomas rechazadas y del motivo.

### Etapa 4. Dataset y modelo de referencia

Esta etapa no está en las cinco fases del README. Sin ella, la inferencia de la fase 5 no tiene un modelo evaluado.

**Teoría.**

- Clasificación supervisada: \(f_\theta(x) \rightarrow y\). \(x\) son las características, \(y\) la clase, \(\theta\) los parámetros aprendidos.
- Ejemplo, característica, etiqueta. Particiones de entrenamiento, validación y prueba.
- Sobreajuste, subajuste, sesgo, varianza y fuga entre particiones.
- Regresión logística, SVM y red neuronal como familias distintas. Pérdida, optimización y umbral de decisión.
- Accuracy, precision, recall, F1 y matriz de confusión. La métrica principal depende del costo de cada error.

**Conjunto inicial.** Tres clases: palmas, golpes sobre una mesa y ruido ambiente. El tecleo, el golpe de puerta y el golpe de madera de la etapa 3 siguen como banco de escucha. Si más adelante entran al conjunto de clases, se etiquetan de nuevo y se rehacen las particiones. El conjunto queda cerrado por escrito antes de etiquetar.

**Práctica.** Etiquetar grabaciones, armar las tres particiones sin mezclar ventanas de la misma toma, entrenar un clasificador simple con características provisionales y revisar los errores uno por uno.

**Entregables.** `ml/data_collection/`, `ml/training/`, `ml/evaluation/`, descripción del dataset y un informe corto del modelo de referencia.

**Criterio de salida.** Hay un modelo de referencia y una explicación de los errores que comete.

### Etapa 5. Características en la PC

Corresponde al estudio de la fase 4 del README, hecho primero en Python. La implementación en C es la etapa 8.

**Teoría.**

- DFT y FFT. La FFT calcula la DFT; es el algoritmo, no otra transformada.
- Resolución frecuencial, ventanas y fuga espectral.
- STFT: la firma cambia en el tiempo. Longitud de ventana, solape, salto, ventana de Hann, magnitud, potencia y escala logarítmica. El compromiso entre resolución temporal y frecuencial se anota con los parámetros elegidos.
- Comparar PCM crudo, magnitudes espectrales, espectrograma, espectrograma Mel y MFCC. Mel y MFCC son representaciones distintas: MFCC aplica pasos adicionales sobre el log-Mel, entre ellos la DCT.

**Práctica.** Graficar la señal, su espectro y espectrogramas con distintas ventanas y saltos. Extraer Mel o MFCC. Entrenar el clasificador de la etapa 4 con cada representación y anotar calidad y costo. Partir de ventanas de 30 ms con solape, como indica el README, y dejar constancia si el experimento fijo otro valor.

**Entregables.** `ml/preprocessing/`, notebook de análisis, comparación visual e informe de la representación elegida, con sus parámetros.

**Criterio de salida.** La representación y sus parámetros (ventana, salto, cantidad de bandas, normalización) quedan justificados por esa comparación.

### Etapa 6. Redes y selección del modelo

**Teoría.**

- Neurona: \(z = Wx + b\), \(a = \phi(z)\). Capas, activaciones y paso de datos.
- Forward, pérdida, gradiente, retropropagación, descenso de gradiente, épocas, tamaño de lote y tasa de aprendizaje.
- Curvas de aprendizaje, regularización, dropout, aumento de datos y elección de hiperparámetros.
- Convolución, filtros, mapas, stride, padding y pooling. Sobre un espectrograma, una CNN pequeña ve patrones locales en tiempo y frecuencia.

**Práctica.** Con el mismo protocolo de la etapa 4, entrenar:

1. Regresión logística o SVM (referencia de la etapa 4, repetida sobre las características ya elegidas).
2. Una MLP pequeña.
3. Una CNN pequeña.

Registrar cantidad de parámetros, métricas y tiempo de entrenamiento. Elegir el modelo por calidad de generalización y por el tamaño que la etapa 7 pueda colocar en la FireBeetle.

**Entregables.** Scripts reproducibles, modelo elegido, matriz de confusión, curvas de entrenamiento y validación, registro de experimentos.

**Criterio de salida.** Un modelo que generaliza de forma razonable en la partición de validación y cuyo tamaño es compatible con el dispositivo. La partición de prueba queda sin usar hasta las etapas 7 y 11.

### Etapa 7. Conversión, cuantización y runtime

**Teoría.**

- El archivo entrenado en Python, el formato de intercambio, el modelo que acepta el runtime y los operadores que ese runtime implementa son cuatro cosas distintas.
- Memoria de constantes del modelo, tensores de entrada y salida, y arena temporal.
- Cuantización: por ejemplo, enteros de 8 bits en lugar de float32. Relación habitual \(x_{\mathrm{real}} \approx s(q - z)\), con \(q\) el entero, \(s\) la escala y \(z\) el cero. Pesos, activaciones y entrada se cuantizan. El conjunto representativo interviene en la cuantización postentrenamiento.
- La conversión puede fallar por un operador o por la forma del tensor. La cuantización puede cambiar la predicción. Por eso el modelo convertido se evalúa otra vez.

**Decisión de runtime.** Se compila un ejemplo concreto en esta placa y con la versión de ESP-IDF fijada en la etapa 0.

- Camino del README: exportar fuentes C/C++ e integrarlas en el proyecto, enlazando `esp-nn` para las extensiones vectoriales del RISC-V.
- Camino de la ruta de aprendizaje: convertir a un modelo que ESP-TFLite-Micro ejecute, y comprobar el ejemplo Micro Speech contra ESP32-P4 y la versión de ESP-IDF ya fijada.

Se adopta el runtime cuyo ejemplo arranca en la DFR1172 y que implementa los operadores del modelo elegido. La decisión, la versión y el motivo quedan en el registro de la etapa.

**Práctica.** Guardar el modelo original. Convertirlo. Evaluarlo en el mismo conjunto de prueba usado como referencia de PC. Comparar tamaño, métricas y predicciones caso a caso. Anotar operadores y memoria estimada.

**Entregables.** Artefacto convertido, scripts de conversión, forma y tipo de la entrada y de la salida, informe anterior y posterior a la cuantización.

**Criterio de salida.** El modelo corre en el runtime elegido, las métricas de PC están medidas después de la conversión, y la memoria necesaria está estimada.

### Etapa 8. El mismo preprocesamiento en C

Corresponde a la fase 4 del README, con la condición de equivalencia de la ruta de aprendizaje. La red no ve PCM crudo: ve la representación elegida en la etapa 5. El pipeline de entrenamiento y el del firmware tienen que coincidir, no solo los pesos.

**Teoría.** Float frente a entero, error numérico, normalización, saturación, desbordamiento, y diferencias entre bibliotecas. En el firmware: memoria estática, reutilización de búferes, dimensiones, alineación y costo por ventana.

**Trabajo.**

1. Exportar desde Python vectores de entrada y la salida esperada de cada paso (ventana de Hann, FFT y espectro de potencia, banco Mel o MFCC, normalización).
2. Implementar esos pasos en C. Usar `esp-dsp` donde la operación coincida con la de Python dentro de la tolerancia fijada. `esp-dsp` aporta rutinas en ensamblador para las extensiones vectoriales del RISC-V de doble núcleo del ESP32-P4.
3. Partir la grabación en ventanas solapadas con los parámetros de la etapa 5.
4. Comparar C contra Python con una tolerancia escrita antes de la prueba. Incluir silencio y un caso en el límite de amplitud.
5. Dibujar la matriz por UART con caracteres ASCII: un símbolo denso donde hay energía y espacio donde hay silencio. Al teclear, la firma tiene que reconocerse en el monitor.

**Entregables.** Código de características, vectores de prueba, prueba de equivalencia, error numérico y tiempo por ventana.

**Criterio de salida.** El preprocesamiento del firmware reproduce el de entrenamiento dentro de la tolerancia, y el dibujo ASCII confirma que la energía sigue al sonido.

### Etapa 9. Inferencia en la FireBeetle

Corresponde a la fase 5 del README.

**Teoría.** Carga del modelo, asignación de tensores, resolución de operadores y ejecución. Distinguir constantes del modelo, entrada y salida, arena temporal, RAM interna, PSRAM y la memoria que ya ocupa el resto del firmware. Colocar un búfer en PSRAM no iguala la velocidad de la SRAM interna. Un operador optimizado acelera esa operación; el resto del grafo se mide aparte.

**Trabajo.**

1. Si el runtime es ESP-TFLite-Micro, partir del ejemplo Micro Speech ya compilado en la etapa 7 y sustituir el modelo por el convertido.
2. Si el runtime es código C exportado, incorporar `.c` y `.h` al árbol ESP-IDF y actualizar `CMakeLists.txt`. Activar `esp-nn` en `menuconfig`.
3. Alimentar la inferencia con la matriz de la etapa 8.
4. Publicar por UART, con `ESP_LOGI`, solo la etiqueta y la confianza. Formato de referencia: `[CLASE: TECLADO_RAPIDO] [CONFIANZA: 0.94]`. Los nombres de clase son los del conjunto cerrado en la etapa 4.
5. Medir tiempo de inferencia y memoria. Comparar salidas contra el modelo convertido en la PC, con los mismos vectores.

**Entregables.** Firmware que infiere, registro de predicciones y primer benchmark de latencia y memoria.

**Criterio de salida.** Las predicciones del dispositivo coinciden con las del modelo convertido en la PC, dentro del criterio escrito en esta etapa. La latencia queda medida. La meta de 30 ms se contrasta con ese número; si no se cumple, el dato igual se registra y el ajuste pasa a la etapa 11.

### Etapa 10. Tiempo real y captura continua

Extiende la fase 1. Hasta aquí el sistema graba X segundos por comando. Esta etapa mantiene la clasificación mientras el micrófono sigue abierto.

**Teoría.**

- Un sistema de tiempo real termina el trabajo dentro del plazo de la aplicación. Latencia, throughput, jitter, periodo de ventana, y la relación entre tiempo de procesamiento y tiempo de adquisición.
- DMA, búfer circular, pase de bloques y pérdida de muestras.
- Tareas, prioridades, colas y bloqueo. Una tarea nueva entra si evita una espera activa o aisla un plazo. El resto puede vivir en una tarea que ya existe.

**Trabajo.**

1. Captura continua con DMA circular.
2. Definir el flujo captura → características → inferencia, con el tamaño de cola y el criterio cuando la cola se llena.
3. Contadores de bloques recibidos, procesados y perdidos.
4. Dejar por escrito el diagrama de tareas y de colas. `Task_UART_Parser` sigue siendo el canal de comando. `Task_Audio_Manager` sigue siendo dueña del audio. Otras tareas solo si el diagrama lo justifica.
5. Correr sesiones largas y guardar los contadores.

**Entregables.** Firmware modular, diagrama, registro de pérdidas y de latencia de extremo a extremo, notas de la prueba sostenida.

**Criterio de salida.** El sistema clasifica de forma continua y toda pérdida de audio queda contada. La inferencia no abre un hueco de captura que el contador no vea.

### Etapa 11. Evaluación y optimización

**Teoría.** Matriz de confusión, precision, recall, F1, falsos positivos y falsos negativos, calculados sobre grabaciones que no participaron del entrenamiento ni de la elección del modelo. Latencia de captura, de preprocesamiento, de inferencia y de decisión. RAM, Flash y, si hay equipo para medirlo, consumo. Cada mejora de una métrica se mira junto con el efecto sobre las demás.

**Trabajo.**

1. Correr en el dispositivo un conjunto de prueba independiente.
2. Medir la latencia de cada etapa y el uso de memoria.
3. Comparar el modelo en float de la PC, el modelo cuantizado en la PC y el firmware.
4. Señalar el cuello de botella principal.
5. Aplicar una optimización y volver a medir el mismo protocolo antes de intentar otra.

**Informe final.** Dataset y protocolo, arquitectura del modelo, métricas, versiones, latencia, memoria, limitaciones, y la comparación entre la PC y la FireBeetle. Las metas de 30 ms y de 85 % aparecen al lado del valor medido.

**Criterio de salida.** El informe muestra, con datos, cómo se comporta el sistema, cuáles son sus límites y por qué la arquitectura quedó así.

## 8. Árbol de trabajo

El árbol del README, más las carpetas de la ruta de aprendizaje:

```text
tiynML_ESP/
├── README.md
├── plan.md
├── CMakeLists.txt
├── main/
│   ├── CMakeLists.txt
│   ├── app_main.c
│   ├── uart_parser.c
│   ├── audio_manager.c
│   ├── i2s_audio.c
│   ├── dsp.c
│   ├── model_inference.c
│   └── include/
│       ├── uart_parser.h
│       ├── audio_manager.h
│       ├── i2s_audio.h
│       ├── dsp.h
│       └── model_inference.h
├── components/
│   └── model/
│       ├── model.c
│       └── model.h
├── ml/
│   ├── data_collection/
│   ├── preprocessing/
│   ├── training/
│   └── evaluation/
├── docs/
│   ├── environment.md
│   └── audio_capture.md
├── sdkconfig
└── .gitignore
```

`components/model/` guarda el artefacto de la etapa 7. Si el runtime exige otro empaquetado, se documenta el cambio en esa etapa y se actualiza este árbol.

## 9. Decisiones que se cierran en la etapa indicada

| Decisión | Cuándo | Mientras tanto |
| --- | --- | --- |
| Revisión de la DFR1172 y versiones de ESP-IDF y bibliotecas | Etapa 0 | No se integra un ejemplo nuevo |
| Conjunto de clases | Etapa 4 | Tres clases iniciales: palmas, golpe de mesa, ruido ambiente |
| Representación y parámetros (ventana, salto, bandas) | Etapa 5 | Ventanas de 30 ms con solape como punto de partida |
| Runtime: C exportado + `esp-nn`, o ESP-TFLite-Micro | Etapa 7 | Los dos se consideran hasta que un ejemplo compile en la placa |
| Tolerancia numérica Python/C | Etapa 8 | Se escribe antes de comparar vectores |
| Tareas adicionales a las dos de la etapa 1 | Etapa 10 | Solo parser UART y gestor de audio |

## 10. Referencias

1. [DFRobot FireBeetle 2 ESP32-P4 — documentación oficial](https://wiki.dfrobot.com/dfr1172/)
2. [DFRobot — ejemplo de grabación de audio](https://wiki.dfrobot.com/dfr1172/docs/22903)
3. [ESP-IDF — ejemplo de recepción I2S/PDM](https://github.com/espressif/esp-idf/tree/master/examples/peripherals/i2s/i2s_basic/i2s_pdm)
4. [ESP-TFLite-Micro — repositorio oficial](https://github.com/espressif/esp-tflite-micro)
5. [ESP-TFLite-Micro — ejemplo Micro Speech](https://github.com/espressif/esp-tflite-micro/tree/master/examples/micro_speech)
6. [ESP-DSP — repositorio oficial](https://github.com/espressif/esp-dsp)
7. [Edge Impulse — tutorial de clasificación acústica](https://docs.edgeimpulse.com/docs/tutorials/end-to-end-tutorials/audio/audio-classification)
8. [ESP-IDF — documentación para ESP32-P4](https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/get-started/index.html)

La compatibilidad se comprueba con el ejemplo y la versión fijada en la etapa 0.

## 11. Cierre

El proyecto termina cuando el informe de la etapa 11 muestra la cadena completa, desde la presión acústica hasta la etiqueta en la UART, con el protocolo de datos, las métricas y las limitaciones escritas. El resultado buscado es poder explicar y medir cada decisión de ese recorrido.
