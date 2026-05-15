"""
========================================================================
GÉNÉRATEUR DE DONNÉES APIAIRES RÉALISTES
========================================================================

Ce script génère :

- 3 ruches ;
- plusieurs niveaux (corps / hausses) ;
- 1 mois de pesées ;
- des variations réalistes ;
- une miellée progressive ;
- des ajouts de hausses.

Les données sont injectées dans l'API FastAPI.

========================================================================
INSTALLATION
========================================================================

pip install requests

========================================================================
LANCEMENT
========================================================================

python generate_fake_data.py
"""

# ============================================================================
# IMPORTS
# ============================================================================

import math
import random
import time

from datetime import datetime
from datetime import timedelta

import requests


# ============================================================================
# CONFIGURATION GLOBALE
# ============================================================================

# URL de l'API Docker
# IMPORTANT :
# - depuis Docker -> utiliser http://api:8000
# - depuis Windows -> utiliser http://localhost:8000
API_URL = "http://localhost:8000"

# Date de début de génération
START_DATE = datetime(2026, 4, 1, 0, 0, 0)

# Date de fin
END_DATE = datetime(2026, 4, 30, 23, 59, 59)

# Une mesure toutes les 15 minutes
MEASUREMENT_INTERVAL_MINUTES = 15

# ============================================================================
# STOCKAGE DES POIDS ACTUELS
# ============================================================================

"""
Ce dictionnaire est TRÈS important.

Il permet de mémoriser le dernier poids connu
de chaque niveau de ruche.

Sans ça :
- chaque mesure repart de zéro ;
- les courbes sont totalement irréalistes.

Format :

CURRENT_WEIGHTS = {
    level_id: poids_actuel
}
"""
CURRENT_WEIGHTS = {}


# ============================================================================
# HELPERS API
# ============================================================================

def api_post(endpoint: str, payload: dict) -> dict:
    """
    Fonction générique pour envoyer des POST à l'API.

    Avantage :
    - évite de dupliquer le code ;
    - centralise la gestion d'erreur.
    """

    response = requests.post(
        f"{API_URL}{endpoint}",
        json=payload,
        timeout=10,
    )

    # Si erreur HTTP -> exception
    response.raise_for_status()

    return response.json()


# ============================================================================
# CRÉATION DES RUCHES
# ============================================================================

def create_hive(name: str) -> dict:
    """
    Crée une ruche.
    """

    print(f"Creating hive: {name}")

    return api_post(
        "/hives",
        {
            "name": name,
        },
    )


# ============================================================================
# CRÉATION DES NIVEAUX
# ============================================================================

def create_hive_level(
    name: str,
    hive_id: int,
    lower_level_id: int | None = None,
) -> dict:
    """
    Crée un niveau de ruche.

    Exemple :
    - Corps
    - Hausse 1
    - Hausse 2
    """

    print(f"Creating level: {name}")

    return api_post(
        "/hive-levels",
        {
            "name": name,
            "hive_id": hive_id,
            "lower_level_id": lower_level_id,
        },
    )


# ============================================================================
# CRÉATION DES PESÉES
# ============================================================================

def create_weighing(
    weight: float,
    level_id: int,
    measured_at: datetime,
) -> None:
    """
    Envoie une pesée à l'API.
    """

    requests.post(
        f"{API_URL}/weighings",
        json={
            "weight": round(weight, 2),
            "level_id": level_id,
            "measured_at": measured_at.isoformat(),
        },
        timeout=10,
    ).raise_for_status()


# ============================================================================
# ACTIVITÉ JOURNALIÈRE
# ============================================================================

def daily_activity_curve(hour: float) -> float:
    """
    Simule l'activité journalière des abeilles.

    Principe :

    Nuit :
    - peu d'activité

    Matin :
    - départ des butineuses
    - perte légère de poids

    Soir :
    - retour nectar
    - augmentation poids

    La fonction sinus produit une belle courbe naturelle.
    """

    activity = math.sin((hour - 6) / 12 * math.pi)

    return max(activity, 0)


# ============================================================================
# MIELLÉE
# ============================================================================

def spring_flow_gain(day_index: int) -> float:
    """
    Simule une miellée progressive.

    Plus on avance dans avril :
    plus les abeilles rentrent du nectar.
    """

    return day_index * 0.015


# ============================================================================
# CRÉATION DES RUCHES
# ============================================================================

print("\n==============================")
print("CREATING HIVES")
print("==============================\n")

hive_1 = create_hive("Ruche Simple")
hive_2 = create_hive("Ruche Double Corps")
hive_3 = create_hive("Ruche Miellée")


# ============================================================================
# CRÉATION DES NIVEAUX
# ============================================================================

print("\n==============================")
print("CREATING LEVELS")
print("==============================\n")

# --------------------------------------------------------------------------
# Ruche 1
# --------------------------------------------------------------------------

hive_1_body = create_hive_level(
    name="Corps",
    hive_id=hive_1["id"],
)

# --------------------------------------------------------------------------
# Ruche 2
# --------------------------------------------------------------------------

hive_2_bottom = create_hive_level(
    name="Corps Bas",
    hive_id=hive_2["id"],
)

hive_2_top = create_hive_level(
    name="Corps Haut",
    hive_id=hive_2["id"],
    lower_level_id=hive_2_bottom["id"],
)

# --------------------------------------------------------------------------
# Ruche 3
# --------------------------------------------------------------------------

hive_3_body = create_hive_level(
    name="Corps",
    hive_id=hive_3["id"],
)


# ============================================================================
# CONFIGURATION DES RUCHES
# ============================================================================

"""
Chaque niveau possède :

- un poids initial ;
- un gain de miel spécifique.

Pourquoi ?

Une hausse :
- prend rapidement du poids.

Un corps :
- plus lentement.
"""

HIVES = [
    {
        "name": "Ruche Simple",
        "levels": [
            {
                "id": hive_1_body["id"],
                "weight": 28.0,
                "honey_factor": 0.8,
            }
        ],
    },
    {
        "name": "Ruche Double Corps",
        "levels": [
            {
                "id": hive_2_bottom["id"],
                "weight": 32.0,
                "honey_factor": 1.0,
            },
            {
                "id": hive_2_top["id"],
                "weight": 18.0,
                "honey_factor": 1.3,
            },
        ],
    },
    {
        "name": "Ruche Miellée",
        "levels": [
            {
                "id": hive_3_body["id"],
                "weight": 30.0,
                "honey_factor": 1.2,
            }
        ],
    },
]


# ============================================================================
# INITIALISATION DES POIDS
# ============================================================================

for hive in HIVES:
    for level in hive["levels"]:

        CURRENT_WEIGHTS[level["id"]] = level["weight"]


# ============================================================================
# GÉNÉRATION DES DONNÉES
# ============================================================================

print("\n==============================")
print("GENERATING WEIGHINGS")
print("==============================\n")

current_date = START_DATE

hive_3_super_1 = None
hive_3_super_2 = None

measurement_count = 0

while current_date <= END_DATE:

    # Nombre de jours depuis le début
    day_index = (current_date - START_DATE).days

    # Heure sous forme décimale
    hour = current_date.hour + current_date.minute / 60

    # Activité des abeilles
    activity_factor = daily_activity_curve(hour)

    # Intensité de miellée
    flow_gain = spring_flow_gain(day_index)

    # ======================================================================
    # AJOUT PREMIÈRE HAUSSE
    # ======================================================================

    if day_index >= 10 and hive_3_super_1 is None:

        print("Adding first super...")

        hive_3_super_1 = create_hive_level(
            name="Hausse 1",
            hive_id=hive_3["id"],
            lower_level_id=hive_3_body["id"],
        )

        new_level = {
            "id": hive_3_super_1["id"],
            "weight": 3.0,
            "honey_factor": 2.0,
        }

        HIVES[2]["levels"].append(new_level)

        CURRENT_WEIGHTS[new_level["id"]] = new_level["weight"]

    # ======================================================================
    # AJOUT DEUXIÈME HAUSSE
    # ======================================================================

    if day_index >= 20 and hive_3_super_2 is None:

        print("Adding second super...")

        hive_3_super_2 = create_hive_level(
            name="Hausse 2",
            hive_id=hive_3["id"],
            lower_level_id=hive_3_super_1["id"],
        )

        new_level = {
            "id": hive_3_super_2["id"],
            "weight": 2.5,
            "honey_factor": 2.5,
        }

        HIVES[2]["levels"].append(new_level)

        CURRENT_WEIGHTS[new_level["id"]] = new_level["weight"]

    # ======================================================================
    # GÉNÉRATION DES PESÉES
    # ======================================================================

    for hive in HIVES:

        for level in hive["levels"]:

            level_id = level["id"]

            # Dernier poids connu
            current_weight = CURRENT_WEIGHTS[level_id]

            # ------------------------------------------------------------------
            # Variation liée aux abeilles
            # ------------------------------------------------------------------

            activity_variation = (
                activity_factor
                * random.uniform(-0.08, 0.15)
            )

            # ------------------------------------------------------------------
            # Gain de miel progressif
            # ------------------------------------------------------------------

            honey_gain = (
                flow_gain
                * level["honey_factor"]
                * random.uniform(0.8, 1.2)
            )

            # ------------------------------------------------------------------
            # Bruit capteur
            # ------------------------------------------------------------------

            sensor_noise = random.uniform(-0.02, 0.02)

            # ------------------------------------------------------------------
            # Mauvaise météo
            # ------------------------------------------------------------------

            weather_penalty = 0

            if random.random() < 0.03:

                weather_penalty = random.uniform(-0.2, -0.05)

            # ------------------------------------------------------------------
            # Variation finale
            # ------------------------------------------------------------------

            variation = (
                activity_variation
                + honey_gain
                + sensor_noise
                + weather_penalty
            )

            # Nouveau poids
            new_weight = current_weight + variation

            # Sécurité anti-valeurs négatives
            new_weight = max(new_weight, 1)

            # Sauvegarde du nouveau poids
            CURRENT_WEIGHTS[level_id] = new_weight

            # Envoi API
            create_weighing(
                weight=new_weight,
                level_id=level_id,
                measured_at=current_date,
            )

            measurement_count += 1

    # Affichage progression
    if measurement_count % 500 == 0:

        print(
            f"{measurement_count} weighings generated..."
        )

    # Avance dans le temps
    current_date += timedelta(
        minutes=MEASUREMENT_INTERVAL_MINUTES,
    )

    # Petite pause pour éviter de spammer l'API
    time.sleep(0.001)


# ============================================================================
# FIN
# ============================================================================

print("\n==============================")
print("GENERATION COMPLETED")
print("==============================")

print(f"Total weighings: {measurement_count}")