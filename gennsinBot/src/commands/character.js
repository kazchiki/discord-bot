const { EmbedBuilder } = require('discord.js');
const axios = require('axios');
const { characterNames } = require('../data/characters');
const { OPTION_NAMES } = require('../constants/commands');
const { saveUserCharacter, getUserUID } = require('../utils/userData');

async function handleCharacterCommand(interaction) {
    const uid = interaction.options.getString(OPTION_NAMES.UID);
    const characterId = interaction.options.getString(OPTION_NAMES.CHARACTER_ID);

    await showCharacterDetails(interaction, uid, characterId);
}

async function showCharacterDetails(interaction, uid, characterId) {
    try {
        await interaction.deferReply();

        const apiUrl = `https://enka.network/api/uid/${uid}/`;
        const response = await axios.get(apiUrl);
        const data = response.data;

        const characters = data.avatarInfoList || [];
        const character = characters.find(char => char.avatarId === characterId);

        if (!character) {
            await interaction.editReply('指定されたキャラクターが見つかりませんでした。');
            return;
        }

        const charName = characterNames[characterId] || `キャラID: ${characterId}`;
        const level = character.propMap['4001'] ? character.propMap['4001'].val : 'N/A';
        const constellation = character.propMap['4002'] ? character.propMap['4002'].val : '0';

        const embed = new EmbedBuilder()
            .setColor(0x00FF00)
            .setTitle(`${charName}の詳細情報`)
            .setDescription(`UID: ${uid}`)
            .addFields(
                { name: 'レベル', value: `${level}`, inline: true },
                { name: '命ノ星座', value: `${constellation}`, inline: true }
            );

        // 戦闘ステータス
        if (character.fightPropMap) {
            const stats = character.fightPropMap;
            embed.addFields(
                { name: 'HP', value: `${Math.round(stats['2000'] || 0)}`, inline: true },
                { name: '攻撃力', value: `${Math.round(stats['2001'] || 0)}`, inline: true },
                { name: '防御力', value: `${Math.round(stats['2002'] || 0)}`, inline: true },
                { name: '会心率', value: `${((stats['20'] || 0) * 100).toFixed(1)}%`, inline: true },
                { name: '会心ダメージ', value: `${((stats['22'] || 0) * 100).toFixed(1)}%`, inline: true },
                { name: '元素チャージ効率', value: `${((stats['23'] || 0) * 100).toFixed(1)}%`, inline: true }
            );
        }

        // 天賦レベル
        if (character.skillLevelMap) {
            const skillLevels = Object.values(character.skillLevelMap);
            embed.addFields({ name: '天賦レベル', value: skillLevels.join(' / '), inline: false });
        }

        // 聖遺物情報
        if (character.equipList) {
            const artifacts = character.equipList.filter(item => item.flat?.reliquaryMainstat);
            if (artifacts.length > 0) {
                const artifactInfo = artifacts.map(artifact => {
                    const setName = artifact.flat?.setNameTextMapHash || '不明';
                    const equipType = artifact.flat?.equipType || '不明';
                    const mainStat = artifact.flat?.reliquaryMainstat?.mainPropId || '不明';
                    const mainValue = artifact.flat?.reliquaryMainstat?.statValue || '不明';
                    const level = artifact.reliquary?.level || 0;

                    return `**${equipType}** (${setName})\n${mainStat}: ${mainValue}\n強化レベル: ${level}`;
                }).join('\n\n');

                embed.addFields({ name: '聖遺物', value: artifactInfo, inline: false });
            }
        }

        await interaction.editReply({ embeds: [embed] });

        // キャラクター情報を自動保存（エラーが発生しても処理は続行）
        try {
            const userId = interaction.user.id;
            const userUID = await getUserUID(userId);
            
            // 自分のUIDでキャラクター取得した場合のみ保存
            if (userUID === uid) {
                await saveUserCharacter(userId, uid, characterId, character, charName);
                console.log(`キャラクター情報を保存しました: ${charName} (ユーザー: ${interaction.user.username}, UID: ${uid})`);
            }
        } catch (saveError) {
            console.error('キャラクター情報の保存に失敗しました:', saveError);
            // 保存エラーはユーザーには表示しない（メイン機能に影響しないため）
        }

    } catch (error) {
        console.error(error);
        await interaction.editReply('キャラクター情報の取得中にエラーが発生しました。');
    }
}

module.exports = {
    handleCharacterCommand,
    showCharacterDetails
}; 