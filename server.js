// Minimal Express server: serves the static app + sync API for quiz history.
// Storage: a single JSON file on a Railway persistent volume (or fallback /tmp).

const express = require('express');
const fs = require('fs');
const path = require('path');

const PORT = parseInt(process.env.PORT || '8080', 10);
const VOLUME = process.env.RAILWAY_VOLUME_MOUNT_PATH || process.env.DATA_DIR || '/tmp/test-geografia-data';
const DATA_FILE = path.join(VOLUME, 'scores.json');

// Ensure storage directory exists.
try { fs.mkdirSync(VOLUME, { recursive: true }); } catch (e) { console.error('mkdir failed', e); }

function readAll() {
  try { return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8') || '{}'); }
  catch (e) { return {}; }
}
function writeAll(obj) {
  const tmp = DATA_FILE + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(obj));
  fs.renameSync(tmp, DATA_FILE);
}

const app = express();
app.use(express.json({ limit: '2mb' }));
app.disable('x-powered-by');

// CORS: open. The app is meant to be embedded on the same Railway domain so this
// is mostly defensive — useful only if someone opens index.html locally during dev.
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
});

// GET /api/sync — returns { profileId: [scores...] } for all profiles
app.get('/api/sync', (req, res) => {
  res.json(readAll());
});

// GET /api/sync/:profile — returns { scores: [...] } for one profile
app.get('/api/sync/:profile', (req, res) => {
  const all = readAll();
  res.json({ scores: all[req.params.profile] || [] });
});

// PUT /api/sync/:profile — replace the full scores array (used for baseline import)
// Body: { scores: [...] }
app.put('/api/sync/:profile', (req, res) => {
  const scores = Array.isArray(req.body?.scores) ? req.body.scores : null;
  if (!scores) return res.status(400).json({ error: 'body.scores must be an array' });
  const all = readAll();
  all[req.params.profile] = scores.slice(0, 200);  // cap history
  writeAll(all);
  res.json({ ok: true, count: scores.length });
});

// POST /api/sync/:profile/score — append one score (used after each quiz)
// Body: { date, score, total, difficulty, errors }
app.post('/api/sync/:profile/score', (req, res) => {
  const s = req.body;
  if (!s || typeof s.score !== 'number' || typeof s.total !== 'number') {
    return res.status(400).json({ error: 'invalid score' });
  }
  const all = readAll();
  if (!all[req.params.profile]) all[req.params.profile] = [];
  all[req.params.profile].unshift(s);
  if (all[req.params.profile].length > 200) all[req.params.profile].length = 200;
  writeAll(all);
  res.json({ ok: true });
});

// Static files (the app itself)
app.use(express.static(path.join(__dirname), {
  setHeaders: (res, filePath) => {
    if (filePath.endsWith('.html')) {
      res.setHeader('Cache-Control', 'no-cache, must-revalidate');
    }
  }
}));

// SPA fallback: serve index.html for unknown routes
app.get(/^(?!\/api\/).*/, (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Test di Geografia listening on :${PORT}, data at ${DATA_FILE}`);
});
