"""
Branch Predictor Visualization Dashboard
"""

from dash import Dash, html, dcc, Output, Input
import plotly.graph_objects as go

from src.utils import load_simulation_data, load_predictor_config
from src.components.treemap import create_tree_map
from src.components.heatmap import create_heatmap
from src.components.timeseries import create_timeseries
from src.components.predictor_info import create_predictor_info
from src.components.summary_cards import create_summary_cards


def create_app(data_path: str = "sample_data/example_data2.json",
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
