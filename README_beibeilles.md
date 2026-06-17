**Permet de récupérer la session et le bon directory sur le serveur de l'appli**

```
su - tom
```

<!-- Car c'est un docker rootless -->

**Lancement local**

```bash
docker compose \
-f docker-compose.yml \
-f docker-compose.dev.yml \
up -d
```

**Arrêter local**

```bash
docker compose \
-f docker-compose.yml \
-f docker-compose.dev.yml \
down
```

**Reset complet local**

```bash
docker compose \
-f docker-compose.yml \
-f docker-compose.dev.yml \
down -v
```

**Rebuild complet :**

```bash
docker compose \
-f docker-compose.yml \
-f docker-compose.dev.yml \
build --no-cache
```

**Alembic migration**

```bash
cd api
alembic revision --autogenerate -m "nom migration"
```

**Si on a une erreur "Target database is not up to date."**

```bash
# C'est une différence entre current et head en version
alembic current
alembic heads
alembic upgrade head
```

**Appliquer migration**

```bash
alembic upgrade head
```

**Connexion postgre sur serveur**

````bash
docker exec -it beibeilles-timescaledb-1 \
psql -U beibeilles -d beibeilles```

**Voir les tables **

```bash
\dt
````

**Connexion postgre sur dbeaver**
Création d'un tunnel ssh local (la base n'est pas exposée)

```bash
ssh -L 5432:localhost:5432 tom@79.137.34.118
```

**Lancement prod**

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v <!-- Fermeture des contener -->

<!-- Nettoyage de tout les docker -> docker system prune -a --volumes -f -->
<!-- Suppresion manuelle contener de la base : docker volume rm beibeilles_timescaledb_data -->
<!-- Création d'arbre : find . -print | sed -e 's;[^/]*/;|   ;g' -->
```

**Création de fichier d'arborescence :**

```bash
cmd //c "tree /F /A > arborescence.txt"
```

<!-- Mdp temporaire bdd : 4b90cedb66834ff8ab4a1d38ff0d5d15 -->

Adresse pour le json de l'api : http://79.137.34.118:8000/openapi.json

**Voir logs watchtower sur server**

```bash
docker logs watchtower -f
```

<!-- Tout lancer en docker local--> docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
<!-- Tout down en docker local--> docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v
<!-- Tout rebuild sans cache en docker local-->docker compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache
<!-- Générer migration des données --> alembic revision --autogenerate -m "..."
<!-- Aller sur le postgre de la bdd depuis server --> docker exec -it beibeilles-timescaledb-1 psql -U beibeilles -d beibeilles
<!-- Pour voir les tables ensuite --> \dt

**INSTALLER REQUIREMENT EN LOCAL**

Depuis les versions récentes d'Ubuntu/Debian, Python est protégé par le mécanisme PEP 668. Il empêche d'installer des paquets avec pip directement dans le Python système.
A faire depuis le dossier Api :

```bash
sudo apt update
sudo apt install python3-venv python3-full
```

<!-- puis toujours dans le dossier api-->

```bash
cd ~/Workspace/beibeilles/api

python3 -m venv .venv

source .venv/bin/activate

# Mettre à jour pip
pip install --upgrade pip
# Installer les requirements
pip install -r requirements.txt
```

**Lancer les tests**

```bash
source .venv/bin/activate
pytest
```

**Voir la couverture de test**

```bash
pytest tests/routers/test_measurement_raw_router.py -v
```

**Lancer les tests d'un seul fichier**

```bash
pytest tests/routers/test_measurement_raw.py -v
```

**Voir les crédentials bdd du server**

```bash
docker inspect beibeilles-timescaledb-1 | grep POSTGRES
```

**Faire passer le linter ruff**

```bash
ruff check .
```

**Faire fixer via le linter ruff**

```bash
ruff check . --fix
```

**Faire formater via le linter ruff**

```bash
ruff format .
```

# Plateforme de supervision apicole connectée

## Objectif du projet

Ce projet vise à construire une plateforme complète de supervision apicole permettant :

- la mesure du poids des ruches ;
- le suivi multi-étages des hausses ;
- le comptage d’activité des abeilles (entrées/sorties) ;
- la mesure de paramètres environnementaux ;
- l’agrégation locale des données sur un Raspberry Pi ;
- la transmission des données vers une API backend centralisée ;
- l’analyse statistique des données apicoles ;
- la corrélation avec des données externes (météo, saisons, floraisons, etc.) ;
- la visualisation avancée des données ;
- la mise en place future d’algorithmes de détection comportementale et prédictive.

Le projet est conçu dès le départ avec une logique d’architecture évolutive, orientée IoT, data engineering et analyse de séries temporelles.

---

# Architecture globale

## Architecture cible

```text
ESP32 + capteurs
        ↓
Bus terrain (USB puis RS485)
        ↓
Raspberry Pi (agrégation locale)
        ↓
API FastAPI centralisée
        ↓
PostgreSQL + TimescaleDB
        ↓
Pipeline analytique
        ↓
Visualisation Dash / analyses
```

---

# Architecture terrain

## Organisation d’un rucher

Un Raspberry Pi peut superviser plusieurs ruches.

Chaque ruche possède :

- un ESP32 dédié ;
- un ensemble de capteurs modulaires ;
- une configuration indépendante.

Architecture cible :

```text
                Raspberry Pi
                      │
     ┌────────────────┼────────────────┐
     │                │                │
 ESP32 ruche 1   ESP32 ruche 2   ESP32 ruche N
     │                │                │
 capteurs         capteurs         capteurs
```

---

# Partie embarquée : ESP32

## Rôle des ESP32

Chaque ESP32 :

- lit les capteurs locaux ;
- réalise un prétraitement minimal ;
- transmet les données au Raspberry Pi ;
- peut être mis à jour automatiquement par le Raspberry Pi.

Les ESP32 sont considérés comme :

- des noeuds terrain ;
- remplaçables ;
- spécialisés ;
- pilotés par le Raspberry Pi.

---

# Mise à jour automatique des ESP32

## Philosophie retenue

Le Raspberry Pi devient :

- superviseur local ;
- orchestrateur ;
- système de déploiement terrain.

Le Raspberry Pi :

- surveille un dépôt Git distant ;
- détecte les nouvelles versions firmware ;
- compile automatiquement les firmwares ESP32 ;
- flashe les ESP32 connectés ;
- redémarre les noeuds si nécessaire.

---

## Pipeline de mise à jour

Architecture :

```text
GitHub
   ↓
Raspberry Pi
   ↓
Compilation firmware ESP32
   ↓
Flash automatique des ESP32
```

---

# Communication ESP32 ↔ Raspberry Pi

## Phase initiale : USB série

Architecture actuelle :

```text
ESP32 → USB → Raspberry Pi
```

---

## Architecture cible : RS485

Architecture future :

```text
ESP32 → RS485 → Raspberry Pi
```

---

# Capteurs supportés

## Mesure de poids

### Matériel retenu

- ESP32
- HX711
- 4 demi-cellules de charge type balance

---

## Gestion multi-étages

Une ruche peut posséder jusqu’à :

- 5 étages instrumentés ;
- une balance par étage.

Chaque étage correspond à un `hive_level`.

Exemple :

```json
{
  "hive": "ruche_1",
  "hive_level": 3,
  "weight": 12.42
}
```

---

## Capteurs environnementaux

### ENS160 + AHT21

Capteur prévu pour :

- qualité de l’air ;
- CO2 équivalent (eCO2) ;
- TVOC ;
- température ;
- humidité.

### DS18B20

Capteur prévu pour :

- température interne ;
- température externe ;
- suivi hivernal ;
- gradients thermiques.

---

# Comptage des abeilles

Le système s’inspirera notamment des travaux suivants :

https://www.david-romeuf.fr/Apiculture/ArticleSNACompteurAbeilles.pdf

---

# Rôle du Raspberry Pi

Le Raspberry Pi agit comme :

- relais local ;
- agrégateur ;
- buffer de sécurité ;
- orchestrateur firmware ;
- superviseur terrain.

---

# Backend central

## Framework retenu : FastAPI

Architecture cible :

```text
FastAPI
    ↓
Services métier
    ↓
Base de données
```

---

# Base de données

## Architecture cible

### PostgreSQL + TimescaleDB

Choix motivé par :

- le support natif des séries temporelles ;
- SQL complet ;
- les agrégations temporelles ;
- la montée en charge.

---

# MQTT (option future)

Architecture possible :

```text
ESP32 → MQTT Broker → Raspberry Pi / Backend
```

---

# Visualisation des données

## Solution retenue

### Plotly Dash

---

# Stack logicielle cible

## Edge

- ESP32
- HX711
- RS485
- Raspberry Pi

## Backend

- FastAPI
- Docker
- PostgreSQL
- TimescaleDB

## Traitement de données

- pandas
- polars
- numpy

## Visualisation

- Plotly Dash

---

# Déploiement serveur

## Infrastructure actuelle

Architecture :

```text
GitHub Actions
      ↓
GHCR
      ↓
Serveur VPS
      ↓
Watchtower
      ↓
Containers mis à jour automatiquement
```

---

# Philosophie générale

Le projet vise une architecture :

- modulaire ;
- distribuée ;
- orientée données ;
- orientée séries temporelles ;
- extensible ;
- adaptée à un déploiement terrain réel.

# Système d'auto-recalibrage des balances

## Contexte

Les cellules de charge utilisées sur les ruches peuvent dériver avec le temps.

Cette dérive peut être provoquée par :

- les variations de température ;
- le vieillissement mécanique ;
- l'humidité ;
- les contraintes permanentes exercées sur la structure ;
- les dérives électroniques des amplificateurs HX711.

Lors des essais réalisés sur plusieurs semaines, certaines balances ont présenté des dérives importantes pouvant atteindre plusieurs dizaines de kilogrammes malgré une charge réelle stable.

L'objectif de ce module est de permettre :

- la détection automatique des périodes stables ;
- l'estimation d'une dérive probable ;
- la génération de calibrations ;
- la conservation complète de l'historique des corrections.

---

# Philosophie générale

Le système sépare volontairement plusieurs notions :

| Concept              | Rôle                            |
| -------------------- | ------------------------------- |
| WeightReferenceEvent | Observation terrain             |
| WeightBaseline       | Estimation automatique          |
| WeightCalibration    | Correction réellement appliquée |
| StabilityAnalysis    | Analyse statistique             |

Cette séparation permet :

- d'expliquer l'origine d'une correction ;
- d'auditer les décisions de l'algorithme ;
- de recalculer les poids historiques.

---

# WeightReferenceEvent

## Objectif

Représente une mesure de référence réalisée volontairement par l'apiculteur.

Exemple :

L'utilisateur pose un poids étalon de 1 kg.

Variation attendue :

+1.000 kg

Variation mesurée :

+0.942 kg

L'événement est enregistré mais aucune correction n'est appliquée.

## Utilisation

Ces événements servent à :

- calculer un gain ;
- vérifier la qualité de calibration ;
- valider les estimations automatiques.

---

# WeightBaseline

## Objectif

Représente une estimation automatique du niveau réel de la balance.

Une baseline est produite lorsque l'algorithme détecte une période suffisamment stable.

Exemple :

Pendant 30 minutes :

- faible variance ;
- faible pente ;
- absence de manipulation.

Poids observé :

52.14 kg

L'algorithme considère alors :

"La balance semble stable autour de 52.14 kg."

Cette valeur est enregistrée comme baseline.

## Important

Une baseline n'est pas une calibration.

Elle représente uniquement une hypothèse.

---

# WeightCalibration

## Objectif

Représente une correction réellement appliquée aux mesures.

Exemple :

Offset :

-2.4 kg

Poids corrigé :

poids_mesuré - offset

Toutes les calibrations sont historisées.

Une seule calibration peut être active simultanément pour une balance.

---

# Analyse de stabilité

## Objectif

Déterminer si une période de mesures peut être considérée comme stable.

L'analyse repose sur :

- la variance ;
- la pente ;
- la durée de la fenêtre.

---

## Régression linéaire

La pente est calculée par régression linéaire.

L'unité utilisée est :

kg / heure

Exemple :

+0.10 kg observé sur une heure

Pente :

0.10 kg/h

Une pente proche de zéro indique une masse stable.

---

## Variance

La variance mesure la dispersion des valeurs autour de leur moyenne.

Une faible variance indique :

- peu de bruit ;
- peu de perturbations ;
- stabilité mécanique.

---

## Durée minimale

Une fenêtre stable doit durer suffisamment longtemps.

Version actuelle :

30 minutes minimum.

---

## Score de confiance

Chaque analyse produit un score :

0.0 → très faible confiance

1.0 → très forte confiance

Ce score dépend :

- de la variance ;
- de la pente ;
- de la durée observée.

---

# Détection automatique de baseline

Le processus est le suivant :

Mesures agrégées
↓
Analyse de stabilité
↓
Fenêtre stable
↓
Calcul du poids moyen
↓
Création d'un BaselineCandidateDTO
↓
Création d'un WeightBaseline

Le poids moyen de la fenêtre devient l'estimation de référence.

---

# Calibration par poids étalon

Lorsqu'un poids de référence est utilisé :

Gain = variation_attendue / variation_mesurée

Exemple :

Attendu :

1.000 kg

Mesuré :

0.950 kg

Gain :

1.0526

Cela signifie que les variations observées doivent être multipliées par environ 1.05.

---

# Historisation

Toutes les informations sont conservées :

- événements de référence ;
- baselines ;
- calibrations.

Cette historisation permet :

- le recalcul des poids historiques ;
- l'audit des décisions ;
- l'amélioration future des algorithmes.

---

# Architecture

## DTO

- StabilityAnalysisDTO
- BaselineCandidateDTO
- CalibrationProposalDTO (prévu)

## Services

- weight_stability_service
- weight_baseline_service
- weight_reference_service
- weight_calibration_service
- auto_calibration_service (prévu)

## Repositories

- weight_baseline_repository
- weight_reference_event_repository
- weight_calibration_repository

---

# Évolutions prévues

## V2

- score de confiance avancé ;
- détection automatique des manipulations ;
- prise en compte de la température ;
- fusion de plusieurs périodes stables.

## V3

- auto-calibration complète ;
- validation automatique des dérives ;
- recalibrage sans intervention utilisateur.

## V4

- apprentissage des profils de dérive ;
- adaptation automatique aux saisons ;
- estimation prédictive de dérive.
