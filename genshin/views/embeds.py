# -*- coding: utf-8 -*-
"""
Embed生成ロジック
すべてのEmbed作成を一元管理
"""

import discord
from datetime import datetime
from config.constants import ColorConstants, ElementConstants


class EmbedBuilder:
    """Discord Embed生成クラス"""
    
    @staticmethod
    def success_embed(title: str, description: str) -> discord.Embed:
        """成功メッセージのEmbed"""
        return discord.Embed(
            title=f'✅ {title}',
            description=description,
            color=ColorConstants.SUCCESS_COLOR
        )
    
    @staticmethod
    def error_embed(title: str, description: str) -> discord.Embed:
        """エラーメッセージのEmbed"""
        return discord.Embed(
            title=f'❌ {title}',
            description=description,
            color=ColorConstants.ERROR_COLOR
        )
    
    @staticmethod
    def info_embed(title: str, description: str = None) -> discord.Embed:
        """情報メッセージのEmbed"""
        embed = discord.Embed(
            title=title,
            color=ColorConstants.INFO_COLOR
        )
        if description:
            embed.description = description
        return embed
    
    @staticmethod
    def warning_embed(title: str, description: str) -> discord.Embed:
        """警告メッセージのEmbed"""
        return discord.Embed(
            title=f'⚠️ {title}',
            description=description,
            color=ColorConstants.WARNING_COLOR
        )
    
    # === 樹脂関連のEmbed ===
    
    @staticmethod
    def resin_status_embed(notes) -> discord.Embed:
        """樹脂状況のEmbed"""
        from datetime import timedelta
        
        embed = discord.Embed(
            title='🔋 樹脂状況',
            color=ColorConstants.INFO_COLOR
        )
        
        # 樹脂回復時間
        if notes.current_resin < notes.max_resin:
            recovery_str = notes.resin_recovery_time.strftime('%Y/%m/%d %H:%M')
        else:
            recovery_str = '満タン！'
        
        embed.add_field(
            name='現在の樹脂',
            value=f'{notes.current_resin}/{notes.max_resin}',
            inline=True
        )
        
        embed.add_field(
            name='満タンまで',
            value=recovery_str,
            inline=True
        )
        
        # デイリー任務
        embed.add_field(
            name='デイリー任務',
            value=f'{notes.completed_commissions}/4 完了',
            inline=True
        )
        
        # 週ボス
        embed.add_field(
            name='週ボス割引',
            value=f'{notes.remaining_resin_discounts}/3 残り',
            inline=True
        )
        
        # 洞天宝銭
        if hasattr(notes, 'current_realm_currency'):
            embed.add_field(
                name='洞天宝銭',
                value=f'{notes.current_realm_currency}/{notes.max_realm_currency}',
                inline=True
            )
        
        # 参量物質変換器
        if hasattr(notes, 'transformer') and notes.transformer.obtained:
            try:
                if notes.transformer.recovery_time:
                    recovery_seconds = int(notes.transformer.recovery_time)
                    if recovery_seconds > 0:
                        transformer_time = datetime.now() + timedelta(seconds=recovery_seconds)
                        transformer_str = transformer_time.strftime('%H:%M')
                    else:
                        transformer_str = '使用可能'
                else:
                    transformer_str = '使用可能'
            except (ValueError, TypeError):
                transformer_str = '不明'
            
            embed.add_field(
                name='参量物質変換器',
                value=transformer_str,
                inline=True
            )
        
        embed.timestamp = discord.utils.utcnow()
        return embed
    
    @staticmethod
    def resin_calculation_embed(current: int, target: int, recovery_time: datetime) -> discord.Embed:
        """樹脂回復計算のEmbed"""
        from config.constants import ResinConstants
        
        resin_needed = target - current
        minutes_needed = resin_needed * ResinConstants.RESIN_RECOVERY_MINUTES
        
        embed = discord.Embed(
            title='樹脂回復計算',
            color=ColorConstants.INFO_COLOR
        )
        
        embed.add_field(
            name='現在の樹脂',
            value=f'{current}/{ResinConstants.MAX_RESIN}',
            inline=True
        )
        embed.add_field(
            name='目標樹脂',
            value=f'{target}/{ResinConstants.MAX_RESIN}',
            inline=True
        )
        embed.add_field(
            name='必要な樹脂',
            value=f'{resin_needed}',
            inline=True
        )
        
        embed.add_field(
            name='回復時間',
            value=f'{minutes_needed // 60}時間 {minutes_needed % 60}分',
            inline=True
        )
        
        embed.add_field(
            name='完了予定時刻',
            value=recovery_time.strftime('%Y/%m/%d %H:%M'),
            inline=True
        )
        
        embed.set_footer(text='樹脂は8分で1回復します')
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    @staticmethod
    def resin_reminder_embed(threshold: int, current_resin: int = None, max_resin: int = 200) -> discord.Embed:
        """樹脂リマインダーのEmbed"""
        embed = discord.Embed(
            title='🔔 樹脂リマインダー',
            color=ColorConstants.SUCCESS_COLOR
        )
        
        if current_resin is not None:
            embed.description = f'樹脂が{threshold}に達しました！'
            embed.add_field(
                name='現在の樹脂',
                value=f'{current_resin}/{max_resin}',
                inline=True
            )
        else:
            embed.description = f'樹脂が満タン（{threshold}）になりました！'
        
        embed.timestamp = discord.utils.utcnow()
        return embed
    
    @staticmethod
    def resin_notification_settings_embed(enabled: bool, threshold: int) -> discord.Embed:
        """樹脂通知設定のEmbed"""
        embed = discord.Embed(
            title='✅ 樹脂通知設定完了',
            color=ColorConstants.SUCCESS_COLOR if enabled else ColorConstants.ERROR_COLOR
        )
        
        if enabled:
            threshold_text = f'{threshold}' if threshold else '満タン（200）'
            embed.description = f'樹脂が{threshold_text}に達したときに通知します。'
            embed.add_field(name='チェック間隔', value='30分ごと', inline=True)
            embed.add_field(name='通知方法', value='DMで通知', inline=True)
        else:
            embed.description = '樹脂通知を無効にしました。'
        
        return embed
    
    # === HoYoLAB関連のEmbed ===
    
    @staticmethod
    def cookie_set_embed(accounts: list) -> discord.Embed:
        """クッキー設定完了のEmbed"""
        embed = discord.Embed(
            title='✅ クッキー設定完了',
            description='HoYoLABのクッキーが正常に設定され、暗号化して保存されました！',
            color=ColorConstants.SUCCESS_COLOR
        )
        
        if accounts:
            account_info = []
            for acc in accounts[:3]:  # 最大3つまで表示
                account_info.append(f'UID: {acc.uid} (AR{acc.level})')
            
            embed.add_field(
                name='原神アカウント',
                value='\n'.join(account_info),
                inline=False
            )
        
        return embed
    
    # === キャラクター関連のEmbed ===
    
    @staticmethod
    def characters_list_embed(characters: list, chars_by_element: dict, element_order: list) -> discord.Embed:
        """キャラクター一覧のEmbed"""
        from config.constants import CharacterNameMapping
        
        embed = discord.Embed(
            title='所持キャラクター',
            description=f'合計 {len(characters)}体',
            color=ColorConstants.FIVE_STAR_COLOR
        )
        
        element_names = ElementConstants.ELEMENT_NAMES
        
        for element in element_order:
            element_chars = chars_by_element.get(element, [])
            if not element_chars:
                continue
            
            # レアリティとレベルでソート
            sorted_chars = sorted(element_chars, key=lambda x: (x.rarity, x.level), reverse=True)
            
            char_list = []
            for char in sorted_chars[:20]:  # 各元素最大20体
                jp_name = CharacterNameMapping.NAMES.get(char.name, char.name)
                element_name = element_names[element]
                char_list.append(f'{jp_name} {element_name} Lv.{char.level}')
            
            if char_list:
                embed.add_field(
                    name=f'{element_names[element]} ({len(element_chars)}体)',
                    value='\n'.join(char_list),
                    inline=False
                )
        
        embed.set_footer(text='HoYoLAB APIより取得')
        embed.timestamp = discord.utils.utcnow()
        
        return embed
    
    # === チーム編成関連のEmbed ===
    
    @staticmethod
    def team_generator_embed(team: list, total_chars: int) -> discord.Embed:
        """チーム編成のEmbed"""
        from config.constants import CharacterNameMapping
        
        embed = discord.Embed(
            title='🎯 おすすめチーム編成',
            description=f'あなたの所持キャラ（{total_chars}人）から生成されたチーム編成です',
            color=ColorConstants.FIVE_STAR_COLOR
        )
        
        for i, (role, char) in enumerate(team, 1):
            element_name = ElementConstants.ELEMENT_NAMES.get(char.element, '不明')
            jp_name = CharacterNameMapping.NAMES.get(char.name, char.name)
            embed.add_field(
                name=f'{i}. {role}',
                value=f'{jp_name} {element_name}\nLv.{char.level}',
                inline=True
            )
        
        embed.add_field(
            name='💡 ヒント',
            value='気に入らない場合は、もう一度コマンドを実行して別の編成を試してください！',
            inline=False
        )
        
        embed.set_footer(text='HoYoLAB APIより取得')
        embed.timestamp = discord.utils.utcnow()
        
        return embed
