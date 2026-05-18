import requests

payload = {
    "device_serial": "ESP32-RUCHE-001",
    "measurements": [
        {
            "type": "weight",
            "value": 12.4,
            "hive_level": 1,
        },
        {
            "type": "temperature",
            "value": 34.1,
        },
    ],
}

response = requests.post(
    "http://79.137.34.118/iot/ingest",
    json=payload,
)

print(response.json())