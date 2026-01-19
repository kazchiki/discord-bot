import discord
from discord.ext import commands
from discord import app_commands
import genshin
import random

class TeamGeneratorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # キャラクターの役割定義
        self.character_roles = {
            # メインDPS
            'dps': [
                '胡桃', '甘雨', '雷電将軍', 'タルタリヤ', '荒瀧一斗', '神里綾華',
                '宵宮', 'エウルア', '魈', 'ヌヴィレット', 'アルレッキーノ',
                'リオセスリ', '放浪者', 'アルハイゼン', 'ナヴィア', 'クロリンデ',
                'ディルック', 'クレー', 'セノ', 'ニィロウ', 'ティナリ', 'キニチ',
                'ムアラニ', 'マーヴィカ'
            ],
            # サブDPS
            'sub_dps': [
                '行秋', '香菱', 'フィッシュル', '北斗', 'ロサリア', '重雲',
                '八重神子', '夜蘭', 'アルベド', 'フリーナ', 'エミリ',
                '煙緋', '凝光', '辛炎', 'セトス', 'カチーナ'
            ],
            # サポート
            'support': [
                'ベネット', 'ディオナ', 'ジン', 'ウェンティ', '楓原万葉', 'スクロース',
                '鍾離', 'ナヒーダ', 'ファルザン', 'レイラ', '雲菫', 'ゴロー',
                '九条裟羅', 'トーマ', 'キャンディス', 'カーヴェ', 'リネット',
                'フレミネット', 'シャルロット', 'シュヴルーズ', 'ガミン', 'オロルン',
                'ラン・ヤン', 'シュヴレーヌ', 'シグウィン', '白朮'
            ],
            # ヒーラー
            'healer': [
                'ベネット', 'ディオナ', 'ジン', 'ココミ', 'バーバラ',
                'ノエル', '七七', '早柚', '瑶瑶', 'ミカ', '白朮',
                'シャルロット', 'フリーナ', 'シグウィン'
            ]
        }

    def get_database_cog(self):
        """データベースCogを取得"""
        return self.bot.get_cog('DatabaseCog')

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
            
            # 1. メインDPS
            if char_by_role['dps']:
                dps = random.choice(char_by_role['dps'])
                team.append(('メインアタッカー', dps))
                used_names.add(dps.name)
            
            # 2. サブDPS
            available_sub = [c for c in char_by_role['sub_dps'] if c.name not in used_names]
            if available_sub:
                sub_dps = random.choice(available_sub)
                team.append(('サブアタッカー', sub_dps))
                used_names.add(sub_dps.name)
            
            # 3. サポート
            available_support = [c for c in char_by_role['support'] if c.name not in used_names]
            if available_support:
                support = random.choice(available_support)
                team.append(('サポート', support))
                used_names.add(support.name)
            
            # 4. ヒーラー
            available_healer = [c for c in char_by_role['healer'] if c.name not in used_names]
            if available_healer:
                healer = random.choice(available_healer)
                team.append(('ヒーラー', healer))
                used_names.add(healer.name)
            
            # チームが4人未満の場合、残りのキャラから補充
            if len(team) < 4:
                all_chars = [c for c in owned_characters if c.name not in used_names]
                while len(team) < 4 and all_chars:
                    extra = random.choice(all_chars)
                    team.append(('サブ', extra))
                    used_names.add(extra.name)
                    all_chars = [c for c in all_chars if c.name != extra.name]
            
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
            characters = await client.get_genshin_characters()
            
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
                embed.add_field(
                    name=f'{i}. {role}',
                    value=f'{char.name} {rarity_stars}\nLv.{char.level}',
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

