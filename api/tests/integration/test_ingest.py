from app.models.measurement_raw import MeasurementRaw
from sqlalchemy import select


def test_raw_ingest_ok(client, integration_context):
    payload = {
        "device_serial": integration_context["sensor_device"].serial_number,
        "measurements": [
            {
                "type": "weight",
                "value": 12.4,
                "hive_level_id": integration_context["hive_level"].id,
            }
        ],
    }

    response = client.post("/measurements/raw/ingest", json=payload)

    assert response.status_code == 200


def test_raw_ingest_creates_measurement(client, integration_context):
    sensor = integration_context["sensor_device"]
    level = integration_context["hive_level"]

    payload = {
        "device_serial": sensor.serial_number,
        "measurements": [
            {
                "type": "weight",
                "value": 10.5,
                "hive_level_id": level.id,
            }
        ],
    }

    response = client.post("/measurements/raw/ingest", json=payload)

    assert response.status_code == 200


def test_raw_ingest_multiple_measurements(
    client,
    integration_context,
):
    sensor = integration_context["sensor_device"]
    level = integration_context["hive_level"]

    payload = {
        "device_serial": sensor.serial_number,
        "measurements": [
            {
                "type": "weight",
                "value": 12.4,
                "hive_level_id": level.id,
            },
            {
                "type": "temperature",
                "value": 34.2,
                "hive_level_id": level.id,
            },
        ],
    }

    response = client.post(
        "/measurements/raw/ingest",
        json=payload,
    )

    assert response.status_code == 200


def test_raw_ingest_persists_measurement(
    client,
    db,
    integration_context,
):
    sensor = integration_context["sensor_device"]
    level = integration_context["hive_level"]

    payload = {
        "device_serial": sensor.serial_number,
        "measurements": [
            {
                "type": "weight",
                "value": 12.4,
                "hive_level_id": level.id,
            }
        ],
    }

    response = client.post(
        "/measurements/raw/ingest",
        json=payload,
    )

    assert response.status_code == 200

    # Recharge les données depuis PostgreSQL
    db.expire_all()

    measurement = db.execute(select(MeasurementRaw)).scalar_one_or_none()

    assert measurement is not None

    assert measurement.value == 12.4
    assert measurement.type == "weight"
    assert measurement.sensor_device_id == sensor.id
    assert measurement.hive_level_id == level.id
