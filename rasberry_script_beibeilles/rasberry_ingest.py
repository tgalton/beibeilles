import requests


payload = {
    "device_serial": "ESP32-RUCHE-001",

    "measurements": [

        {
            "type": "weight",
            "value": 12.4,
            "hive_level_id": 1,
        },

        {
            "type": "temperature",
            "value": 34.1,
        },
    ],
}


response = requests.post(
    "http://79.137.34.118:8000/iot/ingest",
    json=payload,
)

print(response.status_code)

print(response.json())