import {
    ChatInputCommandInteraction,
    EmbedBuilder,
    ActionRowBuilder,
    ButtonBuilder,
    ButtonStyle
} from 'discord.js';
import axios, { AxiosResponse } from 'axios';
import { EnkaApiResponse } from '../types';
import { characterNames } from '../data/characters';
import { OPTION_NAMES } from '../constants/commands';
import { getUserUID } from '../utils/userData';

// 原神情報取得の共通ロジック
export async function executeGenshinLogic(interaction: ChatInputCommandInteraction, uid: string): Promise<void> {

    try {
        await interaction.deferReply();

        const apiUrl = `https://enka.network/api/uid/${uid}/`;
        const response: AxiosResponse<EnkaApiResponse> = await axios.get(apiUrl);
        const data = response.data;

        const playerInfo = data.playerInfo;
        if (!playerInfo) {
            await interaction.editReply(`UID \`${uid}\` のプレイヤー情報が見つかりませんでした。キャラクター詳細をプロフィールで公開しているか確認してください。`);
            return;
        }

        const characters = data.avatarInfoList || [];

        const embed = new EmbedBuilder()
            .setColor(0x0099FF)
            .setTitle(`${playerInfo.nickname}さんの原神ステータス`)
            .setURL(`https://enka.network/u/${uid}/`)
            .setDescription(`UID: ${uid}`)
            .addFields(
                { name: '冒険ランク', value: `${playerInfo.level}`, inline: true },
                { name: '世界ランク', value: `${playerInfo.worldLevel}`, inline: true },
                { name: '深境螺旋', value: `第${playerInfo.towerFloorIndex}層 第${playerInfo.towerLevelIndex}間`, inline: true }
            );

        if (playerInfo.signature) {
            embed.addFields({ name: 'ステータスメッセージ', value: playerInfo.signature, inline: false });
        }

        if (playerInfo.profilePicture?.avatarId) {
            embed.setThumbnail(`https://enka.network/ui/${playerInfo.profilePicture.avatarId}.png`);
        }

        // キャラクターボタンを作成
        const buttons: ButtonBuilder[] = [];
        if (characters.length > 0) {
            characters.forEach(char => {
                const charName = characterNames[char.avatarId] || `キャラID: ${char.avatarId}`;
                const level = char.propMap['4001'] ? char.propMap['4001'].val : 'N/A';

                buttons.push(
                    new ButtonBuilder()
                        .setCustomId(`character_${uid}_${char.avatarId}`)
                        .setLabel(`${charName} (Lv.${level})`)
                        .setStyle(ButtonStyle.Primary)
                );
            });
        }

        const rows: ActionRowBuilder<ButtonBuilder>[] = [];
        for (let i = 0; i < buttons.length; i += 5) {
            rows.push(new ActionRowBuilder<ButtonBuilder>().addComponents(buttons.slice(i, i + 5)));
        }

        await interaction.editReply({
            embeds: [embed],
            components: rows
        });

    } catch (error: any) {
        console.error(error);
        if (error.response) {
            if (error.response.status === 404) {
                await interaction.editReply(`UID \`${uid}\` のプレイヤー情報が見つかりませんでした。キャラクター詳細をプロフィールで公開しているか確認してください。`);
            } else if (error.response.status === 400) {
                await interaction.editReply(`UID \`${uid}\` は不正な形式です。`);
            } else if (error.response.status >= 500) {
                await interaction.editReply('Enka.Networkがメンテナンス中のようです。しばらくしてからもう一度お試しください。');
            } else {
                await interaction.editReply('情報の取得中に不明なエラーが発生しました。');
            }
        } else {
            await interaction.editReply('情報の取得中にエラーが発生しました。');
        }
    }
}

// スラッシュコマンドのハンドラー（UIDを引数から取得、省略時は登録済みUID使用）
export async function handleGenshinCommand(interaction: ChatInputCommandInteraction): Promise<void> {
    let uid = interaction.options.getString(OPTION_NAMES.UID);
    
    // UIDが指定されていない場合、登録済みUIDを使用
    if (!uid) {
        const savedUID = await getUserUID(interaction.user.id);
        if (!savedUID) {
            await interaction.reply({
                content: '❌ UIDが指定されておらず、登録もされていません。\n' +
                        '- UIDを指定するか\n' +
                        '- `/register-uid` コマンドでUIDを登録してください。',
                ephemeral: true
            });
            return;
        }
        uid = savedUID;
    }
    
    await executeGenshinLogic(interaction, uid);
} 