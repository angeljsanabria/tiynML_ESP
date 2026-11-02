# Plan de trabajo y aprendizaje — tiynML_ESP

Programa de formación práctica para un ingeniero senior de sistemas embebidos: clasificador acústico TinyML sobre ESP32-P4. Une el plan de ingeniería del [README](README.md) con la ruta de aprendizaje de `noGit/tiynML_ESP_plan_aprendizaje.md`.

El trabajo avanza por etapas. Cada etapa produce un resultado verificable. Compilar no basta: hay que poder explicar la cadena de herramientas, medir el resultado y dejar versiones reproducibles.

**Hardware:** DFRobot FireBeetle 2 ESP32-P4 AI Vision Board (DFR1172).  
**Aplicación:** detección y clasificación de eventos acústicos en el propio microcontrolador.  
**Stack de firmware:** host Linux/Windows/macOS, toolchain C RISC-V (cross-compilación), CMake, Ninja, ESP-IDF, FreeRTOS, UART, I2S/PDM, DMA, PSRAM, `esp-dsp`, inferencia local.  
**Stack de aprendizaje y entrenamiento (camino principal):** Python (venv propio), NumPy, scikit-learn, TensorFlow/Keras, Audacity, terminal serial.  
**Stack paralelo en PC (opcional):** Edge Impulse u otro estudio TinyML en la computadora, para explorar dataset, features y modelos con rapidez (ver sección 2.1). **No** es el camino de compresión ni de despliegue a la ESP.  
**Runtime de inferencia en placa:** se cierra en la etapa 7 sobre el modelo del camino principal. El README prevé código C/C++ exportado y `esp-nn`. La ruta de aprendizaje prevé ESP-TFLite-Micro. Las dos opciones quedan abiertas hasta comprobar un ejemplo en esta placa.

Antes de integrar periféricos o bibliotecas, se confirma la revisión de la placa DFR1172 **y la revisión de silicio del ESP32-P4** (esta unidad puede ser una revisión antigua). Se fijan ESP-IDF, CMake, Ninja, toolchain y extensión de VS Code a un único conjunto compatible con ese silicio. La configuración dorada de build queda en contenedor (módulo 0B) para no rearmar el target desde cero en cada ejemplo. Un ejemplo publicado para ESP32-P4 se adapta al micrófono de esta placa; no se da por compatible solo por el nombre ni por “la última IDF”.

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

### 2.1 Otra forma de desarrollo (paralela en PC): Edge Impulse

Además del camino principal (scikit-learn + TensorFlow/Keras → conversión propia en etapa 7), se admite un **hilo paralelo en la computadora** con un framework de ayuda tipo **Edge Impulse** (u equivalente).

**Para qué sí**

- Subir o enlazar el mismo audio etiquetado de las etapas 3–4.
- Probar rápido representaciones y clasificadores en la nube/estudio del framework.
- Obtener métricas y matrices de confusión en PC como **referencia de contraste** (“¿el problema es separable con este dataset?”).
- Acelerar la intuición sobre ventanas, Mel/MFCC y errores por clase mientras el camino principal se construye a mano.

**Para qué no**

- No sustituye el entrenamiento reproducible en el venv del repo.
- No es el mecanismo de **compresión / cuantización / export a ESP** de este proyecto. El despliegue a la FireBeetle sigue la etapa 7 (TFLite Micro o C + `esp-nn`) sobre el modelo del camino principal.
- Un `.eim` / firmware generado por el framework **no** cierra las etapas 7–11.

**Cómo encaja en el calendario**

| Cuándo | Uso de Edge Impulse (u otro) | Camino principal |
| --- | --- | --- |
| Desde etapa 3–4 | Proyecto en PC con las mismas clases y tomas | Dataset y baseline sklearn |
| Paralelo a 5–6 | Probar features/modelos en el estudio; anotar ideas | Features y redes en Python propio |
| Etapa 7 en adelante | Solo consulta de notas; no export a placa | Conversión e inferencia propias |

**Entregables del hilo paralelo.** Carpeta `ml/edge_impulse/` (o similar) con: ID/nombre del proyecto, capturas o export de métricas en PC, y un párrafo en el informe de la etapa 6 que compare “estudio Edge Impulse en PC” vs “modelo sklearn/Keras del repo”. Si las conclusiones divergen, gana el protocolo del camino principal salvo que se documente un cambio de dataset o de clases.

**Criterio.** El paralelo es opcional y no bloquea ninguna etapa. Si se usa, queda versionado qué audio y qué partición se subió, para no mezclar con el hold-out de la etapa 11.

## 3. Metas de diseño

Estas cifras son metas. La etapa 11 las mide y el informe distingue el valor obtenido del valor buscado.

- Pipeline completo: captura, características, inferencia local y salida por UART.
- Captura con DMA y el bloque de audio en PSRAM (`MALLOC_CAP_SPIRAM`), sin apoyar ese búfer en la SRAM interna.
- Audio de referencia: PCM mono, 16 bits con signo, little-endian, 16 000 Hz.
- Comando de grabación por UART a 921 600 baudios. En bring-up se prueba en flujo secuencial; en el firmware de entrega se parsea en una tarea bloqueada y se entrega por cola a la tarea de audio.
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
9. **Bring-up primero, multitarea después.** Validar UART, I2S/DMA/PSRAM y el volcado en un flujo secuencial (una sola lógica de aplicación). Recién cuando eso es estable, partir en tareas FreeRTOS con colas. El trabajo final y la clasificación continua exigen multitarea; el diagnóstico temprano no.
10. Agregar una tarea de FreeRTOS cuando el plazo, el bloqueo o el producto lo justifiquen — no “porque el ejemplo trae dos tasks”.

### Matiz obligatorio (ESP-IDF no es baremetal puro)

ESP-IDF **ya ejecuta FreeRTOS** debajo: `app_main` corre como tarea del sistema. “Probar en baremetal” en este proyecto significa **arquitectura mono-flujo** (secuencial, sin `Task_UART_Parser` / `Task_Audio_Manager` propias), no deshabilitar el RTOS del SDK. Eso simplifica buscar fallas de periférico sin mezclar prioridades, colas e I2S. El entregable de ingeniería sí usa multitarea explícita.

No se duplica el trabajo de ML (etapas 4–7): el doble paso aplica al **firmware de adquisición e integración**, no a reentrenar modelos.

## 5. Metodología de cada etapa

Cada etapa cierra con cuatro piezas:

- **Teoría:** lo que hay que poder explicar.
- **Ejemplo:** una operación matemática o un ejemplo de la placa, visto completo.
- **Práctica:** implementación guiada.
- **Validación:** prueba, métrica y nota de lo observado.

El criterio de salida es una comprobación, no un compilado exitoso.

## 6. Secuencia

El orden sigue la dependencia real del sistema y el modo de arquitectura del firmware:

1. **Bring-up (etapas 1–3):** comando UART → captura I2S → volcado/firma, en flujo secuencial dentro de la lógica de aplicación (típicamente desde `app_main` o funciones llamadas en serie). Objetivo: aislar fallas de silicio, PDM, DMA y PSRAM.
2. **ML en PC (etapas 4–7):** sin depender aún del diagrama final de tareas.
3. **DSP e inferencia en chip (etapas 8–9):** se pueden cerrar aún en modo secuencial (un disparo de captura → features → inferir → log).
4. **Producto FreeRTOS (etapa 1F, luego 10–11):** mismas responsabilidades ya validadas, partidas en tareas y colas; después captura continua y evaluación.

El canal de comando queda temprano porque el resto del firmware se dispara con él. FreeRTOS multitarea explícita no se antepone al primer audio limpio.

| Etapa | Modo | Trabajo | Aprendizaje que la sostiene | Depende de |
| --- | --- | --- | --- | --- |
| 0 | — | Estación host (0A) + config única P4 en contenedor (0B) | TinyML, cadena de build, silicio, tools | — |
| 1 | Bring-up | Comando UART binario y parseo en flujo secuencial | Protocolo binario, UART, logs | 0 |
| 2 | Bring-up | I2S PDM, DMA, PSRAM, captura de X segundos (secuencial) | Muestreo, Nyquist, PDM/PCM, DMA | 0, 1 |
| 3 | Bring-up | Volcado RAW, firma acústica, análisis en PC | RAW/WAV, espectrograma visual | 2 |
| 1F | Producto | Partir 1–2 en `Task_UART_Parser`, cola y `Task_Audio_Manager` | Tareas, Blocked, colas, thread safety | 3 |
| 4 | ML | Dataset, particiones, clasificador de referencia | Supervisado, métricas | 3 |
| 5 | ML | Espectrograma / Mel / MFCC en Python; elegir representación | DFT/FFT, STFT, Mel, MFCC | 4 |
| 6 | ML | SVM/logística, MLP, CNN; elegir modelo | Capas, pérdida, convolución | 5 |
| 7 | ML | Conversión, cuantización, runtime | Inferencia, escala y cero | 6 |
| 8 | Bring-up/chip | Mismo preprocesamiento en C (`esp-dsp`), vectores de prueba | Equivalencia numérica | 5, 7 |
| 9 | Bring-up/chip | Inferencia en placa + log clase/confianza (disparo único OK) | Runtime, tensores, memoria | 8 |
| 10 | Producto | Captura continua, contadores, diagrama de tareas | Latencia, jitter, prioridades | 1F, 9 |
| 11 | Producto | Evaluación en dispositivo, optimización una a una, informe | Matriz de confusión, trade-offs | 10 |

## 7. Etapas

### Etapa 0. Entorno y arquitectura

**Trabajo.** Dejar operativa la estación de desarrollo (módulo 0A: host + toolchain C + ESP-IDF + IDE) y la **configuración única de ESP32-P4** (módulo 0B: imagen Docker anclada a la revisión de silicio de esta placa). Crear un proyecto que compile, se flashee y arranque con esa config; crear el venv de Python para ML; dejar todo en `docs/environment.md`. La extensión de VS Code es la interfaz de edición; no sustituye a CMake, al compilador cruzado ni al contenedor que fija el target.

**Teoría.**

- TinyML: entrenamiento en la PC; inferencia en el microcontrolador.
- Restricciones de RAM, Flash, tiempo de CPU y consumo.
- Cadena del producto: micrófono PDM → I2S/PCM → búfer → preprocesamiento → modelo → postprocesado → UART.
- Cadena de build (obligatoria de entender): fuentes C/C++ → CMake (genera el grafo de build) → Ninja (ejecuta la build) → toolchain GCC RISC-V (cross-compila para ESP32-P4) → enlazado → imagen binaria → `esptool`/flash → monitor serie.
- Responsabilidad de cada pieza: host (Git, Python del sistema, permisos USB), ESP-IDF (SDK, componentes, `idf.py`), CMake/Ninja (construcción), toolchain (código máquina del target), contenedor (congela IDF + tools + `IDF_TARGET` para *esta* revisión de P4), VS Code + extensión (edición; build dorado vía contenedor o vía el mismo IDF anclado), venv ML (aparte).
- Revisión de silicio ≠ target genérico: `esp32p4` no basta. Una placa P4 antigua puede exigir una versión concreta de IDF y opciones de `sdkconfig` que un ejemplo “nuevo” rompe. Por eso hay una sola config del repo, no una por tutorial.

**Criterio de salida.** Firmware de prueba flasheado y con log en UART; build reproducible con la imagen/tag del módulo 0B (y, si se usa host, con el **mismo** IDF anclado); `docs/environment.md` con revisión de silicio, tag de imagen y checklist de 0A/0B.

#### Módulo 0A. Estación de desarrollo (host, toolchain C, CMake, IDE)

Este módulo es el onboarding de laboratorio. Un ingeniero senior no “instala el plugin y ya”: deja una estación que otro colega pueda clonar y usar con las mismas versiones.

##### 1. Qué hay que entender (mapa de responsabilidades)

| Pieza | Rol | ¿Quién la aporta? |
| --- | --- | --- |
| Sistema operativo + Git | Host, control de versiones | Instalación del host |
| Python del host | Arranca instaladores y, en algunos flujos, herramientas | Paquete del SO o instalador oficial |
| Paquetes de build del host (Linux) | Librerías y utilidades que el instalador de IDF puede necesitar (`git`, `wget`, `flex`, `bison`, `gperf`, `python3-venv`, etc.) | Gestor de paquetes del SO; seguir la lista oficial de la versión de ESP-IDF elegida |
| **CMake** | Genera el sistema de build a partir de `CMakeLists.txt` | Lo instala el **ESP-IDF Installation Manager** / `install.sh` (versión fijada por IDF). No hace falta un CMake “casero” paralelo |
| **Ninja** | Ejecuta la compilación de forma rápida | Idem, lo trae el instalador de IDF |
| **Toolchain C/C++ RISC-V** (`xtensa`/`riscv32` según chip; en ESP32-P4 es RISC-V) | Compilador, ensamblador, linker, `newlib`/headers del target | Idem: toolchain oficial Espressif, no el `gcc` del host |
| **ccache** (opcional pero habitual) | Acelera recompilaciones | Suele venir con las tools de IDF |
| **OpenOCD + GDB** | Depuración por JTAG/USB-JTAG | Tools de IDF; no obligatorio el día 1 si solo se flashea por UART |
| **esptool / idf.py flash** | Escritura de la imagen en Flash | Parte de ESP-IDF |
| **ESP-IDF** (`IDF_PATH`) | SDK, componentes FreeRTOS, drivers I2S, build scripts | Installation Manager o clone + `install.sh` + `export.sh` |
| **Python de IDF** (`IDF_PYTHON_ENV_PATH`) | Dependencias de `idf.py`, menuconfig, particiones | Venv creado por el instalador de IDF |
| **VS Code** | Editor | Instalación manual |
| **Extensión Espressif IDF** | Wizard, Doctor, botones build/flash/monitor, enlace al `IDF_PATH` | Marketplace de VS Code |
| **Extensión C/C++** (Microsoft C/C++ o clangd) | IntelliSense, ir a definición, diagnósticos sobre headers del target | Marketplace; la extensión ESP-IDF no reemplaza el soporte de lenguaje C |
| **Venv ML** (aparte) | NumPy, scikit-learn, TensorFlow/Keras | Creado a mano para este repo; **nunca** mezclar con el Python de IDF |

Regla de oro: el `gcc`/`g++` del host compila programas para la PC. El firmware del ESP32-P4 lo compila el **toolchain cruzado** de Espressif. Confundir ambos es un error clásico de estación mal montada.

##### 2. Prerrequisitos del host (antes del plugin)

1. Git instalado y accesible en PATH.
2. Python 3 compatible con la versión de ESP-IDF que se va a fijar (consultar la guía Get Started de esa versión).
3. En Linux: instalar los prerrequisitos oficiales documentados para esa versión de ESP-IDF (paquete de build essentials / dependencias listadas por Espressif). Sin esto el Installation Manager o `install.sh` fallan a mitad de camino.
4. Permiso al puerto serie: usuario en el grupo `dialout` (o equivalente). Comprobar con la placa conectada (`/dev/ttyACM*` o `/dev/ttyUSB*`).
5. Espacio en disco suficiente para IDF + tools + builds (varios GB).

Anotar SO, arquitectura del host (`uname -m`) y versiones de Git/Python del sistema en `docs/environment.md`.

##### 3. Instalación de ESP-IDF y de la cadena C (CMake, Ninja, toolchain)

Camino de referencia (laboratorio):

1. Instalar [Visual Studio Code](https://code.visualstudio.com/).
2. Instalar la extensión **Espressif IDF**.
3. Instalar la extensión de lenguaje **C/C++** (Microsoft) o **clangd**, para edición profesional del código C del proyecto.
4. Command Palette → `ESP-IDF: Open ESP-IDF Installation Manager`.
5. Instalar la **misma** versión de ESP-IDF que fije el módulo 0B (tag de `espressif/idf` compatible con la revisión de silicio de *esta* DFR1172). Anotar el número exacto; prohibido “latest”.
6. El Manager descarga e instala, entre otras cosas: **CMake**, **Ninja**, el **toolchain RISC-V**, utilidades de flash/debug y el **venv Python de IDF**. Eso es lo que permite compilar C para la placa; el plugin solo orquesta.
7. `ESP-IDF: Select Current ESP-IDF Version` → elegir esa instalación (alineada con el contenedor).
8. `ESP-IDF: Doctor Command`. Corregir fallos de tools, Python o PATH antes de seguir. Guardar resumen en `docs/environment.md`.

Camino alternativo (CLI, mismo resultado técnico): clonar ESP-IDF, ejecutar `./install.sh esp32p4`, luego `. ./export.sh` en cada shell, y apuntar la extensión a `IDF_PATH` / `IDF_TOOLS_PATH` / `IDF_PYTHON_ENV_PATH`.

Verificación mínima en una terminal ya exportada (o en la terminal que abre la extensión):

```bash
idf.py --version
cmake --version
ninja --version
riscv32-esp-elf-gcc --version
```

Si `cmake` o el `*-esp-elf-gcc` no aparecen, la estación no está lista aunque el plugin esté instalado. Anotar las cuatro salidas en `docs/environment.md`.

##### 4. Cómo entra CMake en este proyecto

- En la raíz: `CMakeLists.txt` del proyecto (incluye ESP-IDF vía `$ENV{IDF_PATH}/tools/cmake/project.cmake` y declara `project(...)`).
- En `main/`: `CMakeLists.txt` del componente principal (`idf_component_register` con `SRCS` e `INCLUDE_DIRS`).
- `idf.py build` (o el botón Build de la extensión) hace, en esencia: configurar con CMake → generar archivos Ninja → compilar/enlazar con el toolchain → producir binarios en `build/`.
- `sdkconfig` / `menuconfig` (`ESP-IDF: SDK Configuration Editor`) fija opciones del target y de componentes; no sustituye a CMake, lo alimenta.
- Tras cambiar de target o romper el árbol de build: `idf.py fullclean` y volver a configurar. No editar a mano el contenido generado en `build/` como si fuera fuente.

El ingeniero debe poder abrir los dos `CMakeLists.txt`, explicar qué fuentes entran al binario y añadir un `.c`/`.h` nuevo sin adivinar.

##### 5. Proyecto, target y placa

1. Abrir `tiynML_ESP` en VS Code (o generar aquí el proyecto ESP-IDF mínimo si aún no existe).
2. `ESP-IDF: Set Espressif Device Target` → `esp32p4` (equivalente: `idf.py set-target esp32p4`).
3. Conectar la DFR1172. `ESP-IDF: Select Port to Use`.
4. OpenOCD solo si se va a depurar por JTAG en esta sesión; para el primer bring-up alcanza flash por UART/USB.
5. Compilar un firmware mínimo (hello-world o el esqueleto del repo), flashear y abrir monitor.

##### 6. Ciclo diario

| Acción | Extensión VS Code | Terminal (entorno IDF activo) |
| --- | --- | --- |
| Configurar target | `Set Espressif Device Target` | `idf.py set-target esp32p4` |
| menuconfig | `SDK Configuration Editor` | `idf.py menuconfig` |
| Compilar | `Build your project` | `idf.py build` |
| Flashear | `Flash your project` | `idf.py -p PORT flash` |
| Monitor | `Monitor your device` | `idf.py -p PORT monitor` |
| Build + flash + monitor | `Build, Flash and Monitor` | `idf.py -p PORT flash monitor` |
| Limpiar build | `Full Clean` | `idf.py fullclean` |

##### 7. Entorno Python de ML (paralelo, no mezclado)

Crear un venv del repo solo para datos y entrenamiento. Instalar ahí NumPy, scikit-learn, TensorFlow/Keras y lo que fije la etapa. No instalar esas librerías dentro del Python de IDF. Anotar ruta del venv y `pip freeze` relevante en `docs/environment.md`.

##### 8. Entregable `docs/environment.md` (checklist de cierre)

- SO del host, Git, Python del sistema.
- VS Code + versión de la extensión Espressif IDF + extensión C/C++ (o clangd).
- Versión de ESP-IDF, `IDF_PATH`, `IDF_TOOLS_PATH`.
- Salidas de `cmake --version`, `ninja --version`, `riscv32-esp-elf-gcc --version` (o el triplete que muestre Doctor para P4).
- Target `esp32p4`, **revisión de silicio** del chip (ver 0B), puerto serie, resultado del Doctor.
- Tag de imagen Docker y que el IDF del host coincide con ese tag (si el host también compila).
- Comando con el que el firmware mínimo mostró log por UART (host y/o contenedor).
- Ruta del venv ML (si ya se creó) y nota de que está separado del Python de IDF.

##### 9. Criterio de salida de este módulo

1. Doctor Command en verde (o fallos documentados y resueltos).
2. CMake, Ninja y toolchain RISC-V visibles y versionados.
3. `idf.py build` produce binarios sin error (host alineado con 0B, o solo vía 0B).
4. Flash + monitor muestran el firmware de prueba en la DFR1172.
5. El ingeniero puede explicar, sin leer un tutorial, el papel de CMake frente al plugin y frente al compilador cruzado.

**Notas.** Cursor u otros forks de VS Code pueden cargar las mismas extensiones; si la UI de Espressif falla ahí, el camino de referencia es VS Code + extensión + `idf.py` (o el contenedor 0B). El 0A enseña la cadena; el 0B la congela para esta placa.

#### Módulo 0B. Configuración única ESP32-P4 (contenedor anclado al silicio)

**Problema que resuelve.** En ejemplos previos, cada cambio de firmware o de tutorial obligó a rearmar ESP-IDF “como desde cero” por el target y por la **revisión de silicio** del P4 (esta unidad es una revisión antigua). Eso no es aceptable en un proyecto serio: la estación tiene **una** configuración dorada por placa, versionada en el repo.

**Idea.** Usar la imagen oficial `espressif/idf:<tag>` (mismo enfoque que el demo CESE LoRa con Compose; ver `extras/containers.md` y [containers.dev](https://containers.dev/) como especificación de Dev Containers). El contenedor no reemplaza el aprendizaje del 0A: **congela** IDF + CMake + Ninja + toolchain + `IDF_TARGET=esp32p4` para *esta* revisión. El host edita; el build dorado sale de esa imagen (o de un IDF host clonado al mismo tag).

##### 1. Qué se ancla (una sola vez, por escrito)

| Ítem | Dónde vive | Regla |
| --- | --- | --- |
| Revisión de silicio del ESP32-P4 | `docs/environment.md` | Leerla del chip (p. ej. log de arranque, `espefuse` / utilidades IDF) y no asumir “P4 genérico” |
| Revisión / SKU de la DFR1172 | idem | Placa ≠ solo el SoC |
| Tag de imagen | `Dockerfile` / `docker-compose.yml` | p. ej. `espressif/idf:vX.Y.Z` — el tag debe soportar P4 **y** esta revisión; nunca `latest` |
| `IDF_TARGET` | compose / env / scripts | Fijo: `esp32p4` |
| Defaults de proyecto | `sdkconfig.defaults` (y defaults de placa si aplica) | Commiteados; no depender de un `sdkconfig` local sin documentar |
| Puerto serie | `.env` local (no secretos; puede ir en `.gitignore`) | p. ej. `ESPPORT=/dev/ttyACM0` |

Si un ejemplo externo pide otra IDF o asume silicio más nuevo: **no** se cambia la imagen del repo a ciegas. Se adapta el ejemplo a la config dorada, o se documenta un experimento desechable fuera del árbol principal.

##### 2. Artefactos en el repo (a crear en esta etapa)

```text
Dockerfile                 # FROM espressif/idf:<tag> anclado
docker-compose.yml         # servicio idf, volume del repo, IDF_TARGET=esp32p4
docker-compose.serial.yml  # devices: puerto serie (flash/monitor)
scripts/idf_build.sh
scripts/idf_flash.sh
scripts/idf_monitor.sh
sdkconfig.defaults         # opciones estables para esta placa/silicio
docs/environment.md        # silicio + tag + comandos que funcionaron
```

Patrón de referencia (otro chip, misma idea de Compose): [CESE-IDS-ESP32_LORA_BEACON_APP](https://github.com/nicoriostaurasi/CESE-IDS-ESP32_LORA_BEACON_APP). Ahí el target es `esp32s3` y el tag `v5.3.5`; aquí el tag y el target se eligen **después** de identificar el silicio de esta FireBeetle.

Opcional más adelante: `.devcontainer/` según [containers.dev](https://containers.dev/) para abrir el mismo entorno dentro del IDE. No es requisito del cierre de la etapa 0.

##### 3. Flujo de trabajo (Linux)

Build (sin placa):

```bash
docker compose build
docker compose run --rm idf idf.py set-target esp32p4
docker compose run --rm idf idf.py build
```

Flash / monitor (con puerto):

```bash
ESPPORT=/dev/ttyACM0 docker compose -f docker-compose.yml -f docker-compose.serial.yml run --rm idf idf.py -p $ESPPORT flash
ESPPORT=/dev/ttyACM0 docker compose -f docker-compose.yml -f docker-compose.serial.yml run --rm idf idf.py -p $ESPPORT monitor
```

(Ajustar el nodo del puerto al de la DFR1172. Usuario en `dialout` u equivalente.)

##### 4. Reglas de disciplina (anti “reconfigurar desde cero”)

1. **Un tag, un target, un silicio documentado.** Cambiar el tag es un cambio de proyecto (PR / nota en `environment.md`), no un gesto de cada tutorial.
2. Tras `set-target` o cambio de IDF: `fullclean` y rebuild; no mezclar `build/` de otra versión.
3. Ejemplos de DFRobot / Espressif se **portan** a este árbol con la imagen dorada; no se abre un segundo IDF “para probar un rato” como camino oficial.
4. El IDF del host (0A), si se usa para build, debe ser el **mismo** `vX.Y.Z` que el tag del contenedor.
5. ML sigue fuera del contenedor de IDF (venv del repo).

##### 5. Criterio de salida de este módulo

1. Revisión de silicio del P4 y tag de `espressif/idf` anotados y coherentes entre sí.
2. `docker compose run --rm idf idf.py build` produce el firmware de prueba sin retocar el entorno a mano.
3. Flash + monitor desde el overlay serial funcionan en esta DFR1172.
4. Queda escrito: “si mañana abro un ejemplo nuevo, uso esta imagen; no reinstalo IDF por el target”.

### Etapa 1. Canal de comando (bring-up secuencial)

Corresponde al protocolo de la fase 1 del README, **sin** particionar aún en tareas propias. FreeRTOS del IDF sigue activo debajo; la aplicación es un solo flujo para aislar fallas de UART y del comando.

**Trabajo.**

1. Configurar UART a 921 600 baudios con las API de ESP-IDF (recepción por interrupción o driver recomendado; sin busy-wait de CPU).
2. Definir un comando de estructura fija en bytes (orden + duración de grabación).
3. Desde la lógica de aplicación (p. ej. `app_main` o un bucle único), leer/parsear el comando y dejar la duración en una variable o estructura local lista para la etapa 2.
4. No crear todavía `Task_UART_Parser`, colas ni `Task_Audio_Manager`. Eso es la etapa 1F.

**Teoría.** Trama binaria, framing, baudrate, buffers de driver UART. Diferencia entre “el SDK usa FreeRTOS” y “mi firmware ya es multitarea de producto”.

**Validación.** Al enviar el comando desde la PC, un `ESP_LOGI` muestra orden y duración parseadas correctamente.

**Criterio de salida.** La duración llega intacta a la función que disparará la captura. Cero tareas de aplicación propias más allá del flujo de bring-up.

### Etapa 1F. Partición FreeRTOS (producto)

Se hace **después** de la etapa 3 (audio y firma validados). Mismas responsabilidades ya probadas; cambia solo la concurrencia. Es el puente hacia el trabajo final y la etapa 10.

**Trabajo.**

1. Crear `Task_UART_Parser` (prioridad media), bloqueada en las API de UART; parsea el mismo comando de la etapa 1.
2. Empaquetar orden + duración en una estructura C y enviarla por cola (`QueueHandle_t`).
3. Crear `Task_Audio_Manager` (prioridad alta), bloqueada en la cola; concentra la captura ya validada en las etapas 2–3.
4. Comprobar que el comportamiento observable (comando → grabación → volcado o log) no empeora respecto al bring-up.

**Teoría.** Ciclo de vida de una tarea, estado Blocked, colas, thread safety, prioridades. Por qué el producto no puede quedarse en un solo flujo cuando UART y audio compiten por tiempo.

**Validación.** Mismo comando de la PC; `ESP_LOGI` muestra recepción, parseo y cruce de cola. Sin espera activa. La captura de X segundos sigue siendo válida a oído/espectrograma.

**Criterio de salida.** Diagrama de dos tareas + cola documentado; el camino comando→audio equivale al bring-up. El diagrama completo (continuo) se cierra en la etapa 10.

### Etapa 2. Captura: teoría, ejemplo de la placa e I2S

Corresponde a la fase 2 del README y al módulo de adquisición. Primero se obtiene audio válido con el ejemplo de grabación de DFRobot y se inspecciona en Python. Después se reproduce esa captura en el firmware del proyecto, aún en **modo bring-up** (la orden viene del parseo secuencial de la etapa 1, no de la cola de 1F).

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
3. Al llegar la orden (desde el parseo secuencial de la etapa 1), reservar el bloque exacto: `16000 muestras * 2 bytes * X segundos`.
4. Alojar ese bloque con `heap_caps_malloc` y `MALLOC_CAP_SPIRAM`, en la PSRAM de 32 MB de la FireBeetle.
5. Vaciar los búferes DMA en ese bloque hasta completar el conteo. Al terminar, deshabilitar el canal I2S.
6. Mantener esta lógica en funciones reutilizables (`i2s_audio_*` / similar) para que la etapa 1F solo cambie *quién* llama, no *cómo* captura.

**Práctica previa al firmware propio.** Ejecutar el ejemplo de grabación de DFRobot, guardar WAV, graficar la forma de onda y el histograma de amplitudes, y comprobar frecuencia, duración, saturación y que las muestras no estén vacías.

**Validación.** `ESP_LOGD` imprime la dirección del búfer. Esa dirección cae en el mapa de la PSRAM externa. El WAV o el RAW de referencia se abre con los parámetros de la etapa 3. Si algo falla, el sospechoso es I2S/DMA/PSRAM/silicio — no el scheduler de tareas propias.

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

**Paralelo opcional (PC).** Con el mismo conjunto de clases, abrir un proyecto en Edge Impulse (sección 2.1) solo para explorar en la computadora. No cuenta como modelo de referencia del repo.

**Entregables.** `ml/data_collection/`, `ml/training/`, `ml/evaluation/`, descripción del dataset y un informe corto del modelo de referencia.

**Criterio de salida.** Hay un modelo de referencia **en el camino principal** y una explicación de los errores que comete.

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

Si corrió el hilo Edge Impulse en PC, incluir en el registro una comparación breve de métricas (estudio vs Keras/sklearn). La elección que entra a la etapa 7 es siempre del camino principal.

**Entregables.** Scripts reproducibles, modelo elegido, matriz de confusión, curvas de entrenamiento y validación, registro de experimentos (y notas del paralelo en PC, si hubo).

**Criterio de salida.** Un modelo del repo que generaliza de forma razonable en la partición de validación y cuyo tamaño es compatible con el dispositivo. La partición de prueba queda sin usar hasta las etapas 7 y 11.

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

Edge Impulse (u otro estudio) **no** aporta aquí el binario ni la cuantización de despliegue: aunque el framework pueda exportar a ESP, en este plan esa vía queda fuera de alcance. La etapa 7 parte del Keras/TF (o del formato intermedio propio) del camino principal.

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

Parte de la arquitectura FreeRTOS de la etapa 1F. Hasta aquí (y en 8–9) el sistema puede grabar X segundos por comando o disparar una inferencia puntual. Esta etapa mantiene la clasificación mientras el micrófono sigue abierto: es el firmware de **producto** del trabajo final.

**Teoría.**

- Un sistema de tiempo real termina el trabajo dentro del plazo de la aplicación. Latencia, throughput, jitter, periodo de ventana, y la relación entre tiempo de procesamiento y tiempo de adquisición.
- DMA, búfer circular, pase de bloques y pérdida de muestras.
- Tareas, prioridades, colas y bloqueo. Una tarea nueva entra si evita una espera activa o aisla un plazo. El resto puede vivir en una tarea que ya existe. El bring-up secuencial ya demostró que el periférico funciona; aquí se demuestra que el scheduler no lo rompe.

**Trabajo.**

1. Captura continua con DMA circular sobre el camino de audio ya validado.
2. Definir el flujo captura → características → inferencia, con el tamaño de cola y el criterio cuando la cola se llena.
3. Contadores de bloques recibidos, procesados y perdidos.
4. Dejar por escrito el diagrama de tareas y de colas. Base obligatoria: `Task_UART_Parser` + `Task_Audio_Manager` de la 1F. Otras tareas solo si el diagrama lo justifica.
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
├── Dockerfile
├── docker-compose.yml
├── docker-compose.serial.yml
├── sdkconfig.defaults
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
├── scripts/
│   ├── idf_build.sh
│   ├── idf_flash.sh
│   └── idf_monitor.sh
├── ml/
│   ├── data_collection/
│   ├── preprocessing/
│   ├── training/
│   ├── evaluation/
│   └── edge_impulse/          # opcional: notas/métricas del estudio en PC
├── docs/
│   ├── environment.md
│   └── audio_capture.md
├── extras/
│   └── containers.md
├── sdkconfig
└── .gitignore
```

`components/model/` guarda el artefacto de la etapa 7. Si el runtime exige otro empaquetado, se documenta el cambio en esa etapa y se actualiza este árbol. `Dockerfile` / Compose son la config dorada del módulo 0B.

## 9. Decisiones que se cierran en la etapa indicada

| Decisión | Cuándo | Mientras tanto |
| --- | --- | --- |
| Revisión de placa DFR1172, revisión de silicio P4, tag `espressif/idf`, extensión VS Code | Etapa 0 (0A+0B) | No se integra un ejemplo nuevo ni se cambia el tag sin anotarlo |
| Imagen Docker / Compose como build dorado del firmware | Etapa 0 (0B) | Host solo si usa el mismo IDF que el tag |
| Conjunto de clases | Etapa 4 | Tres clases iniciales: palmas, golpe de mesa, ruido ambiente |
| Representación y parámetros (ventana, salto, bandas) | Etapa 5 | Ventanas de 30 ms con solape como punto de partida |
| Runtime en placa: C exportado + `esp-nn`, o ESP-TFLite-Micro (camino principal) | Etapa 7 | Los dos se consideran hasta que un ejemplo compile en la placa |
| Edge Impulse (u otro) solo como paralelo de exploración en PC | Desde etapa 4, opcional | No despliega ni cuantiza para la ESP en este proyecto |
| Tolerancia numérica Python/C | Etapa 8 | Se escribe antes de comparar vectores |
| Partición en `Task_UART_Parser` + cola + `Task_Audio_Manager` | Etapa 1F (tras etapa 3) | Etapas 1–3 en flujo secuencial (bring-up) |
| Tareas adicionales a las dos de la 1F | Etapa 10 | Solo parser UART y gestor de audio hasta justificar otra |

## 10. Referencias

1. [DFRobot FireBeetle 2 ESP32-P4 — documentación oficial](https://wiki.dfrobot.com/dfr1172/)
2. [DFRobot — ejemplo de grabación de audio](https://wiki.dfrobot.com/dfr1172/docs/22903)
3. [ESP-IDF — ejemplo de recepción I2S/PDM](https://github.com/espressif/esp-idf/tree/master/examples/peripherals/i2s/i2s_basic/i2s_pdm)
4. [ESP-TFLite-Micro — repositorio oficial](https://github.com/espressif/esp-tflite-micro)
5. [ESP-TFLite-Micro — ejemplo Micro Speech](https://github.com/espressif/esp-tflite-micro/tree/master/examples/micro_speech)
6. [ESP-DSP — repositorio oficial](https://github.com/espressif/esp-dsp)
7. [Edge Impulse — tutorial de clasificación acústica](https://docs.edgeimpulse.com/docs/tutorials/end-to-end-tutorials/audio/audio-classification) (uso en este plan: paralelo en PC, sección 2.1; no despliegue a ESP)
8. [ESP-IDF — documentación para ESP32-P4](https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/get-started/index.html)
9. [Extensión ESP-IDF para VS Code — instalación](https://docs.espressif.com/projects/vscode-esp-idf-extension/en/latest/installation.html)
10. [Extensión ESP-IDF para VS Code — configurar proyecto](https://docs.espressif.com/projects/vscode-esp-idf-extension/en/latest/configureproject.html)
11. [ESP-IDF — Get Started (prerrequisitos del host y tools)](https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/get-started/index.html)
12. [ESP-IDF — Build System (CMake)](https://docs.espressif.com/projects/esp-idf/en/stable/esp32p4/api-guides/build-system.html)
13. [Development Containers](https://containers.dev/)
14. [Imágenes Docker oficiales Espressif IDF](https://hub.docker.com/r/espressif/idf)
15. [Referencia Compose ESP-IDF (CESE, otro target)](https://github.com/nicoriostaurasi/CESE-IDS-ESP32_LORA_BEACON_APP)

La compatibilidad se comprueba con el ejemplo, el tag de imagen y la revisión de silicio fijados en la etapa 0.

## 11. Cierre

El proyecto termina cuando el informe de la etapa 11 muestra la cadena completa, desde la presión acústica hasta la etiqueta en la UART, con el protocolo de datos, las métricas y las limitaciones escritas. El resultado buscado es poder explicar y medir cada decisión de ese recorrido.
