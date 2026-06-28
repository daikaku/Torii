from config import load_config
from state import load_state, save_state
from media import (
    download_media,
    prepare_image_for_bluesky,
    is_video,
)


import json
import os
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup
from atproto import Client, models
from dotenv import load_dotenv
from PIL import Image

import io
import re
from typing import Any


def html_to_text(html: str) -> str:
    """Convert Mastodon HTML content into plain text."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n").strip()

def extract_first_url(text: str) -> str | None:
    """Return the first URL found in text."""
    match = re.search(r"https?://\S+", text)
    if match:
        return match.group(0)
    return None

def get_link_metadata(url: str) -> dict[str, str] | None:
    """Fetch Open Graph metadata from a URL."""

    try:
        r = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Torii/1.0 (+https://github.com/)"
            },
        )
        r.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    def og(name: str) -> str | None:
        tag = soup.find("meta", property=name)
        if tag:
            return tag.get("content")
        return None

    title = (
        og("og:title")
        or (soup.title.string.strip() if soup.title and soup.title.string else "")
    )

    description = (
        og("og:description")
        or ""
    )

    image = (
        og("og:image")
        or ""
    )

    return {
        "url": url,
        "title": title,
        "description": description,
        "image": image,
    }

def upload_external_thumb(
    client: Client,
    image_url: str,
):
    """Download an OGP image and upload it to Bluesky."""

    if not image_url:
        return None

    try:
        image_bytes = download_media(image_url)
        return client.upload_blob(image_bytes).blob
    except Exception as e:
        print(f"Failed to upload OGP image: {e}")
        return None


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


def post_to_bluesky(
    client: Client,
    text: str,
    media: list[dict[str, Any]],
    metadata: dict[str, str] | None = None,
) -> None:
    """Post a status with up to four images to Bluesky."""

    # 画像・動画がない場合
    if not media:
        if metadata:
            thumb = None

            if metadata.get("image"):
                thumb = upload_external_thumb(
                    client,
                    metadata["image"],
                )

            embed = models.AppBskyEmbedExternal.Main(
                external=models.AppBskyEmbedExternal.External(
                    uri=metadata["url"],
                    title=metadata["title"],
                    description=metadata["description"],
                    thumb=thumb,
                )
            )

            client.send_post(text=text, embed=embed)
        else:
            client.send_post(text=text)

        return

    # 動画
    if is_video(media):
        video = next(
            attachment
            for attachment in media
            if attachment.get("type") in ("video", "gifv")
        )

        video_bytes = download_media(video["url"])
        alt = video.get("description") or ""

        client.send_video(
            text=text,
            video=video_bytes,
            video_alt=alt,
        )
        return

    # 画像
    images = []
    image_alts = []

    for image in media[:4]:
        try:
            image_bytes = prepare_image_for_bluesky(
                download_media(image["url"])
            )
        except Exception as e:
            print(f"Skipping image: {e}")
            continue

        images.append(image_bytes)
        image_alts.append(image.get("description") or "")

    if not images:
        client.send_post(text=text)
        return

    client.send_images(
        text=text,
        images=images,
        image_alts=image_alts,
    )

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
