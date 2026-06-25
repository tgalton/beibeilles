# =========================================================
# TESTS DU SERVICE D'INGESTION IOT
# =========================================================
#
# Ce service constitue le point d'entrée principal
# des données provenant des Raspberry Pi installés
# sur les ruches.
#
# Son rôle est de transformer un payload JSON reçu
# depuis le réseau en objets SQLAlchemy persistés
# dans la table MeasurementRaw.
#
# =========================================================
# FLUX COMPLET D'UNE MESURE
# =========================================================
#
# Raspberry Pi
#        │
#        ▼
# POST /measurements/ingest
#        │
#        ▼
# IoTIngest (Pydantic)
#        │
#        ▼
# iot_service.ingest_measurements()
#        │
#        ▼
# MeasurementRaw
#        │
#        ▼
# PostgreSQL / TimescaleDB
#        │
#        ▼
# Service d'agrégation 5 minutes
#        │
#        ▼
# Dashboards Plotly
#
# Toute erreur dans ce service provoque donc
# une perte potentielle de données capteurs.
#
# =========================================================
# RESPONSABILITÉS DU SERVICE
# =========================================================
#
# Le service doit :
#
# 1. retrouver ou créer automatiquement
#    le capteur émetteur
#
# 2. transformer les objets Pydantic
#    en modèles SQLAlchemy
#
# 3. rattacher correctement chaque mesure
#    au capteur correspondant
#
# 4. conserver le timestamp réel envoyé
#    par le Raspberry
#
# 5. effectuer une insertion batch
#    optimisée en base de données
#
# =========================================================
# CRÉATION AUTOMATIQUE DES CAPTEURS
# =========================================================
#
# Les Raspberry sont identifiés par leur
# numéro de série :
#
# Exemple :
#
# ESP32-HIVE-001
#
# Lorsqu'un appareil envoie des données :
#
# - s'il existe déjà :
#       réutilisation
#
# - s'il n'existe pas :
#       création automatique
#
# Cela permet un déploiement très simple :
#
# - branchement du Raspberry
# - première émission
# - enregistrement automatique
#
# sans intervention manuelle.
#
# =========================================================
# CONSERVATION DU TIMESTAMP D'ORIGINE
# =========================================================
#
# Une contrainte importante du système est
# la gestion des pertes réseau.
#
# Exemple :
#
# 14:00
# Raspberry mesure une température.
#
# 14:00 → 14:20
# Wi-Fi indisponible.
#
# 14:21
# Le Raspberry renvoie toutes les mesures
# stockées localement.
#
# Dans ce cas :
#
# la mesure doit conserver son timestamp
# réel (14:00)
#
# et non l'heure de réception (14:21).
#
# Sans cela :
#
# - les graphiques seraient faux
# - les agrégations seraient incorrectes
# - l'historique serait corrompu
#
# =========================================================
# FALLBACK DE SÉCURITÉ
# =========================================================
#
# Si aucun timestamp n'est fourni,
# le serveur utilise automatiquement
# l'heure UTC actuelle.
#
# Cela garantit que :
#
# - la donnée reste exploitable
# - l'insertion ne plante pas
# - l'agrégation future fonctionne
#
# =========================================================
# INSERTION BATCH
# =========================================================
#
# Une requête IoT peut contenir plusieurs
# mesures :
#
# {
#   "device_serial": "...",
#   "measurements": [
#       ...,
#       ...,
#       ...
#   ]
# }
#
# Le service construit l'ensemble des objets
# MeasurementRaw puis effectue une seule
# insertion SQL.
#
# Cela réduit :
#
# - le nombre de commits
# - les temps de réponse
# - la charge PostgreSQL
#
# Ce comportement est essentiel pour
# supporter plusieurs ruches simultanément.
#
# =========================================================
# OBJECTIFS DES TESTS
# =========================================================
#
# Les tests doivent vérifier :
#
# - la récupération du capteur existant
# - la création automatique d'un capteur
# - la transformation correcte du payload
# - l'association sensor_device_id
# - la conservation du timestamp fourni
# - le fallback UTC si absent
# - la création de plusieurs mesures
# - la transmission correcte au repository
#
# Toute régression dans ce service
# impactera immédiatement :
#
# - la collecte IoT
# - les données RAW
# - l'agrégation 5 minutes
# - les dashboards
#
# Il s'agit donc de l'un des services les plus
# critiques de l'application, avec le service
# d'agrégation.
# =========================================================

from datetime import UTC
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

from app.models.measurement_raw import MeasurementRaw
from app.models.sensor_device import SensorDevice

from app.schemas.iot_ingest import IoTIngest
from app.schemas.iot_ingest import IoTMeasurement

from app.services import iot_service


# =========================================================
# Helpers
# =========================================================


def fake_device() -> SensorDevice:

    device = SensorDevice()

    device.id = 42
    device.name = "ESP32 Test"
    device.serial_number = "ABC123"

    return device


def create_payload(
    measurements: list[IoTMeasurement],
) -> IoTIngest:

    return IoTIngest(
        device_serial="ABC123",
        measurements=measurements,
    )


# =========================================================
# Vérifie que le service recherche/crée le device
# =========================================================
@patch(
    "app.services.iot_service.sensor_device_repository.get_or_create_by_serial",
)
@patch(
    "app.services.iot_service.measurement_raw_repository.create_many",
)
def test_ingest_measurements_calls_get_or_create(
    mock_create_many: Mock,
    mock_get_device: Mock,
) -> None:

    mock_get_device.return_value = fake_device()

    payload = create_payload(
        [
            IoTMeasurement(
                type="temperature",
                value=21.5,
            ),
        ],
    )

    iot_service.ingest_measurements(
        db=Mock(),
        payload=payload,
    )

    mock_get_device.assert_called_once()


# =========================================================
# Vérifie le serial transmis
# =========================================================
@patch(
    "app.services.iot_service.sensor_device_repository.get_or_create_by_serial",
)
@patch(
    "app.services.iot_service.measurement_raw_repository.create_many",
)
def test_ingest_measurements_passes_serial(
    mock_create_many: Mock,
    mock_get_device: Mock,
) -> None:

    mock_get_device.return_value = fake_device()

    payload = create_payload(
        [
            IoTMeasurement(
                type="temperature",
                value=21.5,
            ),
        ],
    )

    iot_service.ingest_measurements(
        db=Mock(),
        payload=payload,
    )

    assert mock_get_device.call_args.kwargs["serial_number"] == "ABC123"


# =========================================================
# Vérifie création d'une mesure
# =========================================================
@patch(
    "app.services.iot_service.sensor_device_repository.get_or_create_by_serial",
)
@patch(
    "app.services.iot_service.measurement_raw_repository.create_many",
)
def test_ingest_measurements_creates_measurement(
    mock_create_many: Mock,
    mock_get_device: Mock,
) -> None:

    mock_get_device.return_value = fake_device()

    payload = create_payload(
        [
            IoTMeasurement(
                type="temperature",
                value=22.1,
            ),
        ],
    )

    iot_service.ingest_measurements(
        db=Mock(),
        payload=payload,
    )

    measurements = mock_create_many.call_args.kwargs["measurements"]

    assert len(measurements) == 1

    assert isinstance(
        measurements[0],
        MeasurementRaw,
    )


# =========================================================
# Vérifie plusieurs mesures
# =========================================================
@patch(
    "app.services.iot_service.sensor_device_repository.get_or_create_by_serial",
)
@patch(
    "app.services.iot_service.measurement_raw_repository.create_many",
)
def test_ingest_measurements_multiple_measurements(
    mock_create_many: Mock,
    mock_get_device: Mock,
) -> None:

    mock_get_device.return_value = fake_device()

    payload = create_payload(
        [
            IoTMeasurement(
                type="temperature",
                value=20,
            ),
            IoTMeasurement(
                type="humidity",
                value=70,
            ),
            IoTMeasurement(
                type="co2",
                value=450,
            ),
        ],
    )

    iot_service.ingest_measurements(
        db=Mock(),
        payload=payload,
    )

    measurements = mock_create_many.call_args.kwargs["measurements"]

    assert len(measurements) == 3


# =========================================================
# Vérifie propagation sensor_device_id
# =========================================================
@patch(
    "app.services.iot_service.sensor_device_repository.get_or_create_by_serial",
)
@patch(
    "app.services.iot_service.measurement_raw_repository.create_many",
)
def test_ingest_measurements_sets_sensor_device_id(
    mock_create_many: Mock,
    mock_get_device: Mock,
) -> None:

    mock_get_device.return_value = fake_device()

    payload = create_payload(
        [
            IoTMeasurement(
                type="temperature",
                value=21,
            ),
        ],
    )

    iot_service.ingest_measurements(
        db=Mock(),
        payload=payload,
    )

    measurement = mock_create_many.call_args.kwargs["measurements"][0]

    assert measurement.sensor_device_id == 42


# =========================================================
# Vérifie propagation hive_level_id
# =========================================================
@patch(
    "app.services.iot_service.sensor_device_repository.get_or_create_by_serial",
)
@patch(
    "app.services.iot_service.measurement_raw_repository.create_many",
)
def test_ingest_measurements_sets_hive_level(
    mock_create_many: Mock,
    mock_get_device: Mock,
) -> None:

    mock_get_device.return_value = fake_device()

    payload = create_payload(
        [
            IoTMeasurement(
                type="temperature",
                value=21,
                hive_level_id=5,
            ),
        ],
    )

    iot_service.ingest_measurements(
        db=Mock(),
        payload=payload,
    )

    measurement = mock_create_many.call_args.kwargs["measurements"][0]

    assert measurement.hive_level_id == 5


# =========================================================
# Vérifie conservation timestamp
# =========================================================
@patch(
    "app.services.iot_service.sensor_device_repository.get_or_create_by_serial",
)
@patch(
    "app.services.iot_service.measurement_raw_repository.create_many",
)
def test_ingest_measurements_preserves_timestamp(
    mock_create_many: Mock,
    mock_get_device: Mock,
) -> None:

    timestamp = datetime(
        2026,
        1,
        1,
        12,
        0,
        tzinfo=UTC,
    )

    mock_get_device.return_value = fake_device()

    payload = create_payload(
        [
            IoTMeasurement(
                type="temperature",
                value=21,
                measured_at=timestamp,
            ),
        ],
    )

    iot_service.ingest_measurements(
        db=Mock(),
        payload=payload,
    )

    measurement = mock_create_many.call_args.kwargs["measurements"][0]

    assert measurement.measured_at == timestamp


# =========================================================
# Vérifie type conservé
# =========================================================
@patch(
    "app.services.iot_service.sensor_device_repository.get_or_create_by_serial",
)
@patch(
    "app.services.iot_service.measurement_raw_repository.create_many",
)
def test_ingest_measurements_preserves_type(
    mock_create_many: Mock,
    mock_get_device: Mock,
) -> None:

    mock_get_device.return_value = fake_device()

    payload = create_payload(
        [
            IoTMeasurement(
                type="weight",
                value=38.7,
            ),
        ],
    )

    iot_service.ingest_measurements(
        db=Mock(),
        payload=payload,
    )

    measurement = mock_create_many.call_args.kwargs["measurements"][0]

    assert measurement.type == "weight"


# =========================================================
# Vérifie valeur conservée
# =========================================================
@patch(
    "app.services.iot_service.sensor_device_repository.get_or_create_by_serial",
)
@patch(
    "app.services.iot_service.measurement_raw_repository.create_many",
)
def test_ingest_measurements_preserves_value(
    mock_create_many: Mock,
    mock_get_device: Mock,
) -> None:

    mock_get_device.return_value = fake_device()

    payload = create_payload(
        [
            IoTMeasurement(
                type="weight",
                value=38.7,
            ),
        ],
    )

    iot_service.ingest_measurements(
        db=Mock(),
        payload=payload,
    )

    measurement = mock_create_many.call_args.kwargs["measurements"][0]

    assert measurement.value == 38.7


# =========================================================
# Vérifie appel create_many
# =========================================================
@patch(
    "app.services.iot_service.sensor_device_repository.get_or_create_by_serial",
)
@patch(
    "app.services.iot_service.measurement_raw_repository.create_many",
)
def test_ingest_measurements_calls_create_many(
    mock_create_many: Mock,
    mock_get_device: Mock,
) -> None:

    mock_get_device.return_value = fake_device()

    payload = create_payload(
        [
            IoTMeasurement(
                type="temperature",
                value=20,
            ),
        ],
    )

    iot_service.ingest_measurements(
        db=Mock(),
        payload=payload,
    )

    mock_create_many.assert_called_once()


# =========================================================
# Vérifie retour repository
# =========================================================
@patch(
    "app.services.iot_service.sensor_device_repository.get_or_create_by_serial",
)
@patch(
    "app.services.iot_service.measurement_raw_repository.create_many",
)
def test_ingest_measurements_returns_repository_result(
    mock_create_many: Mock,
    mock_get_device: Mock,
) -> None:

    expected = [
        MeasurementRaw(),
    ]

    mock_get_device.return_value = fake_device()

    mock_create_many.return_value = expected

    payload = create_payload(
        [
            IoTMeasurement(
                type="temperature",
                value=20,
            ),
        ],
    )

    result = iot_service.ingest_measurements(
        db=Mock(),
        payload=payload,
    )

    assert result == expected


# =========================================================
# Cas limite : payload vide
# =========================================================
@patch(
    "app.services.iot_service.sensor_device_repository.get_or_create_by_serial",
)
@patch(
    "app.services.iot_service.measurement_raw_repository.create_many",
)
def test_ingest_measurements_empty_payload(
    mock_create_many: Mock,
    mock_get_device: Mock,
) -> None:

    mock_get_device.return_value = fake_device()

    payload = create_payload([])

    iot_service.ingest_measurements(
        db=Mock(),
        payload=payload,
    )

    measurements = mock_create_many.call_args.kwargs["measurements"]

    assert measurements == []
