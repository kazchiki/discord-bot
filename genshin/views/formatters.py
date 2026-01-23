# -*- coding: utf-8 -*-
"""
テキストフォーマット処理
データを見やすく整形する
"""

from datetime import datetime, timedelta
from config.constants import CharacterNameMapping, ElementConstants


class TextFormatter:
    """テキストフォーマットクラス"""
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = '%Y/%m/%d %H:%M') -> str:
        """日時をフォーマット"""
        return dt.strftime(format_str)
    
    @staticmethod
    def format_duration(minutes: int) -> str:
        """分数を「○時間○分」形式に変換"""
        hours = minutes // 60
        mins = minutes % 60
        
        if hours > 0 and mins > 0:
            return f'{hours}時間 {mins}分'
        elif hours > 0:
            return f'{hours}時間'
        else:
            return f'{mins}分'
    
    @staticmethod
    def format_character_name(english_name: str) -> str:
        """英語名を日本語名に変換"""
        return CharacterNameMapping.NAMES.get(english_name, english_name)
    
    @staticmethod
    def format_element_name(element: str) -> str:
        """元素名を日本語に変換"""
        return ElementConstants.ELEMENT_NAMES.get(element, element)
    
    @staticmethod
    def format_progress(current: int, max_value: int) -> str:
        """進捗を「○/○」形式で表示"""
        return f'{current}/{max_value}'
    
    @staticmethod
    def format_percentage(current: int, max_value: int) -> str:
        """進捗をパーセンテージで表示"""
        if max_value == 0:
            return '0%'
        percentage = (current / max_value) * 100
        return f'{percentage:.1f}%'
    
    @staticmethod
    def format_cookie_string(cookie: str) -> dict:
        """クッキー文字列を辞書形式に変換"""
        cookie_dict = {}
        for item in cookie.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookie_dict[key] = value
        return cookie_dict
    
    @staticmethod
    def validate_cookie(cookie_dict: dict) -> bool:
        """クッキーの形式を検証"""
        return 'ltuid_v2' in cookie_dict and 'ltoken_v2' in cookie_dict
