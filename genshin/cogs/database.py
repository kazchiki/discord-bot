import discord
from discord.ext import commands
import sqlite3
import json
import os
from cryptography.fernet import Fernet

class DatabaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = 'user_data.db'
        self.key_path = 'encryption.key'
        self.init_database()
        self.cipher = self.get_cipher()

    def get_cipher(self):
        """暗号化キーを取得または生成"""
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as key_file:
                key = key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as key_file:
                key_file.write(key)
        return Fernet(key)

    def init_database(self):
        """データベースを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_cookies (
                user_id INTEGER PRIMARY KEY,
                encrypted_cookies TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                resin_reminder_enabled BOOLEAN DEFAULT FALSE,
                resin_threshold INTEGER DEFAULT 200,
                notification_channel_id INTEGER,
                timezone TEXT DEFAULT 'UTC',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 既存のuser_settingsテーブルにresin_thresholdカラムを追加（存在しない場合）
        try:
            cursor.execute("SELECT resin_threshold FROM user_settings LIMIT 1")
        except sqlite3.OperationalError:
            # カラムが存在しない場合は追加
            cursor.execute("ALTER TABLE user_settings ADD COLUMN resin_threshold INTEGER DEFAULT 200")
            print("データベースを更新しました: resin_threshold カラムを追加")
        
        conn.commit()
        conn.close()

    def save_user_cookies(self, user_id: int, cookies: dict):
        """ユーザーのクッキーを暗号化して保存"""
        try:
            cookies_json = json.dumps(cookies)
            encrypted_cookies = self.cipher.encrypt(cookies_json.encode())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_cookies (user_id, encrypted_cookies, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, encrypted_cookies.decode()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"クッキー保存エラー: {e}")
            return False

    def get_user_cookies(self, user_id: int):
        """ユーザーのクッキーを復号化して取得"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT encrypted_cookies FROM user_cookies WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                encrypted_cookies = result[0].encode()
                decrypted_cookies = self.cipher.decrypt(encrypted_cookies)
                return json.loads(decrypted_cookies.decode())
            return None
        except Exception as e:
            print(f"クッキー取得エラー: {e}")
            return None

    def delete_user_cookies(self, user_id: int):
        """ユーザーのクッキーを削除"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM user_cookies WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"クッキー削除エラー: {e}")
            return False

    def save_user_settings(self, user_id: int, **settings):
        """ユーザー設定を保存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 既存の設定を取得
            cursor.execute('SELECT * FROM user_settings WHERE user_id = ?', (user_id,))
            existing = cursor.fetchone()
            
            if existing:
                # 更新
                set_clause = []
                values = []
                for key, value in settings.items():
                    set_clause.append(f"{key} = ?")
                    values.append(value)
                
                if set_clause:
                    values.append(user_id)
                    cursor.execute(f'''
                        UPDATE user_settings 
                        SET {", ".join(set_clause)}, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', values)
            else:
                # 新規作成
                columns = ['user_id'] + list(settings.keys())
                placeholders = ['?'] * len(columns)
                values = [user_id] + list(settings.values())
                
                cursor.execute(f'''
                    INSERT INTO user_settings ({", ".join(columns)})
                    VALUES ({", ".join(placeholders)})
                ''', values)
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"設定保存エラー: {e}")
            return False

    def get_user_settings(self, user_id: int):
        """ユーザー設定を取得"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM user_settings WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            return None
        except Exception as e:
            print(f"設定取得エラー: {e}")
            return None

    @commands.command(name='delete_data')
    async def delete_user_data(self, ctx):
        """ユーザーデータを削除（管理用）"""
        if ctx.author.id != ctx.bot.owner_id:  # Bot所有者のみ実行可能
            return
        
        user_id = ctx.author.id
        cookies_deleted = self.delete_user_cookies(user_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_settings WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        if cookies_deleted:
            await ctx.send('✅ ユーザーデータを削除しました。')
        else:
            await ctx.send('❌ データの削除に失敗しました。')

async def setup(bot):
    await bot.add_cog(DatabaseCog(bot))