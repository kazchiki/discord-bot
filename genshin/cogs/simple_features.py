import discord
from discord.ext import commands
from discord import app_commands
import random
from datetime import datetime, timedelta

class SimpleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # 今日のおすすめ聖遺物ドメイン
        self.artifact_domains = {
            0: "菫色ノ庭（雷電将軍、八重神子用）",  # 月曜日
            1: "華池岩岫（胡桃、ディルック用）",    # 火曜日
            2: "辰砂往生録（タルタリヤ、神里綾人用）", # 水曜日
            3: "深林の記憶（ナヒーダ、ティナリ用）",  # 木曜日
            4: "金メッキの夢（ニィロウ、放浪者用）",  # 金曜日
            5: "氷風を彷徨う勇士（甘雨、神里綾華用）", # 土曜日
            6: "翠緑の影（ウェンティ、楓原万葉用）"   # 日曜日
        }
        
        # 元素反応の説明
        self.reactions = {
            "蒸発": {"elements": ["炎", "水"], "multiplier": "1.5x/2x", "description": "炎→水で1.5倍、水→炎で2倍のダメージ"},
            "溶解": {"elements": ["炎", "氷"], "multiplier": "1.5x/2x", "description": "炎→氷で1.5倍、氷→炎で2倍のダメージ"},
            "過負荷": {"elements": ["炎", "雷"], "multiplier": "固定", "description": "爆発ダメージ、敵を吹き飛ばす"},
            "超電導": {"elements": ["雷", "氷"], "multiplier": "固定", "description": "氷ダメージ、物理耐性-40%"},
            "感電": {"elements": ["雷", "水"], "multiplier": "継続", "description": "継続的な雷ダメージ"},
            "凍結": {"elements": ["氷", "水"], "multiplier": "状態", "description": "敵を凍結させる"},
            "拡散": {"elements": ["風", "他"], "multiplier": "固定", "description": "元素を拡散させる"},
            "結晶": {"elements": ["岩", "他"], "multiplier": "シールド", "description": "元素シールドを生成"}
        }

    @app_commands.command(name='daily_domain', description='今日のおすすめ聖遺物ドメインを表示します')
    async def daily_domain(self, interaction: discord.Interaction):
        today = datetime.now().weekday()
        domain = self.artifact_domains[today]
        
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        
        embed = discord.Embed(
            title=f'📅 今日（{weekdays[today]}曜日）のおすすめドメイン',
            description=domain,
            color=0x9932CC
        )
        
        embed.add_field(
            name='💡 ヒント',
            value='毎日違うドメインをおすすめしているので、計画的に聖遺物を集めましょう！',
            inline=False
        )
        
        embed.set_footer(text='効率的な聖遺物集めを！')
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='element_reaction', description='元素反応の詳細を表示します')
    @app_commands.describe(reaction='元素反応を選択してください')
    @app_commands.choices(reaction=[
        app_commands.Choice(name='蒸発（炎×水）', value='蒸発'),
        app_commands.Choice(name='溶解（炎×氷）', value='溶解'),
        app_commands.Choice(name='過負荷（炎×雷）', value='過負荷'),
        app_commands.Choice(name='超電導（雷×氷）', value='超電導'),
        app_commands.Choice(name='感電（雷×水）', value='感電'),
        app_commands.Choice(name='凍結（氷×水）', value='凍結'),
        app_commands.Choice(name='拡散（風×他）', value='拡散'),
        app_commands.Choice(name='結晶（岩×他）', value='結晶'),
    ])
    async def element_reaction(self, interaction: discord.Interaction, reaction: str):
        reaction_data = self.reactions[reaction]
        
        # 元素の色
        element_colors = {
            '炎': 0xFF6B6B,
            '水': 0x4ECDC4,
            '雷': 0xA8E6CF,
            '氷': 0x88D8C0,
            '風': 0x95E1D3,
            '岩': 0xF38BA8,
            '草': 0x88C999
        }
        
        # 反応に関わる元素の色を使用
        color = element_colors.get(reaction_data['elements'][0], 0x0099FF)
        
        embed = discord.Embed(
            title=f'⚡ {reaction}',
            description=reaction_data['description'],
            color=color
        )
        
        embed.add_field(
            name='関連元素',
            value=' × '.join(reaction_data['elements']),
            inline=True
        )
        
        embed.add_field(
            name='ダメージ倍率',
            value=reaction_data['multiplier'],
            inline=True
        )
        
        # 反応別の詳細情報
        if reaction == '蒸発':
            embed.add_field(
                name='詳細',
                value='• 炎→水: 1.5倍\n• 水→炎: 2倍\n• 元素熟知でダメージアップ',
                inline=False
            )
        elif reaction == '溶解':
            embed.add_field(
                name='詳細',
                value='• 炎→氷: 1.5倍\n• 氷→炎: 2倍\n• 元素熟知でダメージアップ',
                inline=False
            )
        elif reaction == '超電導':
            embed.add_field(
                name='詳細',
                value='• 物理耐性-40%（12秒）\n• 物理アタッカーと相性抜群',
                inline=False
            )
        
        embed.set_footer(text='元素反応を活用して戦闘を有利に！')
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='team_suggest', description='ランダムなチーム編成を提案します')
    async def team_suggest(self, interaction: discord.Interaction):
        # 簡易的なキャラクタープール
        characters = {
            'dps': ['胡桃', '甘雨', '雷電将軍', 'タルタリヤ', 'イット', '神里綾華'],
            'sub_dps': ['行秋', '香菱', 'フィッシュル', '北斗', 'ロサリア', '重雲'],
            'support': ['ベネット', 'ディオナ', 'ジン', 'ウェンティ', '楓原万葉', 'スクロース'],
            'healer': ['ベネット', 'ディオナ', 'ジン', 'ココミ', 'バーバラ', 'ノエル']
        }
        
        # ランダムにチームを編成
        main_dps = random.choice(characters['dps'])
        sub_dps = random.choice([c for c in characters['sub_dps'] if c != main_dps])
        support = random.choice([c for c in characters['support'] if c not in [main_dps, sub_dps]])
        healer = random.choice([c for c in characters['healer'] if c not in [main_dps, sub_dps, support]])
        
        embed = discord.Embed(
            title='🎯 おすすめチーム編成',
            description='ランダムに生成されたチーム編成です',
            color=0xFFD700
        )
        
        embed.add_field(name='メインアタッカー', value=main_dps, inline=True)
        embed.add_field(name='サブアタッカー', value=sub_dps, inline=True)
        embed.add_field(name='サポート', value=support, inline=True)
        embed.add_field(name='ヒーラー', value=healer, inline=True)
        
        embed.add_field(
            name='💡 ヒント',
            value='このチーム編成を参考に、手持ちのキャラクターで調整してみてください！',
            inline=False
        )
        
        embed.set_footer(text='チーム編成の参考に！')
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='artifact_tips', description='聖遺物の厳選のコツを表示します')
    async def artifact_tips(self, interaction: discord.Interaction):
        tips = [
            "メイン効果は最優先！サブ効果より重要です",
            "攻撃力%よりも元素ダメージバフの方が効果的",
            "会心率:会心ダメージ = 1:2 の比率を目指そう",
            "元素熟知は反応ダメージを大幅に上げます",
            "元素チャージ効率は元素爆発の回転率に直結",
            "HP%や防御力%も一部キャラには重要",
            "セット効果よりもメイン効果を優先",
            "4セット効果は強力だが、2+2セットも有効"
        ]
        
        selected_tips = random.sample(tips, 4)
        
        embed = discord.Embed(
            title='💎 聖遺物厳選のコツ',
            description='効率的な聖遺物厳選のためのヒント',
            color=0x9932CC
        )
        
        for i, tip in enumerate(selected_tips, 1):
            embed.add_field(
                name=f'コツ {i}',
                value=tip,
                inline=False
            )
        
        embed.add_field(
            name='📊 優先順位',
            value='1. メイン効果\n2. セット効果\n3. サブ効果\n4. 強化レベル',
            inline=False
        )
        
        embed.set_footer(text='聖遺物厳選頑張って！')
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SimpleCog(bot))