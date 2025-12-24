const BG = "#000000";
const BLACK = "#000000";

function rad(deg) {
  return (deg * Math.PI) / 180;
}

function clamp(val, min, max) {
  return Math.max(min, Math.min(max, val));
}
//TODO change name to getBridgeGlyphOrientation
function getBridgeGlyph(row, col, grid) {
  const isOdd = row % 2 === 1;
  const offsets = isOdd 
    ? { nw: [row-1, col], ne: [row-1, col+1], se: [row+1, col+1], sw: [row+1, col] }
    : { nw: [row-1, col-1], ne: [row-1, col], se: [row+1, col], sw: [row+1, col-1] };
  
  const isBridge = (r, c) => grid[r]?.[c]?.terrain === "bridge";
  
  const nwse = (isBridge(...offsets.nw) ? 1 : 0) + (isBridge(...offsets.se) ? 1 : 0);
  const nesw = (isBridge(...offsets.ne) ? 1 : 0) + (isBridge(...offsets.sw) ? 1 : 0);
  
  // Return ▱ with flip flag for left-leaning
  //TODO move glyph to TERRAIN_MAP
  return { glyph: "▰", flip: nesw > nwse };
}

export function createGridRenderer(config) {
  const {
    canvasId,
    terrainMap,
    fetchHexUrl,
    fetchMapUrl,
    parseMapData,
    onHexClick,
    onHexDoubleClick,
    gridConfig,
    onHoverUpdate,
    hudElementId,
    autoCenterOnResize = false, // Only auto-center city grids on resize
  } = config;

  const canvas = document.getElementById(canvasId);
  if (!canvas) {
    throw new Error(`Canvas element with id "${canvasId}" not found`);
  }
  const ctx = canvas.getContext("2d", { alpha: false });

  const MIN_ZOOM = gridConfig?.minZoom || 1.0;
  const MAX_ZOOM = gridConfig?.maxZoom || 1.5;
  const HEX_SIZE = gridConfig?.hexSize || 30;

  let state = {
    grid: [],
    cols: 0,
    rows: 0,
    viewW: 0,
    viewH: 0,
    cam: { x: 0, y: 0 },
    hovered: null,
    dragging: false,
    active: true,
    params: {
      rot: gridConfig?.rot || -45,
      tilt: gridConfig?.tilt || 0.55,
      zoom: gridConfig?.zoom || 1.2,
      gridAlpha: gridConfig?.gridAlpha || 1,
    },
  };

  function getHexPoints(cx, cy, r) {
    const pts = [];
    for (let i = 0; i < 6; i++) {
      const angle_deg = 60 * i - 30;
      const angle_rad = Math.PI / 180 * angle_deg;
      pts.push({ x: cx + r * Math.cos(angle_rad), y: cy + r * Math.sin(angle_rad) });
    }
    return pts;
  }

  function setTransform() {
    const dpr = window.devicePixelRatio || 1;
    // Reset transform and account for device pixel ratio
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = BG;
    ctx.fillRect(0, 0, state.viewW, state.viewH);
    ctx.translate(state.viewW / 2 + state.cam.x, state.viewH / 2 + state.cam.y);
    ctx.scale(state.params.zoom, state.params.zoom);
    ctx.scale(1, state.params.tilt);
    ctx.rotate(rad(state.params.rot));
  }

  function worldToScreen(wx, wy) {
    let x = wx;
    let y = wy;
    const r = rad(state.params.rot);
    const cos = Math.cos(r);
    const sin = Math.sin(r);
    const rx = x * cos - y * sin;
    const ry = x * sin + y * cos;
    const sx = rx * state.params.zoom + state.cam.x + state.viewW / 2;
    const sy = ry * state.params.zoom * state.params.tilt + state.cam.y + state.viewH / 2;
    return { x: sx, y: sy };
  }

  function screenToWorld(sx, sy) {
    let x = sx - (state.viewW / 2 + state.cam.x);
    let y = sy - (state.viewH / 2 + state.cam.y);
    x /= state.params.zoom;
    y /= state.params.zoom;
    y /= state.params.tilt;
    const r = rad(-state.params.rot);
    const cos = Math.cos(r);
    const sin = Math.sin(r);
    return { x: x * cos - y * sin, y: x * sin + y * cos };
  }

  function screenToHex(sx, sy) {
    const world = screenToWorld(sx, sy);

    const hexR = HEX_SIZE;
    const w = Math.sqrt(3) * hexR;
    const h = 2 * hexR;
    const yStep = h * 0.75;
    const offsetX = -(state.cols * w) / 2;
    const offsetY = -(state.rows * yStep) / 2;

    const rowApprox = Math.round((world.y - offsetY) / yStep);
    const colApprox = Math.round((world.x - offsetX) / w);

    let found = null;
    let minD = Infinity;
    for (let row = rowApprox - 1; row <= rowApprox + 1; row++) {
      for (let col = colApprox - 1; col <= colApprox + 1; col++) {
        if (row < 0 || col < 0 || row >= state.rows || col >= state.cols) continue;
        const xOff = row % 2 === 1 ? w / 2 : 0;
        const cx = col * w + xOff + offsetX;
        const cy = row * yStep + offsetY;
        const dist = (world.x - cx) ** 2 + (world.y - cy) ** 2;
        if (dist < hexR * hexR && dist < minD) {
          minD = dist;
          found = { row, col };
        }
      }
    }
    return found;
  }

  function updateHUD(cell) {
    if (!hudElementId) return;
    const hud = document.getElementById(hudElementId);
    if (!hud) return;

    const coords = document.getElementById("hud-coords");
    const type = document.getElementById("hud-type");
    const threat = document.getElementById("hud-threat");
    const title = document.getElementById("hud-title");

    if (!cell) {
      hud.classList.remove("visible");
      return;
    }

    const data = state.grid[cell.row]?.[cell.col];
    const terrain = data?.terrain || "plains";
    const terrainInfo = terrainMap[terrain] || { label: terrain, glyph: ".." };
    hud.classList.add("visible");
    
    // For city hexes, show district name instead of hex coordinates
    let displayedCoords;
    if (data?.district) {
      // City hex - show district name
      displayedCoords = data.district;
    } else {
      // World hex - show hex coordinates
      displayedCoords = data?.code || data?.hexId || `[${cell.col + 1}, ${cell.row + 1}]`;
    }
    
    if (coords) coords.textContent = displayedCoords;
    if (type) type.textContent = terrainInfo.label;
    if (threat) threat.textContent = terrainInfo.label;
    if (title) title.style.color = "#00ff41";
  }

  function getHexNeighbors(row, col) {
    const isOdd = row % 2 === 1;
    const offsets = isOdd 
      ? [[row-1, col], [row-1, col+1], [row, col+1], [row+1, col+1], [row+1, col], [row, col-1]]
      : [[row-1, col-1], [row-1, col], [row, col+1], [row+1, col], [row+1, col-1], [row, col-1]];
    
    return offsets
      .map(([r, c]) => ({row: r, col: c}))
      .filter(({row, col}) => row >= 0 && col >= 0 && row < state.rows && col < state.cols);
  }

  function drawRoads(offsetX, offsetY, xStep, yStep, w) {
    if (!state.grid.length) return;
    ctx.lineWidth = 3;
    ctx.strokeStyle = 'BLUE';
    ctx.setLineDash([3, 5]);
    
    const drawnEdges = new Set();
    
    for (let row = 0; row < state.rows; row++) {
      for (let col = 0; col < state.cols; col++) {
        const cell = state.grid[row]?.[col];
        if (!cell?.has_road) continue;
        
        const cx = col * xStep + (row % 2 === 1 ? w / 2 : 0) + offsetX;
        const cy = row * yStep + offsetY;
        
        const neighbors = getHexNeighbors(row, col);
        for (const neighbor of neighbors) {
          const nCell = state.grid[neighbor.row]?.[neighbor.col];
          if (nCell?.has_road) {
            // Avoid drawing duplicate lines
            const edgeKey = row < neighbor.row || (row === neighbor.row && col < neighbor.col)
              ? `${row},${col}-${neighbor.row},${neighbor.col}`
              : `${neighbor.row},${neighbor.col}-${row},${col}`;
            
            if (drawnEdges.has(edgeKey)) continue;
            drawnEdges.add(edgeKey);
            
            const nx = neighbor.col * xStep + (neighbor.row % 2 === 1 ? w / 2 : 0) + offsetX;
            const ny = neighbor.row * yStep + offsetY;
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(nx, ny);
            ctx.stroke();
          }
        }
      }
    }
    
    ctx.setLineDash([]);
  }

  function drawGrid(highlight) {
    if (!state.active) return; // Don't draw if this grid is not active
    if (!state.grid.length) return;
    setTransform();

    const r = HEX_SIZE;
    const w = Math.sqrt(3) * r;
    const h = 2 * r;
    const xStep = w;
    const yStep = h * 0.75;
    const offsetX = -(state.cols * xStep) / 2;
    const offsetY = -(state.rows * yStep) / 2;

    const extraCols = Math.ceil((state.viewW / state.params.zoom) / xStep) + 2;
    const extraRows = Math.ceil((state.viewH / state.params.zoom) / yStep) + 2;

    const fontSize = clamp(HEX_SIZE * state.params.zoom * 0.8, 12, 20);
    const glyphs = [];

    ctx.lineWidth = 2;

    for (let row = -extraRows; row < state.rows + extraRows; row++) {
      for (let col = -extraCols; col < state.cols + extraCols; col++) {
        const parity = ((row % 2) + 2) % 2;
        const xOff = parity === 1 ? w / 2 : 0;
        const cx = col * xStep + xOff + offsetX;
        const cy = row * yStep + offsetY;

        const code = state.grid[row]?.[col];
        const terrain = code?.terrain || "deep_sea";
        let glyph = terrainMap[terrain]?.glyph || "..";
        let flipGlyph = false;
        if (terrain === "bridge") {
          const bridgeData = getBridgeGlyph(row, col, state.grid);
          glyph = bridgeData.glyph;
          flipGlyph = bridgeData.flip;
        }

        const pts = getHexPoints(cx, cy, r);
        ctx.beginPath();
        ctx.moveTo(pts[0].x, pts[0].y);
        for (let i = 1; i < 6; i++) ctx.lineTo(pts[i].x, pts[i].y);
        ctx.closePath();

        const isHighlight = highlight && highlight.row === row && highlight.col === col;
        
        // Use district color if available (for city grids), otherwise use terrain fill
        let fillColor;
        if (code?.districtColor) {
          // City hex with district color
          fillColor = isHighlight ? BG : code.districtColor;
        } else {
          // World hex or empty hex
          fillColor = terrainMap[terrain]?.fill || BG;
          if (isHighlight) {
            fillColor = terrainMap[terrain]?.hover_fill || BLACK;
          }
        }
        
        ctx.fillStyle = fillColor;
        ctx.fill();

        ctx.strokeStyle = `rgba(0,0,0,${state.params.gridAlpha})`;
        for (let i = 0; i < 6; i++) {
          const a = pts[i];
          const b = pts[(i + 1) % 6];
          const gap = 0.15;
          const sx = a.x + (b.x - a.x) * gap;
          const sy = a.y + (b.y - a.y) * gap;
          const ex = a.x + (b.x - a.x) * (1 - gap);
          const ey = a.y + (b.y - a.y) * (1 - gap);
          ctx.beginPath();
          ctx.moveTo(sx, sy);
          ctx.lineTo(ex, ey);
          ctx.stroke();
        }

        const screenPos = worldToScreen(cx, cy);
        const symbolColor = terrainMap[terrain]?.symbol_color || BLACK;
        const hoverSymbolColor = terrainMap[terrain]?.hovered_symbol_color || BG;
        glyphs.push({
          x: screenPos.x,
          y: screenPos.y,
          glyph,
          color: isHighlight ? hoverSymbolColor : symbolColor,
          flip: flipGlyph,
        });
      }
    }

    // Draw roads before glyphs
    drawRoads(offsetX, offsetY, xStep, yStep, w);

    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.font = `bold ${fontSize}px Courier New`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    for (const g of glyphs) {
      if (g.x < -fontSize || g.x > state.viewW + fontSize || g.y < -fontSize || g.y > state.viewH + fontSize) continue;
      ctx.fillStyle = g.color;
      if (g.flip) {
        ctx.save();
        ctx.translate(g.x, g.y);
        ctx.scale(-1, 1);
        ctx.fillText(g.glyph, 0, 0);
        ctx.restore();
      } else {
        ctx.fillText(g.glyph, g.x, g.y);
      }
    }
  }

  function normalizePointer(e) {
    const rect = canvas.getBoundingClientRect();
    return {
      mx: (e.clientX - rect.left),
      my: (e.clientY - rect.top),
    };
  }

  function handleClick(x, y) {
    if (!state.active) return;
    const hx = screenToHex(x, y);
    if (!hx) return;
    const cell = state.grid[hx.row]?.[hx.col];
    if (!cell) return;
    drawGrid({ row: hx.row, col: hx.col });
    updateHUD(hx);
    if (onHexClick) {
      onHexClick(cell, hx);
    }
  }

  function handleHover(x, y) {
    if (!state.active) return;
    const hx = screenToHex(x, y);
    if (hx && (!state.hovered || hx.row !== state.hovered.row || hx.col !== state.hovered.col)) {
      state.hovered = hx;
      updateHUD(hx);
      drawGrid(hx);
      if (onHoverUpdate) {
        onHoverUpdate(state.grid[hx.row]?.[hx.col], hx);
      }
    } else if (!hx && state.hovered) {
      state.hovered = null;
      updateHUD(null);
      drawGrid();
    }
  }

  function setupEventHandlers() {
    let clickTimeout = null;
    canvas.addEventListener("click", (e) => {
      const { mx, my } = normalizePointer(e);
      // Handle single click with delay to detect double-click
      if (clickTimeout) {
        clearTimeout(clickTimeout);
        clickTimeout = null;
        // This is a double-click
        const hx = screenToHex(mx, my);
        if (hx) {
          const cell = state.grid[hx.row]?.[hx.col];
          if (cell && onHexDoubleClick) {
            onHexDoubleClick(cell, hx);
            return;
          }
        }
      } else {
        // Single click - wait to see if it becomes a double-click
        clickTimeout = setTimeout(() => {
          handleClick(mx, my);
          clickTimeout = null;
        }, 250); // 250ms delay to detect double-click
      }
    });

    canvas.addEventListener("mousedown", () => {
      if (!state.active) return;
      state.dragging = true;
      document.body.style.cursor = "grabbing";
    });

    window.addEventListener("mouseup", () => {
      if (!state.active) return;
      state.dragging = false;
      document.body.style.cursor = "default";
    });

    window.addEventListener("mousemove", (e) => {
      if (!state.active) return;
      const { mx, my } = normalizePointer(e);
      if (state.dragging) {
        state.cam.x += e.movementX;
        state.cam.y += e.movementY;
        drawGrid(state.hovered);
        return;
      }
      handleHover(mx, my);
    });

    canvas.addEventListener(
      "wheel",
      (e) => {
        if (!state.active) return;
        e.preventDefault();
        const delta = e.deltaY > 0 ? -0.05 : 0.05;
        state.params.zoom = clamp(state.params.zoom + delta, MIN_ZOOM, MAX_ZOOM);
        drawGrid(state.hovered);
        if (config.onZoomChange) {
          config.onZoomChange(state.params.zoom);
        }
      },
      { passive: false }
    );

    let resizeFrameId;
    const performResize = () => {
      if (resizeFrameId) {
        cancelAnimationFrame(resizeFrameId);
      }
      // Use requestAnimationFrame for immediate response on next frame
      resizeFrameId = requestAnimationFrame(() => {
        resize();
        resizeFrameId = null;
      });
    };
    
    window.addEventListener("resize", performResize);
    
    // Use ResizeObserver to detect canvas size changes (including layout changes)
    // ResizeObserver is more reliable than window resize for element size changes
    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        // ResizeObserver already batches, so we can call resize directly
        performResize();
      }
    });
    
    // Observe both the canvas and its parent container
    resizeObserver.observe(canvas);
    if (canvas.parentElement) {
      resizeObserver.observe(canvas.parentElement);
    }
  }

  async function loadMap() {
    if (!fetchMapUrl) return;
    try {
      const url = typeof fetchMapUrl === 'function' ? fetchMapUrl() : fetchMapUrl;
      const res = await fetch(url);
      if (!res.ok) throw new Error("map fetch failed");
      const data = await res.json();
      if (parseMapData) {
        const parsed = parseMapData(data);
        if (parsed) {
          state.grid = parsed.grid;
          state.rows = parsed.rows;
          state.cols = parsed.cols;
          drawGrid();
          return true;
        }
      }
    } catch (e) {
      console.warn("map load failed", e);
    }
    return false;
  }

  function resize() {
    // Force a layout recalculation by reading offsetWidth/offsetHeight first
    // This ensures the browser has calculated the new layout
    const container = canvas.parentElement;
    if (container) {
      // Force layout recalculation
      void container.offsetHeight;
    }
    
    // Use clientWidth/clientHeight which are more reliable than getBoundingClientRect
    // for elements with percentage-based sizing
    const displayWidth = canvas.clientWidth || canvas.offsetWidth;
    const displayHeight = canvas.clientHeight || canvas.offsetHeight;
    
    if (displayWidth === 0 || displayHeight === 0) {
      // Canvas not yet laid out, try again soon
      setTimeout(resize, 50);
      return;
    }
    
    // Handle high-DPI displays
    const dpr = window.devicePixelRatio || 1;
    const actualWidth = Math.floor(displayWidth * dpr);
    const actualHeight = Math.floor(displayHeight * dpr);
    
    // Only update if dimensions actually changed
    if (state.viewW === displayWidth && state.viewH === displayHeight && 
        canvas.width === actualWidth && canvas.height === actualHeight) {
      return;
    }
    
    state.viewW = displayWidth;
    state.viewH = displayHeight;
    
    // Only update canvas dimensions and redraw if this grid is active
    // This prevents inactive grids from clearing the canvas during resize
    if (!state.active) {
      return;
    }
    
    // Set internal canvas resolution (for high-DPI)
    // This is the actual pixel resolution of the canvas
    canvas.width = actualWidth;
    canvas.height = actualHeight;
    
    // Don't set inline styles - let CSS handle the display size
    // The canvas will be scaled by the browser to match CSS dimensions
    
    // Re-center grid after resize if configured to do so and we have grid data
    if (autoCenterOnResize && state.grid.length > 0) {
      centerGrid();
    } else {
      drawGrid();
    }
  }

  function updateParams(params) {
    if (params.rot !== undefined) state.params.rot = params.rot;
    if (params.tilt !== undefined) state.params.tilt = params.tilt;
    if (params.zoom !== undefined) state.params.zoom = clamp(params.zoom, MIN_ZOOM, MAX_ZOOM);
    if (params.gridAlpha !== undefined) state.params.gridAlpha = params.gridAlpha;
    drawGrid(state.hovered);
  }

  function getState() {
    return { ...state };
  }

  function setState(newState) {
    if (newState.grid !== undefined) state.grid = newState.grid;
    if (newState.rows !== undefined) state.rows = newState.rows;
    if (newState.cols !== undefined) state.cols = newState.cols;
    if (newState.cam !== undefined) state.cam = { ...state.cam, ...newState.cam };
    drawGrid(state.hovered);
  }

  function centerGrid() {
    // Center the grid in the viewport
    // The grid is already offset to center at origin in world space,
    // so we just need to ensure the camera is at 0,0
    // This will center the grid in the canvas viewport
    state.cam = { x: 0, y: 0 };
    drawGrid(state.hovered);
  }

  setupEventHandlers();
  resize();

  function setActive(active) {
    state.active = active;
    if (!active) {
      state.hovered = null;
      state.dragging = false;
      updateHUD(null);
    }
  }

  return {
    loadMap,
    drawGrid,
    handleClick,
    handleHover,
    updateParams,
    getState,
    setState,
    resize,
    setActive,
    centerGrid,
  };
}
