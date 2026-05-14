#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
キャラクターデータのシードスクリプト
genshin/ ディレクトリから実行: python seed_characters.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import Database

# 英語名 → 日本語名
CHARACTERS = {
    # 星5 - モンド
    'Venti':              'ウェンティ',
    'Diluc':              'ディルック',
    'Jean':               'ジン',
    'Mona':               'モナ',
    'Klee':               'クレー',
    'Albedo':             'アルベド',
    'Eula':               'エウルア',
    'Varka':              'ファルカ',
    'Durin':              'ドゥリン',
    'Aloy':               'アーロイ',
    # 星5 - 璃月
    'Zhongli':            '鍾離',
    'Qiqi':               '七七',
    'Keqing':             '刻晴',
    'Ganyu':              '甘雨',
    'Hu Tao':             '胡桃',
    'Xiao':               '魈',
    'Shenhe':             '申鶴',
    'Yelan':              '夜蘭',
    'Baizhu':             '白朮',
    'Xianyun':            '閑雲',
    'Zibai':              '兹白',
    # 星5 - 稲妻
    'Raiden Shogun':      '雷電将軍',
    'Kaedehara Kazuha':   '楓原万葉',
    'Yoimiya':            '宵宮',
    'Kamisato Ayaka':     '神里綾華',
    'Kamisato Ayato':     '神里綾人',
    'Sangonomiya Kokomi': '珊瑚宮心海',
    'Yae Miko':           '八重神子',
    'Arataki Itto':       '荒瀧一斗',
    'Chiori':             '千織',
    'Yumemizuki Mizuki':  '夢見月瑞希',
    # 星5 - スメール
    'Nahida':             'ナヒーダ',
    'Tighnari':           'ティナリ',
    'Dehya':              'ディシア',
    'Nilou':              'ニィロウ',
    'Alhaitham':          'アルハイゼン',
    'Cyno':               'セノ',
    'Wanderer':           '放浪者',
    # 星5 - フォンテーヌ
    'Furina':             'フリーナ',
    'Lyney':              'リネ',
    'Neuvillette':        'ヌヴィレット',
    'Wriothesley':        'リオセスリ',
    'Navia':              'ナヴィア',
    'Clorinde':           'クロリンデ',
    'Sigewinne':          'シグウィン',
    'Emilie':             'エミリエ',
    'Escoffier':          'エスコフィエ',
    # 星5 - ナタ
    'Mavuika':            'マーヴィカ',
    'Mualani':            'ムアラニ',
    'Kinich':             'キイニチ',
    'Xilonen':            'シロネン',
    'Citlali':            'シトラリ',
    'Chasca':             'チャスカ',
    'Varesa':             'ヴァレサ',
    # 星5 - ナド・クライ
    'Columbina':          'コロンビーナ',
    'Ineffa':             'イネファ',
    'Nefer':              'ネフェル',
    'Flins':              'フリンズ',
    'Lauma':              'ラウマ',
    'Linnea':             'リンネア',
    # 星5 - スネージナヤ
    'Tartaglia':          'タルタリヤ',
    'Arlecchino':         'アルレッキーノ',
    # 星5 - 分類なし
    'Skirk':              'スカーク',
    'Manekina':           'マネキン(女)',
    'Manekin':            'マネキン(男)',
    # 星4 - モンド
    'Amber':              'アンバー',
    'Kaeya':              'ガイア',
    'Lisa':               'リサ',
    'Barbara':            'バーバラ',
    'Razor':              'レザー',
    'Fischl':             'フィッシュル',
    'Bennett':            'ベネット',
    'Noelle':             'ノエル',
    'Rosaria':            'ロサリア',
    'Diona':              'ディオナ',
    'Sucrose':            'スクロース',
    'Mika':               'ミカ',
    'Dahlia':             'ダリア',
    # 星4 - 璃月
    'Xingqiu':            '行秋',
    'Xiangling':          '香菱',
    'Chongyun':           '重雲',
    'Yanfei':             '煙緋',
    'Ningguang':          '凝光',
    'Xinyan':             '辛炎',
    'Beidou':             '北斗',
    'Yun Jin':            '雲菫',
    'Yaoyao':             'ヨォーヨ',
    'Gaming':             '嘉明',
    'Lan Yan':            '藍硯',
    # 星4 - 稲妻
    'Thoma':              'トーマ',
    'Kujou Sara':         '九条裟羅',
    'Sayu':               '早柚',
    'Kuki Shinobu':       '久岐忍',
    'Gorou':              'ゴロー',
    'Kirara':             '綺良々',
    'Shikanoin Heizou':   '鹿野院平蔵',
    # 星4 - スメール
    'Collei':             'コレイ',
    'Faruzan':            'ファルザン',
    'Dori':               'ドリー',
    'Layla':              'レイラ',
    'Candace':            'キャンディス',
    'Kaveh':              'カーヴェ',
    'Sethos':             'セトス',
    # 星4 - フォンテーヌ
    'Lynette':            'リネット',
    'Freminet':           'フレミネ',
    'Charlotte':          'シャルロット',
    'Chevreuse':          'シュヴルーズ',
    # 星4 - ナタ
    'Kachina':            'カチーナ',
    'Ororon':             'オロルン',
    'Iansan':             'イアンサ',
    'Ifa':                'イファ',
    # 星4 - ナド・クライ
    'Aino':               'アイノ',
    'Jahoda':             'ヤフォダ',
    'Illuga':             'イルーガ',
    # 主人公
    'Traveler':           '旅人',
    'Aether':             '空',
    'Lumine':             '蛍',
}

# キャラ名 → ロールのリスト（複数ロール対応）
CHARACTER_ROLES: dict[str, list[str]] = {
    # dps のみ
    'Klee':               ['dps'],
    'Eula':               ['dps'],
    'Diluc':              ['dps'],
    'Noelle':             ['dps', 'shielder'],
    'Gaming':             ['dps'],
    'Hu Tao':             ['dps'],
    'Ganyu':              ['dps'],
    'Tartaglia':          ['dps'],
    'Xiao':               ['dps'],
    'Ningguang':          ['dps'],
    'Keqing':             ['dps'],
    'Yanfei':             ['dps'],
    'Kamisato Ayato':     ['dps'],
    'Kamisato Ayaka':     ['dps'],
    'Arataki Itto':       ['dps'],
    'Yoimiya':            ['dps'],
    'Alhaitham':          ['dps'],
    'Wanderer':           ['dps'],
    'Sethos':             ['dps'],
    'Cyno':               ['dps'],
    'Tighnari':           ['dps'],
    'Arlecchino':         ['dps'],
    'Neuvillette':        ['dps'],
    'Lyney':              ['dps'],
    'Navia':              ['dps'],
    'Clorinde':           ['dps'],
    'Wriothesley':        ['dps'],
    'Traveler':           ['dps'],
    'Mavuika':            ['dps'],
    'Skirk':              ['dps'],
    'Mualani':            ['dps'],
    'Varesa':             ['dps'],
    'Kinich':             ['dps'],
    'Chasca':             ['dps'],
    'Nefer':              ['dps'],
    'Flins':              ['dps'],
    'Columbina':          ['dps'],
    'Manekina':           ['dps'],
    'Manekin':            ['dps'],
    'Varka':              ['dps'],
    'Zibai':              ['dps'],
    # dps + support
    'Venti':              ['dps', 'support'],
    'Raiden Shogun':      ['dps', 'support'],
    # sub_dps のみ
    'Durin':              ['sub_dps'],
    'Xingqiu':            ['sub_dps'],
    'Xiangling':          ['sub_dps'],
    'Fischl':             ['sub_dps'],
    'Beidou':             ['sub_dps'],
    'Rosaria':            ['sub_dps'],
    'Chongyun':           ['sub_dps'],
    'Yae Miko':           ['sub_dps'],
    'Yelan':              ['sub_dps'],
    'Albedo':             ['sub_dps'],
    'Furina':             ['sub_dps'],
    'Emilie':             ['sub_dps'],
    'Shikanoin Heizou':   ['sub_dps'],
    'Xinyan':             ['sub_dps'],
    'Kachina':            ['sub_dps'],
    'Nilou':              ['sub_dps'],
    'Chiori':             ['sub_dps'],
    'Dori':               ['sub_dps'],
    'Ifa':                ['sub_dps'],
    'Aino':               ['sub_dps'],
    'Dahlia':             ['sub_dps'],
    'Jahoda':             ['sub_dps'],
    'Lauma':              ['sub_dps'],
    'Ineffa':             ['sub_dps'],
    # support のみ
    'Bennett':            ['support'],
    'Kaedehara Kazuha':   ['support'],
    'Sucrose':            ['support'],
    'Zhongli':            ['shielder', 'support'],
    'Nahida':             ['support'],
    'Faruzan':            ['support'],
    'Layla':              ['shielder'],
    'Yun Jin':            ['support'],
    'Gorou':              ['support'],
    'Kujou Sara':         ['support'],
    'Thoma':              ['shielder', 'support'],
    'Candace':            ['support'],
    'Kaveh':              ['support'],
    'Lynette':            ['support'],
    'Freminet':           ['support'],
    'Chevreuse':          ['support'],
    'Ororon':             ['support'],
    'Mika':               ['support'],
    'Lan Yan':            ['support'],
    'Kirara':             ['shielder', 'support'],
    'Yumemizuki Mizuki':  ['support'],
    'Xilonen':            ['support'],
    'Citlali':            ['support'],
    'Xianyun':            ['support'],
    'Kuki Shinobu':       ['support'],
    'Iansan':             ['support'],
    # healer のみ
    'Diona':              ['shielder', 'healer'],
    'Jean':               ['healer'],
    'Sangonomiya Kokomi': ['healer'],
    'Barbara':            ['healer'],
    'Qiqi':               ['healer'],
    'Sayu':               ['healer'],
    'Yaoyao':             ['healer'],
    'Baizhu':             ['healer'],
    'Charlotte':          ['healer'],
    'Sigewinne':          ['healer'],
    # support のみ（shielder以外）
    'Linnea':             ['support'],
    'Illuga':             ['support'],
}

# 誕生日 (MM/DD) ※未入力のキャラはNULL
BIRTHDAYS: dict[str, str] = {
    # 1月
    'Wanderer':           '01/03',
    'Jahoda':             '01/05',
    'Lan Yan':            '01/06',
    'Thoma':              '01/09',
    'Chevreuse':          '01/10',
    'Columbina':          '01/14',
    'Diona':              '01/18',
    'Citlali':            '01/20',
    'Kirara':             '01/22',
    'Rosaria':            '01/24',
    # 2月
    'Lyney':              '02/02',
    'Lynette':            '02/02',
    'Alhaitham':          '02/11',
    'Beidou':             '02/14',
    'Varka':              '02/17',
    'Sangonomiya Kokomi': '02/22',
    'Bennett':            '02/29',
    # 3月
    'Lauma':              '03/01',
    'Qiqi':               '03/03',
    'Yaoyao':             '03/06',
    'Shenhe':             '03/10',
    'Xilonen':            '03/13',
    'Durin':              '03/14',
    'Jean':               '03/14',
    'Yumemizuki Mizuki':  '03/16',
    'Noelle':             '03/21',
    'Ifa':                '03/23',
    'Kamisato Ayato':     '03/26',
    'Sigewinne':          '03/30',
    # 4月
    'Ineffa':             '04/02',
    'Aloy':               '04/04',
    'Dehya':              '04/07',
    'Charlotte':          '04/10',
    'Xianyun':            '04/11',
    'Xiao':               '04/17',
    'Yelan':              '04/20',
    'Kachina':            '04/22',
    'Baizhu':             '04/25',
    'Diluc':              '04/30',
    # 5月
    'Candace':            '05/03',
    'Collei':             '05/08',
    'Nefer':              '05/09',
    'Zibai':              '05/15',
    'Gorou':              '05/18',
    'Yun Jin':            '05/21',
    'Linnea':             '05/23',
    'Dahlia':             '05/25',
    'Fischl':             '05/27',
    'Sethos':             '05/31',
    # 6月
    'Arataki Itto':       '06/01',
    'Escoffier':          '06/08',
    'Lisa':               '06/09',
    'Venti':              '06/16',
    'Yoimiya':            '06/21',
    'Cyno':               '06/23',
    'Raiden Shogun':      '06/26',
    'Yae Miko':           '06/27',
    # 7月
    'Barbara':            '07/05',
    'Kaveh':              '07/09',
    'Kujou Sara':         '07/14',
    'Hu Tao':             '07/15',
    'Tartaglia':          '07/20',
    'Shikanoin Heizou':   '07/24',
    'Klee':               '07/27',
    'Kuki Shinobu':       '07/27',
    'Yanfei':             '07/28',
    # 8月
    'Mualani':            '08/03',
    'Iansan':             '08/08',
    'Amber':              '08/10',
    'Mika':               '08/11',
    'Navia':              '08/16',
    'Chiori':             '08/17',
    'Faruzan':            '08/20',
    'Arlecchino':         '08/22',
    'Ningguang':          '08/26',
    'Mavuika':            '08/28',
    'Mona':               '08/31',
    # 9月
    'Chongyun':           '09/07',
    'Razor':              '09/09',
    'Albedo':             '09/13',
    'Clorinde':           '09/20',
    'Aino':               '09/21',
    'Emilie':             '09/22',
    'Freminet':           '09/24',
    'Kamisato Ayaka':     '09/28',
    # 10月
    'Xingqiu':            '10/09',
    'Furina':             '10/13',
    'Ororon':             '10/14',
    'Xinyan':             '10/16',
    'Sayu':               '10/19',
    'Eula':               '10/25',
    'Nahida':             '10/27',
    'Kaedehara Kazuha':   '10/29',
    'Flins':              '10/31',
    # 11月
    'Xiangling':          '11/02',
    'Skirk':              '11/05',
    'Kinich':             '11/11',
    'Varesa':             '11/15',
    'Keqing':             '11/20',
    'Wriothesley':        '11/23',
    'Sucrose':            '11/26',
    'Kaeya':              '11/30',
    # 12月
    'Ganyu':              '12/02',
    'Nilou':              '12/03',
    'Chasca':             '12/10',
    'Neuvillette':        '12/18',
    'Layla':              '12/19',
    'Dori':               '12/21',
    'Gaming':             '12/22',
    'Illuga':             '12/23',
    'Tighnari':           '12/29',
    'Zhongli':            '12/31',
}

# 実装日 (YYYY-MM-DD) ※不明なキャラはNULL
RELEASE_DATES: dict[str, str] = {
    # Ver 1.0 (2020-09-28)
    'Venti':              '2020-09-28',
    'Diluc':              '2020-09-28',
    'Jean':               '2020-09-28',
    'Mona':               '2020-09-28',
    'Amber':              '2020-09-28',
    'Kaeya':              '2020-09-28',
    'Lisa':               '2020-09-28',
    'Barbara':            '2020-09-28',
    'Razor':              '2020-09-28',
    'Fischl':             '2020-09-28',
    'Bennett':            '2020-09-28',
    'Noelle':             '2020-09-28',
    'Sucrose':            '2020-09-28',
    'Beidou':             '2020-09-28',
    'Xiangling':          '2020-09-28',
    'Xingqiu':            '2020-09-28',
    'Qiqi':               '2020-09-28',
    'Keqing':             '2020-09-28',
    'Ningguang':          '2020-09-28',
    'Chongyun':           '2020-09-28',
    'Traveler':           '2020-09-28',
    'Aether':             '2020-09-28',
    'Lumine':             '2020-09-28',
    'Klee':               '2020-10-20',
    # Ver 1.1 (2020-11-11)
    'Tartaglia':          '2020-11-11',
    'Diona':              '2020-11-11',
    'Zhongli':            '2020-12-01',
    'Xinyan':             '2020-12-01',
    # Ver 1.2 (2020-12-23)
    'Albedo':             '2020-12-23',
    'Ganyu':              '2021-01-12',
    # Ver 1.3 (2021-02-03)
    'Xiao':               '2021-02-03',
    'Hu Tao':             '2021-03-02',
    # Ver 1.4 (2021-03-17)
    'Rosaria':            '2021-04-06',
    # Ver 1.5 (2021-04-28)
    'Yanfei':             '2021-04-28',
    'Eula':               '2021-05-18',
    # Ver 1.6 (2021-06-09)
    'Kaedehara Kazuha':   '2021-06-09',
    # Ver 2.0 (2021-07-21)
    'Kamisato Ayaka':     '2021-07-21',
    'Yoimiya':            '2021-08-10',
    'Sayu':               '2021-08-10',
    # Ver 2.1 (2021-09-01)
    'Raiden Shogun':      '2021-09-01',
    'Kujou Sara':         '2021-09-01',
    'Aloy':               '2021-09-01',
    'Sangonomiya Kokomi': '2021-09-21',
    # Ver 2.2 (2021-10-13)
    'Thoma':              '2021-11-02',
    # Ver 2.3 (2021-11-24)
    'Arataki Itto':       '2021-11-24',
    'Gorou':              '2021-11-24',
    # Ver 2.4 (2022-01-05)
    'Shenhe':             '2022-01-05',
    'Yun Jin':            '2022-01-05',
    # Ver 2.5 (2022-02-16)
    'Yae Miko':           '2022-02-16',
    # Ver 2.6 (2022-03-30)
    'Kamisato Ayato':     '2022-03-30',
    # Ver 2.7 (2022-05-31)
    'Yelan':              '2022-05-31',
    'Kuki Shinobu':       '2022-06-21',
    # Ver 2.8 (2022-07-13)
    'Shikanoin Heizou':   '2022-07-13',
    # Ver 3.0 (2022-08-24)
    'Tighnari':           '2022-08-24',
    'Collei':             '2022-08-24',
    'Dori':               '2022-09-09',
    # Ver 3.1 (2022-09-28)
    'Cyno':               '2022-09-28',
    'Candace':            '2022-09-28',
    'Nilou':              '2022-10-14',
    # Ver 3.2 (2022-11-02)
    'Nahida':             '2022-11-02',
    'Layla':              '2022-11-02',
    # Ver 3.3 (2022-12-07)
    'Wanderer':           '2022-12-07',
    'Faruzan':            '2022-12-07',
    # Ver 3.4 (2023-01-18)
    'Alhaitham':          '2023-01-18',
    'Yaoyao':             '2023-01-18',
    # Ver 3.5 (2023-03-01)
    'Dehya':              '2023-03-01',
    'Mika':               '2023-03-21',
    # Ver 3.6 (2023-04-12)
    'Baizhu':             '2023-05-02',
    'Kaveh':              '2023-05-02',
    # Ver 3.7 (2023-05-24)
    'Kirara':             '2023-05-24',
    # Ver 4.0 (2023-08-16)
    'Lyney':              '2023-08-16',
    'Lynette':            '2023-08-16',
    'Freminet':           '2023-09-05',
    # Ver 4.1 (2023-09-27)
    'Neuvillette':        '2023-09-27',
    'Wriothesley':        '2023-10-17',
    # Ver 4.2 (2023-11-08)
    'Furina':             '2023-11-08',
    'Charlotte':          '2023-11-08',
    # Ver 4.3 (2023-12-20)
    'Navia':              '2023-12-20',
    'Chevreuse':          '2024-01-09',
    # Ver 4.4 (2024-01-31)
    'Xianyun':            '2024-01-31',
    'Gaming':             '2024-01-31',
    # Ver 4.5 (2024-03-13)
    'Chiori':             '2024-03-13',
    # Ver 4.6 (2024-04-24)
    'Arlecchino':         '2024-04-24',
    # Ver 4.7 (2024-06-05)
    'Clorinde':           '2024-06-05',
    'Sethos':             '2024-06-05',
    'Sigewinne':          '2024-07-01',
    # Ver 4.8 (2024-07-17)
    'Emilie':             '2024-08-06',
    # Ver 5.0 (2024-08-28)
    'Mualani':            '2024-08-28',
    'Kachina':            '2024-08-28',
    'Kinich':             '2024-09-17',
    # Ver 5.1 (2024-10-09)
    'Xilonen':            '2024-10-09',
    # Ver 5.2 (2024-11-20)
    'Chasca':             '2024-11-20',
    'Ororon':             '2024-11-20',
    # Ver 5.3 (2025-01-01)
    'Citlali':            '2025-01-01',
    'Lan Yan':            '2025-01-01',
    # Ver 5.4 (2025-02-12)
    'Mavuika':            '2025-02-12',
    'Yumemizuki Mizuki':  '2025-02-12',
    'Iansan':             '2025-03-26',
    # Ver 5.5 (2025-03-26)
    'Varesa':             '2025-03-26',
    # Ver 5.6 (2025-05-07)
    'Escoffier':          '2025-05-07',
    'Ifa':                '2025-05-07',
    # Ver 5.7 (2025-06-18)
    'Skirk':              '2025-06-18',
    'Dahlia':             '2025-06-18',
    # Ver 5.8 (2025-07-30)
    'Ineffa':             '2025-07-30',
    # Ver 5.9 (2025-09-10)
    'Lauma':              '2025-09-10',
    'Aino':               '2025-09-10',
    # Ver 6.0 (2025-10-22)
    'Flins':              '2025-10-01',
    'Nefer':              '2025-10-22',
    # Ver 6.1 (2025-12-03)
    'Durin':              '2025-12-03',
    'Jahoda':             '2025-12-03',
    # Ver 6.2 (2026-01-14)
    'Columbina':          '2026-01-14',
    # Ver 6.3 Phase2 / Luna IV (2026-02-03)
    'Zibai':              '2026-02-03',
    'Illuga':             '2026-02-03',
    # Ver 6.4 (2026-02-25)
    'Varka':              '2026-02-25',
    # Ver 6.5 (2026-04-08)
    'Linnea':             '2026-04-08',
}


def seed():
    db = Database()

    char_count = 0
    role_count = 0

    for name, japanese_name in CHARACTERS.items():
        if db.upsert_character(
            name,
            japanese_name,
            birthday=BIRTHDAYS.get(name),
            release_date=RELEASE_DATES.get(name),
        ):
            char_count += 1

    for name, roles in CHARACTER_ROLES.items():
        if name not in CHARACTERS:
            print(f"  警告: {name} は CHARACTERS に未登録です。スキップします。")
            continue
        for role in roles:
            if db.upsert_character_role(name, role):
                role_count += 1

    print(f"完了: キャラクター {char_count} 件、ロール {role_count} 件を登録しました")


if __name__ == '__main__':
    seed()