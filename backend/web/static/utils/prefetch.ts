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

function extractFirst(pattern: RegExp, text: string): string | null {
  const m = text.match(pattern);
  return m ? (m[1] || m[0]).trim() : null;
}

function parseSettlementFromMarkdown(md: string): any | null {
  // Heuristic: identify settlement by settlement marker or tavern/local fields
  const isSettlement = /⌂\s*\*\*|##\s*Settlement/i.test(md) || /\*\*Population:\*\*/i.test(md);
  if (!isSettlement) return null;
  const name = extractFirst(/⌂\s*\*\*([^*]+)\*\*/i, md) || extractFirst(/#\s*Hex\s*\d{4}\s*\n+\*\*Name:\*\*\s*([^\n]+)/i, md) || 'Settlement';
  const population = extractFirst(/\*\*Population:\*\*\s*([^\n]+)/i, md) || '';
  const atmosphere = extractFirst(/\*\*Atmosphere:\*\*\s*([^\n]+)/i, md) || extractFirst(/##\s*Atmosphere\s*\n+([^\n]+)/i, md) || '';
  const notable_feature = extractFirst(/\*\*Notable Feature:\*\*\s*([^\n]+)/i, md) || extractFirst(/##\s*Notable Feature\s*\n+([^\n]+)/i, md) || '';
  const local_tavern = extractFirst(/\*\*Select Menu:\*\*\s*([^\n]+)/i, md) || '';
  const local_power = extractFirst(/\*\*Local Power:\*\*\s*([^\n]+)/i, md) || '';
  const settlement_art = extractFirst(/```([\s\S]*?)```/m, md) || '';
  return {
    success: true,
    settlement: {
      name,
      description: '',
      population,
      atmosphere,
      notable_feature,
      local_tavern,
      local_power,
      settlement_art
    }
  };
}

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
      const parsedSettlement = parseSettlementFromMarkdown(markdown);
      if (parsedSettlement) {
        await DataStore.setSettlement(lang, hexCode, parsedSettlement);
      }
    }
    processed++;
    if (onProgress && (processed % 50 === 0 || processed === total)) onProgress({ total, processed });
  }

  // Prefetch overlays (API-based, some are generated on-demand)
  try {
    const overlaysResp = await fetch('api/city-overlays');
    if (overlaysResp.ok) {
      const overlays = await overlaysResp.json();
      await DataStore.setOverlay(lang, '__index__', overlays);
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
