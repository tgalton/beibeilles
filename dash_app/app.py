from dash import Dash

from pages.dashboard import layout
from pages.dashboard import register_callbacks


# =========================================================
# Factory Dash
#
# Sépare :
# - création app
# - configuration
# - lancement
# =========================================================
def create_app() -> Dash:

    app = Dash(__name__)

    # -----------------------------------------------------
    # Interface utilisateur
    # -----------------------------------------------------
    app.layout = layout()

    # -----------------------------------------------------
    # Callbacks interactifs
    # -----------------------------------------------------
    register_callbacks(app)

    return app


# =========================================================
# Instance globale Dash
# =========================================================
app = create_app()


# =========================================================
# Lancement local
# =========================================================
if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=8050,
    )