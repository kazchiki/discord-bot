import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import sys

# genshinディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 環境変数を読み込み
load_dotenv()

# Botの設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# データベースインスタンスを1つ作成（全Controllerで共有）
from models.database import Database
database = Database()

@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました！')
    try:
        synced = await bot.tree.sync()
        print(f'{len(synced)} 個のスラッシュコマンドを同期しました')
    except Exception as e:
        print(f'コマンドの同期に失敗しました: {e}')

# コントローラー（拡張機能）を読み込み
async def load_extensions():
    """Controllersフォルダから全てのコントローラーをロード"""
    controllers_dir = './controllers'
    
    if not os.path.exists(controllers_dir):
        print(f'エラー: {controllers_dir} フォルダが見つかりません')
        return
    
    loaded_count = 0
    for filename in os.listdir(controllers_dir):
        if filename.endswith('.py') and not filename.startswith('_'):
            try:
                # データベースインスタンスをbotに保存（Controllerから参照可能にする）
                bot.database = database
                await bot.load_extension(f'controllers.{filename[:-3]}')
                print(f'✅ {filename} を読み込みました')
                loaded_count += 1
            except Exception as e:
                print(f'❌ {filename} の読み込みに失敗しました: {e}')
                import traceback
                traceback.print_exc()
    
    print(f'\n合計 {loaded_count} 個のコントローラーを読み込みました')

async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())