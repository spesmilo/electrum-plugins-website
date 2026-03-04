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

Find the comment `<!-- ADD NEW EXTERNAL PLUGIN ABOVE THIS LINE -->` in the External Plugins section and add a new plugin card **above** that line.

Use this template:

```html
<!-- Plugin Name -->
<article class="plugin-card">
  <img src="assets/plugins/plugin-default.svg" alt="PLUGIN_NAME icon" class="plugin-icon" loading="lazy" width="48" height="48">
  <div class="plugin-info">
    <h3 class="plugin-name">PLUGIN_NAME</h3>
    <p class="plugin-description">BRIEF_DESCRIPTION</p>
    <div class="plugin-meta">
      <span class="badge badge-PLATFORM">PLATFORM_LABEL</span>
      <span class="badge badge-external">External</span>
    </div>
    <a href="REPO_URL" class="plugin-link">View Repository</a>
    <p class="plugin-date">Added: MONTH YEAR</p>
  </div>
</article>
```

### 3. Fill in the fields

| Field | Description | Example |
|---|---|---|
| `PLUGIN_NAME` | Display name of your plugin | `My Plugin` |
| `BRIEF_DESCRIPTION` | One or two sentences describing functionality | `Enables automatic coin selection based on privacy heuristics.` |
| `PLATFORM` | The badge class and label for your plugin's GUI type (see below) | `qt` with label `Desktop` |
| `REPO_URL` | Full URL to your plugin's repository | `https://github.com/user/my-plugin` |
| `MONTH YEAR` | Current month and year | `March 2026` |

**Platform badge classes and labels:**
- `badge-qt` — Desktop GUI (label: `Desktop`)
- `badge-qml` — Android GUI (label: `Android`)
- `badge-cli` — Command-line / daemon plugin (label: `CLI`)

If your plugin supports multiple platforms, add multiple badge spans.

### 4. (Optional) Add a custom icon

If you want a custom icon instead of the default placeholder:

1. Add a PNG image (48x48 or larger, square) to `assets/plugins/`
2. Update the `<img src="...">` path in your plugin card

### 5. Open a pull request

- Title: `Add PLUGIN_NAME to external plugins`
- Description: Brief explanation of your plugin and a link to the repository

## Guidelines

- **One plugin per PR** — Submit separate PRs for separate plugins
- **No modifications to other plugins** — Only add your own entry
- **Keep descriptions factual** — Avoid marketing language; describe what the plugin does
- **External plugins are not endorsed** — Listing here does not imply review or endorsement by the Electrum developers

## Questions?

Open an issue in this repository if you have questions about the submission process.
