#!/usr/bin/env node
/**
 * Captura screenshots multi-viewport (Dark & Light) e audita o DOM real
 * via Chrome DevTools Protocol (Chromium headless, zero dependencias npm).
 *
 * Design Aura v2.0:
 *  - Audita automaticamente fluxo.html, preview.html e index.html com --manifest
 *  - Reporta stack completo de erros JS (DA-JS-ERROR) e assets 404 (DA-ASSET-404)
 *  - Checagens positivas de craft e composicao: DA-DEAD-SPACE, DA-STUB-SCREEN,
 *    DA-RAW-LINK-LIST, DA-FIXED-OVERLAP, DA-SERIF-OPERATE e DA-SURFACE-FLAT
 *
 * Uso:
 *   node capture_and_audit.mjs <arquivo-ou-url> [...] --out <dir> [--manifest screen-manifest.json]
 *        [--viewports desktop,mobile] [--themes dark,light] [--all-viewports] [--no-vitrine] [--strict]
 */
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { spawn } from 'node:child_process';

const VIEWPORTS = {
  desktop: { width: 1440, height: 900, mobile: false, dpr: 1 },
  tablet: { width: 768, height: 1024, mobile: true, dpr: 2 },
  mobile: { width: 390, height: 844, mobile: true, dpr: 2 },
};

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

function entriesFromManifest(manifestPath, includeVitrine) {
  const abs = path.resolve(manifestPath);
  const data = JSON.parse(fs.readFileSync(abs, 'utf8'));
  const base = path.dirname(abs);
  const entries = [];
  const screenDirs = new Set();

  for (const screen of data.screens || []) {
    const file = screen.file;
    if (!file || /^https?:\/\//i.test(file)) continue;
    const resolved = resolveManifestScreenPath(base, file);
    screenDirs.add(path.dirname(resolved));
    entries.push({
      target: resolved,
      platform: (screen.platform || '').toLowerCase() || 'responsive',
      isVitrine: false,
    });
  }

  if (includeVitrine) {
    const searchDirs = [...screenDirs, base];
    const seen = new Set();
    for (const name of ['fluxo.html', 'preview.html', 'index.html']) {
      for (const d of searchDirs) {
        const candidate = path.join(d, name);
        if (fs.existsSync(candidate) && !seen.has(candidate)) {
          seen.add(candidate);
          entries.push({ target: candidate, platform: 'vitrine', isVitrine: true });
          break;
        }
      }
    }
  }
  return { entries, manifestDir: base };
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
    includeVitrine: true,
    allViewports: false,
  };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--out' && argv[i + 1]) args.out = argv[++i];
    else if (a === '--viewports' && argv[i + 1]) args.viewports = argv[++i].split(',').map((s) => s.trim()).filter(Boolean);
    else if (a === '--themes' && argv[i + 1]) args.themes = argv[++i].split(',').map((s) => s.trim()).filter(Boolean);
    else if (a === '--manifest' && argv[i + 1]) args.manifest = argv[++i];
    else if (a === '--no-vitrine') args.includeVitrine = false;
    else if (a === '--all-viewports') args.allViewports = true;
    else if (a === '--strict') args.strict = true;
    else if (a === '--help' || a === '-h') {
      console.log('Uso: node capture_and_audit.mjs <arquivo|url> [...] --manifest screen-manifest.json --out <dir> [--viewports desktop,tablet,mobile] [--themes dark,light] [--all-viewports] [--no-vitrine] [--strict]');
      process.exit(0);
    } else {
      args.entries.push({ target: a, platform: 'responsive', isVitrine: false });
    }
  }
  if (args.manifest) {
    const res = entriesFromManifest(args.manifest, args.includeVitrine);
    args.manifestDir = res.manifestDir;
    args.entries.push(...res.entries);
  }
  const seen = new Set();
  args.entries = args.entries.filter((e) => {
    const k = /^https?:\/\//i.test(e.target) ? e.target : path.resolve(e.target);
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
  if (!args.entries.length) {
    console.error('Erro: informe ao menos 1 arquivo HTML, URL ou --manifest.');
    process.exit(1);
  }
  return args;
}

function findBrowser() {
  const candidates = [
    process.env.CHROME_PATH,
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/snap/bin/chromium',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ].filter(Boolean);
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return null;
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
        resolve({ proc, port: Number(wsUrl.port), userDataDir });
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
  const docEl = document.documentElement;
  const isMobile = window.innerWidth <= 480;
  const isDesktop = window.innerWidth >= 1024;
  const isVitrine = !!document.querySelector('.fx-app, .pv-app, .g-shell, .specimen-sheet') || /design-bible/i.test(location.pathname);
  const titlePath = (document.title + ' ' + location.pathname).toLowerCase();
  const isAuthPage = !!document.querySelector('input[type="password"]') || /(?:login|entrada|acesso|auth|signin|signup|cadastro|2fa)/.test(titlePath);

  function parseRgb(str) {
    const m = str && str.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
    if (!m) return null;
    return [Number(m[1]), Number(m[2]), Number(m[3]), m[4] !== undefined ? Number(m[4]) : 1];
  }
  function resolveBg(el) {
    let cur = el;
    while (cur) {
      const bg = parseRgb(getComputedStyle(cur).backgroundColor);
      if (bg && bg[3] > 0.85) return bg;
      cur = cur.parentElement;
    }
    return [15, 26, 38, 1];
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

  // 6. Amostra de contraste real computado
  let contrastFails = 0;
  const textEls = Array.from(document.querySelectorAll('h1,h2,h3,p,a,button,td,th')).slice(0, 60);
  for (const el of textEls) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0 || !(el.textContent || '').trim()) continue;
    const st = getComputedStyle(el);
    if (parseFloat(st.opacity || '1') < 0.5) continue;
    const fg = parseRgb(st.color);
    const bg = resolveBg(el);
    if (!fg || !bg || fg[3] < 0.8) continue;
    const l1 = lum(fg), l2 = lum(bg);
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    const fs = parseFloat(st.fontSize || '14');
    const fw = parseInt(st.fontWeight || '400', 10);
    const minReq = (fs >= 24 || (fs >= 18.66 && fw >= 700)) ? 3.0 : 4.5;
    if (ratio < minReq) contrastFails++;
  }
  if (contrastFails > 0) {
    issues.push({ severity: 'HIGH', rule: 'DA-B3-01', detail: contrastFails + ' elementos amostrados com contraste abaixo do minimo WCAG AA' });
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

  // === DESIGN AURA v2.0: CHECAGENS POSITIVAS DE CRAFT, COMPOSICAO E SUBSTANCIA ===
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
    for (const a of document.querySelectorAll('li a, td a, nav a, [role="list"] a, [class*="list"] a, [class*="row"] a, [class*="item"] a')) {
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
    if (!isAuthPage) {
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
      if (leafNodes.length < 4) {
        issues.push({ severity: 'HIGH', rule: 'DA-STUB-SCREEN', detail: 'Tela operacional rasa com apenas ' + leafNodes.length + ' elementos estruturais/interativos visiveis' });
      }
    }

    // 14. DA-DEAD-SPACE: vazio morto em desktop (1440x900) + inspector/aside vazio ou subaproveitado
    if (isDesktop && !isAuthPage) {
      for (const aside of document.querySelectorAll('aside, [class*="inspector"], [class*="detail-pane"], [class*="side-panel"]')) {
        const st = getComputedStyle(aside);
        const r = aside.getBoundingClientRect();
        if (st.display === 'none' || st.visibility === 'hidden') continue;
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
      const vx2 = Math.min(window.innerWidth, Math.max(mr.right, vx1 + 600));
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
        if (fillRatio < 0.18) {
          issues.push({ severity: 'BLOCK', rule: 'DA-DEAD-SPACE', detail: 'Vazio morto extremo na area principal desktop: ~' + emptyPct + '% da viewport sem conteudo real' });
        } else if (fillRatio < 0.30) {
          issues.push({ severity: 'HIGH', rule: 'DA-DEAD-SPACE', detail: 'Espaco vazio excessivo na area principal desktop: ~' + emptyPct + '% da viewport sem densidade util' });
        }
      }
    }

    // 15. DA-SURFACE-FLAT: falta de separacao visual Z1 vs Z2
    if (!isAuthPage) {
      const bodyLum = lum(resolveBg(document.body));
      const containers = Array.from(mainEl.querySelectorAll('section, article, table, aside, [class*="card"], [class*="panel"], [class*="sheet"], [class*="box"], [class*="surface"]')).filter((el) => {
        const st = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        return st.display !== 'none' && r.width >= 160 && r.height >= 60;
      });
      if (containers.length >= 1) {
        let elevated = 0;
        for (const el of containers.slice(0, 40)) {
          const st = getComputedStyle(el);
          const bg = parseRgb(st.backgroundColor);
          const hasBgDelta = bg && bg[3] > 0.5 && Math.abs(lum(bg) - bodyLum) >= 0.012;
          const bw = parseFloat(st.borderTopWidth || '0') + parseFloat(st.borderLeftWidth || '0');
          const bc = parseRgb(st.borderTopColor);
          const hasBorder = bw >= 1 && bc && bc[3] > 0.08;
          const hasShadow = st.boxShadow && st.boxShadow !== 'none';
          if (hasBgDelta || hasBorder || hasShadow) elevated++;
        }
        if (elevated === 0) {
          issues.push({ severity: 'HIGH', rule: 'DA-SURFACE-FLAT', detail: 'Superficies Z2 sem separacao visual perceptivel do canvas Z1 (sem borda, elevacao ou delta de luminosidade)' });
        }
      }
    }
  }

  return {
    title: document.title,
    scrollWidth: docEl.scrollWidth,
    innerWidth: window.innerWidth,
    issues,
  };
})()`;

function pickViewportsForEntry(entry, args, hasMultiPlatform) {
  if (entry.isVitrine) return args.viewports.includes('desktop') ? ['desktop'] : [args.viewports[0]];
  if (args.allViewports || !hasMultiPlatform) return args.viewports;
  if (entry.platform === 'desktop' && args.viewports.includes('desktop')) return ['desktop'];
  if (entry.platform === 'mobile' && args.viewports.includes('mobile')) return ['mobile'];
  return args.viewports;
}

async function main() {
  const args = parseArgs(process.argv);
  const browserPath = findBrowser();
  if (!browserPath) {
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
        label: e.target.replace(/[^a-z0-9]+/gi, '-').slice(0, 40),
        url: e.target,
        platform: e.platform,
        isVitrine: e.isVitrine,
      };
    }
    const abs = path.resolve(e.target);
    const rel = path.relative(rootDir, abs).split(path.sep).join('/');
    return {
      label: path.basename(abs, path.extname(abs)),
      url: `http://127.0.0.1:${staticSrv.port}/${rel}`,
      platform: e.platform,
      isVitrine: e.isVitrine,
    };
  });

  let browser = null;
  const report = [];
  try {
    browser = await launchBrowser(browserPath);
    const pagesRes = await fetch(`http://127.0.0.1:${browser.port}/json/list`);
    const pages = await pagesRes.json();
    const pageTarget = pages.find((p) => p.type === 'page') || pages[0];
    if (!pageTarget?.webSocketDebuggerUrl) throw new Error('Target de pagina CDP nao disponivel.');

    const cdp = new CDPClient(pageTarget.webSocketDebuggerUrl);
    await cdp.connect();
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Network.enable');

    const consoleErrors = [];
    const failedAssets = [];
    cdp.on('Runtime.exceptionThrown', (p) => {
      const ex = p.exceptionDetails || {};
      const desc = ex.exception?.description || ex.text || 'Excecao JS nao tratada';
      const firstLine = String(desc).split('\n')[0];
      const loc = ex.url ? ` (${path.basename(ex.url)}:${(ex.lineNumber || 0) + 1})` : '';
      consoleErrors.push(`${firstLine}${loc}`);
    });
    cdp.on('Runtime.consoleAPICalled', (p) => {
      if (p.type === 'error') {
        const msg = (p.args || []).map((a) => a.value || a.description || '').join(' ');
        if (msg && !/favicon\.ico/i.test(msg)) consoleErrors.push(msg.slice(0, 220));
      }
    });
    cdp.on('Network.responseReceived', (p) => {
      const res = p.response || {};
      const url = res.url || '';
      if (res.status >= 400 && url.startsWith('http://127.0.0.1:') && !url.endsWith('/favicon.ico')) {
        failedAssets.push(`HTTP ${res.status}: ${new URL(url).pathname}`);
      }
    });

    for (const target of resolvedTargets) {
      const vps = pickViewportsForEntry(target, args, hasMultiPlatform);
      for (const vpName of vps) {
        const vp = VIEWPORTS[vpName];
        if (!vp) continue;
        for (const theme of args.themes) {
          consoleErrors.length = 0;
          failedAssets.length = 0;
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
          await new Promise((r) => setTimeout(r, target.isVitrine ? 650 : 400));

          await cdp.send('Runtime.evaluate', {
            expression: `(() => {
              document.documentElement.setAttribute('data-theme', '${theme}');
              document.dispatchEvent(new CustomEvent('designaura:themechange', { detail: { theme: '${theme}' } }));
              return true;
            })()`,
            returnByValue: true,
          });
          await new Promise((r) => setTimeout(r, 250));

          const evalRes = await cdp.send('Runtime.evaluate', {
            expression: DOM_AUDIT_FN,
            returnByValue: true,
          });
          const domData = evalRes?.result?.value || { issues: [] };
          const issues = [...(domData.issues || [])];
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

          report.push({
            target: target.label,
            url: target.url,
            viewport: `${vpName} (${vp.width}x${vp.height})`,
            theme,
            screenshot: shotPath,
            issues,
          });
        }
      }
    }
    cdp.close();
  } finally {
    if (browser) {
      try { browser.proc.kill('SIGTERM'); } catch {}
      try { fs.rmSync(browser.userDataDir, { recursive: true, force: true }); } catch {}
    }
    if (staticSrv) {
      try { staticSrv.server.close(); } catch {}
    }
  }

  const reportPath = path.join(outDir, 'audit-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2), 'utf-8');

  let totalBlock = 0;
  let totalHigh = 0;
  console.log('# Auditoria Visual & DOM Real (Design Aura v2.0)');
  console.log(`- **Capturas geradas:** ${report.length} · **Relatorio JSON:** ${reportPath}\n`);
  console.log('| Tela | Viewport | Tema | Screenshot | Status | Achados |');
  console.log('|---|---|---|---|---|---|');
  for (const r of report) {
    const blocks = r.issues.filter((i) => i.severity === 'BLOCK').length;
    const highs = r.issues.filter((i) => i.severity === 'HIGH').length;
    totalBlock += blocks;
    totalHigh += highs;
    const status = blocks > 0 ? 'BLOCK' : highs > 0 ? 'HIGH' : 'PASS';
    const summary = r.issues.length ? r.issues.map((i) => `${i.rule}: ${i.detail}`).join('; ') : 'OK';
    console.log(`| ${r.target} | ${r.viewport} | ${r.theme} | ${path.basename(r.screenshot)} | **${status}** | ${summary} |`);
  }

  if (args.strict && (totalBlock > 0 || totalHigh > 0)) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Falha na auditoria visual headless:', err);
  process.exit(1);
});
