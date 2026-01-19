# 原神 Discord Bot

原神の情報を提供するDiscord Botです。HoYoLAB公式APIを使用してリアルタイム情報を取得できます。

## 主要機能

### 🎯 チームジェネレーター
- **コマンド**: `/team_generator`
- あなたの所持キャラクターから最適なチーム編成を自動生成
- HoYoLAB APIから実際の所持キャラを取得
- 役割別（メインDPS、サブDPS、サポート、ヒーラー）に自動分類

### 🔔 樹脂自動通知機能
- **コマンド**: `/resin_notification [有効/無効] [閾値]`
- 30分ごとにHoYoLAB APIで樹脂をチェック
- 設定した閾値（または満タン）に達したらDMで自動通知
- 定期チェックなので手動確認不要

### 📊 リアルタイム樹脂状況
- **コマンド**: `/resin_status`
- 現在の樹脂数と満タンまでの時間
- デイリー任務の進捗
- 週ボス割引の残り回数
- 洞天宝銭の状況
- 参量物質変換器の状態

### 👥 所持キャラクター一覧
- **コマンド**: `/characters`
- 実際の所持キャラクター一覧
- レベルとレアリティ別に表示
- HoYoLAB APIから自動取得

### ⚙️ 基本機能
- **樹脂計算機**: `/resin` - 樹脂の回復時間を手動計算
- **樹脂リマインダー**: `/resin_reminder` - 指定時間後にDM通知

## セットアップ

### 1. 必要なパッケージをインストール

```bash
cd genshin
pip install -r requirements.txt
```

### 2. Discord Botのトークンを設定

`.env` ファイルを作成:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

### 3. Botを起動

```bash
python bot.py
```

## Discord Bot の作成方法

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 「New Application」をクリックしてアプリケーションを作成
3. 「Bot」タブでBotを作成し、トークンをコピー
4. 「OAuth2」→「URL Generator」で以下の権限を設定:
   - `bot` scope
   - `applications.commands` scope
   - 権限: Send Messages, Embed Links, Read Message History
5. 生成されたURLからBotをサーバーに招待

## HoYoLAB Cookie の取得方法

### 💻 PC（推奨）

1. [HoYoLAB](https://www.hoyolab.com/) にログイン
2. ブラウザの開発者ツール (F12) を開く
3. Application/Storage → Cookies → https://www.hoyolab.com
4. `ltuid_v2` と `ltoken_v2` の値をコピー
5. Botに以下の形式でDM送信:
   ```
   /set_cookie ltuid_v2=123456789; ltoken_v2=abcdefghijklmnop...
   ```

### ⚠️ 重要な注意事項

- **必ずDMで実行**: `/set_cookie` はDMでのみ使用可能（セキュリティのため）
- **暗号化保存**: クッキーは暗号化してデータベースに保存されます
- **ログアウトで無効**: HoYoLABからログアウトすると再設定が必要です
- **安全に管理**: クッキー情報は他人に絶対に教えないでください

## 使用方法

### 初回設定

1. BotにDMを送信
2. `/set_cookie [クッキー]` でHoYoLABクッキーを設定
3. 設定完了後、各コマンドが使用可能に

### コマンド一覧

#### 認証情報管理
- `/set_cookie [クッキー]` - HoYoLABクッキー設定（DMのみ）
- `/delete_cookie` - 保存された認証情報を削除

#### メイン機能
- `/team_generator` - 所持キャラからチーム編成を生成
- `/resin_notification [有効/無効] [閾値]` - 樹脂自動通知の設定
- `/resin_status` - リアルタイム樹脂・デイリー状況
- `/characters` - 所持キャラクター一覧

#### 基本機能
- `/resin [現在の樹脂] [目標樹脂]` - 樹脂回復時間を計算
- `/resin_reminder [現在の樹脂]` - 満タン時にDM通知

## 機能詳細

### 🎯 チームジェネレーター

あなたの所持キャラクターから最適なチーム編成を自動生成します。

**特徴:**
- HoYoLAB APIから実際の所持キャラを取得
- キャラクターを役割別に自動分類（メインDPS、サブDPS、サポート、ヒーラー）
- バランスの取れたチーム編成を提案
- 何度でも再生成可能

**使用例:**
```
/team_generator
```

### 🔔 樹脂自動通知

定期的に樹脂をチェックして、自動でDM通知を送ります。

**特徴:**
- 30分ごとに自動チェック
- 閾値を設定可能（デフォルト: 満タン）
- DMで通知するのでサーバーを汚さない
- いつでも有効/無効を切り替え可能

**使用例:**
```
# 満タンで通知
/resin_notification 有効

# 160に達したら通知
/resin_notification 有効 160

# 通知を停止
/resin_notification 無効
```

## 複数人での使用

- ✅ 各ユーザーが個別に認証情報を設定・管理
- ✅ 暗号化されたデータベースで安全に保存
- ✅ ユーザー間でのデータ漏洩防止
- ✅ Bot再起動後もデータ保持

## トラブルシューティング

### クッキーエラーが出る
- HoYoLABに再ログインして新しいクッキーを設定してください
- ログアウトした場合は必ず再設定が必要です

### コマンドが表示されない
- Botを招待し直して、スラッシュコマンド権限を付与してください
- Bot再起動後、コマンドの同期に数分かかることがあります

### 通知が来ない
- DMの受信設定を確認してください
- `/resin_notification` が有効になっているか確認してください

## セキュリティ

- 認証情報の設定は必ずDMで行ってください
- クッキーは暗号化して保存されます
- 他のユーザーからはアクセスできません
- クッキー情報は絶対に他人に共有しないでください

## 必要なライブラリ

- `discord.py` - Discord Bot API
- `genshin.py` - HoYoLAB API ラッパー
- `cryptography` - クッキー暗号化
- `python-dotenv` - 環境変数管理

## ライセンス

このBotはHoYoLAB公式APIを使用しています。利用規約を遵守してご使用ください。
