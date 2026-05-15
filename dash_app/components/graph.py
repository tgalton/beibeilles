import pandas as pd
import plotly.express as px


def build_weight_graph(df):
    """
    Construit un graphique de l'évolution du poids.
    """

    # Convertit la date en format datetime (obligatoire pour graph temporel)
    df["measured_at"] = pd.to_datetime(df["measured_at"])

    # Trie par date (sinon courbe incohérente)
    df = df.sort_values("measured_at")

    # Création du graphique ligne
    fig = px.line(
        df,
        x="measured_at",
        y="weight",
        title="Évolution du poids de la ruche",
    )

    # Labels des axes
    fig.update_layout(
        xaxis_title="Temps",
        yaxis_title="Poids (kg)",
    )

    return fig