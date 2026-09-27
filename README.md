# GreenLedger — ESG Disclosure Agent

**Google Cloud AI Builder Cup 2026 · Track: Sustainability & Social Impact**

GreenLedger is an agentic pipeline that turns an SME's scattered source documents
(utility bills, fuel logs, flight itineraries, waste memos) into an audit-grade,
IFRS S2-aligned GHG disclosure draft — with every figure cited back to the exact
source record, and every pipeline action logged in a tamper-evident audit trail.

> **Why it can win**: judging is 40% technical depth / 25% problem fit / 25%
> innovation / 10% UX. GreenLedger shows deep Gemini usage (multimodal ingestion,
> tool-constrained factor mapping, cited drafting, grounded Q&A), a mandatory
> regulatory pain point across JAPAC (SGX, HKEX, SSBJ, AASB timelines), and a
> clear innovation line versus existing enterprise ESG suites: agentic + cited +
> built for messy SME data.

## Architecture

```
source docs (PDF/img/CSV/text)
        │
        ▼
[1] Ingestion Agent   — Gemini multimodal extraction → activity records w/ verbatim excerpts
[2] Human review      — confirm / correct / reject (audit-grade human-in-the-loop)
[3] Mapping Agent     — matches records to a CURATED emission-factor library (never invents factors)
[4] Gap Agent         — IFRS S2 / GHG Protocol disclosure gap analysis
[5] Drafting Agent    — cited disclosure draft (markdown, [Ax] citation anchors)
[6] Assurance Q&A     — auditor-style answers, strictly grounded, with citations
        │
   audit trail — every stage logged (timestamp, duration, detail)
```

Stack: **FastAPI + Google ADK-style agents on Gemini API** (backend, Cloud Run) ·
**React/Vite** (frontend, Firebase Hosting or same-service static) · bundled
illustrative emission-factor library (EPA/DEFRA-based).

## Quickstart

```bash
# backend (port 8010; 8000 may be taken by other services)
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8010

# frontend (separate terminal, for dev with hot reload)
cd frontend
npm install
npm run dev           # http://localhost:5173, proxies /api → :8010
```

Open http://localhost:8010 (backend serves the built frontend) or
http://localhost:5173 (dev mode). Click **Load sample company**, then walk
steps 1→6.

### Enable real Gemini (recommended before recording the demo)

```bash
export GEMINI_API_KEY=...        # from Google AI Studio
# optional model overrides
export MODEL_EXTRACT=gemini-2.5-pro
export MODEL_FAST=gemini-2.5-flash
```

Without a key the app runs in **Mock mode** (deterministic heuristics) so the
full flow stays demoable offline — the UI shows which mode is active.

## Repository map

```
backend/app/agents/pipeline.py     agent prompts + Gemini calls (structured JSON output)
backend/app/services/orchestrator.py  pipeline orchestration, IDs, audit, totals
backend/app/services/mock_ai.py    offline mock agents (demo without a key)
backend/app/data/emission_factors.json  curated factor library (16 factors)
frontend/src/components/           Upload / Review / Emissions / Gaps / Report / Ask steps
sample_data/                       synthetic "GreenLeaf Trading Co." demo documents
docs/                              proposal outline & 3-min video storyboard
deploy/                            Cloud Build + Cloud Run deployment
REGISTRATION_CHECKLIST.md          competition registration steps (do this first!)
```

## Competition timeline (from aibuildercup.com)

| Milestone | Date |
|---|---|
| Registration + team formation (2–4 people) | by **2026-10-11** |
| Working prototype submission (proposal + deployed link + 3-min video, all English) | by **2026-10-18** |
| Finalists announced | 2026-11-07 |
| Grand Finale Demo Day, Singapore | 2026-12-04 |

## Next engineering steps

1. Replace bundled factors with authoritative local grid factors per market.
2. Add PDF/image sample docs for the video demo (multimodal showcase).
3. Deploy to Cloud Run (`deploy/`) and record the 3-minute English demo.
4. Draft the English proposal from `docs/proposal_outline.md`.
