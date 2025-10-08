// web/static/utils/prefetch.ts

import { DataStore } from './dataStore.js';
import { getCurrentLanguage } from '../translations.js';

let JSZipLib: any = null;

async function ensureJsZip(): Promise<any> {
  if (JSZipLib) return JSZipLib;
  try {
    const mod = await import('jszip');
    JSZipLib = (mod as any).default || mod;
    return JSZipLib;
  } catch (_) {}
  const w: any = window as any;
  if (w && w.JSZip) {
    JSZipLib = w.JSZip;
    return JSZipLib;
  }
  try {
    JSZipLib = await new Promise<any>((resolve, reject) => {
      const existing = document.getElementById('jszip-lib');
      if (existing) {
        const win: any = window as any;
        return resolve(win.JSZip || null);
      }
      const s = document.createElement('script');
      s.id = 'jszip-lib';
      s.src = 'static/vendor/jszip.min.js';
      s.async = true;
      s.onload = () => {
        const win: any = window as any;
        resolve(win.JSZip || null);
      };
      s.onerror = () => reject(new Error('Failed to load jszip vendor'));
      document.head.appendChild(s);
    });
  } catch (_) {
    JSZipLib = null;
  }
  return JSZipLib;
}

export type PrefetchProgress = {
  total: number;
  processed: number;
};

export async function prefetchAllHexMarkdown(onProgress?: (p: PrefetchProgress) => void): Promise<void> {
  const lang = getCurrentLanguage();
  const serverVersion = (window as any).__GEN_VERSION__ || '';
  const storedVersion = await DataStore.getVersion(lang);
  if (storedVersion && (!serverVersion || storedVersion === String(serverVersion))) {
    return;
  }

  await DataStore.clearHexMarkdown(lang);

  const res = await fetch('api/export');
  if (!res.ok) throw new Error(`Export fetch failed: HTTP ${res.status}`);
  const blob = await res.blob();

  const JSZip = await ensureJsZip();
  if (!JSZip) throw new Error('JSZip not available');
  const zip = await JSZip.loadAsync(blob);

  const entries = Object.keys(zip.files);
  const hexPrefix = entries.find(p => p.endsWith('dying_lands_output/hexes/')) || 'dying_lands_output/hexes/';
  const hexFiles = entries.filter(p => p.startsWith(hexPrefix) && /hex_\d{4}\.md$/.test(p));
  const total = hexFiles.length;
  let processed = 0;
  if (onProgress) onProgress({ total, processed });

  for (const path of hexFiles) {
    const file = zip.files[path];
    if (!file) continue;
    const markdown: string = await file.async('string');
    const codeMatch = path.match(/hex_(\d{4})\.md$/);
    if (codeMatch) {
      const hexCode = codeMatch[1];
      await DataStore.setHexMarkdown(lang, hexCode, markdown);
    }
    processed++;
    if (onProgress && (processed % 50 === 0 || processed === total)) onProgress({ total, processed });
  }

  await DataStore.setVersion(lang, String(serverVersion || storedVersion || '1'));
}
