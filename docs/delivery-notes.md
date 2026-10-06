# Delivery notes (working)

Do not paste secrets. Do not invent live URLs.

## Demo video (as of 2026-10-06 evening)

| Field | Value |
|---|---|
| Local file | `demo-output/GreenLedger_demo_cinematic_3min.mp4` (gitignored) |
| Duration | **178 s** / 1080p / ~9.2 MB (under FAQ “under 3 minutes”) |
| Voice | English TTS `en-US-JennyNeural` + burned ASS |
| Product footage | Mock-mode six-step UI (Gemini extract is too slow for a 3-minute take) |
| Gemini numbers | On-screen card **13.69 tCO2e**; gap count spoken as 5–6 |
| Public URL | **None** — not uploaded to YouTube / Vimeo / Drive |
| Reproduce | `docs/demo-video.md` |

## Deck

| Field | Value |
|---|---|
| PPTX | `docs/greenledger-deck.pptx` (10 slides) |
| PDF | `docs/greenledger-deck.pdf` |
| Rebuild | `python docs/build_deck.py` then `soffice --headless --convert-to pdf --outdir docs docs/greenledger-deck.pptx` |
| Long proposal | `docs/proposal.pdf` |
