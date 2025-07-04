const http = require('http');
const querystring = require('querystring');
const discord = require('discord.js');
const client = new discord.Client();

http.createServer(function (req, res) {
  if (req.method == 'POST') {
    var data = "";
    req.on('data', function (chunk) {
      data += chunk;
    });
    req.on('end', function () {
      if (!data) {
        res.end("No post data");
        return;
      }
      var dataObject = querystring.parse(data);
      console.log("post:" + dataObject.type);
      if (dataObject.type == "wake") {
        console.log("Woke up in post");
        res.end();
        return;
      }
      res.end();
    });
  }
  else if (req.method == 'GET') {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Discord Bot is active now\n');
  }
}).listen(3000);

client.on('ready', message => {
  console.log('Bot準備完了～');
  client.user.setPresence({ activity: { name: '原神' } });
});

client.on('message', message => {
  if (message.author.id == client.user.id || message.author.bot) {
    return;
  }
  if (message.isMemberMentioned(client.user)) {
    sendReply(message, "呼んだか？");
    return;
  }

  // ランダムチームを返す（/チームコマンド）
  if (message.content.match(/^\/チーム|^\/team|^\/ランダムチーム|^\/randomteam/)) {
    const characters = [
      // 主人公
      { name: '空', element: 1, rarity: 5, owned: 1, gender: 1 }, // 炎, 男
      { name: '空', element: 2, rarity: 5, owned: 1, gender: 1 }, // 水, 男
      { name: '空', element: 3, rarity: 5, owned: 1, gender: 1 }, // 風, 男
      { name: '空', element: 4, rarity: 5, owned: 1, gender: 1 }, // 雷, 男
      { name: '空', element: 6, rarity: 5, owned: 1, gender: 1 }, // 岩, 男
      { name: '空', element: 7, rarity: 5, owned: 1, gender: 1 }, // 草, 男
      { name: '蛍', element: 1, rarity: 5, owned: 1, gender: 2 }, // 炎, 女
      { name: '蛍', element: 2, rarity: 5, owned: 1, gender: 2 }, // 水, 女
      { name: '蛍', element: 3, rarity: 5, owned: 1, gender: 2 }, // 風, 女
      { name: '蛍', element: 4, rarity: 5, owned: 1, gender: 2 }, // 雷, 女
      { name: '蛍', element: 6, rarity: 5, owned: 1, gender: 2 }, // 岩, 女
      { name: '蛍', element: 7, rarity: 5, owned: 1, gender: 2 }, // 草, 女
      // { name: '空', element: 5, rarity: 5, owned: 1, gender: 1 }, // 氷, 男　未実装
      // { name: '蛍', element: 5, rarity: 5, owned: 1, gender: 2 }, // 氷, 女 未実装

      // 所持キャラクター
      { name: '神里 綾華', element: 5, rarity: 5, owned: 1, gender: 2 }, // 氷, 女
      { name: 'ジン', element: 3, rarity: 5, owned: 1, gender: 2 }, // 風, 女
      { name: 'リサ', element: 4, rarity: 4, owned: 1, gender: 2 }, // 雷, 女
      { name: 'バーバラ', element: 2, rarity: 4, owned: 1, gender: 2 }, // 水, 女
      { name: 'ガイア', element: 5, rarity: 4, owned: 1, gender: 1 }, // 氷, 男
      { name: 'ディルック', element: 1, rarity: 5, owned: 1, gender: 1 }, // 炎, 男
      { name: 'レザー', element: 4, rarity: 4, owned: 1, gender: 1 }, // 雷, 男
      { name: 'アンバー', element: 1, rarity: 4, owned: 1, gender: 2 }, // 炎, 女
      { name: 'ウェンティ', element: 3, rarity: 5, owned: 1, gender: 1 }, // 風, 男
      { name: '香菱', element: 1, rarity: 4, owned: 1, gender: 2 }, // 炎, 女
      { name: '北斗', element: 4, rarity: 4, owned: 1, gender: 2 }, // 雷, 女
      { name: '行秋', element: 2, rarity: 4, owned: 1, gender: 1 }, // 水, 男
      { name: '魈', element: 3, rarity: 5, owned: 1, gender: 1 }, // 風, 男
      { name: '凝光', element: 6, rarity: 4, owned: 1, gender: 2 }, // 岩, 女
      { name: '鍾離', element: 6, rarity: 5, owned: 1, gender: 1 }, // 岩, 男
      { name: 'フィッシュル', element: 4, rarity: 4, owned: 1, gender: 2 }, // 雷, 女
      { name: 'ベネット', element: 1, rarity: 4, owned: 1, gender: 1 }, // 炎, 男
      { name: 'タルタリヤ', element: 2, rarity: 5, owned: 1, gender: 1 }, // 水, 男
      { name: 'ノエル', element: 6, rarity: 4, owned: 1, gender: 2 }, // 岩, 女
      { name: '七七', element: 5, rarity: 5, owned: 1, gender: 2 }, // 氷, 女
      { name: '重雲', element: 5, rarity: 4, owned: 1, gender: 1 }, // 氷, 男
      { name: 'ディオナ', element: 5, rarity: 4, owned: 1, gender: 2 }, // 氷, 女
      { name: 'モナ', element: 2, rarity: 5, owned: 1, gender: 2 }, // 水, 女
      { name: '刻晴', element: 4, rarity: 5, owned: 1, gender: 2 }, // 雷, 女
      { name: 'スクロース', element: 3, rarity: 4, owned: 1, gender: 2 }, // 風, 女
      { name: '辛炎', element: 1, rarity: 4, owned: 1, gender: 2 }, // 炎, 女
      { name: 'ロサリア', element: 5, rarity: 4, owned: 1, gender: 2 }, // 氷, 女
      { name: '胡桃', element: 1, rarity: 5, owned: 1, gender: 2 }, // 炎, 女
      { name: '楓原 万葉', element: 3, rarity: 5, owned: 1, gender: 1 }, // 風, 男
      { name: '煙緋', element: 1, rarity: 4, owned: 1, gender: 2 }, // 炎, 女
      { name: '宵宮', element: 1, rarity: 5, owned: 1, gender: 2 }, // 炎, 女
      { name: 'トーマ', element: 1, rarity: 4, owned: 1, gender: 1 }, // 炎, 男
      { name: 'エウルア', element: 5, rarity: 5, owned: 1, gender: 2 }, // 氷, 女
      { name: '雷電 将軍', element: 4, rarity: 5, owned: 1, gender: 2 }, // 雷, 女
      { name: '早柚', element: 3, rarity: 4, owned: 1, gender: 2 }, // 風, 女
      { name: '珊瑚宮 心海', element: 2, rarity: 5, owned: 1, gender: 2 }, // 水, 女
      { name: 'ゴロー', element: 6, rarity: 4, owned: 1, gender: 1 }, // 岩, 男
      { name: '九条 裟羅', element: 4, rarity: 4, owned: 1, gender: 2 }, // 雷, 女
      { name: '八重 神子', element: 4, rarity: 5, owned: 1, gender: 2 }, // 雷, 女
      { name: '鹿野院 平蔵', element: 3, rarity: 4, owned: 1, gender: 1 }, // 風, 男
      { name: '夜蘭', element: 2, rarity: 5, owned: 1, gender: 2 }, // 水, 女
      { name: '綺良々', element: 7, rarity: 4, owned: 1, gender: 2 }, // 草, 女
      { name: 'アーロイ', element: 5, rarity: 5, owned: 1, gender: 2 }, // 氷, 女
      { name: '申鶴', element: 5, rarity: 5, owned: 1, gender: 2 }, // 氷, 女
      { name: '雲董', element: 6, rarity: 4, owned: 1, gender: 2 }, // 岩, 女
      { name: '久岐 忍', element: 4, rarity: 4, owned: 1, gender: 2 }, // 雷, 女
      { name: 'コレイ', element: 7, rarity: 4, owned: 1, gender: 2 }, // 草, 女
      { name: 'ドリー', element: 4, rarity: 4, owned: 1, gender: 2 }, // 雷, 女
      { name: 'ティナリ', element: 7, rarity: 5, owned: 1, gender: 1 }, // 草, 男
      { name: 'ニィロウ', element: 2, rarity: 5, owned: 1, gender: 2 }, // 水, 女
      { name: 'キャンディス', element: 2, rarity: 4, owned: 1, gender: 2 }, // 水, 女
      { name: 'ナヒーダ', element: 7, rarity: 5, owned: 1, gender: 2 }, // 草, 女
      { name: 'レイラ', element: 5, rarity: 4, owned: 1, gender: 2 }, // 氷, 女
      { name: '放浪者', element: 3, rarity: 5, owned: 1, gender: 1 }, // 風, 男
      { name: 'ファルザン', element: 3, rarity: 4, owned: 1, gender: 2 }, // 風, 女
      { name: 'ヨォーヨ', element: 7, rarity: 4, owned: 1, gender: 2 }, // 草, 女
      { name: 'ディシア', element: 1, rarity: 5, owned: 1, gender: 2 }, // 炎, 女
      { name: 'ミカ', element: 5, rarity: 4, owned: 1, gender: 1 }, // 氷, 男
      { name: 'カーヴェ', element: 7, rarity: 4, owned: 1, gender: 1 }, // 草, 男
      { name: '白朮', element: 7, rarity: 5, owned: 1, gender: 1 }, // 草, 男
      { name: 'リネット', element: 3, rarity: 4, owned: 1, gender: 2 }, // 風, 女
      { name: 'フレミネ', element: 5, rarity: 4, owned: 1, gender: 2 }, // 氷, 女
      { name: 'ヌヴィレット', element: 2, rarity: 5, owned: 1, gender: 1 }, // 水, 男
      { name: 'シャルロット', element: 5, rarity: 4, owned: 1, gender: 2 }, // 氷, 女
      { name: 'フリーナ', element: 2, rarity: 5, owned: 1, gender: 2 }, // 水, 女
      { name: 'シュヴルーズ', element: 1, rarity: 4, owned: 1, gender: 2 }, // 炎, 女
      { name: 'ナヴィア', element: 6, rarity: 5, owned: 1, gender: 2 }, // 岩, 女
      { name: '嘉明', element: 1, rarity: 4, owned: 1, gender: 1 }, // 炎, 男
      { name: '閑雲', element: 3, rarity: 5, owned: 1, gender: 2 }, // 風, 女
      { name: '千織', element: 6, rarity: 5, owned: 1, gender: 2 }, // 岩, 女
      { name: 'アルレッキーノ', element: 1, rarity: 5, owned: 1, gender: 2 }, // 炎, 女
      { name: 'セトス', element: 4, rarity: 4, owned: 1, gender: 1 }, // 雷, 男
      { name: 'クロリンデ', element: 4, rarity: 5, owned: 1, gender: 2 }, // 雷, 女
      { name: 'カチーナ', element: 6, rarity: 4, owned: 1, gender: 2 }, // 岩, 女
      { name: 'ムアラニ', element: 2, rarity: 5, owned: 1, gender: 2 }, // 水, 女
      { name: 'シロネン', element: 6, rarity: 5, owned: 1, gender: 2 }, // 岩, 女
      { name: 'オロルン', element: 4, rarity: 4, owned: 1, gender: 1 }, // 雷, 男
      { name: 'マーヴィカ', element: 1, rarity: 5, owned: 1, gender: 2 }, // 炎, 女
      { name: 'シトラリ', element: 5, rarity: 5, owned: 1, gender: 2 }, // 氷, 女
      { name: '藍硯', element: 3, rarity: 4, owned: 1, gender: 2 }, // 風, 女
      { name: '夢見月 瑞希', element: 3, rarity: 5, owned: 1, gender: 2 }, // 風, 女
      { name: 'イアンサ', element: 4, rarity: 4, owned: 1, gender: 2 }, // 雷, 女
      { name: 'ヴァレサ', element: 4, rarity: 5, owned: 1, gender: 2 }, // 雷, 女
      { name: 'イファ', element: 3, rarity: 4, owned: 1, gender: 1 }, // 風, 男
      { name: 'スカーク', element: 5, rarity: 5, owned: 1, gender: 2 }, // 氷, 女
      { name: 'ダリア', element: 2, rarity: 4, owned: 1, gender: 1 }, // 水, 男

      // 未入手キャラクター(kaz)
      { name: 'クレー', element: 1, rarity: 5, owned: 1, gender: 2 }, // 炎, 女
      { name: '甘雨', element: 5, rarity: 5, owned: 1, gender: 2 }, // 氷, 女
      { name: 'アルハイゼン', element: 7, rarity: 5, owned: 1, gender: 1 }, // 草, 男
      { name: 'シグウィン', element: 2, rarity: 5, owned: 1, gender: 2 }, // 水, 女
      { name: 'チャスカ', element: 3, rarity: 5, owned: 1, gender: 2 }, // 風, 女
      { name: 'エスコフィエ', element: 5, rarity: 5, owned: 1, gender: 2 }, // 氷, 女

      // 未入手キャラクター
      { name: 'アルベド', element: 6, rarity: 5, owned: 0, gender: 1 }, // 岩, 男
      { name: '荒瀧 一斗', element: 6, rarity: 5, owned: 0, gender: 1 }, // 岩, 男
      { name: '神里 綾人', element: 2, rarity: 5, owned: 0, gender: 1 }, // 水, 男
      { name: 'セノ', element: 4, rarity: 5, owned: 0, gender: 1 }, // 雷, 男
      { name: 'リネ', element: 1, rarity: 5, owned: 0, gender: 1 }, // 炎, 男
      { name: 'リオセスリ', element: 5, rarity: 5, owned: 0, gender: 1 }, // 氷, 男
      { name: 'エミリエ', element: 7, rarity: 5, owned: 0, gender: 2 }, // 草, 女
      { name: 'キイニチ', element: 7, rarity: 5, owned: 0, gender: 1 }, // 草, 男
    ];

    // マッピング定義
    const elementMapping = {
      1: '炎', 2: '水', 3: '風', 4: '雷', 5: '氷', 6: '岩', 7: '草'
    };

    const genderMapping = {
      1: '男', 2: '女'
    };

    // コマンド解析（例: /チーム数 3 /レア度 5星 /元素 炎,水,風 /性別 女 /所持 所持）
    const commandParts = message.content.split(' ');

    // チーム数の取得
    const teamIndex = commandParts.findIndex(part => part.match(/^\/チーム数$|^\/teamcount$/));
    const requestedTeams = teamIndex !== -1 && commandParts[teamIndex + 1] ? parseInt(commandParts[teamIndex + 1]) : null;

    // レア度フィルタ
    const rarityIndex = commandParts.findIndex(part => part.match(/^\/レア度$|^\/rarity$/));
    const rarityInput = rarityIndex !== -1 && commandParts[rarityIndex + 1] ? commandParts[rarityIndex + 1] : null;
    const rarityFilter = rarityInput && rarityInput.match(/^[4-5]星$/) ? parseInt(rarityInput.replace('星', '')) : null;

    // 元素フィルタ（文字列をマッピング）
    const elementIndex = commandParts.findIndex(part => part.match(/^\/元素$|^\/element$/));
    const elementInput = elementIndex !== -1 && commandParts[elementIndex + 1] ? commandParts[elementIndex + 1] : null;
    const elementNames = elementInput ? elementInput.split(',') : null;
    const elementFilters = elementNames ? elementNames.filter(name => ['炎', '水', '風', '雷', '氷', '岩', '草'].includes(name)) : null;

    // 性別フィルタ（文字列をマッピング）
    const genderIndex = commandParts.findIndex(part => part.match(/^\/性別$|^\/gender$/));
    const genderInput = genderIndex !== -1 && commandParts[genderIndex + 1] ? commandParts[genderIndex + 1] : null;
    const genderFilter = genderInput && ['男', '女'].includes(genderInput) ? genderInput : null;

    // 所持状況フィルタ（文字列で指定）
    const ownedIndex = commandParts.findIndex(part => part.match(/^\/所持$|^\/owned$/));
    const ownedInput = ownedIndex !== -1 && commandParts[ownedIndex + 1] ? commandParts[ownedIndex + 1] : null;
    const ownedFilter = ownedInput ?
      (ownedInput === '所持' ? true : ownedInput === '未所持' ? false : null) : null;

    if (requestedTeams === null) {
      sendMsg(message.channel.id, "何チーム必要なのか？専用コマンドで指定してくれ。\n\n**使用例:**\n`/チーム /チーム数 3`\n\n**オプション:**\n• `/レア度 4星` または `/レア度 5星`\n• `/元素 炎,水,風` （複数指定は`,`で区切る）\n• `/性別 男` または `/性別 女`\n• `/所持 所持` または `/所持 未所持`\n\n**完全例:**\n`/チーム /チーム数 2 /レア度 5星 /元素 炎,雷 /性別 女 /所持 所持`");
      return;
    }

    if (requestedTeams < 1 || requestedTeams > 20) {
      sendMsg(message.channel.id, "1から20チームまでしか対応しないが。");
      return;
    }

    // フィルタリング
    let filteredCharacters = characters;

    // 所持状況でフィルタ（デフォルトは所持キャラのみ）
    if (ownedFilter !== null) {
      const ownedValue = ownedFilter ? 1 : 0;
      filteredCharacters = filteredCharacters.filter(char => char.owned === ownedValue);
    } else {
      filteredCharacters = filteredCharacters.filter(char => char.owned === 1);
    }

    // レア度でフィルタ
    if (rarityFilter && [4, 5].includes(rarityFilter)) {
      filteredCharacters = filteredCharacters.filter(char => char.rarity === rarityFilter);
    }

    // 性別でフィルタ
    if (genderFilter && ['男', '女'].includes(genderFilter)) {
      const genderValue = genderFilter === '男' ? 1 : 2;
      filteredCharacters = filteredCharacters.filter(char => char.gender === genderValue);
    }

    // 元素でフィルタ（複数指定対応）
    if (elementFilters) {
      const elementValues = elementFilters.map(el => {
        const reverseMapping = { '炎': 1, '水': 2, '風': 3, '雷': 4, '氷': 5, '岩': 6, '草': 7 };
        return reverseMapping[el];
      }).filter(val => val);
      filteredCharacters = filteredCharacters.filter(char => elementValues.includes(char.element));
    }

    const charactersPerTeam = 4;
    const totalCharactersNeeded = requestedTeams * charactersPerTeam;

    if (filteredCharacters.length < totalCharactersNeeded) {
      const filterDesc = [
        rarityFilter || '',
        elementFilters ? elementFilters.join(',') : '',
        genderFilter || '',
        ownedFilter === true ? '所持' : ownedFilter === false ? '未所持' : '所持'
      ].filter(f => f).join(' ');
      sendMsg(message.channel.id, `条件「${filterDesc}」では${requestedTeams}チーム分のキャラクターが足りないが。利用可能: ${filteredCharacters.length}人、必要: ${totalCharactersNeeded}人`);
      return;
    }

    // 配列をシャッフルして必要な人数分選択
    const shuffled = [...filteredCharacters].sort(() => 0.5 - Math.random());

    sendMsg(message.channel.id, `お前がともに戦うメンバーは彼らだ。`);
    for (let teamNum = 1; teamNum <= requestedTeams; teamNum++) {
      const startIndex = (teamNum - 1) * charactersPerTeam;
      const teamMembers = shuffled.slice(startIndex, startIndex + charactersPerTeam);
      setTimeout(() => {
        sendMsg(message.channel.id, `**第${teamNum}チーム:**`);
        teamMembers.forEach((character, index) => {
          setTimeout(() => {
            const elementName = elementMapping[character.element];
            sendMsg(message.channel.id, `${index + 1}人目: ${character.name}（${elementName}）`);
          }, (index + 1) * 500); // 0.5秒間隔で送信
        });
      }, (teamNum - 1) * 3000); // チーム間は3秒間隔
    }
    return;
  }

  // アルハイゼン構文を返す（/アルハイゼンコマンド）
  if (message.content.match(/^\/アルハイゼン|^\/alhaitham|^\/構文/)) {
    const alhaithamPhrases = [
      "web漫画か？俺は海賊版で読むが",
      "恋は盲目なのか？俺はサングラスだが。",
      "人生は冒険なのか？俺は家から出ないが。",
      "愛は地球を救うのか？俺は火星人だが。",
      "残業か？俺は帰るが",
      "ガチャらないのか？俺は完凸するが",
      "原神するのか？俺はスタレをするが",
      "出勤か？俺は在宅だが",
      "バイトか？俺は休むが",
      "掃除か？俺は散らかすが",
      "読書か？俺はマンガ読むが",
      "筋トレか？俺は脂肪を増やすが",
      "ダイエットか？俺は太るが",
      "早起きか？俺は寝坊するが",
      "整理整頓か？俺は散らかすが",
      "節約か？俺は無駄遣いするが",
      "歯医者か？俺は虫歯を放置するが",
      "旅行か？俺は家にいるが",
      "三月なのか？俺は丹恒だが。",
      "歩くのか？俺はタクシーを使うが",
      "キャンプか？俺はホテルに泊まるが",
      "階段で行くのか？俺はエレベーターを使うが",
      "野球か？俺は三振するが",
      "将棋か？俺は王手を逃すが",
      "九蓮宝燈か？俺は純正九連宝燈だが",
      "南を切るのか？俺は国士無双13面待ちだが",
      "プログラミングか？俺はバグを作るが",
      "年金か？俺は老後に備えないが",
      "英会話か？俺は日本人だが",
      "家事か？俺は家事代行を頼むが",
      "食器洗いか？俺は食洗機を使うが",
      "洗濯か？俺はクリーニングに出すが",
      "駐車場か？俺は路上駐車するが",
      "ガソリンスタンドか？俺は電気自動車に乗るが",
      "リサイクルか？俺は燃えるゴミに出すが",
      "カジノか？俺は家でオンラインカジノをするが",
    ];

    const randomPhrase = alhaithamPhrases[Math.floor(Math.random() * alhaithamPhrases.length)];
    sendMsg(message.channel.id, randomPhrase);
    return;
  }

  // 煙緋のボイスを返す（/煙緋コマンド）
  if (message.content.match(/^\/煙緋|^\/yanfei|^\/はむ/)) {
    const yanfeiPhrases = [
      "私は煙緋",
      "燃えよ!",
      "はあ…なんて最悪な天気なんだ…ひ、冷えるな…\nハ…ハックション…",
      "まったく…モラが稼げないじゃないか",
      "静かで、邪魔をされない、2人だけの時間を楽しみたい…",
      "私が仕事以外でも凄いってことをお前に見せたい",
      "私みたいにテキパキしろよ、ふふ",
      "by煙緋\nおやすみおやすみ…はむ",
    ];

    const randomPhrase = yanfeiPhrases[Math.floor(Math.random() * yanfeiPhrases.length)];
    sendMsg(message.channel.id, randomPhrase);
    return;
  }

  // パイモン（文章に「えへ」が含まれている場合）
  if (message.content.includes('えへ')) {
    let text = "えへってなんだよ!";
    sendMsg(message.channel.id, text);
    return;
  }

  // 俺が…シリーズ
  if (message.content.match(/俺/)) {
    const tohmaPhrases = [
      "俺が払うよ",
      "俺が守るよ",
      "俺が値切るよ",
      "俺は帰るよ",
    ];

    const randomPhrase = tohmaPhrases[Math.floor(Math.random() * tohmaPhrases.length)];
    sendMsg(message.channel.id, randomPhrase);
    return;
  }

  // ボット終了コマンド
  if (message.content.match(/^\/終了|^\/exit|^\/quit|^\/stop/)) {
    sendMsg(message.channel.id, "疲れたのか？俺はもう行くが。");
    setTimeout(() => {
      console.log('ボットを終了します...');
      process.exit(0);
    }, 2000); // 2秒後に終了
    return;
  }
});

if (process.env.TOKEN == undefined) {
  console.log('TOKENが設定されていません。');
  process.exit(0);
}

client.login(process.env.TOKEN);

function sendReply(message, text) {
  message.reply(text)
    .then(console.log("リプライ送信: " + text))
    .catch(console.error);
}

function sendMsg(channelId, text, option = {}) {
  client.channels.get(channelId).send(text, option)
    .then(console.log("メッセージ送信: " + text + JSON.stringify(option)))
    .catch(console.error);
}
