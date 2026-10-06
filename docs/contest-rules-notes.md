# Contest rules notes (working copy)

> Last checked in-repo: **2026-10-06** (evening re-check). Official pages opened in a live browser. This page is an operational summary, not a copy of the rules.

## Sources opened this round (2026-10-06)

| Page | URL | Status |
|---|---|---|
| Homepage | https://aibuildercup.com/ | Opened |
| FAQs | https://aibuildercup.com/Faqs.html | Opened; “Building & Submission” + other tabs |
| Challenges & Requirements | https://aibuildercup.com/themes.html | Opened |
| Hack2skill Dashboard / logged-in Submissions form | (login wall) | **Not** re-opened this round; field labels on the form may still differ |

Do not treat a previous checklist rumour as stronger than these pages.

## Dates (homepage Timeline)

| Milestone | Date |
|---|---|
| Registration & team formation | 1 Sept – **11 Oct 2026** |
| Prototype building & submission | 7 Sept – **18 Oct 2026** |
| Prototype submission deadline | **18 Oct 2026** |
| Evaluation | 19 Oct – 6 Nov 2026 |
| Finalists announced | 7 Nov 2026 |
| Grand Finale, Singapore | 4 Dec 2026 |

Homepage roadmap: register solo is allowed; **form a team of 2–4 by 11 October**; if shortlisted, **only 2 members travel**.

## Eligibility (FAQ: Team Composition)

- Working professionals / entrepreneurs / startups; **21+**; **JAPAC only**. Students disqualify the whole team.
- **Cannot participate solo** for the build; you may register solo then join a team. Teams **2–4**.
- Cross-country JAPAC teams allowed; members outside JAPAC are not.
- One person, one team, one theme.

Dashboard copy previously screenshotted: teams must have **at least 2 members to be eligible for submissions**.

## Stack (FAQ + themes “What you'll build”)

- Must use **Google AI models** (Gemini / Gemma family) **or** agentic platforms (Agent Platform, Antigravity, AI Studio).
- Must deploy on **Google Cloud via Cloud Run or Firebase**. FAQ wording: working prototype “successfully deployed on **Cloud Run/GCP/Firebase**”.
- Other-cloud-primary solutions are **not eligible**.
- Fresh projects built during the hackathon timeline only (FAQ).

Credits: organizers stated Google Cloud credits would support the build. As of 2026-10-06 they are **not** attached to project `greenledger-aibc` (`billingEnabled=false`; 0 billing accounts on the logged-in gcloud user).

## Required for 10/18 — **confirmed on public FAQ + themes** (2026-10-06)

FAQ *“Is there a fixed format for submission…?”* (https://aibuildercup.com/Faqs.html, Building & Submission):

> a working **deployed link** of your prototype, a **video demo under 3 minutes**, the **public GitHub repository** of your prototype and a **deck** explaining your solution in detail.

Themes *“What you'll submit”* (https://aibuildercup.com/themes.html) spells the same pack as:

1. **Clear Proposal** — vision in a **deck/PPT converted into a PDF**; problem, community benefit, feasibility/scalability.
2. **Functional Prototype** — Google Cloud AI tools, deployed on **Cloud Run/GCP/Firebase**.
3. **Comprehensive Documentation** — public **YouTube or Vimeo** or public **Google Drive**, **3 minutes**, product running.
4. **Category / theme** — identify the problem statement (this project: **Sustainability & Social Impact**).
5. **All materials in English** (code, docs, presentations).

Treat **public GitHub** and **deck-as-PDF** as **mandatory**, not optional extras.

Local mapping:

| Required artifact | This repo (2026-10-06, team = 2: Leader FENG YIGEN / fengyigen@qq.com + Biswajit Mondal / rmondal8436dgp@gmail.com) |
|---|---|
| Deployed HTTPS | **Missing** — Cloud Run blocked on billing |
| Video < 3 min | **https://youtu.be/n2NBXwpXshQ** (YouTube Unlisted, **2:59**, uploaded 2026-10-06). Local source: `demo-output/GreenLedger_demo_cinematic_3min.mp4` (gitignored). How-to: `docs/demo-video.md` |
| Public GitHub | **https://github.com/yigenfeng0707-netizen/greenledger** (public, master @ latest push) |
| Deck / proposal PDF | Slide deck: `docs/greenledger-deck.pptx` + `docs/greenledger-deck.pdf` (10 pages). Long-form: `docs/proposal.pdf` |

## Firebase Hosting as a billing workaround — **no**

Firebase Hosting on the free Spark plan can serve **static files** without a billing account. The GreenLedger **API** (FastAPI + Gemini) is not a static site. Cloud Functions, App Hosting, and Cloud Run all need a **Blaze / billed** GCP project. Same `billingEnabled=false` wall. Do not spend a round on an empty Firebase deploy until credits or a card are attached.

## Explicitly not required / not blocking by themselves

- T-shirt size form (already missed).
- Splitting frontend to Firebase Hosting (a single Cloud Run service that serves API + `frontend/dist` still matches “Cloud Run or Firebase”).
- PDF sample documents (now bundled for the video; txt/csv still exist).

## Judging (FAQ + themes)

Same four weights on all themes: Technical & Gen AI **40%** · Problem alignment & impact **25%** · Innovation **25%** · UX **10%**. There is a scoring round **before** the finale that produces the Singapore shortlist.
