# -*- coding: utf-8 -*-
"""
樹脂計算関連のコマンドコントローラー
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime

from models.database import Database
from services.resin_service import ResinService
from views.embeds import EmbedBuilder
from config.constants import ResinConstants, MessageConstants


class ResinController(commands.Cog):
    """樹脂計算関連のコマンドを処理するController"""
    
    def __init__(self, bot: commands.Bot, database: Database):
        self.bot = bot
        self.database = database
        self.resin_service = ResinService()
        self.resin_timers = {}  # ユーザーIDをキーとした樹脂タイマー
    
    @app_commands.command(name='resin', description='樹脂の回復時間を計算します')
    @app_commands.describe(
        current='現在の樹脂数',
        target=f'目標樹脂数（デフォルト: {ResinConstants.MAX_RESIN}）'
    )
    async def resin(self, interaction: discord.Interaction, current: int, target: int = ResinConstants.MAX_RESIN):
        """樹脂回復計算コマンド"""
        # バリデーション
        is_valid, error = self.resin_service.validate_resin_range(current, target)
        if not is_valid:
            await interaction.response.send_message(f'❌ {error}', ephemeral=True)
            return
        
        if current == target:
            await interaction.response.send_message(MessageConstants.RESIN_ALREADY_FULL, ephemeral=True)
            return
        
        # 回復時間を計算
        recovery_time = self.resin_service.calculate_recovery_time(current, target)
        
        if recovery_time is None:
            await interaction.response.send_message(MessageConstants.RESIN_ALREADY_FULL, ephemeral=True)
            return
        
        # Embedを生成して送信
        embed = EmbedBuilder.resin_calculation_embed(current, target, recovery_time)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name='resin_reminder', description='樹脂が満タンになったときにリマインダーを設定します')
    @app_commands.describe(current='現在の樹脂数')
    async def resin_reminder(self, interaction: discord.Interaction, current: int):
        """樹脂リマインダー設定コマンド"""
        # バリデーション
        is_valid, error = self.resin_service.validate_resin_value(current)
        if not is_valid:
            await interaction.response.send_message(f'❌ {error}', ephemeral=True)
            return
        
        if self.resin_service.is_resin_full(current):
            await interaction.response.send_message(MessageConstants.RESIN_MAX_ERROR, ephemeral=True)
            return
        
        user_id = interaction.user.id
        recovery_time = self.resin_service.calculate_recovery_time(current, ResinConstants.MAX_RESIN)
        
        if recovery_time is None:
            await interaction.response.send_message(MessageConstants.RESIN_ALREADY_FULL, ephemeral=True)
            return
        
        # 既存のタイマーをキャンセル
        if user_id in self.resin_timers:
            self.resin_timers[user_id].cancel()
        
        # 待機時間を計算
        wait_seconds = (recovery_time - datetime.now()).total_seconds()
        
        # 負の値の場合（過去の時刻）は即座に通知
        if wait_seconds <= 0:
            await interaction.response.send_message(
                '⚠️ 指定された樹脂数は既に回復済みです。',
                ephemeral=True
            )
            return
        
        # 待機時間が長すぎる場合（24時間以上）は制限
        max_wait_seconds = 24 * 60 * 60  # 24時間
        if wait_seconds > max_wait_seconds:
            await interaction.response.send_message(
                '⚠️ 回復時間が24時間を超えています。より短い時間で設定してください。',
                ephemeral=True
            )
            return
        
        # リマインダータスクを作成
        async def reminder_task():
            await asyncio.sleep(wait_seconds)
            try:
                user = await self.bot.fetch_user(user_id)
                embed = EmbedBuilder.resin_reminder_embed(
                    threshold=ResinConstants.MAX_RESIN,
                    current_resin=ResinConstants.MAX_RESIN,
                    max_resin=ResinConstants.MAX_RESIN
                )
                await user.send(embed=embed)
            except:
                pass  # DMが送信できない場合は無視
            finally:
                if user_id in self.resin_timers:
                    del self.resin_timers[user_id]
        
        task = asyncio.create_task(reminder_task())
        self.resin_timers[user_id] = task
        
        # 設定完了メッセージ
        from views.formatters import TextFormatter
        
        minutes = self.resin_service.calculate_recovery_duration(current, ResinConstants.MAX_RESIN)
        duration_str = TextFormatter.format_duration(minutes)
        
        embed = discord.Embed(
            title=MessageConstants.REMINDER_SET_SUCCESS,
            description=f'樹脂が満タンになる時刻: {recovery_time.strftime("%Y/%m/%d %H:%M")}',
            color=0x00CED1
        )
        embed.add_field(
            name='現在の樹脂',
            value=f'{current}/{ResinConstants.MAX_RESIN}',
            inline=True
        )
        embed.add_field(
            name='回復時間',
            value=duration_str,
            inline=True
        )
        embed.set_footer(text=MessageConstants.DM_NOTIFICATION_INFO)
        
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    """Cogをセットアップ"""
    database = Database()
    await bot.add_cog(ResinController(bot, database))
