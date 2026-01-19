import discord
from discord.ext import commands
from discord import app_commands
import genshin
import re
from datetime import datetime, timedelta

class AuthkeyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_database_cog(self):
        """データベースCogを取得"""
        return self.bot.get_cog('DatabaseCog')

    def extract_authkey_from_url(self, url: str):
        """URLからAuthkeyを抽出"""
        try:
            # authkey パラメータを抽出
            authkey_match = re.search(r'authkey=([^&]+)', url)
            if authkey_match:
                return authkey_match.group(1)
            return None
        except Exception:
            return None

    @app_commands.command(name='set_authkey', description='Authkeyを使用してHoYoLAB認証を設定します（より簡単）')
    @app_commands.describe(
        authkey_or_url='Authkey文字列またはガチャ履歴のURL',
        uid='原神のUID（9桁の数字）'
    )
    async def set_authkey(self, interaction: discord.Interaction, authkey_or_url: str, uid: int):
        # DMでのみ実行可能
        if interaction.guild is not None:
            await interaction.response.send_message(
                '⚠️ セキュリティのため、このコマンドはDMでのみ使用できます。\n'
                'Botに直接DMを送って `/set_authkey` を実行してください。',
                ephemeral=True
            )
            return

        try:
            # URLからAuthkeyを抽出を試行
            authkey = self.extract_authkey_from_url(authkey_or_url)
            if not authkey:
                # 直接Authkeyが渡された場合
                authkey = authkey_or_url

            # UIDの形式チェック
            if not (100000000 <= uid <= 999999999):
                await interaction.response.send_message(
                    '❌ 無効なUID形式です。UIDは9桁の数字である必要があります。',
                    ephemeral=True
                )
                return

            # テスト接続
            client = genshin.Client()
            client.set_authkey(authkey)
            
            # 簡単なテストリクエスト
            try:
                # ガチャ履歴を1件だけ取得してテスト
                wishes = await client.wish_history(limit=1, uid=uid)
                test_success = True
            except Exception as e:
                test_success = False
                error_msg = str(e)

            if not test_success:
                await interaction.response.send_message(
                    f'❌ AuthkeyまたはUIDが無効です。\n'
                    f'エラー: {error_msg}\n\n'
                    '**Authkeyの取得方法:**\n'
                    '1. 原神を起動してガチャ画面を開く\n'
                    '2. ガチャ履歴を開く\n'
                    '3. ブラウザが開いたらURLをコピー\n'
                    '4. そのURLをこのコマンドに貼り付け',
                    ephemeral=True
                )
                return

            # データベースにAuthkeyとUIDを保存
            db_cog = self.get_database_cog()
            if db_cog:
                auth_data = {
                    'authkey': authkey,
                    'uid': uid,
                    'type': 'authkey'
                }
                
                if db_cog.save_user_cookies(interaction.user.id, auth_data):
                    embed = discord.Embed(
                        title='✅ Authkey設定完了',
                        description='Authkeyが正常に設定され、暗号化して保存されました！',
                        color=0x00FF00
                    )
                    
                    embed.add_field(
                        name='設定されたUID',
                        value=str(uid),
                        inline=True
                    )
                    
                    embed.add_field(
                        name='認証方式',
                        value='Authkey',
                        inline=True
                    )
                    
                    embed.add_field(
                        name='利用可能な機能',
                        value='• ガチャ履歴\n• 一部の統計情報',
                        inline=False
                    )
                    
                    embed.add_field(
                        name='⚠️ 注意',
                        value='Authkeyは定期的に更新が必要です（通常24時間で期限切れ）',
                        inline=False
                    )

                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message(
                        '❌ Authkeyの保存に失敗しました。',
                        ephemeral=True
                    )
            else:
                await interaction.response.send_message(
                    '❌ データベースエラーが発生しました。',
                    ephemeral=True
                )

        except Exception as e:
            await interaction.response.send_message(
                f'❌ エラーが発生しました: {str(e)}\n'
                'Authkeyまたはガチャ履歴URLが正しいか確認してください。',
                ephemeral=True
            )

    @app_commands.command(name='gacha_history', description='ガチャ履歴を表示します（最新20件）')
    @app_commands.describe(banner='ガチャの種類を選択')
    @app_commands.choices(banner=[
        app_commands.Choice(name='キャラクターイベント祈願', value='character'),
        app_commands.Choice(name='武器イベント祈願', value='weapon'),
        app_commands.Choice(name='恒常祈願', value='standard'),
        app_commands.Choice(name='初心者祈願', value='novice'),
    ])
    async def gacha_history(self, interaction: discord.Interaction, banner: str = 'character'):
        db_cog = self.get_database_cog()
        if not db_cog:
            await interaction.response.send_message('❌ データベースエラーが発生しました。', ephemeral=True)
            return

        auth_data = db_cog.get_user_cookies(interaction.user.id)
        if not auth_data or 'authkey' not in auth_data:
            await interaction.response.send_message(
                '❌ Authkeyが設定されていません。\n'
                'まず `/set_authkey` コマンドでAuthkeyを設定してください。',
                ephemeral=True
            )
            return

        try:
            await interaction.response.defer()
            
            client = genshin.Client()
            client.set_authkey(auth_data['authkey'])
            
            # バナータイプのマッピング
            banner_types = {
                'character': genshin.models.BannerType.CHARACTER,
                'weapon': genshin.models.BannerType.WEAPON,
                'standard': genshin.models.BannerType.STANDARD,
                'novice': genshin.models.BannerType.NOVICE
            }
            
            banner_names = {
                'character': 'キャラクターイベント祈願',
                'weapon': '武器イベント祈願',
                'standard': '恒常祈願',
                'novice': '初心者祈願'
            }
            
            # ガチャ履歴を取得
            wishes = await client.wish_history(
                banner_type=banner_types[banner],
                limit=20,
                uid=auth_data['uid']
            )
            
            if not wishes:
                await interaction.followup.send(f'{banner_names[banner]}の履歴が見つかりませんでした。')
                return

            embed = discord.Embed(
                title=f'🎲 {banner_names[banner]} 履歴',
                description=f'最新20件の結果（UID: {auth_data["uid"]}）',
                color=0xFFD700
            )
            
            # レアリティ別に分類
            five_star_wishes = [w for w in wishes if w.rarity == 5]
            four_star_wishes = [w for w in wishes if w.rarity == 4]
            three_star_wishes = [w for w in wishes if w.rarity == 3]
            
            if five_star_wishes:
                five_star_list = []
                for wish in five_star_wishes[:5]:  # 最大5件
                    five_star_list.append(f'{wish.name} ({wish.time.strftime("%m/%d %H:%M")})')
                
                embed.add_field(
                    name='⭐⭐⭐⭐⭐ 5星',
                    value='\n'.join(five_star_list) if five_star_list else 'なし',
                    inline=False
                )
            
            if four_star_wishes:
                four_star_list = []
                for wish in four_star_wishes[:8]:  # 最大8件
                    four_star_list.append(f'{wish.name} ({wish.time.strftime("%m/%d %H:%M")})')
                
                embed.add_field(
                    name='⭐⭐⭐⭐ 4星',
                    value='\n'.join(four_star_list) if four_star_list else 'なし',
                    inline=False
                )
            
            # 統計情報
            embed.add_field(
                name='統計（最新20件）',
                value=f'5星: {len(five_star_wishes)}個\n4星: {len(four_star_wishes)}個\n3星: {len(three_star_wishes)}個',
                inline=True
            )
            
            # 最後の5星からの回数を計算
            if wishes:
                last_five_star_index = None
                for i, wish in enumerate(wishes):
                    if wish.rarity == 5:
                        last_five_star_index = i
                        break
                
                if last_five_star_index is not None:
                    pity_count = last_five_star_index
                else:
                    pity_count = len(wishes)
                
                embed.add_field(
                    name='天井カウント',
                    value=f'{pity_count}回',
                    inline=True
                )

            embed.set_footer(text='Authkey APIより取得')
            embed.timestamp = discord.utils.utcnow()
            
            await interaction.followup.send(embed=embed)

        except genshin.errors.AuthkeyTimeout:
            await interaction.followup.send(
                '❌ Authkeyの有効期限が切れています。新しいAuthkeyを設定してください。',
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f'❌ エラーが発生しました: {str(e)}',
                ephemeral=True
            )

    @app_commands.command(name='authkey_help', description='Authkeyの取得方法を説明します')
    async def authkey_help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title='📱 Authkey取得方法',
            description='スマホでも簡単に取得できます！',
            color=0x00BFFF
        )
        
        embed.add_field(
            name='📱 スマホ（推奨）',
            value='1. 原神アプリを起動\n'
                  '2. ガチャ画面を開く\n'
                  '3. 「履歴」をタップ\n'
                  '4. ブラウザが開いたらURLをコピー\n'
                  '5. `/set_authkey [URL] [UID]` で設定',
            inline=False
        )
        
        embed.add_field(
            name='💻 PC',
            value='1. 原神を起動してガチャ画面へ\n'
                  '2. ガチャ履歴を開く\n'
                  '3. ブラウザのURLをコピー\n'
                  '4. `/set_authkey [URL] [UID]` で設定',
            inline=False
        )
        
        embed.add_field(
            name='🆔 UIDの確認方法',
            value='ゲーム内の右下のUIDをメモ\n'
                  '（9桁の数字）',
            inline=False
        )
        
        embed.add_field(
            name='⚠️ 注意事項',
            value='• Authkeyは24時間で期限切れ\n'
                  '• 定期的な再設定が必要\n'
                  '• ログアウト不要\n'
                  '• スマホでも使用可能',
            inline=False
        )
        
        embed.add_field(
            name='🔒 セキュリティ',
            value='• DMでのみ設定可能\n'
                  '• 暗号化して保存\n'
                  '• 他のユーザーからアクセス不可',
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AuthkeyCog(bot))