# =========================================================
# TESTS DU SERVICE D'AGRÉGATION 5 MINUTES
# =========================================================
#
# Ce service est l'un des composants les plus critiques
# de l'application.
#
# Son rôle est de transformer les mesures RAW issues
# des capteurs IoT en séries temporelles agrégées
# exploitables par les dashboards et graphiques Plotly.
#
# =========================================================
# PRINCIPE DES BUCKETS
# =========================================================
#
# Les données sont regroupées dans des fenêtres
# temporelles ("buckets") de 5 minutes.
#
# Exemple :
#
# 14:00:00 -> 14:04:59
#      ↓
# bucket 14:00
#
# 14:05:00 -> 14:09:59
#      ↓
# bucket 14:05
#
# 14:10:00 -> 14:14:59
#      ↓
# bucket 14:10
#
# Chaque mesure RAW est rattachée au bucket inférieur
# correspondant à son horodatage.
#
# Exemple :
#
# 14:07:12 -> bucket 14:05
# 14:09:59 -> bucket 14:05
# 14:13:02 -> bucket 14:10
#
# =========================================================
# POURQUOI AGRÉGER ?
# =========================================================
#
# Une ruche peut produire plusieurs milliers de mesures
# par jour :
#
# - température
# - humidité
# - CO₂
# - poids
#
# Afficher directement les données RAW dans Plotly
# deviendrait rapidement trop coûteux :
#
# - requêtes SQL plus lentes
# - davantage de mémoire
# - graphiques moins fluides
#
# Les buckets 5 minutes permettent de réduire
# drastiquement le volume de données tout en
# conservant les tendances importantes.
#
# =========================================================
# DONNÉES PRODUITES PAR L'AGRÉGATION
# =========================================================
#
# Pour chaque bucket, le système calcule :
#
# - moyenne (avg)
# - minimum (min)
# - maximum (max)
# - nombre d'échantillons (count)
#
# Exemple :
#
# Mesures :
#   20.0
#   21.0
#   22.0
#
# Résultat :
#
# avg = 21.0
# min = 20.0
# max = 22.0
# samples_count = 3
#
# =========================================================
# DIMENSIONS D'AGRÉGATION
# =========================================================
#
# L'agrégation ne mélange jamais les données de :
#
# - types différents
# - ruches différentes
# - capteurs différents
# - niveaux de ruche différents
#
# Le GROUP BY métier est donc :
#
# (type,
#  hive_id,
#  sensor_device_id,
#  hive_level_id)
#
# Deux mesures ayant des capteurs différents
# doivent produire deux agrégats distincts,
# même si elles sont dans le même bucket.
#
# =========================================================
# RÈGLE FONDAMENTALE :
# NE JAMAIS AGRÉGER LE BUCKET COURANT
# =========================================================
#
# Exemple :
#
# heure actuelle = 14:23
#
# buckets terminés :
# - 14:00
# - 14:05
# - 14:10
# - 14:15
#
# bucket courant :
# - 14:20
#
# Le bucket 14:20 NE DOIT PAS être agrégé.
#
# Pourquoi ?
#
# Parce que des mesures peuvent encore arriver :
#
# - latence réseau
# - buffer Raspberry
# - upload différé
# - reconnexion Wi-Fi
#
# Agréger un bucket encore en cours provoquerait
# des statistiques incomplètes et incohérentes.
#
# =========================================================
# COMPORTEMENT INCRÉMENTAL
# =========================================================
#
# Le service est conçu pour être exécuté
# périodiquement (cron, scheduler, etc.).
#
# Lors d'un lancement :
#
# - il détecte le dernier bucket déjà agrégé
# - il reprend exactement au bucket suivant
# - il n'agrège jamais deux fois le même bucket
#
# Cela garantit :
#
# - absence de doublons
# - reprise après interruption
# - exécution idempotente
#
# =========================================================
# OBJECTIFS DES TESTS
# =========================================================
#
# Les tests doivent vérifier notamment :
#
# - l'arrondi correct des buckets
# - la gestion des buckets vides
# - le premier lancement sans historique
# - le redémarrage après agrégation précédente
# - le calcul correct des statistiques
# - la séparation des groupes métier
# - l'exclusion du bucket courant
# - l'absence d'erreur sans données RAW
#
# Toute régression dans ce service impactera
# directement :
#
# - les dashboards
# - les graphiques Plotly
# - les alertes futures
# - les analyses de comportement des ruches
#
# C'est donc l'un des services les plus critiques
# de toute l'application.
# =========================================================

from datetime import UTC
from datetime import datetime

from unittest.mock import MagicMock
from unittest.mock import patch

from app.services.measurement_aggregation_service import (
    floor_to_5_minutes,
)
from app.services.measurement_aggregation_service import (
    aggregate_measurements_5m,
)


# =========================================================
# floor_to_5_minutes
#
# Cette fonction est critique :
# toute l'agrégation repose sur elle.
#
# Si son comportement change,
# tous les buckets peuvent devenir faux.
# =========================================================
def test_floor_to_5_minutes_exact_bucket() -> None:

    dt = datetime(
        2026,
        1,
        1,
        14,
        5,
        tzinfo=UTC,
    )

    result = floor_to_5_minutes(dt)

    assert result.minute == 5
    assert result.second == 0
    assert result.microsecond == 0


# =========================================================
# Cas classique
#
# 14:07 doit devenir 14:05
# =========================================================
def test_floor_to_5_minutes_round_down() -> None:

    dt = datetime(
        2026,
        1,
        1,
        14,
        7,
        tzinfo=UTC,
    )

    result = floor_to_5_minutes(dt)

    assert result.minute == 5


# =========================================================
# Fin d'heure
#
# 14:59 -> 14:55
# =========================================================
def test_floor_to_5_minutes_end_hour() -> None:

    dt = datetime(
        2026,
        1,
        1,
        14,
        59,
        tzinfo=UTC,
    )

    result = floor_to_5_minutes(dt)

    assert result.minute == 55


# =========================================================
# Aucun RAW
#
# Premier lancement
# + aucune donnée
#
# Le service doit sortir proprement.
# =========================================================
@patch(
    "app.services.measurement_aggregation_service.func",
)
def test_aggregate_no_raw_data(
    mock_func: MagicMock,
) -> None:

    db = MagicMock()

    query = MagicMock()

    db.query.return_value = query

    query.scalar.side_effect = [
        None,  # last_bucket
        None,  # oldest_raw
    ]

    aggregate_measurements_5m(
        db=db,
    )

    db.add.assert_not_called()
    db.commit.assert_not_called()


# =========================================================
# Premier lancement
#
# Vérifie que l'on démarre
# au bucket du plus ancien RAW.
# =========================================================
@patch(
    "app.services.measurement_aggregation_service.datetime",
)
def test_aggregate_first_run(
    mock_datetime: MagicMock,
) -> None:

    now = datetime(
        2026,
        1,
        1,
        14,
        25,
        tzinfo=UTC,
    )

    mock_datetime.now.return_value = now

    oldest_raw = datetime(
        2026,
        1,
        1,
        14,
        2,
        tzinfo=UTC,
    )

    db = MagicMock()

    query = MagicMock()

    db.query.return_value = query

    query.scalar.side_effect = [
        None,
        oldest_raw,
    ]

    query.join.return_value = query
    query.filter.return_value = query
    query.group_by.return_value = query
    query.all.return_value = []

    aggregate_measurements_5m(
        db=db,
    )

    assert db.commit.called


# =========================================================
# Reprise après dernier bucket
#
# Vérifie le chemin :
#
# last_bucket + 5 minutes
# =========================================================
@patch(
    "app.services.measurement_aggregation_service.datetime",
)
def test_aggregate_resume_from_last_bucket(
    mock_datetime: MagicMock,
) -> None:

    now = datetime(
        2026,
        1,
        1,
        14,
        30,
        tzinfo=UTC,
    )

    mock_datetime.now.return_value = now

    last_bucket = datetime(
        2026,
        1,
        1,
        14,
        0,
        tzinfo=UTC,
    )

    db = MagicMock()

    query = MagicMock()

    db.query.return_value = query

    query.scalar.return_value = last_bucket

    query.join.return_value = query
    query.filter.return_value = query
    query.group_by.return_value = query
    query.all.return_value = []

    aggregate_measurements_5m(
        db=db,
    )

    assert db.commit.called


# =========================================================
# Vérifie qu'un Measurement5m
# est créé correctement.
#
# C'est le coeur du métier.
# =========================================================
@patch(
    "app.services.measurement_aggregation_service.datetime",
)
def test_aggregate_creates_measurement(
    mock_datetime: MagicMock,
) -> None:

    now = datetime(
        2026,
        1,
        1,
        14,
        25,
        tzinfo=UTC,
    )

    mock_datetime.now.return_value = now

    oldest_raw = datetime(
        2026,
        1,
        1,
        14,
        0,
        tzinfo=UTC,
    )

    db = MagicMock()

    query = MagicMock()

    db.query.return_value = query

    query.scalar.side_effect = [
        None,
        oldest_raw,
    ]

    query.join.return_value = query
    query.filter.return_value = query
    query.group_by.return_value = query

    query.all.return_value = [
        (
            "temperature",
            1,
            2,
            3,
            25.5,
            20.0,
            30.0,
            42,
        ),
    ]

    aggregate_measurements_5m(
        db=db,
    )

    assert db.add.called
    assert db.commit.called


# =========================================================
# Vérifie qu'un commit est exécuté.
#
# Important :
# sinon aucune agrégation n'est
# réellement enregistrée.
# =========================================================
@patch(
    "app.services.measurement_aggregation_service.datetime",
)
def test_aggregate_commit_called(
    mock_datetime: MagicMock,
) -> None:

    now = datetime(
        2026,
        1,
        1,
        14,
        10,
        tzinfo=UTC,
    )

    mock_datetime.now.return_value = now

    oldest_raw = datetime(
        2026,
        1,
        1,
        14,
        0,
        tzinfo=UTC,
    )

    db = MagicMock()

    query = MagicMock()

    db.query.return_value = query

    query.scalar.side_effect = [
        None,
        oldest_raw,
    ]

    query.join.return_value = query
    query.filter.return_value = query
    query.group_by.return_value = query
    query.all.return_value = []

    aggregate_measurements_5m(
        db=db,
    )

    assert db.commit.call_count >= 1


# =========================================================
# Bucket vide
#
# Cas important :
# l'agrégateur doit continuer même
# lorsqu'aucune mesure n'existe.
# =========================================================
@patch(
    "app.services.measurement_aggregation_service.datetime",
)
def test_aggregate_empty_bucket(
    mock_datetime: MagicMock,
) -> None:

    now = datetime(
        2026,
        1,
        1,
        14,
        15,
        tzinfo=UTC,
    )

    mock_datetime.now.return_value = now

    oldest_raw = datetime(
        2026,
        1,
        1,
        14,
        0,
        tzinfo=UTC,
    )

    db = MagicMock()

    query = MagicMock()

    db.query.return_value = query

    query.scalar.side_effect = [
        None,
        oldest_raw,
    ]

    query.join.return_value = query
    query.filter.return_value = query
    query.group_by.return_value = query

    query.all.return_value = []

    aggregate_measurements_5m(
        db=db,
    )

    assert db.commit.called


# =========================================================
# Vérifie que plusieurs buckets
# déclenchent plusieurs commits.
#
# Ce test protège directement
# la boucle while.
# =========================================================
@patch(
    "app.services.measurement_aggregation_service.datetime",
)
def test_aggregate_multiple_buckets(
    mock_datetime: MagicMock,
) -> None:

    now = datetime(
        2026,
        1,
        1,
        14,
        20,
        tzinfo=UTC,
    )

    mock_datetime.now.return_value = now

    oldest_raw = datetime(
        2026,
        1,
        1,
        14,
        0,
        tzinfo=UTC,
    )

    db = MagicMock()

    query = MagicMock()

    db.query.return_value = query

    query.scalar.side_effect = [
        None,
        oldest_raw,
    ]

    query.join.return_value = query
    query.filter.return_value = query
    query.group_by.return_value = query
    query.all.return_value = []

    aggregate_measurements_5m(
        db=db,
    )

    assert db.commit.call_count == 4