const discord = require('discord.js');
const { TOKEN } = require('./config/config');
const { setClient, sendReply } = require('./utils/messageUtils');
const { startServer } = require('./utils/httpServer');
const { handleTeamSlashCommand, teamCommand } = require('./commands/teamCommand');
const { 
  handleAlhaithamSlashCommand,
  handleYanfeiSlashCommand,
  handleTohmaSlashCommand,
  handlePaimonSlashCommand,
  alhaithamCommand,
  yanfeiCommand,
  tohmaCommand,
  paimonCommand
} = require('./commands/phraseCommands');
const { 
  handleShutdownSlashCommand, 
  shutdownCommand 
} = require('./commands/systemCommands');

// Discordクライアントを作成（Intentsを設定）
const client = new discord.Client({
  intents: [
    discord.GatewayIntentBits.Guilds,
    discord.GatewayIntentBits.GuildMessages,
    discord.GatewayIntentBits.MessageContent
  ]
});

// HTTPサーバーを起動
startServer();

// クライアントの準備が完了したときのイベント
client.on('ready', async () => {
  console.log('Bot準備完了～');
  client.user.setPresence({ activity: { name: '原神' } });
  
  // メッセージユーティリティにクライアントを設定
  setClient(client);

  // スラッシュコマンドを登録
  try {
    const commands = [
      teamCommand,
      alhaithamCommand,
      yanfeiCommand,
      tohmaCommand,
      paimonCommand,
      shutdownCommand
    ];
    await client.application.commands.set(commands);
    console.log('スラッシュコマンドを登録しました');
  } catch (error) {
    console.error('スラッシュコマンドの登録に失敗しました:', error);
  }
});

// スラッシュコマンドのハンドラー
client.on('interactionCreate', async (interaction) => {
  if (!interaction.isChatInputCommand()) return;

  switch (interaction.commandName) {
    case 'team':
      await handleTeamSlashCommand(interaction);
      break;
    case 'alhaitham':
      await handleAlhaithamSlashCommand(interaction);
      break;
    case 'yanfei':
      await handleYanfeiSlashCommand(interaction);
      break;
    case 'tohma':
      await handleTohmaSlashCommand(interaction);
      break;
    case 'paimon':
      await handlePaimonSlashCommand(interaction);
      break;
    case 'shutdown':
      await handleShutdownSlashCommand(interaction);
      break;
  }
});

// メッセージを受信したときのイベント（メンション反応のみ）
client.on('messageCreate', async (message) => {
  // ボット自身のメッセージやボットからのメッセージを無視
  if (message.author.id === client.user.id || message.author.bot) {
    return;
  }

  // ボットへのメンションの場合
  if (message.isMemberMentioned(client.user)) {
    await sendReply(message, "呼んだか？");
    return;
  }

  // パイモン反応（「えへ」が含まれている場合）
  if (message.content.includes('えへ')) {
    await sendReply(message, "えへってなんだよ!");
    return;
  }

  // 俺が…シリーズ
  if (message.content.match(/俺/)) {
    const { tohmaPhrases } = require('./data/phrases');
    const randomPhrase = tohmaPhrases[Math.floor(Math.random() * tohmaPhrases.length)];
    await sendReply(message, randomPhrase);
    return;
  }
});

// エラーハンドリング
client.on('error', error => {
  console.error('Discord client error:', error);
});

// プロセス終了時のエラーハンドリング
process.on('unhandledRejection', error => {
  console.error('Unhandled promise rejection:', error);
});

// TOKENの確認とログイン
if (!TOKEN) {
  console.log('TOKENが設定されていません。');
  process.exit(0);
}

client.login(TOKEN); 