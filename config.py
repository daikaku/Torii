import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent


def load_config() -> dict[str, Any]:
    """Load configuration and secrets."""
    load_dotenv(BASE_DIR / ".env")

    with open(BASE_DIR / "config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    config["mastodon"]["access_token"] = os.environ["MASTODON_TOKEN"]
    config["bluesky"]["app_password"] = os.environ["BLUESKY_APP_PASSWORD"]

    return config
