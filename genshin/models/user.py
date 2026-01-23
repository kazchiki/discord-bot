# -*- coding: utf-8 -*-
"""
ユーザーデータモデル
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """ユーザー情報を表すデータクラス"""
    user_id: int
    cookies: Optional[dict] = None
    resin_reminder_enabled: bool = False
    resin_threshold: int = 200
    notification_channel_id: Optional[int] = None
    timezone: str = 'UTC'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class UserSettings:
    """ユーザー設定を表すデータクラス"""
    user_id: int
    resin_reminder_enabled: bool = False
    resin_threshold: int = 200
    notification_channel_id: Optional[int] = None
    timezone: str = 'UTC'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
