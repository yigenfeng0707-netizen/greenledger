#!/usr/bin/env python3
"""Build the 10-slide English judge deck (PPTX + PDF) from proposal facts.

Run from repo root:
    python docs/build_deck.py
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT_PPTX = ROOT / "docs" / "greenledger-deck.pptx"
NAVY = RGBColor(0x0B, 0x1F, 0x33)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CREAM = RGBColor(0xF4, 0xF1, 0xEA)
INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x5C, 0x67, 0x70)
ACCENT = RGBColor(0x1B, 0x6B, 0x4A)
GOLD = RGBColor(0xC4, 0x8A, 0x2B)


def _set_run(run, text, size=18, bold=False, color=INK, font="Calibri"):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font


def _fill(shape, rgb):
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb
    shape.line.fill.background()


def _blank(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = CREAM
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.18), prs.slide_height)
    _fill(bar, ACCENT)
    return slide


def _box(slide, l, t, w, h, text, *, size=18, bold=False, color=INK, align=PP_ALIGN.LEFT, font="Calibri"):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    _set_run(run, text, size, bold, color, font)
    return tb


def _ensure_run(p):
    if p.runs:
        return p.runs[0]
    return p.add_run()


def add_title_block(slide, kicker, title, subtitle=None):
    _box(slide, Inches(0.55), Inches(0.28), Inches(12.2), Inches(0.35), kicker, size=12, bold=True, color=ACCENT)
    _box(slide, Inches(0.55), Inches(0.55), Inches(12.2), Inches(1.15), title, size=32, bold=True, color=NAVY)
    if subtitle:
        _box(slide, Inches(0.55), Inches(1.55), Inches(12.2), Inches(0.55), subtitle, size=16, color=MUTED)


def bullets(slide, items, top=2.2, left=0.55, width=12.2, size=18):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = 0
        p.space_after = Pt(10)
        run = _ensure_run(p)
        _set_run(run, "•  " + item, size=size, color=INK)
    return tb


def build() -> Path:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # 1 title
    s = _blank(prs)
    _box(s, Inches(0.55), Inches(1.6), Inches(12), Inches(0.4), "GOOGLE CLOUD AI BUILDER CUP 2026", size=14, bold=True, color=ACCENT)
    _box(s, Inches(0.55), Inches(2.1), Inches(12.2), Inches(1.4), "GreenLedger", size=54, bold=True, color=NAVY, font="Calibri")
    _box(
        s,
        Inches(0.55),
        Inches(3.5),
        Inches(12),
        Inches(1.1),
        "An auditable ESG disclosure agent for JAPAC SMEs.\nMessy bills in. Cited IFRS S2 draft out.",
        size=22,
        color=INK,
    )
    _box(
        s,
        Inches(0.55),
        Inches(5.2),
        Inches(12),
        Inches(1.4),
        "Track: Sustainability & Social Impact    ·    Team GreenLedger\nJudging: Technical 40%  ·  Impact 25%  ·  Innovation 25%  ·  UX 10%",
        size=16,
        color=MUTED,
    )

    # 2 problem
    s = _blank(prs)
    add_title_block(s, "01  /  PROBLEM", "Climate disclosure is now a supply-chain tax on SMEs")
    bullets(
        s,
        [
            "SGX, HKEX, SSBJ and AASB S2 push IFRS S2-aligned reporting from FY2025 — then buyers push it down the chain.",
            "A consulting-led GHG inventory still costs thousands of dollars and weeks. SMEs do not have ERP feeds.",
            "They have a shoebox: electricity bills, diesel logs, flight CSVs, waste memos, commute surveys.",
            "If the SME cannot produce a cited inventory, the listed buyer cannot defend Scope 3.",
            "The gap is not another chatbot. It is turning messy source documents into numbers a reviewer can trace.",
        ],
        top=2.25,
    )

    # 3 solution
    s = _blank(prs)
    add_title_block(s, "02  /  SOLUTION", "Six agents. Human in the loop. Not a chat window.")
    steps = [
        ("1 Ingestion", "Gemini multimodal extract + verbatim excerpt"),
        ("2 Review", "Confirm, edit or reject before totals"),
        ("3 Mapping", "Select a curated factor — never invent one"),
        ("4 Gaps", "IFRS S2 / GHG Protocol holes, capped at six"),
        ("5 Draft", "Disclosure markdown with [A#] citations"),
        ("6 Ask", "Grounded assurance Q&A, cited answers"),
    ]
    for i, (h, b) in enumerate(steps):
        col, row = i % 3, i // 3
        x, y = Inches(0.55 + col * 4.15), Inches(2.25 + row * 2.25)
        card = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Inches(3.95), Inches(2.05))
        _fill(card, WHITE)
        card.line.color.rgb = RGBColor(0xD8, 0xD2, 0xC8)
        _box(s, x + Inches(0.2), y + Inches(0.25), Inches(3.55), Inches(0.5), h, size=18, bold=True, color=ACCENT)
        _box(s, x + Inches(0.2), y + Inches(0.8), Inches(3.55), Inches(1.0), b, size=15, color=INK)

    # 4 architecture
    s = _blank(prs)
    add_title_block(s, "03  /  ARCHITECTURE", "Fail-closed mapping + an append-only audit trail")
    bullets(
        s,
        [
            "FastAPI agents in pipeline.py; orchestration, IDs, totals in orchestrator.py.",
            "React / Vite six-step UI: Upload → Review → Emissions → Gaps → Report → Ask.",
            "Factor library is bundled JSON (illustrative EPA/DEFRA-style). Unknown factor_id is dropped.",
            "Default activity status is pending. Rejected rows never enter totals.",
            "Claim is narrow: audit-grade draft — not a certified verification opinion.",
            "Offline Mock mode if no GEMINI_API_KEY; live Gemini when a key is set.",
        ],
        top=2.2,
        size=17,
    )

    # 5 technical
    s = _blank(prs)
    add_title_block(s, "04  /  TECHNICAL  40%", "Why Gemini and Google Cloud")
    bullets(
        s,
        [
            "Multimodal structured extraction: text, CSV, PDF and image bytes → JSON schema, not free prose.",
            "Constrained tool-use: the model may pick a factor_id that exists. Invented IDs never land in the inventory.",
            "Reproducible line: quantity × cited factor. Click [A#] to the source excerpt.",
            "Intended runtime: Cloud Run in asia-southeast1; Gemini key in Secret Manager.",
            "Honest status (6 Oct 2026): project greenledger-aibc is active but billing is off — no public URL yet.",
        ],
        top=2.2,
        size=17,
    )

    # 6 numbers
    s = _blank(prs)
    add_title_block(s, "05  /  LIVE GEMINI", "GreenLeaf Trading Co. — verified sample pack")
    metrics = [
        ("12", "activity records"),
        ("13.69", "tCO2e total"),
        ("5–6", "IFRS S2 gaps (on-screen)"),
        ("S1/S2/S3", "2.91 / 2.51 / 8.27 t"),
    ]
    for i, (n, label) in enumerate(metrics):
        x = Inches(0.55 + i * 3.15)
        card = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(2.3), Inches(2.95), Inches(2.3))
        _fill(card, NAVY)
        _box(s, x, Inches(2.5), Inches(2.95), Inches(1.2), n, size=32, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        _box(s, x + Inches(0.1), Inches(3.7), Inches(2.75), Inches(0.7), label, size=14, color=CREAM, align=PP_ALIGN.CENTER)
    _box(
        s,
        Inches(0.55),
        Inches(4.9),
        Inches(12.2),
        Inches(1.8),
        "Gemini total is stable across 27 Sep (commit 2c654a8) and 6 Oct 2026 re-run.\n"
        "Gap count drifted 6 → 5. In the video, read the on-screen gap count.\n"
        "Mock mode on the same files: 14.00 tCO2e / 4 canned gaps — do not mix modes.",
        size=16,
        color=MUTED,
    )

    # 7 impact
    s = _blank(prs)
    add_title_block(s, "06  /  IMPACT  25%", "Built for the firms the value chain actually runs on")
    bullets(
        s,
        [
            "Who: SME finance and ops leads answering IFRS S2-style questionnaires without an ESG department.",
            "Demo scale: six synthetic source documents; minutes, not weeks.",
            "Unit of work is the source document. Citations and the audit trail are the product.",
            "Scale path: swap locale factor packs (SG / HK / JP / AU grid). Keep the pipeline.",
            "Commercial wedge: per-report SaaS; later white-label for financed-emissions evidence. The hackathon artifact is the working agent.",
        ],
        top=2.2,
        size=17,
    )

    # 8 judge path
    s = _blank(prs)
    add_title_block(s, "07  /  JUDGE PATH  90s", "Load sample → extract → confirm → map → totals → gaps → cite → ask")
    bullets(
        s,
        [
            "Load sample company (or swap electricity/gas PDFs for a multimodal take).",
            "Run Ingestion Agent. Confirm or correct rows. Mapping Agent cannot invent factors.",
            "Read 13.69 tCO2e when the badge says Gemini. Then run gaps and open one [A#] chip.",
            "Ask: “Which records drive Scope 2?” — answer is grounded and cited (demo: A4).",
            "Every pipeline action is in the audit-trail drawer.",
        ],
        top=2.2,
        size=17,
    )

    # 9 team
    s = _blank(prs)
    add_title_block(s, "08  /  TEAM", "GreenLedger — recruiting to 2–4 by 11 October 2026")
    bullets(
        s,
        [
            "Leader / backend & AI: FENG YIGEN (confirmed) — Hangzhou, JAPAC. Through the 4 Dec finale.",
            "Open: frontend / full-stack. Open: English narrative. Optional: ESG factor-library review.",
            "Platform rule: at least two members to submit. Waitlisted extra accounts cannot Accept yet.",
            "This deck does not list people who have not joined.",
        ],
        top=2.2,
        size=18,
    )

    # 10 close
    s = _blank(prs)
    add_title_block(s, "09  /  ASK", "Disclosure-grade sustainability, without an ESG department")
    bullets(
        s,
        [
            "Prototype URL: pending Cloud Run (billing / contest credits).",
            "Video: local MP4 via demo.storyboard.json — not uploaded until the captain posts YouTube/Vimeo/Drive.",
            "Proposal: docs/proposal.pdf    ·    This deck: docs/greenledger-deck.pptx + .pdf",
            "Public GitHub: required by FAQ; no remote created yet.",
        ],
        top=2.2,
        size=18,
    )
    _box(s, Inches(0.55), Inches(6.35), Inches(12), Inches(0.6), "GreenLedger  ·  Sustainability & Social Impact  ·  AI Builder Cup 2026", size=14, bold=True, color=ACCENT)

    prs.save(OUT_PPTX)
    return OUT_PPTX


if __name__ == "__main__":
    p = build()
    print("wrote", p, p.stat().st_size, "bytes")
