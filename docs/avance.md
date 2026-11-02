# Avance

Registro de lo medido. Una etapa se cierra en `docs/environment.md` (etapa 0) o en el informe de esa etapa. Este archivo solo dice qué está hecho, con qué evidencia, y qué sigue abierto.

Última actualización: 2026-10-31.

## Dónde estamos

Etapa 0, módulo 0A, a medias. Hay puerto USB, herramientas de Espressif en el disco y silicio leído: ESP32-P4 v1.3. No hay tag adoptado por el repo, no hay firmware y no hay flash.

## Hecho

### Puerto de la DFR1172

Evidencia: `notas/0_conectar_placa.md` y la salida de `dmesg`.

| Dato | Valor |
| --- | --- |
| Bus | USB 1-3, controlador `xhci_hcd` |
| VID:PID | `303a:1001` (Espressif, USB JTAG/serial debug unit) |
| `bcdDevice` | 1.02 (revisión del descriptor USB, no del silicio) |
| Número de serie USB | `30:ED:A0:EA:18:26` |
| Nodo volátil | `/dev/ttyACM0` (`cdc_acm`, interfaz 0) |
| Nodo estable | `/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_30:ED:A0:EA:18:26-if00` |
| Variable de laboratorio | `MY_ESP_P4` en `/etc/environment` |
| Permiso | el usuario `angel-dev` está en el grupo `dialout` |

El enlace `by-id` es el que hay que usar. `ttyACM0` cambia si se enchufa otro CDC.

### Host (medido en esta máquina)

| Pieza | Valor |
| --- | --- |
| SO | Linux 7.0.0-38-generic, x86_64 |
| Git | 2.53.0 (`/usr/bin/git`) |
| Python del sistema / Miniconda `(base)` | 3.14.8 |
| `gcc` del host | presente en `/usr/bin/gcc` (compila para esta PC) |
| CMake del host | 4.2.3 en `/usr/bin/cmake` |
| Ninja en un shell sin activar | ausente |
| Docker | `/usr/local/bin/docker` |
| Conda | Miniconda en `~/miniconda3` (directorio del 2026-10-19). `conda init` en `~/.bashrc` pone `(base)` al abrir una terminal. No lo instaló Espressif |

### Instalación Espressif en disco (no adoptada)

La extensión de VS Code apunta a esta ruta en `.vscode/settings.json` (`idf.currentSetup`). El Installation Manager la registró en `~/.espressif/tools/eim_idf.json` con estado `finished`.

| Pieza | Ruta o versión |
| --- | --- |
| ESP-IDF | 6.1.0 en `/home/angel-dev/.espressif/v6.1/esp-idf` |
| Activación | `source /home/angel-dev/.espressif/tools/activate_idf_v6.1.sh` |
| Toolchain RISC-V | `riscv32-esp-elf` `esp-15.2.0_20251204` |
| Ninja de IDF | 1.12.1 en `~/.espressif/tools/ninja/1.12.1/ninja` |
| CMake de IDF | no hay binario propio; el host aporta CMake 4.2.3. IDF 6.1 pide CMake >= 3.22 |
| Python del venv de IDF | `~/.espressif/tools/python/v6.1/venv` → enlace a Miniconda `python3.14` |
| OpenOCD / GDB RISC-V | presentes bajo `~/.espressif/tools/` |
| `esptool` | shim en `~/.espressif/tools/shims/v6.1/` (entra al `PATH` al activar) |

El checker de esta IDF acepta Python >= 3.10 y no declara un tope. `detect_python.sh` lista intérpretes hasta 3.13.

El virtualenv lo generó el ESP-IDF Installation Manager (EIM), el 2026-10-25. No lo creó este repositorio. `pyvenv.cfg` registra el comando `~/miniconda3/bin/python3 -m venv ~/.espressif/tools/python/v6.1/venv`: usó el Python de Miniconda porque era el que estaba primero en el `PATH`. La carpeta se llama `venv` porque así la nombra el EIM. Python copia ese nombre de carpeta al prompt, y por eso dice `(venv)` y no "esp".

Entrar y salir, en la terminal donde se compila o se flashea:

```bash
source /home/angel-dev/.espressif/tools/activate_idf_v6.1.sh
source /home/angel-dev/.espressif/tools/deactivate_idf_v6.1.sh
```

El primer script lo generó el EIM y activa toolchain, `IDF_PATH` y ese Python. El segundo, también del EIM, deshace las dos cosas. `deactivate` a secas solo suelta el Python y deja el compilador RISC-V en el `PATH`. La extensión de VS Code ejecuta la misma activación en su terminal de ESP-IDF; una terminal común no.

Activación comprobada el 2026-10-31, en un shell con el script cargado:

| Comando | Salida |
| --- | --- |
| `idf.py --version` | ESP-IDF v6.1 |
| `cmake --version` | 4.2.3 (el del host) |
| `ninja --version` | 1.12.1 |
| `riscv32-esp-elf-gcc --version` | 15.2.0 (`esp-15.2.0_20251204`) |
| `IDF_PATH` | `/home/angel-dev/.espressif/v6.1/esp-idf` |
| `IDF_PYTHON_ENV_PATH` | `/home/angel-dev/.espressif/tools/python/v6.1/venv` |

### Silicio leído el 2026-10-31

Comando: `esptool.py --port "$MY_ESP_P4" chip_id` (esptool v5.6.0). El puerto `MY_ESP_P4` resolvió al `by-id` de la DFR1172.

| Dato | Valor |
| --- | --- |
| Chip | ESP32-P4, revisión v1.3 |
| Núcleos | Dual Core + LP Core, 400 MHz |
| Cristal | 40 MHz |
| USB | USB-Serial/JTAG |
| MAC | `30:ed:a0:ea:18:26` (igual al serial USB) |

`esptool` avisó que el nombre `esptool.py` y el comando `chip_id` están deprecados. La próxima lectura usa `esptool chip-id`. El P4 no tiene chip-id distinto de la MAC; la línea útil es `revision v1.3`. El reset final por RTS es el cierre normal del comando.

En IDF 6.1.0, `components/esp_hw_support/port/esp32p4/Kconfig.hw_support` parte el soporte en dos familias que no se mezclan: revisiones anteriores a v3.0, y revisiones v3.0 o posteriores. El mínimo por defecto es v3.1 (`ESP32P4_REV_MIN_301`). Un binario con ese defecto exige revisión >= v3.1; el bootloader aborta con `chip revision check failed` si encuentra v1.3. Esta placa entra en la otra familia (v0.x y v1.x, tope v1.99), activando `ESP32P4_SELECTS_REV_LESS_V3` y un mínimo de v1.0 o menor.

Eso todavía no está escrito en `sdkconfig` del repo. IDF 6.1.0 alcanza para este silicio solo con esa opción. El tag solo, con el defecto de la IDF, no.

## Abierto

1. Adoptar por escrito la config dorada: IDF 6.1.0 + `ESP32P4_SELECTS_REV_LESS_V3` + mínimo v1.0. Sin eso no se crea el proyecto.
2. Revisión de placa DFR1172 (SKU / serigrafía). Distinta de la revisión de silicio.
3. Doctor de la extensión, o el equivalente por CLI.
4. Firmware mínimo, flash y log por el puerto `MY_ESP_P4`.
5. Módulo 0B: imagen `espressif/idf:<tag>` anclada al mismo IDF, `IDF_TARGET=esp32p4`.
6. Venv de ML, separado del Python de IDF y de Conda `(base)`.
7. Cerrar la etapa en `docs/environment.md`.

## Siguiente paso

Confirmar si se adopta IDF 6.1.0 con soporte de P4 anterior a v3.0. Recién después se crea el proyecto mínimo y se flashea.
