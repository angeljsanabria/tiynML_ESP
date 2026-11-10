# 2_raw_carpeta_process_1.py
# Misma conversion que el proceso 1, para todos los WAV de una carpeta.
# Crea carpeta/outputs y guarda un .raw por archivo, con el mismo nombre.
# Imprime el contrato de cada uno. No entra en subcarpetas.
#
# Entorno: PowerShell de Windows.
#   conda activate tinyml
#   cd pruebas_py
#   python 2_raw_carpeta_process_1.py grabacion/parche
import argparse
import wave
from pathlib import Path

CONTRATO_HZ = 16000
CONTRATO_CANALES = 1
CONTRATO_BYTES = 2

parser = argparse.ArgumentParser()
parser.add_argument("carpeta")
args = parser.parse_args()

carpeta = Path(args.carpeta)
salida_dir = carpeta / "outputs"
salida_dir.mkdir(exist_ok=True)

wavs = sorted(p for p in carpeta.iterdir() if p.is_file() and p.suffix.lower() == ".wav")
cumplen = 0

for entrada in wavs:
    salida = salida_dir / (entrada.stem + ".raw")
    with wave.open(str(entrada), "rb") as w:
        canales = w.getnchannels()
        bytes_por_muestra = w.getsampwidth()
        frecuencia = w.getframerate()
        muestras = w.getnframes()
        pcm = w.readframes(muestras)
    salida.write_bytes(pcm)
    contrato = (
        canales == CONTRATO_CANALES
        and bytes_por_muestra == CONTRATO_BYTES
        and frecuencia == CONTRATO_HZ
    )
    if contrato:
        cumplen += 1
    print("entrada:", entrada)
    print("salida:", salida)
    print("canales:", canales)
    print("bytes por muestra:", bytes_por_muestra)
    print("frecuencia:", frecuencia)
    print("muestras:", muestras)
    print("bytes del raw:", len(pcm))
    print("contrato:", contrato)
    print()

print("archivos:", len(wavs))
print("cumplen:", cumplen)
print("no_cumplen:", len(wavs) - cumplen)
