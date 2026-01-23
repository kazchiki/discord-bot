# -*- coding: utf-8 -*-
"""
データベースアクセス層
純粋なデータベース操作のみを行う
"""

import sqlite3
import json
import os
from cryptography.fernet import Fernet
from typing import Optional, Dict, Any, List, Tuple


class Database:
    """データベース操作クラス（Cogではない純粋なDB層）"""
    
    def __init__(self, db_path: str = 'user_data.db', key_path: str = 'encryption.key'):
        """
        データベースを初期化
        
        Args:
            db_path: データベースファイルのパス
            key_path: 暗号化キーファイルのパス
        """
        self.db_path = db_path
        self.key_path = key_path
        self.cipher = self._get_cipher()
        self._init_database()
    
    def _get_cipher(self) -> Fernet:
        """暗号化キーを取得または生成"""
        if os.path.exists(self.key_path):
            with open(self.key_path, 'rb') as key_file:
                key = key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as key_file:
                key_file.write(key)
        return Fernet(key)
    
    def _init_database(self) -> None:
        """データベーステーブルを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # user_cookiesテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_cookies (
                user_id INTEGER PRIMARY KEY,
                encrypted_cookies TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # user_settingsテーブル
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
        
        # resin_thresholdカラムの追加（既存DBとの互換性のため）
        try:
            cursor.execute("SELECT resin_threshold FROM user_settings LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE user_settings ADD COLUMN resin_threshold INTEGER DEFAULT 200")
            print("データベースを更新しました: resin_threshold カラムを追加")
        
        conn.commit()
        conn.close()
    
    # === クッキー関連のメソッド ===
    
    def save_user_cookies(self, user_id: int, cookies: dict) -> bool:
        """
        ユーザーのクッキーを暗号化して保存
        
        Args:
            user_id: ユーザーID
            cookies: クッキーの辞書
            
        Returns:
            bool: 成功したらTrue
        """
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
    
    def get_user_cookies(self, user_id: int) -> Optional[dict]:
        """
        ユーザーのクッキーを復号化して取得
        
        Args:
            user_id: ユーザーID
            
        Returns:
            dict: クッキーの辞書、存在しない場合はNone
        """
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
    
    def delete_user_cookies(self, user_id: int) -> bool:
        """
        ユーザーのクッキーを削除
        
        Args:
            user_id: ユーザーID
            
        Returns:
            bool: 成功したらTrue
        """
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
    
    # === 設定関連のメソッド ===
    
    def save_user_settings(self, user_id: int, **settings) -> bool:
        """
        ユーザー設定を保存
        
        Args:
            user_id: ユーザーID
            **settings: 設定項目（キーワード引数）
            
        Returns:
            bool: 成功したらTrue
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 既存の設定を確認
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
    
    def get_user_settings(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        ユーザー設定を取得
        
        Args:
            user_id: ユーザーID
            
        Returns:
            dict: 設定の辞書、存在しない場合はNone
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM user_settings WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if result:
                columns = [description[0] for description in cursor.description]
                conn.close()
                return dict(zip(columns, result))
            
            conn.close()
            return None
        except Exception as e:
            print(f"設定取得エラー: {e}")
            return None
    
    def delete_user_settings(self, user_id: int) -> bool:
        """
        ユーザー設定を削除
        
        Args:
            user_id: ユーザーID
            
        Returns:
            bool: 成功したらTrue
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM user_settings WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"設定削除エラー: {e}")
            return False
    
    def get_all_users_with_resin_reminder(self) -> List[Tuple[int, bool, int]]:
        """
        樹脂リマインダーが有効なすべてのユーザーを取得
        
        Returns:
            List[Tuple]: (user_id, enabled, threshold) のリスト
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, resin_reminder_enabled, resin_threshold
                FROM user_settings 
                WHERE resin_reminder_enabled = 1
            ''')
            
            users = cursor.fetchall()
            conn.close()
            return users
        except Exception as e:
            print(f"ユーザー一覧取得エラー: {e}")
            return []
    
    # === ユーザーデータの完全削除 ===
    
    def delete_all_user_data(self, user_id: int) -> bool:
        """
        ユーザーの全データを削除（クッキーと設定の両方）
        
        Args:
            user_id: ユーザーID
            
        Returns:
            bool: 成功したらTrue
        """
        try:
            cookies_deleted = self.delete_user_cookies(user_id)
            settings_deleted = self.delete_user_settings(user_id)
            return cookies_deleted or settings_deleted
        except Exception as e:
            print(f"全データ削除エラー: {e}")
            return False
