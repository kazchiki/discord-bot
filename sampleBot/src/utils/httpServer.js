const http = require('http');
const querystring = require('querystring');
const { PORT } = require('../config/config');

// HTTPサーバーを作成
function createHttpServer() {
  return http.createServer(function (req, res) {
    if (req.method === 'POST') {
      handlePostRequest(req, res);
    } else if (req.method === 'GET') {
      handleGetRequest(req, res);
    }
  });
}

// POSTリクエストを処理
function handlePostRequest(req, res) {
  let data = "";
  req.on('data', function (chunk) {
    data += chunk;
  });
  req.on('end', function () {
    if (!data) {
      res.end("No post data");
      return;
    }
    const dataObject = querystring.parse(data);
    console.log("post:" + dataObject.type);
    if (dataObject.type === "wake") {
      console.log("Woke up in post");
      res.end();
      return;
    }
    res.end();
  });
}

// GETリクエストを処理
function handleGetRequest(req, res) {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Discord Bot is active now\n');
}

// サーバーを起動
function startServer() {
  const server = createHttpServer();
  server.listen(PORT, () => {
    console.log(`HTTP server running on port ${PORT}`);
  });
  return server;
}

module.exports = {
  startServer
}; 