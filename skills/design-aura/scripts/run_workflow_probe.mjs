#!/usr/bin/env node
/**
 * Motor CDP de Testes Interativos de Workflow E2E (Design Aura v2.4.0 · Fase 4.5, zero dependencias npm).
 *
 * Projetado para os Subagentes Testers (Read-Only): navega, clica em botoes/linhas,
 * preenche campos, seleciona filtros, alterna tema Dark/Light, valida assertivas de negocio
 * + layout pos-clique (zero overflow, zero recorte, zero erro JS/404) e fotografa evidencias.
 *
 * Uso:
 *   node run_workflow_probe.mjs --scenario qa-scenario.json --out ./qa-evidence [--base-url http://127.0.0.1:4188] [--root ./design] [--strict]
 */
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { spawn } from 'node:child_process';

import { resolveViewport } from './audit_viewports.mjs';

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.mjs': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.webp': 'image/webp',
  '.woff2': 'font/woff2',
};

function parseArgs(argv) {
  const args = { scenario: '', out: './qa-evidence', baseUrl: '', root: '', strict: false };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--scenario' && argv[i + 1]) args.scenario = argv[++i];
    else if (a === '--out' && argv[i + 1]) args.out = argv[++i];
    else if (a === '--base-url' && argv[i + 1]) args.baseUrl = argv[++i];
    else if (a === '--root' && argv[i + 1]) args.root = argv[++i];
    else if (a === '--strict') args.strict = true;
    else if (a === '--help' || a === '-h') {
      console.log('Uso: node run_workflow_probe.mjs --scenario qa-scenario.json --out ./qa-evidence [--base-url http://127.0.0.1:4188] [--root ./design] [--strict]');
      process.exit(0);
    }
  }
  if (!args.scenario) {
    console.error('Erro: informe --scenario <arquivo.json>.');
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
    const rootAbs = path.resolve(rootDir);
    const server = http.createServer((req, res) => {
      try {
        const clean = decodeURIComponent((req.url || '/').split('?')[0]);
        let target = path.resolve(rootAbs, '.' + clean);
        if (!target.startsWith(rootAbs)) { res.writeHead(403); res.end('Forbidden'); return; }
        if (fs.existsSync(target) && fs.statSync(target).isDirectory()) target = path.join(target, 'index.html');
        if (!fs.existsSync(target)) { res.writeHead(404); res.end('Not found'); return; }
        const ext = path.extname(target).toLowerCase();
        res.writeHead(200, { 'Content-Type': MIME_TYPES[ext] || 'application/octet-stream' });
        fs.createReadStream(target).pipe(res);
      } catch (err) {
        res.writeHead(500); res.end(String(err));
      }
    });
    server.on('error', reject);
    server.listen(0, '127.0.0.1', () => resolve({ server, port: server.address().port }));
  });
}

function launchBrowser(browserPath) {
  return new Promise((resolve, reject) => {
    const userDataDir = fs.mkdtempSync('/tmp/da-probe-');
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
        (this.events.get(msg.method) || []).slice().forEach((fn) => fn(msg.params));
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
    const wrapped = (params) => { this.off(method, wrapped); fn(params); };
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
  close() { try { this.ws.close(); } catch {} }
}

function findElementExpr(selector) {
  const s = JSON.stringify(selector);
  return `(() => {
    const sel = ${s};
    if (sel.startsWith('text=')) {
      const needle = sel.slice(5).trim().toLowerCase();
      const cands = Array.from(document.querySelectorAll('button, a, [role="button"], [role="tab"], li, tr, [data-da-open], div, span'));
      for (const el of cands) {
        const st = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        if (st.display === 'none' || st.visibility === 'hidden' || r.width === 0 || r.height === 0) continue;
        const txt = (el.textContent || '').replace(/\\s+/g, ' ').trim().toLowerCase();
        if (txt === needle || (txt.includes(needle) && el.children.length <= 3)) return el;
      }
      return null;
    }
    return document.querySelector(sel);
  })()`;
}

async function runStep(cdp, step, ctx) {
  const act = (step.action || '').trim();
  const label = step.label || `${act} ${step.selector || step.url || step.text || step.theme || ''}`.trim();
  const out = { action: act, label, status: 'PASS', detail: 'OK', screenshot: null };

  try {
    if (act === 'goto') {
      const raw = step.url || step.route || step.file || '/';
      const url = /^https?:\/\//i.test(raw)
        ? raw
        : `${ctx.baseUrl.replace(/\/+$/, '')}${raw.startsWith('/') ? raw : '/' + raw}`;
      const loaded = new Promise((res) => {
        let done = false;
        const fin = () => { if (!done) { done = true; clearTimeout(t); res(); } };
        const h = cdp.once('Page.loadEventFired', fin);
        const t = setTimeout(() => { cdp.off('Page.loadEventFired', h); fin(); }, 6000);
      });
      await cdp.send('Page.navigate', { url });
      await loaded;
      await new Promise((r) => setTimeout(r, step.waitMs || 320));
      out.detail = `Navegou para ${url}`;
    } else if (act === 'setTheme') {
      const th = step.theme === 'light' ? 'light' : 'dark';
      await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: th }] });
      await cdp.send('Runtime.evaluate', {
        expression: `(() => {
          try { localStorage.setItem('design-aura:theme', '${th}'); } catch (e) {}
          document.documentElement.setAttribute('data-theme', '${th}');
          document.dispatchEvent(new CustomEvent('designaura:themechange', { detail: { theme: '${th}' } }));
          return true;
        })()`,
        returnByValue: true,
      });
      await new Promise((r) => setTimeout(r, 200));
      out.detail = `Tema definido para ${th}`;
    } else if (act === 'click') {
      const res = await cdp.send('Runtime.evaluate', {
        expression: `(() => {
          const el = ${findElementExpr(step.selector)};
          if (!el) return { ok: false, reason: 'Elemento nao encontrado: ' + ${JSON.stringify(step.selector)} };
          el.scrollIntoView({ block: 'center', inline: 'center' });
          el.click();
          return { ok: true, tag: el.tagName, text: (el.textContent || '').trim().slice(0, 60) };
        })()`,
        returnByValue: true,
      });
      const val = res?.result?.value || { ok: false, reason: 'Falha ao avaliar clique' };
      if (!val.ok) throw new Error(val.reason);
      await new Promise((r) => setTimeout(r, step.waitMs || 260));
      out.detail = `Clicou em ${val.tag} "${val.text}"`;
    } else if (act === 'fill') {
      const res = await cdp.send('Runtime.evaluate', {
        expression: `(() => {
          const el = ${findElementExpr(step.selector)};
          if (!el) return { ok: false, reason: 'Campo nao encontrado: ' + ${JSON.stringify(step.selector)} };
          el.focus();
          const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
          const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
          if (setter) setter.call(el, ${JSON.stringify(String(step.value ?? ''))});
          else el.value = ${JSON.stringify(String(step.value ?? ''))};
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
          return { ok: true };
        })()`,
        returnByValue: true,
      });
      if (!res?.result?.value?.ok) throw new Error(res?.result?.value?.reason || 'Falha em fill');
      await new Promise((r) => setTimeout(r, 120));
      out.detail = `Preencheu ${step.selector}`;
    } else if (act === 'select') {
      const res = await cdp.send('Runtime.evaluate', {
        expression: `(() => {
          const el = ${findElementExpr(step.selector)};
          if (!el) return { ok: false, reason: 'Select nao encontrado: ' + ${JSON.stringify(step.selector)} };
          el.value = ${JSON.stringify(String(step.value ?? ''))};
          el.dispatchEvent(new Event('change', { bubbles: true }));
          return { ok: true, value: el.value };
        })()`,
        returnByValue: true,
      });
      if (!res?.result?.value?.ok) throw new Error(res?.result?.value?.reason || 'Falha em select');
      await new Promise((r) => setTimeout(r, 140));
      out.detail = `Selecionou ${step.value} em ${step.selector}`;
    } else if (act === 'press') {
      const key = step.key || 'Enter';
      await cdp.send('Runtime.evaluate', {
        expression: `(() => {
          const target = document.activeElement || document.body;
          target.dispatchEvent(new KeyboardEvent('keydown', { key: ${JSON.stringify(key)}, bubbles: true }));
          target.dispatchEvent(new KeyboardEvent('keyup', { key: ${JSON.stringify(key)}, bubbles: true }));
          return true;
        })()`,
        returnByValue: true,
      });
      await new Promise((r) => setTimeout(r, 180));
      out.detail = `Tecla ${key} enviada`;
    } else if (act === 'wait') {
      await new Promise((r) => setTimeout(r, step.ms || 300));
      out.detail = `Aguardou ${step.ms || 300}ms`;
    } else if (act === 'waitFor') {
      const timeout = step.timeoutMs || 4000;
      const t0 = Date.now();
      let found = false;
      while (Date.now() - t0 < timeout) {
        const res = await cdp.send('Runtime.evaluate', {
          expression: `(() => {
            const el = ${findElementExpr(step.selector)};
            if (!el) return false;
            const st = getComputedStyle(el);
            const r = el.getBoundingClientRect();
            return st.display !== 'none' && st.visibility !== 'hidden' && r.width > 0 && r.height > 0;
          })()`,
          returnByValue: true,
        });
        if (res?.result?.value) { found = true; break; }
        await new Promise((r) => setTimeout(r, 120));
      }
      if (!found) throw new Error(`Timeout aguardando elemento visivel: ${step.selector}`);
      out.detail = `Visivel: ${step.selector}`;
    } else if (act === 'assertVisible' || act === 'assertHidden') {
      const res = await cdp.send('Runtime.evaluate', {
        expression: `(() => {
          const el = ${findElementExpr(step.selector)};
          if (!el) return { visible: false };
          const st = getComputedStyle(el);
          const r = el.getBoundingClientRect();
          return { visible: st.display !== 'none' && st.visibility !== 'hidden' && parseFloat(st.opacity || '1') > 0.05 && r.width > 0 && r.height > 0 };
        })()`,
        returnByValue: true,
      });
      const visible = !!res?.result?.value?.visible;
      if (act === 'assertVisible' && !visible) throw new Error(`Esperava elemento visivel: ${step.selector}`);
      if (act === 'assertHidden' && visible) throw new Error(`Esperava elemento oculto: ${step.selector}`);
      out.detail = `${act} OK (${step.selector})`;
    } else if (act === 'assertReachable') {
      if (!step.selector) throw new Error('assertReachable requer selector.');
      const res = await cdp.send('Runtime.evaluate', {
        expression: `(() => {
          const el = ${findElementExpr(step.selector)};
          if (!el || !el.checkVisibility({ opacityProperty: true, visibilityProperty: true })) return 'Controle oculto ou ausente';
          if (el.matches(':disabled') || el.closest('[inert], [aria-disabled="true"]')) return 'Controle desabilitado';
          const r = el.getBoundingClientRect();
          if (r.left < 0 || r.top < 0 || r.right > innerWidth || r.bottom > innerHeight) return 'Controle fora da área visível';
          for (const [x, y] of [[0.5, 0.5], [0.2, 0.25], [0.8, 0.25], [0.2, 0.75], [0.8, 0.75]]) {
            const hit = document.elementFromPoint(r.left + r.width * x, r.top + r.height * y);
            if (!el.contains(hit)) return 'Ação encoberta por ' + (hit?.id || hit?.tagName || 'uma região recortada');
          }
          return '';
        })()`,
        returnByValue: true,
      });
      const issue = res?.result?.value;
      if (issue !== '') throw new Error(`${step.selector}: ${issue || 'Não foi possível verificar o controle'}`);
      out.detail = `Controle alcançável: ${step.selector}`;
    } else if (act === 'assertText') {
      const sel = step.selector || 'body';
      const exact = step.equals !== undefined;
      const needle = String(step.equals ?? step.contains ?? step.text ?? '');
      if (!exact && !needle) throw new Error('assertText requer equals, contains ou text.');
      const expected = JSON.stringify(needle.replace(/\s+/g, ' ').trim());
      const res = await cdp.send('Runtime.evaluate', {
        expression: `(() => {
          const el = ${findElementExpr(sel)};
          if (!el) return { ok: false, reason: 'Elemento nao encontrado: ' + ${JSON.stringify(sel)} };
          const txt = (el.textContent || '').replace(/\\s+/g, ' ').trim();
          return { ok: ${exact} ? txt === ${expected} : txt.toLowerCase().includes(${expected}.toLowerCase()), sample: txt.slice(0, 140) };
        })()`,
        returnByValue: true,
      });
      const v = res?.result?.value;
      if (!v?.ok) throw new Error(v?.reason || `Texto "${needle}" nao encontrado em ${sel} (obtido: "${v?.sample || ''}")`);
      out.detail = `Texto "${needle}" confirmado`;
    } else if (act === 'assertCount') {
      const res = await cdp.send('Runtime.evaluate', {
        expression: `document.querySelectorAll(${JSON.stringify(step.selector)}).length`,
        returnByValue: true,
      });
      const cnt = Number(res?.result?.value ?? 0);
      if (step.equals !== undefined && cnt !== step.equals) throw new Error(`Esperava ${step.equals} elementos em ${step.selector}, obteve ${cnt}`);
      if (step.min !== undefined && cnt < step.min) throw new Error(`Esperava >= ${step.min} elementos em ${step.selector}, obteve ${cnt}`);
      out.detail = `Contagem ${cnt} OK (${step.selector})`;
    } else if (act === 'assertNoOverflow' || act === 'assertNoClip') {
      const res = await cdp.send('Runtime.evaluate', {
        expression: `(() => {
          const issues = [];
          const docEl = document.documentElement;
          if (docEl.scrollWidth > window.innerWidth + 2) {
            issues.push('Overflow horizontal: ' + docEl.scrollWidth + ' > ' + window.innerWidth);
          }
          for (const el of Array.from(document.querySelectorAll('section, article, div, aside, footer')).slice(0, 220)) {
            const st = getComputedStyle(el);
            if (st.display === 'none' || st.visibility === 'hidden') continue;
            const r = el.getBoundingClientRect();
            if (r.width < 80 || r.height < 36) continue;
            if (st.textOverflow === 'ellipsis' || (st.webkitLineClamp && st.webkitLineClamp !== 'none')) continue;
            if ((st.overflowY === 'hidden' || st.overflowY === 'clip') && el.scrollHeight > el.clientHeight + 8) {
              const clippedChild = Array.from(el.children).some((ch) => {
                const cs = getComputedStyle(ch);
                return cs.display !== 'none' && cs.position !== 'absolute' && ch.getBoundingClientRect().bottom > r.bottom + 5;
              });
              if (clippedChild) {
                issues.push('Recorte vertical em ' + (el.className || el.tagName).toString().trim().slice(0, 32));
                break;
              }
            }
          }
          return issues;
        })()`,
        returnByValue: true,
      });
      const found = res?.result?.value || [];
      if (found.length > 0) throw new Error(found.join('; '));
      out.detail = 'Zero overflow horizontal e zero recorte vertical pos-interacao';
    } else if (act === 'screenshot') {
      const fname = (step.name || `step-${ctx.index}`).replace(/[^a-z0-9_-]+/gi, '-') + '.png';
      const fpath = path.join(ctx.outDir, fname);
      const shot = await cdp.send('Page.captureScreenshot', { format: 'png' });
      fs.writeFileSync(fpath, Buffer.from(shot.data, 'base64'));
      out.screenshot = fpath;
      out.detail = `Screenshot salvo: ${fname}`;
    } else {
      throw new Error(`Acao desconhecida no cenario: ${act}`);
    }
  } catch (err) {
    out.status = 'FAIL';
    out.detail = err instanceof Error ? err.message : String(err);
    try {
      const fname = `fail-step-${ctx.index}-${act}.png`.replace(/[^a-z0-9_.-]+/gi, '-');
      const fpath = path.join(ctx.outDir, fname);
      const shot = await cdp.send('Page.captureScreenshot', { format: 'png' });
      fs.writeFileSync(fpath, Buffer.from(shot.data, 'base64'));
      out.screenshot = fpath;
    } catch {}
  }

  return out;
}

async function main() {
  const args = parseArgs(process.argv);
  const browserPath = findBrowser();
  if (!browserPath) {
    console.error('Erro: Chromium/Google Chrome nao encontrado.');
    process.exit(1);
  }
  const scenario = JSON.parse(fs.readFileSync(path.resolve(args.scenario), 'utf8'));
  const vpName = scenario.viewport || 'desktop';
  const vp = resolveViewport(vpName);
  const initTheme = scenario.theme || 'dark';
  if (!['dark', 'light'].includes(initTheme)) throw new Error('Temas válidos: dark e light.');
  const steps = scenario.steps;
  if (!Array.isArray(steps) || !steps.length) throw new Error('Cenário sem passos de QA.');
  const outDir = path.resolve(args.out);
  fs.mkdirSync(outDir, { recursive: true });

  let staticSrv = null;
  let baseUrl = args.baseUrl || scenario.baseUrl || '';
  if (!baseUrl) {
    const rootDir = args.root || scenario.root || path.dirname(path.resolve(args.scenario));
    staticSrv = await startStaticServer(rootDir);
    baseUrl = `http://127.0.0.1:${staticSrv.port}`;
  }

  const consoleErrors = [];
  const failedAssets = [];
  const stepResults = [];
  let browser = null;

  try {
    browser = await launchBrowser(browserPath);
    const pagesRes = await fetch(`http://127.0.0.1:${browser.port}/json/list`);
    const pages = await pagesRes.json();
    const target = pages.find((p) => p.type === 'page') || pages[0];
    const cdp = new CDPClient(target.webSocketDebuggerUrl);
    await cdp.connect();
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Network.enable');

    cdp.on('Runtime.exceptionThrown', (p) => {
      const desc = p.exceptionDetails?.exception?.description || p.exceptionDetails?.text || 'Excecao JS';
      consoleErrors.push(String(desc).split('\n')[0]);
    });
    cdp.on('Runtime.consoleAPICalled', (p) => {
      if (p.type === 'error') {
        const msg = (p.args || []).map((a) => a.value || a.description || '').join(' ');
        if (msg && !/favicon\.ico/i.test(msg)) consoleErrors.push(msg.slice(0, 220));
      }
    });
    cdp.on('Network.responseReceived', (p) => {
      const res = p.response || {};
      if (res.status >= 400 && !String(res.url || '').endsWith('/favicon.ico')) {
        failedAssets.push(`HTTP ${res.status}: ${res.url}`);
      }
    });

    await cdp.send('Emulation.setDeviceMetricsOverride', {
      width: vp.width,
      height: vp.height,
      deviceScaleFactor: vp.dpr,
      mobile: vp.mobile,
    });
    await cdp.send('Emulation.setEmulatedMedia', {
      features: [{ name: 'prefers-color-scheme', value: initTheme }],
    });
    await cdp.send('Page.addScriptToEvaluateOnNewDocument', {
      source: `try { localStorage.setItem('design-aura:theme', '${initTheme}'); } catch (e) {}
               document.addEventListener('DOMContentLoaded', () => {
                 document.documentElement.setAttribute('data-theme', '${initTheme}');
               }, { once: true });`,
    });

    for (let idx = 0; idx < steps.length; idx++) {
      const r = await runStep(cdp, steps[idx], { index: idx + 1, baseUrl, outDir });
      stepResults.push(r);
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

  const failedSteps = stepResults.filter((s) => s.status === 'FAIL');
  const uniqErrors = [...new Set(consoleErrors)];
  const uniq404 = [...new Set(failedAssets)];
  const passed = failedSteps.length === 0 && uniqErrors.length === 0 && uniq404.length === 0;

  const report = {
    name: scenario.name || path.basename(args.scenario),
    viewport: vpName,
    dimensions: { width: vp.width, height: vp.height },
    theme: initTheme,
    passed,
    summary: {
      totalSteps: stepResults.length,
      failedSteps: failedSteps.length,
      consoleErrors: uniqErrors.length,
      failedAssets: uniq404.length,
    },
    consoleErrors: uniqErrors,
    failedAssets: uniq404,
    steps: stepResults,
  };
  const reportPath = path.join(outDir, 'probe-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2), 'utf8');

  console.log(`# Workflow Probe E2E · ${report.name} (${passed ? 'PASS' : 'FAIL'})`);
  console.log(`- Viewport: ${vpName} · Passos: ${stepResults.length} · Falhas: ${failedSteps.length} · JS Errors: ${uniqErrors.length} · 404: ${uniq404.length}`);
  console.log(`- Relatorio: ${reportPath}`);
  for (const s of stepResults) {
    console.log(`  [${s.status}] ${s.label} — ${s.detail}`);
  }
  if (uniqErrors.length) console.log(`  [JS-ERROR] ${uniqErrors.join(' | ')}`);
  if (uniq404.length) console.log(`  [ASSET-404] ${uniq404.join(' | ')}`);

  if (args.strict && !passed) process.exit(1);
}

main().catch((err) => {
  console.error('Falha no Workflow Probe:', err);
  process.exit(1);
});
