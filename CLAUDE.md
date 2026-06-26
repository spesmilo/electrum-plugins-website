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

Each plugin is an `<article class="plugin-card">` with icon, name, description, and links. Plugins carry platform badges (`badge-qt` for Desktop, `badge-qml` for Android, `badge-cli` for CLI) indicating which platforms they support. Internal plugins (bundled with Electrum) carry a `badge-internal` badge labeled "Internal".

## Adding External Plugins

New external plugins go in the appropriate category section of `plugins.html` above the corresponding comment marker (`<!-- ADD NEW EXTERNAL DESKTOP PLUGIN ABOVE THIS LINE -->` or `<!-- ADD NEW EXTERNAL CLI PLUGIN ABOVE THIS LINE -->`). Plugin icons go in `assets/plugins/` (48x48+ PNG/SVG). See `CONTRIBUTING.md` for the full card template. Each plugin also needs a `plugin/{id}/index.html` share redirect page and an `assets/og/{id}.png` OG image (see CONTRIBUTING.md). After editing, regenerate the LLM/agent files: `python3 scripts/generate_llm_files.py` (see below).

## Social Sharing

Each plugin has a shareable URL at `plugin/{id}/` containing a lightweight redirect page with plugin-specific OpenGraph metadata. These pages redirect instantly to `plugins.html#{id}` via `<meta http-equiv="refresh">`. OG images are in `assets/og/{id}.png` (1200x630). A generation script lives at `scripts/generate_og_images.py`. When adding a new external plugin, also create a `plugin/{id}/index.html` redirect page and generate an OG image (see CONTRIBUTING.md).

## LLM & Crawler Discoverability

The site exposes machine-readable files so coding agents, LLMs, and crawlers can consume it:

- `robots.txt` — open to all crawlers (including AI bots); points to the sitemap
- `sitemap.xml` — every HTML page + every `plugin/{id}/` share page
- `llms.txt` — concise, link-first index in the [llmstxt.org](https://llmstxt.org) format
- `llms-full.txt` — full text of all site content flattened to Markdown (home, every plugin, the entire developer guide, contributing summary)

**These four files are generated, not hand-edited.** `scripts/generate_llm_files.py` parses `plugins.html` (plugin list), `developers.html` (dev guide), `index.html` (home), and `CONTRIBUTING.md` (contribution requirements) as the single sources of truth. It uses only the Python standard library (no dependencies) and is deterministic.

**Always regenerate after changing site content** — adding/editing/removing a plugin, or editing a page's text:

```bash
python3 scripts/generate_llm_files.py
```

Commit the regenerated `robots.txt`, `sitemap.xml`, `llms.txt`, and `llms-full.txt` alongside your changes.

If you add a **new top-level page** (a new root `.html`), add a row to the `PAGES` list in `scripts/generate_llm_files.py` so it's included in `sitemap.xml` and `llms.txt`, then regenerate.

> **Deployment note:** these are root-level files, so they must be listed in the `cp` block of `hosting/start.sh` (they already are). Any *new* root-level file you add must also be added there, or Caddy won't serve it.

## Key Files

- `css/style.css` — all styling (mobile-first responsive)
- `hosting/Caddyfile` — web server config
- `hosting/start.sh` — Docker build and deploy script (lists every file/dir copied into the served image)
- `hosting/Dockerfile` — Caddy 2 Alpine image
- `assets/plugins/` — plugin icons
- `developers.html` — plugin hooks reference, manifest.json schema, plugin dev guide
- `scripts/generate_llm_files.py` — generates `robots.txt`, `sitemap.xml`, `llms.txt`, `llms-full.txt`
- `scripts/generate_og_images.py` — generates per-plugin OG share images
- `robots.txt`, `sitemap.xml`, `llms.txt`, `llms-full.txt` — generated; see LLM & Crawler Discoverability
