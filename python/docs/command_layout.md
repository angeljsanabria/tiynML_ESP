# Layout del comando de grabación

Lo arma y lo lee `pruebas_py/1_comando.py` con `struct`, formato `"<BH"`. Little-endian. Tres bytes, sin relleno.

| Offset | Campo | Ancho | Tipo C | Valor de prueba |
| --- | --- | --- | --- | --- |
| 0 | `orden` | 1 | `uint8_t` | 1, grabar |
| 1 | `duracion_s` | 2 | `uint16_t` | segundos de la toma |

La struct que copia el parser UART de la etapa 1 de `plan.md`:

```c
typedef struct __attribute__((packed)) {
    uint8_t orden;
    uint16_t duracion_s;
} comando_grabacion_t;
```

`packed` evita el byte de relleno que el compilador puede insertar entre el campo de 8 bits y el de 16 bits. Sin ese atributo la struct mediría 4 bytes y no coincidiría con los 3 de Python.

La duración recuperada define el bloque de audio: `16000 * 2 * duracion_s` bytes.
