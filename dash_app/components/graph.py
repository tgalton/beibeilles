import pandas as pd
import plotly.express as px


def build_measurements_graph(df):
    df["measured_at"] = pd.to_datetime(df["measured_at"])
    df = df.sort_values("measured_at")

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