"""
Branch Predictor Visualization Dashboard
"""

from dash import Dash, html, dcc, Output, Input, dash_table
import plotly.graph_objects as go

from src.utils import (
    load_all_simulation_data,
    load_predictor_config,
    extract_trace_summary,
    parse_data_for_loop_frequencies,
)
from src.components.treemap import create_tree_map
from src.components.heatmap import create_heatmap
from src.components.src_misp import create_src_misp_graph
from src.components.bar_chart import create_bar_graph
from src.components.timeseries import create_timeseries
from src.components.stacked import create_stacked_area
from src.components.predictor_info import create_predictor_info
from src.components.summary_cards import create_summary_cards

GRAPH_CONFIG = {
    'toImageButtonOptions': {
        'format': 'svg', 
        'filename': 'image',
        'height': 600,
        'width': 1000,
        'scale': 1
    },
}

def create_app(data_folder: str = "sample_data",
               config_path: str = "sample_data/predictor.yml") -> Dash:
    """Create and configure the Dash application."""

    sim_data = load_all_simulation_data(data_folder)
    predictor_config = load_predictor_config(config_path)

    trace_names = list(sim_data.keys())
    default_trace = trace_names[0] if trace_names else None

    # Build table data with summary statistics for each trace
    table_data = [
        extract_trace_summary(name, sim_data[name])
        for name in trace_names
    ]

    app = Dash(__name__)
    app.title = "PredictViz"

    app.layout = html.Div(
        className="main-container",
        children=[

            # Store simulation data in browser
            dcc.Store(id='sim-data-store', data=sim_data),

            # Header
            html.Div(
                className="header",
                children=[
                    html.H1("Branch Predictor Visualization"),
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

            # Trace selector table
            html.Div(
                className="chart-container trace-table-container",
                children=[
                    html.H3("Select Trace", className="section-title"),
                    html.P(
                        "Click on a row to select a trace and update visualizations.",
                        className="heatmap-description"
                    ),
                    dash_table.DataTable(
                        id='trace-table',
                        columns=[
                            {"name": "Trace", "id": "Trace"},
                            {"name": "Instructions", "id": "NUM_INSTRUCTIONS", "type": "numeric",
                             "format": {"specifier": ",.0f"}},
                            {"name": "Branches", "id": "NUM_BR", "type": "numeric",
                             "format": {"specifier": ",.0f"}},
                            {"name": "Uncond. Branches", "id": "NUM_UNCOND_BR", "type": "numeric",
                             "format": {"specifier": ",.0f"}},
                            {"name": "Cond. Branches", "id": "NUM_CONDITIONAL_BR", "type": "numeric",
                             "format": {"specifier": ",.0f"}},
                            {"name": "Mispredictions", "id": "NUM_MISPREDICTIONS", "type": "numeric",
                             "format": {"specifier": ",.0f"}},
                            {"name": "Mispred/1K Inst", "id": "MISPRED_PER_1K_INST", "type": "numeric",
                             "format": {"specifier": ".4f"}},
                        ],
                        data=table_data,
                        style_table={'overflowX': 'auto'},
                        style_cell={
                            'textAlign': 'left',
                            'padding': '12px 15px',
                            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                        },
                        style_header={
                            'backgroundColor': '#1a365d',
                            'color': 'white',
                            'fontWeight': 'bold',
                            'textAlign': 'left',
                        },
                        style_data={
                            'backgroundColor': 'white',
                            'color': '#333',
                        },
                        style_data_conditional=[
                            {
                                'if': {'state': 'active'},
                                'backgroundColor': '#e2e8f0',
                                'border': '1px solid #1a365d',
                            },
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': '#f8fafc',
                            },
                        ],
                        page_size=10,
                        sort_action="native",
                        sort_mode="single",
                    ),
                    # Store the selected trace name
                    dcc.Store(id='selected-trace-store', data=default_trace),
                ]
            ),

            html.Div(
                className="chart-container",
                children=[
                    html.H3("Summary Statistics", className="section-title"),
                    html.Div(id='stats-container', className="stats-container"),
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
                    dcc.Graph(id='timeseries-graph', config=GRAPH_CONFIG),
                ]
            ),
            html.Div(
                className="chart-container",
                children=[
                    html.H3("Number of usefull entries in each TAGE Table", className="section-title"),
                    html.P(
                        "Evolution of usefull entries in each TAGE table. "
                        "Sudden dips represent U bit reset which marks entries as not usefull.",
                        className="heatmap-description"
                    ),
                    dcc.Graph(id='stacked-graph', config=GRAPH_CONFIG),
                ]
            ),

            html.Div(
                className="chart-container",
                children=[
                    html.H3("Bimodal Table Access Heatmap", className="section-title"),
                    html.P(
                        "Visualization of number of access into Bimodal table memory. "
                        "Each cell represents one Bimodal counter.",
                        className="heatmap-description"
                    ),
                    dcc.Graph(id='heatmap-graph', config=GRAPH_CONFIG),
                ]
            ),
            html.Div(
                className="chart-container",
                children=[
                    html.H3("Source of Mispredictions", className="section-title"),
                    html.P(
                        "The TAGE-SC-L predictor has two main components"
                        " which can be used as a source for prediction -"
                        " TAGE prediction and the Loop predictor."
                        " Additionally, the prediction can be subsequently"
                        " corrected by a Statistical Corrector (SC) component.",
                        className="heatmap-description"
                    ),
                    dcc.Graph(id='src-misp-graph', config=GRAPH_CONFIG),
                ]
            ),
            html.Div(
                className="chart-container",
                children=[
                    html.H3("Lengths of Loops Predicted by Loop Predictor", className="section-title"),
                    html.P(
                        "The Loop predictor component finds loops of up to 1024 iterations"
                        " and is able to predict them perfectly.",
                        className="heatmap-description"
                    ),
                    dcc.Graph(id='loop-frequencies'),
                ]
            ),
        ]
    )

    # Callback to update selected trace store when a cell is clicked
    # Uses active_cell and derived_virtual_data (sorted view) to get the trace name
    @app.callback(
        Output('selected-trace-store', 'data'),
        Input('trace-table', 'active_cell'),
        Input('trace-table', 'derived_virtual_data')
    )
    def update_selected_trace(active_cell, virtual_data):
        if active_cell is None or not virtual_data:
            return default_trace
        row_idx = active_cell['row']
        if row_idx < len(virtual_data):
            return virtual_data[row_idx]['Trace']
        return default_trace

    @app.callback(
        Output('stats-container', 'children'),
        Input('selected-trace-store', 'data'),
        Input('sim-data-store', 'data')
    )
    def update_stats(selected_trace, sim_data):
        if not selected_trace or not sim_data:
            return []
        trace_data = sim_data.get(selected_trace, {})
        return create_summary_cards(trace_data)

    @app.callback(
        Output('heatmap-graph', 'figure'),
        Input('selected-trace-store', 'data'),
        Input('sim-data-store', 'data')
    )
    def update_heatmap(selected_trace, sim_data):
        if not selected_trace or not sim_data:
            return go.Figure()
        trace_data = sim_data.get(selected_trace, {})
        return create_heatmap(trace_data.get("heatmap_bimodal_table", []))

    @app.callback(
        Output('timeseries-graph', 'figure'),
        Input('selected-trace-store', 'data'),
        Input('sim-data-store', 'data')
    )
    def update_timeseries(selected_trace, sim_data):
        if not selected_trace or not sim_data:
            return go.Figure()
        trace_data = sim_data.get(selected_trace, {})
        return create_timeseries(trace_data.get("MPKBr_periodic", []))

    @app.callback(
        Output('tree-map', 'figure'),
        Input('selected-trace-store', 'data'),
        Input('sim-data-store', 'data')
    )
    def update_tree_map(selected_trace, sim_data):
        if not selected_trace or not sim_data:
            return go.Figure()
        trace_data = sim_data.get(selected_trace, {})
        return create_tree_map(trace_data.get("size_map", []))

    @app.callback(
        Output('stacked-graph', 'figure'),
        Input('selected-trace-store', 'data'),
        Input('sim-data-store', 'data')
    )
    def update_stacked_graph(selected_trace, sim_data):
        if not selected_trace or not sim_data:
            return go.Figure()
        trace_data = sim_data.get(selected_trace, {})
        names = [ "Shared table 1", "Shared table 2" ]
        return create_stacked_area(trace_data.get("tage_usefull_entries", []), names)

    @app.callback(
        Output('src-misp-graph', 'figure'),
        Input('selected-trace-store', 'data'),
        Input('sim-data-store', 'data')
    )
    def update_src_misp_graph(selected_trace, sim_data):
        if not selected_trace or not sim_data:
            return go.Figure()
        trace_data = sim_data.get(selected_trace, {})
        return create_src_misp_graph(trace_data)

    @app.callback(
        Output('loop-frequencies', 'figure'),
        Input('selected-trace-store', 'data'),
        Input('sim-data-store', 'data')
    )
    def update_loop_freq_graph(selected_trace, sim_data):
        if not selected_trace or not sim_data:
            return go.Figure()
        trace_data = sim_data.get(selected_trace, {})

        data = parse_data_for_loop_frequencies(trace_data.get("loop_predictor_loop_counts", []))
        return create_bar_graph(data)


    return app

# Create app instance at module level for gunicorn
app = create_app()
server = app.server  # Gunicorn will import this

if __name__ == "__main__":
    print("Starting Branch Predictor Visualization Dashboard")
    app.run(debug=True)
