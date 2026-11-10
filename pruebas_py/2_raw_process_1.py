# 2_raw_process_1.py
# Primer paso del proceso. Lee un WAV y guarda el PCM en output_1.raw.
# output_1.raw queda junto al archivo, sin el encabezado del WAV.
# Imprime canales, bits, frecuencia y bytes para compararlos con el contrato.
#
# Entorno: PowerShell de Windows.
#   conda activate tinyml
#   cd pruebas_py
#   python 2_raw_process_1.py sonidos/tono.wav
import argparse
import wave
from pathlib import Path

CONTRATO_HZ = 16000
CONTRATO_CANALES = 1
CONTRATO_BYTES = 2

parser = argparse.ArgumentParser()
parser.add_argument("archivo")
args = parser.parse_args()

entrada = Path(args.archivo)
salida = entrada.parent / "output_1.raw"

with wave.open(str(entrada), "rb") as w:
    canales = w.getnchannels()
    bytes_por_muestra = w.getsampwidth()
    frecuencia = w.getframerate()
    muestras = w.getnframes()
    pcm = w.readframes(muestras)

salida.write_bytes(pcm)

print("entrada:", entrada)
print("salida:", salida)
print("canales:", canales)
print("bytes por muestra:", bytes_por_muestra)
print("frecuencia:", frecuencia)
print("muestras:", muestras)
print("bytes del raw:", len(pcm))
print(
    "contrato:",
    canales == CONTRATO_CANALES
    and bytes_por_muestra == CONTRATO_BYTES
    and frecuencia == CONTRATO_HZ,
)
