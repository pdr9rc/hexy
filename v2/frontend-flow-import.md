## Frontend Flow (Retro CRT, Markdown-Only, v2)

### Layout & Visuals
- Background root: `#feea00`; CRT scanlines/overlay from `frontend-spec.md`.
- Header: reuse v1 ASCII lettering in black on `#feea00`.
- Three regions:
  1) Left: Grid module canvas (world map and city overlays).
  2) Optional thin control strip (language/overlay/map toggle/export/import).
  3) Right: UI Generic Cards (inverted CRT card layout) for markdown display.

### Map & Overlay (Grid Module)
- Use the grid module from `v2/frontend-spec.md` for both world map and overlay views (canvas, pixelated, scanlines).
- World map: load data from backend (preferred: ascii_map.txt or hex list); hover/click selects hex -> fetch `/api/hex/:code?language=...`.
- Overlay view: same grid module; select overlay from list, render overlay grid; click overlay hex -> fetch `/api/city-overlay/:name/hex/:hexId` or `/api/city-overlay/:name`.
- Keyboard/mouse: WASD/arrow to pan/select; click selects; visible HUD styled per CRT spec.

### Detail Panel (Right Cards)
- Use UI Generic Cards from `frontend-spec.md` (inverted CRT, borders, scanlines).
- Show tabs: Raw Markdown | Styled View.
- Actions: Copy, Save locally, Refresh; show language and manifest version; error toasts minimal.

### Header & Controls
- Header banner = original ASCII in black on `#feea00`.
- Controls under header: language selector (`/api/languages`, `/api/set-language`), export/import buttons, bootstrap trigger, overlay selector, view toggle (world/overlay).

### Backend Endpoints (v2)
- `/api/health`, `/api/bootstrap`, `/api/hex/:code`, `/api/languages`, `/api/set-language`, `/api/export`, `/api/import`, `/api/city-overlays`, `/api/city-overlay/:name`, `/api/city-overlay/:name/ascii`, `/api/debug-cache` (manifest/version).
- Always pass `language`; cache/invalidate using manifest version from `/api/debug-cache`.

### Offline & Caching
- Service worker + IndexedDB: cache shell assets, ascii_map.txt (if present), fetched markdown (hex/overlay) keyed by manifest version.
- On load: bootstrap -> fetch manifest -> hydrate caches; offline: if missing, show “not cached”.

### Parity with v1 (simplified to markdown)
- Map click → detail; city overlay drill-down; language toggle; export/import; optional skull/bleed loading splash as a toggle.
- Maintain icon/legend semantics visually (cities, settlements, specials) even though backend serves markdown only.

### Styling Tokens
- Palette: `#feea00` background; black lettering for header; CRT accent `#00ff41` (per spec); monospace fonts.
- Reuse scanline/vignette/flicker overlays from `frontend-spec.md`.

