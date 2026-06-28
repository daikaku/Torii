from typing import Any

import requests

def get_own_account_id(config: dict[str, Any]) -> str:
    """Return the authenticated Mastodon account ID."""
    instance = config["mastodon"]["instance"]
    token = config["mastodon"]["access_token"]

    r = requests.get(
        f"{instance}/api/v1/accounts/verify_credentials",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["id"]


def get_latest_statuses(
    config: dict[str, Any],
    account_id: str,
    ) -> list[dict[str, Any]]:
    """Fetch the latest Mastodon statuses."""
    instance = config["mastodon"]["instance"]
    token = config["mastodon"]["access_token"]

    r = requests.get(
        f"{instance}/api/v1/accounts/{account_id}/statuses",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "limit": 5,
            "exclude_reblogs": str(not config["options"]["include_boosts"]).lower(),
            "exclude_replies": str(not config["options"]["include_replies"]).lower(),
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


