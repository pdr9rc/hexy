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
  // Fallback: window.JSZip
  const w: any = window as any;
  if (w && w.JSZip) {
    JSZipLib = w.JSZip;
    return JSZipLib;
  }
  // Last resort: dynamically load local vendor script
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

function isSettlementMarkdown(md: string): boolean {
  return /##\s+Settlement Details|⌂\s+\*\*/.test(md) || /\*\*Population:\*\*/i.test(md);
}

function isCityMarkdown(md: string): boolean {
  return /Major City:/i.test(md) || /is_major_city\s*[:=]\s*true/i.test(md);
}

export async function prefetchAllHexMarkdown(onProgress?: (p: PrefetchProgress) => void): Promise<void> {
  const lang = getCurrentLanguage();
  const version = (window as any).__GEN_VERSION__ || '';
  const current = await DataStore.getVersion(lang);
  if (current && current === String(version)) {
    return; // Already synced
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
      try {
        if (isSettlementMarkdown(markdown)) {
          const resp = await fetch(`api/settlement/${hexCode}`);
          if (resp.ok) {
            const data = await resp.json();
            await DataStore.setSettlement(lang, hexCode, data);
          }
        }
      } catch (_) {}
      try {
        if (isCityMarkdown(markdown)) {
          const resp = await fetch(`api/city/${hexCode}`);
          if (resp.ok) {
            const data = await resp.json();
            await DataStore.setCity(lang, hexCode, data);
          }
        }
      } catch (_) {}
    }
    processed++;
    if (onProgress && (processed % 50 === 0 || processed === total)) onProgress({ total, processed });
  }

  try {
    const loreResp = await fetch('api/lore-overview');
    if (loreResp.ok) {
      const lore = await loreResp.json();
      await DataStore.setLore(lang, lore);
    }
  } catch (_) {}

  await DataStore.setVersion(lang, String(version));
}
