module.exports = {
  // Discord Bot設定
  TOKEN: process.env.TOKEN,
  
  // HTTPサーバー設定
  PORT: process.env.PORT || 3000,
  
  // 元素マッピング
  ELEMENTS: {
    1: '炎',
    2: '水',
    3: '風',
    4: '雷',
    5: '氷',
    6: '岩',
    7: '草'
  },
  
  // 性別マッピング
  GENDERS: {
    1: '男',
    2: '女'
  },
  
  // チーム設定
  CHARACTERS_PER_TEAM: 4,
  MAX_TEAMS: 20,
  
  // メッセージ送信間隔（ミリ秒）
  MESSAGE_INTERVAL: 500,
  TEAM_INTERVAL: 3000,
  
  // ボット終了遅延時間
  SHUTDOWN_DELAY: 2000
}; 