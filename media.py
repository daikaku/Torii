import io
from typing import Any

import requests
from PIL import Image

def download_media(url: str) -> bytes:
    """Download media from Mastodon and return its bytes."""
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.content

def prepare_image_for_bluesky(image_bytes: bytes) -> bytes:
    """Compress an image to fit within Bluesky's upload size limit."""
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

def is_video(media: list[dict[str, Any]]) -> bool:
    """Return True if the attachment contains a video."""
    return any(
        attachment.get("type") in ("video", "gifv")
        for attachment in media
    )

