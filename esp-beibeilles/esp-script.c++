#include <ArduinoJson.h>
#include <HX711.h>
#define HX711_DT 4
#define HX711_SCK 5

HX711 scale;

// =====================================================
// IDENTIFIANT UNIQUE DE L'ESP32
//
// Chaque ESP32 possède un identifiant gravé en usine.
//
// Nous allons l'utiliser comme préfixe pour construire
// les identifiants de tous les capteurs.
//
// Exemple :
//
// ESP = A0B7651F92CC
//
// donnera
//
// A0B7651F92CC:HX711-1
// A0B7651F92CC:BME280-1
//
// Ainsi l'identifiant est garanti unique.
// =====================================================

String espUid;

// =====================================================
// DESCRIPTION DES CAPTEURS
//
// Ici on décrit TOUS les capteurs branchés.
//
// Plus tard on pourra en avoir plusieurs.
//
// Il suffira d'ajouter une ligne.
//
// Le reste du programme ne changera pas.
//
// =====================================================

struct SensorDefinition
{
    const char *slot;
    const char *type;
};

SensorDefinition sensors[] =
    {
        {"HX711-1",
         "weight"},
};

void setup()
{
    Serial.begin(115200);

    scale.begin(
        HX711_DT,
        HX711_SCK);

    delay(1000);

    // ============================================
    // Lecture de l'identifiant matériel unique
    // de l'ESP32.
    //
    // Cette valeur est gravée en usine.
    // Deux ESP32 n'auront jamais la même.
    // ============================================

    uint64_t chipId =
        ESP.getEfuseMac();

    char uid[13];

    sprintf(
        uid,
        "%04X%08X",
        (uint16_t)(chipId >> 32),
        (uint32_t)chipId);

    espUid = String(uid);

    Serial.println("READY");
}

// =====================================================
// Construit un identifiant unique de capteur.
//
// Exemple :
//
// ESP
// A0B7651F92CC
//
// +
// HX711-1
//
// =>
//
// A0B7651F92CC:HX711-1
//
// =====================================================

String buildSensorSerial(
    const char *slot)
{
    return espUid + ":" + slot;
}

void loop()
{
    if (!scale.is_ready())
    {
        delay(1000);
        return;
    }

    long raw =
        scale.read();

    StaticJsonDocument<256> doc;

    // ============================================
    // Chaque payload correspond à UN capteur.
    //
    // Ce sera beaucoup plus simple côté API.
    // ============================================

    doc["device_serial"] =
        buildSensorSerial(
            sensors[0].slot);

    JsonArray measurements =
        doc.createNestedArray(
            "measurements");

    JsonObject measurement =
        measurements.createNestedObject();

    measurement["type"] =
        sensors[0].type;

    measurement["value"] =
        raw;

    serializeJson(
        doc,
        Serial);

    Serial.println();

    delay(1000);
}