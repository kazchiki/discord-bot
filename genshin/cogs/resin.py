import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
from config.constants import ResinConstants, ColorConstants, MessageConstants
class ResinCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.resin_timers = {}  # ユーザーIDをキーとした樹脂タイマー

    def calculate_resin_time(self, current_resin: int, target_resin: int = ResinConstants.MAX_RESIN):
        """樹脂の回復時間を計算"""
        if current_resin >= target_resin:
            return None
        
        resin_needed = target_resin - current_resin
        minutes_needed = resin_needed * ResinConstants.RESIN_RECOVERY_MINUTES  # 1樹脂 = 8分
        
        return datetime.now() + timedelta(minutes=minutes_needed)

    @app_commands.command(name='resin', description='樹脂の回復時間を計算します')
    @app_commands.describe(
        current='現在の樹脂数',
        target=f'目標樹脂数（デフォルト: {ResinConstants.MAX_RESIN}）'
    )
    async def resin(self, interaction: discord.Interaction, current: int, target: int = ResinConstants.MAX_RESIN):
        if current < 0 or current > ResinConstants.MAX_RESIN:
            await interaction.response.send_message(MessageConstants.RESIN_RANGE_ERROR, ephemeral=True)
            return
        
        if target < current or target > ResinConstants.MAX_RESIN:
            await interaction.response.send_message(MessageConstants.TARGET_RESIN_ERROR, ephemeral=True)
            return
        
        if current == target:
            await interaction.response.send_message(MessageConstants.RESIN_ALREADY_FULL, ephemeral=True)
            return
        
        recovery_time = self.calculate_resin_time(current, target)
        
        # recovery_timeがNoneの場合のチェック（既に目標に達している場合）
        if recovery_time is None:
            await interaction.response.send_message(MessageConstants.RESIN_ALREADY_FULL, ephemeral=True)
            return
        
        resin_needed = target - current
        minutes_needed = resin_needed * ResinConstants.RESIN_RECOVERY_MINUTES
        
        embed = discord.Embed(
            title='樹脂回復計算',
            color=ColorConstants.INFO_COLOR
        )
        
        embed.add_field(name='現在の樹脂', value=f'{current}/{ResinConstants.MAX_RESIN}', inline=True)
        embed.add_field(name='目標樹脂', value=f'{target}/{ResinConstants.MAX_RESIN}', inline=True)
        embed.add_field(name='必要な樹脂', value=f'{resin_needed}', inline=True)
        
        embed.add_field(
            name='回復時間',
            value=f'{minutes_needed // 60}時間 {minutes_needed % 60}分',
            inline=True
        )
        
        embed.add_field(
            name='完了予定時刻',
            value=recovery_time.strftime('%Y/%m/%d %H:%M'),
            inline=True
        )
        
        embed.set_footer(text=MessageConstants.RESIN_RECOVERY_INFO)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='resin_reminder', description='樹脂が満タンになったときにリマインダーを設定します')
    @app_commands.describe(current='現在の樹脂数')
    async def resin_reminder(self, interaction: discord.Interaction, current: int):
        if current < 0 or current > ResinConstants.MAX_RESIN:
            await interaction.response.send_message(MessageConstants.RESIN_RANGE_ERROR, ephemeral=True)
            return
        
        if current == ResinConstants.MAX_RESIN:
            await interaction.response.send_message(MessageConstants.RESIN_MAX_ERROR, ephemeral=True)
            return
        
        user_id = interaction.user.id
        recovery_time = self.calculate_resin_time(current, ResinConstants.MAX_RESIN)
        
        # recovery_timeがNoneの場合（既に満タンの場合）のチェック
        if recovery_time is None:
            await interaction.response.send_message(MessageConstants.RESIN_ALREADY_FULL, ephemeral=True)
            return
        
        # 既存のタイマーをキャンセル
        if user_id in self.resin_timers:
            self.resin_timers[user_id].cancel()
        
        # 新しいタイマーを設定
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
        
        async def reminder_task():
            await asyncio.sleep(wait_seconds)
            try:
                user = await self.bot.fetch_user(user_id)
                embed = discord.Embed(
                    title='🔔 樹脂リマインダー',
                    description=f'樹脂が満タン（{ResinConstants.MAX_RESIN}）になりました！',
                    color=ColorConstants.SUCCESS_COLOR
                )
                await user.send(embed=embed)
            except:
                pass  # DMが送信できない場合は無視
            finally:
                if user_id in self.resin_timers:
                    del self.resin_timers[user_id]
        
        task = asyncio.create_task(reminder_task())
        self.resin_timers[user_id] = task
        
        embed = discord.Embed(
            title=MessageConstants.REMINDER_SET_SUCCESS,
            description=f'樹脂が満タンになる時刻: {recovery_time.strftime("%Y/%m/%d %H:%M")}',
            color=ColorConstants.INFO_COLOR
        )
        embed.add_field(name='現在の樹脂', value=f'{current}/{ResinConstants.MAX_RESIN}', inline=True)
        embed.add_field(name='回復時間', value=f'{(ResinConstants.MAX_RESIN-current)*ResinConstants.RESIN_RECOVERY_MINUTES//60}時間 {(ResinConstants.MAX_RESIN-current)*ResinConstants.RESIN_RECOVERY_MINUTES%60}分', inline=True)
        embed.set_footer(text=MessageConstants.DM_NOTIFICATION_INFO)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ResinCog(bot))