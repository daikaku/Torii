from config import load_config
from state import load_state, save_state
from media import (
    download_media,
    prepare_image_for_bluesky,
    is_video,
)
from links import (
    html_to_text,
    extract_first_url,
    get_link_metadata,
    upload_external_thumb,
)
from mastodon import (
    get_own_account_id,
    get_latest_statuses,
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
