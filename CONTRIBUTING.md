# Contributing an External Plugin

Want to list your Electrum plugin on the plugins directory? Submit a pull request to this repository.

## Requirements

Before submitting, make sure your plugin meets these criteria:

1. **Working repository** — Your plugin must have a public Git repository with source code that builds and runs
2. **License** — Your plugin must have an open-source license (MIT, GPL, Apache, etc.)
3. **Description** — Provide a clear, concise description of what your plugin does
4. **Compatibility** — Your plugin must work with a recent version of Electrum (4.5+)
5. **manifest.json** — Your plugin repository must include a valid `manifest.json`

## How to Submit

### 1. Fork this repository

### 2. Edit `plugins.html`

Add a new plugin card to the appropriate category section(s) in `plugins.html`, **above** the corresponding comment marker:

- **Graphical User Interface** (Qt/QML GUI) — add above `<!-- ADD NEW EXTERNAL DESKTOP PLUGIN ABOVE THIS LINE -->`
- **Daemon only** (CLI/Daemon) — add above `<!-- ADD NEW EXTERNAL CLI PLUGIN ABOVE THIS LINE -->`

Use this template:

```html
<!-- Plugin Name -->
<article class="plugin-card" id="PLUGIN_ID">
  <a href="plugin/PLUGIN_ID/" class="plugin-share" title="Share this plugin" aria-label="Share PLUGIN_NAME plugin"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg></a>
  <img src="assets/plugins/plugin-default.svg" alt="PLUGIN_NAME icon" class="plugin-icon" loading="lazy" width="48" height="48">
  <div class="plugin-info">
    <h3 class="plugin-name">PLUGIN_NAME</h3>
    <p class="plugin-description">BRIEF_DESCRIPTION</p>
    <div class="plugin-meta">
      <span class="badge badge-qt">Desktop</span>
    </div>
    <a href="REPO_URL" class="plugin-link">View Repository</a>
  </div>
</article>
```

### 3. Add the correct platform badge

Replace or add the appropriate platform badge in the `plugin-meta` div:

| Badge class | Label | Use when |
|---|---|---|
| `badge-qt` | Desktop | Plugin has a Qt GUI |
| `badge-qml` | Android | Plugin has a QML GUI |
| `badge-cli` | CLI | Plugin is daemon/CLI only |

For example, a CLI-only plugin would use `<span class="badge badge-cli">CLI</span>` instead of the `badge-qt` shown in the template.

### 4. Fill in the fields

| Field | Description | Example |
|---|---|---|
| `PLUGIN_NAME` | Display name of your plugin | `My Plugin` |
| `BRIEF_DESCRIPTION` | One or two sentences describing functionality | `Enables automatic coin selection based on privacy heuristics.` |
| `REPO_URL` | Full URL to your plugin's repository | `https://github.com/user/my-plugin` |

### 5. (Optional) Add a custom icon

If you want a custom icon instead of the default placeholder:

1. Add a PNG image (48x48 or larger, square) to `assets/plugins/`
2. Update the `<img src="...">` path in your plugin card

### 6. Add a share page and OG image

Each plugin needs a share page for social media previews:

1. Create the directory `plugin/{your-plugin-id}/`
2. Create `plugin/{your-plugin-id}/index.html` using this template:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=../../plugins.html#PLUGIN_ID">
  <title>PLUGIN_NAME — Electrum Plugin</title>
  <meta property="og:title" content="PLUGIN_NAME — Electrum Plugin">
  <meta property="og:description" content="BRIEF_DESCRIPTION">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://plugins.electrum.org/plugin/PLUGIN_ID">
  <meta property="og:image" content="https://plugins.electrum.org/assets/og/PLUGIN_ID.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:alt" content="PLUGIN_NAME — Electrum Plugin">
  <meta property="og:site_name" content="Electrum Plugins">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="PLUGIN_NAME — Electrum Plugin">
  <meta name="twitter:description" content="BRIEF_DESCRIPTION">
  <meta name="twitter:image" content="https://plugins.electrum.org/assets/og/PLUGIN_ID.png">
  <link rel="canonical" href="https://plugins.electrum.org/plugins.html#PLUGIN_ID">
</head>
<body><p>Redirecting to <a href="../../plugins.html#PLUGIN_ID">PLUGIN_NAME</a>...</p></body>
</html>
```

3. Generate an OG image: `python3 scripts/generate_og_images.py` (requires Pillow). Or manually add a 1200x630 PNG to `assets/og/PLUGIN_ID.png`.

### 7. Open a pull request

- Title: `Add PLUGIN_NAME to external plugins`
- Description: Brief explanation of your plugin and a link to the repository

## Guidelines

- **One plugin per PR** — Submit separate PRs for separate plugins
- **No modifications to other plugins** — Only add your own entry
- **Keep descriptions factual** — Avoid marketing language; describe what the plugin does
- **External plugins are not endorsed** — Listing here does not imply review or endorsement by the Electrum developers

## Questions?

Open an issue in this repository if you have questions about the submission process.
