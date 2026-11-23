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
