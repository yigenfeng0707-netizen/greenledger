# Proposal Outline (English, ~3 pages + diagrams)

> Submit as PDF. Tone: factual, engineering-first. Map every section to the
> rubric: Technical 40% · Problem fit & impact 25% · Innovation 25% · UX 10%.

## Title
**GreenLedger: an auditable ESG disclosure agent for JAPAC's SMEs**
Track: Sustainability & Social Impact

## 1. Problem & evidence (≈0.5 page)
- Mandatory climate disclosure is rolling out across JAPAC: SGX (Singapore),
  HKEX (Hong Kong), SSBJ (Japan), AASB S2 (Australia) — phased from FY2025.
- Compliance cost falls hardest on SMEs in listed companies' value chains:
  consulting-led GHG inventories cost thousands of USD per cycle and take weeks.
- Existing ESG software targets large enterprises (ERP integrations, months-long
  deployments). SMEs have *messy, scattered* documents — not clean APIs.

## 2. Solution (≈0.5 page)
Drop messy documents → get an audit-grade, IFRS S2-aligned GHG disclosure draft.
- 5-agent pipeline: Ingestion → (human review) → Factor Mapping → Gap Analysis →
  Drafting, plus grounded Assurance Q&A.
- **Every number is cited** to the source document excerpt; **every factor comes
  from a curated library** (the agent selects; it never invents).
- **Every action is logged** in an audit trail with timestamps and durations.

## 3. How it works — architecture (≈1 page, include the diagram)
- Gemini multimodal extraction (PDF/image/CSV/text) with structured JSON output.
- Mapping Agent is *tool-constrained*: it can only pick factors from the bundled
  curated library → auditable, reproducible.
- FastAPI backend (Cloud Run), React frontend (Firebase Hosting), Gemini API.
- Human-in-the-loop review step: the SME finance team confirms/corrects records
  before they enter the inventory — the feature that makes the output defensible.

## 4. Why Gemini / Google Cloud (≈0.5 page) — feeds the 40% technical score
- Multimodal long-context ingestion across heterogeneous messy documents.
- Constrained structured output for extraction, mapping, drafting.
- Deployed on Cloud Run; frontend on Firebase Hosting.
- (Stretch) BigQuery public datasets for benchmarking; Maps for site metadata.

## 5. Impact & scale (≈0.5 page) — feeds the 25% impact score
- Demo: synthetic SME (35 staff, trading company) fully inventoried from 6
  documents in minutes: **13.69 tCO2e** across Scopes 1–3 (reconfirmed 2026-10-06),
  **5–6** disclosure gaps depending on the Gemini draw (commit `2c654a8` = 6;
  2026-10-06 dry-run = 5). Mock mode is 14.00 tCO2e / 4 canned gaps — do not
  quote mock figures in the PDF if the video shows Gemini.
- "Build in JAPAC, for the world": factor library is locale-parametric — ship
  SG/HK/JP/AU grid factors; same pipeline, any disclosure framework.
- Business model: per-report SaaS for SMEs; white-label to banks' SME lending
  (financed-emissions data) — name the wedge, keep it short.

## 6. Team (≈0.25 page)
- Confirmed: FENG YIGEN (leader, backend/AI). Open: frontend/full-stack, English
  narrative. State availability through Dec 4 finale. Do not list waitlisted names.

## 7. Link
- Deployed prototype URL + 3-minute video link (unlisted OK where allowed).
- As of 2026-10-06 both URLs are still blank; full draft: `docs/proposal.md`.
