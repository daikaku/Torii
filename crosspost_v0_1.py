import json
import os
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup
from atproto import Client
from dotenv import load_dotenv
from PIL import Image

import io

def download_media(url):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.content

def prepare_image_for_bluesky(image_bytes):
    MAX_SIZE = 2_000_000

    if len(image_bytes) <= MAX_SIZE:
        return image_bytes

    image = Image.open(io.BytesIO(image_bytes))

    # JPEGに変換（アルファチャンネルがあれば白背景にする）
    if image.mode in ("RGBA", "LA"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.getchannel("A"))
        image = background
    elif image.mode != "RGB":
        image = image.convert("RGB")

    quality = 95

    while quality >= 40:
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=quality, optimize=True)

        data = output.getvalue()

        if len(data) <= MAX_SIZE:
            print(f"Image compressed to {len(data):,} bytes (quality={quality})")
            return data

        quality -= 5

    raise ValueError("Unable to compress image below Bluesky size limit.")

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / "state.json"


def load_config():
    load_dotenv(BASE_DIR / ".env")

    with open(BASE_DIR / "config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    config["mastodon"]["access_token"] = os.environ["MASTODON_TOKEN"]
    config["bluesky"]["app_password"] = os.environ["BLUESKY_APP_PASSWORD"]
    return config


def load_state():
    if not STATE_FILE.exists():
        return {"posted_ids": []}

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n").strip()


def get_own_account_id(config):
    instance = config["mastodon"]["instance"]
    token = config["mastodon"]["access_token"]

    r = requests.get(
        f"{instance}/api/v1/accounts/verify_credentials",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["id"]


def get_latest_statuses(config, account_id):
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


def post_to_bluesky(config, text, media):
    client = Client()
    client.login(
        config["bluesky"]["handle"],
        config["bluesky"]["app_password"],
    )

    if not media:
        client.send_post(text)
        return

    image = media[0]
    image_bytes = prepare_image_for_bluesky(
    download_media(image["url"])
    )
    alt = image.get("description") or ""
    client.send_images(
        text=text,
        images=[image_bytes],
        image_alts=[alt],
    )

def main():
    config = load_config()
    state = load_state()

    account_id = get_own_account_id(config)
    statuses = get_latest_statuses(config, account_id)

    # 古い順に投稿する
    for status in reversed(statuses):
        status_id = status["id"]

        if status_id in state["posted_ids"]:
            continue

        if status.get("visibility") != "public":
            continue

        text = html_to_text(status["content"])

        if not text:
            continue

        # Blueskyは基本300字まで
        if len(text) > 300:
            text = text[:280] + "\n\n（以下略）"

        print(f"Posting to Bluesky: {text}")
        media = status.get("media_attachments", [])
        post_to_bluesky(config, text, media)

        state["posted_ids"].append(status_id)
        save_state(state)

    print("Done.")


if __name__ == "__main__":
    main()
