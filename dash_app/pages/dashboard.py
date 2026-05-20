from dash import html, dcc
from dash.dependencies import Input, Output

from api.client import get_hives, get_measurements
from components.graph import build_measurements_graph

def layout():
    """
    Layout = structure de la page.

    IMPORTANT :
    Ici on NE FAIT PAS d'appel API.
    On construit juste l'UI.
    """

    return html.Div(
        style={"padding": "20px"},
        children=[
            html.H1("Dashboard Ruche 🐝"),

            # -----------------------------
            # Dropdown ruche (chargé dynamiquement)
            # -----------------------------
            dcc.Dropdown(
                id="type-selector",
                options=[
                    {"label": "Weight", "value": "weight"},
                    {"label": "Temperature", "value": "temperature"},
                    {"label": "Humidity", "value": "humidity"},
                    {"label": "CO2", "value": "co2"},
                ],
                value="weight",
            )

            # -----------------------------
            # Graph poids
            # -----------------------------
            dcc.Graph(id="weight-graph"),
        ],
    )


def register_callbacks(app):
    """
    Les callbacks = logique interactive Dash.
    """

    # ---------------------------------------------------------
    # 1) Charger les ruches dans le dropdown au démarrage
    # ---------------------------------------------------------
    @app.callback(
        Output("hive-selector", "options"),
        Output("hive-selector", "value"),
        Input("hive-selector", "id"),  # hack Dash: déclenche au chargement
    )
    def load_hives(_):
        """
        Cette fonction s'exécute UNE fois au chargement de la page.

        Elle :
        - appelle l'API
        - construit les options du dropdown
        - sélectionne la première ruche par défaut
        """

        hives = get_hives()

        options = [
            {"label": hive["name"], "value": hive["id"]}
            for hive in hives
        ]

        default_value = hives[0]["id"] if hives else None

        return options, default_value


    # ---------------------------------------------------------
    # 2) Mise à jour du graphe quand on change de ruche
    # ---------------------------------------------------------
    @app.callback(
        Output("weight-graph", "figure"),
        Input("hive-selector", "value"),
    )
    def update_graph(hive_id, measurement_type):
        df = get_measurements(
            hive_level_id=hive_id,
            measurement_type=measurement_type,
        )

        return build_measurements_graph(df[df["type"] == measurement_type])