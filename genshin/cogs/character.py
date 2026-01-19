import discord
from discord.ext import commands
from discord import app_commands

class CharacterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # 原神キャラクターデータ
        self.characters = {
            'hu_tao': {
                'name': '胡桃',
                'element': '炎',
                'weapon': '長柄武器',
                'rarity': 5,
                'description': '往生堂の堂主。いつも明るく元気だが、時々不思議な行動を取る。',
                'image': 'https://static.wikia.nocookie.net/gensin-impact/images/a/a0/Character_Hu_Tao_Card.png'
            },
            'zhongli': {
                'name': '鍾離',
                'element': '岩',
                'weapon': '長柄武器',
                'rarity': 5,
                'description': '往生堂の客卿。博識で落ち着いた性格の男性。',
                'image': 'https://static.wikia.nocookie.net/gensin-impact/images/c/c2/Character_Zhongli_Card.png'
            },
            'raiden': {
                'name': '雷電将軍',
                'element': '雷',
                'weapon': '長柄武器',
                'rarity': 5,
                'description': '稲妻を統治する雷神。永遠を追求する。',
                'image': 'https://static.wikia.nocookie.net/gensin-impact/images/5/52/Character_Raiden_Shogun_Card.png'
            },
            'ganyu': {
                'name': '甘雨',
                'element': '氷',
                'weapon': '弓',
                'rarity': 5,
                'description': '璃月七星の秘書。半仙の血を引く。',
                'image': 'https://static.wikia.nocookie.net/gensin-impact/images/b/b2/Character_Ganyu_Card.png'
            }
        }
        
        # 元素の色
        self.element_colors = {
            '炎': 0xFF6B6B,
            '水': 0x4ECDC4,
            '雷': 0xA8E6CF,
            '氷': 0x88D8C0,
            '風': 0x95E1D3,
            '岩': 0xF38BA8,
            '草': 0x88C999
        }

    @app_commands.command(name='character', description='原神キャラクターの情報を表示します')
    @app_commands.describe(name='キャラクター名を選択してください')
    @app_commands.choices(name=[
        app_commands.Choice(name='胡桃', value='hu_tao'),
        app_commands.Choice(name='鍾離', value='zhongli'),
        app_commands.Choice(name='雷電将軍', value='raiden'),
        app_commands.Choice(name='甘雨', value='ganyu'),
    ])
    async def character(self, interaction: discord.Interaction, name: str):
        character = self.characters.get(name)
        
        if not character:
            await interaction.response.send_message('そのキャラクターは見つかりませんでした。', ephemeral=True)
            return
        
        # Embedを作成
        embed = discord.Embed(
            title=character['name'],
            description=character['description'],
            color=self.element_colors.get(character['element'], 0x0099FF)
        )
        
        embed.add_field(name='元素', value=character['element'], inline=True)
        embed.add_field(name='武器', value=character['weapon'], inline=True)
        embed.add_field(name='レアリティ', value='⭐' * character['rarity'], inline=True)
        
        embed.set_thumbnail(url=character['image'])
        embed.set_footer(text='原神キャラクター情報')
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CharacterCog(bot))