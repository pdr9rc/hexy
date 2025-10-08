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

function isSettlementMarkdown(md: string): boolean {
  return /##\s+Settlement Details|⌂\s+\*\*/.test(md) || /\*\*Population:\*\*/i.test(md);
}

function isCityMarkdown(md: string): boolean {
  return /Major City:/i.test(md) || /is_major_city\s*[:=]\s*true/i.test(md);
}

export async function prefetchAllHexMarkdown(onProgress?: (p: PrefetchProgress) => void): Promise<void> {
  const lang = getCurrentLanguage();
  const serverVersion = (window as any).__GEN_VERSION__ || '';
  const storedVersion = await DataStore.getVersion(lang);
  // If we already have a stored version and either server version is absent or matches, skip prefetch
  if (storedVersion && (!serverVersion || storedVersion === String(serverVersion))) {
    return;
  }

  // If serverVersion exists and differs, proceed; if absent but no storedVersion, proceed

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

  try {
    const overlaysResp = await fetch('api/city-overlays');
    if (overlaysResp.ok) {
      const overlays = await overlaysResp.json();
      const list = overlays?.overlays || [];
      for (const ov of list) {
        const name = ov.name || ov.key || ov.display_name;
        if (!name) continue;
        try {
          const gridResp = await fetch(`api/city-overlay/${name}`);
          if (gridResp.ok) {
            const grid = await gridResp.json();
            await DataStore.setOverlay(lang, name, grid);
            const hexGrid = grid?.overlay?.hex_grid || grid?.hex_grid || {};
            for (const hexId of Object.keys(hexGrid)) {
              try {
                const hx = await fetch(`api/city-overlay/${name}/hex/${hexId}`);
                if (hx.ok) {
                  const data = await hx.json();
                  await DataStore.setOverlayHex(lang, name, hexId, data);
                }
              } catch (_) {}
            }
          }
        } catch (_) {}
      }
    }
  } catch (_) {}

  await DataStore.setVersion(lang, String(serverVersion || storedVersion || '1'));
}
