const discord = require('discord.js');

// Discordクライアントを保持する変数
let client = null;

// クライアントを設定
function setClient(discordClient) {
  client = discordClient;
}

// リプライを送信
function sendReply(message, text) {
  return message.reply(text)
    .then(() => console.log("リプライ送信: " + text))
    .catch(console.error);
}

// メッセージを送信
function sendMsg(channelId, text, option = {}) {
  if (!client) {
    console.error('Discord client not initialized');
    return Promise.reject(new Error('Discord client not initialized'));
  }
  
  return client.channels.get(channelId).send(text, option)
    .then(() => console.log("メッセージ送信: " + text + JSON.stringify(option)))
    .catch(console.error);
}

module.exports = {
  setClient,
  sendReply,
  sendMsg
}; 