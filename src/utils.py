import json
import yaml

def load_simulation_data(json_path: str) -> dict:
    """Load simulation results from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)


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
