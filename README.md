# Hexy v2 (WIP)

This repository now holds two tracks:

- `v1/` – the original Hexy stack (backend, frontend, launcher). Use this for the legacy experience.
- `v2/` – a fresh backend-first rewrite focused on markdown-only delivery with boot-time caching and a simplified frontend spec.

## Status

- v2 backend skeleton is in place under `v2/backend/`.
- Generation logic and caching reuse are being ported from v1; endpoints are minimal during the transition.

## Running v2 backend (dev)

```bash
cd v2
python -m backend.app
```

Environment variables:

- `HEXY_OUTPUT_DIR` – optional override for generated output (defaults to `~/.local/share/hexy/dying_lands_output`).
- `HEXY_CACHE_DIR` – optional override for boot cache (Lambda defaults to `/tmp/hexy-cache`).
- `HEXY_PORT` – server port (default 6660).

## Where is v1?

Legacy docs, scripts, and code now live in `v1/` unchanged.

## Roadmap

The attached `hex.plan.md` tracks the v2 rollout: archive v1, rebuild backend with generation + /tmp cache, derive a slimmer frontend spec, then implement the new retro UI. Note: do not edit that plan file directly.

