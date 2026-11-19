#!/usr/bin/env node
/**
 * Captura screenshots multi-viewport (Dark & Light) e audita o DOM real
 * via Chrome DevTools Protocol (Chromium headless, zero dependencias npm).
 *
 * Uso:
 *   node capture_and_audit.mjs <arquivo-ou-url> [...] --out <dir> [--viewports desktop,mobile] [--themes dark,light] [--strict]
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
};

function screensFromManifest(manifestPath) {
  const abs = path.resolve(manifestPath);
  const data = JSON.parse(fs.readFileSync(abs, 'utf8'));
  const base = path.dirname(abs);
  return (data.screens || [])
    .map((screen) => screen.file)
    .filter((file) => file && !/^https?:\/\//i.test(file))
    .map((file) => path.resolve(base, file));
}

function parseArgs(argv) {
  const args = { targets: [], out: './audit-shots', viewports: ['desktop', 'mobile'], themes: ['dark', 'light'], strict: false, manifest: '' };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--out' && argv[i + 1]) args.out = argv[++i];
    else if (a === '--viewports' && argv[i + 1]) args.viewports = argv[++i].split(',').map((s) => s.trim()).filter(Boolean);
    else if (a === '--themes' && argv[i + 1]) args.themes = argv[++i].split(',').map((s) => s.trim()).filter(Boolean);
    else if (a === '--manifest' && argv[i + 1]) args.manifest = argv[++i];
    else if (a === '--strict') args.strict = true;
    else if (a === '--help' || a === '-h') {
      console.log('Uso: node capture_and_audit.mjs <arquivo|url> [...] --manifest screen-manifest.json --out <dir> [--viewports desktop,tablet,mobile] [--themes dark,light] [--strict]');
      process.exit(0);
    } else args.targets.push(a);
  }
  if (args.manifest) args.targets.push(...screensFromManifest(args.manifest));
  args.targets = [...new Set(args.targets)];
  if (!args.targets.length) {
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
        const list = this.events.get(msg.method) || [];
        list.forEach((fn) => fn(msg.params));
      }
    });
  }
  on(method, fn) {
    if (!this.events.has(method)) this.events.set(method, []);
    this.events.get(method).push(fn);
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

  // 3. Alvos de toque mobile < 44x44px em controles principais (ignora links inline e elementos escalados dentro de canvas Figma)
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

  return {
    title: document.title,
    scrollWidth: docEl.scrollWidth,
    innerWidth: window.innerWidth,
    issues,
  };
})()`;

async function main() {
  const args = parseArgs(process.argv);
  const browserPath = findBrowser();
  if (!browserPath) {
    console.error('Erro: Chromium/Google Chrome nao encontrado no ambiente.');
    process.exit(1);
  }

  const outDir = path.resolve(args.out);
  fs.mkdirSync(outDir, { recursive: true });

  // Determina pasta raiz caso haja arquivos locais
  const localFiles = args.targets.filter((t) => !/^https?:\/\//i.test(t)).map((t) => path.resolve(t));
  let staticSrv = null;
  let rootDir = process.cwd();
  if (localFiles.length) {
    rootDir = path.dirname(localFiles[0]);
    for (const f of localFiles) {
      while (!f.startsWith(rootDir + path.sep) && f !== rootDir && path.dirname(rootDir) !== rootDir) {
        rootDir = path.dirname(rootDir);
      }
    }
    staticSrv = await startStaticServer(rootDir);
  }

  const resolvedTargets = args.targets.map((t) => {
    if (/^https?:\/\//i.test(t)) return { label: t.replace(/[^a-z0-9]+/gi, '-').slice(0, 40), url: t };
    const abs = path.resolve(t);
    const rel = path.relative(rootDir, abs).split(path.sep).join('/');
    return { label: path.basename(abs, path.extname(abs)), url: `http://127.0.0.1:${staticSrv.port}/${rel}` };
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

    const consoleErrors = [];
    cdp.on('Runtime.exceptionThrown', (p) => {
      consoleErrors.push(p.exceptionDetails?.text || 'Excecao JS nao tratada');
    });
    cdp.on('Runtime.consoleAPICalled', (p) => {
      if (p.type === 'error') {
        consoleErrors.push((p.args || []).map((a) => a.value || a.description || '').join(' '));
      }
    });

    for (const target of resolvedTargets) {
      for (const vpName of args.viewports) {
        const vp = VIEWPORTS[vpName];
        if (!vp) continue;
        for (const theme of args.themes) {
          consoleErrors.length = 0;
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
            const onLoad = () => res();
            cdp.on('Page.loadEventFired', onLoad);
            setTimeout(onLoad, 6000);
          });
          await cdp.send('Page.navigate', { url: target.url });
          await loadPromise;
          await new Promise((r) => setTimeout(r, 450));

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
          for (const ce of consoleErrors) {
            issues.push({ severity: 'BLOCK', rule: 'DA-JS-ERROR', detail: ce });
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
  console.log('# Auditoria Visual & DOM Real (Design Aura)');
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
