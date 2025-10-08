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

function matchFirst(text: string, patterns: RegExp[]): string | null {
  for (const rx of patterns) {
    const m = text.match(rx);
    if (m) return (m[1] || '').trim();
  }
  return null;
}

function section(text: string, header: string): string | null {
  const rx = new RegExp(`##\\s*${header}\\s*\n([\\s\\S]*?)(?:\n##|$)`, 'i');
  const m = text.match(rx);
  return m ? m[1].trim() : null;
}

function parseSettlementFromMarkdown(md: string): any | null {
  const isSettlement = /⌂\s*\*\*|##\s*Settlement/i.test(md) || /\*\*Population:\*\*/i.test(md);
  if (!isSettlement) return null;

  const name = matchFirst(md, [/⌂\s*\*\*([^*]+)\*\*/i, /\*\*Name:\*\*\s*([^\n]+)/i]) || 'Settlement';
  const population = matchFirst(md, [/\*\*Population:\*\*\s*([^\n]+)/i]) || '';
  const atmosphere = matchFirst(md, [/\*\*Atmosphere:\*\*\s*([^\n]+)/i, /##\s*Atmosphere\s*\n([^\n]+)/i]) || '';
  const notable_feature = matchFirst(md, [/\*\*Notable Feature:\*\*\s*([^\n]+)/i, /##\s*Notable Feature\s*\n([^\n]+)/i]) || '';
  const local_tavern = matchFirst(md, [/\*\*Select Menu:\*\*\s*([^\n]+)/i]) || '';
  const local_power = matchFirst(md, [/\*\*Local Power:\*\*\s*([^\n]+)/i]) || '';
  const weather = matchFirst(md, [/\*\*Weather:\*\*\s*([^\n]+)/i]) || '';
  const city_event = matchFirst(md, [/\*\*City Event:\*\*\s*([^\n]+)/i]) || '';

  const tavern_details: any = {};
  const select_dish = matchFirst(md, [/\*\*Select Menu:\*\*\s*([^\n]+)/i]);
  const budget_dish = matchFirst(md, [/\*\*Budget Menu:\*\*\s*([^\n]+)/i]);
  const innkeeper_quirk = matchFirst(md, [/\*\*Innkeeper:\*\*\s*([^\n]+)/i]);
  const patron_trait = matchFirst(md, [/\*\*Notable Patron:\*\*\s*([^\n]+)/i]);
  if (select_dish) tavern_details.select_dish = select_dish;
  if (budget_dish) tavern_details.budget_dish = budget_dish;
  if (innkeeper_quirk) tavern_details.innkeeper_quirk = innkeeper_quirk;
  if (patron_trait) tavern_details.patron_trait = patron_trait;

  const settlement_art = (() => {
    const sec = section(md, 'Settlement') || section(md, 'Denizen') || md;
    const m = sec.match(/```([\s\S]*?)```/m);
    return m ? m[0] : '';
  })();

  const loot = (() => {
    const sec = section(md, 'Loot Found');
    if (!sec) return null;
    // Collect key-value pairs if present, else return as text
    const pairs: Record<string, string> = {};
    const lines = sec.split(/\n+/);
    let anyPair = false;
    for (const line of lines) {
      const pm = line.match(/\*\*([^:]+):\*\*\s*(.+)/);
      if (pm) { pairs[pm[1].trim()] = pm[2].trim(); anyPair = true; }
    }
    if (anyPair) return pairs;
    return sec.trim();
  })();

  const description = (() => {
    const den = section(md, 'Denizen');
    if (den) return den.split(/\n+/).slice(0, 3).join('\n');
    const enc = section(md, 'Encounter');
    if (enc) return enc.split(/\n+/).slice(0, 3).join('\n');
    return '';
  })();

  return {
    success: true,
    settlement: {
      name,
      description,
      population,
      atmosphere,
      notable_feature,
      local_tavern,
      local_power,
      settlement_art,
      weather,
      city_event,
      tavern_details,
      loot
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
