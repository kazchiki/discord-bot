# -*- coding: utf-8 -*-
"""
チーム編成サービス
チーム編成アルゴリズムを実装
"""

import random
from typing import List, Tuple, Set, Optional


class TeamService:
    """チーム編成サービスクラス"""
    
    # キャラクターの役割定義(GameWith評価)
    CHARACTER_ROLES = {
        'dps': [
            'Venti', 'Klee', 'Eula', 'Diluc', 'Noelle',
            'Gaming', 'Hu Tao', 'Ganyu', 'Tartaglia', 'Xiao', 'Ningguang', 'Keqing', 'Yanfei',
            'Raiden Shogun', 'Kamisato Ayato', 'Kamisato Ayaka', 'Arataki Itto', 'Yoimiya', 'Yumemizuki Mizuki',
            'Alhaitham', 'Wanderer', 'Sethos', 'Cyno', 'Tighnari',
            'Arlecchino', 'Neuvillette', 'Lyney', 'Navia', 'Clorinde', 'Wriothesley', 'Traveler',
            'Mavuika', 'Skirk', 'Mualani', 'Varesa', 'Kinich', 'Chasca',
            'Nefer', 'Flins', 'Columbina',
            'Manekina', 'Manekin',
        ],
        'sub_dps': [
            'Durin', 'Xingqiu', 'Xiangling', 'Fischl', 'Beidou', 'Rosaria', 'Chongyun',
            'Yae Miko', 'Yelan', 'Albedo', 'Furina', 'Emilie', 'Shikanoin Heizou',
            'Xinyan', 'Kachina', 'Nilou', 'Chiori', 'Dori', 'Ifa',
            'Aino', 'Dahlia', 'Jahoda', 'Lauma', 'Ineffa',
        ],
        'support': [
            'Bennett', 'Venti', 'Kaedehara Kazuha', 'Sucrose',
            'Zhongli', 'Nahida', 'Faruzan', 'Layla', 'Yun Jin', 'Gorou',
            'Kujou Sara', 'Thoma', 'Candace', 'Kaveh', 'Lynette',
            'Freminet', 'Chevreuse', 'Ororon', 'Mika',
            'Lan Yan', 'Kirara', 'Xilonen', 'Citlali', 'Xianyun', 'Kuki Shinobu', 'Iansan'
        ],
        'healer': [
            'Diona', 'Jean', 'Sangonomiya Kokomi', 'Barbara',
            'Qiqi', 'Sayu', 'Yaoyao', 'Baizhu',
            'Charlotte', 'Sigewinne'
        ]
    }
    
    @staticmethod
    def classify_character_role(char_name: str) -> List[str]:
        """
        キャラクターの役割を判定
        
        Args:
            char_name: キャラクター名（英語）
            
        Returns:
            List[str]: 役割のリスト
        """
        roles = []
        for role, characters in TeamService.CHARACTER_ROLES.items():
            if char_name in characters:
                roles.append(role)
        return roles if roles else ['other']
    
    @staticmethod
    def filter_owned_characters(characters: List, min_level: int = 1) -> List:
        """
        所持キャラクターをフィルタリング
        
        Args:
            characters: キャラクターのリスト
            min_level: 最小レベル（デフォルト: 1より大きい = レベル上げしたキャラ）
            
        Returns:
            List: フィルタリングされたキャラクターのリスト
        """
        return [c for c in characters if c.level > min_level]
    
    @staticmethod
    def create_team(owned_characters: List) -> List[Tuple[str, any]]:
        """
        所持キャラからランダムなチームを編成
        
        Args:
            owned_characters: 所持キャラクターのリスト
            
        Returns:
            List[Tuple[str, any]]: (役割名, キャラクター)のタプルのリスト
        """
        # 役割別に分類
        char_by_role = {
            'dps': [],
            'sub_dps': [],
            'support': [],
            'healer': []
        }
        
        for char in owned_characters:
            roles = TeamService.classify_character_role(char.name)
            for role in roles:
                if role in char_by_role:
                    char_by_role[role].append(char)
        
        # チーム編成（重複を避ける）
        team = []
        used_names: Set[str] = set()
        
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
        
        # チームが4人未満の場合、残りのキャラから補充
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
    
    @staticmethod
    def validate_team_requirements(characters: List, min_chars: int = 4) -> Tuple[bool, Optional[str]]:
        """
        チーム編成に必要な条件を検証
        
        Args:
            characters: キャラクターのリスト
            min_chars: 最小必要人数
            
        Returns:
            Tuple[bool, str]: (有効フラグ, エラーメッセージ)
        """
        if not characters:
            return False, "キャラクターが見つかりませんでした"
        
        if len(characters) < min_chars:
            return False, f"チーム編成には最低{min_chars}人のキャラクターが必要です（現在: {len(characters)}人）"
        
        return True, None
