import https from 'node:https';

const host = 'books.aimake.cc';
const key = '8d470adea45f876b543ff67d291aa27f';
const keyLocation = `https://${host}/${key}.txt`;

const urlList = [
  `https://${host}/`,
  `https://${host}/concepts/agent-loop`,
  `https://${host}/concepts/cache-and-cost-economics`,
  `https://${host}/concepts/context-vs-memory`,
  `https://${host}/concepts/approval-vs-sandbox`,
  `https://${host}/systems/pi`,
  `https://${host}/systems/codex`,
  `https://${host}/systems/letta`,
  `https://${host}/comparisons/persisted-vs-visible`,
  `https://${host}/lab`,
  `https://${host}/feedback`,
  `https://${host}/downloads`,
];

const payload = JSON.stringify({
  host,
  key,
  keyLocation,
  urlList,
});

const req = https.request(
  'https://api.indexnow.org/indexnow',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Content-Length': Buffer.byteLength(payload),
    },
  },
  (res) => {
    console.log(`IndexNow submission response code: ${res.statusCode} (${res.statusMessage})`);
    if (res.statusCode === 200 || res.statusCode === 202) {
      console.log('✅ IndexNow successfully received the URL batch for instant indexing by Bing/Yandex.');
    } else {
      console.log(`ℹ️ Status details: ${res.statusCode}`);
    }
  }
);

req.on('error', (err) => {
  console.error('IndexNow submission failed:', err.message);
});

req.write(payload);
req.end();
