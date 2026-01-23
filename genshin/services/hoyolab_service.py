# -*- coding: utf-8 -*-
"""
HoYoLAB API連携サービス
APIとのやり取りやデータ取得を担当
"""

import genshin
from typing import Optional, List, Tuple
from config.constants import CharacterNameMapping, ElementConstants


class HoyolabService:
    """HoYoLAB API連携サービスクラス"""
    
    @staticmethod
    async def validate_cookies(cookies: dict) -> Tuple[bool, Optional[List], Optional[str]]:
        """
        クッキーの有効性を検証
        
        Args:
            cookies: クッキーの辞書
            
        Returns:
            Tuple[bool, List, str]: (成功フラグ, アカウントリスト, エラーメッセージ)
        """
        try:
            client = genshin.Client(cookies)
            accounts = await client.get_game_accounts()
            
            if not accounts:
                return False, None, "アカウントが見つかりませんでした"
            
            return True, accounts, None
        except genshin.errors.InvalidCookies:
            return False, None, "無効なクッキーです"
        except Exception as e:
            return False, None, str(e)
    
    @staticmethod
    def parse_cookie_string(cookie_str: str) -> dict:
        """
        クッキー文字列を辞書形式に変換
        
        Args:
            cookie_str: クッキー文字列
            
        Returns:
            dict: クッキーの辞書
        """
        cookie_dict = {}
        for item in cookie_str.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookie_dict[key] = value
        return cookie_dict
    
    @staticmethod
    def validate_cookie_format(cookies: dict) -> bool:
        """
        クッキーの形式を検証
        
        Args:
            cookies: クッキーの辞書
            
        Returns:
            bool: 有効な形式ならTrue
        """
        return 'ltuid_v2' in cookies and 'ltoken_v2' in cookies
    
    @staticmethod
    async def get_genshin_notes(cookies: dict):
        """
        原神のリアルタイムノート（樹脂状況など）を取得
        
        Args:
            cookies: クッキーの辞書
            
        Returns:
            genshin.models.Notes: ノート情報
            
        Raises:
            genshin.errors.InvalidCookies: クッキーが無効
            Exception: その他のエラー
        """
        client = genshin.Client(cookies)
        return await client.get_genshin_notes()
    
    @staticmethod
    async def get_genshin_characters(cookies: dict, uid: Optional[int] = None) -> List:
        """
        所持キャラクター一覧を取得
        
        Args:
            cookies: クッキーの辞書
            uid: ユーザーのUID（Noneの場合は自動取得）
            
        Returns:
            List: キャラクターのリスト
        """
        client = genshin.Client(cookies)
        
        # UIDが指定されていない場合は自動取得
        if uid is None:
            accounts = await client.get_game_accounts()
            genshin_accounts = [acc for acc in accounts if acc.game == genshin.Game.GENSHIN]
            
            if not genshin_accounts:
                return []
            
            uid = genshin_accounts[0].uid
        
        characters = await client.get_genshin_characters(uid)
        return characters
    
    @staticmethod
    async def get_genshin_accounts(cookies: dict) -> List:
        """
        原神アカウント情報を取得
        
        Args:
            cookies: クッキーの辞書
            
        Returns:
            List: 原神アカウントのリスト
        """
        client = genshin.Client(cookies)
        accounts = await client.get_game_accounts()
        return [acc for acc in accounts if acc.game == genshin.Game.GENSHIN]
    
    @staticmethod
    def get_japanese_name(english_name: str) -> str:
        """
        英語キャラ名を日本語名に変換
        
        Args:
            english_name: 英語名
            
        Returns:
            str: 日本語名
        """
        return CharacterNameMapping.NAMES.get(english_name, english_name)
    
    @staticmethod
    def classify_characters_by_element(characters: List) -> dict:
        """
        キャラクターを元素別に分類
        
        Args:
            characters: キャラクターのリスト
            
        Returns:
            dict: 元素をキーとしたキャラクターの辞書
        """
        element_order = ElementConstants.ELEMENT_ORDER
        chars_by_element = {}
        
        for element in element_order:
            chars_by_element[element] = [c for c in characters if c.element == element]
        
        return chars_by_element
