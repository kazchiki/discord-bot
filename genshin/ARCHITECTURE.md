# アーキテクチャ設計書

このBotはMVCパターンに近い設計を採用しています。

## 📁 ディレクトリ構造

```
genshin/
├── bot.py                      # エントリーポイント
├── config/                     # 設定・定数管理
│   ├── __init__.py
│   └── constants.py           # 定数定義
├── models/                     # Model層 - データ構造とDB操作
│   ├── __init__.py
│   ├── database.py            # データベースアクセス層
│   └── user.py                # ユーザーデータモデル
├── services/                   # Service層 - ビジネスロジック
│   ├── __init__.py
│   ├── hoyolab_service.py     # HoYoLAB API連携
│   ├── resin_service.py       # 樹脂計算ロジック
│   ├── team_service.py        # チーム編成ロジック
│   └── notification_service.py # 通知ロジック
├── views/                      # View層 - Discord表示
│   ├── __init__.py
│   ├── embeds.py              # Embed生成
│   └── formatters.py          # テキストフォーマット
└── controllers/                # Controller層 - コマンド処理
    ├── __init__.py
    ├── hoyolab_controller.py  # HoYoLAB関連コマンド
    ├── resin_controller.py    # 樹脂計算コマンド
    └── team_controller.py     # チーム編成コマンド
```

## 🏗️ 各層の役割

### Model層 (`models/`)

**責務**: データの永続化とデータ構造の定義

- `database.py`: データベースへの直接アクセス（CRUD操作のみ）
  - クッキーの暗号化/復号化
  - ユーザー設定の保存/取得
  - **Discord Cogではない**純粋なPythonクラス

- `user.py`: データクラス定義
  - ユーザー情報のデータ構造
  - 型定義とバリデーション

**特徴**:
- Discordに依存しない
- 再利用可能な純粋なデータアクセス層
- テストが容易

### Service層 (`services/`)

**責務**: ビジネスロジックの実装

- `hoyolab_service.py`: HoYoLAB APIとの通信
  - クッキーの検証
  - キャラクター情報の取得
  - 樹脂状況の取得

- `resin_service.py`: 樹脂計算ロジック
  - 回復時間の計算
  - バリデーション
  - ビジネスルールの適用

- `team_service.py`: チーム編成アルゴリズム
  - キャラクターの役割分類
  - チーム編成ロジック
  - バランス調整

- `notification_service.py`: 通知管理
  - DM送信ロジック
  - 通知タイミングの制御
  - 樹脂チェックループ

**特徴**:
- Discord UIから独立
- 再利用可能なロジック
- 単体テストが可能

### View層 (`views/`)

**責務**: データの表示形式を整形

- `embeds.py`: Discord Embedの生成
  - すべてのEmbed作成を一元管理
  - 一貫したデザイン
  - 色やフォーマットの統一

- `formatters.py`: データフォーマット
  - 日時の整形
  - 文字列の変換
  - 表示用データの加工

**特徴**:
- ビジネスロジックを含まない
- 表示だけに集中
- 容易なデザイン変更

### Controller層 (`controllers/`)

**責務**: ユーザー入力の処理とレスポンス

- `hoyolab_controller.py`: HoYoLAB関連コマンド
  - `/set_cookie` - クッキー設定
  - `/status` - 樹脂状況表示
  - `/characters` - キャラ一覧
  - `/resin_notification` - 通知設定

- `resin_controller.py`: 樹脂計算コマンド
  - `/resin` - 回復時間計算
  - `/resin_reminder` - リマインダー設定

- `team_controller.py`: チーム編成コマンド
  - `/team_generator` - チーム生成

**特徴**:
- Discord Cogとして実装
- Serviceを呼び出してロジックを実行
- Viewを使って結果を表示
- 薄い層（ロジックを持たない）

## 🔄 データフロー

```
ユーザー入力
    ↓
Controller（コマンド受信）
    ↓
Service（ビジネスロジック実行）
    ↓
Model（データ取得/保存）
    ↓
Service（結果を整形）
    ↓
View（Discord Embed生成）
    ↓
Controller（レスポンス送信）
    ↓
ユーザーへ表示
```

## 📝 実装例

### 新機能を追加する場合

例: 武器情報表示機能を追加

1. **Service層**: `services/weapon_service.py`
   ```python
   class WeaponService:
       @staticmethod
       async def get_user_weapons(cookies: dict):
           # HoYoLAB APIから武器情報を取得
           pass
   ```

2. **View層**: `views/embeds.py`に追加
   ```python
   @staticmethod
   def weapon_list_embed(weapons: list) -> discord.Embed:
       # 武器一覧のEmbed生成
       pass
   ```

3. **Controller層**: `controllers/weapon_controller.py`
   ```python
   class WeaponController(commands.Cog):
       @app_commands.command(name='weapons')
       async def weapons(self, interaction):
           # Serviceで取得 → Viewで整形 → 送信
           pass
   ```

## ✅ メリット

1. **保守性**: 各層が独立しているため、変更の影響が限定的
2. **テスト容易性**: Service層を単独でテストできる
3. **再利用性**: ロジックを他のプロジェクトでも使える
4. **可読性**: コードの役割が明確
5. **拡張性**: 新機能の追加が容易

## 🔧 開発ガイドライン

### Controller層
- ✅ ユーザー入力の検証
- ✅ Serviceの呼び出し
- ✅ Viewを使った結果の表示
- ❌ ビジネスロジックを書かない
- ❌ データベースに直接アクセスしない

### Service層
- ✅ ビジネスロジックの実装
- ✅ 外部API呼び出し
- ✅ データの加工・計算
- ❌ Discord UIに依存しない
- ❌ データベースに直接アクセスしない（Modelを使う）

### View層
- ✅ Embedの生成
- ✅ データの整形・フォーマット
- ❌ ビジネスロジックを含まない
- ❌ データベースアクセスしない

### Model層
- ✅ データベースCRUD操作
- ✅ データ構造の定義
- ❌ ビジネスロジックを含まない
- ❌ Discordに依存しない

## 🚀 起動方法

```bash
cd genshin
python bot.py
```

bot.pyが自動的に`controllers/`フォルダから全てのコントローラーをロードします。

## 🔍 トラブルシューティング

### インポートエラーが出る
- `genshin`ディレクトリから実行していることを確認
- Pythonパスが正しく設定されているか確認

### コントローラーが読み込まれない
- `controllers/`フォルダ内のファイル名を確認
- `__init__.py`が存在することを確認
- ファイル名が`.py`で終わっているか確認
