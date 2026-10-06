# GreenLedger: an auditable ESG disclosure agent for JAPAC SMEs

**Track:** Sustainability and Social Impact  
**Event:** Google Cloud AI Builder Cup 2026  
**Team:** GreenLedger (1 confirmed member as of 2026-10-06; recruiting to 2–4)  
**Prototype URL:** not deployed yet (target: Cloud Run service `greenledger-api` in `asia-southeast1` on GCP project `greenledger-aibc`)  
**Demo video URL:** local file only — `demo-output/GreenLedger_demo_cinematic_3min.mp4` (178s, not uploaded; `docs/demo-video.md`)

This draft maps to the published rubric: Technical 40% · Problem fit & impact 25% · Innovation 25% · UX 10%. Export to PDF before the 18 October 2026 submission. Do not treat placeholder links as live.

---

## 1. Problem and evidence

Mandatory climate disclosure is no longer a large-cap-only problem in JAPAC. Singapore (SGX), Hong Kong (HKEX), Japan (SSBJ), and Australia (AASB S2) are phasing IFRS S2-aligned reporting from FY2025 onward. Listed companies then push the same data demand down their value chains.

The cost lands on SMEs that sit in those chains. A consulting-led GHG inventory still typically costs thousands of US dollars per cycle and takes weeks. Existing ESG platforms assume ERP integrations, months of onboarding, and clean activity feeds. A 35-person trading company does not have that. It has a folder of electricity bills, a diesel log, a commute survey, a waste memo, and a CSV of flights.

If those firms cannot produce a cited inventory, two things fail at once: the SME cannot answer customer questionnaires, and the listed buyer cannot defend Scope 3. The bottleneck is not “another chatbot that talks about sustainability.” It is turning messy source documents into numbers a reviewer can trace.

## 2. Solution

GreenLedger is an agentic pipeline, not a chat window. The user drops source files and walks six steps:

1. **Ingestion** — Gemini multimodal extraction into activity records, each carrying a verbatim excerpt.
2. **Human review** — confirm, edit quantity/unit, or reject. Nothing unreviewed is required for a defensible inventory; rejected rows never enter totals.
3. **Factor mapping** — a tool-constrained agent may *select* a factor from a curated library; it cannot invent a factor ID.
4. **Gap analysis** — IFRS S2 / GHG Protocol missing pieces (metrics, targets, methodology, dual reporting, and related Scope 3 holes), capped at six items.
5. **Drafting** — a markdown disclosure with `[A#]` citation anchors back to records.
6. **Assurance Q&A** — answers grounded in the inventory plus citations; no free-wheeling advice.

Every pipeline action is written to an audit trail (stage, detail, timestamp, duration). The product claim is narrow: **audit-grade draft**, not a certified verification opinion.

## 3. How it works (architecture)

```
source docs (PDF / image / CSV / text)
        |
        v
[1] Ingestion Agent     Gemini structured JSON + excerpts
[2] Human review        confirm / edit / reject
[3] Mapping Agent       curated emission-factor library only
[4] Gap Agent           IFRS S2 / GHG Protocol gaps
[5] Drafting Agent      cited disclosure markdown
[6] Assurance Q&A       grounded answers
        |
   append-only audit trail
```

**Backend.** FastAPI on Python. Agents live in `backend/app/agents/pipeline.py` with Google GenAI structured output. Orchestration, IDs, totals, and persistence are in `backend/app/services/orchestrator.py`. Uploads and project JSON stay on local disk in development; the Cloud Run image bakes in sample documents so judges do not need a database.

**Frontend.** React + Vite. Six-step UI (Upload → Review → Emissions → Gaps → Report → Ask) plus an audit-trail drawer. In production the same Cloud Run service can serve `frontend/dist` (see `deploy/cloudbuild.yaml`). Firebase Hosting is an optional later split, not a current URL.

**Factor library.** Bundled JSON (`backend/app/data/emission_factors.json`), EPA/DEFRA-style illustrative factors with units and scopes. Mapping fails closed if the model returns an unknown `factor_id`. Locale packs (SG/HK/JP/AU grid factors) are the post-hackathon hardening path; the demo is honest that the library is curated-but-illustrative.

**Human-in-the-loop.** Default activity status is `pending`. The finance user is the control owner. This is the feature that makes the output usable in a real close process rather than a screenshot of generated text.

**Failure modes.** With no `GEMINI_API_KEY`, the UI runs a deterministic mock pipeline so the six steps still complete offline and the badge says Mock. With a key, live Gemini is used; model IDs fall back when a default model is retired or overloaded (fix recorded in commit `2c654a8`).

## 4. Why Gemini and Google Cloud (technical 40%)

- **Multimodal long-context ingestion.** The same agent path accepts text, CSV, and (when provided) PDF/image bytes. Extraction is JSON-schema constrained, not free prose.
- **Constrained tool-use for mapping.** The model proposes `factor_id` values that must exist in the library. Invented factors are dropped. That is the difference between “LLM maths” and a reproducible inventory line: quantity × published factor.
- **Cited drafting and grounded Q&A.** Draft sections and answers point at record IDs. An auditor can click from a tonne figure to the excerpt that justified the activity.
- **Intended runtime.** Cloud Run in `asia-southeast1` (Singapore, finale venue and JAPAC latency). Gemini API via Secret Manager (`greenledger-gemini-key`). `MOCK_AI=0` on the service. Frontend may later move to Firebase Hosting against the same API.
- **What is not claimed yet.** No public HTTPS URL exists as of 2026-10-06. GCP project `greenledger-aibc` is active, gcloud is authenticated, **billing is disabled**, Cloud Run Admin API is not enabled, and the logged-in account has **zero** billing accounts. Deploy commands are ready in `deploy/README_deploy.md`; they will not succeed until credits or a billing account are linked.

Live Gemini verification: sample pack “GreenLeaf Trading Co.”, **12 activity records**, **13.69 tCO2e** (stable on 2026-09-27 commit `2c654a8` and a 2026-10-06 re-run). Gap count was **6** then and **5** on the re-run — cite the on-screen list. Mock mode on the same files is 14.00 tCO2e / 4 canned gaps.

## 5. Impact and scale (impact 25%)

**Who.** SME finance / operations leads in JAPAC supply chains who must answer IFRS S2-style questionnaires without an ESG department.

**Demo scale.** Synthetic trading SME, six source documents, minutes rather than weeks. Gemini: 13.69 tCO2e across Scopes 1–3; five to six IFRS S2 / GHG Protocol gaps (missing purchased-goods Scope 3, absent targets, and related methodology holes).

**Why this is not a generic dashboard.** The unit of work is the source document. Citations and the audit trail are the product, because that is what a buyer’s sustainability team actually asks for.

**Scale story, kept short.** Factor packs are locale-parametric: swap grid factors, keep the pipeline. Commercial wedge: per-report SaaS for SMEs, with a later white-label path to banks that need financed-emissions evidence. The hackathon judging artifact is the working agent, not a five-year TAM slide.

## 6. Team

| Role | Status | Notes |
|---|---|---|
| Leader / backend & AI pipeline | **FENG YIGEN** (confirmed) | Hangzhou, JAPAC; designs the agent graph, Gemini integration, and Cloud Run path. Available through the 4 December 2026 finale. |
| Frontend / full-stack | **Open** | UI polish, demo reliability, optional Firebase Hosting split. |
| English narrative | **Open** | Proposal PDF finish, 3-minute voiceover, judge path timing. |
| Optional 4th (ESG / domain review) | **Open** | Factor-library QA; not required to ship the demo. |

Official team formation closes **11 October 2026**. Platform rule: at least two members to submit. Additional registered accounts for this team are still on Hack2skill waitlist and **cannot Accept** until shortlisted. This proposal does not list names of people who have not joined.

## 7. Links and submission checklist

| Artifact | Status on 2026-10-06 |
|---|---|
| Public Cloud Run / Firebase URL | **Missing** — blocked on GCP billing / official credits |
| 3-minute English video | **Local MP4 only** — `demo-output/GreenLedger_demo_cinematic_3min.mp4` (178s). No YouTube/Vimeo/Drive URL yet |
| Proposal PDF | `docs/proposal.pdf` |
| Public GitHub | **Not created** (no git remote). Required by FAQ. |
| Slide deck | `docs/greenledger-deck.pptx` + `docs/greenledger-deck.pdf` (10 slides) |
| Track label | Sustainability and Social Impact — to be selected again at Submissions time |

Judge path (about 60–90 seconds, then the rest of the video): Load sample company → extract → confirm rows → map factors → read 13.69 tCO2e (Gemini) → run gaps → open one citation on the draft → ask “Which records drive Scope 2?”
