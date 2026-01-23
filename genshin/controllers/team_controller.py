# -*- coding: utf-8 -*-
"""
チーム編成関連のコマンドコントローラー
"""

import discord
from discord.ext import commands
from discord import app_commands
import genshin

from models.database import Database
from services.hoyolab_service import HoyolabService
from services.team_service import TeamService
from views.embeds import EmbedBuilder


class TeamController(commands.Cog):
    """チーム編成関連のコマンドを処理するController"""
    
    def __init__(self, bot: commands.Bot, database: Database):
        self.bot = bot
        self.database = database
        self.hoyolab_service = HoyolabService()
        self.team_service = TeamService()
    
    @app_commands.command(name='team_generator', description='所持キャラからランダムなチーム編成を提案します')
    async def team_generator(self, interaction: discord.Interaction):
        """チーム編成生成コマンド"""
        user_cookies = self.database.get_user_cookies(interaction.user.id)
        if not user_cookies:
            await interaction.response.send_message(
                '❌ HoYoLABのクッキーが設定されていません。\n'
                'まず `/set_cookie` コマンドでクッキーを設定してください。',
                ephemeral=True
            )
            return
        
        try:
            await interaction.response.defer()
            
            # HoYoLAB APIから所持キャラを取得
            characters = await self.hoyolab_service.get_genshin_characters(user_cookies)
            
            if not characters:
                await interaction.followup.send('❌ キャラクターが見つかりませんでした。')
                return
            
            # レベル1以上のキャラのみ（所持している）
            owned_chars = self.team_service.filter_owned_characters(characters, min_level=1)
            
            # チーム編成の条件を検証
            is_valid, error = self.team_service.validate_team_requirements(owned_chars, min_chars=4)
            if not is_valid:
                await interaction.followup.send(f'❌ {error}')
                return
            
            # チームを編成
            team = self.team_service.create_team(owned_chars)
            
            if not team:
                await interaction.followup.send('❌ チーム編成に失敗しました。')
                return
            
            # Embedを生成して送信
            embed = EmbedBuilder.team_generator_embed(team=team, total_chars=len(owned_chars))
            await interaction.followup.send(embed=embed)
        
        except genshin.errors.InvalidCookies:
            await interaction.followup.send(
                '❌ クッキーが無効です。新しいクッキーを設定してください。',
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f'❌ エラーが発生しました: {str(e)}',
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    """Cogをセットアップ"""
    database = Database()
    await bot.add_cog(TeamController(bot, database))
