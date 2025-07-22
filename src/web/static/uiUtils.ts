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

export function showLoreModal(lore: any) {
  const container = document.getElementById('modalContainer');
  if (!container) return;
  let html = `<div class="ascii-modal"><pre>\n`;
  html += `╔══════════════════════════════════════════════════════════════╗\n`;
  html += `║                        LORE OVERVIEW                        ║\n`;
  html += `╠══════════════════════════════════════════════════════════════╣\n`;
  if (lore.major_cities) {
    html += `║ Major Cities:                                               ║\n`;
    (lore.major_cities as string[]).forEach(city => {
      (city.match(/.{1,58}/g) || [city]).forEach(line => {
        html += `║ ${line.padEnd(58)}║\n`;
      });
    });
    html += `╠══════════════════════════════════════════════════════════════╣\n`;
  }
  if (lore.factions) {
    html += `║ Factions:                                                   ║\n`;
    (lore.factions as string[]).forEach(faction => {
      (faction.match(/.{1,58}/g) || [faction]).forEach(line => {
        html += `║ ${line.padEnd(58)}║\n`;
      });
    });
    html += `╠══════════════════════════════════════════════════════════════╣\n`;
  }
  if (lore.notable_npcs) {
    html += `║ Notable NPCs:                                               ║\n`;
    (lore.notable_npcs as string[]).forEach(npc => {
      (npc.match(/.{1,58}/g) || [npc]).forEach(line => {
        html += `║ ${line.padEnd(58)}║\n`;
      });
    });
    html += `╠══════════════════════════════════════════════════════════════╣\n`;
  }
  if (lore.regional_lore) {
    html += `║ Regional Lore:                                              ║\n`;
    (lore.regional_lore as string[]).forEach(region => {
      (region.match(/.{1,58}/g) || [region]).forEach(line => {
        html += `║ ${line.padEnd(58)}║\n`;
      });
    });
    html += `╠══════════════════════════════════════════════════════════════╣\n`;
  }
  html += `║                                                              ║\n`;
  html += `╚══════════════════════════════════════════════════════════════╝\n`;
  html += `</pre></div>`;
  container.innerHTML = html;
} 