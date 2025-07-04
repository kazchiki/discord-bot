// 必要なモジュールをインポート
require('dotenv/config');
const {
    Client,
    GatewayIntentBits,
    REST,
    Routes,
    ActivityType
} = require('discord.js');

// 分離したモジュールをインポート
const { commands } = require('./commands');
const { handleGenshinCommand } = require('./commands/genshin');
const { handleCharacterCommand, showCharacterDetails } = require('./commands/character');
const { handleRegisterCommand } = require('./commands/register');
const { handleMyGenshinCommand } = require('./commands/myGenshin');
const { handleMyCharactersCommand, handleMyCharacterCommand } = require('./commands/myCharacters');
const { handleMyAccounts, handleSwitchUID } = require('./commands/accounts');
const { handleMyCharacterBuild } = require('./commands/myBuildPlan');
const { COMMAND_NAMES } = require('./constants/commands');

// Discordクライアントの作成
const client = new Client({ 
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
    ]
});

// ボットが準備できたときのイベント
client.on('ready', async () => {
    console.log(`Logged in as ${client.user?.tag}!`);
    client.user?.setActivity('原神', { type: ActivityType.Playing });

    try {
        const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);
        console.log('スラッシュコマンドを登録中...');

        await rest.put(
            Routes.applicationCommands(client.user.id),
            { body: commands },
        );

        console.log('スラッシュコマンドの登録が完了しました！');
    } catch (error) {
        console.error('スラッシュコマンドの登録に失敗しました:', error);
    }
});

// スラッシュコマンドの処理
client.on('interactionCreate', async interaction => {
    if (!interaction.isChatInputCommand()) return;

    const { commandName } = interaction;

    if (commandName === COMMAND_NAMES.GENSHIN) {
        await handleGenshinCommand(interaction);
    } else if (commandName === COMMAND_NAMES.CHARACTER) {
        await handleCharacterCommand(interaction);
    } else if (commandName === COMMAND_NAMES.REGISTER) {
        await handleRegisterCommand(interaction);
    } else if (commandName === COMMAND_NAMES.MY_INFO) {
        await handleMyGenshinCommand(interaction);
    } else if (commandName === COMMAND_NAMES.MY_CHARACTERS) {
        await handleMyCharactersCommand(interaction);
    } else if (commandName === COMMAND_NAMES.MY_CHARACTER) {
        await handleMyCharacterCommand(interaction);
    } else if (commandName === COMMAND_NAMES.MY_ACCOUNTS) {
        await handleMyAccounts(interaction);
    } else if (commandName === COMMAND_NAMES.SWITCH_UID) {
        await handleSwitchUID(interaction);
    } else if (commandName === COMMAND_NAMES.MY_CHARACTER_BUILD) {
        await handleMyCharacterBuild(interaction);
    }
});

// ボタンインタラクションの処理
client.on('interactionCreate', async interaction => {
    if (!interaction.isButton()) return;

    const [action, uid, characterId] = interaction.customId.split('_');

    if (action === 'character') {
        await showCharacterDetails(interaction, uid, characterId);
    }
});

// Discordにログイン
client.login(process.env.DISCORD_TOKEN); 