import * as api from './api.js';
import * as ui from './uiUtils.js';
export function setupControls(app) {
    // Lore button
    const loreBtn = document.getElementById('lore-btn');
    if (loreBtn) {
        loreBtn.addEventListener('click', async () => {
            ui.showLoading('Loading lore...');
            try {
                const data = await api.getLoreOverview();
                ui.hideLoading();
                ui.showLoreModal(data.lore);
            }
            catch (e) {
                ui.hideLoading();
                ui.showNotification(e.message || 'Failed to load lore', 'error');
            }
        });
    }
    // Reset button
    const resetBtn = document.getElementById('reset-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', async () => {
            if (!confirm('This will reset the entire continent and regenerate all content. This action cannot be undone. Continue?'))
                return;
            ui.showLoading('Resetting continent...');
            try {
                await api.resetContinent();
                ui.hideLoading();
                window.location.reload();
            }
            catch (e) {
                ui.hideLoading();
                ui.showNotification(e.message || 'Failed to reset continent', 'error');
            }
        });
    }
    // Language selector
    const langSel = document.getElementById('language-selector');
    if (langSel) {
        langSel.addEventListener('change', async () => {
            ui.showLoading('Changing language...');
            try {
                await api.setLanguage(langSel.value);
                ui.hideLoading();
                window.location.reload();
            }
            catch (e) {
                ui.hideLoading();
                ui.showNotification(e.message || 'Failed to change language', 'error');
            }
        });
    }
}
