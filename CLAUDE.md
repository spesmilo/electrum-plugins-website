# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Static website for the Electrum Bitcoin wallet plugins directory (plugins.electrum.org). Pure HTML/CSS with no JavaScript, no build system, and no package manager. Serves 3 pages: home (`index.html`), plugin directory (`plugins.html`), and developer guide (`developers.html`).

**Docker deployment:**
```bash
cd hosting && ./start.sh
```
This builds a Caddy 2 Alpine image, copies site files, and runs on port 80.

## Architecture

- **No build step** — edit HTML/CSS directly, no transpilation or bundling
- **No client-side JS** — hamburger menu uses CSS checkbox trick
- **CSS variables** in `css/style.css` control theming (colors, typography, spacing)
- **Responsive breakpoints**: mobile <768px, tablet ≥768px (2-col), desktop ≥1024px (3-col)
- **Hosting**: Docker → Caddy 2 with gzip, security headers (X-Frame-Options DENY, nosniff, no-referrer)

## Content Structure

`plugins.html` contains 3 plugin categories:
- **Utility plugins**  — LabelSync, NWC, Audio MODEM, Revealer, etc.
- **Hardware wallets** — Trezor, Ledger, Coldcard, BitBox02, etc.
- **External plugins** — community-contributed, added via PR

Each plugin is an `<article class="plugin-card">` with icon, name, description, platform badges, and links.

## Adding External Plugins

New external plugins go in `plugins.html` above the `<!-- ADD NEW EXTERNAL PLUGIN ABOVE THIS LINE -->` comment. Platform badge classes: `badge-qt` (Desktop), `badge-qml` (Android), `badge-cli` (CLI). Plugin icons go in `assets/plugins/` (48x48+ PNG/SVG). See `CONTRIBUTING.md` for the full card template.

## Key Files

- `css/style.css` — all styling (884 lines, mobile-first responsive)
- `hosting/Caddyfile` — web server config
- `hosting/start.sh` — Docker build and deploy script
- `hosting/Dockerfile` — Caddy 2 Alpine image
- `assets/plugins/` — plugin icons
- `developers.html` — plugin hooks reference, manifest.json schema, plugin dev guide
