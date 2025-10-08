// web/static/controls.ts
import { DyingLandsApp } from './main.js';
import * as api from './api.js';
import * as ui from './uiUtils.js';
import { setLanguage } from './translations.js';
import { SandboxStore } from './utils/sandboxStore.js';
import { DataStore } from './utils/dataStore.js';
import { ensureJsZip } from './utils/jszipLoader.js';

export { setupControls as initializeControls };

async function clearServiceWorkerCaches(): Promise<void> {
  try {
    if ('serviceWorker' in navigator) {
      const regs = await navigator.serviceWorker.getRegistrations();
      await Promise.all(regs.map(r => r.unregister().catch(()=>{})));
    }
    const keys = await caches.keys();
    await Promise.all(keys.map(k => caches.delete(k)));
  } catch (_e) {}
}

export function setupControls(app: DyingLandsApp) {
  // Lore button
  const loreBtn = document.getElementById('lore-btn');
  if (loreBtn) {
    loreBtn.addEventListener('click', async () => {
      ui.showLoading('Loading lore...');
      try {
        const data = await api.getLoreOverview();
        ui.hideLoading();
        ui.showLoreModal(data.lore);
      } catch (e: any) {
        ui.hideLoading();
        ui.showNotification(e.message || 'Failed to load lore', 'error');
      }
    });
  }
  // Reset button
  const resetBtn = document.getElementById('reset-btn');
  if (resetBtn) {
    resetBtn.addEventListener('click', async () => {
      // Show overlay and bleed immediately
      ui.showLoading('');
      setTimeout(() => {
        const w: any = window as any;
        if (typeof w.startBleeding === 'function') w.startBleeding();
      }, 0);

      // Ask for confirmation without blocking
      ui.showResetConfirm(async () => {
        try {
          // Local-only reset: clear sandbox data and rotate sandbox id
          await SandboxStore.clearAll();
          await clearServiceWorkerCaches();
          const v = (window as any).__GEN_VERSION__ || Date.now();
          window.location.replace('?t=' + v);
        } catch (e: any) {
          ui.hideLoading();
          ui.showNotification(e.message || 'Failed to reset continent', 'error');
        }
      }, () => {
        // Cancel: reset bleeding and hide overlay
        ui.resetBleedingToTop();
        ui.hideLoading();
      });
    });
  }
  // Language selector
  const langSel = document.getElementById('language-selector') as HTMLSelectElement;
  if (langSel) {
    langSel.addEventListener('change', async () => {
      ui.showLoading('');
      try {
        const lang = langSel.value;
        await api.setLanguage(lang);
        setLanguage(lang);
        await clearServiceWorkerCaches();
        const v = (window as any).__GEN_VERSION__ || Date.now();
        window.location.replace('?t=' + v);
      } catch (e: any) {
        ui.hideLoading();
        ui.showNotification(e.message || 'Failed to change language', 'error');
      }
    });
  }
  // Export button
  const exportBtn = document.getElementById('export-btn');
  if (exportBtn) {
    exportBtn.addEventListener('click', async () => {
      try {
        // Fetch server zip
        const res = await fetch('api/export');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const zipBlob = await res.blob();

        // Try to obtain JSZip
        const JSZip = await ensureJsZip();
        if (JSZip) {
          const serverZip = await JSZip.loadAsync(zipBlob);
          // Dump client datastore
          const ds = await DataStore.dumpAll();
          const dsJson = JSON.stringify(ds);
          serverZip.file('client_datastore.json', dsJson);
          // Produce combined zip
          const combinedBlob = await serverZip.generateAsync({ type: 'blob' });
          const url = URL.createObjectURL(combinedBlob);
          const a = document.createElement('a');
          const ts = new Date().toISOString().replace(/[:.]/g, '');
          a.href = url;
          a.download = `dying_lands_bundle-${ts}.zip`;
          document.body.appendChild(a);
          a.click();
          a.remove();
          URL.revokeObjectURL(url);
          ui.showNotification('Exported world + client data');
        } else {
          // Fallback: download server zip directly
          const url = URL.createObjectURL(zipBlob);
          const a = document.createElement('a');
          const ts = new Date().toISOString().replace(/[:.]/g, '');
          a.href = url;
          a.download = `dying_lands_export-${ts}.zip`;
          document.body.appendChild(a);
          a.click();
          a.remove();
          URL.revokeObjectURL(url);
          ui.showNotification('Exported server world data');
        }
      } catch (e: any) {
        ui.showNotification(e.message || 'Failed to export', 'error');
      }
    });
  }

  // Import button + file input
  const importBtn = document.getElementById('import-btn');
  const importFile = document.getElementById('import-file') as HTMLInputElement | null;
  if (importBtn && importFile) {
    importBtn.addEventListener('click', () => importFile.click());
    importFile.addEventListener('change', async () => {
      const file = importFile.files && importFile.files[0];
      if (!file) return;
      if (!file.name.endsWith('.zip')) {
        ui.showNotification('Please select a .zip file', 'error');
        importFile.value = '';
        return;
      }
      ui.showLoading('Importing...');
      try {
        // Read zip locally to restore datastore if present
        const JSZip = (await import('jszip')).default;
        const zip = await JSZip.loadAsync(file);
        const dsEntry = zip.file('client_datastore.json');
        if (dsEntry) {
          const dsText = await dsEntry.async('string');
          try { await DataStore.restoreAll(JSON.parse(dsText)); } catch (_) {}
        }
        // Send to server import endpoint as well
        await api.importZip(file);
        ui.hideLoading();
        ui.showNotification('Import complete');
        await clearServiceWorkerCaches();
        const v = (window as any).__GEN_VERSION__ || Date.now();
        window.location.replace('/?t=' + v);
      } catch (e: any) {
        ui.hideLoading();
        ui.showNotification(e.message || 'Failed to import', 'error');
      } finally {
        importFile.value = '';
      }
    });
  }
} 