import { apiClient } from '@/api/client';
import { uiUtils } from '@/utils/uiUtils';

export class Controls {
  private loreBtn: HTMLButtonElement | null = null;
  private resetBtn: HTMLButtonElement | null = null;
  private langSelector: HTMLSelectElement | null = null;

  constructor() {
    this.initialize();
  }

  private initialize(): void {
    this.setupElements();
    this.setupEventListeners();
  }

  private setupElements(): void {
    this.loreBtn = document.getElementById('lore-btn') as HTMLButtonElement;
    this.resetBtn = document.getElementById('reset-btn') as HTMLButtonElement;
    this.langSelector = document.getElementById('language-selector') as HTMLSelectElement;
  }

  private setupEventListeners(): void {
    // Lore button
    if (this.loreBtn) {
      this.loreBtn.addEventListener('click', async () => {
        await this.handleLoreClick();
      });
    }

    // Reset button
    if (this.resetBtn) {
      this.resetBtn.addEventListener('click', async () => {
        await this.handleResetClick();
      });
    }

    // Language selector
    if (this.langSelector) {
      this.langSelector.addEventListener('change', async () => {
        await this.handleLanguageChange();
      });
    }
  }

  private async handleLoreClick(): Promise<void> {
    uiUtils.showLoading('Loading lore...');
    try {
      const response = await apiClient.getLoreOverview();
      uiUtils.hideLoading();
      
      if (response.success && response.data) {
        this.showLoreModal(response.data.lore);
      } else {
        uiUtils.showNotification('Failed to load lore', 'error');
      }
    } catch (error) {
      uiUtils.hideLoading();
      uiUtils.showNotification('Failed to load lore', 'error');
    }
  }

  private async handleResetClick(): Promise<void> {
    if (!confirm('This will reset the entire continent and regenerate all content. This action cannot be undone. Continue?')) {
      return;
    }

    uiUtils.showLoading('Resetting continent...');
    try {
      const response = await apiClient.resetContinent();
      uiUtils.hideLoading();
      
      if (response.success) {
        window.location.reload();
      } else {
        uiUtils.showNotification('Failed to reset continent', 'error');
      }
    } catch (error) {
      uiUtils.hideLoading();
      uiUtils.showNotification('Failed to reset continent', 'error');
    }
  }

  private async handleLanguageChange(): Promise<void> {
    if (!this.langSelector) return;

    uiUtils.showLoading('Changing language...');
    try {
      const response = await apiClient.setLanguage(this.langSelector.value);
      uiUtils.hideLoading();
      
      if (response.success) {
        window.location.reload();
      } else {
        uiUtils.showNotification('Failed to change language', 'error');
      }
    } catch (error) {
      uiUtils.hideLoading();
      uiUtils.showNotification('Failed to change language', 'error');
    }
  }

  private showLoreModal(lore: any): void {
    const container = document.getElementById('hex-content');
    if (!container) return;
    
    let html = `
      <div class="lore-modal">
        <div class="lore-header">
          <h2>LORE OVERVIEW</h2>
        </div>
        <div class="lore-content">
    `;
    
    if (lore.major_cities) {
      html += `
        <div class="lore-section">
          <h3>MAJOR CITIES</h3>
          <ul>
            ${(lore.major_cities as string[]).map(city => `<li>${city}</li>`).join('')}
          </ul>
        </div>
      `;
    }
    
    if (lore.factions) {
      html += `
        <div class="lore-section">
          <h3>FACTIONS</h3>
          <ul>
            ${(lore.factions as string[]).map(faction => `<li>${faction}</li>`).join('')}
          </ul>
        </div>
      `;
    }
    
    if (lore.notable_npcs) {
      html += `
        <div class="lore-section">
          <h3>NOTABLE NPCS</h3>
          <ul>
            ${(lore.notable_npcs as string[]).map(npc => `<li>${npc}</li>`).join('')}
          </ul>
        </div>
      `;
    }
    
    if (lore.regional_lore) {
      html += `
        <div class="lore-section">
          <h3>REGIONAL LORE</h3>
          <ul>
            ${(lore.regional_lore as string[]).map(loreItem => `<li>${loreItem}</li>`).join('')}
          </ul>
        </div>
      `;
    }
    
    html += `
        </div>
      </div>
    `;
    
    container.innerHTML = html;
  }

  public setLanguage(language: string): void {
    if (this.langSelector) {
      this.langSelector.value = language;
    }
  }

  public getCurrentLanguage(): string {
    return this.langSelector?.value || 'en';
  }

  public enableControls(): void {
    if (this.loreBtn) this.loreBtn.disabled = false;
    if (this.resetBtn) this.resetBtn.disabled = false;
    if (this.langSelector) this.langSelector.disabled = false;
  }

  public disableControls(): void {
    if (this.loreBtn) this.loreBtn.disabled = true;
    if (this.resetBtn) this.resetBtn.disabled = true;
    if (this.langSelector) this.langSelector.disabled = true;
  }
} 