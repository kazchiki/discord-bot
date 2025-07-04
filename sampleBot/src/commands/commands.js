// --- teamCommand.js ---
const { characters } = require('../data/characters');
const { ELEMENTS, GENDERS, CHARACTERS_PER_TEAM, MAX_TEAMS, MESSAGE_INTERVAL, TEAM_INTERVAL, SHUTDOWN_DELAY } = require('../config/config');
const { sendMsg } = require('../utils/messageUtils');
const { alhaithamPhrases, yanfeiPhrases, tohmaPhrases } = require('../data/phrases');

// チームコマンドのハンドラー
async function handleTeamCommand(message) {
  const commandParts = message.content.split(' ');

  // チーム数の取得
  const teamIndex = commandParts.findIndex(part => part.match(/^\/チーム数$|^\/teamcount$/));
  const requestedTeams = teamIndex !== -1 && commandParts[teamIndex + 1] ? parseInt(commandParts[teamIndex + 1]) : null;

  if (requestedTeams === null) {
    await sendMsg(message.channel.id, "何チーム必要なのか？専用コマンドで指定してくれ。\n\n**使用例:**\n`/チーム /チーム数 3`\n\n**オプション:**\n• `/レア度 4星` または `/レア度 5星`\n• `/元素 炎,水,風` （複数指定は`,`で区切る）\n• `/性別 男` または `/性別 女`\n• `/所持 所持` または `/所持 未所持`\n\n**完全例:**\n`/チーム /チーム数 2 /レア度 5星 /元素 炎,雷 /性別 女 /所持 所持`" );
    return;
  }

  if (requestedTeams < 1 || requestedTeams > MAX_TEAMS) {
    await sendMsg(message.channel.id, `1から${MAX_TEAMS}チームまでしか対応しないが。`);
    return;
  }

  // フィルタリングオプションの解析
  const filters = parseFilters(commandParts);
  
  // キャラクターフィルタリング
  let filteredCharacters = applyFilters(characters, filters);

  const totalCharactersNeeded = requestedTeams * CHARACTERS_PER_TEAM;

  if (filteredCharacters.length < totalCharactersNeeded) {
    const filterDesc = buildFilterDescription(filters);
    await sendMsg(message.channel.id, `条件「${filterDesc}」では${requestedTeams}チーム分のキャラクターが足りないが。利用可能: ${filteredCharacters.length}人、必要: ${totalCharactersNeeded}人`);
    return;
  }

  // チーム生成と送信
  await generateAndSendTeams(message.channel.id, filteredCharacters, requestedTeams);
}

// フィルタリングオプションを解析
function parseFilters(commandParts) {
  // レア度フィルタ
  const rarityIndex = commandParts.findIndex(part => part.match(/^\/レア度$|^\/rarity$/));
  const rarityInput = rarityIndex !== -1 && commandParts[rarityIndex + 1] ? commandParts[rarityIndex + 1] : null;
  const rarityFilter = rarityInput && rarityInput.match(/^[4-5]星$/) ? parseInt(rarityInput.replace('星', '')) : null;

  // 元素フィルタ
  const elementIndex = commandParts.findIndex(part => part.match(/^\/元素$|^\/element$/));
  const elementInput = elementIndex !== -1 && commandParts[elementIndex + 1] ? commandParts[elementIndex + 1] : null;
  const elementNames = elementInput ? elementInput.split(',') : null;
  const elementFilters = elementNames ? elementNames.filter(name => ['炎', '水', '風', '雷', '氷', '岩', '草'].includes(name)) : null;

  // 性別フィルタ
  const genderIndex = commandParts.findIndex(part => part.match(/^\/性別$|^\/gender$/));
  const genderInput = genderIndex !== -1 && commandParts[genderIndex + 1] ? commandParts[genderIndex + 1] : null;
  const genderFilter = genderInput && ['男', '女'].includes(genderInput) ? genderInput : null;

  // 所持状況フィルタ
  const ownedIndex = commandParts.findIndex(part => part.match(/^\/所持$|^\/owned$/));
  const ownedInput = ownedIndex !== -1 && commandParts[ownedIndex + 1] ? commandParts[ownedIndex + 1] : null;
  const ownedFilter = ownedInput ?
    (ownedInput === '所持' ? true : ownedInput === '未所持' ? false : null) : null;

  return {
    rarity: rarityFilter,
    elements: elementFilters,
    gender: genderFilter,
    owned: ownedFilter
  };
}

// フィルタを適用
function applyFilters(characters, filters) {
  let filteredCharacters = [...characters];

  // 所持状況でフィルタ（デフォルトは所持キャラのみ）
  if (filters.owned !== null) {
    const ownedValue = filters.owned ? 1 : 0;
    filteredCharacters = filteredCharacters.filter(char => char.owned === ownedValue);
  } else {
    filteredCharacters = filteredCharacters.filter(char => char.owned === 1);
  }

  // レア度でフィルタ
  if (filters.rarity && [4, 5].includes(filters.rarity)) {
    filteredCharacters = filteredCharacters.filter(char => char.rarity === filters.rarity);
  }

  // 性別でフィルタ
  if (filters.gender && ['男', '女'].includes(filters.gender)) {
    const genderValue = filters.gender === '男' ? 1 : 2;
    filteredCharacters = filteredCharacters.filter(char => char.gender === genderValue);
  }

  // 元素でフィルタ
  if (filters.elements) {
    const elementValues = filters.elements.map(el => {
      const reverseMapping = { '炎': 1, '水': 2, '風': 3, '雷': 4, '氷': 5, '岩': 6, '草': 7 };
      return reverseMapping[el];
    }).filter(val => val);
    filteredCharacters = filteredCharacters.filter(char => elementValues.includes(char.element));
  }

  return filteredCharacters;
}

// フィルタ説明文を作成
function buildFilterDescription(filters) {
  const filterDesc = [
    filters.rarity ? `${filters.rarity}星` : '',
    filters.elements ? filters.elements.join(',') : '',
    filters.gender || '',
    filters.owned === true ? '所持' : filters.owned === false ? '未所持' : '所持'
  ].filter(f => f).join(' ');
  return filterDesc;
}

// チーム生成と送信
async function generateAndSendTeams(channelId, filteredCharacters, requestedTeams) {
  // シャッフルして選択
  const shuffled = [...filteredCharacters].sort(() => 0.5 - Math.random());

  await sendMsg(channelId, `お前がともに戦うメンバーは彼らだ。`);
  
  for (let teamNum = 1; teamNum <= requestedTeams; teamNum++) {
    const startIndex = (teamNum - 1) * CHARACTERS_PER_TEAM;
    const teamMembers = shuffled.slice(startIndex, startIndex + CHARACTERS_PER_TEAM);
    
    setTimeout(() => {
      sendMsg(channelId, `**第${teamNum}チーム:**`);
      teamMembers.forEach((character, index) => {
        setTimeout(() => {
          const elementName = ELEMENTS[character.element];
          sendMsg(channelId, `${index + 1}人目: ${character.name}（${elementName}）`);
        }, (index + 1) * MESSAGE_INTERVAL);
      });
    }, (teamNum - 1) * TEAM_INTERVAL);
  }
}

// --- phraseCommands.js ---
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

// --- systemCommands.js ---
// ボット終了コマンドのハンドラー
async function handleShutdownCommand(message) {
  await sendMsg(message.channel.id, "疲れたのか？俺はもう行くが。");
  setTimeout(() => {
    console.log('ボットを終了します...');
    process.exit(0);
  }, SHUTDOWN_DELAY);
}

module.exports = {
  handleTeamCommand,
  handleAlhaithamCommand,
  handleYanfeiCommand,
  handleTohmaCommand,
  handlePaimonCommand,
  handleShutdownCommand
}; 