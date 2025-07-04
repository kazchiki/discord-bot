// 必要なモジュールをインポート
import 'dotenv/config';
import {
    Client,
    GatewayIntentBits,
    REST,
    Routes,
    ActivityType
} from 'discord.js';

// 分離したモジュールをインポート
import { commands } from './commands';
import { handleGenshinCommand } from './commands/genshin';
import { handleCharacterCommand, showCharacterDetails } from './commands/character';
import { handleRegisterCommand } from './commands/register';
import { handleMyGenshinCommand } from './commands/myGenshin';
import { handleMyCharactersCommand, handleMyCharacterCommand } from './commands/myCharacters';
import { handleMyAccounts, handleSwitchUID } from './commands/accounts';
import { handleMyCharacterBuild } from './commands/myBuildPlan';
import { COMMAND_NAMES } from './constants/commands';

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
        const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN!);
        console.log('スラッシュコマンドを登録中...');

        await rest.put(
            Routes.applicationCommands(client.user!.id),
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