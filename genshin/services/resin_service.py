# -*- coding: utf-8 -*-
"""
樹脂計算サービス
樹脂の回復時間計算などのビジネスロジック
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from config.constants import ResinConstants


class ResinService:
    """樹脂計算サービスクラス"""
    
    @staticmethod
    def calculate_recovery_time(current_resin: int, target_resin: int = ResinConstants.MAX_RESIN) -> Optional[datetime]:
        """
        樹脂の回復時間を計算
        
        Args:
            current_resin: 現在の樹脂数
            target_resin: 目標樹脂数
            
        Returns:
            datetime: 回復完了時刻（既に達している場合はNone）
        """
        if current_resin >= target_resin:
            return None
        
        resin_needed = target_resin - current_resin
        minutes_needed = resin_needed * ResinConstants.RESIN_RECOVERY_MINUTES
        
        return datetime.now() + timedelta(minutes=minutes_needed)
    
    @staticmethod
    def calculate_recovery_duration(current_resin: int, target_resin: int) -> int:
        """
        樹脂回復にかかる時間（分数）を計算
        
        Args:
            current_resin: 現在の樹脂数
            target_resin: 目標樹脂数
            
        Returns:
            int: 回復にかかる分数
        """
        if current_resin >= target_resin:
            return 0
        
        resin_needed = target_resin - current_resin
        return resin_needed * ResinConstants.RESIN_RECOVERY_MINUTES
    
    @staticmethod
    def validate_resin_value(resin: int) -> Tuple[bool, Optional[str]]:
        """
        樹脂の値を検証
        
        Args:
            resin: 樹脂の値
            
        Returns:
            Tuple[bool, str]: (有効フラグ, エラーメッセージ)
        """
        if resin < 0:
            return False, "樹脂数は0以上である必要があります"
        if resin > ResinConstants.MAX_RESIN:
            return False, f"樹脂数は{ResinConstants.MAX_RESIN}以下である必要があります"
        return True, None
    
    @staticmethod
    def validate_resin_range(current: int, target: int) -> Tuple[bool, Optional[str]]:
        """
        樹脂の範囲を検証
        
        Args:
            current: 現在の樹脂
            target: 目標樹脂
            
        Returns:
            Tuple[bool, str]: (有効フラグ, エラーメッセージ)
        """
        # 現在の樹脂を検証
        is_valid, error = ResinService.validate_resin_value(current)
        if not is_valid:
            return False, error
        
        # 目標樹脂を検証
        is_valid, error = ResinService.validate_resin_value(target)
        if not is_valid:
            return False, error
        
        # 範囲を検証
        if target <= current:
            return False, "目標樹脂数は現在の樹脂数より大きい値を指定してください"
        
        return True, None
    
    @staticmethod
    def is_resin_full(current_resin: int) -> bool:
        """
        樹脂が満タンかどうかを判定
        
        Args:
            current_resin: 現在の樹脂数
            
        Returns:
            bool: 満タンならTrue
        """
        return current_resin >= ResinConstants.MAX_RESIN
    
    @staticmethod
    def get_resin_percentage(current_resin: int) -> float:
        """
        樹脂の充填率をパーセンテージで取得
        
        Args:
            current_resin: 現在の樹脂数
            
        Returns:
            float: パーセンテージ（0-100）
        """
        return (current_resin / ResinConstants.MAX_RESIN) * 100
