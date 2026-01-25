import json
import yaml
import os
from pathlib import Path


def load_simulation_data(json_path: str) -> dict:
    """Load simulation results from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def load_all_simulation_data(data_folder: str) -> dict:
    """Load all simulation results from JSON files in a folder.

    Returns a dict mapping trace names to their data.
    """
    all_data = {}
    folder_path = Path(data_folder)

    for json_file in folder_path.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                file_data = json.load(f)
                # Each JSON file may contain multiple traces
                all_data.update(file_data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load {json_file}: {e}")

    return all_data


def extract_trace_summary(trace_name: str, trace_data: dict) -> dict:
    """Extract summary statistics from a trace for table display."""
    return {
        "Trace": trace_name,
        "NUM_INSTRUCTIONS": trace_data.get("NUM_INSTRUCTIONS", 0),
        "NUM_BR": trace_data.get("NUM_BR", 0),
        "NUM_UNCOND_BR": trace_data.get("NUM_UNCOND_BR", 0),
        "NUM_CONDITIONAL_BR": trace_data.get("NUM_CONDITIONAL_BR", 0),
        "NUM_MISPREDICTIONS": trace_data.get("NUM_MISPREDICTIONS", 0),
        "MISPRED_PER_1K_INST": trace_data.get("MISPRED_PER_1K_INST", 0.0),
    }


def load_predictor_config(yaml_path: str) -> dict:
    """Load predictor configuration from YAML file."""
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)


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

def parse_data_for_loop_frequencies(data: dict) -> dict:
    """
    Parses the raw dictionary object into a sorted frequency dictionary.
    """
    if not data:
        return {}

    sorted_data = sorted(data, key=lambda x: x.get("key", 0))

    result_dict = {
        item.get("key"): item.get("value") 
        for item in sorted_data
    }

    return result_dict

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
