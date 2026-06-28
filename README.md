# Torii

**Torii** is a lightweight bridge that automatically cross-posts your public Mastodon posts to Bluesky.

It preserves images, videos, alt text, and external link previews while preventing duplicate posts.

## Features

- 🚀 Cross-post public Mastodon posts to Bluesky
- 🖼️ Support up to 4 images
- 🎥 Video support
- 🔗 External URL card support (Open Graph)
- ♿ Preserve image and video alt text
- 🔄 Automatic duplicate prevention
- ⚙️ Automatic execution with macOS `launchd`

## Requirements

- Python 3.13 or later
- A Mastodon account
- A Bluesky account with an App Password

## Installation

Clone the repository.

```bash
git clone https://github.com/daikaku/Torii.git
cd Torii
```

Create a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

## Configuration

Copy the example environment file.

```bash
cp .env.example .env
```

Edit `.env`.

```text
MASTODON_TOKEN=...
BLUESKY_APP_PASSWORD=...
```

Edit `config.yaml`.

```yaml
mastodon:
  instance: https://your.instance

bluesky:
  handle: yourname.bsky.social

options:
  include_replies: false
  include_boosts: false
```

## Usage

Run once.

```bash
python main.py
```

Torii remembers previously cross-posted statuses using `state.json`, so duplicate posts are automatically skipped.

## Automatic execution (macOS)

Torii can be executed automatically using `launchd`.

A sample LaunchAgent configuration is included in the documentation.

## Project structure

```
main.py         Entry point
mastodon.py     Mastodon API
bluesky.py      Bluesky API
media.py        Image / video handling
links.py        URL card handling
config.py       Configuration
state.py        Duplicate prevention
```

## Roadmap

- Logging improvements
- Clickable URL facets
- Misskey support
- Thread support

## License

MIT License