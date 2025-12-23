import { createGridRenderer } from './grid.js';
import { createUIBox } from './uiBox.js';
import { createHeaderControls } from './header.js';

const BG = "#feea00";
const PINK = "#FF3EB5";
const BLACK = "#000000";
const DEFAULT_LANGUAGE = "en";
const BLUE = '#2daefd';

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

const appState = {
  mode: "world",
  overlayName: null,
  lang: DEFAULT_LANGUAGE,
  worldGrid: null,
  cityGrid: null,
  uiBox: null,
  header: null,
  cityOverviewMarkdown: null,
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
  return { grid, rows, cols };
}

function parseCityOverlayData(data) {
  // Handle API response structure: {success: true, overlay: {...}}
  const overlay = data.overlay || data;
  if (!overlay.hex_grid) return null;
  
  const hexGrid = overlay.hex_grid;
  const rows = new Set();
  const cols = new Set();
  
  for (const hexId of Object.keys(hexGrid)) {
    if (hexId.includes('_')) {
      const [row, col] = hexId.split('_').map(Number);
      rows.add(row);
      cols.add(col);
    }
  }
  
  if (rows.size === 0 || cols.size === 0) return null;
  
  const maxRow = Math.max(...rows);
  const maxCol = Math.max(...cols);
  const grid = [];
  
  for (let row = 0; row <= maxRow; row++) {
    const rowData = [];
    for (let col = 0; col <= maxCol; col++) {
      const hexId = `${row}_${col}`;
      const hexData = hexGrid[hexId];
      if (hexData) {
        const content = hexData.content || {};
        const terrain = content.type || "empty";
        rowData.push({ terrain, hexId, code: hexId, content, district: hexData.district });
      } else {
        rowData.push({ terrain: "empty", hexId, code: hexId });
      }
    }
    grid.push(rowData);
  }
  
  return { grid, rows: grid.length, cols: grid[0]?.length || 0 };
}

async function fetchWorldHex(code) {
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
      appState.uiBox.renderStyled(md);
      appState.uiBox.renderRaw(md);
      return;
    } catch {
      /* ignore */
    }
  }
  appState.uiBox.renderStyled(`# Hex ${code}\n\nNot found.`);
  appState.uiBox.renderRaw("Not found.");
}

async function fetchCityHex(overlayName, hexId) {
  try {
    const res = await fetch(`/api/city-overlay/${overlayName}/hex/${hexId}?language=${appState.lang}`);
    if (!res.ok) {
      appState.uiBox.renderStyled(`# City Hex ${hexId}\n\nNot found.`);
      appState.uiBox.renderRaw("Not found.");
      return;
    }
    const data = await res.json();
    if (data.success && data.hex) {
      const hex = data.hex;
      const content = hex.content || {};
      let md = `# ${content.name || hexId}\n\n`;
      md += `**Type:** ${content.type || 'unknown'}\n\n`;
      if (content.description) md += `**Description:** ${content.description}\n\n`;
      if (content.encounter) md += `**Encounter:** ${content.encounter}\n\n`;
      if (content.atmosphere) md += `**Atmosphere:** ${content.atmosphere}\n\n`;
      if (hex.district) md += `**District:** ${hex.district}\n\n`;
      appState.uiBox.renderStyled(md);
      appState.uiBox.renderRaw(md);
      // Show back button when viewing city hex detail
      document.getElementById("btn-back-city-overview")?.classList.add("visible");
    } else {
      appState.uiBox.renderStyled(`# City Hex ${hexId}\n\nNot found.`);
      appState.uiBox.renderRaw("Not found.");
    }
  } catch (error) {
    console.error("Error fetching city hex:", error);
    appState.uiBox.renderStyled(`# City Hex ${hexId}\n\nError loading hex details.`);
    appState.uiBox.renderRaw("Error loading hex details.");
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

async function handleCityHexClick(cell, hexPos) {
  if (!cell || !cell.hexId) return;
  fetchCityHex(appState.overlayName, cell.hexId);
}

async function tryLoadOverlay(hexCode) {
  try {
    const res = await fetch(`/api/city-overlay/by-hex/${hexCode}`);
    if (!res.ok) return false;
    const data = await res.json();
    
    if (!data.name) return false;
    
    const overlayRes = await fetch(`/api/city-overlay/${data.name}`);
    if (!overlayRes.ok) return false;
    const overlayData = await overlayRes.json();
    
    if (!overlayData.success || !overlayData.overlay) return false;
    
    const parsed = parseCityOverlayData(overlayData.overlay);
    if (!parsed) return false;
    
    if (!appState.cityGrid) {
      appState.cityGrid = createGridRenderer({
        canvasId: "grid-canvas",
        terrainMap: CITY_TERRAIN_MAP,
        fetchHexUrl: (hexId) => `/api/city-overlay/${data.name}/hex/${hexId}`,
        fetchMapUrl: () => `/api/city-overlay/${data.name}`,
        parseMapData: parseCityOverlayData,
        onHexClick: handleCityHexClick,
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
    
    if (overlayData.overlay.raw_markdown) {
      appState.cityOverviewMarkdown = overlayData.overlay.raw_markdown;
      appState.uiBox.renderStyled(overlayData.overlay.raw_markdown);
      appState.uiBox.renderRaw(overlayData.overlay.raw_markdown);
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
    gridConfig: GRID_CFG,
    hudElementId: "hud",
    onZoomChange: (zoom) => {
      if (appState.header) {
        appState.header.setParams({ zoom });
      }
    },
  });
  
  appState.worldGrid.loadMap();
  
  document.getElementById("btn-exit-overlay")?.addEventListener("click", () => {
    exitOverlay();
  });
  
  document.getElementById("btn-back-city-overview")?.addEventListener("click", () => {
    backToCityOverview();
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
}

init();
