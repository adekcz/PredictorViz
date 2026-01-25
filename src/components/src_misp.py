import plotly.graph_objects as go


def create_src_misp_graph(trace_data: dict) -> go.Figure:
    if not trace_data:
        fig = go.Figure()
        fig.update_layout(
            title="No MPKBr periodic data available",
            template="plotly_white",
            height=600,
        )
        return fig

    labels = [
        "TAGE Correct", "TAGE Incorrect", "Loop Correct", "Loop Incorrect",
        "Internal Prediction Correct", "Internal Prediction Incorrect",
        "Final Prediction Correct", "Final Prediction Incorrect"
    ]

    node_colors = [
        "mediumseagreen", "indianred", "mediumseagreen", "indianred",
        "mediumseagreen", "indianred", "mediumseagreen", "indianred"
    ]

    source = [ 0, 1, 2, 3, 4, 4, 4, 5, 5, 5 ]
    target = [ 4, 5, 4, 5, 6, 6, 7, 7, 7, 6]
    value = [
        trace_data.get("tage_correct", 0), trace_data.get("tage_incorrect", 0),
        trace_data.get("loop_correct", 0), trace_data.get("loop_incorrect", 0),
        trace_data.get("inter_correct_sc_agree", 0),
        trace_data.get("inter_correct_sc_flip_ignored", 0),
        trace_data.get("inter_correct_sc_flip", 0),
        trace_data.get("inter_incorrect_sc_agree", 0),
        trace_data.get("inter_incorrect_sc_flip_ignored", 0),
        trace_data.get("inter_incorrect_sc_flip", 0),
    ]

    link_colors = [
        "rgba(60, 179, 113, 0.4)",
        "rgba(205, 92, 92, 0.4)",
        "rgba(60, 179, 113, 0.4)",
        "rgba(205, 92, 92, 0.4)",
        
        "rgba(60, 179, 113, 0.4)",
        "rgba(60, 179, 113, 0.4)",
        "rgba(205, 92, 92, 0.4)",
        
        "rgba(205, 92, 92, 0.4)",
        "rgba(205, 92, 92, 0.4)",
        "rgba(60, 179, 113, 0.4)"
    ]

    link_labels = [
        "TAGE was Right", "TAGE was Wrong", "Loop Predictor was Right","Loop Predictor was Wrong",
        "Statistical Corrector Agreed", "Statistical Corrector Flip Ignored", "Statistical Corrector Flipped Prediction",
        "Statistical Corrector Agreed", "Statistical Corrector Flip Ignored", "Statistical Corrector Flipped Prediction"
    ]
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = labels,
          color = node_colors
        ),
        link = dict(
          source = source,
          target = target,
          value = value,
          color = link_colors,
          label = link_labels
      ))])

    fig.update_layout(title_text="Source of Mispredictions", font_size=10)

    return fig
