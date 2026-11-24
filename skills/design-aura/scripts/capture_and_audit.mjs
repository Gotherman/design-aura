#!/usr/bin/env node
/**
 * Captura screenshots multi-viewport (Dark & Light) e audita o DOM real
 * via Chrome DevTools Protocol (Chromium headless, zero dependencias npm).
 *
 * Design Aura:
 *  - Pool paralelo de abas CDP (--concurrency 4 padrao) com progresso ao vivo em stderr
 *  - Pre-injecao limpa de data-theme antes do load (elimina flash dark->light e falsos positivos de transicao)
 *  - Audita automaticamente fluxo.html, preview.html e index.html com --manifest
 *  - Reporta stack completo de erros JS (DA-JS-ERROR) e assets 404 (DA-ASSET-404)
 *  - Checagens positivas de craft e composicao: DA-DEAD-SPACE, DA-STUB-SCREEN,
 *    DA-RAW-LINK-LIST, DA-FIXED-OVERLAP, DA-SERIF-OPERATE, DA-SURFACE-FLAT,
 *    DA-CLIPPED-CONTENT, DA-MOBILE-FLEX-CLIP, DA-NAV-TRUNCATION e DA-HEADER-HSCROLL
 *
 * Uso:
 *   node capture_and_audit.mjs <arquivo-ou-url> [...] --out <dir> [--manifest screen-manifest.json]
 *        [--viewports desktop,mobile] [--themes dark,light] [--concurrency 4] [--all-viewports] [--no-vitrine] [--quiet] [--strict]
 */
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { spawn } from 'node:child_process';

import { resolveViewport, validateViewports, findBrowser } from './audit_viewports.mjs';

// Registro unico de regras: a camada de cada regra limita a severidade (heuristica nunca bloqueia).
const RULES = (() => {
  try { return JSON.parse(fs.readFileSync(new URL('../data/rules.json', import.meta.url), 'utf8')); } catch { return { rules: [], caps: {}, budgets: {}, version: '' }; }
})();
const RULE_LAYER = Object.fromEntries((RULES.rules || []).map((r) => [r.id, r.layer]));
const SEV_ORDER = { BLOCK: 0, HIGH: 1, REVIEW: 2, MEDIUM: 3, LOW: 4 };
const DEFAULT_BUDGETS = RULES.budgets?.operate || {};
function capIssue(issue) {
  const base = String(issue.rule || '').replace(/-INTERACT$/, '');
  const layer = RULE_LAYER[base];
  if (!layer) return issue;
  const limit = (RULES.caps || {})[layer];
  let severity = issue.severity;
  if (limit === 'REVIEW') severity = 'REVIEW';
  else if (limit && SEV_ORDER[severity] < SEV_ORDER[limit]) severity = limit;
  return { ...issue, severity, layer };
}
function budgetsFor(mode, overrides) {
  const m = String(mode || 'operate').toLowerCase();
  return { ...(RULES.budgets?.[m] || DEFAULT_BUDGETS), mode: m, ...(overrides || {}) };
}

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.mjs': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
};

function resolveManifestScreenPath(manifestDir, relFile) {
  const direct = path.resolve(manifestDir, relFile);
  if (fs.existsSync(direct)) return direct;
  const inTelas = path.resolve(manifestDir, 'telas', relFile);
  if (fs.existsSync(inTelas)) return inTelas;
  return direct;
}

const DEFAULT_STATE_RE = /^(populad|padr[aã]o|default|populated|cheio|normal|base)/i;
const OPEN_STATE_RE = /^(abert|p[oó]s[- ]?a[cç][aã]o|open|after|detalhe)/i;
const SPARSE_STATE_RE = /(vazi|empty|erro|error|falha|offline|carregand|loading|sem[- ]?result|sem[- ]?dados|bloquead|permiss)/i;

function slugify(text) {
  return String(text).normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'estado';
}

function normalizePrimaryAction(pa) {
  if (!pa) return null;
  if (typeof pa === 'string') return pa.trim() ? { label: pa.trim(), selector: '' } : null;
  const label = String(pa.label || '').trim();
  const selector = String(pa.selector || '').trim();
  return label || selector ? { label, selector } : null;
}

function primaryActionExpr(pa) {
  return `(() => {
    const sel = ${JSON.stringify(pa.selector || '')};
    const label = ${JSON.stringify(String(pa.label || '').trim().toLowerCase())};
    const norm = (s) => String(s || '').replace(/\\s+/g, ' ').trim().toLowerCase();
    const shown = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
    let el = null;
    try { el = sel ? document.querySelector(sel) : null; } catch (e) { el = null; }
    if (!el && label) {
      const cands = Array.from(document.querySelectorAll('button, a, [role="button"], input[type="submit"], input[type="button"]')).filter(shown);
      const text = (e) => norm(e.textContent || e.value);
      el = cands.find((e) => text(e) === label || norm(e.getAttribute('aria-label')) === label)
        || cands.find((e) => text(e).includes(label) || norm(e.getAttribute('aria-label')).includes(label));
    }
    if (!el) return { status: 'missing' };
    el.scrollIntoView({ block: 'center', inline: 'center' });
    const st = getComputedStyle(el);
    let out = { status: 'ok' };
    const r = el.getBoundingClientRect();
    if (st.visibility === 'hidden' || st.display === 'none' || parseFloat(st.opacity || '1') < 0.1 || r.width < 1 || r.height < 1) out = { status: 'blocked', reason: 'invisível ou sem área clicável' };
    else if (el.matches(':disabled') || el.getAttribute('aria-disabled') === 'true') out = { status: 'disabled' };
    else {
      const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
      if (hit && !el.contains(hit) && !hit.contains(el)) out = { status: 'blocked', reason: 'encoberta por ' + (hit.id ? '#' + hit.id : (hit.className && typeof hit.className === 'string' ? '.' + hit.className.trim().split(/\\s+/)[0] : hit.tagName.toLowerCase())) };
    }
    window.scrollTo(0, 0);
    return out;
  })()`;
}

function entriesFromManifest(manifestPath, includeVitrine, baseUrl = '') {
  const abs = path.resolve(manifestPath);
  const data = JSON.parse(fs.readFileSync(abs, 'utf8'));
  const base = path.dirname(abs);
  const normBase = (baseUrl || data.project?.appBaseUrl || '').replace(/\/+$/, '');
  const projectMode = data.project?.surfaceMode || data.project?.mode || 'operate';
  const projectBudgets = data.project?.budgets || {};
  const entries = [];
  const screenDirs = new Set();
  const missing = [];

  for (const screen of data.screens || []) {
    const route = (screen.route || '').trim();
    const file = (screen.file || '').trim();
    const state = {
      viewports: screen.viewports === undefined ? undefined : validateViewports(screen.viewports),
      clickSelector: (screen.clickSelector || '').trim(),
      afterClickSelector: (screen.afterClickSelector || '').trim(),
      budgets: budgetsFor(screen.mode || projectMode, { ...projectBudgets, ...(screen.budgets || {}) }),
      mode: String(screen.mode || projectMode).toLowerCase(),
      primaryAction: normalizePrimaryAction(screen.primaryAction),
    };
    if (state.afterClickSelector && !state.clickSelector) {
      throw new Error(`Tela ${screen.id}: afterClickSelector requer clickSelector.`);
    }
    if (route && (normBase || /^https?:\/\//i.test(route))) {
      const url = /^https?:\/\//i.test(route)
        ? route
        : `${normBase}${route.startsWith('/') ? route : '/' + route}`;
      entries.push({
        target: url,
        labelOverride: screen.id || '',
        platform: (screen.platform || '').toLowerCase() || 'responsive',
        isVitrine: false,
        ...state,
      });
      continue;
    }
    if (!file) {
      for (const viewport of state.viewports || [undefined]) {
        missing.push({ target: screen.id || route || 'Tela sem rota', viewport, detail: 'Rota requer --base-url ou arquivo válido.' });
      }
      continue;
    }
    if (/^https?:\/\//i.test(file)) {
      entries.push({
        target: file,
        labelOverride: screen.id || '',
        platform: (screen.platform || '').toLowerCase() || 'responsive',
        isVitrine: false,
        ...state,
      });
      continue;
    }
    if (file.startsWith('/') && normBase) {
      entries.push({
        target: `${normBase}${file}`,
        labelOverride: screen.id || '',
        platform: (screen.platform || '').toLowerCase() || 'responsive',
        isVitrine: false,
        ...state,
      });
      continue;
    }
    const resolved = resolveManifestScreenPath(base, file);
    screenDirs.add(path.dirname(resolved));
    entries.push({
      target: resolved,
      labelOverride: screen.id || '',
      platform: (screen.platform || '').toLowerCase() || 'responsive',
      isVitrine: false,
      ...state,
    });
  }
  // Estados declarados (vazio, erro, aberto...): viram capturas proprias ou pendencia de cobertura.
  for (const screen of data.screens || []) {
    const baseEntry = entries.find((e) => e.labelOverride === (screen.id || '') && !e.stateName);
    for (const raw of Array.isArray(screen.states) ? screen.states : []) {
      const st = typeof raw === 'string' ? { name: raw } : (raw || {});
      const name = String(st.name || '').trim();
      if (!name || DEFAULT_STATE_RE.test(name) || st.covered_by || st.coveredBy) continue;
      const hasRecipe = st.query || st.hash || st.file || st.route || st.click;
      if (!hasRecipe) {
        if (OPEN_STATE_RE.test(name) && (screen.clickSelector || '').trim()) continue; // coberto pelo pos-clique da tela
        missing.push({ target: `${screen.id}@${slugify(name)}`, viewport: undefined,
          detail: `Estado "${name}" declarado sem caminho de captura. Use {"name", "query"|"hash"|"file"|"route"|"click"} ou "covered_by": "probe".` });
        continue;
      }
      if (!baseEntry && !st.file && !st.route) {
        missing.push({ target: `${screen.id}@${slugify(name)}`, viewport: undefined, detail: `Estado "${name}": a tela base não tem captura.` });
        continue;
      }
      let target = baseEntry ? baseEntry.target : '';
      if (st.file) {
        target = /^https?:\/\//i.test(st.file) ? st.file : (st.file.startsWith('/') && normBase ? `${normBase}${st.file}` : resolveManifestScreenPath(base, st.file));
      } else if (st.route) {
        target = /^https?:\/\//i.test(st.route) ? st.route : `${normBase}${st.route.startsWith('/') ? st.route : '/' + st.route}`;
      }
      const suffix = `${st.query ? (String(st.query).startsWith('?') ? st.query : '?' + st.query) : ''}${st.hash ? (String(st.hash).startsWith('#') ? st.hash : '#' + st.hash) : ''}`;
      entries.push({
        ...(baseEntry || { platform: (screen.platform || '').toLowerCase() || 'responsive', isVitrine: false,
          budgets: budgetsFor(screen.mode || projectMode, { ...projectBudgets, ...(screen.budgets || {}) }), mode: String(screen.mode || projectMode).toLowerCase(),
          viewports: screen.viewports === undefined ? undefined : validateViewports(screen.viewports) }),
        target,
        labelOverride: `${screen.id}@${slugify(name)}`,
        stateName: name,
        budgets: { ...((baseEntry && baseEntry.budgets) || budgetsFor(screen.mode || projectMode, { ...projectBudgets, ...(screen.budgets || {}) })),
                   sparseState: SPARSE_STATE_RE.test(name) },
        urlSuffix: suffix,
        clickSelector: String(st.click || '').trim(),
        afterClickSelector: String(st.after || '').trim(),
        primaryAction: normalizePrimaryAction(st.primaryAction),
      });
    }
  }

  const vitrineViewports = data.project?.vitrineViewports === undefined
    ? undefined : validateViewports(data.project.vitrineViewports);
  if (includeVitrine) {
    const searchDirs = [...screenDirs, base];
    const seen = new Set();
    for (const name of ['entrega.html', 'fluxo.html', 'preview.html', 'index.html']) {
      for (const d of searchDirs) {
        const candidate = path.join(d, name);
        if (fs.existsSync(candidate) && !seen.has(candidate)) {
          seen.add(candidate);
          // se --base-url (ex.: serve_entrega.mjs) foi informado, audita a vitrine no servidor unificado
          // evitando 404 falso em iframes SPA (/app/*) que nao existem num servidor estatico secundario
          const target = normBase ? `${normBase}/${name}` : candidate;
          entries.push({
            target,
            labelOverride: path.basename(name, '.html'),
            platform: 'vitrine',
            isVitrine: true,
            clickSelector: '',
            viewports: vitrineViewports,
            budgets: budgetsFor('persuade'),
            mode: 'persuade',
          });
          break;
        }
      }
    }
  }
  if (vitrineViewports && !entries.some((entry) => entry.isVitrine && entry.labelOverride === 'entrega')) {
    for (const viewport of vitrineViewports) {
      missing.push({ target: 'entrega', viewport, detail: 'Vitrine declarada sem captura (arquivo ausente ou --no-vitrine).' });
    }
  }
  return { entries, manifestDir: base, missing };
}

function parseArgs(argv) {
  const args = {
    entries: [],
    out: './audit-shots',
    viewports: ['desktop', 'mobile'],
    themes: ['dark', 'light'],
    strict: false,
    manifest: '',
    manifestDir: '',
    baseUrl: '',
    includeVitrine: true,
    allViewports: false,
    smokeInteract: false,
    a11yExtra: true,
    concurrency: 4,
    quiet: false,
    missing: [],
    mode: 'operate',
    baseline: '',
    checkMotion: true,
  };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--out' && argv[i + 1]) args.out = argv[++i];
    else if (a === '--viewports' && argv[i + 1]) args.viewports = argv[++i].split(',').map((s) => s.trim()).filter(Boolean);
    else if (a === '--themes' && argv[i + 1]) args.themes = argv[++i].split(',').map((s) => s.trim()).filter(Boolean);
    else if (a === '--manifest' && argv[i + 1]) args.manifest = argv[++i];
    else if (a === '--base-url' && argv[i + 1]) args.baseUrl = argv[++i];
    else if (a === '--concurrency' && argv[i + 1]) args.concurrency = Math.max(1, Math.min(8, parseInt(argv[++i], 10) || 4));
    else if (a === '--no-vitrine') args.includeVitrine = false;
    else if (a === '--all-viewports') args.allViewports = true;
    else if (a === '--smoke-interact') args.smokeInteract = true;
    else if (a === '--quiet') args.quiet = true;
    else if (a === '--mode' && argv[i + 1]) args.mode = argv[++i];
    else if (a === '--baseline' && argv[i + 1]) args.baseline = argv[++i];
    else if (a === '--no-motion-check') args.checkMotion = false;
    else if (a === '--no-a11y-extra') args.a11yExtra = false;
    else if (a === '--strict') args.strict = true;
    else if (a === '--help' || a === '-h') {
      console.log('Uso: node capture_and_audit.mjs <arquivo|url> [...] --manifest screen-manifest.json --out <dir> [--base-url http://127.0.0.1:4188] [--viewports desktop,1920x1080,mobile-360x800] [--themes dark,light] [--concurrency 4] [--smoke-interact] [--all-viewports] [--no-vitrine] [--mode operate|read|persuade] [--baseline <dir-de-capturas-anteriores>] [--no-motion-check] [--no-a11y-extra] [--quiet] [--strict]');
      process.exit(0);
    } else {
      const isVit = /(?:entrega|fluxo|preview|index|design-bible)\.html$/i.test(a);
      args.entries.push({ target: a, platform: isVit ? 'vitrine' : 'responsive', isVitrine: isVit, clickSelector: '' });
    }
  }
  for (const e of args.entries) {
    if (!e.budgets) { e.budgets = budgetsFor(e.isVitrine ? 'persuade' : args.mode); e.mode = e.isVitrine ? 'persuade' : args.mode; }
  }
  if (args.manifest) {
    const res = entriesFromManifest(args.manifest, args.includeVitrine, args.baseUrl);
    args.manifestDir = res.manifestDir;
    args.missing = res.missing;
    args.entries.push(...res.entries);
  }
  const seen = new Set();
  args.entries = args.entries.filter((e) => {
    const address = /^https?:\/\//i.test(e.target) ? e.target : path.resolve(e.target);
    const k = JSON.stringify([address, e.labelOverride, e.viewports, e.clickSelector, e.afterClickSelector, e.urlSuffix || '']);
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
  if (!args.entries.length && !args.missing.length) {
    console.error('Erro: informe ao menos 1 arquivo HTML, URL ou --manifest.');
    process.exit(1);
  }
  args.viewports = validateViewports(args.viewports);
  if (!args.themes.length || args.themes.some((theme) => !['dark', 'light'].includes(theme))) {
    throw new Error('Temas válidos: dark e light.');
  }
  args.themes = [...new Set(args.themes)];
  return args;
}


function startStaticServer(rootDir) {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      try {
        const cleanUrl = decodeURIComponent((req.url || '/').split('?')[0]);
        let targetPath = path.resolve(rootDir, '.' + cleanUrl);
        if (!targetPath.startsWith(path.resolve(rootDir))) {
          res.writeHead(403); res.end('Forbidden'); return;
        }
        if (fs.existsSync(targetPath) && fs.statSync(targetPath).isDirectory()) {
          targetPath = path.join(targetPath, 'index.html');
        }
        if (!fs.existsSync(targetPath)) {
          res.writeHead(404); res.end('Not found'); return;
        }
        const ext = path.extname(targetPath).toLowerCase();
        res.writeHead(200, { 'Content-Type': MIME_TYPES[ext] || 'application/octet-stream' });
        fs.createReadStream(targetPath).pipe(res);
      } catch (err) {
        res.writeHead(500); res.end(String(err));
      }
    });
    server.on('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const addr = server.address();
      resolve({ server, port: addr.port });
    });
  });
}

function launchBrowser(browserPath) {
  return new Promise((resolve, reject) => {
    const userDataDir = fs.mkdtempSync('/tmp/da-cdp-');
    const proc = spawn(browserPath, [
      '--headless=new',
      '--no-sandbox',
      '--disable-gpu',
      '--disable-dev-shm-usage',
      '--disable-background-networking',
      '--remote-debugging-port=0',
      `--user-data-dir=${userDataDir}`,
      'about:blank',
    ], { stdio: ['ignore', 'pipe', 'pipe'] });

    let stderrBuf = '';
    const timer = setTimeout(() => {
      proc.kill('SIGKILL');
      reject(new Error(`Timeout ao iniciar Chromium: ${stderrBuf}`));
    }, 15000);

    proc.stderr.on('data', (chunk) => {
      stderrBuf += chunk.toString();
      const m = stderrBuf.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if (m) {
        clearTimeout(timer);
        const wsUrl = new URL(m[1]);
        resolve({ proc, port: Number(wsUrl.port), browserWsUrl: m[1], userDataDir });
      }
    });
    proc.on('exit', (code) => {
      clearTimeout(timer);
      reject(new Error(`Chromium encerrou prematuramente (${code}): ${stderrBuf}`));
    });
  });
}

class CDPClient {
  constructor(wsUrl) {
    this.ws = new WebSocket(wsUrl);
    this.nextId = 1;
    this.pending = new Map();
    this.events = new Map();
  }
  async connect() {
    await new Promise((resolve, reject) => {
      this.ws.addEventListener('open', resolve, { once: true });
      this.ws.addEventListener('error', reject, { once: true });
    });
    this.ws.addEventListener('message', (ev) => {
      const msg = JSON.parse(String(ev.data));
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(msg.error.message || JSON.stringify(msg.error)));
        else resolve(msg.result);
      } else if (msg.method) {
        const list = (this.events.get(msg.method) || []).slice();
        list.forEach((fn) => fn(msg.params));
      }
    });
  }
  on(method, fn) {
    if (!this.events.has(method)) this.events.set(method, []);
    this.events.get(method).push(fn);
  }
  off(method, fn) {
    const list = this.events.get(method);
    if (!list) return;
    const idx = list.indexOf(fn);
    if (idx >= 0) list.splice(idx, 1);
  }
  once(method, fn) {
    const wrapped = (params) => {
      this.off(method, wrapped);
      fn(params);
    };
    this.on(method, wrapped);
    return wrapped;
  }
  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
  close() {
    try { this.ws.close(); } catch {}
  }
}

const DOM_AUDIT_FN = `(() => {
  const issues = [];
  const B = Object.assign(${JSON.stringify(DEFAULT_BUDGETS)}, window.__DA_BUDGETS__ || {});
  // Sites (Persuade) e leitura (Read) tem outra gramatica: links sublinhados, pouco controle e muito respiro sao normais.
  const isAppMode = !B.mode || B.mode === 'operate';
  const docEl = document.documentElement;
  const isMobile = window.innerWidth <= 480;
  const isDesktop = window.innerWidth >= 1024;
  const isVitrine = !!document.querySelector('.fx-app, .pv-app, .g-shell, .specimen-sheet, .da-hub, [data-hub="true"]') || /(?:design-bible|entrega)\.html$/i.test(location.pathname);
  const titlePath = (document.title + ' ' + location.pathname).toLowerCase();
  const isAuthPage = !!document.querySelector('input[type="password"]') || /(?:login|entrada|acesso|auth|signin|signup|cadastro|2fa)/.test(titlePath);

  function parseRgb(str) {
    const m = str && str.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
    if (!m) return null;
    return [Number(m[1]), Number(m[2]), Number(m[3]), m[4] !== undefined ? Number(m[4]) : 1];
  }
  // Normaliza qualquer cor CSS (rgb, oklch, color(srgb), color-mix resolvido) via canvas 1x1.
  const colorCtx = (() => { try { const c = document.createElement('canvas'); c.width = c.height = 1; return c.getContext('2d', { willReadFrequently: true }); } catch (e) { return null; } })();
  const colorCache = new Map();
  function colorOf(str) {
    if (!str || str === 'transparent' || str === 'none') return null;
    if (colorCache.has(str)) return colorCache.get(str);
    let out = parseRgb(str);
    if (!out && colorCtx) {
      colorCtx.clearRect(0, 0, 1, 1);
      colorCtx.fillStyle = 'rgba(1, 2, 3, 0)';
      colorCtx.fillStyle = str;
      if (colorCtx.fillStyle !== 'rgba(1, 2, 3, 0)') {
        colorCtx.fillRect(0, 0, 1, 1);
        const d = colorCtx.getImageData(0, 0, 1, 1).data;
        out = [d[0], d[1], d[2], d[3] / 255];
      }
    }
    colorCache.set(str, out);
    return out;
  }
  const GRADIENT_COLOR_RE = /(rgba?\\([^)]*\\)|color\\([^)]*\\)|oklch\\([^)]*\\)|oklab\\([^)]*\\)|lab\\([^)]*\\)|lch\\([^)]*\\)|hsla?\\([^)]*\\)|#[0-9a-fA-F]{3,8}\\b)/g;
  function pageCanvas() {
    const scheme = getComputedStyle(docEl).colorScheme || '';
    return (/dark/.test(scheme) && !/light/.test(scheme)) ? [18, 18, 18, 1] : [255, 255, 255, 1];
  }
  function blend(top, bottom) {
    const a = top[3];
    return [top[0] * a + bottom[0] * (1 - a), top[1] * a + bottom[1] * (1 - a), top[2] * a + bottom[2] * (1 - a), 1];
  }
  // Fundos reais atras do elemento: compoe camadas semitransparentes e, em gradiente, devolve um fundo por
  // parada de cor (o contraste vale contra a pior). null = imagem atras do texto, nao da para julgar.
  function resolveBgs(el) {
    const layers = [];
    let cur = el;
    while (cur && cur.nodeType === 1) {
      const cs = getComputedStyle(cur);
      const bi = cs.backgroundImage;
      let opaque = false;
      if (bi && bi !== 'none') {
        if (/url\\(/.test(bi)) return null;
        const stops = (bi.match(GRADIENT_COLOR_RE) || []).map(colorOf).filter(Boolean);
        if (stops.length) {
          layers.push(stops);
          opaque = stops.every((c) => c[3] >= 0.99);
        }
      }
      const c = colorOf(cs.backgroundColor);
      if (!opaque && c && c[3] > 0) {
        layers.push([c]);
        opaque = c[3] >= 0.99;
      }
      if (opaque) break;
      cur = cur.parentElement;
    }
    let cands = [pageCanvas()];
    for (let i = layers.length - 1; i >= 0; i--) {
      const next = [];
      for (const b of cands) for (const t of layers[i]) next.push(blend(t, b));
      cands = next.slice(0, 8);
    }
    return cands;
  }
  function resolveBg(el) {
    const all = resolveBgs(el);
    return all && all.length ? all[0] : pageCanvas();
  }
  function lum(rgb) {
    const [r, g, b] = rgb.slice(0, 3).map((v) => {
      const c = v / 255;
      return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }

  // 1. Overflow horizontal
  if (docEl.scrollWidth > window.innerWidth + 2) {
    issues.push({ severity: 'BLOCK', rule: 'DA-DOM-OVERFLOW', detail: 'Overflow horizontal: scrollWidth=' + docEl.scrollWidth + ' > innerWidth=' + window.innerWidth });
  }

  // 2. Imagens quebradas ou sem alt
  for (const img of document.querySelectorAll('img')) {
    const st = getComputedStyle(img);
    if (st.display === 'none' || st.visibility === 'hidden') continue;
    if (!img.hasAttribute('alt')) {
      issues.push({ severity: 'BLOCK', rule: 'DA-B10-03', detail: 'Imagem sem alt: ' + (img.getAttribute('src') || 'inline') });
    }
    if (img.complete && img.naturalWidth === 0) {
      issues.push({ severity: 'BLOCK', rule: 'DA-B10-IMG', detail: 'Imagem quebrada (naturalWidth=0): ' + (img.getAttribute('src') || '') });
    }
  }

  // 3. Alvos de toque mobile < 44x44px em controles principais
  if (isMobile) {
    let smallCount = 0;
    const samples = [];
    for (const el of document.querySelectorAll('button, [role="button"], input:not([type="hidden"]), select')) {
      if (el.closest('.fx-world, [data-canvas-world]')) continue;
      const r = el.getBoundingClientRect();
      const st = getComputedStyle(el);
      if (st.display === 'none' || st.visibility === 'hidden' || r.width === 0 || r.height === 0) continue;
      if (r.width < 40 || r.height < 40) {
        smallCount++;
        if (samples.length < 3) samples.push((el.tagName.toLowerCase()) + ' (' + Math.round(r.width) + 'x' + Math.round(r.height) + ')');
      }
    }
    if (smallCount > 0) {
      issues.push({ severity: 'HIGH', rule: 'DA-B3-03', detail: smallCount + ' controles mobile menores que 44px: ' + samples.join(', ') });
    }
  }

  // 4. Texto corpo < 12px
  let tinyText = 0;
  for (const el of document.querySelectorAll('p, li, td, label')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    const fs = parseFloat(getComputedStyle(el).fontSize || '14');
    if (fs < 11.5 && (el.textContent || '').trim().length > 0) tinyText++;
  }
  if (tinyText > 0) {
    issues.push({ severity: 'HIGH', rule: 'DA-B3-03', detail: tinyText + ' blocos de texto abaixo de 12px' });
  }

  // 5. Inputs sem label visivel nem aria-label
  for (const inp of document.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]), select, textarea')) {
    const r = inp.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    const hasAria = inp.hasAttribute('aria-label') || inp.hasAttribute('aria-labelledby');
    const hasFor = inp.id && document.querySelector('label[for="' + CSS.escape(inp.id) + '"]');
    const wrapped = !!inp.closest('label');
    if (!hasAria && !hasFor && !wrapped) {
      issues.push({ severity: 'BLOCK', rule: 'DA-B9-01', detail: 'Campo sem label acessivel: ' + (inp.getAttribute('placeholder') || inp.name || inp.tagName) });
    }
  }

  // 6. Amostra de contraste real computado (inclui emblemas/monogramas/badges em div/span)
  let contrastFails = 0;
  const contrastSamples = [];
  let gradientEdge = 0;
  const gradientSamples = [];
  const primaryTextEls = Array.from(document.querySelectorAll('h1,h2,h3,p,a,button,td,th')).slice(0, 60);
  const emblemBadgeEls = Array.from(document.querySelectorAll('[class*="emblem"],[class*="monogram"],[class*="badge"],[class*="chip"],[class*="pill"],[class*="avatar"],[class*="logo"]')).filter((el) => {
    if (el.children.length > 1) return false;
    const txt = (el.textContent || '').trim();
    return txt.length >= 1 && txt.length <= 26;
  }).slice(0, 30);
  const textEls = [...new Set([...primaryTextEls, ...emblemBadgeEls])];
  for (const el of textEls) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0 || !(el.textContent || '').trim()) continue;
    const st = getComputedStyle(el);
    if (parseFloat(st.opacity || '1') < 0.5) continue;
    // Texto de logotipo ou marca nao tem exigencia de contraste (WCAG 1.4.3).
    const cls = (typeof el.className === 'string' ? el.className : '') + ' ' + ((el.parentElement && typeof el.parentElement.className === 'string') ? el.parentElement.className : '');
    if (/(^|[\\s_-])(logo|wordmark|brand-mark|logotipo)([\\s_-]|$)/i.test(cls)) continue;
    const fg = colorOf(st.color);
    const bgs = resolveBgs(el);
    if (!fg || !bgs || !bgs.length || fg[3] < 0.8) continue;
    const ratioOf = (bg) => { const l1 = lum(fg), l2 = lum(bg); return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05); };
    let ratio = 99;
    for (const bg of bgs) ratio = Math.min(ratio, ratioOf(bg));
    // Gradiente: se so a parada extrema reprova e o meio passa, e caso de olhar a captura (REVIEW), nao falha.
    let meanRatio = ratio;
    if (bgs.length > 1) {
      const avg = [0, 1, 2].map((k) => bgs.reduce((acc, b) => acc + b[k], 0) / bgs.length).concat([1]);
      meanRatio = ratioOf(avg);
    }
    const fs = parseFloat(st.fontSize || '14');
    const fw = parseInt(st.fontWeight || '400', 10);
    const minReq = (fs >= 24 || (fs >= 18.66 && fw >= 700)) ? 3.0 : 4.5;
    if (ratio < minReq && meanRatio >= minReq) {
      gradientEdge++;
      if (gradientSamples.length < 2) {
        const cls = (typeof el.className === 'string' && el.className.trim()) ? '.' + el.className.trim().split(/\\s+/)[0] : el.tagName.toLowerCase();
        gradientSamples.push(cls + ' "' + (el.textContent || '').trim().slice(0, 20) + '" (' + ratio.toFixed(2) + ':1 na parada extrema, ' + meanRatio.toFixed(2) + ':1 no meio)');
      }
    } else if (ratio < minReq) {
      contrastFails++;
      if (contrastSamples.length < 2) {
        const cls = (typeof el.className === 'string' && el.className.trim()) ? '.' + el.className.trim().split(/\\s+/)[0] : el.tagName.toLowerCase();
        contrastSamples.push(cls + ' "' + (el.textContent || '').trim().slice(0, 20) + '" (' + ratio.toFixed(2) + ':1)');
      }
    }
  }
  if (gradientEdge > 0) {
    issues.push({ severity: 'REVIEW', rule: 'DA-B3-01', detail: gradientEdge + ' texto(s) sobre gradiente reprovam só na parada extrema: ' + gradientSamples.join(', ') + '. Confira na captura se alguma letra fica sobre a parte fraca.' });
  }
  if (contrastFails > 0) {
    issues.push({ severity: 'HIGH', rule: 'DA-B3-01', detail: contrastFails + ' elementos amostrados com contraste abaixo do minimo WCAG AA: ' + contrastSamples.join(', ') });
  }

  // 7. Raios iguais aninhados com padding curto (concentricidade)
  let pinched = 0;
  const radiusNodes = document.querySelectorAll('div, article, section, li, a, button');
  for (const el of Array.from(radiusNodes).slice(0, 200)) {
    const st = getComputedStyle(el);
    const pad = Math.min(parseFloat(st.paddingTop) || 0, parseFloat(st.paddingLeft) || 0);
    const outer = parseFloat(st.borderTopLeftRadius) || 0;
    if (pad < 4 || pad > 24 || outer < 8) continue;
    const child = el.firstElementChild;
    if (!child) continue;
    const inner = parseFloat(getComputedStyle(child).borderTopLeftRadius) || 0;
    if (inner >= 8 && Math.abs(inner - outer) < 1) pinched++;
  }
  if (pinched > 0) {
    issues.push({ severity: 'HIGH', rule: 'DA-B7-01', detail: pinched + ' pares com o mesmo raio aninhado e padding <= 24px' });
  }

  // 8. Scroll aninhado acidental
  function canScroll(el) {
    if (!el || el === document.body || el === document.documentElement) return false;
    const st = getComputedStyle(el);
    if (st.overflowY !== 'auto' && st.overflowY !== 'scroll') return false;
    return el.scrollHeight > el.clientHeight + 8;
  }
  let nestedScroll = 0;
  for (const el of Array.from(document.querySelectorAll('div, section, main, ul')).slice(0, 300)) {
    if (!canScroll(el)) continue;
    let parent = el.parentElement;
    while (parent) {
      if (canScroll(parent)) { nestedScroll++; break; }
      parent = parent.parentElement;
    }
  }
  if (nestedScroll > 0) {
    issues.push({ severity: 'MEDIUM', rule: 'DA-B10-02', detail: nestedScroll + ' regioes com scroll aninhado' });
  }

  // 9. Numeros de tabela sem alinhamento a direita
  let ragged = 0;
  for (const cell of document.querySelectorAll('td')) {
    const text = (cell.textContent || '').trim();
    if (!/^[-+R$€£]?\\d[\\d.,\\s%]*$/.test(text)) continue;
    const align = getComputedStyle(cell).textAlign;
    if (align !== 'right' && align !== 'end') ragged++;
  }
  if (ragged > 0) {
    issues.push({ severity: 'HIGH', rule: 'DA-B8-03', detail: ragged + ' celulas numericas sem alinhamento a direita' });
  }

  // === CHECAGENS POSITIVAS DE CRAFT, COMPOSICAO E SUBSTANCIA ===
  if (!isVitrine) {
    const mainEl = document.querySelector('main') || document.body;

    // 10. DA-FIXED-OVERLAP: barra inferior fixa cobrindo conteudo visivel mesmo no fim da rolagem
    const fixedBars = [];
    for (const el of document.querySelectorAll('nav, footer, div, aside, header')) {
      const st = getComputedStyle(el);
      if (st.display === 'none' || st.visibility === 'hidden') continue;
      if (st.position !== 'fixed' && st.position !== 'sticky') continue;
      const r = el.getBoundingClientRect();
      if (r.height >= 40 && r.height <= 120 && r.width >= window.innerWidth * 0.6 && r.bottom >= window.innerHeight - 8 && r.top > window.innerHeight * 0.5) {
        fixedBars.push({ el, rect: r });
      }
    }
    if (fixedBars.length > 0) {
      const prevY = window.scrollY;
      window.scrollTo(0, docEl.scrollHeight);
      const bar = fixedBars[0];
      const barRect = bar.el.getBoundingClientRect();
      let clipped = 0;
      const samples = [];
      for (const node of mainEl.querySelectorAll('p, li, a, button, td, h2, h3, label, input, textarea')) {
        if (bar.el.contains(node)) continue;
        const st = getComputedStyle(node);
        if (st.display === 'none' || st.visibility === 'hidden') continue;
        const r = node.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) continue;
        if (r.bottom > barRect.top + 6 && r.top < barRect.bottom - 2) {
          clipped++;
          if (samples.length < 2) samples.push((node.textContent || node.tagName).trim().slice(0, 28));
        }
      }
      window.scrollTo(0, prevY);
      if (clipped > 0) {
        issues.push({ severity: 'BLOCK', rule: 'DA-FIXED-OVERLAP', detail: clipped + ' elemento(s) cortado(s)/encoberto(s) pela barra fixa inferior: ' + samples.join(', ') });
      }
    }

    // 11. DA-RAW-LINK-LIST: links <a> sublinhados crus em listas/tabelas/menus de app
    let rawLinks = 0;
    for (const a of (isAppMode ? document.querySelectorAll('li a, td a, nav a, [role="list"] a, [class*="list"] a, [class*="row"] a, [class*="item"] a') : [])) {
      const r = a.getBoundingClientRect();
      const st = getComputedStyle(a);
      if (st.display === 'none' || st.visibility === 'hidden' || r.width === 0 || r.height === 0) continue;
      if ((a.textContent || '').trim().length < 2) continue;
      if ((st.textDecorationLine || '').includes('underline')) {
        rawLinks++;
      }
    }
    if (rawLinks >= 1) {
      issues.push({ severity: 'HIGH', rule: 'DA-RAW-LINK-LIST', detail: rawLinks + ' link(s) <a> sublinhado(s) cru(s) dentro de listas/tabelas/menus de aplicativo' });
    }

    // 12. DA-SERIF-OPERATE: fonte serifada editorial em sistema operacional sem opt-in
    const hasAppChrome = !!document.querySelector('table, aside, nav, [class*="sidebar"], [class*="shell"], [class*="toolbar"], [class*="inbox"], [class*="phone"]');
    if (hasAppChrome && docEl.getAttribute('data-allow-serif') !== 'true' && document.body.getAttribute('data-allow-serif') !== 'true') {
      const serifPat = /(?:source serif|georgia|palatino|times new roman|merriweather|playfair|garamond|iowan|baskerville|^serif$|,\\s*serif$)/i;
      const headEl = document.querySelector('h1') || document.querySelector('h2');
      const headFont = headEl ? getComputedStyle(headEl).fontFamily : '';
      const bodyFont = getComputedStyle(document.body).fontFamily || '';
      if (serifPat.test(headFont) || serifPat.test(bodyFont)) {
        issues.push({ severity: 'HIGH', rule: 'DA-SERIF-OPERATE', detail: 'Tipografia serifada editorial em tela operacional Operate: ' + (headFont || bodyFont).slice(0, 60) });
      }
    }

    // 13. DA-STUB-SCREEN: tabelas operacionais rasas (1-2 linhas) ou tela casca quase vazia
    // Estado declarado como vazio, erro ou carregando e raso por definicao: nao recebe este sinal.
    if (!isAuthPage && isAppMode && !B.sparseState) {
      let stubTables = 0;
      for (const tbl of document.querySelectorAll('table')) {
        const st = getComputedStyle(tbl);
        const r = tbl.getBoundingClientRect();
        if (st.display === 'none' || r.width === 0 || r.height === 0) continue;
        const rows = Array.from(tbl.querySelectorAll('tbody tr')).filter((tr) => {
          const rs = getComputedStyle(tr);
          return rs.display !== 'none' && (tr.textContent || '').trim().length > 0;
        });
        if (rows.length >= 1 && rows.length <= 2) stubTables++;
      }
      if (stubTables > 0) {
        issues.push({ severity: 'HIGH', rule: 'DA-STUB-SCREEN', detail: stubTables + ' tabela(s) operacional(is) rasa(s) com apenas 1-2 linhas (parece stub vazio)' });
      }

      const leafNodes = Array.from(mainEl.querySelectorAll('tr, li, article, button, input, select, textarea, svg, canvas, [class*="card"], [class*="kpi"], [class*="metric"], [class*="row"], [class*="item"]')).filter((el) => {
        const st = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        return st.display !== 'none' && st.visibility !== 'hidden' && r.width > 12 && r.height > 12;
      });
      const hasFocusedForm = leafNodes.length < 4 && Array.from(mainEl.querySelectorAll('form')).some((form) => {
        const controls = leafNodes.filter((el) => form.contains(el));
        const hasLabeledField = controls.some((el) => el.matches('input, select, textarea') && el.labels?.length);
        const hasAction = controls.some((el) => el.matches('button, input[type="submit"]') && !el.disabled);
        return hasLabeledField && hasAction;
      });
      if (leafNodes.length < 4 && !hasFocusedForm) {
        issues.push({ severity: 'HIGH', rule: 'DA-STUB-SCREEN', detail: 'Tela operacional rasa com apenas ' + leafNodes.length + ' elementos estruturais/interativos visiveis' });
      }
    }

    // 14. DA-DEAD-SPACE: vazio morto em desktop (1440x900) + inspector/aside vazio ou subaproveitado
    if (isDesktop && !isAuthPage && B.mode !== 'persuade' && !B.sparseState) {
      for (const aside of document.querySelectorAll('aside, [class*="inspector"], [class*="detail-pane"], [class*="side-panel"]')) {
        const st = getComputedStyle(aside);
        const r = aside.getBoundingClientRect();
        if (st.display === 'none' || st.visibility === 'hidden') continue;
        // Sidebar de navegacao nao e inspector: o vazio abaixo do menu e esperado.
        if (aside.querySelector('nav, [role="navigation"]') || aside.matches('[class*="sidebar"], [class*="nav"]') || r.left < 24) continue;
        if (r.width >= 200 && r.height >= 280 && r.left < window.innerWidth && r.right > 0) {
          const txtLen = (aside.textContent || '').replace(/\\s+/g, ' ').trim().length;
          const meaningful = Array.from(aside.querySelectorAll('p, li, dd, tr, button, a, input, canvas, svg, [class*="row"], [class*="item"], [class*="kpi"], [class*="card"]')).filter((el) => {
            const es = getComputedStyle(el);
            const er = el.getBoundingClientRect();
            return es.display !== 'none' && er.width > 8 && er.height > 8;
          }).length;
          let maxBot = r.top;
          for (const leaf of aside.querySelectorAll('*')) {
            if (leaf.children.length > 0 && leaf.tagName !== 'SVG' && leaf.tagName !== 'CANVAS') continue;
            const ls = getComputedStyle(leaf);
            const lr = leaf.getBoundingClientRect();
            if (ls.display === 'none' || lr.height < 4 || lr.width < 4) continue;
            if ((leaf.textContent || '').trim() || leaf.tagName === 'SVG' || leaf.tagName === 'CANVAS' || leaf.tagName === 'IMG') {
              if (lr.bottom > maxBot) maxBot = lr.bottom;
            }
          }
          const usedRatio = (maxBot - r.top) / Math.max(1, r.height);
          const isTallSparseAside = r.height >= 500 && usedRatio < 0.45 && txtLen < 180;
          if (txtLen < 48 || meaningful < 2 || isTallSparseAside) {
            const emptyPct = Math.max(0, Math.round((1 - usedRatio) * 100));
            issues.push({ severity: 'HIGH', rule: 'DA-DEAD-SPACE', detail: 'Painel lateral/inspector subaproveitado (~' + emptyPct + '% vazio, ' + txtLen + ' chars em ' + Math.round(r.width) + 'x' + Math.round(r.height) + 'px)' });
          }
        }
      }

      const mr = mainEl.getBoundingClientRect();
      const vx1 = Math.max(0, mr.left);
      const vy1 = Math.max(0, mr.top);
      const workspace = mainEl.closest('[data-da-workspace]');
      const workspaceRight = workspace?.getBoundingClientRect().right;
      const vx2 = Math.min(window.innerWidth, Math.max(workspaceRight ?? mr.right, vx1 + 600));
      // Mede contra a altura util real da viewport (nao apenas mr.bottom) para detectar telas que morrem no terco superior!
      const vy2 = window.innerHeight;
      const vw = Math.max(0, vx2 - vx1), vh = Math.max(0, vy2 - vy1);
      if (vw >= 500 && vh >= 480) {
        const cols = 12, rows = 8;
        const grid = new Uint8Array(cols * rows);
        const blocks = mainEl.querySelectorAll('h1, h2, h3, h4, p, li, td, th, button, a, input, select, textarea, svg, canvas, img, figure, [class*="kpi"], [class*="chart"], [class*="badge"], [class*="pill"], [class*="bubble"]');
        for (const b of blocks) {
          const st = getComputedStyle(b);
          if (st.display === 'none' || st.visibility === 'hidden' || parseFloat(st.opacity || '1') < 0.1) continue;
          const r = b.getBoundingClientRect();
          if (r.width < 8 || r.height < 8) continue;
          if (r.width > vw * 0.96 && r.height > vh * 0.85) continue;
          const x1 = Math.max(vx1, r.left), y1 = Math.max(vy1, r.top);
          const x2 = Math.min(vx2, r.right), y2 = Math.min(vy2, r.bottom);
          if (x2 <= x1 || y2 <= y1) continue;
          const c1 = Math.max(0, Math.floor(((x1 - vx1) / vw) * cols));
          const c2 = Math.min(cols - 1, Math.floor(((x2 - vx1 - 1) / vw) * cols));
          const r1 = Math.max(0, Math.floor(((y1 - vy1) / vh) * rows));
          const r2 = Math.min(rows - 1, Math.floor(((y2 - vy1 - 1) / vh) * rows));
          for (let gy = r1; gy <= r2; gy++) {
            for (let gx = c1; gx <= c2; gx++) grid[gy * cols + gx] = 1;
          }
        }
        let filled = 0;
        for (let i = 0; i < grid.length; i++) filled += grid[i];
        const fillRatio = filled / grid.length;
        const emptyPct = Math.round((1 - fillRatio) * 100);
        const reviewFill = 1 - (B.deadSpaceReviewPct / 100);
        if (fillRatio < reviewFill) {
          issues.push({ severity: 'REVIEW', rule: 'DA-DEAD-SPACE', detail: 'Area principal desktop com ~' + emptyPct + '% sem conteudo (orcamento do projeto: ' + B.deadSpaceReviewPct + '%). Confirme na captura se o vazio e respiro intencional ou falta de estrutura.' });
        }
      }
    }

    // 15. DA-SURFACE-FLAT: falta de separacao visual Z1 vs Z2
    if (!isAuthPage && isAppMode && !B.sparseState) {
      const bodyLum = lum(resolveBg(document.body));
      const containers = Array.from(mainEl.querySelectorAll('section, article, table, aside, [class*="card"], [class*="panel"], [class*="sheet"], [class*="box"], [class*="surface"]')).filter((el) => {
        const st = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        return st.display !== 'none' && r.width >= 160 && r.height >= 60;
      });
      // Itens de lista com borda propria (ou no link-cartao interno) tambem separam os planos.
      const borderedItem = Array.from(mainEl.querySelectorAll('li, li > a, [role="listitem"], [class*="item"], [class*="row"]')).slice(0, 60).some((el) => {
        const st = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        const bw = parseFloat(st.borderTopWidth || '0') + parseFloat(st.borderBottomWidth || '0');
        const bc = colorOf(st.borderTopColor) || colorOf(st.borderBottomColor);
        return r.width >= 160 && r.height >= 32 && bw >= 1 && bc && bc[3] > 0.08;
      });
      if (containers.length >= 1) {
        let elevated = 0;
        if (borderedItem) elevated++;
        for (const el of containers.slice(0, 40)) {
          const st = getComputedStyle(el);
          const bg = colorOf(st.backgroundColor);
          const hasBgDelta = bg && bg[3] > 0.5 && Math.abs(lum(bg) - bodyLum) >= 0.012;
          const bw = parseFloat(st.borderTopWidth || '0') + parseFloat(st.borderLeftWidth || '0');
          const bc = colorOf(st.borderTopColor);
          const hasBorder = bw >= 1 && bc && bc[3] > 0.08;
          const hasShadow = st.boxShadow && st.boxShadow !== 'none';
          if (hasBgDelta || hasBorder || hasShadow) elevated++;
        }
        if (elevated === 0) {
          issues.push({ severity: 'HIGH', rule: 'DA-SURFACE-FLAT', detail: 'Superficies Z2 sem separacao visual perceptivel do canvas Z1 (sem borda, elevacao ou delta de luminosidade)' });
        }
      }
    }

    // 16. DA-CARD-INTERNAL-VOID: buraco vertical vazio (> 95px) dentro de um card Z2 esticado em Bento Grid
    if (isDesktop && !isAuthPage) {
      let voidCards = 0;
      const voidSamples = [];
      const cards = mainEl.querySelectorAll('article, section, [class*="panel-z2"], [class*="card"]');
      for (const card of Array.from(cards).slice(0, 30)) {
        const st = getComputedStyle(card);
        const cr = card.getBoundingClientRect();
        if (st.display === 'none' || cr.width < 220 || cr.height < 220 || cr.width > window.innerWidth * 0.75) continue;
        const kids = Array.from(card.children).filter((ch) => {
          const cs = getComputedStyle(ch);
          const r = ch.getBoundingClientRect();
          return cs.display !== 'none' && cs.visibility !== 'hidden' && cs.position !== 'absolute' && r.height >= 12 && r.width >= 40;
        });
        if (kids.length >= 2 && kids.length <= 6) {
          kids.sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
          for (let i = 0; i < kids.length - 1; i++) {
            const r1 = kids[i].getBoundingClientRect();
            const r2 = kids[i + 1].getBoundingClientRect();
            const gap = r2.top - r1.bottom;
            if (gap > B.cardVoidPx) {
              voidCards++;
              const title = (card.querySelector('h2, h3, h4, strong')?.textContent || card.className || 'card').trim().slice(0, 32);
              if (voidSamples.length < 2) voidSamples.push(title + ' (' + Math.round(gap) + 'px vazio interno)');
              break;
            }
          }
        }
      }
      if (voidCards > 0) {
        issues.push({ severity: 'MEDIUM', rule: 'DA-CARD-INTERNAL-VOID', detail: voidCards + ' card(s) com buraco vertical interno > ' + B.cardVoidPx + 'px (provavel space-between/margin-top:auto): ' + voidSamples.join(', ') });
      }
    }

    // 17. DA-CLIPPED-CONTENT & DA-MOBILE-FLEX-CLIP: detecta cards/paineis cortando proprio conteudo ou flex-column rolavel que esmaga filhos overflow:hidden
    {
      let clippedCards = 0;
      const clipSamples = [];
      for (const el of Array.from(mainEl.querySelectorAll('section, article, div, aside, ul, ol')).slice(0, 260)) {
        const st = getComputedStyle(el);
        if (st.display === 'none' || st.visibility === 'hidden') continue;
        const r = el.getBoundingClientRect();
        if (r.width < 80 || r.height < 36) continue;
        // Ignora truncamento intencional de texto em 1 linha (text-overflow: ellipsis) e line-clamp
        if (st.textOverflow === 'ellipsis' || (st.webkitLineClamp && st.webkitLineClamp !== 'none')) continue;
        if (st.overflowY === 'hidden' || st.overflowY === 'clip') {
          if (el.scrollHeight > el.clientHeight + 8) {
            // Verifica se ha texto/elemento real alem do fundo do card
            const hasRealInnerOverflow = Array.from(el.children).some((ch) => {
              const cs = getComputedStyle(ch);
              if (cs.display === 'none' || cs.position === 'absolute') return false;
              return ch.getBoundingClientRect().bottom > r.bottom + 5;
            });
            if (hasRealInnerOverflow) {
              clippedCards++;
              const lbl = (el.querySelector('h2, h3, h4, strong')?.textContent || el.className || el.tagName).trim().slice(0, 32);
              if (clipSamples.length < 3) clipSamples.push(lbl + ' (' + Math.round(el.scrollHeight) + 'px > ' + Math.round(el.clientHeight) + 'px)');
            }
          }
        }
      }
      if (clippedCards > 0) {
        issues.push({ severity: 'BLOCK', rule: 'DA-CLIPPED-CONTENT', detail: clippedCards + ' card(s)/painel(is) cortando proprio conteudo verticalmente com overflow:hidden: ' + clipSamples.join(', ') });
      }

      // Detecta bomba-relogio de flex-shrink em containers rolaveis (ex.: .mob-scroll flex-direction: column onde filhos com overflow:hidden nao tem flex-shrink: 0)
      let shrinkBombs = 0;
      for (const container of document.querySelectorAll('main, [class*="scroll"], [class*="mob-body"], [class*="sheet-panel"]')) {
        const st = getComputedStyle(container);
        if (st.display !== 'flex' || st.flexDirection !== 'column') continue;
        for (const ch of Array.from(container.children)) {
          const cs = getComputedStyle(ch);
          if (cs.display === 'none' || cs.position === 'fixed' || cs.position === 'absolute') continue;
          if ((cs.overflowY === 'hidden' || cs.overflow === 'hidden') && parseFloat(cs.flexShrink || '1') > 0 && ch.getBoundingClientRect().height >= 48) {
            shrinkBombs++;
          }
        }
      }
      if (shrinkBombs > 0) {
        issues.push({ severity: 'BLOCK', rule: 'DA-MOBILE-FLEX-CLIP', detail: shrinkBombs + ' card(s) com overflow:hidden dentro de container flex-column sem flex-shrink:0 (esmaga e corta texto ao abrir no mockup/preview!)' });
      }
    }

    // 19. DA-BADGE-ECHO: mesmo texto de badge/chip repetido >= 4x na mesma vista poluindo lista
    {
      const counts = new Map();
      for (const el of Array.from(mainEl.querySelectorAll('[class*="badge"], [class*="chip"], [class*="pill"], [class*="status"], [class*="tag"]')).slice(0, 160)) {
        const st = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        if (st.display === 'none' || st.visibility === 'hidden' || r.width < 12 || r.height < 12) continue;
        const txt = (el.textContent || '').replace(/\\s+/g, ' ').trim();
        if (txt.length < 3 || txt.length > 32 || /^[\\d.,%+\\-/: ]+$/.test(txt)) continue;
        const key = txt.toLowerCase();
        counts.set(key, (counts.get(key) || 0) + 1);
      }
      for (const [k, cnt] of counts.entries()) {
        if (cnt >= 4) {
          issues.push({ severity: 'HIGH', rule: 'DA-BADGE-ECHO', detail: 'Selo-eco "' + k + '" repetido ' + cnt + 'x na mesma lista/aba (exiba selos apenas para excecoes ou estados distintos)' });
          break;
        }
      }
    }

    // 20. DA-MOBILE-HERO-BLOAT: hero + banners de aviso no topo do mobile consumindo > 38% da tela antes da lista principal
    if (isMobile && !isAuthPage) {
      const heroEls = Array.from(mainEl.querySelectorAll('[class*="hero"], [class*="alert"], [class*="banner"], [class*="aviso"], [class*="notice"]')).filter((el) => {
        const st = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        return st.display !== 'none' && st.visibility !== 'hidden' && r.top >= 0 && r.top < 540 && r.height >= 48 && r.width >= window.innerWidth * 0.65;
      });
      // Dedup aninhados: conta apenas blocos de topo nao contidos em outro candidato
      const topBanners = heroEls.filter((el) => !heroEls.some((other) => other !== el && other.contains(el)));
      const totalBannerH = topBanners.reduce((acc, el) => acc + el.getBoundingClientRect().height, 0);
      if (totalBannerH > window.innerHeight * (B.mobileTopMaxPct / 100) && totalBannerH > B.mobileTopMaxPx) {
        issues.push({
          severity: 'HIGH',
          rule: 'DA-MOBILE-HERO-BLOAT',
          detail: 'Hero + banners de topo no mobile consomem ' + Math.round(totalBannerH) + 'px (' + Math.round((totalBannerH / window.innerHeight) * 100) + '% da tela) antes da lista principal (orcamento do projeto: ' + B.mobileTopMaxPct + '% / ' + B.mobileTopMaxPx + 'px)',
        });
      }
    }

    // 21. DA-HEADER-STACK-BLOAT & DA-TAB-OVERFLOW: pilha de 3+ barras no topo desktop ou > 6 abas irmas numa unica linha
    if (isDesktop && !isAuthPage) {
      const topBands = Array.from(document.querySelectorAll('header, [class*="topbar"], [class*="toolbar"], [class*="subbar"], [class*="status-bar"], [class*="filter-bar"], [class*="tabs"], [role="tablist"]')).filter((el) => {
        if (el.closest('aside, [class*="sidebar"]')) return false;
        const st = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        return st.display !== 'none' && st.visibility !== 'hidden' && r.top >= 0 && r.top <= 250 && r.height >= 28 && r.height <= 92 && r.width >= 520;
      });
      const distinctBands = topBands.filter((el) => !topBands.some((o) => o !== el && o.contains(el)));
      distinctBands.sort((a, b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
      let stackedCount = 0;
      let lastBottom = -10;
      let totalStackH = 0;
      for (const b of distinctBands) {
        const r = b.getBoundingClientRect();
        if (r.top >= lastBottom - 4) {
          stackedCount++;
          totalStackH += r.height;
          lastBottom = r.bottom;
        }
      }
      if (stackedCount > B.headerMaxBars && totalStackH > B.headerMaxPx) {
        issues.push({
          severity: 'HIGH',
          rule: 'DA-HEADER-STACK-BLOAT',
          detail: stackedCount + ' barras horizontais empilhadas no topo do desktop consumindo ' + Math.round(totalStackH) + 'px antes dos dados reais (orcamento do projeto: ' + B.headerMaxBars + ' barras / ' + B.headerMaxPx + 'px)',
        });
      }

      for (const grp of document.querySelectorAll('[role="tablist"], [class*="tabs"], [class*="segmented"], [class*="filter-tabs"]')) {
        if (grp.closest('aside, [class*="sidebar"]')) continue;
        const st = getComputedStyle(grp);
        if (st.display === 'none' || st.visibility === 'hidden') continue;
        const tabKids = Array.from(grp.children).filter((ch) => {
          const tag = ch.tagName;
          const cs = getComputedStyle(ch);
          const cr = ch.getBoundingClientRect();
          return (tag === 'BUTTON' || tag === 'A' || ch.getAttribute('role') === 'tab') && cs.display !== 'none' && cr.width > 24 && cr.height > 20;
        });
        if (tabKids.length > B.maxSiblingTabs) {
          issues.push({
            severity: 'MEDIUM',
            rule: 'DA-TAB-OVERFLOW',
            detail: 'Barra de filtros/abas com ' + tabKids.length + ' abas irmas lado a lado (orcamento do projeto: ' + B.maxSiblingTabs + '; considere agrupar as secundarias num menu)',
          });
          break;
        }
      }
    }
  }

  // 18. DA-NAV-TRUNCATION & DA-HEADER-HSCROLL: detecta marca/nav cortados horizontalmente e barra superior com overflow/scrollbar
  if (isDesktop) {
    let navTrunc = 0;
    const truncSamples = [];
    const navLabels = document.querySelectorAll('aside [class*="brand"] strong, [class*="sidebar"] [class*="brand"] strong, [class*="brand-name"], aside nav a, [class*="sidebar"] nav a, header nav a, .pv-jbtn, .fx-flow-btn');
    for (const el of navLabels) {
      if (el.closest('.fx-world, [data-canvas-world], .is-collapsed, [data-collapsed="true"]')) continue;
      const st = getComputedStyle(el);
      if (st.display === 'none' || st.visibility === 'hidden') continue;
      const r = el.getBoundingClientRect();
      if (r.width < 18 || r.height < 12) continue;
      const txt = (el.textContent || '').replace(/\\s+/g, ' ').trim();
      if (txt.length < 3 || txt.length > 42) continue;
      const selfClip = el.scrollWidth > el.clientWidth + 2;
      let parentClip = false;
      let p = el.parentElement;
      for (let lvl = 0; lvl < 3 && p; lvl++, p = p.parentElement) {
        const ps = getComputedStyle(p);
        const pr = p.getBoundingClientRect();
        if ((ps.overflowX === 'hidden' || ps.overflowX === 'clip' || ps.overflow === 'hidden') && (r.right > pr.right + 2 || r.left < pr.left - 2)) {
          parentClip = true;
          break;
        }
      }
      if (selfClip || parentClip) {
        navTrunc++;
        if (truncSamples.length < 3) truncSamples.push('"' + txt.slice(0, 26) + '"');
      }
    }
    if (navTrunc > 0) {
      issues.push({ severity: 'HIGH', rule: 'DA-NAV-TRUNCATION', detail: navTrunc + ' rotulo(s) de marca/navegacao truncado(s) horizontalmente: ' + truncSamples.join(', ') });
    }

    let hScrollHeaders = 0;
    const hScrollSamples = [];
    for (const bar of document.querySelectorAll('header, [class*="topbar"], .pv-journeys, .fx-flows')) {
      const st = getComputedStyle(bar);
      if (st.display === 'none' || st.visibility === 'hidden') continue;
      const r = bar.getBoundingClientRect();
      if (r.top > 110 || r.height < 24 || r.height > 104 || r.width < 120) continue;
      if (bar.scrollWidth > bar.clientWidth + 6 && (st.overflowX === 'auto' || st.overflowX === 'scroll' || st.overflowX === 'hidden' || st.overflowX === 'clip')) {
        const kids = Array.from(bar.querySelectorAll('a, button')).filter((k) => {
          const kr = k.getBoundingClientRect();
          return kr.width > 0 && kr.height > 0;
        });
        const clippedKid = kids.some((k) => {
          const kr = k.getBoundingClientRect();
          return kr.left < r.left - 4 || kr.right > r.right + 4;
        });
        if (clippedKid) {
          hScrollHeaders++;
          if (hScrollSamples.length < 2) hScrollSamples.push((bar.className || bar.tagName).toString().trim().slice(0, 28) + ' (' + Math.round(bar.scrollWidth) + 'px > ' + Math.round(bar.clientWidth) + 'px)');
        }
      }
    }
    if (hScrollHeaders > 0) {
      issues.push({ severity: 'HIGH', rule: 'DA-HEADER-HSCROLL', detail: hScrollHeaders + ' barra(s) superior(es) com overflow/corte horizontal em desktop: ' + hScrollSamples.join(', ') });
    }
  }

  // DA-DUPLICATE-TEXT e DA-ALIGN-EDGES (v3.1): sinais de composicao para revisao visual, nunca bloqueiam.
  const mainForComp = document.querySelector('main, [role="main"]') || document.body;
  if (isDesktop && !isVitrine && !isAuthPage && mainForComp) {
    const regions = (el) => el.closest('section, article, aside, [class*="panel"], [class*="card"], [class*="drawer"], [class*="inspector"], [role="dialog"]');
    const seenText = new Map();
    for (const el of mainForComp.querySelectorAll('h1, h2, h3, h4, p, dd, dt, strong, span, div')) {
      if (el.children.length || el.closest('nav, tr, li, [role="row"], [role="tab"], button, a, select, option, label, [class*="badge"], [class*="chip"], [class*="pill"]')) continue;
      const st = getComputedStyle(el);
      if (st.display === 'none' || st.visibility === 'hidden') continue;
      const t = (el.textContent || '').replace(/\s+/g, ' ').trim();
      if (t.length < 6 || t.length > 64 || /^[\d\s.,:%R$+\-\/()]+$/.test(t)) continue;
      const reg = regions(el);
      if (!seenText.has(t)) seenText.set(t, new Set());
      seenText.get(t).add(reg || mainForComp);
    }
    const dups = [...seenText.entries()].filter(([, regs]) => regs.size >= B.duplicateTextMin).map(([t, regs]) => '"' + t.slice(0, 40) + '" x' + regs.size);
    if (dups.length) {
      issues.push({ severity: 'REVIEW', rule: 'DA-DUPLICATE-TEXT', detail: 'Mesmo texto em varias regioes da vista: ' + dups.slice(0, 4).join(', ') + '. Cada dado deveria aparecer uma vez por vista.' });
    }
    const lefts = new Map();
    for (const el of mainForComp.querySelectorAll('h1, h2, h3, h4, p, label, dt, legend, [class*="title"]')) {
      if (el.closest('table, nav, [role="grid"], [class*="chart"], svg')) continue;
      const r = el.getBoundingClientRect();
      if (r.width < 24 || r.height < 8 || r.top > window.innerHeight * 1.5) continue;
      const x = Math.round(r.left / 4) * 4;
      lefts.set(x, (lefts.get(x) || 0) + 1);
    }
    const edges = [...lefts.values()].filter((n) => n >= 2).length;
    if (edges > B.alignEdgesMax) {
      issues.push({ severity: 'REVIEW', rule: 'DA-ALIGN-EDGES', detail: edges + ' linhas de alinhamento a esquerda distintas na dobra (orcamento: ' + B.alignEdgesMax + '). Verifique se a grade esta coerente.' });
    }
  }

  return {
    title: document.title,
    scrollWidth: docEl.scrollWidth,
    innerWidth: window.innerWidth,
    issues,
  };
})()`;

function auditExpr(budgets) {
  return '(() => { window.__DA_BUDGETS__ = ' + JSON.stringify(budgets || DEFAULT_BUDGETS) + '; return ' + DOM_AUDIT_FN + '; })()';
}

// Zoom de 200%: rolagem horizontal da pagina (fora de tabelas e areas com rolagem propria) e texto cortado sem reticencias.
const ZOOM_CHECK_FN = `(() => {
  const se = document.scrollingElement || document.documentElement;
  let over = Math.max(0, se.scrollWidth - window.innerWidth);
  if (over > 4) {
    // descarta o excesso que vem de tabelas, grades, mapas, codigo e areas com overflow proprio
    let culprit = null;
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect();
      if (r.right <= window.innerWidth + 4 || r.width === 0) continue;
      if (el.closest('table, pre, code, canvas, svg, [role="grid"], [class*="grid-scroll"], [class*="table"]')) continue;
      let p = el.parentElement, scrolls = false;
      while (p && p !== document.body) {
        const ps = getComputedStyle(p);
        if (/(auto|scroll)/.test(ps.overflowX)) { scrolls = true; break; }
        p = p.parentElement;
      }
      if (!scrolls) { culprit = el; break; }
    }
    if (!culprit) over = 0;
  }
  let clipped = 0; const samples = [];
  for (const el of document.querySelectorAll('h1, h2, h3, p, a, button, label, td, th, li, span, strong')) {
    if (el.children.length) continue;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    const st = getComputedStyle(el);
    const hidesX = st.overflow === 'hidden' || st.overflowX === 'hidden' || st.overflowX === 'clip';
    if (hidesX && st.textOverflow !== 'ellipsis' && el.scrollWidth > el.clientWidth + 2) {
      clipped++;
      if (samples.length < 3) samples.push('"' + (el.textContent || '').trim().slice(0, 24) + '"');
    }
  }
  return { over: Math.round(over), clipped, samples };
})()`;

// Cores forcadas: controles cujo contorno dependia so do fundo (o sistema remove o fundo e a sombra).
const FORCED_COLORS_CHECK_FN = `(() => {
  const active = matchMedia('(forced-colors: active)').matches;
  let unbounded = 0; const samples = [];
  for (const el of document.querySelectorAll('button, [role="button"], input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]), select, textarea, a[class*="btn"], a[class*="button"]')) {
    const r = el.getBoundingClientRect();
    if (r.width < 8 || r.height < 8) continue;
    const st = getComputedStyle(el);
    if (st.visibility === 'hidden' || st.display === 'none') continue;
    const border = ['Top', 'Right', 'Bottom', 'Left'].some((s) => parseFloat(st['border' + s + 'Width']) >= 1 && st['border' + s + 'Style'] !== 'none');
    const outline = parseFloat(st.outlineWidth) >= 1 && st.outlineStyle !== 'none';
    if (!border && !outline) {
      unbounded++;
      if (samples.length < 3) samples.push((el.tagName.toLowerCase()) + ' "' + ((el.textContent || el.value || el.getAttribute('aria-label') || '').trim().slice(0, 20)) + '"');
    }
  }
  return { active, unbounded, samples };
})()`;

const MOTION_CHECK_FN = `(() => {
  const waiting = /skeleton|spinner|loading|progress|typing|shimmer|busy|recording|pulse-live/i;
  const offenders = [];
  for (const anim of document.getAnimations ? document.getAnimations() : []) {
    const timing = anim.effect && anim.effect.getComputedTiming ? anim.effect.getComputedTiming() : {};
    const el = anim.effect && anim.effect.target;
    if (!el || anim.playState !== 'running') continue;
    if (timing.iterations !== Infinity || !(timing.duration > 0)) continue;
    const label = (el.className && String(el.className)) + ' ' + (el.getAttribute && (el.getAttribute('aria-busy') || el.getAttribute('role') || ''));
    if (waiting.test(label) || el.closest('[aria-busy="true"], [role="progressbar"], [role="status"]')) continue;
    offenders.push((el.tagName || '').toLowerCase() + (el.className ? '.' + String(el.className).trim().split(/\s+/).slice(0, 2).join('.') : ''));
  }
  return offenders.slice(0, 5);
})()`;

async function pixelDiff(cdp, currentPath, baselinePath, outPath) {
  const cur = fs.readFileSync(currentPath).toString('base64');
  const base = fs.readFileSync(baselinePath).toString('base64');
  const res = await cdp.send('Runtime.evaluate', {
    expression: `(async () => {
      const load = (src) => new Promise((ok, ko) => { const i = new Image(); i.onload = () => ok(i); i.onerror = () => ko(new Error('img')); i.src = src; });
      const [a, b] = await Promise.all([load('data:image/png;base64,${cur}'), load('data:image/png;base64,${base}')]);
      if (a.width !== b.width || a.height !== b.height) return { sizeMismatch: [a.width, a.height, b.width, b.height] };
      const w = a.width, h = a.height;
      const c = document.createElement('canvas'); c.width = w; c.height = h;
      const x = c.getContext('2d', { willReadFrequently: true });
      x.drawImage(a, 0, 0); const da = x.getImageData(0, 0, w, h).data;
      x.clearRect(0, 0, w, h); x.drawImage(b, 0, 0); const db = x.getImageData(0, 0, w, h).data;
      const out = x.createImageData(w, h); let changed = 0;
      for (let i = 0; i < da.length; i += 4) {
        const d = Math.abs(da[i] - db[i]) + Math.abs(da[i + 1] - db[i + 1]) + Math.abs(da[i + 2] - db[i + 2]);
        if (d > 48) { changed++; out.data[i] = 255; out.data[i + 1] = 48; out.data[i + 2] = 96; out.data[i + 3] = 255; }
        else { const g = (da[i] + da[i + 1] + da[i + 2]) / 3; out.data[i] = out.data[i + 1] = out.data[i + 2] = g; out.data[i + 3] = 60; }
      }
      x.putImageData(out, 0, 0);
      return { pct: Math.round((changed * 10000) / (w * h)) / 100, png: c.toDataURL('image/png').split(',')[1] };
    })()`,
    awaitPromise: true,
    returnByValue: true,
  });
  const val = res?.result?.value;
  if (!val) return null;
  if (val.sizeMismatch) return { baseline: baselinePath, sizeMismatch: val.sizeMismatch };
  fs.writeFileSync(outPath, Buffer.from(val.png, 'base64'));
  return { baseline: baselinePath, pct: val.pct, diff: outPath };
}

function pickViewportsForEntry(entry, args, hasMultiPlatform) {
  if (entry.viewports) return entry.viewports;
  if (entry.isVitrine) return args.viewports.includes('desktop') ? ['desktop'] : [args.viewports[0]];
  if (args.allViewports || !hasMultiPlatform) return args.viewports;
  if (entry.platform === 'desktop' && args.viewports.includes('desktop')) return ['desktop'];
  if (entry.platform === 'mobile' && args.viewports.includes('mobile')) return ['mobile'];
  return args.viewports;
}

async function main() {
  const args = parseArgs(process.argv);
  const browserPath = findBrowser();
  if (!browserPath && args.entries.length) {
    console.error('Erro: Chromium/Google Chrome nao encontrado no ambiente.');
    process.exit(1);
  }

  const outDir = path.resolve(args.out);
  fs.mkdirSync(outDir, { recursive: true });

  const localFiles = args.entries.filter((e) => !/^https?:\/\//i.test(e.target)).map((e) => path.resolve(e.target));
  let staticSrv = null;
  let rootDir = process.cwd();
  if (localFiles.length) {
    rootDir = args.manifestDir ? path.resolve(args.manifestDir) : path.dirname(localFiles[0]);
    for (const f of localFiles) {
      while (!f.startsWith(rootDir + path.sep) && f !== rootDir && path.dirname(rootDir) !== rootDir) {
        rootDir = path.dirname(rootDir);
      }
    }
    // Sobe a raiz conforme a profundidade maxima de "../" usada nos HTMLs locais (ex.: ../../sistema/img/...)
    let maxUp = 0;
    for (const f of localFiles) {
      try {
        if (!f.endsWith('.html') && !f.endsWith('.htm')) continue;
        const text = fs.readFileSync(f, 'utf8');
        for (const m of text.matchAll(/(?:href|src)=["']((?:\.\.\/)+)/g)) {
          const depth = (m[1].match(/\.\.\//g) || []).length;
          if (depth > maxUp) maxUp = Math.min(depth, 3);
        }
      } catch {}
    }
    const baseDepthDir = path.dirname(localFiles[0]);
    for (let k = 0; k < maxUp; k++) {
      const targetRoot = path.resolve(baseDepthDir, '../'.repeat(k + 1));
      if (rootDir.startsWith(targetRoot) && targetRoot.length < rootDir.length) {
        rootDir = targetRoot;
      }
    }
    staticSrv = await startStaticServer(rootDir);
  }

  const platforms = new Set(args.entries.filter((e) => !e.isVitrine).map((e) => e.platform));
  const hasMultiPlatform = platforms.has('desktop') && platforms.has('mobile');

  const resolvedTargets = args.entries.map((e) => {
    if (/^https?:\/\//i.test(e.target)) {
      return {
        label: e.labelOverride || e.target.replace(/^https?:\/\/[^/]+/i, '').replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '').slice(0, 40) || 'root',
        url: e.target + (e.urlSuffix || ''),
        ...e,
      };
    }
    const abs = path.resolve(e.target);
    const rel = path.relative(rootDir, abs).split(path.sep).join('/');
    return {
      label: e.labelOverride || path.basename(abs, path.extname(abs)),
      url: `http://127.0.0.1:${staticSrv.port}/${rel}${e.urlSuffix || ''}`,
      ...e,
    };
  });

  const jobs = [];
  for (const target of resolvedTargets) {
    const vps = pickViewportsForEntry(target, args, hasMultiPlatform);
    for (const vpName of vps) {
      const vp = resolveViewport(vpName);
      for (const theme of args.themes) {
        jobs.push({ idx: jobs.length, target, vpName, vp, theme });
      }
    }
  }

  const startedAt = Date.now();
  let browser = null;
  let browserCdp = null;
  const report = new Array(jobs.length);
  let completed = 0;

  async function runJobOnTab(cdp, job, prevPreloadId) {
    const t0 = Date.now();
    const { target, vpName, vp, theme } = job;
    const consoleErrors = [];
    const failedAssets = [];
    const net = { bytes: 0, requests: 0, fonts: 0 };

    const onEx = (p) => {
      const ex = p.exceptionDetails || {};
      const desc = ex.exception?.description || ex.text || 'Excecao JS nao tratada';
      const firstLine = String(desc).split('\n')[0];
      const loc = ex.url ? ` (${path.basename(ex.url)}:${(ex.lineNumber || 0) + 1})` : '';
      consoleErrors.push(`${firstLine}${loc}`);
    };
    const onConsole = (p) => {
      if (p.type === 'error') {
        const msg = (p.args || []).map((a) => a.value || a.description || '').join(' ');
        if (msg && !/favicon\.ico/i.test(msg)) consoleErrors.push(msg.slice(0, 220));
      }
    };
    const onNet = (p) => {
      const res = p.response || {};
      const url = res.url || '';
      net.requests++;
      if (p.type === 'Font') net.fonts++;
      if (res.status >= 400 && url.startsWith('http://127.0.0.1:') && !url.endsWith('/favicon.ico')) {
        failedAssets.push(`HTTP ${res.status}: ${new URL(url).pathname}`);
      }
    };

    cdp.on('Runtime.exceptionThrown', onEx);
    cdp.on('Runtime.consoleAPICalled', onConsole);
    cdp.on('Network.responseReceived', onNet);
    const onLoaded = (p) => { net.bytes += p.encodedDataLength || 0; };
    cdp.on('Network.loadingFinished', onLoaded);

    let nextPreloadId = prevPreloadId;
    try {
      if (prevPreloadId) {
        try { await cdp.send('Page.removeScriptToEvaluateOnNewDocument', { identifier: prevPreloadId }); } catch {}
        nextPreloadId = null;
      }
      const preload = await cdp.send('Page.addScriptToEvaluateOnNewDocument', {
        source: `try { localStorage.setItem('design-aura:theme', '${theme}'); } catch (e) {}
                 document.addEventListener('DOMContentLoaded', () => {
                   document.documentElement.setAttribute('data-theme', '${theme}');
                 }, { once: true });`,
      });
      nextPreloadId = preload?.identifier || null;

      await cdp.send('Emulation.setDeviceMetricsOverride', {
        width: vp.width,
        height: vp.height,
        deviceScaleFactor: vp.dpr,
        mobile: vp.mobile,
      });
      await cdp.send('Emulation.setEmulatedMedia', {
        features: [{ name: 'prefers-color-scheme', value: theme }],
      });

      const loadPromise = new Promise((res) => {
        let done = false;
        const finish = () => {
          if (!done) {
            done = true;
            clearTimeout(t);
            res();
          }
        };
        const handler = cdp.once('Page.loadEventFired', finish);
        const t = setTimeout(() => {
          cdp.off('Page.loadEventFired', handler);
          finish();
        }, 6000);
      });
      await cdp.send('Page.navigate', { url: target.url });
      await loadPromise;

      if (target.isVitrine) {
        await cdp.send('Runtime.evaluate', {
          expression: `new Promise((resolve) => {
            const start = Date.now();
            function check() {
              const frames = Array.from(document.querySelectorAll('iframe.fx-preview-frame'));
              const allLoaded = frames.length === 0 || frames.every((f) => f.classList.contains('is-loaded'));
              if (allLoaded || Date.now() - start > 1900) return resolve(true);
              setTimeout(check, 120);
            }
            setTimeout(check, 450);
          })`,
          awaitPromise: true,
          returnByValue: true,
        });
      } else {
        await new Promise((r) => setTimeout(r, 320));
      }

      await cdp.send('Runtime.evaluate', {
        expression: `(() => {
          document.documentElement.setAttribute('data-theme', '${theme}');
          document.dispatchEvent(new CustomEvent('designaura:themechange', { detail: { theme: '${theme}' } }));
          return true;
        })()`,
        returnByValue: true,
      });
      await new Promise((r) => setTimeout(r, 220));

      const evalRes = await cdp.send('Runtime.evaluate', {
        expression: auditExpr(target.budgets),
        returnByValue: true,
      });
      const domData = evalRes?.result?.value;
      let docPath = '';
      try { docPath = new URL(target.url).pathname; } catch { docPath = ''; }
      const mainDoc404 = docPath && failedAssets.some((fa) => fa.endsWith(': ' + docPath));
      // Pagina que nao existe nao recebe sinais de composicao: o problema e o 404.
      const issues = mainDoc404 ? [] : [...(domData?.issues || [])];
      if (!domData) {
        issues.push({ severity: 'BLOCK', rule: 'DA-AUDIT-COVERAGE', detail: 'Auditoria do DOM sem resultado.' });
      }
      for (const ce of [...new Set(consoleErrors)]) {
        issues.push({ severity: 'BLOCK', rule: 'DA-JS-ERROR', detail: ce });
      }
      for (const fa of [...new Set(failedAssets)]) {
        issues.push({ severity: 'BLOCK', rule: 'DA-ASSET-404', detail: fa });
      }

      const shotName = `${target.label}-${vpName}-${theme}.png`;
      const shotPath = path.join(outDir, shotName);
      const shot = await cdp.send('Page.captureScreenshot', { format: 'png' });
      fs.writeFileSync(shotPath, Buffer.from(shot.data, 'base64'));

      if (target.primaryAction && !mainDoc404) {
        const pa = target.primaryAction;
        const paRes = await cdp.send('Runtime.evaluate', { expression: primaryActionExpr(pa), returnByValue: true });
        const v = paRes?.result?.value || {};
        const name = pa.label || pa.selector;
        if (v.status === 'missing') {
          issues.push({ severity: 'REVIEW', rule: 'DA-REACHABLE', detail: `Ação primária "${name}" não encontrada pelo rótulo nesta largura. Declare primaryAction.selector ou confira na captura.` });
        } else if (v.status === 'disabled') {
          issues.push({ severity: 'REVIEW', rule: 'DA-REACHABLE', detail: `Ação primária "${name}" desabilitada no estado capturado. Confirme que o motivo aparece para a pessoa.` });
        } else if (v.status === 'blocked') {
          issues.push({ severity: 'HIGH', rule: 'DA-REACHABLE', detail: `Ação primária "${name}" ${v.reason}.` });
        }
      }

      const budgets = target.budgets || DEFAULT_BUDGETS;
      const transferKB = Math.round(net.bytes / 1024);
      if (!target.isVitrine && budgets.perfMaxKB && (transferKB > budgets.perfMaxKB || net.requests > budgets.perfMaxRequests || net.fonts > budgets.perfMaxFonts)) {
        issues.push({ severity: 'REVIEW', rule: 'DA-PERF-BUDGET', detail: `Carregou ${transferKB} KB em ${net.requests} requisicoes e ${net.fonts} fontes (orcamento: ${budgets.perfMaxKB} KB / ${budgets.perfMaxRequests} / ${budgets.perfMaxFonts}).` });
      }
      if (args.checkMotion && !target.isVitrine) {
        try {
          await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: theme }, { name: 'prefers-reduced-motion', value: 'reduce' }] });
          await new Promise((r) => setTimeout(r, 200));
          const mres = await cdp.send('Runtime.evaluate', { expression: MOTION_CHECK_FN, returnByValue: true });
          const offenders = mres?.result?.value || [];
          if (offenders.length) {
            issues.push({ severity: 'REVIEW', rule: 'DA-REDUCED-MOTION', detail: 'Animacoes infinitas seguem rodando com prefers-reduced-motion: ' + offenders.join(', ') });
          }
        } finally {
          await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: theme }] });
        }
      }

      // Zoom de 200% e cores forcadas: uma vez por tela (largura desktop, primeiro tema), com capturas para o critico.
      const a11yHere = args.a11yExtra && !target.isVitrine && !mainDoc404 && vp.width >= 1024 && !vp.mobile && theme === args.themes[0];
      if (a11yHere) {
        try {
          await cdp.send('Emulation.setDeviceMetricsOverride', { width: Math.round(vp.width / 2), height: Math.round(vp.height / 2), deviceScaleFactor: 2, mobile: false });
          await new Promise((r) => setTimeout(r, 260));
          const zres = await cdp.send('Runtime.evaluate', { expression: ZOOM_CHECK_FN, returnByValue: true });
          const z = zres?.result?.value || {};
          const zShot = await cdp.send('Page.captureScreenshot', { format: 'png' });
          fs.writeFileSync(path.join(outDir, `${target.label}-${vpName}-${theme}-zoom200.png`), Buffer.from(zShot.data, 'base64'));
          if (z.over > 4 || z.clipped > 0) {
            const parts = [];
            if (z.over > 4) parts.push(`a página rola ${z.over}px na horizontal fora de tabelas e áreas com rolagem própria`);
            if (z.clipped > 0) parts.push(`${z.clipped} texto(s) cortado(s): ${z.samples.join(', ')}`);
            issues.push({ severity: 'REVIEW', rule: 'DA-ZOOM-REFLOW', detail: `Com zoom de 200% (${Math.round(vp.width / 2)}px CSS), ${parts.join('; ')}. Confira a captura -zoom200.` });
          }
        } catch (err) {
          issues.push({ severity: 'REVIEW', rule: 'DA-ZOOM-REFLOW', detail: 'Checagem de zoom não rodou: ' + String(err.message || err).slice(0, 120) });
        } finally {
          await cdp.send('Emulation.setDeviceMetricsOverride', { width: vp.width, height: vp.height, deviceScaleFactor: vp.dpr, mobile: vp.mobile });
        }
        try {
          await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: theme }, { name: 'forced-colors', value: 'active' }] });
          await new Promise((r) => setTimeout(r, 200));
          const fres = await cdp.send('Runtime.evaluate', { expression: FORCED_COLORS_CHECK_FN, returnByValue: true });
          const f = fres?.result?.value || {};
          const fShot = await cdp.send('Page.captureScreenshot', { format: 'png' });
          fs.writeFileSync(path.join(outDir, `${target.label}-${vpName}-${theme}-forced-colors.png`), Buffer.from(fShot.data, 'base64'));
          if (f.active && f.unbounded > 0) {
            issues.push({ severity: 'REVIEW', rule: 'DA-FORCED-COLORS', detail: `Em cores forçadas, ${f.unbounded} controle(s) perdem o contorno (fundo some, sem borda): ${f.samples.join(', ')}. Use borda transparente ou @media (forced-colors: active).` });
          }
        } catch (err) {
          issues.push({ severity: 'REVIEW', rule: 'DA-FORCED-COLORS', detail: 'Checagem de cores forçadas não rodou: ' + String(err.message || err).slice(0, 120) });
        } finally {
          await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: theme }] });
          await new Promise((r) => setTimeout(r, 120));
        }
      }

      // Smoke interativo pos-clique: valida Resize In-Place / abertura de conferencia sem erro JS ou recorte
      let interactScreenshot = null;
      let interactionVerified = false;
      const interactSel = target.clickSelector || (args.smokeInteract && !target.isVitrine ? '[data-da-open]' : '');
      if (interactSel && !target.isVitrine) {
        const clickRes = await cdp.send('Runtime.evaluate', {
          expression: `(() => {
            const el = document.querySelector(${JSON.stringify(interactSel)});
            if (!el) return false;
            el.scrollIntoView({ block: 'center' });
            el.click();
            return true;
          })()`,
          returnByValue: true,
        });
        if (clickRes?.result?.value) {
          await new Promise((r) => setTimeout(r, 280));
          const postEval = await cdp.send('Runtime.evaluate', {
            expression: auditExpr(target.budgets),
            returnByValue: true,
          });
          const postIssues = postEval?.result?.value?.issues || [];
          let expectedState = !target.afterClickSelector;
          if (target.afterClickSelector) {
            const state = await cdp.send('Runtime.evaluate', {
              expression: `document.querySelector(${JSON.stringify(target.afterClickSelector)})?.checkVisibility()`,
              returnByValue: true,
            });
            expectedState = state?.result?.value === true;
          }
          interactionVerified = Boolean(postEval?.result?.value) && expectedState;
          for (const pi of postIssues) {
            if (['DA-DOM-OVERFLOW', 'DA-CLIPPED-CONTENT', 'DA-FIXED-OVERLAP', 'DA-MOBILE-FLEX-CLIP'].includes(pi.rule)) {
              issues.push({ severity: pi.severity, rule: `${pi.rule}-INTERACT`, detail: `[Pos-clique ${interactSel}] ${pi.detail}` });
            }
          }
          for (const ce of [...new Set(consoleErrors)]) {
            if (!issues.some((i) => i.rule === 'DA-JS-ERROR' && i.detail === ce)) {
              issues.push({ severity: 'BLOCK', rule: 'DA-JS-ERROR', detail: `[Pos-clique ${interactSel}] ${ce}` });
            }
          }
          const iShotName = `${target.label}-${vpName}-${theme}-interact.png`;
          interactScreenshot = path.join(outDir, iShotName);
          const iShot = await cdp.send('Page.captureScreenshot', { format: 'png' });
          fs.writeFileSync(interactScreenshot, Buffer.from(iShot.data, 'base64'));
        }
      }

      if (target.afterClickSelector && !interactionVerified) {
        issues.push({ severity: 'HIGH', rule: 'DA-AUDIT-COVERAGE', detail: `Estado pós-clique não verificado: ${target.afterClickSelector}` });
      }
      for (const detail of new Set(failedAssets)) {
        if (!issues.some((issue) => issue.rule === 'DA-ASSET-404' && issue.detail === detail)) {
          issues.push({ severity: 'BLOCK', rule: 'DA-ASSET-404', detail });
        }
      }
      let visualDiff = null;
      if (args.baseline) {
        const basePath = path.join(path.resolve(args.baseline), path.basename(shotPath));
        if (fs.existsSync(basePath)) {
          try { visualDiff = await pixelDiff(cdp, shotPath, basePath, shotPath.replace(/\.png$/, '-diff.png')); } catch (err) { visualDiff = { baseline: basePath, error: String(err.message || err) }; }
        } else {
          visualDiff = { baseline: basePath, missing: true };
        }
      }
      const cappedIssues = issues.map(capIssue);
      issues.length = 0;
      issues.push(...cappedIssues);
      const entry = {
        target: target.label,
        url: target.url,
        mode: target.mode || args.mode,
        metrics: { transferKB: Math.round(net.bytes / 1024), requests: net.requests, fonts: net.fonts },
        ...(visualDiff ? { visualDiff } : {}),
        viewport: `${vpName} (${vp.width}x${vp.height})`,
        theme,
        screenshot: shotPath,
        dimensions: { width: vp.width, height: vp.height, layoutWidth: domData?.innerWidth ?? null },
        states: {
          initial: domData ? 'captured' : 'unverified',
          ...(interactSel && { postClick: interactionVerified ? 'captured' : 'unverified' }),
        },
        ...(interactScreenshot ? { interactScreenshot } : {}),
        issues,
      };
      report[job.idx] = entry;
      completed++;
      if (!args.quiet) {
        const blocks = issues.filter((i) => i.severity === 'BLOCK').length;
        const highs = issues.filter((i) => i.severity === 'HIGH').length;
        const reviews = issues.filter((i) => i.severity === 'REVIEW').length;
        const stLabel = blocks > 0 ? 'BLOCK' : highs > 0 ? 'HIGH' : reviews > 0 ? 'REVIEW' : 'PASS';
        const sec = ((Date.now() - t0) / 1000).toFixed(1);
        const pad = String(completed).padStart(String(jobs.length).length, '0');
        process.stderr.write(`[${pad}/${jobs.length}] ${target.label} (${vpName} · ${theme}) -> ${stLabel} (${sec}s)\n`);
      }
      return nextPreloadId;
    } catch (error) {
      report[job.idx] = {
        target: target.label, url: target.url, viewport: vpName, theme, screenshot: null,
        issues: [{ severity: 'BLOCK', rule: 'DA-AUDIT-COVERAGE', detail: `Captura falhou: ${error.message}` }],
      };
      return nextPreloadId;
    } finally {
      cdp.off('Runtime.exceptionThrown', onEx);
      cdp.off('Runtime.consoleAPICalled', onConsole);
      cdp.off('Network.responseReceived', onNet);
      cdp.off('Network.loadingFinished', onLoaded);
    }
  }

  if (jobs.length) try {
    browser = await launchBrowser(browserPath);
    const workerCount = Math.max(1, Math.min(args.concurrency, jobs.length));
    let cursor = 0;

    if (workerCount === 1 || !browser.browserWsUrl) {
      const pagesRes = await fetch(`http://127.0.0.1:${browser.port}/json/list`);
      const pages = await pagesRes.json();
      const pageTarget = pages.find((p) => p.type === 'page') || pages[0];
      if (!pageTarget?.webSocketDebuggerUrl) throw new Error('Target de pagina CDP nao disponivel.');
      const cdp = new CDPClient(pageTarget.webSocketDebuggerUrl);
      await cdp.connect();
      await cdp.send('Page.enable');
      await cdp.send('Runtime.enable');
      await cdp.send('Network.enable');
      let preloadId = null;
      for (const job of jobs) {
        preloadId = await runJobOnTab(cdp, job, preloadId);
      }
      cdp.close();
    } else {
      browserCdp = new CDPClient(browser.browserWsUrl);
      await browserCdp.connect();
      const workers = Array.from({ length: workerCount }, async () => {
        let browserContextId = null;
        try {
          const ctx = await browserCdp.send('Target.createBrowserContext');
          browserContextId = ctx?.browserContextId || null;
        } catch {}
        const createParams = browserContextId ? { url: 'about:blank', browserContextId } : { url: 'about:blank' };
        const created = await browserCdp.send('Target.createTarget', createParams);
        const targetId = created.targetId;
        const cdp = new CDPClient(`ws://127.0.0.1:${browser.port}/devtools/page/${targetId}`);
        await cdp.connect();
        await cdp.send('Page.enable');
        await cdp.send('Runtime.enable');
        await cdp.send('Network.enable');
        let preloadId = null;
        try {
          while (cursor < jobs.length) {
            const job = jobs[cursor++];
            preloadId = await runJobOnTab(cdp, job, preloadId);
          }
        } finally {
          cdp.close();
          try { await browserCdp.send('Target.closeTarget', { targetId }); } catch {}
          if (browserContextId) {
            try { await browserCdp.send('Target.disposeBrowserContext', { browserContextId }); } catch {}
          }
        }
      });
      await Promise.all(workers);
      browserCdp.close();
    }
  } finally {
    if (browser) {
      try { browser.proc.kill('SIGTERM'); } catch {}
      try { fs.rmSync(browser.userDataDir, { recursive: true, force: true }); } catch {}
    }
    if (staticSrv) {
      try { staticSrv.server.close(); } catch {}
    }
  }

  const finalReport = jobs.map(({ idx, target, vpName, theme }) => report[idx] ?? {
    target: target.label, viewport: vpName, theme, screenshot: null,
    issues: [{ severity: 'BLOCK', rule: 'DA-AUDIT-COVERAGE', detail: 'Captura planejada sem resultado.' }],
  });
  for (const { target, viewport, detail } of args.missing) {
    finalReport.push({ target, viewport: viewport || '—', theme: '—', screenshot: null,
      issues: [{ severity: 'HIGH', rule: 'DA-AUDIT-COVERAGE', detail }],
    });
  }
  for (const row of finalReport) row.issues = (row.issues || []).map(capIssue);
  const reportPath = path.join(outDir, 'audit-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(finalReport, null, 2), 'utf-8');

  const elapsedSec = ((Date.now() - startedAt) / 1000).toFixed(1);
  let totalBlock = 0;
  let totalHigh = 0;
  let totalReview = 0;
  console.log(`# Auditoria Visual & DOM Real (Design Aura v${RULES.version || ''})`);
  console.log('- BLOCK e HIGH falham em --strict. REVIEW e um sinal de composicao: abra a captura e confirme ou dispense com motivo.');
  console.log(`- **Capturas geradas:** ${finalReport.filter((entry) => entry.screenshot).length} · **Tempo:** ${elapsedSec}s (concurrency=${Math.min(args.concurrency, Math.max(1, jobs.length))}) · **Relatorio JSON:** ${reportPath}\n`);
  console.log('| Tela | Viewport | Tema | Screenshot | Status | Achados |');
  console.log('|---|---|---|---|---|---|');
  for (const r of finalReport) {
    const blocks = r.issues.filter((i) => i.severity === 'BLOCK').length;
    const highs = r.issues.filter((i) => i.severity === 'HIGH').length;
    const reviews = r.issues.filter((i) => i.severity === 'REVIEW').length;
    totalBlock += blocks;
    totalHigh += highs;
    totalReview += reviews;
    const status = blocks > 0 ? 'BLOCK' : highs > 0 ? 'HIGH' : reviews > 0 ? 'REVIEW' : 'PASS';
    const summary = r.issues.length ? r.issues.map((i) => `${i.rule}: ${i.detail}`).join('; ') : 'OK';
    console.log(`| ${r.target} | ${r.viewport} | ${r.theme} | ${r.screenshot ? path.basename(r.screenshot) : '—'} | **${status}** | ${summary} |`);
  }

  console.log(`\n- **Total:** BLOCK ${totalBlock} · HIGH ${totalHigh} · REVIEW ${totalReview}`);
  const diffs = finalReport.filter((r) => r.visualDiff && typeof r.visualDiff.pct === 'number');
  if (diffs.length) {
    console.log('- **Mudanca contra a linha de base:** ' + diffs.map((r) => `${r.target} ${r.viewport} ${r.theme}: ${r.visualDiff.pct}%`).join(' · '));
  }
  if (args.strict && (totalBlock > 0 || totalHigh > 0)) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Falha na auditoria visual headless:', err);
  process.exit(1);
});
