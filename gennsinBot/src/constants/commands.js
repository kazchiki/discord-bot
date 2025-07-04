// コマンド関連の定数
const COMMAND_NAMES = {
    GENSHIN: 'genshin',
    CHARACTER: 'character',
    REGISTER: 'register-uid',
    MY_INFO: 'my-genshin',
    MY_CHARACTERS: 'my-characters',
    MY_CHARACTER: 'my-character',
    MY_ACCOUNTS: 'my-accounts',
    SWITCH_UID: 'switch-uid',
    MY_CHARACTER_BUILD: 'my-character-build'
};

const COMMAND_DESCRIPTIONS = {
    GENSHIN: '原神のプレイヤー情報を取得します',
    CHARACTER: 'キャラクターの詳細情報を取得します',
    REGISTER: 'あなたのUIDを登録・更新します',
    MY_INFO: '登録済みのUIDで原神情報を表示します',
    MY_CHARACTERS: '保存されたキャラクターをセレクトメニューで表示し詳細確認できます',
    MY_CHARACTER: 'セレクトメニューまたは名前指定でキャラクター詳細を表示します',
    MY_ACCOUNTS: '登録済みのアカウント一覧を表示します',
    SWITCH_UID: 'アクティブなUIDを切り替えます',
    MY_CHARACTER_BUILD: 'あなたのキャラクターから選択して育成計画を立てます'
};

const OPTION_NAMES = {
    UID: 'uid',
    CHARACTER_ID: 'character_id',
    CHARACTER_NAME: 'character_name',
    NICKNAME: 'nickname',
    CURRENT_LEVEL: 'current_level',
    TARGET_LEVEL: 'target_level',
    TALENT_TYPE: 'talent_type'
};

const OPTION_DESCRIPTIONS = {
    UID: 'プレイヤーのUID',
    CHARACTER_ID: 'キャラクターID',
    CHARACTER_NAME: 'キャラクター名',
    NICKNAME: 'ニックネーム（オプション）',
    CURRENT_LEVEL: '現在のレベル',
    TARGET_LEVEL: '目標レベル',
    TALENT_TYPE: '天賦の種類（normal/skill/burst）'
};

module.exports = {
    COMMAND_NAMES,
    COMMAND_DESCRIPTIONS,
    OPTION_NAMES,
    OPTION_DESCRIPTIONS
}; 