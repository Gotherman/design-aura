#!/usr/bin/env node
/**
 * Servidor Unificado de Link Unico da Design Aura.
 *
 * Combina em 1 unica porta (padrao 0.0.0.0:4188):
 *   - '/'           -> entrega.html (Hub unificado: Mapa Figma · App ao Vivo · Preview · Galeria · Biblia + PDF)
 *   - '/design/*'   -> artefatos da pasta design/ (fluxo.html, preview.html, index.html, DESIGN-BIBLE.html/pdf, tokens.css)
 *   - '/app/*'      -> SPA buildada (ex.: dist/ de React/Vite/Next) com fallback automatico para dist/index.html
 *   - '/healthz'    -> checagem JSON 200 OK
 *
 * Uso:
 *   node serve_entrega.mjs --design-dir ./design [--app-dir ./dist] [--port 4188] [--host 0.0.0.0]
 */
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.htm': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.mjs': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.gif': 'image/gif',
  '.ico': 'image/x-icon',
  '.pdf': 'application/pdf',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
  '.ttf': 'font/ttf',
  '.txt': 'text/plain; charset=utf-8',
  '.md': 'text/markdown; charset=utf-8',
};

function parseArgs(argv) {
  const cfg = {
    designDir: process.cwd(),
    appDir: '',
    port: 4188,
    host: '0.0.0.0',
  };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if ((a === '--design-dir' || a === '--dir') && argv[i + 1]) cfg.designDir = argv[++i];
    else if (a === '--app-dir' && argv[i + 1]) cfg.appDir = argv[++i];
    else if (a === '--port' && argv[i + 1]) cfg.port = parseInt(argv[++i], 10) || 4188;
    else if (a === '--host' && argv[i + 1]) cfg.host = argv[++i];
    else if (a === '--help' || a === '-h') {
      console.log('Uso: node serve_entrega.mjs --design-dir ./design [--app-dir ./dist] [--port 4188] [--host 0.0.0.0]');
      process.exit(0);
    }
  }
  cfg.designDir = path.resolve(cfg.designDir);
  cfg.appDir = cfg.appDir ? path.resolve(cfg.appDir) : '';
  return cfg;
}

function safeResolve(rootDir, relPath) {
  const normalized = path.normalize('/' + relPath).replace(/^(\.\.[/\\])+/, '');
  const candidate = path.resolve(rootDir, '.' + normalized);
  if (candidate !== rootDir && !candidate.startsWith(rootDir + path.sep)) return null;
  return candidate;
}

function sendFile(res, filePath) {
  const ext = path.extname(filePath).toLowerCase();
  res.writeHead(200, {
    'Content-Type': MIME[ext] || 'application/octet-stream',
    'Cache-Control': 'no-store',
  });
  fs.createReadStream(filePath).pipe(res);
}

function findEntryFile(dir, candidates) {
  if (!dir || !fs.existsSync(dir)) return null;
  for (const name of candidates) {
    const full = path.join(dir, name);
    if (fs.existsSync(full) && fs.statSync(full).isFile()) return full;
  }
  return null;
}

export function createEntregaServer({ designDir, appDir }) {
  const designRoot = path.resolve(designDir);
  const appRoot = appDir ? path.resolve(appDir) : '';

  return http.createServer((req, res) => {
    try {
      const rawUrl = req.url || '/';
      const pathname = decodeURIComponent(rawUrl.split('?')[0]);

      if (pathname === '/healthz') {
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
        res.end(JSON.stringify({ ok: true, designDir: designRoot, appDir: appRoot || null }));
        return;
      }

      if (pathname === '/' || pathname === '/entrega.html') {
        const entry =
          findEntryFile(designRoot, ['entrega.html', 'fluxo.html', 'index.html']) ||
          findEntryFile(appRoot, ['entrega.html', 'index.html']);
        if (entry) return sendFile(res, entry);
      }

      // 1. Rotas /design/* -> servidas da pasta design/
      if (pathname === '/design' || pathname.startsWith('/design/')) {
        const sub = pathname.replace(/^\/design\/?/, '');
        const resolved = safeResolve(designRoot, sub || 'entrega.html');
        if (resolved && fs.existsSync(resolved)) {
          const target = fs.statSync(resolved).isDirectory()
            ? findEntryFile(resolved, ['entrega.html', 'index.html', 'fluxo.html'])
            : resolved;
          if (target) return sendFile(res, target);
        }
      }

      // 2. Rotas /app/* -> servidas da pasta dist/ (SPA) com fallback para index.html
      if (appRoot && (pathname === '/app' || pathname.startsWith('/app/'))) {
        const sub = pathname.replace(/^\/app\/?/, '');
        const resolved = safeResolve(appRoot, sub || 'index.html');
        if (resolved && fs.existsSync(resolved) && fs.statSync(resolved).isFile()) {
          return sendFile(res, resolved);
        }
        const spaFallback = findEntryFile(appRoot, ['index.html']);
        if (spaFallback) return sendFile(res, spaFallback);
      }

      // 3. Tenta resolver diretamente na pasta design/ (ex.: /fluxo.html, /preview.html, /tokens.css, /tela.html)
      const directDesign = safeResolve(designRoot, pathname);
      if (directDesign && fs.existsSync(directDesign)) {
        const target = fs.statSync(directDesign).isDirectory()
          ? findEntryFile(directDesign, ['entrega.html', 'index.html'])
          : directDesign;
        if (target) return sendFile(res, target);
      }

      // 4. Tenta resolver na pasta app/ (assets como /assets/index-xxx.js ou rotas diretas SPA)
      if (appRoot) {
        const directApp = safeResolve(appRoot, pathname);
        if (directApp && fs.existsSync(directApp) && fs.statSync(directApp).isFile()) {
          return sendFile(res, directApp);
        }
        // Fallback SPA somente para caminhos sem extensao de asset ausente
        if (!path.extname(pathname)) {
          const spaFallback = findEntryFile(appRoot, ['index.html']);
          if (spaFallback) return sendFile(res, spaFallback);
        }
      }

      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end(`Not found: ${pathname}`);
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end(String(err));
    }
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const cfg = parseArgs(process.argv);
  const server = createEntregaServer(cfg);
  server.listen(cfg.port, cfg.host, () => {
    console.log(`Design Aura · Entrega Unificada ativa em http://${cfg.host}:${cfg.port}/`);
    console.log(`  - Design Dir: ${cfg.designDir}`);
    if (cfg.appDir) console.log(`  - App SPA Dir: ${cfg.appDir} (montado em /app e fallback SPA)`);
  });
}
