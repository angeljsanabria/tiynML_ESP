# Avance — copia Python

Registro de lo ya ejecutado. El procedimiento está en [plan_python.md](../../plan_python.md).

## Etapa 0. Entorno

Hecho. Conda, entorno `tinyml`, Python 3.12.16. El ejecutable es `C:\Users\angel\miniconda3\envs\tinyml\python.exe`. El detalle está en [environment.md](environment.md).

## Tono de prueba

Archivo: `pruebas_py/sonidos/tono.wav`.

Lo generó `pruebas_py/0_tono.py`, corrido desde `pruebas_py` con el Python 3.12.16 de `tinyml`. El script usa el módulo `wave` de la biblioteca estándar. No se instaló ninguna librería.

El tono es una senoide de 440 Hz, 1 segundo, mono, 16 bits con signo, little-endian, 16 000 Hz. La amplitud es 16000, dentro del rango −32768 a 32767.

Salida del script:

```text
canales: 1
bytes por muestra: 2
frecuencia: 16000
muestras: 16000
bytes de audio: 32000
```

`32000` es `16000 * 2 * 1`. Es el mismo cálculo del bloque de audio del plan original para una toma de 1 segundo.

## Comando de grabación

Hecho el empaquetado. Script: `pruebas_py/1_comando.py`, con `struct` y formato `"<BH"`. El layout y la struct C están en [command_layout.md](command_layout.md).

Salida del script:

```text
bytes del comando: 3
orden: 1
duracion_s: 1
muestras: 16000
bytes de audio: 32000
```

La orden 1 y la duración de 1 segundo se recuperan iguales. Esos 32000 bytes son los del tono de `pruebas_py/sonidos/tono.wav`.

## Payload en bruto

Hecho. `pruebas_py/2_raw.py` se corrió desde `pruebas_py` con el Python de `tinyml`. Leyó `sonidos/tono.wav` y escribió el PCM, sin encabezado, en `sonidos/tono.raw`. La duración salió del comando.

Salida del script:

```text
orden: 1
duracion_s: 1
canales: 1
bytes por muestra: 2
frecuencia: 16000
muestras: 16000
bytes del raw: 32000
bytes esperados: 32000
```

El `.raw` mide lo mismo que el payload del seno. Es el bloque de 1 segundo del plan original.

## Firma del tono

Hecho. `pruebas_py/3_firma.py` se corrió desde `pruebas_py` con el Python de `tinyml`. NumPy 2.5.4, fijado en `pruebas_py/requirements.txt`, calculó la FFT del `.raw`.

Salida del script:

```text
muestras: 16000
frecuencia del pico: 440.0
```

El pico cae en 440 Hz. Es la frecuencia del seno que generó `0_tono.py`. Con 16000 muestras y 16000 Hz, cada bin mide 1 Hz.

## Scripts para una grabación

Los que leen una toma quedaron con parámetro de archivo y salida `output_n` junto a ese archivo.

| Orden | Script | Entrada | Salida |
| --- | --- | --- | --- |
| 1 | `pruebas_py/2_raw_process_1.py` | un WAV | `output_1.raw` junto a ese archivo |
| 1, por carpeta | `pruebas_py/2_raw_carpeta_process_1.py` | carpeta | `carpeta/outputs/<nombre>.raw` |
| 2 | `pruebas_py/3_firma_process_2.py` | `.raw` | `output_2.txt` |
| 3 | `pruebas_py/4_forma_process_3.py` | `.raw` | `output_3.png` |

`0_tono.py` sigue generando el seno de prueba. `1_comando.py` sigue armando el comando de 3 bytes. Ninguno de los dos lee una grabación.

## Cadena del tono

Hecha, desde `pruebas_py`, con el Python de `tinyml`.

```text
entrada: sonidos\tono.wav
salida: sonidos\output_1.raw
canales: 1
bytes por muestra: 2
frecuencia: 16000
muestras: 16000
bytes del raw: 32000
contrato: True
salida: sonidos\output_2.txt
muestras: 16000
frecuencia del pico: 440.0
salida: sonidos\output_3.png
```

`output_1.raw` es el payload. `output_2.txt` confirma el seno de 440 Hz. `output_3.png` es la forma de onda de los primeros 10 ms.

## Captura

El formato y el motivo están en [audio_capture.md](audio_capture.md): WAV y `.raw` mono, 16 bits con signo, little-endian, 16 000 Hz. Es el PCM que el I2S de la FireBeetle entrega después del micrófono PDM.

## Clases

El conjunto cerrado para el modelo es el bombo legüero: golpe al parche (`PARCHE`), golpe al anillo (`ANILLO`) y sonido ambiente (`AMBIENTE`). Quedó escrito en `plan_python.md`, `plan.md` y `audio_capture.md`.

## PCM de las grabaciones

Hecho. Desde `pruebas_py`, con el entorno `tinyml` activo, `2_raw_carpeta_process_1.py` convirtió los WAV de cada clase. El script y el destino de cada `.raw` están en [audio_capture.md](audio_capture.md). Las duraciones están en [formato.md](../../pruebas_py/grabacion/formato.md).

```text
python 2_raw_carpeta_process_1.py grabacion/parche
archivos: 30
cumplen: 30
no_cumplen: 0

python 2_raw_carpeta_process_1.py grabacion/anillo
archivos: 30
cumplen: 30
no_cumplen: 0

python 2_raw_carpeta_process_1.py grabacion/ambiente
archivos: 20
cumplen: 20
no_cumplen: 0
```

Cada archivo salió con 1 canal, 2 bytes por muestra, 16 000 Hz y `contrato: True`. El `.raw` quedó en `outputs` dentro de la misma carpeta, con el nombre del WAV. `amb_1.wav` no entró en estas tres corridas.

## Notebook de firma

`pruebas_py/firma.ipynb` abre con el Python de `tinyml`. `ipykernel` 7.4.0 se instaló desde `pruebas_py` con `python -m pip install -r requirements.txt`. La notebook lee los `.raw` de `carpeta/outputs/` y dibuja el histograma de la clase y, por toma, la forma de onda y el histograma. La carpeta se cambia en `CARPETA`.

## Siguiente

Seguir en la etapa 2 de [plan_python.md](../../plan_python.md). Mirar `parche`, `anillo` y `ambiente` en la notebook. Falta contar clipping y silencio, ver el espectrograma y escribir qué tomas se aceptan. El formato válido no alcanza para aceptarlas.
