// web/static/uiUtils.ts

export function showLoading(msg: string = 'Loading...') {
  const el = document.getElementById('loading-indicator');
  if (el) {
    el.removeAttribute('hidden');
    const msgEl = document.getElementById('loading-message');
    if (msgEl) msgEl.textContent = msg;
  }
}

export function hideLoading() {
  const el = document.getElementById('loading-indicator');
  if (el) el.setAttribute('hidden', 'true');
}

export function showNotification(msg: string, type: 'info' | 'error' = 'info') {
  const el = document.getElementById('notification-container');
  if (!el) return;
  el.textContent = msg;
  el.style.display = 'block';
  el.style.color = type === 'error' ? 'var(--mork-magenta)' : 'var(--mork-yellow)';
  setTimeout(() => { el.style.display = 'none'; }, 3500);
}

export const showError = (msg: string) => showNotification(msg, 'error');

export function showLoreModal(lore: any) {
  const container = document.getElementById('details-panel');
  if (!container) return;
  
  let html = `
    <div class="city-hex-details-box">
      <div class="ascii-box">
        <div class="ascii-inner-box">
          <div class="ascii-section ascii-lore-title">
            <span>LORE OVERVIEW</span>
          </div>`;
  
  if (lore.major_cities) {
    html += `
          <div class="ascii-section ascii-lore-cities">
            <span>MAJOR CITIES</span>
            <pre>${(lore.major_cities as string[]).join('\n')}</pre>
          </div>`;
  }
  
  if (lore.factions) {
    html += `
          <div class="ascii-section ascii-lore-factions">
            <span>FACTIONS</span>
            <pre>${(lore.factions as string[]).join('\n')}</pre>
          </div>`;
  }
  
  if (lore.notable_npcs) {
    html += `
          <div class="ascii-section ascii-lore-npcs">
            <span>NOTABLE NPCS</span>
            <pre>${(lore.notable_npcs as string[]).join('\n')}</pre>
          </div>`;
  }
  
  if (lore.regional_lore) {
    html += `
          <div class="ascii-section ascii-lore-regions">
            <span>REGIONAL LORE</span>
            <pre>${(lore.regional_lore as string[]).join('\n')}</pre>
          </div>`;
  }
  
  html += `
        </div>
      </div>
    </div>`;
  
  container.innerHTML = html;
} 