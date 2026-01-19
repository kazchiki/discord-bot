# 原神 Discord Bot

原神の情報を提供するDiscord Botです。複数の認証方式に対応し、スマホでも簡単に使えます。

## 機能

### 基本機能（認証不要）
- **キャラクター情報**: `/character` - 原神キャラクターの詳細情報を表示
- **ガチャシミュレーター**: `/gacha` - 単発・10連ガチャのシミュレーション
- **樹脂計算機**: `/resin` - 樹脂の回復時間を計算
- **樹脂リマインダー**: `/resin_reminder` - 樹脂満タン時にDMで通知
- **今日のドメイン**: `/daily_domain` - おすすめ聖遺物ドメイン
- **元素反応**: `/element_reaction` - 元素反応の詳細説明
- **チーム提案**: `/team_suggest` - ランダムチーム編成提案
- **聖遺物のコツ**: `/artifact_tips` - 厳選のヒント

### HoYoLAB Cookie方式（PC推奨）
- **リアルタイム樹脂状況**: `/resin_status` - 現在の樹脂・デイリー任務・週ボスの状況
- **所持キャラクター**: `/characters` - 実際の所持キャラクター一覧とレベル
- **クッキー設定**: `/set_cookie` - HoYoLABのクッキーを設定（DMのみ）

### Authkey方式（スマホ対応・推奨）
- **ガチャ履歴**: `/gacha_history` - 実際のガチャ履歴を表示
- **Authkey設定**: `/set_authkey` - Authkeyを設定（DMのみ）
- **取得方法**: `/authkey_help` - Authkey取得方法の説明

## セットアップ

1. 必要なパッケージをインストール:
```bash
pip install -r requirements.txt
```

2. `.env` ファイルを作成し、Discord Botのトークンを設定:
```
DISCORD_TOKEN=your_discord_bot_token_here
```

3. Botを起動:
```bash
python bot.py
```

## 認証方式の比較

| 方式 | 対応デバイス | 設定の簡単さ | 有効期限 | 取得可能データ |
|------|-------------|-------------|----------|---------------|
| **Authkey** | 📱スマホ・PC | ⭐⭐⭐ | 24時間 | ガチャ履歴 |
| **Cookie** | 💻PC | ⭐⭐ | ログアウトまで | 樹脂・キャラクター |

### 📱 Authkey方式（推奨）
**メリット:**
- スマホでも簡単に取得可能
- ログアウト不要
- ガチャ履歴が見れる

**デメリット:**
- 24時間で期限切れ
- 樹脂情報は取得不可

**取得方法:**
1. 原神アプリでガチャ画面を開く
2. 「履歴」をタップ
3. ブラウザのURLをコピー
4. `/set_authkey [URL] [UID]` で設定

### 💻 Cookie方式
**メリット:**
- リアルタイム樹脂情報
- 所持キャラクター情報
- 長期間有効

**デメリット:**
- PC必須
- ログアウトで無効化
- 取得が複雑

**取得方法:**
1. [HoYoLAB](https://www.hoyolab.com/) にログイン
2. ブラウザの開発者ツール (F12) を開く
3. Application/Storage → Cookies → https://www.hoyolab.com
4. `ltuid_v2` と `ltoken_v2` をコピー
5. `/set_cookie ltuid_v2=123456; ltoken_v2=abcdef...` で設定

## Discord Bot の作成方法

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 「New Application」をクリックしてアプリケーションを作成
3. 「Bot」タブでBotを作成し、トークンをコピー
4. 「OAuth2」→「URL Generator」で必要な権限を設定してBotをサーバーに招待

### 必要な権限
- Send Messages
- Use Slash Commands
- Embed Links
- Send Messages in Threads

## 使用方法

### 基本コマンド（認証不要）
- `/character [キャラクター名]` - キャラクター情報を表示
- `/gacha [回数]` - ガチャシミュレーション
- `/daily_domain` - 今日のおすすめドメイン
- `/element_reaction [反応]` - 元素反応の説明
- `/team_suggest` - ランダムチーム編成
- `/artifact_tips` - 聖遺物厳選のコツ

### Authkeyコマンド（スマホ対応）
- `/authkey_help` - 取得方法の説明
- `/set_authkey [URL/Authkey] [UID]` - Authkey設定（DMのみ）
- `/gacha_history [バナー]` - ガチャ履歴表示

### Cookieコマンド（PC）
- `/set_cookie [クッキー]` - HoYoLABクッキー設定（DMのみ）
- `/resin_status` - リアルタイム樹脂状況
- `/characters` - 所持キャラクター一覧

### 共通コマンド
- `/delete_cookie` - 保存された認証情報を削除

## 注意事項

- 認証情報の設定は必ずDMで行ってください（セキュリティのため）
- 認証情報は暗号化してデータベースに保存されます
- Authkeyは24時間で期限切れになります
- Cookieはログアウト時に無効になります
- API制限により、頻繁なリクエストは避けてください

## 複数人での使用

- ✅ 各ユーザーが個別に認証情報を設定・管理
- ✅ 暗号化されたデータベースで安全に保存
- ✅ ユーザー間でのデータ漏洩防止
- ✅ Bot再起動後もデータ保持
- ✅ スケーラブルな設計