import re

import requests
from atproto import Client
from bs4 import BeautifulSoup

from media import download_media

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


