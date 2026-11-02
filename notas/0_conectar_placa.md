## Check USB device

#### Ver los dispositivos USB reconocidos por el sistema
```
ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null 
```
```
// 2>/dev/null  -> 2 Identifica el flujo de errores, stderr.
//              -> Redirige ese flujo hacia otro destino.
// /dev/null    -> Descarta todo lo que se escribe allí.

```


#### Antes de conectar el dispositivo
```
sudo dmesg -w
```

[  689.543486] usb 1-3: USB disconnect, device number 8                    
                // Se corto la conexion del BUS 1 y PUERTO 3; 
[  691.709449] usb 1-3: new full-speed USB device number 9 using xhci_hcd
[  691.833616] usb 1-3: New USB device found, idVendor=303a, idProduct=1001, bcdDevice= 1.02
                // 303a -> identificador de Espressif; 
[  691.833622] usb 1-3: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[  691.833624] usb 1-3: Product: USB JTAG/serial debug unit
[  691.833625] usb 1-3: Manufacturer: Espressif
[  691.833626] usb 1-3: SerialNumber: 30:ED:A0:EA:18:26
                // serie del chip
[  691.836158] cdc_acm 1-3:1.0: ttyACM0: USB ACM device
                // El driver es cdc_acm y tomo la interfaz "0" y creo "/dev/ttyACM0" para el monitor.

#### Ver nombre estable y Enlace ttyACM* o ttyUSB*
```
ls -l /dev/serial/by-id/
```


#### Ver logs
```
cat /dev/ttyACM0
```

### Identificar USB by-id
```
1)
Conectar un dispositvo USB nuevo.
2)
identifcar el tty* con ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null  o con sudo dmesg -w
3) Identificado el tty; busco el "id" con  ls -l /dev/serial/by-id/

y pudo usar  /dev/serial/by-id/  + "usb-Espressif_USB_JTAG_serial_debug_unit_30:ED:A0:EA:18:26-if00"
para formar  "/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_30:ED:A0:EA:18:26-if00"

4) creo variable entorno:
// temporal:
export MY_ESP_P4="/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_30:ED:A0:EA:18:26-if00"
// en el sistema:
sudo nano /etc/environment

agrego: MY_ESP_P4="/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_30:ED:A0:EA:18:26-if00"

5) Compuebo

echo $MY_ESP_P4
cat $MY_ESP_P4

```


## ESP-IDF


### Activar entorno env de esp
```
source /home/angel-dev/.espressif/tools/activate_idf_v6.1.sh
source /home/angel-dev/.espressif/tools/deactivate_idf_v6.1.sh

```
### Pedir datos a la ROM por USB
```
python -m esptool --port "$MY_ESP_P4" chip-id
    -   ESP32-P4 (revision v1.3)
    - se identifica la version y por lo tanto se debe usar CONFIG_ESP32P4_SELECTS_REV_LESS_V3=y

```


### Configs utiles
```
CONFIG_ESP32P4_SELECTS_REV_LESS_V3=y
CONFIG_ESP32P4_REV_MIN_100=y
CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y
CONFIG_ESP_CONSOLE_USB_SERIAL_JTAG=y
CONFIG_BOOTLOADER_WDT_TIME_MS=15000
```

### Creo proyecto basico a mano
```
1) Crear carpeta
mkdir 0_test_target

2) Crear CMakeLists.txt de la Raiz
touch CMakeLists.txt
-> idf.py toma como proyecto el directorio actual, y ese directorio tiene que tener ese archivo.
-- cmake_minimum_required(VERSION 3.22) exige un CMake de esa versión o más nueva. 
-- include($ENV{IDF_PATH}/tools/cmake/project.cmake) trae el sistema de build de Espressif
-- project(tinyml_esp) tiene que ir después del include. Ahí IDF engancha el target, los componentes y la generación del binario. 

3) crear archiv sdkconfig.defaults
touch sdkconfig.defaults
-> Estas cinco líneas son opciones reales de IDF 6.1 y están en el archivo correcto. idf.py set-target las lee al generar sdkconfig

4) Crear carpeta main/ y app_main.c
touch app_main.c

5) Crear carpeta main/ y su CMakeLists.txt
-- ESP-IDF no compila “todos los .c de la carpeta”. Compila componentes. 
--- n componente es una carpeta con su propio CMakeLists.txt que llama a idf_component_register. La carpeta main es el componente obligatorio: IDF lo busca siempre, al lado del CMakeLists.txt de la raíz. 
--- SRCS es la lista de fuentes de este componente.


Quedando:
esp_codes/
└── 0_test_target/
    ├── CMakeLists.txt
    ├── sdkconfig.defaults
    └── main/
        ├── CMakeLists.txt
        └── app_main.c
```















