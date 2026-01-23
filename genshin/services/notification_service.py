# -*- coding: utf-8 -*-
"""
通知サービス
Discord通知ロジックを管理
"""

import discord
from typing import Optional
from models.database import Database
from views.embeds import EmbedBuilder


class NotificationService:
    """通知サービスクラス"""
    
    def __init__(self, bot: discord.Client, database: Database):
        """
        通知サービスを初期化
        
        Args:
            bot: Discord Botインスタンス
            database: データベースインスタンス
        """
        self.bot = bot
        self.database = database
    
    async def send_resin_reminder(self, user_id: int, current_resin: int, max_resin: int, threshold: int) -> bool:
        """
        樹脂リマインダーを送信
        
        Args:
            user_id: ユーザーID
            current_resin: 現在の樹脂数
            max_resin: 最大樹脂数
            threshold: 通知閾値
            
        Returns:
            bool: 送信成功したらTrue
        """
        try:
            user = await self.bot.fetch_user(user_id)
            
            embed = EmbedBuilder.resin_reminder_embed(
                threshold=threshold,
                current_resin=current_resin,
                max_resin=max_resin
            )
            
            # 満タンでない場合は追加情報
            if current_resin < max_resin:
                from datetime import datetime, timedelta
                from config.constants import ResinConstants
                
                remaining = max_resin - current_resin
                minutes = remaining * ResinConstants.RESIN_RECOVERY_MINUTES
                recovery_time = datetime.now() + timedelta(minutes=minutes)
                
                embed.add_field(
                    name='満タンまで',
                    value=recovery_time.strftime('%H:%M'),
                    inline=True
                )
            
            embed.set_footer(text='通知を停止するには /resin_notification off を実行してください')
            
            await user.send(embed=embed)
            return True
        except discord.Forbidden:
            print(f"通知送信失敗 (User {user_id}): DMが無効です")
            return False
        except Exception as e:
            print(f"通知送信エラー (User {user_id}): {e}")
            return False
    
    async def send_dm(self, user_id: int, embed: discord.Embed) -> bool:
        """
        ユーザーにDMを送信
        
        Args:
            user_id: ユーザーID
            embed: 送信するEmbed
            
        Returns:
            bool: 送信成功したらTrue
        """
        try:
            user = await self.bot.fetch_user(user_id)
            await user.send(embed=embed)
            return True
        except discord.Forbidden:
            print(f"DM送信失敗 (User {user_id}): DMが無効です")
            return False
        except Exception as e:
            print(f"DM送信エラー (User {user_id}): {e}")
            return False
    
    async def check_all_resin_reminders(self, hoyolab_service) -> None:
        """
        すべてのユーザーの樹脂をチェックして必要に応じて通知
        
        Args:
            hoyolab_service: HoyolabServiceインスタンス
        """
        users = self.database.get_all_users_with_resin_reminder()
        
        for user_id, enabled, threshold in users:
            if not enabled:
                continue
            
            # ユーザーのクッキーを取得
            user_cookies = self.database.get_user_cookies(user_id)
            if not user_cookies:
                continue
            
            try:
                # 樹脂情報を取得
                notes = await hoyolab_service.get_genshin_notes(user_cookies)
                
                # 閾値チェック
                resin_threshold = threshold if threshold else notes.max_resin
                
                if notes.current_resin >= resin_threshold:
                    await self.send_resin_reminder(
                        user_id=user_id,
                        current_resin=notes.current_resin,
                        max_resin=notes.max_resin,
                        threshold=resin_threshold
                    )
            
            except Exception as e:
                print(f"樹脂チェックエラー (User {user_id}): {e}")
                continue
