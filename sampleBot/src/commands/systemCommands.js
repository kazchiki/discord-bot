const { sendMsg } = require('../utils/messageUtils');
const { SHUTDOWN_DELAY } = require('../config/config');

// ボット終了コマンドのハンドラー
async function handleShutdownCommand(message) {
  await sendMsg(message.channel.id, "疲れたのか？俺はもう行くが。");
  setTimeout(() => {
    console.log('ボットを終了します...');
    process.exit(0);
  }, SHUTDOWN_DELAY);
}

module.exports = {
  handleShutdownCommand
}; 