export const uiUtils = {
  showLoading(msg: string = 'Loading...'): void {
    const el = document.getElementById('loading-indicator');
    if (el) {
      el.removeAttribute('hidden');
      const msgEl = document.getElementById('loading-message');
      if (msgEl) msgEl.textContent = msg;
    }
  },

  hideLoading(): void {
    const el = document.getElementById('loading-indicator');
    if (el) el.setAttribute('hidden', 'true');
  },

  showNotification(msg: string, type: 'info' | 'error' | 'success' = 'info'): void {
    const el = document.getElementById('notification-container');
    if (!el) return;
    
    el.textContent = msg;
    el.style.display = 'block';
    
    // Set color based on type
    switch (type) {
      case 'error':
        el.style.color = '#ff4444';
        break;
      case 'success':
        el.style.color = '#44ff44';
        break;
      default:
        el.style.color = '#ffff44';
    }
    
    // Auto-hide after 3.5 seconds
    setTimeout(() => {
      el.style.display = 'none';
    }, 3500);
  },

  showError(msg: string): void {
    this.showNotification(msg, 'error');
  },

  showSuccess(msg: string): void {
    this.showNotification(msg, 'success');
  },

  showLoreModal(lore: any): void {
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
  },

  createLoadingIndicator(): void {
    // Create loading indicator if it doesn't exist
    if (!document.getElementById('loading-indicator')) {
      const loadingDiv = document.createElement('div');
      loadingDiv.id = 'loading-indicator';
      loadingDiv.className = 'loading-indicator';
      loadingDiv.setAttribute('hidden', 'true');
      loadingDiv.innerHTML = `
        <div class="loading-spinner"></div>
        <div id="loading-message">Loading...</div>
      `;
      document.body.appendChild(loadingDiv);
    }

    // Create notification container if it doesn't exist
    if (!document.getElementById('notification-container')) {
      const notificationDiv = document.createElement('div');
      notificationDiv.id = 'notification-container';
      notificationDiv.className = 'notification-container';
      notificationDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #333;
        color: #fff;
        padding: 1rem;
        border-radius: 4px;
        z-index: 10000;
        display: none;
        max-width: 300px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
      `;
      document.body.appendChild(notificationDiv);
    }
  }
}; 