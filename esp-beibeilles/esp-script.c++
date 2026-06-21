#include <HX711.h>
#include <ArduinoJson.h>

#define HX711_DT 4
#define HX711_SCK 5

#define HIVE_LEVEL_ID 1

const char* DEVICE_SERIAL = "ESP32-RUCHE-001";

HX711 scale;

#define SAMPLE_COUNT 25

float samples[SAMPLE_COUNT];

#define CALIBRATION_FACTOR 1.0f

float median(float* values, int size)
{
    float sorted[SAMPLE_COUNT];

    memcpy(sorted, values, sizeof(float) * size);

    for (int i = 0; i < size - 1; i++)
    {
        for (int j = i + 1; j < size; j++)
        {
            if (sorted[j] < sorted[i])
            {
                float tmp = sorted[i];
                sorted[i] = sorted[j];
                sorted[j] = tmp;
            }
        }
    }

    return sorted[size / 2];
}

float readFilteredWeight()
{
    for (int i = 0; i < SAMPLE_COUNT; i++)
    {
        samples[i] = scale.get_units(1);
        delay(20);
    }

    return median(samples, SAMPLE_COUNT);
}

void setup()
{
    Serial.begin(115200);

    scale.begin(
        HX711_DT,
        HX711_SCK
    );

    delay(1000);

    scale.set_scale(
        CALIBRATION_FACTOR
    );

    Serial.println("Tare...");

    scale.tare();

    delay(2000);

    Serial.println("Ready");
}

void loop()
{
    float weight =
        readFilteredWeight();

    StaticJsonDocument<256> doc;

    doc["device_serial"] =
        DEVICE_SERIAL;

    JsonArray measurements =
        doc.createNestedArray(
            "measurements"
        );

    JsonObject measurement =
        measurements.createNestedObject();

    measurement["type"] =
        "weight";

    measurement["value"] =
        roundf(weight * 100.0f) / 100.0f;

    measurement["hive_level_id"] =
        HIVE_LEVEL_ID;

    serializeJson(
        doc,
        Serial
    );

    Serial.println();

    delay(1000);
}