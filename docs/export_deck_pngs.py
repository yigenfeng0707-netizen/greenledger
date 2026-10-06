#!/usr/bin/env python3
"""Rasterize docs/greenledger-deck.pdf to 1920x1080 PNGs for the demo video."""

from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "docs" / "greenledger-deck.pdf"
OUT = ROOT / "assets" / "deck-slides"


def main() -> None:
    if not PDF.exists():
        raise SystemExit(f"missing {PDF}; run docs/build_deck.py then soffice convert")
    OUT.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF)
    for i, page in enumerate(doc, start=1):
        zoom_x = 1920 / page.rect.width
        zoom_y = 1080 / page.rect.height
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom_x, zoom_y), alpha=False)
        dest = OUT / f"slide-{i:02d}.png"
        pix.save(dest)
        print(dest.name, pix.width, pix.height, dest.stat().st_size)
    print("pages", doc.page_count)


if __name__ == "__main__":
    main()
