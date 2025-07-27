// web/static/mapRenderer.ts
import { DyingLandsApp, HexData } from './main.js';

export { renderMapGrid as renderMap };

export function renderMapGrid(app: DyingLandsApp) {
  const grid = document.getElementById('hexGrid');
  if (!grid) return;
  grid.innerHTML = '';
  // Render map rows
  for (let y = 1; y <= app.mapHeight; y++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'hex-row';
    for (let x = 1; x <= app.mapWidth; x++) {
      const hexCode = x.toString().padStart(2, '0') + y.toString().padStart(2, '0');
      const hex: HexData = app.mapData[hexCode];
      
      // Create hex container for positioning
      const hexContainer = document.createElement('div');
      hexContainer.className = 'hex-container';
      hexContainer.setAttribute('data-hex', hexCode);
      
      const span = document.createElement('span');
      span.className = 'hex-cell';
      span.setAttribute('data-hex', hexCode);
      span.tabIndex = 0;
      
      if (hex) {
        hex.css_class.split(' ').forEach((cls: string) => {
          if (cls) span.classList.add(cls);
        });
        if (hex.is_city) span.classList.add('major-city');
        if (hex.content_type === 'settlement') span.classList.add('settlement');
        if (hex.has_content) span.classList.add('has-content');
        span.textContent = hex.symbol;
        span.title = hex.is_city ? `HEX ${hexCode} - ${hex.city_name}` : `HEX ${hexCode}`;
        
        // Add floating city name if it's a city
        if (hex.is_city && hex.city_name) {
          const cityName = document.createElement('div');
          cityName.className = 'city-name-label';
          cityName.textContent = hex.city_name;
          cityName.title = hex.city_name;
          hexContainer.appendChild(cityName);
        }
      } else {
        span.classList.add('terrain-unknown', 'no-content');
        span.textContent = '?';
        span.title = `HEX ${hexCode}`;
      }
      
      hexContainer.appendChild(span);
      rowDiv.appendChild(hexContainer);
    }
    grid.appendChild(rowDiv);
  }
} 