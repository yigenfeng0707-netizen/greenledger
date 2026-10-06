# Deploy to Google Cloud Run

The submission requires a working prototype deployed on Google Cloud. This repo
ships a single-service setup: Cloud Build builds the frontend, then the backend
Docker image serves both API and static frontend on Cloud Run.

## One-time setup

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable cloudbuild.googleapis.com run.googleapis.com \
  artifactregistry.googleapis.com secretmanager.googleapis.com

# Artifact Registry repo for images
gcloud artifacts repositories create greenledger \
  --repository-format=docker --location=asia-southeast1

# Gemini key as a secret
gcloud secrets create greenledger-gemini-key --data-file=-   # paste key, Ctrl-D
```

Region `asia-southeast1` (Singapore) is a nice nod to the finale venue and low
latency across JAPAC.

## Build & deploy

```bash
gcloud builds submit --config deploy/cloudbuild.yaml .
```

This runs `npm ci && npm run build` in `frontend/`, builds `backend/Dockerfile`
(which copies `frontend/dist`), pushes to Artifact Registry, and deploys
`greenledger-api` with `GEMINI_API_KEY` mounted from Secret Manager.

## Verify

```bash
gcloud run services describe greenledger-api --region asia-southeast1 --format 'value(status.url)'
curl "$(...)/healthz"          # {"ok":true}
curl "$(...)/api/meta"         # {"mode":"gemini", ...}
```

Open the service URL — the app is the same as local, mock badge replaced by the
Gemini badge.

## Current blocker (checked 2026-10-06)

Local gcloud **is** logged in (`yigen.feng0707@gmail.com`) and project
`greenledger-aibc` **is** active. That is not enough to ship HTTPS:

| Check | Result |
|---|---|
| `gcloud billing projects describe greenledger-aibc` | `billingEnabled: false`, empty `billingAccountName` |
| `gcloud billing accounts list` | **0 accounts** on this user |
| Cloud Run Admin API | **not enabled** (`run.googleapis.com` SERVICE_DISABLED) |
| Cloud Build / Artifact Registry | not enabled (not in the enabled-services list) |
| Existing `greenledger-api` service | none (list failed because Run API is off) |

Do **not** treat this as a successful deploy. Enabling Run/Build without a billing
account will still fail.

### What you click (re-checked 2026-10-06 evening)

Logged-in gcloud user `yigen.feng0707@gmail.com` still has **zero** billing
accounts. Pick **one** of these, then come back so deploy can run:

1. **Contest credits (preferred)**  
   Open the official Discord https://discord.gg/x5GRzJbKpa and look for the
   Google Cloud credits / coupon post (also the 29 Sep Welcome email). Redeem
   the code at https://console.cloud.google.com/education (or the URL in that
   post). Then go to  
   https://console.cloud.google.com/billing/linkedaccount?project=greenledger-aibc  
   and **Link a billing account**.

2. **Your own card / existing Cloud billing**  
   https://console.cloud.google.com/billing?authuser=0  
   → **Create account** (or open an account you already own) → add an eligible
   payment method → back to  
   https://console.cloud.google.com/billing/linkedaccount?project=greenledger-aibc  
   → **Link**.

3. **Sanity check** (we can run this for you after you link):

```bash
gcloud billing accounts list
gcloud billing projects describe greenledger-aibc
# expect billingEnabled: true
```

```bash
gcloud config set project greenledger-aibc

# after billing is on:
gcloud services enable cloudbuild.googleapis.com run.googleapis.com \
  artifactregistry.googleapis.com secretmanager.googleapis.com

gcloud artifacts repositories create greenledger \
  --repository-format=docker --location=asia-southeast1

# paste key via stdin only; do not put it in git
gcloud secrets create greenledger-gemini-key --data-file=-

gcloud builds submit --config deploy/cloudbuild.yaml .

gcloud run services describe greenledger-api --region asia-southeast1 \
  --format "value(status.url)"
```

Then probe `/healthz` and `/api/meta` (expect `"mode":"gemini"`). Put the HTTPS
URL into `docs/proposal.md` section 7 and the submission form — never a tunnel.

## Notes

- Cloud Run scale-to-zero is fine for judging; first request warms in ~2s.
- The bundled sample data lives in the image; no external DB needed.
- If you later split the frontend to Firebase Hosting, point `VITE_API_BASE`
  (or the dev proxy target) at the Cloud Run URL and keep CORS as-is.
  Firebase Hosting Spark can host static files without billing; the API still
  needs a billed Cloud Run / Functions / App Hosting project. Same blocker as
  `billingEnabled=false` — do not run an empty Firebase deploy as a substitute.
