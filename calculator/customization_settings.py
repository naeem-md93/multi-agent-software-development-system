import os
import json

# Default configuration
DEFAULT_CONFIG = {
    'output_verbosity': 'normal',
    'coding_standards': 'PEP8'
}

CONFIG_FILE = 'config.json'

def load_config():
    """Load configuration from the config file. If the file does not exist, use defaults."""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

def save_config(config):
    """Save the configuration to the config file."""
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)

def update_config(setting, value):
    """Update a specific configuration setting."""
    config = load_config()
    config[setting] = value
    save_config(config)

def get_config(setting):
    """Retrieve the value of a specific configuration setting."""
    config = load_config()
    return config.get(setting, DEFAULT_CONFIG.get(setting))

# Example usage
if __name__ == '__main__':
    print('Current configuration:', load_config())
    update_config('output_verbosity', 'verbose')
    print('Updated configuration:', load_config())
