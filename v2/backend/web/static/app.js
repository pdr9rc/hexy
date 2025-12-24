import { createGridRenderer } from './grid.js';
import { createUIBox } from './uiBox.js';
import { createHeaderControls } from './header.js';
import * as city from './city.js';
import * as cache from './cache.js';

const BG = "#feea00";
const PINK = "#FF3EB5";
const BLACK = "#000000";
const DEFAULT_LANGUAGE = "en";
const BLUE = '#2daefd';

/**
 * Generate a shaded version of a color by adding black
 * @param {string} hexColor - Hex color string (e.g., "#FF3EB5")
 * @param {number} shadeAmount - Amount of black to add (0-1, where 0 = no shade, 1 = pure black)
 * @returns {string} - Shaded hex color
 */
function shadeColor(hexColor, shadeAmount) {
  // Remove # if present
  hexColor = hexColor.replace('#', '');
  
  // Parse RGB values
  const r = parseInt(hexColor.substring(0, 2), 16);
  const g = parseInt(hexColor.substring(2, 4), 16);
  const b = parseInt(hexColor.substring(4, 6), 16);
  
  // Add black (multiply by (1 - shadeAmount))
  const shadedR = Math.round(r * (1 - shadeAmount));
  const shadedG = Math.round(g * (1 - shadeAmount));
  const shadedB = Math.round(b * (1 - shadeAmount));
  
  // Convert back to hex
  return `#${shadedR.toString(16).padStart(2, '0')}${shadedG.toString(16).padStart(2, '0')}${shadedB.toString(16).padStart(2, '0')}`;
}

/**
 * Generate district color map with unique pink shades for each district
 * @param {Array} districts - Array of district names
 * @returns {Object} - Map of district name -> shaded pink color
 */
function generateDistrictColors(districts) {
  const districtColors = {};
  const uniqueDistricts = [...new Set(districts.filter(d => d))]; // Remove empty and duplicates
  
  // Generate shades from lightest to darkest
  // Use a wider range from 0.05 (lightest) to 0.85 (darkest) for more distinction
  const minShade = 0.05;
  const maxShade = 0.85;
  
  uniqueDistricts.forEach((districtName, index) => {
    // Use a more aggressive distribution curve for better distinction
    // Apply a slight curve to push shades further apart
    const normalizedIndex = index / Math.max(1, uniqueDistricts.length - 1);
    // Use a power curve to spread out the shades more
    const curvedIndex = Math.pow(normalizedIndex, 0.7); // 0.7 gives a slight curve
    const shadeAmount = minShade + curvedIndex * (maxShade - minShade);
    districtColors[districtName] = shadeColor(PINK, shadeAmount);
  });
  
  return districtColors;
}

/**
 * Persist district colors to localStorage
 */
function persistDistrictColors(cityData, districtColors) {
  const cityName = cityData?.city_name || cityData?.display_name || 'unknown';
  const lang = appState.lang || 'en';
  cache.cacheDistrictColors(cityName, districtColors, lang);
}

/**
 * Load district colors from localStorage using unified cache
 */
function loadDistrictColors(cityName, language) {
  return cache.getCachedDistrictColors(cityName, language);
}

const WORLD_TERRAIN_MAP = {
  plains:        { glyph: "..", label: "PLAINS",        color: PINK, fill: BG, hover_fill: PINK, symbol_color: BLACK, hovered_symbol_color: BG },
  forest:        { glyph: "↟↟", label: "FOREST",        color: PINK, fill: BG, hover_fill: PINK, symbol_color: BLACK, hovered_symbol_color: BG },
  mountain:      { glyph: "▲▲", label: "MOUNTAIN",      color: PINK, fill: BG, hover_fill: PINK, symbol_color: BLACK, hovered_symbol_color: BG },
  bridge:        { glyph: "╲ ╲", label: "BRIDGE",        color: PINK, fill: BG, hover_fill: PINK, symbol_color: BLACK, hovered_symbol_color: BG },
  coast:         { glyph: "≈",  label: "COAST",         color: PINK, fill: PINK, hover_fill: BG, symbol_color: BLACK, hovered_symbol_color: PINK },
  swamp:         { glyph: "⁖⁖", label: "SWAMP",         color: PINK, fill: BG, hover_fill: PINK, symbol_color: BLACK, hovered_symbol_color: BG },
  desert:        { glyph: "∴∴", label: "DESERT",         color: PINK, fill: BG, hover_fill: PINK, symbol_color: BLACK, hovered_symbol_color: BG },
  snow:          { glyph: "  ", label: "SNOW",         color: PINK, fill: BG, hover_fill: PINK, symbol_color: BG, hovered_symbol_color: PINK },
  river:         { glyph: " ~ ", label: "RIVER",         color: PINK, fill: PINK, hover_fill: BG, symbol_color: BG, hovered_symbol_color: PINK },
  hills:         { glyph: "^^", label: "HILLS",          color: PINK, fill: BG, hover_fill: PINK, symbol_color: BG, hovered_symbol_color: BG },
  city:          { glyph: "🜲", label: "CITY",            color: PINK, fill: BG, hover_fill: PINK, symbol_color: PINK, hovered_symbol_color: BG },
  settlement:    { glyph: "⛫", label: "SETTLEMENT",      color: PINK, fill: BG, hover_fill: PINK, symbol_color: PINK, hovered_symbol_color: BG },
  dungeon:       { glyph: "🜄", label: "DUNGEON",         color: PINK, fill: BG, hover_fill: PINK, symbol_color: BLACK, hovered_symbol_color: BG },
  beast:         { glyph: "🜹", label: "BEAST",           color: PINK, fill: BG, hover_fill: PINK, symbol_color: PINK, hovered_symbol_color: BG },
  npc:           { glyph: "🜏", label: "NPC",             color: PINK, fill: BG, hover_fill: PINK, symbol_color: PINK, hovered_symbol_color: BG },
  sea:           { glyph: "~~", label: "SEA",           color: PINK, fill: PINK, hover_fill: BG, symbol_color: BG, hovered_symbol_color: PINK },
  deep_sea:      { glyph: "~~", label: "DEEP SEA",       color: PINK, fill: PINK, hover_fill: BG, symbol_color: BG, hovered_symbol_color: PINK },
  sea_encounter: { glyph: "≋",  label: "SEA ENCOUNTER",  color: PINK, fill: PINK, hover_fill: BG, symbol_color: PINK, hovered_symbol_color: BG },
};

const CITY_TERRAIN_MAP = {
  district:  { glyph: "🝔", label: "DISTRICT",  color: PINK, fill: PINK, hover_fill: BG, symbol_color: BG, hovered_symbol_color: BLACK },
  building:  { glyph: "🜨", label: "BUILDING",  color: PINK, fill: PINK, hover_fill: BG, symbol_color: BG, hovered_symbol_color: BLACK },
  street:    { glyph: "═", label: "STREET",    color: PINK, fill: PINK, hover_fill: BG, symbol_color: BG, hovered_symbol_color: BLACK },
  landmark:  { glyph: "🜳", label: "LANDMARK",  color: PINK, fill: PINK, hover_fill: BG, symbol_color: BG, hovered_symbol_color: BLACK },
  market:    { glyph: "⯚", label: "MARKET",    color: PINK, fill: PINK, hover_fill: BG, symbol_color: BG, hovered_symbol_color: BLACK },
  temple:    { glyph: "🜏", label: "TEMPLE",    color: PINK, fill: PINK, hover_fill: BG, symbol_color: BG, hovered_symbol_color: BLACK },
  tavern:    { glyph: "🜟", label: "TAVERN",    color: PINK, fill: PINK, hover_fill: BG, symbol_color: BG, hovered_symbol_color: BLACK },
  guild:     { glyph: "🜌", label: "GUILD",     color: PINK, fill: PINK, hover_fill: BG, symbol_color: BG, hovered_symbol_color: BLACK },
  residence: { glyph: "🝪", label: "RESIDENCE", color: PINK, fill: PINK, hover_fill: BG, symbol_color: BG, hovered_symbol_color: BLACK },
  ruins:     { glyph: "🝏", label: "RUINS",     color: PINK, fill: PINK, hover_fill:  BG, symbol_color: BG, hovered_symbol_color: BLACK },
  empty:     { glyph: " ", label: "EMPTY",     color: PINK, fill: BLACK, hover_fill: BLACK, symbol_color: BG, hovered_symbol_color: BLACK },
};

const GRID_CFG = {
  hexSize: 30,
  zoom: 1.2,
  tilt: 0.55,
  rot: -45,
  gridAlpha: 1,
  minZoom: 1.0,
  maxZoom: 1.5,
};

// Load persisted language preference
function loadPersistedLanguage() {
  try {
    const stored = localStorage.getItem('hexy_language');
    if (stored) {
      return stored;
    }
  } catch (e) {
    console.warn('Failed to load persisted language:', e);
  }
  return DEFAULT_LANGUAGE;
}

// Persist language preference
function persistLanguage(lang) {
  try {
    localStorage.setItem('hexy_language', lang);
  } catch (e) {
    console.warn('Failed to persist language:', e);
  }
}

const appState = {
  mode: "world",
  overlayName: null,
  lang: loadPersistedLanguage(),
  worldGrid: null,
  cityGrid: null,
  uiBox: null,
  header: null,
  cityOverviewMarkdown: null,
  currentHexId: null,
  currentHexContent: null,
  districtColors: {}, // Map of district name -> shaded pink color
  editingWorldHex: false, // Track if we're editing a world hex
  editingHexCode: null, // Hex code being edited
  currentWorldHexCode: null, // Current world hex code being displayed
};

function parseWorldMapData(data) {
  const lines = (data.ascii || "").split("\n").map((l) => l.trimEnd());
  const dataLines = lines.filter((l) => /^\d{1,2}\s/.test(l));
  if (!dataLines.length) return null;
  const grid = [];
  const roadHexes = new Set(data.road_hexes || []);
  for (let row = 0; row < dataLines.length; row++) {
    const line = dataLines[row];
    const parts = line.split(" ").filter(Boolean);
    if (parts.length <= 1) continue;
    const rowNum = parseInt(parts[0], 10);
    parts.shift();
    const rowData = [];
    for (let col = 0; col < parts.length; col++) {
      const hexCode = `${String(col + 1).padStart(2, "0")}${String(rowNum).padStart(2, "0")}`;
      const terrainMap = data.terrain_map || {};
      const terrain = terrainMap[hexCode] || "plains";
      const has_road = roadHexes.has(hexCode);
      rowData.push({ terrain, code: hexCode, has_road });
    }
    grid.push(rowData);
  }
  const rows = grid.length;
  const cols = grid[0]?.length || 0;
  const parsedData = { grid, rows, cols, terrain_map: data.terrain_map, road_hexes: data.road_hexes, ascii: data.ascii };
  
  // Cache the parsed map data
  const lang = data.language || appState.lang;
  cache.cacheWorldMapData(parsedData, lang);
  
  return parsedData;
}

function parseCityOverlayData(data) {
  // Handle new API response structure: {success: true, city_data: {...}, district_matrix: [...]}
  // District matrix is static, we generate grid from it
  const cityData = data.city_data || data.overlay?.city_data;
  const districtMatrix = data.district_matrix || data.overlay?.district_matrix;
  
  if (!cityData || !districtMatrix) return null;
  
  const rows = districtMatrix.length;
  const cols = districtMatrix[0]?.length || 0;
  
  if (rows === 0 || cols === 0) return null;
  
  // Collect all unique district names
  const allDistricts = [];
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const districtName = districtMatrix[row]?.[col] || "";
      if (districtName && !allDistricts.includes(districtName)) {
        allDistricts.push(districtName);
      }
    }
  }
  
  // Try to load district colors from localStorage, otherwise generate
  const cityName = cityData?.city_name || cityData?.display_name || 'unknown';
  const lang = data.language || appState.lang || 'en';
  let districtColors = loadDistrictColors(cityName, lang);
  
  // If no cached colors or district list changed, regenerate
  if (!districtColors || !allDistricts.every(d => districtColors[d])) {
    districtColors = generateDistrictColors(allDistricts);
    // Store district colors in appState and localStorage for persistence
    appState.districtColors = districtColors;
    persistDistrictColors(cityData, districtColors);
  } else {
    // Use cached colors
    appState.districtColors = districtColors;
  }
  
  // Check if we have cached hex content, otherwise generate
  const encounterTables = data.encounter_tables || {};
  let allHexContent = {};
  
  // Count total hexes that need content
  let totalHexes = 0;
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const districtName = districtMatrix[row]?.[col] || "";
      if (districtName) {
        totalHexes++;
      }
    }
  }
  
  // Try to get cached content for each hex
  const cachedHexIds = [];
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const hexId = `${row}_${col}`;
      const districtName = districtMatrix[row]?.[col] || "";
      if (districtName) {
        const cached = city.getHexContent(hexId);
        if (cached) {
          allHexContent[hexId] = cached;
          cachedHexIds.push(hexId);
        }
      }
    }
  }
  
  // Generate content only for hexes that don't have cached content
  // NEVER regenerate encounters for cached hexes
  if (cachedHexIds.length < totalHexes) {
    // Only generate for hexes that don't have cached content
    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        const hexId = `${row}_${col}`;
        const districtName = districtMatrix[row]?.[col] || "";
        if (districtName && !allHexContent[hexId]) {
          // Only generate if not cached
          const generatedContent = city.generateHexContent(
            hexId,
            cityData,
            encounterTables
          );
          allHexContent[hexId] = generatedContent;
        }
      }
    }
  }
  
  // Store only newly generated content in cache (don't overwrite existing cached content)
  // This preserves encounters that were already cached
  Object.keys(allHexContent).forEach(hexId => {
    // Only cache if it wasn't already cached (to preserve existing encounters)
    if (!cachedHexIds.includes(hexId)) {
      city.setHexContent(hexId, allHexContent[hexId]);
    }
  });
  
  const grid = [];
  
  for (let row = 0; row < rows; row++) {
    const rowData = [];
    for (let col = 0; col < cols; col++) {
      const hexId = `${row}_${col}`;
      const districtName = districtMatrix[row]?.[col] || "";
      
      if (!districtName) {
        // Empty hex
        rowData.push({ terrain: "empty", hexId, code: hexId, district: "" });
      } else {
        // Get generated content for this hex
        const hexContent = allHexContent[hexId];
        // Use content type as terrain for glyph display
        const terrain = hexContent?.type || "district";
        // Get district-specific color
        const districtColor = districtColors[districtName] || PINK;
        rowData.push({ 
          terrain, 
          hexId, 
          code: hexId, 
          district: districtName,
          districtColor: districtColor, // Store district color
          content: hexContent // Store content with grid cell
        });
      }
    }
    grid.push(rowData);
  }
  
  return { grid, rows, cols };
}

async function fetchWorldHex(code) {
  // Exit edit mode if we're clicking a different hex
  if (appState.editingWorldHex && appState.editingHexCode !== code) {
    // Save current edit if any
    saveWorldHexEdit();
  }
  
  // Store current hex code
  appState.currentWorldHexCode = code;
  
  // Check cache first (this includes edited content)
  const cached = cache.getCachedWorldHex(code, appState.lang);
  if (cached && cached.raw_markdown) {
    appState.uiBox.renderStyled(cached.raw_markdown);
    appState.uiBox.renderRaw(cached.raw_markdown);
    // Hide save button if not editing
    if (!appState.editingWorldHex) {
      document.getElementById("btn-save-world-hex")?.classList.remove("visible");
    }
    // Setup double-click handler on card content for edit mode
    setupWorldHexCardDoubleClick();
    return;
  }
  
  // If not cached, fetch from API
  const attempts = [
    `/api/city/${code}?language=${appState.lang}`,
    `/api/settlement/${code}?language=${appState.lang}`,
    `/api/hex/${code}?language=${appState.lang}`,
  ];
  for (const url of attempts) {
    try {
      const res = await fetch(url);
      if (!res.ok) continue;
      const data = await res.json();
      const md = data.raw_markdown || "";
      
      // Cache the result
      cache.cacheWorldHex(code, data, appState.lang);
      
      appState.uiBox.renderStyled(md);
      appState.uiBox.renderRaw(md);
      // Setup double-click handler on card content for edit mode
      setupWorldHexCardDoubleClick();
      return;
    } catch {
      /* ignore */
    }
  }
  appState.uiBox.renderStyled(`# Hex ${code}\n\nNot found.`);
  appState.uiBox.renderRaw("Not found.");
}

function renderHexContent(generatedContent, hexId, districtName) {
  // Build markdown from generated content
  let md = `# ${generatedContent.name || hexId}\n\n`;
  md += `**Type:** ${generatedContent.type || 'unknown'}\n\n`;
  if (generatedContent.description) md += `**Description:** ${generatedContent.description}\n\n`;
  if (generatedContent.encounter) md += `**Encounter:** ${generatedContent.encounter}\n\n`;
  if (generatedContent.atmosphere) md += `**Atmosphere:** ${generatedContent.atmosphere}\n\n`;
  
  if (districtName) {
    md += `**District:** ${districtName}\n\n`;
  }
  
  // Add additional fields based on content type
  if (generatedContent.random_table && Array.isArray(generatedContent.random_table)) {
    md += `**Random Table:**\n`;
    generatedContent.random_table.forEach(entry => {
      md += `- ${entry}\n`;
    });
    md += `\n`;
  }
  
  if (generatedContent.notable_features && Array.isArray(generatedContent.notable_features)) {
    md += `**Notable Features:**\n`;
    generatedContent.notable_features.forEach(feature => {
      md += `- ${feature}\n`;
    });
    md += `\n`;
  }
  
  if (generatedContent.market_specialty) {
    md += `**Market Specialty:** ${generatedContent.market_specialty}\n\n`;
  }
  
  if (generatedContent.items_sold && Array.isArray(generatedContent.items_sold)) {
    md += `**Items Sold:** ${generatedContent.items_sold.join(', ')}\n\n`;
  }
  
  if (generatedContent.services && Array.isArray(generatedContent.services)) {
    md += `**Services:** ${generatedContent.services.join(', ')}\n\n`;
  }
  
  if (generatedContent.temple_deity) {
    md += `**Temple Deity:** ${generatedContent.temple_deity}\n\n`;
  }
  
  if (generatedContent.rituals && Array.isArray(generatedContent.rituals)) {
    md += `**Rituals:** ${generatedContent.rituals.join(', ')}\n\n`;
  }
  
  if (generatedContent.tavern_menu) {
    md += `**Tavern Menu:** ${generatedContent.tavern_menu}\n\n`;
  }
  
  if (generatedContent.tavern_innkeeper) {
    md += `**Innkeeper:** ${generatedContent.tavern_innkeeper}\n\n`;
  }
  
  if (generatedContent.tavern_patron) {
    md += `**Patrons:** ${generatedContent.tavern_patron}\n\n`;
  }
  
  if (generatedContent.guild_purpose) {
    md += `**Guild Purpose:** ${generatedContent.guild_purpose}\n\n`;
  }
  
  if (generatedContent.residence_inhabitants) {
    md += `**Inhabitants:** ${generatedContent.residence_inhabitants}\n\n`;
  }
  
  if (generatedContent.threats && Array.isArray(generatedContent.threats)) {
    md += `**Threats:** ${generatedContent.threats.join(', ')}\n\n`;
  }
  
  // Add regeneration controls
  md += `---\n\n`;
  md += `**Actions:**\n`;
  
  appState.uiBox.renderStyled(md);
  appState.uiBox.renderRaw(md);
  
  // Add action buttons after markdown is rendered
  addActionButtons(hexId, districtName);
}

function addActionButtons(hexId, districtName) {
  const cardContent = document.getElementById("card-content");
  if (!cardContent) return;
  
  // Remove any existing action buttons
  const existingActions = cardContent.querySelector('.hex-actions');
  if (existingActions) {
    existingActions.remove();
  }
  
  // Find the Actions section and add buttons after it
  const actionsSection = Array.from(cardContent.querySelectorAll('.md-p')).find(p => 
    p.textContent.includes('Actions:')
  );
  
  if (!actionsSection) return;
  
  // Create button container
  const buttonContainer = document.createElement('div');
  buttonContainer.className = 'hex-actions';
  
  // Regenerate Encounter button
  const regenerateBtn = document.createElement('button');
  regenerateBtn.className = 'hex-action-btn';
  regenerateBtn.textContent = 'Regenerate Encounter';
  regenerateBtn.addEventListener('click', () => {
    regenerateHexEncounter(hexId, districtName);
  });
  buttonContainer.appendChild(regenerateBtn);
  
  // Location selector dropdown (if district has locations)
  const cached = city.getCachedCityData();
  if (cached && districtName) {
    const districtData = city.getDistrictData(districtName, cached.cityData);
    if (districtData) {
      const locations = getDistrictLocations(districtData);
      if (locations.length > 0) {
        const locationContainer = document.createElement('div');
        locationContainer.style.display = 'flex';
        locationContainer.style.gap = '8px';
        locationContainer.style.alignItems = 'center';
        
        const locationLabel = document.createElement('label');
        locationLabel.textContent = 'Select Location:';
        locationLabel.style.marginRight = '8px';
        locationLabel.style.fontWeight = 'bold';
        locationLabel.style.fontSize = '12px';
        
        const locationSelect = document.createElement('select');
        locationSelect.className = 'hex-location-select';
        locationSelect.style.flex = '1';
        
        // Add empty option
        const emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = '-- Select a location --';
        locationSelect.appendChild(emptyOption);
        
        // Add location options
        locations.forEach(location => {
          const option = document.createElement('option');
          option.value = location.name;
          option.textContent = `${location.name} (${location.type})`;
          locationSelect.appendChild(option);
        });
        
        locationSelect.addEventListener('change', (e) => {
          if (e.target.value) {
            const selected = locations.find(l => l.name === e.target.value);
            if (selected) {
              const cached = city.getCachedCityData();
              const generatedContent = city.generateHexContent(
                hexId,
                cached.cityData,
                cached.encounterTables,
                { locationName: selected.name }
              );
              
              // Update cache
              city.setHexContent(hexId, generatedContent);
              appState.currentHexContent = generatedContent;
              
              // Update grid cell content and terrain (for glyph)
              if (appState.cityGrid) {
                const gridState = appState.cityGrid.getState();
                const parts = hexId.split('_');
                const row = parseInt(parts[0], 10);
                const col = parseInt(parts[1], 10);
                if (gridState.grid[row] && gridState.grid[row][col]) {
                  gridState.grid[row][col].content = generatedContent;
                  gridState.grid[row][col].terrain = generatedContent.type || "district";
                  // Preserve district color
                  if (!gridState.grid[row][col].districtColor && districtName && appState.districtColors[districtName]) {
                    gridState.grid[row][col].districtColor = appState.districtColors[districtName];
                  }
                  // Update state and redraw to show updated glyph
                  appState.cityGrid.setState({ grid: gridState.grid });
                }
              }
              
              renderHexContent(generatedContent, hexId, districtName);
            }
          }
        });
        
        locationContainer.appendChild(locationLabel);
        locationContainer.appendChild(locationSelect);
        buttonContainer.appendChild(locationContainer);
      }
    }
  }
  
  // Insert buttons after the Actions section
  actionsSection.parentNode.insertBefore(buttonContainer, actionsSection.nextSibling);
}

function getDistrictLocations(districtData) {
  const locations = [];
  const locationTypes = [
    { key: 'buildings', label: 'Building' },
    { key: 'streets', label: 'Street' },
    { key: 'landmarks', label: 'Landmark' },
    { key: 'markets', label: 'Market' },
    { key: 'temples', label: 'Temple' },
    { key: 'taverns', label: 'Tavern' },
    { key: 'guilds', label: 'Guild' },
    { key: 'residences', label: 'Residence' },
    { key: 'ruins', label: 'Ruin' }
  ];
  
  locationTypes.forEach(({ key, label }) => {
    const arr = districtData[key];
    if (Array.isArray(arr) && arr.length > 0) {
      arr.forEach(item => {
        const itemName = typeof item === 'string' ? item : (item.name || String(item));
        locations.push({ name: itemName, type: label });
      });
    }
  });
  
  return locations;
}

function regenerateHexEncounter(hexId, districtName) {
  const cached = city.getCachedCityData();
  if (!cached || !appState.currentHexContent) {
    return;
  }
  
  // Get district data
  const districtData = districtName ? city.getDistrictData(districtName, cached.cityData) : null;
  
  // Regenerate encounter
  const updatedContent = city.regenerateEncounter(
    appState.currentHexContent,
    districtData,
    cached.encounterTables
  );
  
  // Update stored content in cache
  city.setHexContent(hexId, updatedContent);
  appState.currentHexContent = updatedContent;
  
  // Update grid cell content and redraw
  if (appState.cityGrid) {
    const gridState = appState.cityGrid.getState();
    const parts = hexId.split('_');
    const row = parseInt(parts[0], 10);
    const col = parseInt(parts[1], 10);
    if (gridState.grid[row] && gridState.grid[row][col]) {
      gridState.grid[row][col].content = updatedContent;
      // Update state and redraw
      appState.cityGrid.setState({ grid: gridState.grid });
    }
  }
  
  // Re-render
  renderHexContent(updatedContent, hexId, districtName);
}

// showLocationSelector removed - now handled by dropdown in addActionButtons

async function fetchCityHex(overlayName, hexId) {
  try {
    // Get cached city data
    const cached = city.getCachedCityData();
    if (!cached) {
      // If no cached data, try to load overlay first
      appState.uiBox.renderStyled(`# City Hex ${hexId}\n\nCity data not loaded.`);
      appState.uiBox.renderRaw("City data not loaded.");
      return;
    }
    
    // Check for cached hex content first
    let hexContent = city.getHexContent(hexId);
    
    // If no cached content, generate it
    if (!hexContent) {
      hexContent = city.generateHexContent(
        hexId,
        cached.cityData,
        cached.encounterTables
      );
      // Cache the newly generated content
      city.setHexContent(hexId, hexContent);
    }
    
    // Store current hex state
    appState.currentHexId = hexId;
    appState.currentHexContent = hexContent;
    
    // Get district name
    const parts = hexId.split('_');
    let districtName = '';
    if (parts.length === 2) {
      const row = parseInt(parts[0], 10);
      const col = parseInt(parts[1], 10);
      const districtMatrix = cached.cityData.district_matrix || [];
      if (row < districtMatrix.length && col < districtMatrix[row]?.length) {
        districtName = districtMatrix[row][col] || '';
      }
    }
    
    // Render content
    renderHexContent(hexContent, hexId, districtName);
    
    // Show back button when viewing city hex detail
    document.getElementById("btn-back-city-overview")?.classList.add("visible");
  } catch (error) {
    console.error("Error generating city hex content:", error);
    appState.uiBox.renderStyled(`# City Hex ${hexId}\n\nError generating hex content.`);
    appState.uiBox.renderRaw("Error generating hex content.");
  }
}

async function handleWorldHexClick(cell, hexPos) {
  if (!cell || !cell.code) return;
  const terrain = cell.terrain || "plains";
  const code = cell.code;
  
  if (terrain === "city" || terrain === "settlement") {
    const overlayLoaded = await tryLoadOverlay(code);
    if (overlayLoaded) return;
  }
  fetchWorldHex(code);
}

// World hex double-click removed - now handled by card content double-click
async function handleWorldHexDoubleClick(cell, hexPos) {
  // Do nothing - editing is now triggered by double-clicking the card content
  return;
}

/**
 * Enter edit mode for a world hex
 */
async function enterWorldHexEditMode(code) {
  // First, fetch the hex content if not already loaded
  let currentContent = '';
  const cached = cache.getCachedWorldHex(code, appState.lang);
  if (cached && cached.raw_markdown) {
    currentContent = cached.raw_markdown;
  } else {
    // Fetch from API
    const attempts = [
      `/api/city/${code}?language=${appState.lang}`,
      `/api/settlement/${code}?language=${appState.lang}`,
      `/api/hex/${code}?language=${appState.lang}`,
    ];
    for (const url of attempts) {
      try {
        const res = await fetch(url);
        if (!res.ok) continue;
        const data = await res.json();
        currentContent = data.raw_markdown || "";
        // Cache it
        cache.cacheWorldHex(code, data, appState.lang);
        break;
      } catch {
        /* ignore */
      }
    }
  }
  
  // Set edit mode
  appState.editingWorldHex = true;
  appState.editingHexCode = code;
  
  // Hide back button, show save button
  document.getElementById("btn-back-city-overview")?.classList.remove("visible");
  document.getElementById("btn-save-world-hex")?.classList.add("visible");
  
  // Create editable textarea
  const cardContent = document.getElementById("card-content");
  if (cardContent) {
    const textarea = document.createElement("textarea");
    textarea.id = "world-hex-editor";
    textarea.className = "world-hex-editor";
    textarea.value = currentContent;

    cardContent.innerHTML = "";
    cardContent.appendChild(textarea);
    textarea.focus();
    
    // Also update raw content
    appState.uiBox.renderRaw(currentContent);
    
    // Update borders to match the new content height
    appState.uiBox.updateBorders();
    
    // Setup click-outside handler to cancel edit mode
    setupClickOutsideHandler();
  }
}

/**
 * Save edited world hex content
 */
function saveWorldHexEdit() {
  if (!appState.editingWorldHex || !appState.editingHexCode) return;
  
  const editor = document.getElementById("world-hex-editor");
  if (!editor) return;
  
  const editedContent = editor.value;
  const code = appState.editingHexCode;
  
  // Get existing cached data or create new
  const cached = cache.getCachedWorldHex(code, appState.lang) || {};
  
  // Update with edited content
  const updatedData = {
    ...cached,
    raw_markdown: editedContent,
    edited: true, // Mark as edited
    editedAt: Date.now()
  };
  
  // Save to cache
  cache.cacheWorldHex(code, updatedData, appState.lang);
  
  // Exit edit mode
  appState.editingWorldHex = false;
  appState.editingHexCode = null;
  
  // Hide save button, show back button if needed
  document.getElementById("btn-save-world-hex")?.classList.remove("visible");
  
  // Remove click-outside handler
  document.removeEventListener('click', handleClickOutside);
  
  // Re-render the content
  appState.uiBox.renderStyled(editedContent);
  appState.uiBox.renderRaw(editedContent);
  
  // Re-setup double-click handler for future edits
  setupWorldHexCardDoubleClick();
}

/**
 * Setup double-click handler on card content to enter edit mode
 */
function setupWorldHexCardDoubleClick() {
  const cardContent = document.getElementById("card-content");
  if (!cardContent || !appState.currentWorldHexCode) return;
  
  // Remove existing handler if any
  cardContent.removeEventListener('dblclick', handleCardDoubleClick);
  
  // Add double-click handler
  cardContent.addEventListener('dblclick', handleCardDoubleClick);
}

/**
 * Handle double-click on card content
 */
function handleCardDoubleClick(e) {
  // Only handle if we're in world mode and not already editing
  if (appState.mode !== "world" || appState.editingWorldHex) return;
  if (!appState.currentWorldHexCode) return;
  
  // Don't trigger if clicking on buttons or links
  if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' || e.target.closest('button') || e.target.closest('a')) {
    return;
  }
  
  // Enter edit mode for current hex
  enterWorldHexEditMode(appState.currentWorldHexCode);
}

/**
 * Setup click-outside handler to cancel edit mode
 */
function setupClickOutsideHandler() {
  // Remove existing handler if any
  document.removeEventListener('click', handleClickOutside);
  
  // Add click handler with a small delay to allow other click handlers to run first
  setTimeout(() => {
    document.addEventListener('click', handleClickOutside);
  }, 0);
}

/**
 * Handle clicks outside the edit box to cancel edit mode
 */
function handleClickOutside(e) {
  if (!appState.editingWorldHex) {
    document.removeEventListener('click', handleClickOutside);
    return;
  }
  
  const editor = document.getElementById("world-hex-editor");
  const cardContent = document.getElementById("card-content");
  const saveBtn = document.getElementById("btn-save-world-hex");
  
  // Check if click is outside the editor, card content, and save button
  if (editor && cardContent && saveBtn) {
    const clickedElement = e.target;
    const isClickInsideEditor = editor.contains(clickedElement);
    const isClickInsideCard = cardContent.contains(clickedElement);
    const isClickOnSaveBtn = saveBtn.contains(clickedElement) || clickedElement === saveBtn;
    
    // If click is outside all of these, cancel edit mode
    if (!isClickInsideEditor && !isClickOnSaveBtn) {
      // Cancel edit mode (don't save)
      cancelWorldHexEdit();
      document.removeEventListener('click', handleClickOutside);
    }
  }
}

/**
 * Cancel world hex edit without saving
 */
function cancelWorldHexEdit() {
  if (!appState.editingWorldHex || !appState.editingHexCode) return;
  
  const code = appState.editingHexCode;
  
  // Exit edit mode
  appState.editingWorldHex = false;
  appState.editingHexCode = null;
  
  // Hide save button
  document.getElementById("btn-save-world-hex")?.classList.remove("visible");
  
  // Reload the original content
  const cached = cache.getCachedWorldHex(code, appState.lang);
  if (cached && cached.raw_markdown) {
    appState.uiBox.renderStyled(cached.raw_markdown);
    appState.uiBox.renderRaw(cached.raw_markdown);
  } else {
    // Re-fetch if not cached
    fetchWorldHex(code);
  }
  
  // Re-setup double-click handler for future edits
  setupWorldHexCardDoubleClick();
}

async function handleCityHexClick(cell, hexPos) {
  if (!cell || !cell.hexId) return;
  fetchCityHex(appState.overlayName, cell.hexId);
}

// City hexes should not allow double-click editing
function handleCityHexDoubleClick(cell, hexPos) {
  // Do nothing - city hexes don't support editing
  return;
}

async function tryLoadOverlay(hexCode) {
  try {
    const res = await fetch(`/api/city-overlay/by-hex/${hexCode}`);
    if (!res.ok) return false;
    const data = await res.json();
    
    if (!data.name) return false;
    
    const overlayRes = await fetch(`/api/city-overlay/${data.name}?language=${appState.lang}`);
    if (!overlayRes.ok) return false;
    const overlayData = await overlayRes.json();
    
    if (!overlayData.success) return false;
    
    // Cache city data for use in hex clicks
    // This also loads persisted hex content from localStorage
    city.cacheCityData(overlayData);
    
    // DON'T clear hex content cache - we want to preserve cached encounters!
    // Only regenerate encounters when user explicitly clicks "Regenerate Encounter"
    
    const parsed = parseCityOverlayData(overlayData);
    if (!parsed) return false;
    
    if (!appState.cityGrid) {
      appState.cityGrid = createGridRenderer({
        canvasId: "grid-canvas",
        terrainMap: CITY_TERRAIN_MAP,
        fetchHexUrl: (hexId) => `/api/city-overlay/${data.name}/hex/${hexId}`,
        fetchMapUrl: () => `/api/city-overlay/${data.name}`,
        parseMapData: parseCityOverlayData,
        onHexClick: handleCityHexClick,
        onHexDoubleClick: handleCityHexDoubleClick, // Prevent editing city hexes
        gridConfig: GRID_CFG,
        hudElementId: "hud",
        autoCenterOnResize: true, // Auto-center city grid on resize
        onZoomChange: (zoom) => {
          if (appState.header) {
            appState.header.setParams({ zoom });
          }
        },
      });
      appState.cityGrid.setActive(false);
    }
    
    appState.mode = "overlay";
    appState.overlayName = data.name;
    appState.currentWorldHexCode = null; // Clear world hex code when entering city mode
    if (appState.worldGrid) appState.worldGrid.setActive(false);
    if (appState.cityGrid) {
      appState.cityGrid.setActive(true);
      appState.cityGrid.setState({
        grid: parsed.grid,
        rows: parsed.rows,
        cols: parsed.cols,
      });
      // Resize and center the grid in the left pane after state is set
      // Use requestAnimationFrame to ensure DOM has updated
      requestAnimationFrame(() => {
        appState.cityGrid.resize(); // This will also call centerGrid() internally
      });
    }
    document.getElementById("btn-exit-overlay")?.classList.add("visible");
    
    // Generate city overview markdown from city data
    const cityData = overlayData.city_data;
    if (cityData) {
      let overviewMd = `# ${cityData.display_name || cityData.city_name || data.name}\n\n`;
      if (cityData.description) {
        overviewMd += `${cityData.description}\n\n`;
      }
      if (cityData.theme) {
        overviewMd += `**Theme:** ${cityData.theme}\n\n`;
      }
      overviewMd += `## Districts\n\n`;
      if (cityData.districts && Array.isArray(cityData.districts)) {
        cityData.districts.forEach(district => {
          overviewMd += `### ${district.name || 'Unknown District'}\n\n`;
          if (district.description) {
            overviewMd += `${district.description}\n\n`;
          }
        });
      }
      appState.cityOverviewMarkdown = overviewMd;
      appState.uiBox.renderStyled(overviewMd);
      appState.uiBox.renderRaw(overviewMd);
    }
    
    // Hide back button when showing city overview
    document.getElementById("btn-back-city-overview")?.classList.remove("visible");
    
    return true;
  } catch (error) {
    console.error("Error loading overlay:", error);
    return false;
  }
}

function exitOverlay() {
  appState.mode = "world";
  appState.overlayName = null;
  appState.cityOverviewMarkdown = null;
  if (appState.cityGrid) appState.cityGrid.setActive(false);
  if (appState.worldGrid) {
    appState.worldGrid.setActive(true);
    appState.worldGrid.loadMap();
  }
  document.getElementById("btn-exit-overlay")?.classList.remove("visible");
  document.getElementById("btn-back-city-overview")?.classList.remove("visible");
}

function backToCityOverview() {
  if (appState.cityOverviewMarkdown) {
    appState.uiBox.renderStyled(appState.cityOverviewMarkdown);
    appState.uiBox.renderRaw(appState.cityOverviewMarkdown);
    document.getElementById("btn-back-city-overview")?.classList.remove("visible");
  }
}

function init() {
  appState.uiBox = createUIBox({});
  
  appState.header = createHeaderControls({
    onParamsChange: (params) => {
      const activeGrid = appState.mode === "overlay" ? appState.cityGrid : appState.worldGrid;
      if (activeGrid) {
        activeGrid.updateParams(params);
      }
    },
    onReset: async () => {
      const res = await fetch("/api/bootstrap", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ force: true }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || `Bootstrap failed: ${res.status}`);
      }
      if (appState.worldGrid) {
        await appState.worldGrid.loadMap();
      }
    },
    minZoom: GRID_CFG.minZoom,
    maxZoom: GRID_CFG.maxZoom,
  });
  
  appState.worldGrid = createGridRenderer({
    canvasId: "grid-canvas",
    terrainMap: WORLD_TERRAIN_MAP,
    fetchHexUrl: (code) => `/api/hex/${code}?language=${appState.lang}`,
    fetchMapUrl: () => "/api/map",
    parseMapData: parseWorldMapData,
    onHexClick: handleWorldHexClick,
    // No double-click on grid - editing is triggered by double-clicking card content
    gridConfig: GRID_CFG,
    hudElementId: "hud",
    onZoomChange: (zoom) => {
      if (appState.header) {
        appState.header.setParams({ zoom });
      }
    },
  });
  
  // Run migration on startup to migrate old cache format
  cache.migrateOldCache(appState.lang);
  
  // Check cache first before loading map
  const cachedMapData = cache.getCachedWorldMapData(appState.lang);
  if (cachedMapData && cachedMapData.grid) {
    // Use cached data directly
    appState.worldGrid.setState({
      grid: cachedMapData.grid,
      rows: cachedMapData.rows,
      cols: cachedMapData.cols
    });
  } else {
    // Load from API
    appState.worldGrid.loadMap();
  }
  
  document.getElementById("btn-exit-overlay")?.addEventListener("click", () => {
    exitOverlay();
  });
  
  document.getElementById("btn-back-city-overview")?.addEventListener("click", () => {
    backToCityOverview();
  });
  
  document.getElementById("btn-save-world-hex")?.addEventListener("click", () => {
    saveWorldHexEdit();
  });
  


  // Keyboard shortcut: Ctrl+D then M to toggle controls
  let ctrlHeld = false;
  let dPressed = false;
  let sequenceTimeout = null;
  const SEQUENCE_TIMEOUT_MS = 2000; // Reset sequence after 2 seconds

  function resetSequence() {
    dPressed = false;
    if (sequenceTimeout) {
      clearTimeout(sequenceTimeout);
      sequenceTimeout = null;
    }
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Control" || e.key === "Meta") {
      ctrlHeld = true;
      resetSequence();
      return;
    }

    if (!ctrlHeld) {
      resetSequence();
      return;
    }

    if (e.key === "d" || e.key === "D") {
      e.preventDefault();
      dPressed = true;
      if (sequenceTimeout) {
        clearTimeout(sequenceTimeout);
      }
      sequenceTimeout = setTimeout(resetSequence, SEQUENCE_TIMEOUT_MS);
      return;
    }

    if ((e.key === "m" || e.key === "M") && dPressed) {
      e.preventDefault();
      const controlsEl = document.querySelector(".controls");
      if (controlsEl) {
        controlsEl.classList.toggle("visible");
      }
      resetSequence();
      return;
    }

    // If any other key is pressed while waiting for M, reset
    resetSequence();
  });

  document.addEventListener("keyup", (e) => {
    if (e.key === "Control" || e.key === "Meta") {
      ctrlHeld = false;
      resetSequence();
    }
  });
  
  // Setup language selector
  setupLanguageSelector();
  
  // Setup import/export buttons
  setupImportExport();
}

/**
 * Setup language selector dropdown
 */
function setupLanguageSelector() {
  const langSelect = document.getElementById('lang-select');
  if (!langSelect) return;
  
  // Load available languages from API
  fetch('/api/languages')
    .then(res => res.json())
    .then(data => {
      if (data.languages && Array.isArray(data.languages)) {
        // Clear existing options
        langSelect.innerHTML = '';
        // Add options for each language
        data.languages.forEach(lang => {
          const option = document.createElement('option');
          option.value = lang;
          option.textContent = lang.toUpperCase();
          langSelect.appendChild(option);
        });
        // Set current language from appState (which loads from localStorage) or API response
        // Don't overwrite persisted language unless API has a different valid language
        const currentLang = appState.lang || data.current || 'en';
        langSelect.value = currentLang;
        // Only update appState if it wasn't already set from localStorage
        if (!appState.lang || appState.lang === DEFAULT_LANGUAGE) {
          appState.lang = currentLang;
          if (currentLang !== DEFAULT_LANGUAGE) {
            persistLanguage(currentLang);
          }
        }
      }
    })
    .catch(err => {
      console.warn('Failed to load languages:', err);
      // Set default if API fails
      langSelect.value = appState.lang || 'en';
    });
  
  // Handle language change
  langSelect.addEventListener('change', async (e) => {
    const newLang = e.target.value;
    if (newLang === appState.lang) return;
    
    try {
      const res = await fetch('/api/set-language', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: newLang })
      });
      
      if (res.ok) {
        // Persist language preference
        persistLanguage(newLang);
        await handleLanguageChange(newLang);
      } else {
        // Revert selection on error
        langSelect.value = appState.lang;
        const data = await res.json();
        alert(`Failed to change language: ${data.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Language change failed:', err);
      langSelect.value = appState.lang;
      alert(`Failed to change language: ${err.message}`);
    }
  });
  
  // Expose function to update selector when language changes programmatically
  window.updateLanguageSelector = (lang) => {
    if (langSelect && langSelect.value !== lang) {
      langSelect.value = lang;
    }
  };
}

/**
 * Setup import/export buttons
 */
function setupImportExport() {
  const exportBtn = document.getElementById('btn-export');
  const importBtn = document.getElementById('btn-import');
  const importFile = document.getElementById('import-file');
  
  // Export button
  if (exportBtn) {
    exportBtn.addEventListener('click', async () => {
      try {
        exportBtn.disabled = true;
        exportBtn.textContent = 'EXPORTING...';
        
        // Export cache data
        const cacheData = exportCacheData();
        
        // Fetch the ZIP from backend
        const res = await fetch('/api/export');
        if (!res.ok) {
          throw new Error('Export failed');
        }
        
        // Get the blob
        const blob = await res.blob();
        
        // Create a blob URL and download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dying_lands_output-${new Date().toISOString().slice(0, 10)}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        // Also save cache data to a separate file (optional - can be included in ZIP via backend)
        const cacheBlob = new Blob([JSON.stringify(cacheData, null, 2)], { type: 'application/json' });
        const cacheUrl = window.URL.createObjectURL(cacheBlob);
        const cacheA = document.createElement('a');
        cacheA.href = cacheUrl;
        cacheA.download = `client_cache_${appState.lang}.json`;
        document.body.appendChild(cacheA);
        cacheA.click();
        document.body.removeChild(cacheA);
        window.URL.revokeObjectURL(cacheUrl);
        
        exportBtn.textContent = 'EXPORT';
        alert('Export complete!');
      } catch (err) {
        console.error('Export failed:', err);
        exportBtn.textContent = 'EXPORT';
        alert(`Export failed: ${err.message}`);
      } finally {
        exportBtn.disabled = false;
      }
    });
  }
  
  // Import button
  if (importBtn && importFile) {
    importBtn.addEventListener('click', () => {
      importFile.click();
    });
    
    importFile.addEventListener('change', async (e) => {
      const file = e.target.files?.[0];
      if (!file) return;
      
      if (!file.name.toLowerCase().endsWith('.zip')) {
        alert('Please select a .zip file');
        importFile.value = '';
        return;
      }
      
      try {
        importBtn.disabled = true;
        importBtn.textContent = 'IMPORTING...';
        
        // Create FormData and send to backend
        const formData = new FormData();
        formData.append('file', file);
        
        const res = await fetch('/api/import', {
          method: 'POST',
          body: formData
        });
        
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.error || 'Import failed');
        }
        
        const data = await res.json();
        
        // Import cache data if present
        if (data.cacheData) {
          importCacheData(data.cacheData, appState.lang);
        }
        
        // Also try to load cache from the ZIP if it was included
        // (This would require reading the ZIP on frontend, which is more complex)
        // For now, we rely on the backend extracting client_cache.json
        
        importBtn.textContent = 'IMPORT';
        alert('Import complete! Reloading...');
        
        // Reload the page to use imported data
        window.location.reload();
      } catch (err) {
        console.error('Import failed:', err);
        importBtn.textContent = 'IMPORT';
        alert(`Import failed: ${err.message}`);
      } finally {
        importBtn.disabled = false;
        importFile.value = '';
      }
    });
  }
}

/**
 * Handle language change
 */
async function handleLanguageChange(newLang) {
  if (newLang === appState.lang) return;
  
  // Update app state
  appState.lang = newLang;
  
  // Update language selector if it exists
  if (window.updateLanguageSelector) {
    window.updateLanguageSelector(newLang);
  }
  
  // Clear in-memory caches (optional - we can keep both languages cached)
  // For now, we'll keep both cached but switch the active language
  
  // Reload current view with new language
  if (appState.mode === "overlay" && appState.overlayName) {
    // Reload city overlay with new language
    const hexCode = appState.currentHexId || "0101"; // Fallback
    await tryLoadOverlay(hexCode);
  } else {
    // Reload world map with new language
    const cachedMapData = cache.getCachedWorldMapData(newLang);
    if (cachedMapData && cachedMapData.grid) {
      appState.worldGrid.setState({
        grid: cachedMapData.grid,
        rows: cachedMapData.rows,
        cols: cachedMapData.cols
      });
    } else {
      await appState.worldGrid.loadMap();
    }
  }
}

/**
 * Export cache data (for inclusion in ZIP export)
 */
function exportCacheData() {
  return cache.exportCacheData(appState.lang);
}

/**
 * Import cache data (from ZIP import)
 */
function importCacheData(cacheData, language) {
  if (!cacheData) return false;
  return cache.importCacheData(cacheData, language || appState.lang);
}

init();
