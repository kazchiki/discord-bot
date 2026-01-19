import discord
from discord.ext import commands
from discord import app_commands
import genshin
import asyncio
from datetime import datetime, timedelta

class HoyolabCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_database_cog(self):
        """データベースCogを取得"""
        return self.bot.get_cog('DatabaseCog')

    @app_commands.command(name='set_cookie', description='HoYoLABのクッキーを設定します（DMで送信してください）')
    @app_commands.describe(cookie='HoYoLABのクッキー（ltuid_v2とltoken_v2）')
    async def set_cookie(self, interaction: discord.Interaction, cookie: str):
        # DMでのみ実行可能
        if interaction.guild is not None:
            await interaction.response.send_message(
                '⚠️ セキュリティのため、このコマンドはDMでのみ使用できます。\n'
                'Botに直接DMを送って `/set_cookie` を実行してください。',
                ephemeral=True
            )
            return

        try:
            # クッキーの形式をチェック
            if 'ltuid_v2' not in cookie or 'ltoken_v2' not in cookie:
                await interaction.response.send_message(
                    '❌ 無効なクッキー形式です。\n'
                    'HoYoLABのクッキーには `ltuid_v2` と `ltoken_v2` が必要です。',
                    ephemeral=True
                )
                return

            # クッキーを辞書形式に変換
            cookie_dict = {}
            for item in cookie.split(';'):
                if '=' in item:
                    key, value = item.strip().split('=', 1)
                    cookie_dict[key] = value

            # テスト接続
            client = genshin.Client(cookie_dict)
            accounts = await client.get_game_accounts()
            
            if not accounts:
                await interaction.response.send_message(
                    '❌ アカウントが見つかりませんでした。クッキーを確認してください。',
                    ephemeral=True
                )
                return

            # データベースにクッキーを保存
            db_cog = self.get_database_cog()
            if db_cog and db_cog.save_user_cookies(interaction.user.id, cookie_dict):
                embed = discord.Embed(
                    title='✅ クッキー設定完了',
                    description='HoYoLABのクッキーが正常に設定され、暗号化して保存されました！',
                    color=0x00FF00
                )
                
                # アカウント情報を表示
                genshin_accounts = [acc for acc in accounts if acc.game == genshin.Game.GENSHIN]
                if genshin_accounts:
                    account_info = []
                    for acc in genshin_accounts[:3]:  # 最大3つまで表示
                        account_info.append(f'UID: {acc.uid} (AR{acc.level})')
                    
                    embed.add_field(
                        name='原神アカウント',
                        value='\n'.join(account_info),
                        inline=False
                    )

                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(
                    '❌ クッキーの保存に失敗しました。',
                    ephemeral=True
                )

        except Exception as e:
            await interaction.response.send_message(
                f'❌ エラーが発生しました: {str(e)}\n'
                'クッキーが正しいか確認してください。',
                ephemeral=True
            )

    @app_commands.command(name='resin_status', description='現在の樹脂状況を取得します')
    async def resin_status(self, interaction: discord.Interaction):
        db_cog = self.get_database_cog()
        if not db_cog:
            await interaction.response.send_message('❌ データベースエラーが発生しました。', ephemeral=True)
            return

        user_cookies = db_cog.get_user_cookies(interaction.user.id)
        if not user_cookies:
            await interaction.response.send_message(
                '❌ HoYoLABのクッキーが設定されていません。\n'
                'まず `/set_cookie` コマンドでクッキーを設定してください。',
                ephemeral=True
            )
            return

        try:
            await interaction.response.defer()
            
            client = genshin.Client(user_cookies)
            notes = await client.get_genshin_notes()
            
            # 樹脂回復時間を計算
            if notes.current_resin < notes.max_resin:
                recovery_time = datetime.now() + timedelta(seconds=notes.resin_recovery_time)
                recovery_str = recovery_time.strftime('%Y/%m/%d %H:%M')
            else:
                recovery_str = '満タン！'

            embed = discord.Embed(
                title='🔋 樹脂状況',
                color=0x00CED1
            )
            
            embed.add_field(
                name='現在の樹脂',
                value=f'{notes.current_resin}/{notes.max_resin}',
                inline=True
            )
            
            embed.add_field(
                name='満タンまで',
                value=recovery_str,
                inline=True
            )
            
            # デイリー任務
            embed.add_field(
                name='デイリー任務',
                value=f'{notes.completed_commissions}/4 完了',
                inline=True
            )
            
            # 週ボス
            embed.add_field(
                name='週ボス割引',
                value=f'{notes.remaining_resin_discounts}/3 残り',
                inline=True
            )
            
            # 洞天宝銭
            if hasattr(notes, 'current_realm_currency'):
                embed.add_field(
                    name='洞天宝銭',
                    value=f'{notes.current_realm_currency}/{notes.max_realm_currency}',
                    inline=True
                )
            
            # 参量物質変換器
            if hasattr(notes, 'transformer'):
                if notes.transformer.obtained:
                    if notes.transformer.recovery_time:
                        transformer_time = datetime.now() + timedelta(seconds=notes.transformer.recovery_time)
                        transformer_str = transformer_time.strftime('%H:%M')
                    else:
                        transformer_str = '使用可能'
                    
                    embed.add_field(
                        name='参量物質変換器',
                        value=transformer_str,
                        inline=True
                    )

            embed.set_footer(text=f'HoYoLAB APIより取得 | UID: {interaction.user.id}')
            embed.timestamp = discord.utils.utcnow()
            
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
        db_cog = self.get_database_cog()
        if not db_cog:
            await interaction.response.send_message('❌ データベースエラーが発生しました。', ephemeral=True)
            return

        user_cookies = db_cog.get_user_cookies(interaction.user.id)
        if not user_cookies:
            await interaction.response.send_message(
                '❌ HoYoLABのクッキーが設定されていません。\n'
                'まず `/set_cookie` コマンドでクッキーを設定してください。',
                ephemeral=True
            )
            return

        try:
            await interaction.response.defer()
            
            client = genshin.Client(user_cookies)
            characters = await client.get_genshin_characters()
            
            if not characters:
                await interaction.followup.send('キャラクターが見つかりませんでした。')
                return

            # レアリティ別に分類
            five_star_chars = [c for c in characters if c.rarity == 5]
            four_star_chars = [c for c in characters if c.rarity == 4]
            
            embed = discord.Embed(
                title='🎭 所持キャラクター',
                color=0xFFD700
            )
            
            if five_star_chars:
                five_star_list = []
                for char in sorted(five_star_chars, key=lambda x: x.level, reverse=True)[:10]:
                    five_star_list.append(f'{char.name} Lv.{char.level}')
                
                embed.add_field(
                    name='⭐⭐⭐⭐⭐ 5星キャラクター',
                    value='\n'.join(five_star_list),
                    inline=False
                )
            
            if four_star_chars:
                four_star_list = []
                for char in sorted(four_star_chars, key=lambda x: x.level, reverse=True)[:15]:
                    four_star_list.append(f'{char.name} Lv.{char.level}')
                
                embed.add_field(
                    name='⭐⭐⭐⭐ 4星キャラクター',
                    value='\n'.join(four_star_list),
                    inline=False
                )
            
            embed.add_field(
                name='統計',
                value=f'5星: {len(five_star_chars)}体\n4星: {len(four_star_chars)}体\n合計: {len(characters)}体',
                inline=False
            )
            
            embed.set_footer(text=f'HoYoLAB APIより取得 | UID: {interaction.user.id}')
            embed.timestamp = discord.utils.utcnow()
            
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(
                f'❌ エラーが発生しました: {str(e)}',
                ephemeral=True
            )

    @app_commands.command(name='delete_cookie', description='保存されたクッキーを削除します')
    async def delete_cookie(self, interaction: discord.Interaction):
        db_cog = self.get_database_cog()
        if not db_cog:
            await interaction.response.send_message('❌ データベースエラーが発生しました。', ephemeral=True)
            return

        if db_cog.delete_user_cookies(interaction.user.id):
            embed = discord.Embed(
                title='✅ クッキー削除完了',
                description='保存されていたHoYoLABクッキーを削除しました。',
                color=0x00FF00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                '❌ クッキーの削除に失敗しました。',
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(HoyolabCog(bot))