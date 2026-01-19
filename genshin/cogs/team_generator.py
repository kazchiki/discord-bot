import discord
from discord.ext import commands
from discord import app_commands
import genshin
import random
from config.constants import CharacterNameMapping

class TeamGeneratorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.character_roles = {
            # メインDPS
            'dps': [
                'Hu Tao', 'Ganyu', 'Raiden Shogun', 'Tartaglia', 'Arataki Itto', 'Kamisato Ayaka',
                'Yoimiya', 'Eula', 'Xiao', 'Neuvillette', 'Arlecchino','Sethos', 'Gaming',
                'Wriothesley', 'Wanderer', 'Alhaitham', 'Navia', 'Clorinde', 'Yanfei', 'Ningguang',
                'Diluc', 'Klee', 'Cyno', 'Tighnari', 'Kinich', 'Chasca',
                'Mualani', 'Mavuika', 'Keqing', 'Lyney',
                'Durin', 'Manekina', 'Manekin', 'Columbina', 'Skirk',
                'Yumemizuki Mizuki', 'Neferiti', 'Flins'
            ],
            # サブDPS
            'sub_dps': [
                'Xingqiu', 'Xiangling', 'Fischl', 'Beidou', 'Rosaria', 'Chongyun',
                'Yae Miko', 'Yelan', 'Albedo', 'Furina', 'Emilie', 'Shikanoin Heizou',
                'Xinyan', 'Kachina', 'Nilou', 'Chiori', 'Dori', 'Ifa', 'Noelle',
                'Aino', 'Dahlia', 'Jahoda', 'Lauma', 'Ineffa',
            ],
            # サポート
            'support': [
                'Bennett', 'Venti', 'Kaedehara Kazuha', 'Sucrose',
                'Zhongli', 'Nahida', 'Faruzan', 'Layla', 'Yun Jin', 'Gorou',
                'Kujou Sara', 'Thoma', 'Candace', 'Kaveh', 'Lynette',
                'Freminet', 'Charlotte', 'Chevreuse', 'Ororon', 'Mika',
                'Lan Yan', 'Kirara', 'Xilonen', 'Citlali', 'Xianyun', 'Kuki Shinobu', 'Iansan'
            ],
            # ヒーラー
            'healer': [
                'Diona', 'Jean', 'Sangonomiya Kokomi', 'Barbara',
                'Qiqi', 'Sayu', 'Yaoyao', 'Baizhu',
                'Charlotte', 'Sigewinne'
            ]
        }

    def get_database_cog(self):
        """データベースCogを取得"""
        return self.bot.get_cog('DatabaseCog')

    def get_japanese_name(self, english_name: str):
        """英語名を日本語名に変換"""
        return CharacterNameMapping.NAMES.get(english_name, english_name)
    
    def classify_character_role(self, char_name: str):
        """キャラクターの役割を判定"""
        roles = []
        for role, characters in self.character_roles.items():
            if char_name in characters:
                roles.append(role)
        return roles if roles else ['other']

    def create_team(self, owned_characters):
        """所持キャラからチームを編成"""
        try:
            # 役割別に分類
            char_by_role = {
                'dps': [],
                'sub_dps': [],
                'support': [],
                'healer': []
            }
            
            for char in owned_characters:
                roles = self.classify_character_role(char.name)
                for role in roles:
                    if role in char_by_role:
                        char_by_role[role].append(char)
            
            # チーム編成（重複を避ける）
            team = []
            used_names = set()
            
            # 優先順位付きでチーム編成
            role_assignments = [
                ('メインアタッカー', 'dps'),
                ('サブアタッカー', 'sub_dps'),
                ('サポート', 'support'),
                ('ヒーラー', 'healer')
            ]
            
            for display_role, role_key in role_assignments:
                if len(team) >= 4:
                    break
                    
                available = [c for c in char_by_role[role_key] if c.name not in used_names]
                if available:
                    selected = random.choice(available)
                    team.append((display_role, selected))
                    used_names.add(selected.name)
            
            # チームが4人未満の場合、残りのキャラから役割を自動判定して補充
            if len(team) < 4:
                remaining_chars = [c for c in owned_characters if c.name not in used_names]
                
                # レアリティとレベルでソート（高い方を優先）
                remaining_chars.sort(key=lambda x: (x.rarity, x.level), reverse=True)
                
                # 残りの役割を割り当て
                remaining_roles = ['メインアタッカー', 'サブアタッカー', 'サポート', 'ヒーラー']
                used_roles = [role for role, _ in team]
                available_roles = [r for r in remaining_roles if r not in used_roles]
                
                for char in remaining_chars:
                    if len(team) >= 4:
                        break
                    
                    # まだ使われていない役割があれば使用、なければ「サブ」
                    if available_roles:
                        role = available_roles.pop(0)
                    else:
                        role = 'サブ'
                    
                    team.append((role, char))
                    used_names.add(char.name)
            
            return team
        
        except Exception as e:
            print(f"チーム編成エラー: {e}")
            return None

    @app_commands.command(name='team_generator', description='所持キャラからランダムなチーム編成を提案します')
    async def team_generator(self, interaction: discord.Interaction):
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
            
            # HoYoLAB APIから所持キャラを取得
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
                await interaction.followup.send('❌ キャラクターが見つかりませんでした。')
                return
            
            # レベル1以上のキャラのみ（所持している）
            owned_chars = [c for c in characters if c.level > 1]
            
            if len(owned_chars) < 4:
                await interaction.followup.send(
                    f'❌ チーム編成には最低4人のキャラクターが必要です。\n'
                    f'現在の所持数: {len(owned_chars)}人'
                )
                return
            
            # チームを編成
            team = self.create_team(owned_chars)
            
            if not team:
                await interaction.followup.send('❌ チーム編成に失敗しました。')
                return
            
            # Embed作成
            embed = discord.Embed(
                title='🎯 おすすめチーム編成',
                description=f'あなたの所持キャラ（{len(owned_chars)}人）から生成されたチーム編成です',
                color=0xFFD700
            )
            
            for i, (role, char) in enumerate(team, 1):
                rarity_stars = '⭐' * char.rarity
                jp_name = self.get_japanese_name(char.name)
                embed.add_field(
                    name=f'{i}. {role}',
                    value=f'{jp_name} {rarity_stars}\nLv.{char.level}',
                    inline=True
                )
            
            embed.add_field(
                name='💡 ヒント',
                value='気に入らない場合は、もう一度コマンドを実行して別の編成を試してください！',
                inline=False
            )
            
            embed.set_footer(text='HoYoLAB APIより取得')
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

async def setup(bot):
    await bot.add_cog(TeamGeneratorCog(bot))

