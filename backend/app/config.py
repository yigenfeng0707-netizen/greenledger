import os

from pathlib import Path

# backend/app/config.py -> parents[1] == backend/
BACKEND_DIR = Path(__file__).resolve().parents[1]
# parents[2] == repo root (contains backend/, frontend/, sample_data/)
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
WORKSPACE_DIR = DATA_DIR / "workspace"
SAMPLE_DIR = ROOT_DIR / "sample_data"


class Settings:
    def __init__(self) -> None:
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.model_extract = os.getenv("MODEL_EXTRACT", "gemini-2.5-pro")
        self.model_fast = os.getenv("MODEL_FAST", "gemini-2.5-flash")
        self.mock = os.getenv("MOCK_AI", "").lower() in ("1", "true", "yes")

    @property
    def use_mock(self) -> bool:
        # Run the deterministic mock pipeline when no key is configured so the
        # whole product stays demoable offline.
        return self.mock or not self.gemini_api_key


settings = Settings()

for d in (DATA_DIR, UPLOAD_DIR, WORKSPACE_DIR):
    d.mkdir(parents=True, exist_ok=True)
