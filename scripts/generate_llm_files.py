#!/usr/bin/env python3
"""Generate LLM / AI-agent discoverability files for plugins.electrum.org.

Outputs (written to the repo root, committed, and served as static files):

    robots.txt      Crawler policy (open to all, incl. AI bots) + sitemap pointer.
    sitemap.xml     Every HTML page + every plugin share page.
    llms.txt        Concise, link-first index in the llmstxt.org format.
    llms-full.txt   Full text of all site content flattened to Markdown.

Single sources of truth (parsed, never hand-duplicated):

    plugins.html      the plugin list (the part that changes most often)
    developers.html   the plugin development guide
    index.html        the home page (tagline, "Enabling Plugins" steps)
    CONTRIBUTING.md   the external-plugin contribution requirements

The script uses only the Python standard library (no Pillow / no third-party
deps, unlike generate_og_images.py) and is deterministic: the same inputs always
produce byte-identical output (no timestamps), so re-running never creates noise.

Run it after adding or editing a plugin or a page:

    python3 scripts/generate_llm_files.py
"""

import html as htmllib
import re
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://plugins.electrum.org"
REPO_HTML = "https://github.com/spesmilo/electrum-plugins-website"
CONTRIB_URL = f"{REPO_HTML}/blob/master/CONTRIBUTING.md"

SITE_NAME = "Electrum Plugins"
SUMMARY = (
    "Directory of plugins for the Electrum Bitcoin wallet — utility plugins, "
    "hardware-wallet integrations, and community extensions — plus a developer "
    "guide for building and distributing your own plugins."
)
INTRO = (
    "This site lists plugins for the Electrum Bitcoin wallet (enabled via "
    "Tools → Plugins) across desktop (Qt), Android (QML), and "
    "command-line/daemon interfaces, including hardware-wallet integrations, and "
    "documents how to build, package, and distribute your own plugin. Plugins "
    "marked \"Internal\" ship with Electrum; all others are third-party and are "
    "not reviewed or endorsed by the Electrum developers."
)

# plugins.html category section id -> human-readable heading.
CATEGORIES = [
    ("desktop", "Graphical User Interface"),
    ("daemon", "Daemon only"),
    ("hardware", "Hardware Wallets"),
]

# Top-level HTML pages: (source file, URL path under BASE_URL, label, sitemap priority).
# Add a row here when you add a new top-level page so it lands in sitemap.xml and llms.txt.
PAGES = [
    ("index.html", "", "Home", "1.0"),
    ("plugins.html", "plugins.html", "Plugin directory", "0.8"),
    ("developers.html", "developers.html", "Developer guide", "0.8"),
]


# --------------------------------------------------------------------------- #
# plugins.html parser: extract plugin cards grouped by category.
# --------------------------------------------------------------------------- #
class PluginParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.by_cat = {cid: [] for cid, _ in CATEGORIES}
        self._cat = None
        self._cur = None
        self._field = None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = a.get("class", "").split()
        if tag == "section" and a.get("id") in self.by_cat:
            self._cat = a.get("id")
        elif tag == "article" and "plugin-card" in classes:
            self._cur = {
                "id": a.get("id", ""),
                "name": "",
                "description": "",
                "platforms": [],
                "internal": False,
                "link": None,
                "link_label": None,
            }
        elif self._cur is not None and self._field is None:
            if tag == "h3" and "plugin-name" in classes:
                self._field, self._buf = "name", []
            elif tag == "p" and "plugin-description" in classes:
                self._field, self._buf = "description", []
            elif tag == "span" and "badge" in classes:
                self._field, self._buf = "badge", []
            elif tag == "a" and "plugin-link" in classes:
                self._cur["link"] = a.get("href")
                self._field, self._buf = "link", []

    def handle_data(self, data):
        if self._field is not None:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if self._cur is not None and self._field is not None:
            text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if self._field == "name":
                self._cur["name"] = text
            elif self._field == "description":
                self._cur["description"] = text
            elif self._field == "badge":
                if text.lower() == "internal":
                    self._cur["internal"] = True
                elif text:
                    self._cur["platforms"].append(text)
            elif self._field == "link":
                self._cur["link_label"] = text
            self._field, self._buf = None, []
        if tag == "article" and self._cur is not None:
            if self._cat:
                self.by_cat[self._cat].append(self._cur)
            self._cur = None


def parse_plugins(path):
    p = PluginParser()
    p.feed(path.read_text(encoding="utf-8"))
    return p.by_cat


# --------------------------------------------------------------------------- #
# Minimal HTML -> Markdown converter for a single rooted region of a page.
# --------------------------------------------------------------------------- #
_HEADINGS = {f"h{i}": i for i in range(1, 7)}


class Markdown(HTMLParser):
    """Convert the content of one element (matched by tag + id/class) to Markdown.

    Handles headings, paragraphs, ordered/unordered lists, <pre><code> blocks,
    tables, images, and inline code/strong/em/links. `<div class="disclaimer">`
    becomes a blockquote. With capture_root_inline the matched element's own
    inline content is captured directly (used for standalone note blocks).
    """

    def __init__(self, root_tag, attr, value, heading_offset=0,
                 capture_root_inline=False):
        super().__init__(convert_charrefs=True)
        self.root_tag, self.attr, self.value = root_tag, attr, value
        self.heading_offset = heading_offset
        self.capture_root_inline = capture_root_inline
        self.active = False
        self.depth = 0
        self.blocks = []
        self.inline = None
        self.mode = None
        self.h_level = 0
        self.links = []
        self.list_stack = []
        self.list_lines = []
        self.in_pre = False
        self.pre = []
        self.in_table = False
        self.rows = []
        self.row = None
        self.row_header = False

    # -- helpers -----------------------------------------------------------
    def _match(self, tag, a):
        if tag != self.root_tag:
            return False
        v = a.get(self.attr, "")
        return self.value in v.split() if self.attr == "class" else v == self.value

    def _begin_inline(self, mode):
        self.inline, self.mode = [], mode

    def _finish_inline(self):
        text = "".join(self.inline) if self.inline is not None else ""
        self.inline, self.mode = None, None
        return re.sub(r"[ \t\f\v]*\n[ \t\f\v\n]*", " ", text).strip()

    def _ins(self, s):
        if self.inline is not None:
            self.inline.append(s)

    def _block(self, s):
        if s:
            self.blocks.append(s)

    def _abs(self, href):
        if not href or href.startswith(("http://", "https://", "mailto:", "#")):
            return href
        return f"{BASE_URL}/{href.lstrip('/')}"

    # -- parser callbacks --------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if not self.active:
            if self._match(tag, a):
                self.active = True
                self.depth = 1
                if self.capture_root_inline:
                    self._begin_inline("blockquote")
            return
        if tag == self.root_tag:
            self.depth += 1
        self._start(tag, a)

    def handle_endtag(self, tag):
        if not self.active:
            return
        if tag == self.root_tag:
            self.depth -= 1
            if self.depth == 0:
                if self.capture_root_inline:
                    self._block("> " + self._finish_inline())
                self.active = False
                return
        self._end(tag)

    def handle_data(self, data):
        if not self.active:
            return
        if self.in_pre:
            self.pre.append(data)
        elif self.inline is not None:
            self.inline.append(data)

    # -- element handling --------------------------------------------------
    def _start(self, tag, a):
        if self.in_pre:
            return
        classes = a.get("class", "").split()
        if tag == "pre":
            self.in_pre, self.pre = True, []
        elif tag in _HEADINGS:
            self._begin_inline("h")
            self.h_level = _HEADINGS[tag]
        elif tag == "p":
            self._begin_inline("p")
        elif tag in ("ul", "ol"):
            self.list_stack.append([tag, 0])
        elif tag == "li":
            if self.list_stack:
                self.list_stack[-1][1] += 1
            self._begin_inline("li")
        elif tag == "table":
            self.in_table, self.rows = True, []
        elif tag == "tr":
            self.row, self.row_header = [], False
        elif tag in ("th", "td"):
            if tag == "th":
                self.row_header = True
            self._begin_inline("cell")
        elif tag == "div" and "disclaimer" in classes:
            self._begin_inline("blockquote")
        elif tag == "code":
            self._ins("`")
        elif tag in ("strong", "b"):
            self._ins("**")
        elif tag in ("em", "i"):
            self._ins("*")
        elif tag == "a":
            self.links.append(a.get("href", ""))
            self._ins("[")
        elif tag == "img":
            alt = re.sub(r"\s+", " ", a.get("alt", "")).strip()
            self._block(f"![{alt}]({self._abs(a.get('src', ''))})")

    def _end(self, tag):
        if self.in_pre:
            if tag == "pre":
                code = "".join(self.pre).strip("\n")
                self._block("```\n" + code + "\n```")
                self.in_pre, self.pre = False, []
            return
        if tag in _HEADINGS:
            lvl = min(6, self.h_level + self.heading_offset)
            self._block("#" * lvl + " " + self._finish_inline())
        elif tag == "p":
            self._block(self._finish_inline())
        elif tag in ("ul", "ol"):
            if self.list_stack:
                self.list_stack.pop()
            if not self.list_stack:
                self._block("\n".join(self.list_lines))
                self.list_lines = []
        elif tag == "li":
            text = self._finish_inline()
            depth = max(0, len(self.list_stack) - 1)
            lst = self.list_stack[-1] if self.list_stack else ["ul", 1]
            marker = f"{lst[1]}. " if lst[0] == "ol" else "- "
            self.list_lines.append("  " * depth + marker + text)
        elif tag in ("th", "td"):
            self.row.append(self._finish_inline())
        elif tag == "tr":
            if self.row is not None:
                self.rows.append((self.row_header, self.row))
            self.row = None
        elif tag == "table":
            self._emit_table()
            self.in_table, self.rows = False, []
        elif tag == "a":
            href = self._abs(self.links.pop()) if self.links else ""
            self._ins(f"]({href})")
        elif tag == "code":
            self._ins("`")
        elif tag in ("strong", "b"):
            self._ins("**")
        elif tag in ("em", "i"):
            self._ins("*")
        elif tag == "div" and self.mode == "blockquote":
            self._block("> " + self._finish_inline())

    def _emit_table(self):
        if not self.rows:
            return
        header, body = None, []
        for is_h, cells in self.rows:
            if is_h and header is None:
                header = cells
            else:
                body.append(cells)
        if header is None and body:
            header = body.pop(0)
        if not header:
            return
        n = len(header)

        def fmt(cells):
            cells = [c.replace("|", "\\|") for c in cells] + [""] * (n - len(cells))
            return "| " + " | ".join(cells[:n]) + " |"

        lines = [fmt(header), "| " + " | ".join(["---"] * n) + " |"]
        lines += [fmt(r) for r in body]
        self._block("\n".join(lines))

    def markdown(self):
        return "\n\n".join(b for b in self.blocks if b.strip())


def html_to_md(path, root_tag, attr, value, **kw):
    m = Markdown(root_tag, attr, value, **kw)
    m.feed(path.read_text(encoding="utf-8"))
    return m.markdown()


# --------------------------------------------------------------------------- #
# Small <head> helpers and CONTRIBUTING.md requirement extraction.
# --------------------------------------------------------------------------- #
def page_meta(path):
    text = path.read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", text, re.S)
    desc = re.search(r'<meta\s+name="description"\s+content="(.*?)"', text, re.S)
    t = htmllib.unescape(title.group(1).strip()) if title else ""
    d = htmllib.unescape(desc.group(1).strip()) if desc else ""
    return t, d


def contributing_requirements(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    out, capturing = [], False
    for line in lines:
        if line.strip().lower() == "## requirements":
            capturing = True
            continue
        if capturing:
            if line.startswith("## "):
                break
            if re.match(r"\s*\d+\.\s", line):
                out.append(line.strip())
    return out


# --------------------------------------------------------------------------- #
# Plugin presentation helpers.
# --------------------------------------------------------------------------- #
def plugin_anchor(p):
    return f"{BASE_URL}/plugins.html#{p['id']}"


def platforms_str(p):
    return ", ".join(p["platforms"]) if p["platforms"] else "n/a"


def distribution_str(p):
    return "Internal (bundled with Electrum)" if p["internal"] else "External (third-party)"


# --------------------------------------------------------------------------- #
# File builders.
# --------------------------------------------------------------------------- #
AI_BOTS = [
    "GPTBot", "ChatGPT-User", "OAI-SearchBot",      # OpenAI
    "ClaudeBot", "Claude-User", "Claude-SearchBot", "anthropic-ai",  # Anthropic
    "Google-Extended",                               # Google AI
    "PerplexityBot", "Perplexity-User",              # Perplexity
    "CCBot",                                          # Common Crawl
    "Bytespider",                                     # ByteDance
    "Amazonbot", "Applebot", "Applebot-Extended",    # Amazon / Apple
    "Meta-ExternalAgent", "cohere-ai",               # Meta / Cohere
]


def build_robots():
    lines = [
        "# robots.txt for plugins.electrum.org",
        "#",
        "# This site is intentionally open to search engines, AI crawlers, and",
        "# coding agents. Machine-readable summaries for LLMs are available at:",
        "#   /llms.txt       concise, link-first index",
        "#   /llms-full.txt  full text of every page",
        "",
        "User-agent: *",
        "Disallow:",
        "",
        "# AI / LLM crawlers and assistants are explicitly welcome.",
    ]
    for bot in AI_BOTS:
        lines += [f"User-agent: {bot}", "Disallow:", ""]
    lines.append(f"Sitemap: {BASE_URL}/sitemap.xml")
    return "\n".join(lines) + "\n"


def build_sitemap(by_cat):
    urls = [(f"{BASE_URL}/{path}", pri) for _, path, _, pri in PAGES]
    for cid, _ in CATEGORIES:
        for p in by_cat[cid]:
            urls.append((f"{BASE_URL}/plugin/{p['id']}/", "0.5"))
    body = "\n".join(
        f"  <url><loc>{loc}</loc><priority>{pri}</priority></url>"
        for loc, pri in urls
    )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f"{body}\n</urlset>\n")
    return xml, len(urls)


def build_llms_txt(by_cat, descs):
    out = [f"# {SITE_NAME}", "", f"> {SUMMARY}", "", INTRO, "", "## Pages"]
    for src, path, label, _ in PAGES:
        out.append(f"- [{label}]({BASE_URL}/{path}): {descs[src]}")
    for cid, label in CATEGORIES:
        out += ["", f"## {label} plugins"]
        for p in by_cat[cid]:
            tail = f" ({platforms_str(p)}; {'internal' if p['internal'] else 'external'}"
            if p["link"]:
                tail += f"; source: {p['link']}"
            tail += ")"
            out.append(f"- [{p['name']}]({plugin_anchor(p)}): {p['description']}{tail}")
    out += ["", "## Optional",
            f"- [Full site content (llms-full.txt)]({BASE_URL}/llms-full.txt): "
            "Complete Markdown text of every page for deep context.",
            f"- [Contributing guide]({CONTRIB_URL}): How to submit an external plugin.",
            "- [Electrum source code](https://github.com/spesmilo/electrum)",
            f"- [Website source code]({REPO_HTML})",
            "- [electrum.org](https://electrum.org)"]
    return "\n".join(out) + "\n"


def build_llms_full(by_cat, paths):
    index_html, plugins_html, developers_html, contributing_md = paths
    out = [f"# {SITE_NAME} — full site content", "", f"> {SUMMARY}", "",
           "This file concatenates the full text of every page on "
           "plugins.electrum.org as Markdown, for LLMs and coding agents that "
           "want complete context in a single fetch. A concise index lives at "
           f"{BASE_URL}/llms.txt.", "",
           "## About", "", INTRO]

    enabling = html_to_md(index_html, "div", "class", "quick-start")
    if enabling:
        out += ["", enabling]

    out += ["", "## Plugin directory", "",
            "Plugins marked Internal ship with Electrum and are enabled from "
            "Tools → Plugins. All other plugins are third-party: they are "
            "not reviewed or endorsed by the Electrum developers, so verify the "
            "source before installing."]
    for cid, label in CATEGORIES:
        out += ["", f"### {label}"]
        for p in by_cat[cid]:
            out += ["", f"#### {p['name']}", "", p["description"], "",
                    f"- Platforms: {platforms_str(p)}",
                    f"- Distribution: {distribution_str(p)}",
                    f"- Page: {plugin_anchor(p)}"]
            if p["link"]:
                out.append(f"- {p['link_label'] or 'Link'}: {p['link']}")

    dev = html_to_md(developers_html, "div", "class", "dev-content", heading_offset=1)
    out += ["", "## Plugin development guide", "", dev]

    reqs = contributing_requirements(contributing_md)
    out += ["", "## Contributing a plugin", "",
            "External plugins are added by opening a pull request against the "
            "website repository. Summary of requirements:"]
    if reqs:
        out += ["", *[f"{r}" for r in reqs]]
    out += ["", f"Full contribution guide: {CONTRIB_URL}"]
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------- #
# Entry point.
# --------------------------------------------------------------------------- #
def main():
    index_html = REPO_ROOT / "index.html"
    plugins_html = REPO_ROOT / "plugins.html"
    developers_html = REPO_ROOT / "developers.html"
    contributing_md = REPO_ROOT / "CONTRIBUTING.md"

    by_cat = parse_plugins(plugins_html)
    n_plugins = sum(len(v) for v in by_cat.values())
    descs = {src: page_meta(REPO_ROOT / src)[1] for src, _, _, _ in PAGES}

    robots = build_robots()
    sitemap, n_urls = build_sitemap(by_cat)
    llms = build_llms_txt(by_cat, descs)
    llms_full = build_llms_full(
        by_cat, (index_html, plugins_html, developers_html, contributing_md))

    (REPO_ROOT / "robots.txt").write_text(robots, encoding="utf-8")
    (REPO_ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (REPO_ROOT / "llms.txt").write_text(llms, encoding="utf-8")
    (REPO_ROOT / "llms-full.txt").write_text(llms_full, encoding="utf-8")

    print(f"Wrote robots.txt ({len(AI_BOTS)} named AI bots, all allowed)")
    print(f"Wrote sitemap.xml ({n_urls} urls)")
    print(f"Wrote llms.txt ({n_plugins} plugins)")
    print(f"Wrote llms-full.txt ({n_plugins} plugins + dev guide)")


if __name__ == "__main__":
    main()
