import discord
from discord.ext import commands, tasks
from discord import app_commands
import genshin
import asyncio
from datetime import datetime, timedelta
from config.constants import CharacterNameMapping

class HoyolabCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.resin_check_loop.start()  # 樹脂チェックタスク開始

    def cog_unload(self):
        """Cog終了時にタスクを停止"""
        self.resin_check_loop.cancel()

    def get_database_cog(self):
        """データベースCogを取得"""
        return self.bot.get_cog('DatabaseCog')
    
    def get_japanese_name(self, english_name: str):
        """英語名を日本語名に変換"""
        return CharacterNameMapping.NAMES.get(english_name, english_name)

    @tasks.loop(minutes=30)  # 30分ごとにチェック
    async def resin_check_loop(self):
        """定期的に樹脂をチェックして通知"""
        try:
            db_cog = self.get_database_cog()
            if not db_cog:
                return
            
            # データベースから全ユーザーの設定を取得
            conn = db_cog.bot.get_cog('DatabaseCog').db_path
            import sqlite3
            conn = sqlite3.connect(db_cog.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, resin_reminder_enabled, resin_threshold
                FROM user_settings 
                WHERE resin_reminder_enabled = 1
            ''')
            
            users = cursor.fetchall()
            conn.close()
            
            for user_id, enabled, threshold in users:
                if not enabled:
                    continue
                
                # ユーザーのクッキーを取得
                user_cookies = db_cog.get_user_cookies(user_id)
                if not user_cookies:
                    continue
                
                try:
                    # 樹脂情報を取得
                    client = genshin.Client(user_cookies)
                    notes = await client.get_genshin_notes()
                    
                    # 閾値チェック（デフォルトは満タン）
                    resin_threshold = threshold if threshold else notes.max_resin
                    
                    if notes.current_resin >= resin_threshold:
                        # 通知送信
                        try:
                            user = await self.bot.fetch_user(user_id)
                            
                            embed = discord.Embed(
                                title='🔔 樹脂リマインダー',
                                description=f'樹脂が{resin_threshold}に達しました！',
                                color=0x00FF00
                            )
                            
                            embed.add_field(
                                name='現在の樹脂',
                                value=f'{notes.current_resin}/{notes.max_resin}',
                                inline=True
                            )
                            
                            if notes.current_resin < notes.max_resin:
                                recovery_time = datetime.now() + timedelta(seconds=notes.resin_recovery_time)
                                embed.add_field(
                                    name='満タンまで',
                                    value=recovery_time.strftime('%H:%M'),
                                    inline=True
                                )
                            
                            embed.set_footer(text='通知を停止するには /resin_notification off を実行してください')
                            embed.timestamp = discord.utils.utcnow()
                            
                            await user.send(embed=embed)
                            
                            # 通知後、一時的に無効化（1時間後に再度有効化）
                            # これにより同じ通知が連続で送られるのを防ぐ
                            # 実装を簡単にするため、ここでは通知後は無効化せず次回チェックまで待つ
                            
                        except Exception as e:
                            print(f"通知送信エラー (User {user_id}): {e}")
                
                except genshin.errors.InvalidCookies:
                    # クッキーが無効な場合はスキップ
                    continue
                except Exception as e:
                    print(f"樹脂チェックエラー (User {user_id}): {e}")
                    continue
        
        except Exception as e:
            print(f"樹脂チェックループエラー: {e}")

    @resin_check_loop.before_loop
    async def before_resin_check(self):
        """Bot起動完了を待つ"""
        await self.bot.wait_until_ready()

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
            
            # アカウント情報からUIDを取得
            accounts = await client.get_game_accounts()
            genshin_accounts = [acc for acc in accounts if acc.game == genshin.Game.GENSHIN]
            
            if not genshin_accounts:
                await interaction.followup.send('❌ 原神のアカウントが見つかりませんでした。')
                return
            
            uid = genshin_accounts[0].uid
            characters = await client.get_genshin_characters(uid)
            
            if not characters:
                await interaction.followup.send('キャラクターが見つかりませんでした。')
                return

            # 元素別に分類
            element_order = ['Pyro', 'Hydro', 'Electro', 'Cryo', 'Anemo', 'Geo', 'Dendro']
            element_names = {
                'Pyro': '🔥 炎',
                'Hydro': '💧 水',
                'Electro': '⚡ 雷',
                'Cryo': '❄️ 氷',
                'Anemo': '🌪️ 風',
                'Geo': '🪨 岩',
                'Dendro': '🌿 草'
            }
            
            chars_by_element = {}
            for element in element_order:
                chars_by_element[element] = [c for c in characters if c.element == element]
            
            embed = discord.Embed(
                title='🎭 所持キャラクター（元素順）',
                description=f'合計 {len(characters)}体',
                color=0xFFD700
            )
            
            for element in element_order:
                element_chars = chars_by_element[element]
                if not element_chars:
                    continue
                
                # レアリティとレベルでソート
                sorted_chars = sorted(element_chars, key=lambda x: (x.rarity, x.level), reverse=True)
                
                char_list = []
                for char in sorted_chars[:20]:  # 各元素最大20体
                    jp_name = self.get_japanese_name(char.name)
                    stars = '⭐' * char.rarity
                    char_list.append(f'{jp_name} {stars} Lv.{char.level}')
                
                if char_list:
                    embed.add_field(
                        name=f'{element_names[element]} ({len(element_chars)}体)',
                        value='\n'.join(char_list),
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
        db_cog = self.get_database_cog()
        if not db_cog:
            await interaction.response.send_message('❌ データベースエラーが発生しました。', ephemeral=True)
            return

        # クッキーが設定されているか確認
        user_cookies = db_cog.get_user_cookies(interaction.user.id)
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
        
        if db_cog.save_user_settings(interaction.user.id, **settings):
            embed = discord.Embed(
                title='✅ 樹脂通知設定完了',
                color=0x00FF00 if is_enabled else 0xFF0000
            )
            
            if is_enabled:
                threshold_text = f'{threshold}' if threshold else '満タン（200）'
                embed.description = f'樹脂が{threshold_text}に達したときに通知します。'
                embed.add_field(
                    name='チェック間隔',
                    value='30分ごと',
                    inline=True
                )
                embed.add_field(
                    name='通知方法',
                    value='DMで通知',
                    inline=True
                )
            else:
                embed.description = '樹脂通知を無効にしました。'
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                '❌ 設定の保存に失敗しました。',
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