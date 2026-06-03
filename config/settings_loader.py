"""Settings loader for converter app configuration."""

import json
from pathlib import Path


def get_settings() -> dict:
    """Load application settings from config/settings.json.

    Returns:
        Dictionary of settings with defaults applied for missing keys.
    """
    default_settings = {
        "rate_expiry_hours": 24,
        "default_currencies": ["USD", "EUR", "GBP", "INR", "JPY"],
        "network_timeout_seconds": 5,
        "max_input_value": 1_000_000_000.0,
        "decimal_precision": 4,
    }

    settings_path = Path(__file__).resolve().parent.parent / "config" / "settings.json"

    if not settings_path.exists():
        return default_settings

    try:
        with open(settings_path, "r") as f:
            user_settings = json.load(f)
        # Merge with defaults (user values override)
        merged = dict(default_settings)
        merged.update(user_settings)
        return merged
    except (json.JSONDecodeError, OSError):
        return default_settings
