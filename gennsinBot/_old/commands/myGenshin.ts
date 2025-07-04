import { ChatInputCommandInteraction } from 'discord.js';
import { getUserUID } from '../utils/userData';

export async function handleMyGenshinCommand(interaction: ChatInputCommandInteraction): Promise<void> {
    const userId = interaction.user.id;

    try {
        // 登録されたUIDを取得
        const savedUID = await getUserUID(userId);

        if (!savedUID) {
            await interaction.reply({
                content: '❌ UIDが登録されていません。\n`/register-uid` コマンドでまずUIDを登録してください。',
                ephemeral: true
            });
            return;
        }

        // genshinコマンドから共通処理部分をインポートして使用
        const { executeGenshinLogic } = await import('./genshin');
        await executeGenshinLogic(interaction, savedUID);

    } catch (error: any) {
        console.error('自分の原神情報取得エラー:', error);
        await interaction.reply({
            content: '❌ 情報取得中にエラーが発生しました。',
            ephemeral: true
        });
    }
} 