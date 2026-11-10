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
| 1 | `pruebas_py/2_raw_process_1.py` | WAV | `output_1.raw` |
| 2 | `pruebas_py/3_firma_process_2.py` | `.raw` | `output_2.txt` |
| 3 | `pruebas_py/4_forma_process_3.py` | `.raw` | `output_3.png` |

`0_tono.py` sigue generando el seno de prueba. `1_comando.py` sigue armando el comando de 3 bytes. Ninguno de los dos lee una grabación.

## Siguiente

Correr la cadena con el tono, para comprobar los nombres nuevos:

```text
python 2_raw_process_1.py sonidos/tono.wav
python 3_firma_process_2.py sonidos/output_1.raw
python 4_forma_process_3.py sonidos/output_1.raw
```
