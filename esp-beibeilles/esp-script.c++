#include <HX711.h>

#define HX711_DT 4
#define HX711_SCK 5

HX711 scale;

void setup()
{
    Serial.begin(115200);

    scale.begin(
        HX711_DT,
        HX711_SCK
    );

    delay(2000);

    Serial.println("HX711 READY");
}

void loop()
{
    if (scale.is_ready())
    {
        long raw = scale.read();

        // =====================================================
        // TODO : à supprimer plus tard - test
        //
        // Permet de vérifier si le HX711 dérive
        // sans aucune calibration.
        //
        // Si cette valeur dérive fortement
        // alors le problème est matériel.
        // =====================================================
        Serial.print("RAW=");
        Serial.println(raw);
    }
    else
    {
        Serial.println("HX711 NOT READY");
    }

    delay(1000);
}