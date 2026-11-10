# 0_tono.py
# Genera un tono seno de 440 Hz y lo guarda en sonidos/tono.wav.
# PCM mono, 16 bits con signo, little-endian, 16000 Hz, 1 segundo.
# Esas muestras son el payload. El WAV les agrega un encabezado.
#
# Entorno: PowerShell de Windows.
#   conda activate tinyml
#   cd pruebas_py
#   python 0_tono.py
import math
import struct
import wave

FRECUENCIA_HZ = 16000
DURACION_S = 1
CANALES = 1
BYTES_POR_MUESTRA = 2
TONO_HZ = 440

n_muestras = FRECUENCIA_HZ * DURACION_S
muestras = []
for n in range(n_muestras):
    valor = int(16000 * math.sin(2 * math.pi * TONO_HZ * n / FRECUENCIA_HZ))
    muestras.append(valor)

ruta = "sonidos/tono.wav"
with wave.open(ruta, "wb") as w:
    w.setnchannels(CANALES)
    w.setsampwidth(BYTES_POR_MUESTRA)
    w.setframerate(FRECUENCIA_HZ)
    w.writeframes(struct.pack("<" + "h" * n_muestras, *muestras))

with wave.open(ruta, "rb") as w:
    print("canales:", w.getnchannels())
    print("bytes por muestra:", w.getsampwidth())
    print("frecuencia:", w.getframerate())
    print("muestras:", w.getnframes())

print("bytes de audio:", n_muestras * CANALES * BYTES_POR_MUESTRA)