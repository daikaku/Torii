# Torii

A lightweight bridge between Mastodon and Bluesky.

Torii automatically cross-posts your public Mastodon posts to Bluesky while preserving media attachments, alt text, and long-form content whenever possible.

## Features

- Cross-post public posts
- Image support (up to 4 images)
- Alt text preservation
- Long post truncation with a link back to Mastodon
- Automatic duplicate prevention
- Robust logging
- Safe retry mechanism

## Planned

- Video support
- launchd integration
- Bidirectional synchronization
- Misskey support
- Threads support

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy

```
.env.example
```

to

```
.env
```

and edit

```
config.yaml
```

## License

MIT License
