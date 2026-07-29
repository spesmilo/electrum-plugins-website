#!/usr/bin/env python3
"""Generate branded OG images for each plugin.

Usage: python3 scripts/generate_og_images.py

Requires: Pillow, rsvg-convert (for SVG icons), fonts-dejavu-core
Outputs: assets/og/{plugin-id}.png (1200x630 each)
"""

import io
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = REPO_ROOT / "assets"
OG_DIR = ASSETS_DIR / "og"
PLUGIN_ICONS_DIR = ASSETS_DIR / "plugins"
ELECTRUM_LOGO = ASSETS_DIR / "icons" / "electrum_darkblue.svg"

WIDTH, HEIGHT = 1200, 630
BG_COLOR = (26, 58, 92)        # #1a3a5c
BG_INNER = (30, 45, 61)        # #1e2d3d (subtle inner area)
ACCENT_COLOR = (74, 158, 255)  # #4a9eff
TEXT_COLOR = (220, 230, 240)
SUBTEXT_COLOR = (140, 160, 180)
ICON_BG = (240, 244, 248)      # #f0f4f8
MARGIN = 40

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# All plugins: (id, display_name, icon_filename_or_None)
PLUGINS = [
    ("audio-modem", "Audio MODEM", "speaker.svg"),
    ("labelsync", "LabelSync", "labelsync.png"),
    ("nostr-cosigner", "Nostr Cosigner", "nostr_multisig.png"),
    ("nostr-wallet-connect", "Nostr Wallet Connect", "nwc.png"),
    ("revealer", "Revealer", "revealer.png"),
    ("timelock-recovery", "Timelock Recovery", "timelock_recovery_60.png"),
    ("two-factor-authentication", "Two Factor Authentication", "trustedcoin-status.png"),
    ("bitcoin-after-life", "Bitcoin After Life", "bal.svg"),
    ("guardian", "Guardian", "guardian.svg"),
    ("joinstr", "Joinstr", "joinstr.svg"),
    ("ln-graph-visualizer", "LN Graph Visualizer", "ln-graph-visualizer.png"),
    ("clink", "CLINK Plugin", "clink.svg"),
    ("silent-payments-sender", "Silent Payments Sender", "silent-payments-sender.svg"),
    ("electrum-personal-server", "Electrum Personal Server", "electrum-personal-server.svg"),
    ("swapserver-gui", "SwapServer GUI", "swapserver-gui.svg"),
    ("swapserver", "SwapServer", None),  # emoji icon, no file
    ("watchtower", "Watchtower", "watchtower.svg"),
    ("lnurl-server", "LNURL Server", "lnurl-server.svg"),
    ("notary", "Notary", "notary.svg"),
    ("payserver", "PayServer", "payserver.svg"),
    ("bitbox02", "BitBox02", "bitbox02.png"),
    ("coldcard", "Coldcard", "coldcard.png"),
    ("digital-bitbox", "Digital Bitbox", "digitalbitbox.png"),
    ("jade", "Jade", "jade.png"),
    ("keepkey", "KeepKey", "keepkey.png"),
    ("ledger", "Ledger", "ledger.png"),
    ("safe-t-mini", "Safe-T mini", "safe-t.png"),
    ("trezor", "Trezor", "trezor.png"),
]


def svg_to_png(svg_path, size):
    """Convert SVG to PNG at given size using rsvg-convert."""
    result = subprocess.run(
        ["rsvg-convert", "-w", str(size), "-h", str(size), str(svg_path)],
        check=True, capture_output=True,
    )
    return Image.open(io.BytesIO(result.stdout)).convert("RGBA")


def load_icon(filename, size=120):
    """Load and resize a plugin icon."""
    if filename is None:
        return None
    path = PLUGIN_ICONS_DIR / filename
    try:
        if path.suffix.lower() == ".svg":
            img = svg_to_png(path, size)
        else:
            img = Image.open(path).convert("RGBA")
            img = img.resize((size, size), Image.LANCZOS)
        return img
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"  Warning: icon {path} failed ({e}), skipping icon")
        return None


def load_electrum_logo(size=48):
    """Load the Electrum logo SVG as PNG."""
    try:
        return svg_to_png(ELECTRUM_LOGO, size)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def generate_og_image(plugin_id, name, icon_filename, fonts, logo):
    """Generate a single OG image."""
    font_name, font_subtitle, font_footer = fonts
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw.rectangle(
        [MARGIN, MARGIN, WIDTH - MARGIN, HEIGHT - MARGIN],
        fill=BG_INNER,
    )

    icon_size = 120
    icon_box_size = 140
    icon_box_radius = 12
    icon = load_icon(icon_filename, icon_size)

    if icon:
        icon_box_x = (WIDTH - icon_box_size) // 2
        icon_box_y = 120
        draw.rounded_rectangle(
            [icon_box_x, icon_box_y,
             icon_box_x + icon_box_size, icon_box_y + icon_box_size],
            radius=icon_box_radius,
            fill=ICON_BG,
        )
        icon_x = icon_box_x + (icon_box_size - icon_size) // 2
        icon_y = icon_box_y + (icon_box_size - icon_size) // 2
        img.paste(icon, (icon_x, icon_y), icon)
        text_y_start = icon_box_y + icon_box_size + 40
    else:
        text_y_start = 180

    name_bbox = draw.textbbox((0, 0), name, font=font_name)
    name_w = name_bbox[2] - name_bbox[0]
    name_x = (WIDTH - name_w) // 2
    draw.text((name_x, text_y_start), name, fill=TEXT_COLOR, font=font_name)

    subtitle = "Electrum Plugin"
    sub_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_x = (WIDTH - sub_w) // 2
    sub_y = text_y_start + (name_bbox[3] - name_bbox[1]) + 16
    draw.text((sub_x, sub_y), subtitle, fill=SUBTEXT_COLOR, font=font_subtitle)

    url_text = "plugins.electrum.org"
    url_bbox = draw.textbbox((0, 0), url_text, font=font_footer)
    url_w = url_bbox[2] - url_bbox[0]

    if logo:
        logo_w = logo.width
        total_w = logo_w + 8 + url_w
        start_x = (WIDTH - total_w) // 2
        logo_y = HEIGHT - MARGIN - logo_w - 16
        img.paste(logo, (start_x, logo_y), logo)
        draw.text(
            (start_x + logo_w + 8, logo_y + 6),
            url_text, fill=SUBTEXT_COLOR, font=font_footer,
        )
    else:
        url_x = (WIDTH - url_w) // 2
        draw.text(
            (url_x, HEIGHT - MARGIN - 30),
            url_text, fill=SUBTEXT_COLOR, font=font_footer,
        )

    draw.rectangle([MARGIN, MARGIN, WIDTH - MARGIN, MARGIN + 3], fill=ACCENT_COLOR)

    out_path = OG_DIR / f"{plugin_id}.png"
    img.save(out_path, "PNG", optimize=True)
    print(f"  Generated: {out_path.relative_to(REPO_ROOT)}")


def main():
    OG_DIR.mkdir(parents=True, exist_ok=True)

    # Load fonts and logo once, reuse across all images
    fonts = (
        ImageFont.truetype(FONT_BOLD, 48),
        ImageFont.truetype(FONT_REGULAR, 24),
        ImageFont.truetype(FONT_REGULAR, 18),
    )
    logo = load_electrum_logo(32)

    print(f"Generating {len(PLUGINS)} OG images...")
    for plugin_id, name, icon_filename in PLUGINS:
        generate_og_image(plugin_id, name, icon_filename, fonts, logo)
    print("Done.")


if __name__ == "__main__":
    main()
