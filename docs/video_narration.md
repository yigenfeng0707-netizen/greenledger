# GreenLedger — 3-minute English voiceover

Read against `docs/video_storyboard.md`. Target ~180 seconds (~430 words at ~145 wpm).
Record with the **Gemini** badge visible. Speak **13.69 tCO2e**. If the gap count on screen is not five, **say the on-screen count**.

---

**[0:00–0:20 — Hook]**

Climate disclosure is now law across Asia-Pacific — SGX, HKEX, Japan, Australia. For a small supplier, one consulting-led greenhouse-gas inventory still costs thousands of dollars and weeks of work. Their data is not an ERP feed. It is a shoebox of bills and spreadsheets.

**[0:20–0:50 — Ingestion]**

GreenLedger is an agentic pipeline, not a chatbot. Drop the mess — utility bills, fuel logs, flight itineraries. Two of these samples are real PDFs so Gemini can read them multimodally. The Ingestion Agent extracts every activity datum and keeps the verbatim source excerpt beside it.

**[0:50–1:20 — Review and mapping]**

Nothing enters the inventory unreviewed. The finance team confirms or corrects each record — that is what makes the output audit-grade. Then the Mapping Agent matches every record to a curated emission-factor library. It may choose a factor. It can never invent one.

**[1:20–1:50 — Totals and gaps]**

Thirteen point six nine tonnes of CO2 equivalent, split by Scope 1, 2, and 3. Every line is reproducible: quantity times a cited factor. The Gap Agent then checks the inventory against IFRS S2 and the GHG Protocol. It flags several gaps — missing Scope 3 spend data, absent targets, methodology holes — each with a concrete fix. If the on-screen gap count differs from this script, read the number on screen. Gap counts drift between five and six on live Gemini; the tonne total does not.

**[1:50–2:30 — Draft, audit trail, Ask]**

The Drafting Agent writes the disclosure. Every figure cites the record it came from — click the chip and you are at the source excerpt. Every pipeline action is logged in an audit trail. An auditor can interrogate the inventory. Ask: “Which records drive Scope 2?” Answers come strictly from the data, with citations.

**[2:30–3:00 — Close]**

Built with Gemini multimodal structured extraction and constrained agentic tool-use, served from Google Cloud Run. Factor packs are locale-parametric: the same pipeline that reads a Shanghai SME’s bills today reads a Tokyo supplier’s tomorrow. GreenLedger — disclosure-grade sustainability, for the companies the value chain actually runs on. Track: Sustainability and Social Impact. Team GreenLedger.

---

## Timing notes

| Block | Approx. words | Cue |
|---|---|---|
| Hook | ~70 | messy bills / deadline |
| Ingestion | ~70 | upload PDFs + txt/csv |
| Review / map | ~65 | confirm one row; mapping |
| Totals / gaps | ~95 | **13.69 tCO2e**; on-screen gaps |
| Draft / Ask | ~75 | citation chip + Ask A4 |
| Close | ~70 | architecture + track + team |

Do not read mock totals (14.00 tCO2e / 4 canned gaps) while the badge says Gemini.
