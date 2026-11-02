#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "test_target";

void app_main(void)
{
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_NUM_3),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };

    gpio_config(&io_conf);

    int nivel = 0;

    while (1) {
        nivel = !nivel;

        if (nivel) {
            ESP_LOGI(TAG, "LED encendido");
        } else {
            ESP_LOGI(TAG, "LED apagado");
        }

        gpio_set_level(GPIO_NUM_3, nivel);
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
}
