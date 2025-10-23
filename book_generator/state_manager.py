import json
import os

def save_state(base_dir, state):
    """Saves the current application state to a JSON file."""
    state_filepath = os.path.join(base_dir, 'generation_state.json')
    with open(state_filepath, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4)

def load_state(base_dir):
    """Loads the application state from a JSON file if it exists."""
    state_filepath = os.path.join(base_dir, 'generation_state.json')
    if os.path.exists(state_filepath):
        with open(state_filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None
