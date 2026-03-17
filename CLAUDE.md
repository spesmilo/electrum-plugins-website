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
- **Graphical User Interface** — Qt/QML GUI plugins (Audio MODEM, LabelSync, Revealer, etc.)
- **Daemon only** — CLI/Daemon plugins (SwapServer, Watchtower, etc.)
- **Hardware Wallets** — Trezor, Ledger, Coldcard, BitBox02, etc.

Each plugin is an `<article class="plugin-card">` with icon, name, description, and links. Plugins carry platform badges (`badge-qt` for Desktop, `badge-qml` for Android, `badge-cli` for CLI) indicating which platforms they support. External plugins also carry a `badge-external` badge.

## Adding External Plugins

New external plugins go in the appropriate category section of `plugins.html` above the corresponding comment marker (`<!-- ADD NEW EXTERNAL DESKTOP PLUGIN ABOVE THIS LINE -->` or `<!-- ADD NEW EXTERNAL CLI PLUGIN ABOVE THIS LINE -->`). Plugin icons go in `assets/plugins/` (48x48+ PNG/SVG). See `CONTRIBUTING.md` for the full card template.

## Key Files

- `css/style.css` — all styling (mobile-first responsive)
- `hosting/Caddyfile` — web server config
- `hosting/start.sh` — Docker build and deploy script
- `hosting/Dockerfile` — Caddy 2 Alpine image
- `assets/plugins/` — plugin icons
- `developers.html` — plugin hooks reference, manifest.json schema, plugin dev guide
