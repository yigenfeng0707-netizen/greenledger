# Demo video — how to reproduce

Local cinematic MP4 only. **Not uploaded** to YouTube / Vimeo / Drive.

## Output

| Item | Path |
|---|---|
| Storyboard | `demo.storyboard.json` |
| Final MP4 (after a successful run) | `demo-output/GreenLedger_demo_cinematic_3min.mp4` |
| Engine | `demo-video-factory` + `cinematic-demo-video` skills (do not fork compose scripts into this repo) |

Target: **178s** (FAQ: under 3 minutes), English TTS (`en-US-JennyNeural`), 1080p30, ASS burned in, CRF~17.

Intro/outro use deck PNGs, not the factory `title` cards (those are branded TenderPilot in the shared engine).

Honest split:

- Browser scene = **Mock mode** so the six-step UI completes inside the time budget (live Gemini extract was ~9 minutes on 2026-10-06).
- Totals card = **live Gemini 13.69 tCO2e** from the 2026-09-27 / 2026-10-06 dry-runs. Do not speak Mock 14.00 t while that card is on screen.

## One-time

```powershell
python docs/build_deck.py
soffice --headless --convert-to pdf --outdir docs docs/greenledger-deck.pptx
python docs/export_deck_pngs.py

New-Item -ItemType Directory -Force -Path tools/demo-video | Out-Null
Set-Location tools/demo-video
npm init -y
npm i -D playwright
npx playwright install chromium
npx playwright install ffmpeg
Set-Location ../..
```

Python: `edge-tts`, `Pillow`. `ffmpeg` on PATH.

## Each run

Terminal 1 — **force Mock** even if a Gemini key is in the environment:

```powershell
cd backend
$env:MOCK_AI = "1"
python -m uvicorn app.main:app --port 8010
```

Terminal 2:

```powershell
cd frontend
npm install
npm run dev          # binds localhost:5173 on this machine (not 127.0.0.1)
```

Then:

```powershell
powershell -File "$env:USERPROFILE\.cursor\skills\demo-video-factory\scripts\run_demo_video.ps1" `
  -Storyboard demo.storyboard.json
```

Recompose only (skip Playwright) after changing `minDuration` / CRF / subs:

```powershell
python "$env:USERPROFILE\.cursor\skills\demo-video-factory\scripts\compose_demo_video.py" `
  --storyboard demo.storyboard.json
```

If the app is down, `record_demo.mjs` fails the health check. Fall back: keep deck PNG scenes in the storyboard and drop the `h2` browser scene, then re-run compose after a screenshot-only pass — or re-export PNGs and keep image scenes only.

## Upload (needs your Google login — CLI/Drive MCP were not signed in)

Local file: `demo-output/GreenLedger_demo_cinematic_3min.mp4` (**178s**, gitignored).

**YouTube (unlisted) — ~2 minutes**

1. Open https://studio.youtube.com while signed into a Google account that can publish.
2. **Create** → **Upload videos** → pick the MP4 above.
3. Title: `GreenLedger — AI Builder Cup 2026 demo`
4. Visibility: **Unlisted** (or Public). Wait until processing finishes.
5. Copy the watch URL (`youtube.com/watch?v=...`) and paste it into `docs/proposal.md` section 7 and the Hack2skill form.

**Google Drive (public link)**

1. Open https://drive.google.com → **New** → **File upload** → same MP4.
2. Right-click → **Share** → General access **Anyone with the link** → Viewer.
3. Copy the link into the same two places.

Do not commit the MP4. After the URL exists, tell the agent to backfill docs.

