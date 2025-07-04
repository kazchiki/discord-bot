const { alhaithamPhrases, yanfeiPhrases, tohmaPhrases } = require('../data/phrases');
const { sendMsg } = require('../utils/messageUtils');

// アルハイゼンコマンドのハンドラー
async function handleAlhaithamCommand(message) {
  const randomPhrase = alhaithamPhrases[Math.floor(Math.random() * alhaithamPhrases.length)];
  await sendMsg(message.channel.id, randomPhrase);
}

// 煙緋コマンドのハンドラー
async function handleYanfeiCommand(message) {
  const randomPhrase = yanfeiPhrases[Math.floor(Math.random() * yanfeiPhrases.length)];
  await sendMsg(message.channel.id, randomPhrase);
}

// トーマコマンドのハンドラー（「俺」が含まれた場合）
async function handleTohmaCommand(message) {
  const randomPhrase = tohmaPhrases[Math.floor(Math.random() * tohmaPhrases.length)];
  await sendMsg(message.channel.id, randomPhrase);
}

// パイモンコマンドのハンドラー（「えへ」が含まれた場合）
async function handlePaimonCommand(message) {
  const text = "えへってなんだよ!";
  await sendMsg(message.channel.id, text);
}

module.exports = {
  handleAlhaithamCommand,
  handleYanfeiCommand,
  handleTohmaCommand,
  handlePaimonCommand
}; 