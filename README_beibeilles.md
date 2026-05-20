<!-- Lancement -> docker compose up --build -->
<!-- Fermeture des contener -> docker compose down -v  -->
<!-- Nettoyage de tout les docker -> docker system prune -a --volumes -f -->
<!-- Suppresion manuelle contener de la base : docker volume rm beibeilles_timescaledb_data -->
<!-- Création d'arbre : find . -print | sed -e 's;[^/]*/;|   ;g' -->
<!-- Création de fichier d'arborescence : cmd //c "tree /F /A > arborescence.txt" -->
<!-- Mdp temporaire bdd : 4b90cedb66834ff8ab4a1d38ff0d5d15 -->
<!-- Lancer uvicorn app.main:app --reload pour tester le back avant de pousser -->

docker logs watchtower -f

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
