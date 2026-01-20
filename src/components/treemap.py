import plotly.graph_objects as go
from src.utils import parse_data_for_treemap


def create_tree_map(size_map: dict) -> go.Figure:
    if not size_map:
        fig = go.Figure()
        fig.update_layout(
            title="Dictionary with component sizes not available",
            template="plotly_white",
            height=600,
        )
        return fig

    labels, parents, values = parse_data_for_treemap(size_map, root_name="Predictor Components")

    # TODO: Fix colors
    fig = go.Figure(go.Treemap(
        labels = labels,
        parents = parents,
        root_color="lightgrey",
        values=values
    ))

    fig.update_layout(
        title="Predictor Component Sizes",
        template="plotly_white",
    )

    return fig
