"""
Branch Predictor Visualization Dashboard
"""

import json
import math

import yaml
from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objects as go
from plotly_resampler import FigureResampler

def load_simulation_data(json_path: str) -> dict:
    """Load simulation results from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def load_predictor_config(yaml_path: str) -> dict:
    """Load predictor configuration from YAML file."""
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


def format_large_number(num: int | float) -> str:
    """Format large numbers with appropriate suffixes."""
    if num is None:
        return "N/A"
    if num >= 1e9:
        return f"{num / 1e9:.2f}B"
    elif num >= 1e6:
        return f"{num / 1e6:.2f}M"
    elif num >= 1e3:
        return f"{num / 1e3:.2f}K"
    else:
        return f"{num:.2f}"


def create_summary_cards(trace_data: dict) -> list:
    stats = [
        ("Total Instructions", trace_data.get("NUM_INSTRUCTIONS"), "instructions"),
        ("Total Branches", trace_data.get("NUM_BR"), "branches"),
        ("Unconditional Branches", trace_data.get("NUM_UNCOND_BR"), "branches"),
        ("Conditional Branches", trace_data.get("NUM_CONDITIONAL_BR"), "branches"),
        ("Mispredictions", trace_data.get("NUM_MISPREDICTIONS"), "mispredictions"),
        ("Mispred/1K Instructions", trace_data.get("MISPRED_PER_1K_INST"), ""),
    ]

    cards = []
    for title, value, unit in stats:
        if isinstance(value, float) and value < 1:
            display_value = f"{value:.6f}"
        else:
            display_value = format_large_number(value)

        cards.append(
            html.Div(
                className="stat-card",
                children=[
                    html.H4(title, className="stat-title"),
                    html.P(display_value, className="stat-value"),
                    html.P(unit, className="stat-unit"),
                ],
            )
        )

    return cards

def parse_data_for_treemap(data, root_name):
    labels = [root_name]
    parents = [""]
    values = [0]

    def recursive_parse(node_list, parent_name):
        for item in node_list:
            key = item['key']
            val = item['value']

            labels.append(key)
            parents.append(parent_name)

            if isinstance(val, list):
                # Container node
                values.append(0)
                recursive_parse(val, key)
            else:
                # Leaf node
                values.append(val)

    recursive_parse(data, root_name)

    return labels, parents, values

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
        colorbar=dict(title="MPKBr"),
    ))

    fig.update_layout(
        title=f"MPKBr Periodic Heatmap ({actual_size}x{actual_size} periods)",
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


def create_predictor_info(config: dict) -> html.Div:
    """Create predictor configuration display."""
    predictor = config.get("predictor", {})
    reproduction = config.get("reproduction", {})

    predictor_info = html.Div([
        html.H4("Predictor Information"),
        html.Table([
            html.Tr([html.Td("Name:"), html.Td(predictor.get("name", "N/A"))]),
            html.Tr([html.Td("Version:"), html.Td(predictor.get("version", "N/A"))]),
            html.Tr([html.Td("CBP Version:"), html.Td(predictor.get("CBP_ver", "N/A"))]),
        ], className="info-table")
    ])

    repro_info = html.Div([
        html.H4("Simulation Information"),
        html.Table([
            html.Tr([html.Td("Date:"), html.Td(reproduction.get("date_of_run", "N/A"))]),
            html.Tr([html.Td("MPKI:"), html.Td(f"{reproduction.get('MPKI', 'N/A'):.4f}" if reproduction.get('MPKI') else "N/A")]),
            html.Tr([html.Td("Number of Traces:"), html.Td(str(reproduction.get("num_traces", "N/A")))]),
        ], className="info-table")
    ])

    return html.Div(
        className="predictor-info-container",
        children=[predictor_info, repro_info]
    )


def create_app(data_path: str = "sample_data/example_data.json",
               config_path: str = "sample_data/predictor.yml") -> Dash:
    """Create and configure the Dash application."""

    sim_data = load_simulation_data(data_path)
    predictor_config = load_predictor_config(config_path)

    trace_names = list(sim_data.keys())
    default_trace = trace_names[0]

    app = Dash(__name__)

    app.layout = html.Div(
        className="main-container",
        children=[

            # Store simulation data in browser
            dcc.Store(id='sim-data-store', data=sim_data),

            # Header with trace selector
            html.Div(
                className="header",
                children=[
                    html.H1("Branch Predictor Visualization"),
                    html.Div(
                        className="trace-selector",
                        children=[
                            html.Label("Select Trace:"),
                            dcc.Dropdown(
                                id='trace-dropdown',
                                options=[{'label': name, 'value': name} for name in trace_names],
                                value=default_trace,
                                className="trace-dropdown",
                                clearable=False,
                                style={'color': '#333'}
                            ),
                        ]
                    ),
                ]
            ),

            html.Div(
                className="chart-container",
                children=[
                    html.H3("Summary Statistics", className="section-title"),
                    html.Div(id='stats-container', className="stats-container"),
                ]
            ),

            html.Div([
                html.H3("Predictor Configuration", className="section-title"),
                create_predictor_info(predictor_config),
            ], className="chart-container"),

            html.Div(
                className="chart-container",
                children=[
                    html.H3("Size of Individual Predictor Components", className="section-title"),
                    html.P(
                        "Visualization of predictor structure and size of all components.",
                        className="tree-map-description"
                    ),
                    dcc.Graph(id='tree-map'),
                ]
            ),
            html.Div(
                className="chart-container",
                children=[
                    html.H3("MPKBr Periodic Heatmap", className="section-title"),
                    html.P(
                        "Visualization of mispredictions per 1K branches over time periods. "
                        "Each cell represents a measurement period.",
                        className="heatmap-description"
                    ),
                    dcc.Graph(id='heatmap-graph'),
                ]
            ),
            html.Div(
                className="chart-container",
                children=[
                    html.H3("Misspredictions Per Thousand Branches (MPKBr) over Time", className="section-title"),
                    html.P(
                        "Visualization of mispredictions per 1K branches over time periods. "
                        "Each point represents a thousand retired branches.",
                        className="heatmap-description"
                    ),
                    dcc.Graph(id='timeseries-graph'),
                ]
            ),
        ]
    )

    #not tested
    @app.callback(
        Output('stats-container', 'children'),
        Input('trace-dropdown', 'value'),
        Input('sim-data-store', 'data')
    )
    def update_stats(selected_trace, sim_data):
        if not selected_trace or not sim_data:
            return []
        trace_data = sim_data.get(selected_trace, {})
        return create_summary_cards(trace_data)

    @app.callback(
        Output('heatmap-graph', 'figure'),
        Input('trace-dropdown', 'value'),
        Input('sim-data-store', 'data')
    )
    def update_heatmap(selected_trace, sim_data):
        if not selected_trace or not sim_data:
            return go.Figure()
        trace_data = sim_data.get(selected_trace, {})
        return create_heatmap(trace_data.get("MPKBr_periodic", []))

    @app.callback(
        Output('timeseries-graph', 'figure'),
        Input('trace-dropdown', 'value'),
        Input('sim-data-store', 'data')
    )
    def update_timeseries(selected_trace, sim_data):
        if not selected_trace or not sim_data:
            return go.Figure()
        trace_data = sim_data.get(selected_trace, {})
        return create_timeseries(trace_data.get("MPKBr_periodic", []))

    @app.callback(
        Output('tree-map', 'figure'),
        Input('trace-dropdown', 'value'),
        Input('sim-data-store', 'data')
    )
    def update_tree_map(selected_trace, sim_data):
        if not selected_trace or not sim_data:
            return go.Figure()
        trace_data = sim_data.get(selected_trace, {})
        return create_tree_map(trace_data.get("size_map", []))

    return app

if __name__ == "__main__":
    app = create_app()
    print("Starting Branch Predictor Visualization Dashboard")
    app.run(debug=True)
