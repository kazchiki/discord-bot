# -*- coding: utf-8 -*-
"""
HoYoLAB関連のコマンドコントローラー
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import genshin

from models.database import Database
from services.hoyolab_service import HoyolabService
from services.notification_service import NotificationService
from views.embeds import EmbedBuilder


class HoyolabController(commands.Cog):
    """HoYoLAB関連のコマンドを処理するController"""
    
    def __init__(self, bot: commands.Bot, database: Database):
        self.bot = bot
        self.database = database
        self.hoyolab_service = HoyolabService()
        self.notification_service = NotificationService(bot, database)
        self.resin_check_loop.start()  # 樹脂チェックタスク開始
    
    def cog_unload(self):
        """Cog終了時にタスクを停止"""
        self.resin_check_loop.cancel()
    
    @tasks.loop(minutes=30)  # 30分ごとにチェック
    async def resin_check_loop(self):
        """定期的に樹脂をチェックして通知"""
        try:
            await self.notification_service.check_all_resin_reminders(self.hoyolab_service)
        except Exception as e:
            print(f"樹脂チェックループエラー: {e}")
    
    @resin_check_loop.before_loop
    async def before_resin_check(self):
        """Bot起動完了を待つ"""
        await self.bot.wait_until_ready()
    
    @app_commands.command(name='set_cookie', description='HoYoLABのクッキーを設定します（DMで送信してください）')
    @app_commands.describe(cookie='HoYoLABのクッキー（ltuid_v2とltoken_v2）')
    async def set_cookie(self, interaction: discord.Interaction, cookie: str):
        """クッキー設定コマンド"""
        # DMでのみ実行可能
        if interaction.guild is not None:
            await interaction.response.send_message(
                '⚠️ セキュリティのため、このコマンドはDMでのみ使用できます。\n'
                'Botに直接DMを送って `/set_cookie` を実行してください。',
                ephemeral=True
            )
            return
        
        try:
            # クッキーを辞書形式に変換
            cookie_dict = self.hoyolab_service.parse_cookie_string(cookie)
            
            # クッキーの形式をチェック
            if not self.hoyolab_service.validate_cookie_format(cookie_dict):
                await interaction.response.send_message(
                    '❌ 無効なクッキー形式です。\n'
                    'HoYoLABのクッキーには `ltuid_v2` と `ltoken_v2` が必要です。',
                    ephemeral=True
                )
                return
            
            # テスト接続
            success, accounts, error = await self.hoyolab_service.validate_cookies(cookie_dict)
            
            if not success:
                await interaction.response.send_message(
                    f'❌ {error}\nクッキーを確認してください。',
                    ephemeral=True
                )
                return
            
            # データベースにクッキーを保存
            if self.database.save_user_cookies(interaction.user.id, cookie_dict):
                # 原神アカウント情報を取得
                genshin_accounts = [acc for acc in accounts if acc.game == genshin.Game.GENSHIN]
                embed = EmbedBuilder.cookie_set_embed(genshin_accounts)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(
                    '❌ クッキーの保存に失敗しました。',
                    ephemeral=True
                )
        
        except Exception as e:
            await interaction.response.send_message(
                f'❌ エラーが発生しました: {str(e)}',
                ephemeral=True
            )
    
    @app_commands.command(name='status', description='現在のゲーム内状況を取得します')
    async def status(self, interaction: discord.Interaction):
        """ゲーム内状況表示コマンド"""
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
            
            # 樹脂情報を取得
            notes = await self.hoyolab_service.get_genshin_notes(user_cookies)
            
            # Embedを生成して送信
            embed = EmbedBuilder.resin_status_embed(notes)
            embed.set_footer(text=f'HoYoLAB APIより取得 | UID: {interaction.user.id}')
            
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
    
    @app_commands.command(name='characters', description='所持キャラクター一覧を表示します')
    async def characters(self, interaction: discord.Interaction):
        """キャラクター一覧表示コマンド"""
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
            
            # キャラクター一覧を取得
            characters = await self.hoyolab_service.get_genshin_characters(user_cookies)
            
            if not characters:
                await interaction.followup.send('キャラクターが見つかりませんでした。')
                return
            
            # 元素別に分類
            from config.constants import ElementConstants
            chars_by_element = self.hoyolab_service.classify_characters_by_element(characters)
            
            # Embedを生成して送信
            embed = EmbedBuilder.characters_list_embed(
                characters=characters,
                chars_by_element=chars_by_element,
                element_order=ElementConstants.ELEMENT_ORDER
            )
            embed.set_footer(text=f'HoYoLAB APIより取得 | UID: {interaction.user.id}')
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(
                f'❌ エラーが発生しました: {str(e)}',
                ephemeral=True
            )
    
    @app_commands.command(name='resin_notification', description='樹脂の自動通知を設定します')
    @app_commands.describe(
        enabled='通知を有効にするか',
        threshold='通知する樹脂の閾値（デフォルト: 満タン）'
    )
    @app_commands.choices(enabled=[
        app_commands.Choice(name='有効', value='on'),
        app_commands.Choice(name='無効', value='off'),
    ])
    async def resin_notification(self, interaction: discord.Interaction, enabled: str, threshold: int = None):
        """樹脂通知設定コマンド"""
        # クッキーが設定されているか確認
        user_cookies = self.database.get_user_cookies(interaction.user.id)
        if not user_cookies:
            await interaction.response.send_message(
                '❌ HoYoLABのクッキーが設定されていません。\n'
                'まず `/set_cookie` コマンドでクッキーを設定してください。',
                ephemeral=True
            )
            return
        
        is_enabled = (enabled == 'on')
        
        # 閾値のバリデーション
        if threshold is not None and (threshold < 1 or threshold > 200):
            await interaction.response.send_message(
                '❌ 閾値は1〜200の範囲で設定してください。',
                ephemeral=True
            )
            return
        
        # 設定を保存
        settings = {
            'resin_reminder_enabled': is_enabled,
            'resin_threshold': threshold if threshold else 200
        }
        
        if self.database.save_user_settings(interaction.user.id, **settings):
            embed = EmbedBuilder.resin_notification_settings_embed(
                enabled=is_enabled,
                threshold=threshold if threshold else 200
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                '❌ 設定の保存に失敗しました。',
                ephemeral=True
            )
    
    @app_commands.command(name='delete_cookie', description='保存されたクッキーを削除します')
    async def delete_cookie(self, interaction: discord.Interaction):
        """クッキー削除コマンド"""
        if self.database.delete_user_cookies(interaction.user.id):
            embed = EmbedBuilder.success_embed(
                title='クッキー削除完了',
                description='保存されていたHoYoLABクッキーを削除しました。'
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                '❌ クッキーの削除に失敗しました。',
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    """Cogをセットアップ"""
    # bot.databaseはbot.pyで初期化済み
    await bot.add_cog(HoyolabController(bot, bot.database))
