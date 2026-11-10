# 3_firma_process_2.py
# Segundo paso. Lee el PCM .raw y busca en que frecuencia esta la energia.
# NumPy calcula la FFT. El resultado queda en output_2.txt, junto al archivo.
# La frecuencia de muestreo del proyecto es 16000 Hz.
#
# Entorno: PowerShell de Windows.
#   conda activate tinyml
#   cd pruebas_py
#   python -m pip install -r requirements.txt
#   python 3_firma_process_2.py sonidos/output_1.raw
import argparse
from pathlib import Path

import numpy as np

FRECUENCIA_HZ = 16000

parser = argparse.ArgumentParser()
parser.add_argument("archivo")
args = parser.parse_args()

entrada = Path(args.archivo)
salida = entrada.parent / "output_2.txt"

pcm = np.fromfile(entrada, dtype="<i2")
espectro = np.abs(np.fft.rfft(pcm))
frecuencias = np.fft.rfftfreq(pcm.size, d=1.0 / FRECUENCIA_HZ)
pico = int(np.argmax(espectro))

lineas = (
    "muestras: %s\n" % pcm.size
    + "frecuencia del pico: %s\n" % frecuencias[pico]
)
salida.write_text(lineas, encoding="utf-8")
print("salida:", salida)
print(lineas, end="")
