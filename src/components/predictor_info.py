from dash import html


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
