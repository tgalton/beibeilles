<!-- Lancement -> docker compose up --build -->
<!-- Fermeture des contener -> docker compose down -v  -->
<!-- Nettoyage de tout les docker -> docker system prune -a --volumes -f -->
<!-- Suppresion manuelle contener de la base : docker volume rm beibeilles_timescaledb_data -->
<!-- Création d'arbre : find . -print | sed -e 's;[^/]*/;|   ;g' -->
<!-- Création de fichier d'arborescence : cmd //c "tree /F /A > arborescence.txt" -->
<!-- Mdp temporaire bdd : 4b90cedb66834ff8ab4a1d38ff0d5d15 -->

# Plateforme de supervision apicole connectée

## Objectif du projet

Ce projet vise à construire une plateforme complète de supervision apicole permettant :

- la mesure du poids des ruches ;
- le comptage d’activité des abeilles (entrées/sorties) ;
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
ESP32 + HX711 + cellules de charge
        ↓
Raspberry Pi (agrégation locale)
        ↓
API backend centralisée
        ↓
Base de données time-series
        ↓
Pipeline analytique
        ↓
Visualisation et analyses
```

---

# Partie embarquée : mesure du poids

## Matériel retenu

### Microcontrôleur

- ESP32

### Amplificateur / ADC

- HX711

### Cellules de charge

- 4 demi-cellules de charge type balance

Architecture retenue :

- pont de Wheatstone complet reconstitué ;
- meilleure répartition mécanique ;
- meilleure stabilité qu’une cellule unique ;
- meilleure résistance aux déséquilibres de charge.

---

# Communication ESP32 → Raspberry Pi

## Phase initiale

### USB série

Architecture actuelle :

```text
ESP32 → USB → Raspberry Pi
```

Avantages :

- simplicité ;
- alimentation électrique ;
- debug facile ;
- flash firmware direct ;
- rapidité de mise en place.

---

## Architecture cible

### RS485

Architecture future :

```text
ESP32 → RS485 → Raspberry Pi
```

Matériel prévu :

- modules MAX485 côté ESP32 ;
- adaptateur USB RS485 côté Raspberry Pi.

Raisons du choix :

- robustesse électrique ;
- longues distances ;
- bus partagé multi-ruches ;
- bonne résistance au bruit ;
- évolutivité.

---

# Rôle du Raspberry Pi

Le Raspberry Pi agit comme :

- relais local ;
- agrégateur ;
- buffer de sécurité ;
- point de collecte.

Il n’est pas considéré comme le backend principal.

Responsabilités :

- lecture des données série ;
- prétraitement léger ;
- agrégation ;
- retransmission vers le backend central ;
- fonctionnement dégradé hors ligne.

---

# Format des données

Format retenu : JSON.

Exemple :

```json
{
  "hive": "ruche_1",
  "weight": 42.31,
  "temperature": 18.2,
  "timestamp": "2026-05-13T14:22:00Z"
}
```

---

# Backend central

## Framework retenu : FastAPI

FastAPI est préféré à Flask pour :

- la validation automatique des données ;
- la documentation OpenAPI native ;
- le typage Python moderne ;
- les performances ;
- l’async natif ;
- l’intégration avec l’écosystème data science Python.

Architecture logicielle cible :

```text
FastAPI
    ↓
Services métier
    ↓
Base de données
```

---

# Base de données

## Phase initiale

### SQLite

Utilisé pour :

- le prototypage ;
- les premiers tests ;
- le développement local.

---

## Architecture cible

### PostgreSQL + TimescaleDB

Choix motivé par :

- le support natif des séries temporelles ;
- SQL complet ;
- les jointures analytiques ;
- les corrélations météo ;
- les agrégations temporelles ;
- la montée en charge.

---

# Gestion de la volumétrie

Deux catégories de données ont été identifiées :

## Données lentes

Exemples :

- poids ;
- température ;
- humidité ;
- météo.

Ces données sont adaptées à une base time-series classique.

---

## Données événementielles haute fréquence

Exemples :

- comptage d’abeilles ;
- entrées/sorties.

La stratégie retenue consiste à agréger localement les événements avant stockage.

Exemple :

```json
{
  "timestamp": "2026-05-13T10:00:00Z",
  "entries": 542,
  "exits": 531
}
```

Cette approche :

- réduit fortement la volumétrie ;
- simplifie les analyses ;
- évite une architecture de type ELK ;
- reste adaptée aux besoins comportementaux.

---

# Data visualisation

## Besoins identifiés

Le projet vise :

- l’exploration analytique ;
- les statistiques ;
- les corrélations météo ;
- les visualisations interactives ;
- les analyses temporelles avancées.

---

## Solutions étudiées

### Grafana

Très adapté au monitoring temps réel, mais jugé insuffisant comme outil analytique principal.

---

### R / Shiny

Très bon pour l’analyse statistique et la recherche exploratoire.

---

### Plotly Dash

Solution retenue comme visualiseur principal.

Raisons :

- intégration Python ;
- compatibilité pandas/polars ;
- dashboards interactifs ;
- bonnes capacités analytiques ;
- compatibilité Docker.

---

# Stack logicielle cible

## Edge

- ESP32
- HX711
- RS485
- Raspberry Pi

---

## Backend

- FastAPI
- Docker
- PostgreSQL
- TimescaleDB

---

## Traitement de données

- pandas
- polars
- numpy

---

## Visualisation

- Plotly Dash

---

## Outils complémentaires

- Bruno pour les tests API
- Docker Compose
- MQTT potentiellement

---

# Perspectives futures

## Mesure de poids avancée

- suivi journalier ;
- détection de miellée ;
- détection de famine ;
- suivi hivernal.

---

## Activité des abeilles

- comptage entrée/sortie ;
- activité journalière ;
- corrélation météo ;
- détection d’anomalies.

---

## Corrélation avec données externes

- API météo ;
- humidité ;
- température ;
- pression atmosphérique ;
- pluie ;
- floraison.

---

## Analyses avancées

- détection d’essaimage ;
- clustering de ruches ;
- modèles prédictifs ;
- machine learning.

---

## Robustesse terrain

- bufferisation locale ;
- fonctionnement hors ligne ;
- supervision RS485 ;
- OTA futures ;
- reprise automatique après coupure.

---

# Philosophie générale

Le projet vise une architecture :

- modulaire ;
- distribuée ;
- orientée données ;
- orientée séries temporelles ;
- extensible ;
- adaptée à un déploiement terrain réel.

L’objectif n’est pas uniquement de construire une balance connectée, mais une véritable plateforme d’observation et d’analyse apicole.
