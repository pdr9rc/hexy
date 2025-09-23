// web/static/controls.ts
import { DyingLandsApp } from './main.js';
import * as api from './api.js';
import * as ui from './uiUtils.js';
import { setLanguage } from './translations.js';
import { SandboxStore } from './utils/sandboxStore.js';

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
          window.location.replace('?t=' + Date.now());
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
                window.location.replace('?t=' + Date.now());
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
        // Export current sandbox markdown overrides as a JSON alongside server zip
        const res = await fetch('api/export');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        const ts = new Date().toISOString().replace(/[:.]/g, '');
        a.href = url;
        a.download = `dying_lands_output-${ts}.zip`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
        ui.showNotification('Exported world data');
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
        await api.importZip(file);
        // Keep sandbox overrides; do not clear IndexedDB
        ui.hideLoading();
        ui.showNotification('Import complete');
        await clearServiceWorkerCaches();
        window.location.replace('/?t=' + Date.now());
      } catch (e: any) {
        ui.hideLoading();
        ui.showNotification(e.message || 'Failed to import', 'error');
      } finally {
        importFile.value = '';
      }
    });
  }
} 