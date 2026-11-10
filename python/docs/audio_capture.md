# Captura de audio

Contrato de las tomas de la copia Python y del PCM que la etapa 2 de [plan.md](../../plan.md) pide al I2S de la FireBeetle 2 ESP32-P4 (DFR1172).

## Formato

| Parámetro | Valor |
| --- | --- |
| Contenedor de trabajo | WAV, para grabar y escuchar |
| Payload | PCM en `.raw`, sin encabezado |
| Canales | 1 (mono) |
| Muestra | 16 bits con signo, little-endian |
| Frecuencia | 16 000 Hz |
| Rango de una muestra | −32768 a 32767 |

Un segundo de audio ocupa `16000 * 2` bytes. Una toma de X segundos ocupa `16000 * 2 * X` bytes. Es la misma cuenta con la que el firmware reserva el bloque en la PSRAM.

`pruebas_py/2_raw_process_1.py` lee un WAV, escribe `output_1.raw` junto a ese archivo y pone `contrato: True` solo si es mono, de 2 bytes por muestra y de 16 000 Hz. Sirve para una toma. En una carpeta con varios WAV, ese único `output_1.raw` se reemplaza en cada corrida.

`pruebas_py/2_raw_carpeta_process_1.py` hace la misma conversión para todos los WAV de una carpeta. El argumento es la carpeta, no un archivo. Lee solo los `.wav` de ese nivel y no entra en subcarpetas. Crea `carpeta/outputs/` y guarda cada PCM con el mismo nombre y extensión `.raw`. `grabacion/parche/parche-01.wav` queda en `grabacion/parche/outputs/parche-01.raw`. Usa el módulo `wave` de la biblioteca estándar. No agrega librerías. Imprime, por archivo, canales, bytes por muestra, frecuencia, muestras, bytes del raw y `contrato`, y al final cuántos cumplieron.

## Por qué esta calidad

El micrófono de la DFR1172 es un MEMS PDM. GPIO12 es el reloj y GPIO9 son los datos. El I2S del ESP32-P4 convierte ese PDM a PCM en hardware. El plan fija esa salida en 16 000 Hz, mono y 16 bits. El reloj PDM y esos 16 000 Hz no son la misma frecuencia.

La grabación de la PC imita ese PCM, no el tren de pulsos del micrófono. Así el `.raw`, la ventana y la FFT tienen las mismas dimensiones en Python y en el firmware.

- **Mono.** La placa tiene un micrófono. Un archivo estéreo obligaría a descartar un canal antes de compararlo con el búfer.
- **16 bits.** Cada muestra entra en dos bytes, el ancho del volcado y del `dtype="<i2"` de los procesos 2 y 3. El rango alcanza para los eventos de este proyecto sin pasar a 24 o 32 bits, que el bloque de la PSRAM no usa.
- **16 000 Hz.** Representa frecuencias hasta 8 000 Hz. Es la banda que van a ver el modelo de la PC y el de la placa. Una toma a 48 000 Hz habría que remuestrear antes de la FFT, y la cantidad de muestras dejaría de coincidir con `16000 * X`.

## Cómo grabar en la PC

En Audacity, antes de grabar:

- Project Rate (Hz): `16000`.
- Canales de grabación: 1 (Mono).

Exportar con File, Export Audio, WAV (Microsoft), Signed 16-bit PCM. Guardar el archivo en `pruebas_py/sonidos/`.

Si el micrófono de Windows solo ofrece 48 000 Hz y estéreo, se deja así. La frecuencia del proyecto y la exportación en Audacity son las que arman el WAV de 16 000 Hz, mono y 16 bits. El proceso 1 juzga ese archivo.

Hay que grabar las tres clases: golpe al parche, golpe al anillo y sonido ambiente. Cada archivo lleva una sola clase. La duración es la del archivo.

## Comprobación

Desde `pruebas_py`, con el entorno `tinyml` activo:

```text
python 2_raw_process_1.py sonidos/nombre.wav
python 2_raw_carpeta_process_1.py grabacion/parche
```

`contrato: True` y `bytes del raw` igual a `16000 * 2 * segundos` habilitan el proceso 2 (`output_2.txt`) y el proceso 3 (`output_3.png`) sobre un `.raw`. Esos dos procesos siguen siendo de un archivo: leen el `.raw` que se les pasa.

## Tomas

El formato de los 81 WAV está en [formato.md](../../pruebas_py/grabacion/formato.md). Los 80 de `parche`, `anillo` y `ambiente` ya tienen su `.raw` en la `outputs` de cada carpeta. `amb_1.wav` sigue suelto en `grabacion` y no se convirtió. El tono `pruebas_py/sonidos/tono.wav` cumple el contrato y no es una clase del dataset.

Cumplir el contrato de formato no acepta la toma para entrenar. Eso lo decide la etapa 2, con la forma de onda, el silencio, el clipping y el espectrograma.
