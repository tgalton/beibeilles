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

    # vérifie la présence des bonnes colonne pour évite problème futur maj
    required_columns = [
        "bucket_at",
        "avg_value",
        "type",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        return px.line(
            title=f"Colonnes manquantes : {missing_columns}",
        )
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
    df["bucket_at"] = pd.to_datetime(
        df["bucket_at"],
    )

    # =====================================================
    # Tri chronologique
    # =====================================================

    df = df.sort_values(
        "bucket_at",
    )

    # =====================================================
    # Construction figure Plotly
    # =====================================================

    fig = px.line(
        df,
        x="bucket_at",
        y="avg_value",
        color="type",
        title="Mesures de la ruche",
    )

    fig.update_layout(
        xaxis_title="Temps",
        yaxis_title="Valeur",
    )

    return fig