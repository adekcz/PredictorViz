import plotly.graph_objects as go
from plotly_resampler import FigureResampler


def create_bar_graph(data: dict) -> go.Figure:
    if not data:
        fig = go.Figure()
        fig.update_layout(
            title="No Loop Count Data Available",
            template="plotly_white",
            height=600,
        )
        return fig

    x_vals = [str(k) for k in data.keys()]
    y_vals = list(data.values())

    fig = go.Figure(
        data=[
            go.Bar(
                x=x_vals, 
                y=y_vals,
                marker_color='royalblue',
                hovertemplate='<b>Loop Count: %{x}</b><br>Frequency: %{y}<extra></extra>'
            )
        ]
    )

    fig.update_layout(
        title="Loop Predictor: Loop Iteration Count Distribution",
        xaxis_title="Iteration Count (Iterations)",
        yaxis_title="Frequency (Times Encountered)",
        template="plotly_white",
        bargap=0.2,
        height=500
    )

    return fig

