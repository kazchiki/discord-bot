const { 
    EmbedBuilder, 
    ActionRowBuilder, 
    ButtonBuilder, 
    ButtonStyle, 
    StringSelectMenuBuilder, 
    StringSelectMenuOptionBuilder, 
    ComponentType
} = require('discord.js');
const { calculateBuildCost, calculateTalentCost, calculateFullBuildCost } = require('../utils/buildCalculator');
const { getUserCharacters } = require('../utils/userData');
const { findEnglishCharacterName } = require('../utils/characterMapping');
const { OPTION_NAMES } = require('../constants/commands');

// モラをフォーマットする関数
function formatMora(mora) {
    return mora.toLocaleString('ja-JP');
}

// レアリティに応じた絵文字を取得
function getRarityEmoji(rarity) {
    const rarityEmojis = {
        1: '⚪',
        2: '🟢', 
        3: '🔵',
        4: '🟣',
        5: '🟡'
    };
    return rarityEmojis[rarity] || '⚪';
}

// キャラクター名からキャラクターIDを検索（保存データ用）
function findCharacterIdByName(characterName, userCharacters) {
    for (const [characterId, savedCharacter] of Object.entries(userCharacters)) {
        if (savedCharacter.characterName.includes(characterName) || 
            characterName.includes(savedCharacter.characterName)) {
            return characterId;
        }
    }
    return null;
}

// 育成コスト詳細を表示
async function showBuildCostDetails(interaction, savedCharacter, targetLevel) {
    const currentLevel = savedCharacter.data.propMap['4001']?.val || 1;
    
    if (currentLevel >= targetLevel) {
        const embed = new EmbedBuilder()
            .setTitle('❌ 育成不要')
            .setDescription(`${savedCharacter.characterName} は既にレベル ${currentLevel} です。目標レベル（${targetLevel}）より高いか同じです。`)
            .setColor('#FF4444');
        
        await interaction.editReply({ embeds: [embed], components: [] });
        return;
    }

    // 英語名を取得して育成コスト計算
    const englishName = findEnglishCharacterName(savedCharacter.characterName);
    if (!englishName) {
        const embed = new EmbedBuilder()
            .setTitle('❌ エラー')
            .setDescription(`「${savedCharacter.characterName}」の育成データが見つかりませんでした。`)
            .setColor('#FF4444');
        
        await interaction.editReply({ embeds: [embed], components: [] });
        return;
    }

    const buildCost = await calculateBuildCost(englishName, currentLevel, targetLevel);
    if (!buildCost) {
        const embed = new EmbedBuilder()
            .setTitle('❌ エラー')
            .setDescription('育成コスト計算に失敗しました。')
            .setColor('#FF4444');
        
        await interaction.editReply({ embeds: [embed], components: [] });
        return;
    }

    const embed = new EmbedBuilder()
        .setTitle(`🎯 ${savedCharacter.characterName} の育成コスト`)
        .setDescription(`**レベル ${currentLevel} → ${targetLevel}**\n💪 あなたのキャラクターの育成計画`)
        .setColor('#00D2FF')
        .setTimestamp()
        .setFooter({ text: `保存データ更新: ${new Date(savedCharacter.lastUpdated).toLocaleDateString('ja-JP')}` });

    // コンステレーションを取得
    const constellation = savedCharacter.data.propMap['1002']?.val || 0;
    
    // 育成段階判定
    let currentStage = '';
    if (currentLevel < 20) currentStage = '未突破';
    else if (currentLevel < 40) currentStage = '1段階突破';
    else if (currentLevel < 50) currentStage = '2段階突破';
    else if (currentLevel < 60) currentStage = '3段階突破';
    else if (currentLevel < 70) currentStage = '4段階突破';
    else if (currentLevel < 80) currentStage = '5段階突破';
    else if (currentLevel < 90) currentStage = '6段階突破';
    else currentStage = '最大レベル';
    
    let targetStage = '';
    if (targetLevel <= 20) targetStage = '1段階突破';
    else if (targetLevel <= 40) targetStage = '2段階突破';
    else if (targetLevel <= 50) targetStage = '3段階突破';
    else if (targetLevel <= 60) targetStage = '4段階突破';
    else if (targetLevel <= 70) targetStage = '5段階突破';
    else if (targetLevel <= 80) targetStage = '6段階突破';
    else targetStage = '最大レベル';

    // 現在の状況と目標
    embed.addFields({
        name: '📊 育成状況',
        value: `**現在:** Lv.${currentLevel} (${currentStage})\n**目標:** Lv.${targetLevel} (${targetStage})\n**コンス:** ${constellation}`,
        inline: true
    });

    // 総合コスト概要
    embed.addFields({
        name: '💎 必要リソース',
        value: `🪙 **${formatMora(buildCost.mora)}** モラ`,
        inline: true
    });

    // 進捗表示
    const progress = Math.floor((currentLevel / targetLevel) * 100);
    const progressBar = '█'.repeat(Math.floor(progress / 10)) + '░'.repeat(10 - Math.floor(progress / 10));
    embed.addFields({
        name: '📈 育成進捗',
        value: `${progressBar} ${progress}%`,
        inline: true
    });

    // 経験書
    if (buildCost.expBooks.heroWit > 0 || buildCost.expBooks.adventurerExp > 0 || buildCost.expBooks.wandererAdvice > 0) {
        let expBooksText = '';
        if (buildCost.expBooks.heroWit > 0) {
            expBooksText += `🟣 **大英雄の経験:** ${buildCost.expBooks.heroWit}個\n`;
        }
        if (buildCost.expBooks.adventurerExp > 0) {
            expBooksText += `🔵 **冒険家の経験:** ${buildCost.expBooks.adventurerExp}個\n`;
        }
        if (buildCost.expBooks.wandererAdvice > 0) {
            expBooksText += `🟢 **流浪者の経験:** ${buildCost.expBooks.wandererAdvice}個\n`;
        }

        embed.addFields({
            name: '📚 経験書',
            value: expBooksText.trim(),
            inline: false
        });
    }

    // 昇格素材
    if (buildCost.materials.length > 0) {
        // 素材をレアリティ順にソート
        const sortedMaterials = buildCost.materials.sort((a, b) => b.rarity - a.rarity);
        const materialsText = sortedMaterials
            .map(material => `${getRarityEmoji(material.rarity)} **${material.name}:** ${material.count}個`)
            .join('\n');

        embed.addFields({
            name: '💎 昇格素材',
            value: materialsText,
            inline: false
        });
    }

    // 育成のヒント
    embed.addFields({
        name: '💡 育成のヒント',
        value: '• **効率的な育成:** レベル80/90推奨（コスパ最高）\n• **素材収集:** 曜日ダンジョンを活用\n• **経験書:** イベント報酬を優先活用',
        inline: false
    });

    await interaction.editReply({ embeds: [embed], components: [] });
}

// 育成プランオプションを表示
async function showBuildPlanOptions(interaction, savedCharacter, currentLevel) {
    // 英語名を取得
    const englishName = findEnglishCharacterName(savedCharacter.characterName);
    if (!englishName) {
        await interaction.editReply(`❌ 「${savedCharacter.characterName}」の育成データが見つかりませんでした。`);
        return;
    }

    // 完全育成コストを計算
    const fullBuildCost = await calculateFullBuildCost(englishName);
    if (!fullBuildCost) {
        await interaction.editReply('❌ 育成コスト計算に失敗しました。');
        return;
    }

    // コンステレーションを取得
    const constellation = savedCharacter.data.propMap['1002']?.val || 0;

    const embed = new EmbedBuilder()
        .setTitle(`🎯 ${savedCharacter.characterName} の育成プラン`)
        .setDescription(`**HoyoLab風育成計算器**\n現在レベル: ${currentLevel} | コンス: ${constellation}`)
        .setColor('#4A90E2')
        .setTimestamp()
        .setFooter({ text: 'あなたのキャラクターデータを基にした育成計画です' });

    // 推奨育成段階
    const buildStages = [];
    
    if (currentLevel < 20) buildStages.push({ level: 20, name: '1段階突破', desc: '最初の突破' });
    if (currentLevel < 40) buildStages.push({ level: 40, name: '2段階突破', desc: '天賦1解放' });
    if (currentLevel < 50) buildStages.push({ level: 50, name: '3段階突破', desc: '天賦2解放' });
    if (currentLevel < 60) buildStages.push({ level: 60, name: '4段階突破', desc: '実用レベル' });
    if (currentLevel < 70) buildStages.push({ level: 70, name: '5段階突破', desc: '高難易度対応' });
    if (currentLevel < 80) buildStages.push({ level: 80, name: '6段階突破', desc: '最終突破' });
    if (currentLevel < 90) buildStages.push({ level: 90, name: '最大レベル', desc: 'HP・攻撃力最大化' });

    if (buildStages.length === 0) {
        embed.addFields({
            name: '🎉 育成完了！',
            value: 'このキャラクターは既に最大レベル（90）に到達しています。',
            inline: false
        });
    } else {
        // 次の推奨ステップ
        const nextStage = buildStages[0];
        embed.addFields({
            name: `🎯 次の推奨ステップ: レベル${nextStage.level}`,
            value: `**${nextStage.name}**\n${nextStage.desc}`,
            inline: false
        });

        // 全育成段階
        const stagesText = buildStages
            .map(stage => `• **レベル${stage.level}**: ${stage.name}`)
            .join('\n');
        
        embed.addFields({
            name: '📈 利用可能な育成段階',
            value: stagesText,
            inline: false
        });
    }

    // 完全育成の概算コスト
    const heroWitCount = fullBuildCost.levelCost?.expBooks.heroWit || 0;
    embed.addFields({
        name: '💎 完全育成の概算コスト（レベル1→90）',
        value: `**モラ:** ${formatMora(fullBuildCost.totalMora)}` + 
               `\n**大英雄の経験:** ${heroWitCount}個` +
               `\n**昇格素材:** 各種必要` +
               `\n**天賦育成:** 9/9/9まで含む`,
        inline: false
    });

    embed.addFields({
        name: '💡 使用方法',
        value: '具体的な育成コストを計算するには:\n`/my-character-build キャラクター名 目標レベル`\n例: `/my-character-build 胡桃 80`',
        inline: false
    });

    await interaction.editReply({ embeds: [embed], components: [] });
}

// キャラクター選択メニューを表示
async function showCharacterSelectMenu(interaction, userCharacters, targetLevel) {
    const characters = Object.entries(userCharacters);
    
    if (characters.length === 0) {
        await interaction.editReply('❌ 保存されたキャラクター情報がありません。まず `/character` コマンドでキャラクター情報を取得してください。');
        return;
    }

    // セレクトメニューのオプションを作成
    const options = characters.slice(0, 25).map(([characterId, character]) => {
        const currentLevel = character.data.propMap['4001']?.val || 1;
        const constellation = character.data.propMap['1002']?.val || 0;
        
        return new StringSelectMenuOptionBuilder()
            .setLabel(character.characterName)
            .setDescription(`レベル ${currentLevel} | コンス ${constellation}`)
            .setValue(`${characterId}|${targetLevel || 'plan'}`);
    });

    const selectMenu = new StringSelectMenuBuilder()
        .setCustomId('character_build_select')
        .setPlaceholder('育成計画を立てるキャラクターを選択してください')
        .addOptions(options);

    const row = new ActionRowBuilder().addComponents(selectMenu);

    const embed = new EmbedBuilder()
        .setTitle('🎯 育成計画キャラクター選択')
        .setDescription(
            targetLevel 
                ? `**目標レベル ${targetLevel}** の育成計画を立てるキャラクターを選択してください。`
                : '**総合育成プラン**を表示するキャラクターを選択してください。'
        )
        .setColor('#4A90E2')
        .addFields({
            name: '📊 保存キャラクター数',
            value: `${characters.length}体のキャラクターが保存されています`,
            inline: true
        })
        .setFooter({ text: 'キャラクターを選択すると育成計画が表示されます' });

    const response = await interaction.editReply({ embeds: [embed], components: [row] });

    // セレクトメニューの応答を待機
    try {
        const selectInteraction = await response.awaitMessageComponent({
            componentType: ComponentType.StringSelect,
            time: 60000,
            filter: (i) => i.user.id === interaction.user.id
        });

        const [selectedCharacterId, targetLevelStr] = selectInteraction.values[0].split('|');
        const selectedCharacter = userCharacters[selectedCharacterId];
        
        await selectInteraction.deferUpdate();
        
        if (targetLevelStr === 'plan') {
            // 総合育成プラン表示
            await showBuildPlanOptions(selectInteraction, selectedCharacter, selectedCharacter.data.propMap['4001']?.val || 1);
        } else {
            // 具体的な育成コスト計算
            await showBuildCostDetails(selectInteraction, selectedCharacter, parseInt(targetLevelStr));
        }

    } catch (error) {
        console.error('セレクトメニュー応答エラー:', error);
        const timeoutEmbed = new EmbedBuilder()
            .setTitle('⏰ 時間切れ')
            .setDescription('キャラクター選択がタイムアウトしました。もう一度コマンドを実行してください。')
            .setColor('#FF4444');
        
        await interaction.editReply({ embeds: [timeoutEmbed], components: [] });
    }
}

// 保存されたキャラクターの育成コスト計算
async function handleMyCharacterBuild(interaction) {
    try {
        const characterName = interaction.options.getString(OPTION_NAMES.CHARACTER_NAME);
        const targetLevel = interaction.options.getInteger(OPTION_NAMES.TARGET_LEVEL);
        const userId = interaction.user.id;

        await interaction.deferReply({ ephemeral: true });

        // 入力値検証
        if (targetLevel && (targetLevel < 1 || targetLevel > 90)) {
            await interaction.editReply('❌ 目標レベルは1〜90の範囲で入力してください。');
            return;
        }

        // ユーザーの保存キャラクターを取得
        const userCharacters = await getUserCharacters(userId);
        if (!userCharacters) {
            await interaction.editReply('❌ 保存されたキャラクター情報がありません。まず `/character` コマンドでキャラクター情報を取得してください。');
            return;
        }

        // キャラクター名が指定されていない場合はセレクトメニューを表示
        if (!characterName) {
            await showCharacterSelectMenu(interaction, userCharacters, targetLevel || undefined);
            return;
        }

        // キャラクター名からIDを検索
        const characterId = findCharacterIdByName(characterName, userCharacters);
        if (!characterId) {
            await interaction.editReply(`❌ 「${characterName}」の保存データが見つかりませんでした。\n\`/my-characters\` で保存されているキャラクターを確認してください。`);
            return;
        }

        const savedCharacter = userCharacters[characterId];
        if (!savedCharacter) {
            await interaction.editReply('❌ キャラクターデータの取得に失敗しました。');
            return;
        }

        // EnkaのpropMapからレベルを取得（プロパティID 4001はレベル）
        const currentLevel = savedCharacter.data.propMap['4001']?.val || 1;
        
        // 目標レベルが指定されていない場合は、育成プランオプションを提示
        if (!targetLevel) {
            await showBuildPlanOptions(interaction, savedCharacter, currentLevel);
            return;
        }
        
        // 具体的な育成コスト計算
        await showBuildCostDetails(interaction, savedCharacter, targetLevel);

    } catch (error) {
        console.error('保存キャラクター育成コスト計算エラー:', error);
        await interaction.editReply('❌ 育成コスト計算中にエラーが発生しました。');
    }
}

// 保存されたキャラクターの天賦育成コスト
async function handleMyCharacterTalent(interaction) {
    try {
        const characterName = interaction.options.getString(OPTION_NAMES.CHARACTER_NAME);
        const talentType = interaction.options.getString(OPTION_NAMES.TALENT_TYPE);
        const targetLevel = interaction.options.getInteger(OPTION_NAMES.TARGET_LEVEL);
        const userId = interaction.user.id;

        await interaction.deferReply({ ephemeral: true });

        // 入力値検証
        if (targetLevel < 1 || targetLevel > 10) {
            await interaction.editReply('❌ 天賦レベルは1〜10の範囲で入力してください。');
            return;
        }

        await interaction.editReply('⚠️ この機能は現在開発中です。天賦レベル情報の保存が必要です。');

    } catch (error) {
        console.error('保存キャラクター天賦コスト計算エラー:', error);
        await interaction.editReply('❌ 天賦コスト計算中にエラーが発生しました。');
    }
}

module.exports = {
    handleMyCharacterBuild,
    handleMyCharacterTalent
}; 