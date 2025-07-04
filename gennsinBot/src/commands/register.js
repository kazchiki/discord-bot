const { EmbedBuilder } = require('discord.js');
const { setUserUID, deleteUserData } = require('../utils/userData');
const { OPTION_NAMES } = require('../constants/commands');

async function handleRegisterCommand(interaction) {
    const uid = interaction.options.getString(OPTION_NAMES.UID);
    const nickname = interaction.options.getString(OPTION_NAMES.NICKNAME);
    const userId = interaction.user.id;

    try {
        await interaction.deferReply({ ephemeral: true }); // 他人に見えないようにephemeralに

        // UIDの形式チェック（簡易版）
        if (!/^\d{9}$/.test(uid)) {
            await interaction.editReply('❌ UIDは9桁の数字で入力してください。例: 123456789');
            return;
        }

        // ユーザーデータを保存
        await setUserUID(userId, uid, nickname || undefined);

        const nicknameText = nickname ? `（ニックネーム: ${nickname}）` : '';

        const embed = new EmbedBuilder()
            .setColor(0x00FF00)
            .setTitle('✅ UID登録完了')
            .setDescription(`あなたのUID \`${uid}\` を登録しました！${nicknameText}`)
            .addFields(
                { name: '📌 使い方', value: '今後は `/my-genshin` コマンドでUID入力なしで情報を表示できます。', inline: false },
                { name: '🔄 更新', value: 'UIDを変更したい場合は、再度このコマンドを実行してください。', inline: false },
                { name: '📊 複数アカウント', value: '複数のUIDを登録でき、`/switch-uid`で切り替えられます。', inline: false }
            )
            .setFooter({ text: `登録者: ${interaction.user.username}` })
            .setTimestamp();

        await interaction.editReply({ embeds: [embed] });

    } catch (error) {
        console.error('UID登録エラー:', error);
        await interaction.editReply('❌ UID登録中にエラーが発生しました。しばらくしてからもう一度お試しください。');
    }
}

async function handleDeleteUserDataCommand(interaction) {
    const userId = interaction.user.id;

    try {
        await interaction.deferReply({ ephemeral: true });

        const deleted = await deleteUserData(userId);

        if (deleted) {
            const embed = new EmbedBuilder()
                .setColor(0xFF0000)
                .setTitle('🗑️ データ削除完了')
                .setDescription('登録されたUIDデータを削除しました。')
                .setFooter({ text: `削除者: ${interaction.user.username}` })
                .setTimestamp();

            await interaction.editReply({ embeds: [embed] });
        } else {
            await interaction.editReply('ℹ️ 登録されたUIDデータが見つかりませんでした。');
        }

    } catch (error) {
        console.error('データ削除エラー:', error);
        await interaction.editReply('❌ データ削除中にエラーが発生しました。');
    }
}

module.exports = {
    handleRegisterCommand,
    handleDeleteUserDataCommand
}; 