# Hexy v2 Frontend Spec (retro markdown-first)

## Goals
- Consume markdown-only backend responses.
- Keep retro CRT-style look; low-latency, offline-friendly.
- Minimal controls: view map, pick hex, view markdown, export/import/save edits.

## API surface (v2)
- `GET /api/health` — availability.
- `POST /api/bootstrap` — trigger/ensure generation (uses cache).
- `GET /api/hex/:hexCode` — returns `{hex_code, raw_markdown, exists}`.
- `GET /api/debug-cache` — inspect cache state (dev).

## Primary views
- **Map overview**
  - Load ascii/summary once from generated output (read `ascii_map.txt` if shipped).
  - Click hex -> fetch `/api/hex/:code`, show markdown panel.
  - Indicate generated/unknown hex states.
- **Hex detail panel**
  - Render markdown (light styling); copy/share action.
  - Edit markdown (optional local-only), with save-to-file (export).
  - Show raw + formatted tabs.
- **Language toggle**
  - Until backend adds language switching, default to cfg language; keep UI ready for `?language=` param.
- **City overlays**
  - Defer generation UI; leave placeholder section to list overlays once `/api/city-overlay` endpoints are added back.
- **Export / Import**
  - Export: download zipped output dir (target future `/api/export`).
  - Import: upload zip and refresh cache (future `/api/import`).
- **Offline / caching**
  - Precache shell (HTML/CSS/JS/fonts) and last fetched hex markdown.
  - On load: call `/api/bootstrap`, then hydrate local cache.
  - If offline and hex missing locally, show fallback “not cached”.

## UX/Visual notes
- CRT/retro palette (greens/amber on dark), monospace, scanline overlay toggle.
- Keyboardable: arrow/WASD to move selection; Enter to open hex.
- Accessible semantics: `<main>`, `<nav>`, `<button>`, `<article>`; focus states visible.

## Data handling
- Store recent hex markdown in IndexedDB (keyed by hex code + version).
- Track generation version from `/api/debug-cache` manifest to invalidate caches.
- Do not attempt client-side parsing beyond markdown render.

## Deferred (Cursor Designer later)
- Full theming/polish.
- City overlay visualization.
- Integrated export/import UI once endpoints land.

##Grid module

```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hybrid Wireframe Grid - CRT</title>
    <style>
        :root {
            --bg-color: #feea00;
            --ui-bg: rgba(10, 15, 20, 0.9);
            --accent: #00ff41;
            --font-stack: 'Courier New', Courier, monospace; 
            
        }

        body {
            background-color: var(--bg-color);
            margin: 0;
            overflow: hidden;
            font-family: var(--font-stack);
            color: #ccc;
            user-select: none;
        }

        canvas {
            display: block;
            width: 100vw;
            height: 100vh;
            /* CRITICAL: Keeps pixels sharp when scaled up */
            image-rendering: pixelated; 
            /* CRT: Slight blur to blend pixels and boost saturation */
            filter: blur(0.4px) contrast(1.1) saturate(1.1);
        }

        /* --- CONTROLS --- */
        .controls {
            position: absolute;
            top: 20px;
            left: 20px;
            width: 200px;
            background: var(--ui-bg);
            padding: 15px;
            border: 1px solid #333;
            border-left: 3px solid var(--accent);
            color: #fff;
            font-size: 11px;
            font-family: sans-serif;
            z-index: 10;
            /* CRT: UI Glow */
            box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
            text-shadow: 0 0 2px rgba(255, 255, 255, 0.5);
        }
        
        .control-group { margin-bottom: 10px; }
        .control-group label { display: flex; justify-content: space-between; margin-bottom: 4px; color: #888; text-shadow: none; }
        input[type="range"] { width: 100%; cursor: pointer; accent-color: var(--accent); }

        /* --- HUD --- */
        .hud {
            position: absolute;
            bottom: 30px;
            right: 30px;
            width: 250px;
            background: var(--ui-bg);
            border: 1px solid #333;
            border-right: 4px solid var(--accent);
            padding: 20px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            z-index: 10;
            /* CRT: UI Glow */
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
            text-shadow: 0 0 4px currentColor;
        }
        .hud.visible { opacity: 1; }
        .hud h2 { margin: 0 0 10px 0; font-size: 14px; letter-spacing: 2px; border-bottom: 1px solid #333; padding-bottom: 5px; color: var(--accent); }
        .hud-row { display: flex; justify-content: space-between; margin-bottom: 5px; }
        .hud-val { font-weight: bold; color: #fff; font-family: var(--font-stack); }

        /* --- CRT FILTER OVERLAY --- */
        .crt-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 999;
            pointer-events: none; /* Let clicks pass through */
            
            /* Scanlines */
            background: linear-gradient(
                rgba(18, 16, 16, 0) 50%, 
                rgba(0, 0, 0, 0.1) 50%
            ), linear-gradient(
                90deg, 
                rgba(255, 0, 0, 0.06), 
                rgba(0, 255, 0, 0.02), 
                rgba(0, 0, 255, 0.06)
    s        );
            background-size: 100% 3px, 3px 100%;
            
            /* Vignette */
            box-shadow: inset 0 0 100px rgba(0,0,0,0.7);
            
            /* Subtle Flicker */
            animation: flicker 0.15s infinite;
        }

        @keyframes flicker {
            0% { opacity: 0.97; }
            100% { opacity: 1; }
        }

    </style>
</head>
<body>

    <div class="crt-overlay"></div>

    <div class="controls">
        <div class="control-group">
            <label>Rotate <span id="val-rot">-45</span></label>
            <input type="range" id="param-rot" min="-180" max="180" value="-45">
        </div>
        <div class="control-group">
            <label>Tilt <span id="val-tilt">0.45</span></label>
            <input type="range" id="param-tilt" min="0.2" max="1.0" step="0.01" value="0.55">
        </div>
        <div class="control-group">
            <label>Zoom <span id="val-zoom">3.0</span></label>
            <input type="range" id="param-zoom" min="0.5" max="5.0" step="0.1" value="2.0">
        </div>
        <div class="control-group">
            <label>Grid Opacity <span id="val-grid">0.3</span></label>
            <input type="range" id="param-grid" min="0" max="1" step="0.05" value="0.3">
        </div>
    </div>

    <canvas id="mainCanvas"></canvas>

    <div class="hud" id="hud">
        <h2 id="hud-title">SCANNING</h2>
        <div class="hud-row"><span>COORDS</span> <span class="hud-val" id="hud-coords">--</span></div>
        <div class="hud-row"><span>TYPE</span> <span class="hud-val" id="hud-type">--</span></div>
        <div class="hud-row"><span>THREAT</span> <span class="hud-val" id="hud-threat">--</span></div>
    </div>

    <script>
        /* --- CONFIG --- */
        // NEW: Controls how "crunchy" the pixels are. Higher = more pixelated.
        const PIXEL_SCALE = 1.05; 

        const CFG = {
            cols: 50,
            rows: 50,
            hexSize: 16 // Radius of the hex in pixels
        };

        const TERRAIN = {
            '~':  { s: '~~', label: 'DEEP SEA', threat: 'LOW', color: '#000' },
            '.':  { s: '..', label: 'PLAINS', threat: 'NONE', color: '#000' },
            'f':  { s: '↟↟', label: 'FOREST', threat: 'LOW', color: '#000' },
            'm':  { s: '▲▲', label: 'MOUNTAINS', threat: 'MED', color: '#000' },
            'd':  { s: '∴∴', label: 'DESERT', threat: 'HIGH', color: '#000' },
            's':  { s: '⁖⁖', label: 'SWAMP', threat: 'HIGH', color: '#000' },
            'C':  { s: '🜲', label: 'CITY', threat: 'SAFE', color: '#000' },
            'T':  { s: '⛫', label: 'SETTLEMENT', threat: 'SAFE', color: '#000' },
            'X':  { s: '🜹', label: 'ENCOUNTER', threat: 'EXTREME', color: '#000' },
            'O':  { s: '🜄', label: 'DUNGEON', threat: 'DEADLY', color: '#000c' },
        };

        /* --- MAP GENERATION --- */
        const map = [];
        for(let y=0; y<CFG.rows; y++) {
            const row = [];
            for(let x=0; x<CFG.cols; x++) {
                const r = Math.random();
                let t = '.';
                if(r>0.98) t='X'; else if(r>0.96) t='O'; else if(r>0.95) t='C';
                else if(r>0.90) t='T'; else if(r>0.80) t='m'; else if(r>0.70) t='f';
                else if(r>0.60) t='d'; else if(r>0.50) t='s'; else if(r>0.40) t='~';
                row.push(t);
            }
            map.push(row);
        }

        /* --- ENGINE --- */
        const canvas = document.getElementById('mainCanvas');
        const ctx = canvas.getContext('2d', { alpha: false });
        
        let cam = { x: 0, y: 0 };
        let hovered = null;
        let isDragging = false;
        
        const params = {
            rot: -35,
            tilt: 0.45,
            zoom: 3.5,
            gridAlpha: 0.3
        };

        const rad = deg => deg * Math.PI / 180;

        // NEW: Linear Interpolation helper for gap math
        const lerp = (p1, p2, t) => ({
            x: p1.x + (p2.x - p1.x) * t,
            y: p1.y + (p2.y - p1.y) * t
        });

        /* --- GEOMETRY HELPERS --- */
        function getHexPoints(cx, cy, r) {
            const points = [];
            for (let i = 0; i < 6; i++) {
                const angle_deg = 60 * i - 30;
                const angle_rad = Math.PI / 180 * angle_deg;
                points.push({
                    x: cx + r * Math.cos(angle_rad),
                    y: cy + r * Math.sin(angle_rad)
                });
            }
            return points;
        }

        /* --- MATH: SCREEN <-> WORLD --- */
    s    function screenToWorld(sx, sy) {
            let x = sx - (canvas.width/2 + cam.x);
            let y = sy - (canvas.height/2 + cam.y);
            x /= params.zoom;
            y /= params.zoom;
            y /= params.tilt; 
            const r = rad(-params.rot);
            const cos = Math.cos(r), sin = Math.sin(r);
            return { x: x * cos - y * sin, y: x * sin + y * cos };
        }

        /* --- RENDER LOOP --- */
        function draw() {
            // 1. Clear
            ctx.setTransform(1, 0, 0, 1, 0, 0);
            ctx.fillStyle = '#feea00'; // Sage green background
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // 2. Camera Transform
            // This applies rotation to the entire context.
            // Everything drawn below (including text) will rotate with the hex.
            ctx.translate(canvas.width/2 + cam.x, canvas.height/2 + cam.y);
            ctx.scale(params.zoom, params.zoom);
            ctx.scale(1, params.tilt);
            ctx.rotate(rad(params.rot));

            // 3. Grid Settings
            ctx.lineWidth = 1;
            // Slightly larger font to make the text/rotation visible
            ctx.font = "bold 8px Courier New"; 
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";

            // Hexagon Math
            const r = CFG.hexSize;
            const w = Math.sqrt(3) * r;
            const h = 2 * r;
            const xStep = w;
            const yStep = h * 0.75;

            // Draw Loop
            const offsetX = -(CFG.cols * xStep) / 2;
            const offsetY = -(CFG.rows * yStep) / 2;

            for (let row = 0; row < CFG.rows; row++) {
                for (let col = 0; col < CFG.cols; col++) {
                    
                    // Calculate Center Position
                    const xOff = (row % 2 === 1) ? (w / 2) : 0;
                    const cx = (col * xStep) + xOff + offsetX;
                    const cy = (row * yStep) + offsetY;

                    // Culling
                    if (cx*cx + cy*cy > 3000000) continue;

                    const type = map[row][col];
                    const data = TERRAIN[type];
                    const isHovered = hovered && hovered.r === row && hovered.c === col;

                    const pts = getHexPoints(cx, cy, r);

                    // --- DRAW FILL (Background shape) ---
                    ctx.beginPath();
                    ctx.moveTo(pts[0].x, pts[0].y);
                    for(let i=1; i<6; i++) ctx.lineTo(pts[i].x, pts[i].y);
                    ctx.closePath();
    s                ctx.fillStyle = isHovered ? '#000' : '#feea00'; 
                    ctx.fill();

                    // --- DRAW GAPPED LINES (Wireframe) ---
                    ctx.strokeStyle = '#000';
                    ctx.lineWidth = 1; 

                    for(let i=0; i<6; i++) {
                        const pStart = pts[i];
                        const pEnd = pts[(i+1)%6]; 

                        // 0.15 means start 15% along the line, and end at 85%
                        const gapSize = 0.15; 
                        const lineStart = lerp(pStart, pEnd, gapSize);
                        const lineEnd = lerp(pStart, pEnd, 1 - gapSize);

                        ctx.beginPath();
                        ctx.moveTo(lineStart.x, lineStart.y);
                        ctx.lineTo(lineEnd.x, lineEnd.y);
                        ctx.stroke();
                    }

                    // --- DRAW CONTENT ---
                    ctx.fillStyle = isHovered ? '#feea00' : data.color;
                    ctx.shadowBlur = 0; 
                    // This text is drawn inside the rotated context, so it rotates with the hex
                    ctx.fillText(data.s, cx, cy);
                }
            }
        }

        /* --- INTERACTION --- */
        const uiParams = {
            rot: document.getElementById('param-rot'),
            tilt: document.getElementById('param-tilt'),
            zoom: document.getElementById('param-zoom'),
            grid: document.getElementById('param-grid')
        };
        const uiVals = {
            rot: document.getElementById('val-rot'),
            tilt: document.getElementById('val-tilt'),
            zoom: document.getElementById('val-zoom'),
            grid: document.getElementById('val-grid')
        };

        function updateParams() {
            params.rot = parseFloat(uiParams.rot.value);
            params.tilt = parseFloat(uiParams.tilt.value);
            params.zoom = parseFloat(uiParams.zoom.value);
            params.gridAlpha = parseFloat(uiParams.grid.value);
            
            uiVals.rot.innerText = params.rot;
            uiVals.tilt.innerText = params.tilt;
            uiVals.zoom.innerText = params.zoom;
            uiVals.grid.innerText = params.gridAlpha;
            draw();
        }

        Object.values(uiParams).forEach(el => el.addEventListener('input', updateParams));

        function handleMove(e) {
            // Scale mouse input to match pixel resolution
            const mx = e.clientX / PIXEL_SCALE;
            const my = e.clientY / PIXEL_SCALE;

            if (isDragging) {
                cam.x += e.movementX / PIXEL_SCALE;
                cam.y += e.movementY / PIXEL_SCALE;
                requestAnimationFrame(draw);
                return;
            } 
            
            // Hover Logic
            const w = screenToWorld(mx, my);
            const r = CFG.hexSize;
            const h = 2 * r;
            const yStep = h * 0.75;
            const wHex = Math.sqrt(3) * r;
            
            const offsetX = -(CFG.cols * wHex) / 2;
            const offsetY = -(CFG.rows * yStep) / 2;
            
            const rowApprox = Math.round((w.y - offsetY) / yStep);
            const colApprox = Math.round((w.x - offsetX) / wHex);
            
            let found = null;
            let minD = Infinity;
            
            for(let row = rowApprox - 1; row <= rowApprox + 1; row++) {
                for(let col = colApprox - 1; col <= colApprox + 1; col++) {
                    if (row >= 0 && row < CFG.rows && col >= 0 && col < CFG.cols) {
                        const xOff = (row % 2 === 1) ? (wHex / 2) : 0;
                        const cx = (col * wHex) + xOff + offsetX;
                        const cy = (row * yStep) + offsetY;
                        
                        const dist = (w.x - cx)**2 + (w.y - cy)**2;
                        if (dist < r*r) { 
                            if (dist < minD) {
                                minD = dist;
                                found = { r: row, c: col };
                            }
                        }
                    }
                }
            }

            if (found) {
                if (!hovered || hovered.r !== found.r || hovered.c !== found.c) {
                    hovered = found;
                    updateHUD(found);
                    requestAnimationFrame(draw);
                }
            } else if (hovered) {
                hovered = null;
                updateHUD(null);
                requestAnimationFrame(draw);
            }
        }

        /* --- HUD --- */
        const hud = document.getElementById('hud');
        const hudEls = {
            coords: document.getElementById('hud-coords'),
            type: document.getElementById('hud-type'),
            threat: document.getElementById('hud-threat'),
            title: document.getElementById('hud-title')
        };

        function updateHUD(cell) {
            if (!cell) {
                hud.classList.remove('visible');
                return;
            }
            const type = map[cell.r][cell.c];
            const data = TERRAIN[type];
            
            hud.classList.add('visible');
            hud.style.borderRightColor = data.color;
            hudEls.title.style.color = data.color;
            
            hudEls.coords.innerText = `[${cell.c}, ${cell.r}]`;
            hudEls.type.innerText = data.label;
            hudEls.threat.innerText = data.threat;
            hudEls.threat.style.color = (data.threat === 'EXTREME' || data.threat === 'DEADLY') ? '#ef4444' : '#fff';
        }

        function resize() {
            // Set canvas internal resolution to fraction of screen size
            canvas.width = window.innerWidth / PIXEL_SCALE;
            canvas.height = window.innerHeight / PIXEL_SCALE;
            draw();
        }

        // Init
        canvas.addEventListener('mousedown', () => { isDragging = true; document.body.style.cursor = 'grabbing'; });
        window.addEventListener('mouseup', () => { isDragging = false; document.body.style.cursor = 'default'; });
        window.addEventListener('mousemove', handleMove);
        window.addEventListener('resize', resize);
        
        resize();

    </script>
</body>
</html>
```

##UI GENERIC CARDS:

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monochrome Inverted CRT</title>
    <style>
        :root {
            /* --- MONOCHROME INVERTED PALETTE --- */
            --bg-void: #050806;        /* Almost black background */
            
            /* The Core Single Color */
            --sage-bright: #feea00;    /* The main screen color */
            --sage-dim: #5a8a70;       /* For subtle gradients if needed */
            
            /* Inverted Text Color */
            --text-ink: #000000;       /* Pure black text */
            
            --font-stack: 'Courier New', Courier, monospace; 
            --line-height: 1.5;
            
            /* Outer CRT Glow (Green glow radiating from the bright box) */
            --box-glow: 0 0 25px rgba(131, 183, 153, 0.6), 0 0 50px rgba(131, 183, 153, 0.3);
        }

        body {
            background-color: var(--bg-void);
            margin: 0;
            padding: 40px;
            font-family: var(--font-stack);
            /* Default body color is green, but the card will override it */
            color: var(--sage-bright); 
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
            overflow-x: hidden;
            
            /* Subtle noisy background for the void outside the screen */
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.1'/%3E%3C/svg%3E");
        }

        /* --- CRT SCREEN EFFECTS --- */
        .screen-overlay {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            pointer-events: none;
            z-index: 999;
            
            /* Scanlines adapted for monochrome green */
            background: repeating-linear-gradient(
                0deg,
                rgba(0, 0, 0, 0.15) 0px,
                rgba(0, 0, 0, 0.15) 1px,
                transparent 1px,
                transparent 3px
            ),
            linear-gradient(
                90deg, 
                rgba(131, 183, 153, 0.03), 
                rgba(131, 183, 153, 0.08), 
                rgba(131, 183, 153, 0.03)
            );

            /* Flicker Animation */
            animation: flicker 0.15s infinite;
            opacity: 0.8;
        }

        @keyframes flicker {
            0% { opacity: 0.8; }
            50% { opacity: 0.75; }
            100% { opacity: 0.82; }
        }

        /* --- CARD STRUCTURE (INVERTED) --- */
        .ascii-card {
            display: flex;
            flex-direction: column;
            /* CRITICAL: Inverted Background */
            background: var(--sage-bright);
            /* CRITICAL: Inverted Text */
            color: var(--text-ink);
            
            width: 100%;
            max-width: 550px;
            /* Green glow radiating outwards */
            box-shadow: var(--box-glow);
            border: 2px solid var(--text-ink);
            margin-bottom: 50px;
            position: relative;
            z-index: 1;
        }

        /* NOTE: Inner text glow removed for clarity in inverted mode. 
           Black text glowing green looks muddy. */

        .border-row {
            display: flex;
            align-items: center;
            height: 20px;
            user-select: none;
            color: var(--text-ink);
            font-weight: 900; /* Extra thick borders */
        }

        .border-corner { width: 20px; text-align: center; flex-shrink: 0; }
        .border-fill { flex-grow: 1; overflow: hidden; white-space: nowrap; }
        
        .middle-row { display: flex; flex-direction: row; flex-grow: 1; }

        .border-side {
            width: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            overflow: hidden;
            color: var(--text-ink);
            user-select: none;
            flex-shrink: 0;
            font-weight: 900;
        }
        .border-side span { display: block; line-height: 14px; }

        .card-content {
            flex-grow: 1;
            padding: 20px 30px;
            min-height: 200px;
        }

        /* --- DYNAMIC MARKDOWN STYLING (INVERTED) --- */
        
        /* Headers */
        .md-h1 {
            font-size: 1.6em;
            text-transform: uppercase;
            color: var(--text-ink);
            border-bottom: 3px double var(--text-ink);
            padding-bottom: 10px;
            margin: 0 0 20px 0;
            letter-spacing: 2px;
            text-align: center;
            font-weight: 900;
        }
        
        .md-h2 {
            font-size: 1.1em;
            margin-top: 30px;
            margin-bottom: 15px;
            text-transform: uppercase;
            /* Inverted block style for H2 */
            background: var(--text-ink);
            color: 'white';
            padding: 4px 12px;
            display: inline-block;
            font-weight: bold;
            letter-spacing: 1px;
        }

        /* Paragraphs & Text */
        .md-p {
            margin-bottom: 15px;
            font-size: 0.95em;
            line-height: 1.6;
            color: var(--text-ink);
            font-weight: 600;
        }

        /* Strong/Bold (Keys) */
        strong {
            color: var(--text-ink);
            font-weight: 900;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.5px;
        }

        /* Key: Value Lines */
        .key-value-line {
            display: block;
            margin-bottom: 8px;
            padding-left: 15px;
            border-left: 3px solid var(--text-ink);
        }

        /* The '≈' Encounter Bullet */
        .special-bullet {
            color: var(--text-ink);
            font-weight: 900;
            margin-right: 10px;
            font-size: 1.3em;
            vertical-align: middle;
        }

        /* Threat Level Highlighting - Now just bold black pulsing */
        .threat-high {
            color: var(--text-ink);
            font-weight: 900;
            text-transform: uppercase;
            text-decoration: underline double;
            animation: panicMonochrome 0.8s infinite alternate;
        }

        @keyframes panicMonochrome {
            from { opacity: 0.7; }
            to { opacity: 1; }
        }

        /* Archaic decoration */
        .decoration-line {
            text-align: center;
            color: var(--text-ink);
            margin: 20px 0;
            letter-spacing: -2px;
            font-weight: 900;
            opacity: 0.5;
        }

    </style>
</head>
<body>

    <div class="screen-overlay"></div>

    <div class="ascii-card">
        <div class="border-row">
            <div class="border-corner">╔</div>
            <div class="border-fill">═════════════════════════════════════════════════════════════════════════</div>
            <div class="border-corner">╗</div>
        </div>

        <div class="middle-row">
            <div class="border-side" id="border-left"></div> <div class="card-content" id="markdown-target">
                </div>

            <div class="border-side" id="border-right"></div> </div>

        <div class="border-row">
            <div class="border-corner">╚</div>
            <div class="border-fill">═════════════════════════════════════════════════════════════════════════</div>
            <div class="border-corner">╝</div>
        </div>
    </div>

    <script>
        /* --- 1. THE RAW MARKDOWN DATA --- */
        const markdownData = `
# Hex 0104

**Terrain:** Mar

## Encounter
≈ **Horror Marinho Encounter**

## Denizen
**Horror Marinho**

Um terror antigo que dormiu sob as ondas por eras.

**Origem:** This entity emerged from the depths when the world began to die. It is said to be one of the Tephrotic nightmares that plague the dying lands.

**Comportamento:** The creature aguarda this area of the sea, preparando-se para o fim dos tempos.

**Threat Level:** Catastrophic - this entity represents an existential threat to all who encounter it.

**Território:** This section of the sea has been claimed by the nightmare, its influence corrupting the very waters themselves.

**Sunken Treasure:** A trinket with Mysterious properties. (lost to the depths)

## Notable Feature
Um local onde o próprio tempo parece fluir diferentemente

## Atmosphere
Sombras dançam sob a superfície, sugerindo coisas melhor deixadas invisíveis

## Loot Found
**Type:** trinket
**Item:** Duas mãos decepadas
**Description:** A trinket w#feea00ith Mysterious properties.
**Full Description:** A mysterious trinket that Mysterious properties. Its origins are unknown.

## Sea Encounter Details
**Tipo:** Horror Marinho

## Nível de Ameaça
Catastrophic - this entity represents an existential threat to all who encounter it.
`;

        /* --- 2. THE PARSER --- */
        function parseAndRender(md) {
            const lines = md.split('\n');
            let html = '';#feea00

            // Decoration logic
            const divider = '<div class="decoration-line">---===---</div>';

            lines.forEach(line => {
                line = line.trim();
                if(!line) return; 

                // 1. Header 1 (#)
                if (line.startsWith('# ')) {
                    html += `<h1 class="md-h1">${line.substring(2)}</h1>`;
                    return;
                }

                // 2. Header 2 (##)
                if (line.startsWith('## ')) {
                    html += `<h2 class="md-h2">${line.substring(3)}</h2>`;
                    return;
                }

                // 3. Bold Parsing (**text**)
                let content = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

                // 4. Special Encounter Bullet (≈)
                if (content.startsWith('≈')) {
                    content = content.substring(1).trim();
                    html += `<div class="md-p"><span class="special-bullet">≈</span>${content}</div>`;
                    return;
                }

                // 5. Threat Level Styling
                if (content.toLowerCase().includes('catastrophic') || content.toLowerCase().includes('deadly')) {
                    content = content.replace(/Catastrophic|Deadly/gi, match => `<span class="threat-high">${match}</span>`);
                }

                // 6. Key: Value detection
                if (content.startsWith('<strong>') && content.includes('</strong>:')) {
                    html += `<div class="key-value-line md-p">${content}</div>`;
                } else {
                    html += `<div class="md-p">${content}</div>`;
                }
            });

            return html;
        }

        /* --- 3. BORDER LOGIC --- */
        function updateBorders() {
            const sides = document.querySelectorAll('.border-side');
            sides.forEach(side => {
                side.innerHTML = '';
                const count = Math.ceil(side.parentElement.offsetHeight / 14); 
                let str = '';
                // Using double lines for archaic heavy feel
                for(let i=0;#feea00 i<count; i++) str += '<span>║</span>';
                side.innerHTML = str;
            });
        }

        /* --- 4. INIT --- */
        const target = document.getElementById('markdown-target');
        
        target.innerHTML = parseAndRender(markdownData);
        
        setTimeout(updateBorders, 50);
        window.addEventListene#feea00r('resize', updateBorders);

    </script>
</body>
</html>

