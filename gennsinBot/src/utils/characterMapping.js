const genshindb = require('genshin-db');

// 動的にgenshin-dbから全キャラクター名を取得
function getAllCharacterNames() {
    try {
        genshindb.setOptions({ resultLanguage: 'Japanese' });
        const allCharacters = genshindb.characters('names', { matchCategories: true });
        return allCharacters || [];
    } catch (error) {
        console.error('キャラクター名取得エラー:', error);
        return [];
    }
}

// 日本語名から英語名を検索
function findEnglishCharacterName(japaneseName) {
    try {
        // 日本語で検索
        genshindb.setOptions({ resultLanguage: 'Japanese' });
        const character = genshindb.characters(japaneseName);
        
        if (character) {
            // 英語名を取得
            genshindb.setOptions({ resultLanguage: 'English' });
            const englishCharacter = genshindb.characters(character.id);
            return englishCharacter?.name || null;
        }
        
        return null;
    } catch (error) {
        console.error('キャラクター名変換エラー:', error);
        return null;
    }
}

// あいまい検索（部分一致）
function searchCharacterName(query) {
    try {
        genshindb.setOptions({ resultLanguage: 'Japanese' });
        const allCharacters = genshindb.characters('names', { matchCategories: true });
        
        return allCharacters.filter(name => 
            name.includes(query) || 
            name.toLowerCase().includes(query.toLowerCase())
        ) || [];
    } catch (error) {
        console.error('キャラクター検索エラー:', error);
        return [];
    }
}

module.exports = {
    getAllCharacterNames,
    findEnglishCharacterName,
    searchCharacterName
}; 