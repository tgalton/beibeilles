from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output

from api.client import get_hives
from api.client import get_measurements
from components.graph import build_measurements_graph

from datetime import datetime
from datetime import timedelta
from datetime import UTC

import pandas as pd


# =========================================================
# Layout principal
#
# IMPORTANT :
# Le layout décrit UNIQUEMENT l'interface.
#
# Aucun appel API lourd ne doit être fait ici.
#
# Les données dynamiques sont chargées
# via les callbacks Dash.
# =========================================================
def layout():

    return html.Div(
        style={"padding": "20px"},
        children=[

            # =================================================
            # Titre
            # =================================================
            html.H1("Dashboard Ruche"),

            # =================================================
            # Sélection de la ruche
            #
            # Les options sont injectées dynamiquement
            # par un callback au démarrage.
            # =================================================
            dcc.Dropdown(
                id="hive-selector",
                placeholder="Sélectionner une ruche",
            ),

            html.Br(),

            # =================================================
            # Sélection du type de mesure
            # =================================================
            dcc.Dropdown(
                id="type-selector",
                options=[
                    {
                        "label": "Poids",
                        "value": "weight",
                    },
                    {
                        "label": "Température",
                        "value": "temperature",
                    },
                    {
                        "label": "Humidité",
                        "value": "humidity",
                    },
                    {
                        "label": "CO2",
                        "value": "co2",
                    },
                ],
                value="weight",
                clearable=False,
            ),
            
            dcc.Dropdown(
                id="time-range-selector",
                options=[
                    {
                        "label": "1 heure",
                        "value": "1h",
                    },
                    {
                        "label": "24 heures",
                        "value": "24h",
                    },
                    {
                        "label": "7 jours",
                        "value": "7d",
                    },
                    {
                        "label": "30 jours",
                        "value": "30d",
                    },
                ],
                value="24h",
                clearable=False,
            ),

            html.Br(),

            # =================================================
            # Graphique Plotly
            # =================================================
            dcc.Graph(
                id="measurement-graph",
            ),
        ],
    )


# =========================================================
# Enregistrement des callbacks Dash
# =========================================================
def register_callbacks(app):

    # =====================================================
    # Chargement des ruches au démarrage
    #
    # Astuce Dash :
    # on utilise un Input fictif pour déclencher
    # le callback une seule fois.
    # =====================================================
    @app.callback(
        Output("hive-selector", "options"),
        Output("hive-selector", "value"),
        Input("hive-selector", "id"),
    )
    def load_hives(_):

        hives = get_hives()
        # -------------------------------------------------
        # Construction des options du dropdown
        # -------------------------------------------------
        options = [
            {
                "label": hive["name"],
                "value": hive["id"],
            }
            for hive in hives
        ]

        # -------------------------------------------------
        # Sélection automatique de la première ruche
        # -------------------------------------------------
        default_value = (
            hives[0]["id"]
            if hives
            else None
        )

        return options, default_value


    # =====================================================
    # Mise à jour du graphique
    #
    # Déclenché quand :
    # - on change de ruche
    # - on change de type de mesure
    # =====================================================
    @app.callback(
        Output("measurement-graph", "figure"),
        Input("hive-selector", "value"),
        Input("type-selector", "value"),
    )
    def update_graph(
        hive_id,
        measurement_type,
        time_range,
    ):
        
        # Création de la plage de sélection horaire
        now = datetime.now(UTC)

        if time_range == "1h":
            start_at = now - timedelta(hours=1)

        elif time_range == "24h":
            start_at = now - timedelta(hours=24)

        elif time_range == "7d":
            start_at = now - timedelta(days=7)

        elif time_range == "30d":
            start_at = now - timedelta(days=30)

        else:
            start_at = now - timedelta(hours=24)

        # -------------------------------------------------
        # Protection :
        # aucun graphique tant qu'aucune ruche
        # n'est sélectionnée
        # -------------------------------------------------
        if hive_id is None:
            return build_measurements_graph(
                pd.DataFrame()
            )

        # -------------------------------------------------
        # Chargement des données
        # -------------------------------------------------
        df = get_measurements(
            hive_level_id=hive_id,
            measurement_type=measurement_type,
            start_at=start_at,
            end_at=now,
        )

        # -------------------------------------------------
        # Construction du graphique
        # -------------------------------------------------
        return build_measurements_graph(df)