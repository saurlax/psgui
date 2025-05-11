import os
import json

# Default configuration
DEFAULT_CONFIG = {
    "duration": 5,
    "picoscenes_rx_command": "-d debug -i 2 --mode logger --preset RX_CBW_80 --plot",
    "subfolder_name": "default"
}

CONFIG_FILE = "psgui.json"


def load_config():
    """Load configuration from JSON file, use default if not exists"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        else:
            return DEFAULT_CONFIG.copy()
    except Exception:
        # Use default config if parsing fails
        return DEFAULT_CONFIG.copy()


def save_config(config):
    """Save configuration to JSON file"""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False
