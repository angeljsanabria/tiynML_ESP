# 4_forma_process_3.py
# Tercer paso. Dibuja los primeros 10 ms de un PCM .raw.
# La figura queda en output_3.png, junto al archivo.
#
# Entorno: PowerShell de Windows.
#   conda activate tinyml
#   cd pruebas_py
#   python -m pip install -r requirements.txt
#   python 4_forma_process_3.py sonidos/output_1.raw
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FRECUENCIA_HZ = 16000
VENTANA_S = 0.010

parser = argparse.ArgumentParser()
parser.add_argument("archivo")
args = parser.parse_args()

entrada = Path(args.archivo)
salida = entrada.parent / "output_3.png"

pcm = np.fromfile(entrada, dtype="<i2")
n = min(int(FRECUENCIA_HZ * VENTANA_S), pcm.size)
tiempo_ms = np.arange(n) * 1000.0 / FRECUENCIA_HZ

plt.plot(tiempo_ms, pcm[:n])
plt.xlabel("tiempo (ms)")
plt.ylabel("muestra")
plt.title(entrada.stem)
plt.tight_layout()
plt.savefig(salida)
print("salida:", salida)
plt.show()
