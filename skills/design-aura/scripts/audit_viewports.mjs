import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const presets = new Map([
  ['desktop', { width: 1440, height: 900, mobile: false, dpr: 1 }],
  ['tablet', { width: 768, height: 1024, mobile: true, dpr: 2 }],
  ['mobile', { width: 390, height: 844, mobile: true, dpr: 2 }],
]);

export function resolveViewport(name) {
  if (presets.has(name)) return presets.get(name);
  const match = typeof name === 'string' && /^(mobile-)?([1-9]\d{1,3})x([1-9]\d{1,3})$/.exec(name);
  if (!match) throw new Error(`Viewport inválido: ${name}. Use desktop, tablet, mobile, 1920x1080 ou mobile-360x800.`);
  const mobile = Boolean(match[1]);
  return { width: Number(match[2]), height: Number(match[3]), mobile, dpr: mobile ? 2 : 1 };
}

export function validateViewports(viewports) {
  if (!Array.isArray(viewports) || !viewports.length) throw new Error('Informe ao menos um viewport.');
  for (const name of viewports) resolveViewport(name);
  return [...new Set(viewports)];
}


/** Chrome, Chromium ou Edge em Linux, macOS ou Windows (CHROME_PATH tem prioridade). */
export function findBrowser() {
  const env = process.env;
  const win = [env.PROGRAMFILES, env['PROGRAMFILES(X86)'], env.LOCALAPPDATA].filter(Boolean);
  const candidates = [
    env.CHROME_PATH,
    env.PUPPETEER_EXECUTABLE_PATH,
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/snap/bin/chromium',
    '/usr/bin/microsoft-edge',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    ...win.map((d) => path.join(d, 'Google', 'Chrome', 'Application', 'chrome.exe')),
    ...win.map((d) => path.join(d, 'Microsoft', 'Edge', 'Application', 'msedge.exe')),
  ].filter(Boolean);
  for (const c of candidates) {
    try { if (fs.existsSync(c)) return c; } catch { /* segue */ }
  }
  // Chromium baixado pelo Playwright
  const pw = path.join(os.homedir(), env.LOCALAPPDATA ? 'AppData/Local/ms-playwright' : '.cache/ms-playwright');
  try {
    for (const dir of fs.readdirSync(pw).filter((d) => d.startsWith('chromium')).sort().reverse()) {
      for (const rel of ['chrome-linux/chrome', 'chrome-win/chrome.exe', 'chrome-mac/Chromium.app/Contents/MacOS/Chromium']) {
        const p = path.join(pw, dir, rel);
        if (fs.existsSync(p)) return p;
      }
    }
  } catch { /* sem cache do Playwright */ }
  return null;
}
