from dash import Dash

from pages.dashboard import layout
from pages.dashboard import register_callbacks


def create_app():
    """
    Crée et configure l'application Dash.
    """

    app = Dash(__name__)

    # Layout = interface utilisateur (HTML + composants)
    app.layout = layout()

    # Callbacks = interactions (dropdown -> graph)
    register_callbacks(app)

    return app


# Création de l'app
app = create_app()


if __name__ == "__main__":
    # Lance le serveur Dash
    app.run(
        debug=True,
        host="0.0.0.0",
        port=8050,
    )