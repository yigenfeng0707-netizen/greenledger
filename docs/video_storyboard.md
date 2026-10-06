# 3-Minute Demo Video Storyboard (English voiceover)

> Rules: show the product *running*. Record 1440×900, 30fps, captions burned in.
> Upload as YouTube (unlisted) / Vimeo / Drive link. Script below ≈ 420 words.

## 0:00–0:20 — Hook (problem)
- Visual: stack of messy invoices/bills raining onto a spreadsheet; SME finance
  manager facepalms; calendar shows "Disclosure deadline".
- VO: "Climate disclosure is now law across Asia-Pacific — SGX, HKEX, Japan, Australia.
  For a small supplier, one consulting-led GHG inventory costs thousands of dollars
  and weeks of work. Their data? A shoebox of bills and spreadsheets."

## 0:20–0:50 — The drop (magic moment #1)
- Visual: GreenLedger upload screen; drag the 6 sample documents in (for
  multimodal: electricity + gas **PDFs** plus the other four txt/csv; do not also
  drop the matching `.txt` bills).
- VO: "GreenLedger. An agentic pipeline, not a chatbot. Drop the mess — utility bills,
  fuel logs, flight itineraries — and the Ingestion Agent reads them with Gemini,
  multimodally, extracting every activity datum with its verbatim source excerpt."

## 0:50–1:20 — Human-in-the-loop (magic moment #2)
- Visual: Review table; correct one quantity; confirm all; click mapping.
- VO: "Nothing enters the inventory unreviewed. The finance team confirms or corrects
  each record — that's what makes the output audit-grade. Then the Mapping Agent
  matches every record to a *curated* emission-factor library. It can choose a factor —
  it can never invent one."

## 1:20–1:50 — Results (technical credibility)
- Visual: Emissions step — totals cards (**13.69 tCO2e** on live Gemini, Scope 1/2/3),
  factor table. Do **not** read mock totals if the badge says Gemini.
- VO: "Thirteen point six nine tonnes, split by scope, each line reproducible:
  quantity times cited factor. The Gap Agent then checks the inventory against
  IFRS S2 and the GHG Protocol — it flags several gaps (five or six depending on
  the live run), including missing Scope 3 spend data and absent targets, with
  concrete fixes. Read the on-screen count, not this script, if they differ."

## 1:50–2:30 — The disclosure + audit trail (differentiation)
- Visual: Report page — scroll the cited draft, hover a [Ax] chip; open the audit
  trail drawer; then Ask step: "Which records drive Scope 2?" → cited answer.
- VO: "The Drafting Agent writes the disclosure. Every figure cites the record it
  came from — click it and you're at the source excerpt. Every pipeline action is
  logged in an audit trail. And an auditor can interrogate the inventory: answers
  come strictly from the data, with citations."

## 2:30–3:00 — Stack + scale (close)
- Visual: architecture diagram (FastAPI + Gemini on Cloud Run, React on Firebase);
  JAPAC map with factor packs lighting up SG/HK/JP/AU; team card.
- VO: "Built with Gemini multimodal structured extraction and constrained agentic
  tool-use, served from Google Cloud Run. Factor packs are locale-parametric:
  the same pipeline that reads a Shanghai SME's bills today reads a Tokyo supplier's
  tomorrow. GreenLedger — disclosure-grade sustainability, for the companies the
  value chain actually runs on."

## Numbers to keep consistent (do not mix modes)

| Mode | Evidence | Activities | Total | Gaps |
|---|---|---|---|---|
| Live Gemini | commit `2c654a8` (2026-09-27) | 12 | **13.69 tCO2e** | **6** |
| Live Gemini | 2026-10-06 in-process dry-run (~9 min) | 12 | **13.69 tCO2e** | **5** |
| Mock (`MOCK_AI=1`) | 2026-10-06 same samples | 12 | **14.00 tCO2e** | **4** canned |

Total tCO2e is stable in Gemini (13.69). Gap count is model-variable (5–6). Record with the Gemini badge and speak the number on screen.

## Recording checklist
- [ ] Enable GEMINI_API_KEY mode (badge shows "Gemini") for authenticity
- [x] Tiny synthetic PDFs in `sample_data/` (electricity + gas); regen: `python sample_data/make_sample_pdfs.py`
- [ ] Voiceover: `docs/video_narration.md` (not recorded)
- [x] Mock dry run 2026-10-06: 12 records, 14.00 tCO2e, 4 gaps, 5-section draft, Q&A cited A4
- [x] Gemini dry run 2026-10-06: 12 records, **13.69 tCO2e**, **5** gaps, 5-section draft, Q&A cited A4 (~9 min)
- [ ] Captions on; no dead air; end card with team + track name (1 confirmed member + open roles)
- [ ] Full video edit / YouTube-Vimeo-Drive upload (not done this round)

## Dry run log

- **2026-10-06 mock** (`MOCK_AI=1`, in-process orchestrator, 6 `sample_data` files):
  12 activities, 12 mapped rows, **14.00 tCO2e** (S1 2.91 / S2 2.51 / S3 8.58 t),
  **4** canned gaps, 5-section draft, Ask “Which records drive Scope 2?” cited `A4`.
  Path is walkable offline. Speak Gemini totals (13.69 t) only when the badge says Gemini.
- **2026-10-06 Gemini** (key already in the environment; ~9 min wall time): 12 activities,
  **13.69 tCO2e** (S1 2.91 / S2 2.51 / S3 8.27 t), **5** gaps, 5-section draft, Q&A cited `A4`.
  Full video edit still not done.
