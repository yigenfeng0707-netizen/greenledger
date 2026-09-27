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

## Notes

- Cloud Run scale-to-zero is fine for judging; first request warms in ~2s.
- The bundled sample data lives in the image; no external DB needed.
- If you later split the frontend to Firebase Hosting, point `VITE_API_BASE`
  (or the dev proxy target) at the Cloud Run URL and keep CORS as-is.
