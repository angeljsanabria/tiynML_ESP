# Formato de las grabaciones

Los 81 WAV de `pruebas_py/grabacion` cumplen el contrato de [audio_capture.md](../../python/docs/audio_capture.md). Todos son PCM sin compresión, 1 canal, 2 bytes por muestra y 16 000 Hz.

La duración no es fija, y eso entra en el plan: el proceso 1 mide el largo de cada archivo. Cada archivo tiene un solo sonido.

| Carpeta | Archivos | Duración |
| --- | --- | --- |
| `parche` | 30 | 1,15 s a 2,18 s |
| `anillo` | 30 | 1,34 s a 2,03 s |
| `ambiente` | 20 | 0,93 s a 2,12 s |
| `amb_1.wav` | 1, suelto en `grabacion` | 20,64 s |
