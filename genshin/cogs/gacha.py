import discord
from discord.ext import commands
from discord import app_commands
import random

class GachaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # ガチャアイテム
        self.five_star_characters = ['胡桃', '鍾離', '雷電将軍', '甘雨', 'ナヒーダ', 'フリーナ']
        self.four_star_characters = ['香菱', 'フィッシュル', 'スクロース', 'ベネット', 'ディオナ', 'ロサリア']
        self.three_star_weapons = ['飛天御剣', '黒纓槍', '弾弓', '魔導緒論', '冷刃']
        
        # 確率設定
        self.rates = {
            'five_star': 0.006,  # 0.6%
            'four_star': 0.051,  # 5.1%
            'three_star': 0.943  # 94.3%
        }

    def single_pull(self):
        """単発ガチャ"""
        rand = random.random()
        
        if rand < self.rates['five_star']:
            item = random.choice(self.five_star_characters)
            rarity = 5
            color = 0xFFD700  # 金色
        elif rand < self.rates['five_star'] + self.rates['four_star']:
            item = random.choice(self.four_star_characters)
            rarity = 4
            color = 0x9932CC  # 紫色
        else:
            item = random.choice(self.three_star_weapons)
            rarity = 3
            color = 0x4169E1  # 青色
            
        return item, rarity, color

    @app_commands.command(name='gacha', description='原神ガチャシミュレーター')
    @app_commands.describe(count='ガチャを引く回数（1または10）')
    @app_commands.choices(count=[
        app_commands.Choice(name='単発', value=1),
        app_commands.Choice(name='10連', value=10),
    ])
    async def gacha(self, interaction: discord.Interaction, count: int = 1):
        results = []
        five_star_count = 0
        four_star_count = 0
        
        for _ in range(count):
            item, rarity, color = self.single_pull()
            results.append((item, rarity, color))
            
            if rarity == 5:
                five_star_count += 1
            elif rarity == 4:
                four_star_count += 1
        
        # 結果をまとめる
        if count == 1:
            item, rarity, color = results[0]
            embed = discord.Embed(
                title='ガチャ結果',
                description=f'**{item}** {"⭐" * rarity}',
                color=color
            )
        else:
            # 10連の場合
            embed = discord.Embed(
                title='10連ガチャ結果',
                color=0x00FF00
            )
            
            # レアリティ別に整理
            five_stars = [item for item, rarity, _ in results if rarity == 5]
            four_stars = [item for item, rarity, _ in results if rarity == 4]
            three_stars = [item for item, rarity, _ in results if rarity == 3]
            
            if five_stars:
                embed.add_field(
                    name='⭐⭐⭐⭐⭐ (5星)',
                    value='\n'.join(five_stars),
                    inline=False
                )
            
            if four_stars:
                embed.add_field(
                    name='⭐⭐⭐⭐ (4星)',
                    value='\n'.join(four_stars),
                    inline=False
                )
            
            if three_stars:
                embed.add_field(
                    name='⭐⭐⭐ (3星)',
                    value='\n'.join(three_stars[:5]) + ('...' if len(three_stars) > 5 else ''),
                    inline=False
                )
            
            embed.add_field(
                name='統計',
                value=f'5星: {five_star_count}個\n4星: {four_star_count}個\n3星: {10 - five_star_count - four_star_count}個',
                inline=False
            )
        
        embed.set_footer(text='※これはシミュレーションです')
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(GachaCog(bot))