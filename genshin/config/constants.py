# -*- coding: utf-8 -*-
"""
原神Discord Bot - 定数管理ファイル
すべての定数をここで一元管理します
"""

# ===== 樹脂関連定数 =====
class ResinConstants:
    MAX_RESIN = 200  # 最大樹脂数
    RESIN_RECOVERY_MINUTES = 8  # 1樹脂回復にかかる分数
    RESIN_RECOVERY_SECONDS = RESIN_RECOVERY_MINUTES * 60  # 秒換算


# ===== 色設定 =====
class ColorConstants:
    # レアリティ色
    FIVE_STAR_COLOR = 0xFFD700  # 金色
    FOUR_STAR_COLOR = 0x9932CC  # 紫色
    THREE_STAR_COLOR = 0x4169E1  # 青色
    
    # 元素色
    ELEMENT_COLORS = {
        '炎': 0xFF6B6B,
        '水': 0x4ECDC4,
        '雷': 0xA8E6CF,
        '氷': 0x88D8C0,
        '風': 0x74C0FC,
        '岩': 0xF39C12,
        '草': 0x2ECC71
    }
    
    # 一般的な色
    SUCCESS_COLOR = 0x00FF00
    ERROR_COLOR = 0xFF0000
    INFO_COLOR = 0x00CED1
    WARNING_COLOR = 0xFFA500


# ===== メッセージ・テキスト関連 =====
class MessageConstants:
    # エラーメッセージ
    RESIN_RANGE_ERROR = "現在の樹脂数は0〜160の間で入力してください。"
    TARGET_RESIN_ERROR = "目標樹脂数は現在の樹脂数より大きく、160以下で入力してください。"
    RESIN_ALREADY_FULL = "既に目標樹脂数に達しています！"
    RESIN_MAX_ERROR = "既に樹脂が満タンです！"
    
    # 成功メッセージ
    REMINDER_SET_SUCCESS = "リマインダー設定完了"
    
    # 情報メッセージ
    RESIN_RECOVERY_INFO = "樹脂は8分で1回復します"
    DM_NOTIFICATION_INFO = "DMでお知らせします"

# ===== API・外部サービス関連 =====
class APIConstants:
    # HoYoLAB関連
    HOYOLAB_BASE_URL = "https://bbs-api-os.hoyolab.com"
    GENSHIN_GAME_RECORD_URL = f"{HOYOLAB_BASE_URL}/game_record/genshin/api"
    
    # リクエスト制限
    REQUEST_TIMEOUT = 30  # 秒
    MAX_RETRIES = 3
    
    # ヘッダー
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

# ===== データベース関連 =====
class DatabaseConstants:
    # テーブル名
    USER_DATA_TABLE = "user_data"
    GACHA_HISTORY_TABLE = "gacha_history"
    
    # 暗号化関連
    ENCRYPTION_KEY_LENGTH = 32
    
    # データ保持期間（日数）
    DATA_RETENTION_DAYS = 30

# ===== 制限・制約関連 =====
class LimitConstants:
    # コマンド使用制限
    COMMAND_COOLDOWN = 5  # 秒
    GACHA_MAX_PULLS = 10  # 一度に引けるガチャの最大数
    
    # 文字列長制限
    MAX_USERNAME_LENGTH = 32
    MAX_MESSAGE_LENGTH = 2000
    
    # ファイルサイズ制限
    MAX_IMAGE_SIZE_MB = 8