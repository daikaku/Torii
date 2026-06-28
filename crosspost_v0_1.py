from config import load_config
from state import load_state, save_state

from links import (
    html_to_text,
    get_link_metadata,
)

from mastodon import (
    get_own_account_id,
    get_latest_statuses,
)

from bluesky import post_to_bluesky

from bs4 import BeautifulSoup
from atproto import Client


def main() -> None:
    """Synchronize new Mastodon posts to Bluesky."""
    config = load_config()
    state = load_state()
    client = Client()
    client.login(
        config["bluesky"]["handle"],
        config["bluesky"]["app_password"],
        )

    account_id = get_own_account_id(config)
    statuses = get_latest_statuses(config, account_id)

    # 古い順に投稿する
    for status in reversed(statuses):
        status_id = status["id"]

        if status_id in state["posted_ids"]:
            continue

        if status.get("visibility") != "public":
            continue

        html = status["content"]

        text = html_to_text(html)
        
        soup = BeautifulSoup(html, "html.parser")
        link = soup.find("a", href=True)

        url = link["href"] if link else None
        metadata = get_link_metadata(url) if url else None

        spoiler = html_to_text(status.get("spoiler_text", ""))
        if spoiler:
            text = f"CW: {spoiler}\n\n{text}"

        if not text:
            continue

        # Blueskyは基本300字まで
        if len(text) > 300:
            text = text[:280] + "\n\n（以下略）"

        print(f"Posting to Bluesky: {text}")
        media = status.get("media_attachments", [])

        post_to_bluesky(client, text, media, metadata)
        state["posted_ids"].append(status_id)
        save_state(state)

    print("Done.")


if __name__ == "__main__":
    main()
