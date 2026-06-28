# Installing Torii

Torii is a small Python application that automatically cross-posts your public Mastodon posts to Bluesky.

## 1. Requirements

* Python 3.13 or later
* A Mastodon account
* A Bluesky account
* A Mastodon access token
* A Bluesky App Password

## 2. Clone the repository

```bash
git clone https://github.com/daikaku/Torii.git
cd Torii
```

## 3. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Configure environment variables

Copy `.env.example` to `.env`.

```bash
cp .env.example .env
```

Edit `.env`.

```text
MASTODON_TOKEN=your_mastodon_access_token
BLUESKY_APP_PASSWORD=your_bluesky_app_password
```

## 6. Edit config.yaml

Edit `config.yaml`.

```yaml
mastodon:
  instance: "https://your.mastodon.instance"

bluesky:
  handle: "yourname.bsky.social"

options:
  include_replies: false
  include_boosts: false
```

Example:

```yaml
mastodon:
  instance: "https://fedibird.com"

bluesky:
  handle: "example.bsky.social"

options:
  include_replies: false
  include_boosts: false
```

## 7. Run Torii once

```bash
python main.py
```

If everything is configured correctly, you should see:

```text
Done.
```

Torii stores already cross-posted Mastodon status IDs in `state.json`, so the same post will not be posted twice.

## 8. Run automatically on macOS

You can use `launchd` to run Torii automatically every 5 minutes.

Create a LaunchAgent file:

```bash
nano ~/Library/LaunchAgents/jp.daikaku.torii.plist
```

Adjust the paths for your environment.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>jp.daikaku.torii</string>

    <key>ProgramArguments</key>
    <array>
        <string>/path/to/Torii/.venv/bin/python</string>
        <string>/path/to/Torii/main.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/path/to/Torii</string>

    <key>StartInterval</key>
    <integer>300</integer>

    <key>RunAtLoad</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/path/to/Torii/logs/stdout.log</string>

    <key>StandardErrorPath</key>
    <string>/path/to/Torii/logs/stderr.log</string>
</dict>
</plist>
```

Create the log directory.

```bash
mkdir -p logs
```

Load the LaunchAgent.

```bash
launchctl load ~/Library/LaunchAgents/jp.daikaku.torii.plist
```

Check that it is loaded.

```bash
launchctl list | grep torii
```

If `jp.daikaku.torii` appears, Torii is registered successfully.

## 9. Stop automatic execution

```bash
launchctl unload ~/Library/LaunchAgents/jp.daikaku.torii.plist
```

## 10. Check logs

```bash
tail -20 logs/stdout.log
tail -20 logs/stderr.log
```

If `stderr.log` is empty, Torii is probably running correctly.

