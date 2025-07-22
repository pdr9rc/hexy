// web/static/mapRenderer.ts
import { DyingLandsApp, HexData } from './main.js';

export function renderMapGrid(app: DyingLandsApp) {
  const grid = document.getElementById('hexGrid');
  if (!grid) return;
  grid.innerHTML = '';
  // Render column headers
  const headerRow = document.createElement('div');
  headerRow.className = 'map-header-row';
  headerRow.innerHTML = '<span style="margin-right: 20px;"></span>' +
    Array.from({ length: app.mapWidth }, (_, x) =>
      `<span class="col-header" style="margin-right: 4px; font-size: 9px; display: inline-block; width: 1.5em; text-align: center;">${(x+1).toString().padStart(2, '0')}</span>`
    ).join('');
  grid.appendChild(headerRow);
  // Render map rows
  for (let y = 1; y <= app.mapHeight; y++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'map-row';
    const rowNum = document.createElement('span');
    rowNum.className = 'row-number';
    rowNum.textContent = y.toString().padStart(2, '0');
    rowDiv.appendChild(rowNum);
    for (let x = 1; x <= app.mapWidth; x++) {
      const hexCode = x.toString().padStart(2, '0') + y.toString().padStart(2, '0');
      const hex: HexData = app.mapData[hexCode];
      const span = document.createElement('span');
      span.className = 'hex-cell';
      span.setAttribute('data-hex', hexCode);
      span.tabIndex = 0;
      if (hex) {
        hex.css_class.split(' ').forEach(cls => {
          if (cls) span.classList.add(cls);
        });
        if (hex.is_city) span.classList.add('major-city');
        if (hex.content_type === 'settlement') span.classList.add('settlement');
        if (hex.has_content) span.classList.add('has-content');
        span.textContent = hex.symbol;
        span.title = hex.is_city ? `HEX ${hexCode} - ${hex.city_name}` : `HEX ${hexCode}`;
      } else {
        span.classList.add('terrain-unknown', 'no-content');
        span.textContent = '?';
        span.title = `HEX ${hexCode}`;
      }
      span.addEventListener('click', () => app.onHexClick(hexCode));
      rowDiv.appendChild(span);
    }
    grid.appendChild(rowDiv);
  }
} 