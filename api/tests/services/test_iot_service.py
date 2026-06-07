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