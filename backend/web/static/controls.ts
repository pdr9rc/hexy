// web/static/controls.ts
import { DyingLandsApp } from './main.js';
import * as api from './api.js';
import * as ui from './uiUtils.js';
import { setLanguage } from './translations.js';

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
          await api.resetContinent();
          await clearServiceWorkerCaches();
          window.location.replace('/?t=' + Date.now());
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
        window.location.replace('/?t=' + Date.now());
      } catch (e: any) {
        ui.hideLoading();
        ui.showNotification(e.message || 'Failed to change language', 'error');
      }
    });
  }
} 