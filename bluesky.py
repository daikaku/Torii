from typing import Any

from atproto import Client, models

from links import upload_external_thumb
from media import (
    download_media,
    is_video,
    prepare_image_for_bluesky,
)

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

