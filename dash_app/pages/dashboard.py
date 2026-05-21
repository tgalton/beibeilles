from dash import dcc
from dash import html
from dash.dependencies import Input
from dash.dependencies import Output

from api.client import get_hives
from api.client import get_measurements
from components.graph import build_measurements_graph
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
    ):

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
        )

        # -------------------------------------------------
        # Construction du graphique
        # -------------------------------------------------
        return build_measurements_graph(df)