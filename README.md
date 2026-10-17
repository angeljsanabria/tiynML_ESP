# tiynML_ESP

Proyecto de desarrollo de ingeniería para un clasificador acústico embebido basado en TinyML sobre plataformas ESP32/ESP-IDF con FreeRTOS, I2S, DMA, PSRAM, DSP y inferencia local con redes neuronales.

## Objetivo general

Desarrollar un sistema de detección de eventos acústicos en tiempo real usando un micrófono MEMS PDM, procesamiento digital de señales en el propio microcontrolador y una red neuronal ligera para clasificación local. El proyecto busca combinar conceptos de sistemas embebidos, audio digital, optimización de memoria, aceleración con hardware y TinyML.

## Plan de Desarrollo de Ingeniería: Clasificador Acústico Embebido (TinyML + FreeRTOS)

### Fase 1: Arquitectura Multitarea y Canal de Comunicación (FreeRTOS & UART)

El objetivo de esta fase es implementar los cimientos del sistema operativo en tiempo real. En la industria no se utilizan bucles bloqueantes; las responsabilidades se delegan en hilos de ejecución independientes (Tasks) que se comunican mediante colas de datos (Queues).

- Hito Didáctico: Dominar el ciclo de vida de las tareas en FreeRTOS, el paso de mensajes de forma segura entre hilos (Thread Safety) y el manejo de flujos de datos binarios por interrupción de hardware a alta velocidad (921,600 bauds).
- Implementación de Ingeniería:
  1. Crea una tarea llamada `Task_UART_Parser` con prioridad media. Esta tarea debe estar en estado Blocked (sin consumir CPU) utilizando las APIs nativas de interrupción de ESP-IDF para la UART, despertando únicamente cuando entran bytes por el puerto serie.
  2. Diseña un comando con estructura fija en bytes. Cuando el usuario envía el comando, la tarea extrae el valor de forma segura.
  3. Define una estructura de datos en C que contenga la orden y la duración de la grabación. Envía esta estructura a través de una cola de FreeRTOS (`QueueHandle_t`) para notificar a la siguiente tarea.
  4. Crea la segunda tarea llamada `Task_Audio_Manager` con prioridad alta, la cual se mantendrá bloqueada esperando datos en la cola de FreeRTOS.
- Métrica de Validación: Al enviar el comando desde la PC, la consola debe imprimir un log industrial de información utilizando `ESP_LOGI` detallando que el mensaje fue recibido, parseado y transmitido con éxito a través de la cola sin bloquear el procesador.

### Fase 2: Control de Periféricos de Audio e Ingesta a PSRAM (I2S, DMA & PSRAM)

En esta etapa se configura el micrófono MEMS PDM integrado (GPIO12 para CLK y GPIO9 para DATA) a bajo nivel. Para evitar pérdida de información en señales de audio, se requiere mover los datos directamente a la memoria sin que intervenga la CPU principal.

- Hito Didáctico: Comprender el funcionamiento del Acceso Directo a Memoria (DMA), la configuración de búferes circulares en hardware de audio y la asignación dinámica de bloques grandes en la memoria RAM externa (PSRAM) del ESP32-P4.
- Implementación de Ingeniería:
  1. Configura el periférico I2S en modo PDM de recepción (`i2s_pdm.h`) utilizando los controladores modernos de ESP-IDF. Establece la frecuencia de muestreo a 16,000 Hz con una resolución de 16 bits (PCM Mono).
  2. Habilita el descriptor DMA asignándole búferes internos intermedios. El DMA recolectará los bits del micrófono continuamente en segundo plano.
  3. Al recibir la notificación de la cola (de la Fase 1), calcula dinámicamente la memoria exacta necesaria basándote en la tasa de transferencia de datos de la señal: `16000 muestras * 2 bytes * X segundos`.
  4. Utiliza la función de asignación de memoria con capacidades de Espressif (`heap_caps_malloc`) configurando el flag `MALLOC_CAP_SPIRAM` para forzar que el búfer de audio masivo se aloje en los 32 MB de PSRAM de la FireBeetle, protegiendo la memoria interna SRAM del chip.
  5. Lee los bloques del DMA consecutivamente para llenar el bloque reservado en la PSRAM. Al completar el conteo exacto de muestras, deshabilita el canal I2S de forma inmediata.
- Métrica de Validación: Imprime por la consola mediante `ESP_LOGD` (mensajes de depuración) la dirección de memoria del puntero asignado. Debes verificar matemáticamente que el puntero reside dentro del mapa de direcciones asignado a la PSRAM externa.

### Fase 3: Instrumentación, Volcado Binario y Análisis de la Firma Acústica

Como ingeniero, debes ser capaz de validar de forma manual que los datos recolectados por el silicio están completamente limpios de ruido blanco, ruido eléctrico o distorsiones antes de entrenar cualquier modelo matemático.

- Hito Didáctico: Diferenciar el almacenamiento de datos crudos (RAW PCM) de contenedores estructurados de audio (WAV) y aprender a realizar análisis espectroscópico visual humano para identificar patrones de frecuencias.
- Implementación de Ingeniería:
  1. Implementa una función en C que realice un volcado binario directo (Memory Dump) del bloque de la PSRAM hacia la UART. No utilices texto plano; transmite los bytes crudos secuencialmente de un solo golpe.
  2. Configura un software terminal profesional capaz de registrar flujos binarios entrantes directo a un archivo plano en tu disco duro (un volcado `.raw`).
  3. Abre el software industrial de análisis de audio Audacity. Utiliza la herramienta de importación de datos en bruto (Import Raw Data) configurando manualmente los parámetros del periférico: 16-bit signed PCM, Little-Endian, Mono, 16000 Hz.
  4. Cambia el modo de visualización de la pista de audio de "Forma de Onda" a "Espectrograma".
- Métrica de Validación (Tus Ojos y Oídos):
  - Escucha: Al reproducir el audio con auriculares, tus golpes en la puerta o los tecleos en tu escritorio deben oírse naturales y claros. Si escuchas estática constante, debes ajustar la ganancia interna del micrófono PDM en el firmware.
  - Visión: Analiza el espectrograma. El silencio de tu habitación debe verse oscuro o azul uniforme. Las teclas mecánicas deben manifestarse como líneas verticales brillantes de alta frecuencia muy definidas. Los golpes de madera deben verse como explosiones verticales densas concentradas en las frecuencias medias y bajas.

### Fase 4: Procesamiento Digital de Señales en el Chip (DSP & Extracción de Características)

Para que un modelo de IA corra de forma óptima en microcontroladores, el audio nunca entra crudo. Se debe replicar exactamente el proceso visual que hiciste en Audacity (el espectrograma), pero calculándolo matemáticamente dentro del microprocesador en tiempo real.

- Hito Didáctico: Comprender la aplicación de la Transformada Rápida de Fourier (FFT), las funciones de enventanado y el filtrado por banco de frecuencias espaciadas en la escala Mel (MFE).
- Implementación de Ingeniería:
  1. Integra en tu proyecto el componente oficial de Espressif `esp-dsp`. Esta librería ejecuta operaciones matemáticas complejas escritas en ensamblador optimizado para las extensiones vectoriales de tu procesador RISC-V de doble núcleo.
  2. Divide tu grabación en fragmentos fijos superpuestos (por ejemplo, ventanas de 30 ms).
  3. Aplica una función de ventana matemática (como la ventana de Hann) en C para suavizar los bordes del audio y mitigar errores de discontinuidad espectral.
  4. Ejecuta la FFT para calcular el espectro de potencia de cada ventana, convirtiendo los datos del dominio del tiempo al dominio de la frecuencia. Pasa los resultados por un banco de filtros Mel para compactar las frecuencias en una matriz pequeña de coeficientes (espectrograma Mel).
- Métrica de Validación: Crea una rutina que dibuje la matriz generada en tu terminal serie de forma gráfica utilizando caracteres ASCII (por ejemplo, imprimiendo caracteres densos como `#` en las frecuencias con mucha energía y espacios vacíos en el silencio). Al teclear, deberías ver cómo se genera un dibujo de la firma acústica en tu monitor serial en tiempo real.

### Fase 5: Implementación de la Red Neuronal Local (Inferencia con ESP-NN)

El paso final es inyectar la inteligencia. El modelo TinyML toma la matriz matemática extraída localmente en la Fase 4 y la procesa a través de capas ocultas de una Red Neuronal Convolucional (CNN) para clasificar el sonido.

- Hito Didáctico: Integrar código de redes neuronales autogeneradas en C y entender cómo utilizar las librerías de aceleración de hardware para operaciones de matrices densas.
- Implementación de Ingeniería:
  1. Exporta tu modelo entrenado desde la plataforma TinyML elegida como "C/C++ Source Code" limpio (archivos `.c` y `.h` puros, sin empaquetar en librerías de terceros).
  2. Inserta los archivos en la estructura de directorios de tu proyecto de ESP-IDF dentro de VS Code, adaptando el archivo de configuración de compilación `CMakeLists.txt` para incluir los nuevos archivos fuente.
  3. Asegúrate de enlazar el componente nativo de Espressif `esp-nn` en el SDK de configuración (`menuconfig`). Esto activa las extensiones vectoriales físicas del procesador de la FireBeetle, logrando que los cálculos convolucionales pesados se resuelvan en apenas un par de milisegundos.
  4. Alimenta la función de inferencia con la matriz calculada en la Fase 4.
  5. Escribe la lógica de salida industrial por la UART utilizando `ESP_LOGI` para imprimir únicamente la etiqueta del estado detectado junto con su nivel de certeza flotante: `[CLASE: TECLADO_RAPIDO] [CONFIANZA: 0.94]`.
- Métrica de Validación: El sistema completo debe correr de manera continua en tiempo real, arrojando predicciones por la UART con una latencia de inferencia menor a los 30 milisegundos y una precisión superior al 85%.

## Estructura sugerida del proyecto

```text
tiynML_ESP/
├── README.md
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
├── sdkconfig
└── .gitignore
```

## Metas técnicas del proyecto

- Implementar un pipeline de audio completo desde captura hasta inferencia local.
- Garantizar captura robusta con DMA y PSRAM.
- Trabajar con audio RAW, FFT, features y redes neuronales sobre MCU.
- Mantener la lógica en tiempo real y con bajo consumo.
- Validar resultados usando logs serios, inspección visual y medición de latencia.

## Tecnologías previstas

- ESP-IDF
- FreeRTOS
- UART de alta velocidad
- I2S/PDM
- DMA
- PSRAM
- DSP (`esp-dsp`)
- Neural inference (`esp-nn`)
- C/C++ embebido
- Herramientas de análisis: Audacity, terminal serial, Python para postprocesado

## Nota

Este repositorio se usará como base para el desarrollo incremental del sistema, avanzando fase por fase desde la arquitectura embebida hasta la inferencia local de TinyML.
