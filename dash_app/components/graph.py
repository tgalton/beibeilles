import pandas as pd
import plotly.express as px

from plotly.graph_objects import Figure


def build_measurements_graph(
    df: pd.DataFrame,
) -> Figure:
    """
    Génère un graphique Plotly
    à partir des measurements.
    """

    # =====================================================
    # Sécurité :
    # données absentes ou invalides
    # =====================================================
    if not isinstance(df, pd.DataFrame) or df.empty:

        return px.line(
            title="Aucune donnée disponible",
        )

    # =====================================================
    # Conversion datetime
    # =====================================================
    df["measured_at"] = pd.to_datetime(
        df["measured_at"],
    )

    # =====================================================
    # Tri chronologique
    # =====================================================
    df = df.sort_values(
        "measured_at",
    )

    # =====================================================
    # Construction figure Plotly
    # =====================================================
    fig = px.line(
        df,
        x="measured_at",
        y="value",
        color="type",
        title="Mesures de la ruche",
    )

    fig.update_layout(
        xaxis_title="Temps",
        yaxis_title="Valeur",
    )

    return fig