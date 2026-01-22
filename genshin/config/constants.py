# -*- coding: utf-8 -*-
"""
原神Discord Bot - 定数管理ファイル
すべての定数をここで一元管理します
"""

# ===== 元素関連定数 =====
class ElementConstants:
    """元素関連の定数"""
    # 元素名マッピング（英語→日本語）
    ELEMENT_NAMES = {
        'Pyro': '炎',
        'Hydro': '水',
        'Electro': '雷',
        'Cryo': '氷',
        'Anemo': '風',
        'Geo': '岩',
        'Dendro': '草'
    }
    
    # 元素順序（表示用）
    ELEMENT_ORDER = ['Pyro', 'Hydro', 'Electro', 'Cryo', 'Anemo', 'Geo', 'Dendro']


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
    RESIN_RANGE_ERROR = "現在の樹脂数は0〜200の間で入力してください。"
    TARGET_RESIN_ERROR = "目標樹脂数は現在の樹脂数より大きく、200以下で入力してください。"
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
    
    # 暗号化関連
    ENCRYPTION_KEY_LENGTH = 32
    
    # データ保持期間（日数）
    DATA_RETENTION_DAYS = 30

# ===== キャラクター名マッピング =====
class CharacterNameMapping:
    """英語名→日本語名の変換マッピング"""
    NAMES = {
        # 星5キャラクター
        # モンド
        'Venti': 'ウェンティ',
        'Diluc': 'ディルック',
        'Jean': 'ジン',
        'Mona': 'モナ',
        'Klee': 'クレー',
        'Albedo': 'アルベド',
        'Eula': 'エウルア',
        'Durin': 'ドゥリン',
        'Aloy': 'アーロイ',

        # 璃月
        'Zhongli': '鍾離',
        'Qiqi': '七七',
        'Keqing': '刻晴',
        'Ganyu': '甘雨',
        'Hu Tao': '胡桃',
        'Xiao': '魈',
        'Shenhe': '申鶴',
        'Yelan': '夜蘭',
        'Baizhu': '白朮',
        'Xianyun': '閑雲',

        # 稲妻
        'Raiden Shogun': '雷電将軍',
        'Kaedehara Kazuha': '楓原万葉',
        'Yoimiya': '宵宮',
        'Kamisato Ayaka': '神里綾華',
        'Kamisato Ayato': '神里綾人',
        'Sangonomiya Kokomi': '珊瑚宮心海',
        'Yae Miko': '八重神子',
        'Arataki Itto': '荒瀧一斗',
        'Chiori': '千織',
        'Yumemizuki Mizuki': '夢見月瑞希',

        # スメール
        'Nahida': 'ナヒーダ',
        'Tighnari': 'ティナリ',
        'Dehya': 'ディシア',
        'Nilou': 'ニィロウ',
        'Alhaitham': 'アルハイゼン',
        'Cyno': 'セノ',
        'Wanderer': '放浪者',

        # フォンテーヌ
        'Furina': 'フリーナ',
        'Lyney': 'リネ',
        'Neuvillette': 'ヌヴィレット',
        'Wriothesley': 'リオセスリ',
        'Navia': 'ナヴィア',
        'Clorinde': 'クロリンデ',
        'Sigewinne': 'シグウィン',
        'Emilie': 'エミリエ',
        'Escofier': 'エスコフィエ',

        # ナタ
        'Mavuika': 'マーヴィカ',
        'Mualani': 'ムアラニ',
        'Kinich': 'キイニチ',
        'Xilonen': 'シロネン',
        'Citlali': 'シトラリ',
        'Chasca': 'チャスカ',
        'Varesa': 'ヴァレサ',

        # ナド・クライ
        'Columbina': 'コロンビーナ',
        'Ineffa': 'イネファ',
        'Neferiti': 'ネフェル',
        'Flins': 'フリンズ',
        'Lauma': 'ラウマ',

        # スネージナヤ
        'Tartaglia': 'タルタリヤ',
        'Arlecchino': 'アルレッキーノ',

        # 分類なし
        'Skirk': 'スカーク',
        'Manekina': 'マネキン(女)',
        'Manekin': 'マネキン(男)',

        # 星4キャラクター
        # モンド
        'Amber': 'アンバー',
        'Bennett': 'ベネット',
        'Lisa': 'リサ',
        'Kaeya': 'ガイア',
        'Razor': 'レザー',
        'Fischl': 'フィッシュル',
        'Rosaria': 'ロサリア',
        'Diona': 'ディオナ',
        'Sucrose': 'スクロース',
        'Barbara': 'バーバラ',
        'Mika': 'ミカ',
        'Dahlia': 'ダリア',

        # 璃月
        'Xingqiu': '行秋',
        'Xiangling': '香菱',
        'Chongyun': '重雲',
        'Yanfei': '煙緋(えんひ)',
        'Ningguang': '凝光(ぎょうこう)',
        'Xinyan': '辛炎(しんえん)',
        'Beidou': '北斗',
        'Yun Jin': '雲菫',
        'Yaoyao': 'ヨーヨ',
        'Gaming': '嘉明(がみん)',
        'Lan Yan': '藍硯(らんやん)',

        # 稲妻
        'Thoma': 'トーマ',
        'Kujou Sara': '九条裟羅',
        'Sayu': '早柚',
        'Kuki Shinobu': '久岐忍',
        'Gorou': 'ゴロー',
        'Kirara': '綺良々(きらら)',
        'Shikanoin Heizou': '鹿野院平蔵',

        # スメール
        'Collei': 'コレイ',
        'Faruzan': 'ファルザン',
        'Dori': 'ドリー',
        'Layla': 'レイラ',
        'Candace': 'キャンディス',
        'Kaveh': 'カーヴェ',
        'Sethos': 'セトス',

        # フォンテーヌ
        'Lynette': 'リネット',
        'Freminet': 'フレミネ',
        'Charlotte': 'シャルロット',
        'Chevreuse': 'シュヴルーズ',

        # ナタ
        'Kachina': 'カチーナ',
        'Ororon': 'オロルン',
        'Iansan': 'イアンサ',
        'Ifa': 'イファ',

        # ナド・クライ
        'Aino': 'アイノ',
        'Jahoda': 'ヤフォダ',

        # 主人公
        'Traveler': '旅人',
        'Aether': '空',
        'Lumine': '蛍',
    }

# ===== 制限・制約関連 =====
class LimitConstants:
    # コマンド使用制限
    COMMAND_COOLDOWN = 5  # 秒
    
    # 文字列長制限
    MAX_USERNAME_LENGTH = 32
    MAX_MESSAGE_LENGTH = 2000
    
    # ファイルサイズ制限
    MAX_IMAGE_SIZE_MB = 8