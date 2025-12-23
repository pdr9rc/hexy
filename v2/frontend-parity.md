# v1 → v2 Frontend Logic Parity (markdown-first)

## Core flows
- Map view: v1 rendered grid + overlays → v2 fetches ascii/summary from generated outputs; per-hex fetch via `/api/hex/:code` returns markdown only.
- Language toggle: v1 JS toggled translations → v2 `/api/set-language` plus `/api/languages`; frontend sends `?language=` when fetching markdown.
- Overlays/cities/settlements: v1 used overlay analyzer; v2 serves pre-generated markdown files under `/api/city-overlay/:name` (+ `/ascii`) and `/api/city/:hex`, `/api/settlement/:hex` reading from generated output.
- Export/Import: v1 had zip export/import; v2 `/api/export`/`/api/import` with local-only semantics.
- Offline: reuse service-worker strategy; cache shell + fetched markdown; invalidate on generation manifest version.
- Editing: v1 could PUT hex; v2 keeps backend read-only markdown; edits are client-side saved/exported.

## Markdown fields to parse in UI
- Hex files: title, sections (Encounter, Denizen, Notable Feature, Atmosphere, Loot/Scroll), icons (⌂ ▲ ※ ☉ ≈) encoded in text.
- City/overlay files: name, grid notes; assume heading + section markers.
- Language: include `language` in responses; UI chooses markdown set.

## Gaps to watch
- Ensure generation writes overlay markdown/ASCII into per-language output.
- Confirm version/manifest exposed via `/api/debug-cache` for cache invalidation.
- Add client-side parsers to extract symbols/types from markdown (no server parsing).

