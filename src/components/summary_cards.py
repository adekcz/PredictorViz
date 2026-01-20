from dash import html
from src.utils import format_large_number


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
