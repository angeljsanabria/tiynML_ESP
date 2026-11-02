# Contenedores y config unica ESP32-P4

## Links

- Spec Dev Containers: https://containers.dev/
- Referencia (Compose + `espressif/idf`, otro chip): https://github.com/nicoriostaurasi/CESE-IDS-ESP32_LORA_BEACON_APP

## Uso en este proyecto

El plan adopta el enfoque del repo de referencia (imagen oficial anclada + Compose + overlay serial) como **modulo 0B**: una sola configuracion de ESP-IDF para la DFR1172 y la revision de silicio de *esta* unidad P4 (puede ser antigua).

- No copiar el tag ni el `IDF_TARGET` del ejemplo CESE (`esp32s3` / `v5.3.5`).
- Elegir `espressif/idf:<tag>` que soporte ESP32-P4 **y** el silicio medido; documentarlo en `docs/environment.md`.
- El contenedor congela la toolchain; no sustituye entender CMake/Ninja/gcc cruzado (modulo 0A).
- ML (venv Python) sigue fuera de la imagen IDF.

Detalle operativo: `plan.md`, etapa 0, modulo 0B.
