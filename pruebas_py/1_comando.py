# 1_comando.py
# Arma el comando de grabacion: orden (1 byte) y duracion en segundos (2 bytes).
# Formato "<BH", little-endian, 3 bytes, igual que comando_grabacion_t.
# La duracion recuperada define las muestras y los bytes de audio.
#
# Entorno: PowerShell de Windows.
#   conda activate tinyml
#   cd pruebas_py
#   python 1_comando.py
import struct

ORDEN_GRABAR = 1
FORMATO = "<BH"
DURACION_S = 1
FRECUENCIA_HZ = 16000
BYTES_POR_MUESTRA = 2

mensaje = struct.pack(FORMATO, ORDEN_GRABAR, DURACION_S)
orden, duracion_s = struct.unpack(FORMATO, mensaje)

n_muestras = FRECUENCIA_HZ * duracion_s
bytes_audio = n_muestras * BYTES_POR_MUESTRA

print("bytes del comando:", len(mensaje))
print("orden:", orden)
print("duracion_s:", duracion_s)
print("muestras:", n_muestras)
print("bytes de audio:", bytes_audio)