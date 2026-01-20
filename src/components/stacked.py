import plotly.graph_objects as go
from plotly_resampler import FigureResampler

import pandas as pd
from plotly_resampler.aggregation import EveryNthPoint

def create_stacked_area(data_lists: list[list], trace_names: list[str] = None) -> go.Figure:
    if not data_lists:
        fig = go.Figure()
        fig.update_layout(
            title="No MPKBr periodic data available",
            template="plotly_white",
            height=600,
        )
        return fig


    fig = FigureResampler(go.Figure(), default_downsampler=EveryNthPoint())

    for i, y_data in enumerate(data_lists):
        name = trace_names[i] if trace_names and i < len(trace_names) else f"Series {i+1}"

        fig.add_trace(
            go.Scatter(
                name=name,
                y=y_data,
                mode='lines',
                stackgroup='one', # This triggers the stacking behavior
                # Optional: Smooth the line visual slightly if data is jagged
                line=dict(width=1)
            )
        )

    fig.update_layout(
        title="Stacked Area Chart (Time Series)",
        xaxis_title="Time",
        yaxis_title="Cumulative Amplitude",
        template="plotly_white",
        height=700,
        yaxis=dict(constrain="domain"),
        xaxis=dict(constrain="domain"),
        hovermode="x unified" # Very helpful for stacked charts
    )

    return fig
