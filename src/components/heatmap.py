import math
import plotly.graph_objects as go


def create_heatmap(mpkbr_periodic: list) -> go.Figure:
    if not mpkbr_periodic:
        fig = go.Figure()
        fig.update_layout(
            title="No MPKBr periodic data available",
            template="plotly_white",
            height=600,
        )
        return fig

    data_len = len(mpkbr_periodic)
    actual_size = int(math.sqrt(data_len))


    # Reshape data into 2D array
    heatmap_data = []
    for i in range(actual_size):
        start_idx = i * actual_size
        end_idx = start_idx + actual_size
        if end_idx <= len(mpkbr_periodic):
            heatmap_data.append(mpkbr_periodic[start_idx:end_idx])
        else:
            # Pad with zeros if needed
            row = mpkbr_periodic[start_idx:] + [0] * (end_idx - len(mpkbr_periodic))
            heatmap_data.append(row)

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        colorscale='Viridis',
        colorbar=dict(title="Num Accesses"),
    ))

    fig.update_layout(
        title=f"Bimodal Table Access Heatmap ({actual_size}x{actual_size} periods)",
        xaxis_title="Period (column)",
        yaxis_title="Period (row)",
        template="plotly_white",
        height=700,
        xaxis=dict(
            scaleanchor="y",
            scaleratio=1,
            constrain="domain",
        ),
        yaxis=dict(
            constrain="domain",
        ),
    )

    return fig
