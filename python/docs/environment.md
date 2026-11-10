# Entorno Python

Registro del paso 0 de `plan_python.md`. Las librerías de la sección 2 de ese plan se anotan acá cuando un script las use.

- Terminal: PowerShell de Windows. La terminal de Ubuntu en WSL no tiene conda.
- Gestor: conda
- Prefijo de conda: `C:\Users\angel\miniconda3`
- Nombre del entorno: `tinyml`
- Python: 3.12.16
- Ejecutable: `C:\Users\angel\miniconda3\envs\tinyml\python.exe`

Comprobación hecha con:

```powershell
conda run -n tinyml python -c "import sys; print(sys.executable); print(sys.version)"
```

Salida:

```text
C:\Users\angel\miniconda3\envs\tinyml\python.exe
3.12.16 | packaged by Anaconda, Inc. | (main, Oct 26 2026, 20:13:05) [MSC v.1942 64 bit (AMD64)]
```

El entorno anterior `tiynml` fue eliminado. El nombre que queda es `tinyml`.

## Librerías fijadas

El archivo es `pruebas_py/requirements.txt`. Se instala desde `pruebas_py` con `python -m pip install -r requirements.txt`. Cada librería nueva se agrega ahí con versión exacta.

| Librería | Versión fijada | La usa |
| --- | --- | --- |
| numpy | 2.5.4 | `pruebas_py/3_firma_process_2.py`, FFT de un `.raw` |
| matplotlib | 3.11.2 | `pruebas_py/4_forma_process_3.py`, forma de onda de un `.raw` |
| ipykernel | 7.4.0 | `pruebas_py/firma.ipynb`, para abrir la notebook con el Python de `tinyml`. Solo corre en la PC |

## Firmware

Versiones pendientes de la etapa 0 de `plan.md`.

| Componente | Versión | Rol |
| --- | --- | --- |
| ESP-IDF | pendiente | Firmware y periféricos |
| FreeRTOS | pendiente | Tareas y colas |
| esp-dsp | pendiente | Ventana de Hann y FFT |
| esp-nn | pendiente | Kernels, si el runtime de la etapa 7 lo usa |
| ESP-TFLite-Micro | pendiente | Runtime alternativo de la etapa 7 de `plan.md` |
