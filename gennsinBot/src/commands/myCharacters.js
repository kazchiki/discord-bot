const {
    EmbedBuilder,
    ActionRowBuilder,
    StringSelectMenuBuilder,
    StringSelectMenuOptionBuilder,
    ComponentType
} = require('discord.js');
const { getUserCharacters } = require('../utils/userData');
const { OPTION_NAMES } = require('../constants/commands');

// 保存されたキャラクター一覧をセレクトメニューで表示
async function handleMyCharactersCommand(interaction) {
    const userId = interaction.user.id;

    try {
        await interaction.deferReply({ ephemeral: true });

        const savedCharacters = await getUserCharacters(userId);

        if (!savedCharacters || Object.keys(savedCharacters).length === 0) {
            const embed = new EmbedBuilder()
                .setColor(0xFFFF00)
                .setTitle('📋 保存されたキャラクター')
                .setDescription('まだキャラクター情報が保存されていません。\n\n' +
                    '💡 **キャラクター情報の保存方法:**\n' +
                    '1. `/register-uid` でUIDを登録\n' +
                    '2. `/character` コマンドで自分のキャラクター詳細を表示\n' +
                    '→ 自動的に保存されます！')
                .setFooter({ text: `${interaction.user.username}` })
                .setTimestamp();

            await interaction.editReply({ embeds: [embed] });
            return;
        }

        // セレクトメニューのオプションを作成
        const characters = Object.entries(savedCharacters);
        const options = characters.slice(0, 25).map(([characterId, data]) => {
            const level = data.data.propMap['4001']?.val || '不明';
            const constellation = data.data.propMap['1002']?.val || '0';
            const lastUpdated = new Date(data.lastUpdated).toLocaleDateString('ja-JP');
            
            return new StringSelectMenuOptionBuilder()
                .setLabel(data.characterName)
                .setDescription(`レベル ${level} | コンス ${constellation} | 更新: ${lastUpdated}`)
                .setValue(characterId);
        });

        const selectMenu = new StringSelectMenuBuilder()
            .setCustomId('character_detail_select')
            .setPlaceholder('詳細を見るキャラクターを選択してください')
            .addOptions(options);

        const row = new ActionRowBuilder().addComponents(selectMenu);

        const embed = new EmbedBuilder()
            .setColor(0x0099FF)
            .setTitle('📋 保存されたキャラクター一覧')
            .setDescription('**下のメニューからキャラクターを選択**して詳細情報を表示できます。')
            .addFields({
                name: '📊 保存データ概要',
                value: `🎭 **合計:** ${characters.length}体のキャラクター\n🔄 **最新更新:** ${new Date(Math.max(...characters.map(([_, data]) => new Date(data.lastUpdated).getTime()))).toLocaleDateString('ja-JP')}`,
                inline: false
            })
            .setFooter({ text: `${interaction.user.username} | キャラクターを選択して詳細表示` })
            .setTimestamp();

        const response = await interaction.editReply({ embeds: [embed], components: [row] });

        // セレクトメニューの応答を待機
        try {
            const selectInteraction = await response.awaitMessageComponent({
                componentType: ComponentType.StringSelect,
                time: 60000,
                filter: (i) => i.user.id === interaction.user.id
            });

            const selectedCharacterId = selectInteraction.values[0];
            const selectedCharacter = savedCharacters[selectedCharacterId];
            
            await selectInteraction.deferUpdate();
            
            // 選択されたキャラクターの詳細を表示
            await displaySavedCharacterDetails(selectInteraction, selectedCharacter.data, selectedCharacter.characterName, selectedCharacter.lastUpdated);

        } catch (error) {
            console.error('セレクトメニュー応答エラー:', error);
            const timeoutEmbed = new EmbedBuilder()
                .setTitle('⏰ 時間切れ')
                .setDescription('キャラクター選択がタイムアウトしました。もう一度コマンドを実行してください。')
                .setColor('#FF4444');
            
            await interaction.editReply({ embeds: [timeoutEmbed], components: [] });
        }

    } catch (error) {
        console.error('保存されたキャラクター一覧取得エラー:', error);
        await interaction.editReply('❌ キャラクター一覧の取得中にエラーが発生しました。');
    }
}

// キャラクター選択メニューを表示（my-character用）
async function showMyCharacterSelectMenu(interaction, savedCharacters) {
    // セレクトメニューのオプションを作成
    const characters = Object.entries(savedCharacters);
    const options = characters.slice(0, 25).map(([characterId, character]) => {
        const level = character.data.propMap['4001']?.val || '不明';
        const constellation = character.data.propMap['1002']?.val || '0';
        const lastUpdated = new Date(character.lastUpdated).toLocaleDateString('ja-JP');
        
        return new StringSelectMenuOptionBuilder()
            .setLabel(character.characterName)
            .setDescription(`レベル ${level} | コンス ${constellation} | 更新: ${lastUpdated}`)
            .setValue(characterId);
    });

    const selectMenu = new StringSelectMenuBuilder()
        .setCustomId('my_character_select')
        .setPlaceholder('詳細を表示するキャラクターを選択してください')
        .addOptions(options);

    const row = new ActionRowBuilder().addComponents(selectMenu);

    const embed = new EmbedBuilder()
        .setColor(0x9932CC)
        .setTitle('🎭 キャラクター詳細表示')
        .setDescription('**詳細情報を見たいキャラクターを選択**してください。')
        .addFields({
            name: '📊 保存キャラクター数',
            value: `${characters.length}体のキャラクターが保存されています`,
            inline: true
        })
        .setFooter({ text: 'キャラクターを選択すると詳細情報が表示されます' });

    const response = await interaction.editReply({ embeds: [embed], components: [row] });

    // セレクトメニューの応答を待機
    try {
        const selectInteraction = await response.awaitMessageComponent({
            componentType: ComponentType.StringSelect,
            time: 60000,
            filter: (i) => i.user.id === interaction.user.id
        });

        const selectedCharacterId = selectInteraction.values[0];
        const selectedCharacter = savedCharacters[selectedCharacterId];
        
        await selectInteraction.deferUpdate();
        
        // 選択されたキャラクターの詳細を表示
        await displaySavedCharacterDetails(selectInteraction, selectedCharacter.data, selectedCharacter.characterName, selectedCharacter.lastUpdated);

    } catch (error) {
        console.error('セレクトメニュー応答エラー:', error);
        const timeoutEmbed = new EmbedBuilder()
            .setTitle('⏰ 時間切れ')
            .setDescription('キャラクター選択がタイムアウトしました。もう一度コマンドを実行してください。')
            .setColor('#FF4444');
        
        await interaction.editReply({ embeds: [timeoutEmbed], components: [] });
    }
}

// 特定の保存されたキャラクター詳細を表示
async function handleMyCharacterCommand(interaction) {
    const userId = interaction.user.id;
    const characterName = interaction.options.getString(OPTION_NAMES.CHARACTER_NAME);

    try {
        await interaction.deferReply({ ephemeral: true });

        const savedCharacters = await getUserCharacters(userId);

        if (!savedCharacters || Object.keys(savedCharacters).length === 0) {
            const embed = new EmbedBuilder()
                .setColor(0xFFFF00)
                .setTitle('📋 保存されたキャラクター')
                .setDescription('まだキャラクター情報が保存されていません。\n\n' +
                    '💡 **キャラクター情報の保存方法:**\n' +
                    '1. `/register-uid` でUIDを登録\n' +
                    '2. `/character` コマンドで自分のキャラクター詳細を表示\n' +
                    '→ 自動的に保存されます！')
                .setFooter({ text: `${interaction.user.username}` })
                .setTimestamp();

            await interaction.editReply({ embeds: [embed] });
            return;
        }

        // キャラクター名が指定されていない場合はセレクトメニューを表示
        if (!characterName) {
            await showMyCharacterSelectMenu(interaction, savedCharacters);
            return;
        }

        // キャラクター名で検索（従来の手入力方式）
        const characterEntry = Object.entries(savedCharacters)
            .find(([_, data]) => data.characterName.includes(characterName));

        if (!characterEntry) {
            const availableNames = Object.values(savedCharacters)
                .map(data => data.characterName)
                .join('\n・');
            
            await interaction.editReply(`❌ 「${characterName}」に一致するキャラクターが見つかりませんでした。\n\n` +
                `**保存されたキャラクター:**\n・${availableNames}\n\n` +
                `💡 キャラクター名を省略すると選択メニューが表示されます。`);
            return;
        }

        const [characterId, savedData] = characterEntry;
        const character = savedData.data;
        const charName = savedData.characterName;

        // キャラクター詳細を表示
        await displaySavedCharacterDetails(interaction, character, charName, savedData.lastUpdated);

    } catch (error) {
        console.error('保存されたキャラクター詳細取得エラー:', error);
        await interaction.editReply('❌ キャラクター詳細の取得中にエラーが発生しました。');
    }
}

// 保存されたキャラクター詳細の表示ロジック
async function displaySavedCharacterDetails(interaction, character, charName, lastUpdated) {
    const level = character.propMap['4001'] ? character.propMap['4001'].val : 'N/A';
    const constellation = character.propMap['4002'] ? character.propMap['4002'].val : '0';

    const embed = new EmbedBuilder()
        .setColor(0x9932CC) // 保存データは紫色で区別
        .setTitle(`💾 ${charName}の保存データ`)
        .setDescription(`最終更新: ${new Date(lastUpdated).toLocaleString('ja-JP')}`)
        .addFields(
            { name: 'レベル', value: `${level}`, inline: true },
            { name: '命ノ星座', value: `${constellation}`, inline: true },
            { name: '　', value: '　', inline: true } // スペーサー
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

    // 聖遺物情報（簡略版）
    if (character.equipList) {
        const artifacts = character.equipList.filter(item => item.flat?.reliquaryMainstat);
        if (artifacts.length > 0) {
            const artifactSummary = `聖遺物装備数: ${artifacts.length}個`;
            embed.addFields({ name: '聖遺物', value: artifactSummary, inline: false });
        }
    }

    embed.addFields({
        name: '🔄 最新情報を取得',
        value: '最新の情報を確認するには `/character` コマンドを使用してください。',
        inline: false
    });

    await interaction.editReply({ embeds: [embed] });
}

module.exports = {
    handleMyCharactersCommand,
    handleMyCharacterCommand
}; 