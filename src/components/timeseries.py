import plotly.graph_objects as go
from plotly_resampler import FigureResampler


def create_timeseries(mpkbr_periodic: list) -> go.Figure:
    if not mpkbr_periodic:
        fig = go.Figure()
        fig.update_layout(
            title="No MPKBr periodic data available",
            template="plotly_white",
            height=600,
        )
        return fig

    fig = FigureResampler(go.Figure())

    fig.add_trace(
        go.Scattergl(name='MPKBr', showlegend=True, line_color='#440154'),
        hf_y=mpkbr_periodic
    )

    fig.update_layout(
        title="MPKBr over Time",
        xaxis_title="Number of mispredictions",
        yaxis_title="Time",
        template="plotly_white",
        height=700,

        yaxis=dict(
            constrain="domain",
        ),
        xaxis=dict(
            constrain="domain",
        )
    )

    return fig

