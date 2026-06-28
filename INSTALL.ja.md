# Torii の設置方法

Torii は、Mastodon の公開投稿を Bluesky に自動で転送するための Python アプリケーションです。

## 1. 必要なもの

* Python 3.13 以上
* Mastodon アカウント
* Bluesky アカウント
* Mastodon のアクセストークン
* Bluesky の App Password

## 2. ダウンロード

```bash
git clone https://github.com/daikaku/Torii.git
cd Torii
```

## 3. 仮想環境を作る

```bash
python -m venv .venv
source .venv/bin/activate
```

## 4. 必要なライブラリを入れる

```bash
pip install -r requirements.txt
```

## 5. 環境変数を設定する

`.env.example` をコピーして `.env` を作ります。

```bash
cp .env.example .env
```

`.env` を開いて、次のように設定します。

```text
MASTODON_TOKEN=your_mastodon_access_token
BLUESKY_APP_PASSWORD=your_bluesky_app_password
```

## 6. config.yaml を設定する

`config.yaml` を編集します。

```yaml
mastodon:
  instance: "https://your.mastodon.instance"

bluesky:
  handle: "yourname.bsky.social"

options:
  include_replies: false
  include_boosts: false
```

例：

```yaml
mastodon:
  instance: "https://fedibird.com"

bluesky:
  handle: "example.bsky.social"

options:
  include_replies: false
  include_boosts: false
```

## 7. 一度だけ実行して確認する

```bash
python main.py
```

次のように表示されれば成功です。

```text
Done.
```

Torii は `state.json` に投稿済み ID を記録するため、同じ投稿を何度も転送しません。

## 8. macOS で自動実行する

5分ごとに自動実行したい場合は、`launchd` を使います。

`~/Library/LaunchAgents/jp.daikaku.torii.plist` を作成します。

```bash
nano ~/Library/LaunchAgents/jp.daikaku.torii.plist
```

中身は環境に合わせて変更してください。

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

`logs` ディレクトリを作ります。

```bash
mkdir -p logs
```

登録します。

```bash
launchctl load ~/Library/LaunchAgents/jp.daikaku.torii.plist
```

確認します。

```bash
launchctl list | grep torii
```

`jp.daikaku.torii` が表示されれば成功です。

## 9. 停止する場合

```bash
launchctl unload ~/Library/LaunchAgents/jp.daikaku.torii.plist
```

## 10. ログを見る

```bash
tail -20 logs/stdout.log
tail -20 logs/stderr.log
```

`stderr.log` にエラーが出ていなければ、基本的には正常に動作しています。

