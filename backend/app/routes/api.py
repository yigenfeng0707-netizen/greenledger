from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from ..config import SAMPLE_DIR, settings
from ..services import orchestrator, store
from ..services.emission_factors import all_factors, meta as ef_meta

router = APIRouter()


class ProjectIn(BaseModel):
    name: str = ""


class ActivityPatch(BaseModel):
    status: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    category: Optional[str] = None


class QuestionIn(BaseModel):
    question: str


@router.post("/projects")
def create_project(body: ProjectIn):
    p = store.create_project(body.name)
    return {"project": p}


@router.get("/projects/{pid}")
def get_project(pid: str):
    p = store.get_project(pid)
    if p is None:
        raise HTTPException(404, "project not found")
    return {"project": p, "totals": orchestrator.totals(p)}


@router.post("/projects/{pid}/documents")
async def upload_documents(pid: str, files: List[UploadFile] = File(...)):
    if store.get_project(pid) is None:
        raise HTTPException(404, "project not found")
    added = []
    for f in files:
        raw = await f.read()
        name = f.filename or "upload.bin"
        mime = f.content_type or "application/octet-stream"
        text: Optional[str] = None
        if mime.startswith("text/") or name.lower().endswith((".txt", ".csv", ".md")):
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = None
        doc = store.add_document(pid, name, mime, len(raw), raw, text)
        added.append(doc)
    p = store.get_project(pid)
    store.add_audit(p, "upload", f"{len(added)} document(s) uploaded")
    store.save_project(p)
    return {"added": added, "project": p}


@router.post("/projects/{pid}/load-sample")
def load_sample(pid: str):
    try:
        count = store.load_sample_documents(pid, SAMPLE_DIR)
    except KeyError:
        raise HTTPException(404, "project not found")
    p = store.get_project(pid)
    store.add_audit(p, "upload", f"{count} sample document(s) loaded")
    store.save_project(p)
    return {"added": count, "project": p}


@router.post("/projects/{pid}/extract")
def extract(pid: str):
    try:
        p = orchestrator.extract_all(pid)
    except KeyError:
        raise HTTPException(404, "project not found")
    return {"project": p}


@router.patch("/projects/{pid}/activities/{item_id}")
def patch_activity(pid: str, item_id: str, body: ActivityPatch):
    try:
        p = orchestrator.update_activity(pid, item_id, body.status, body.quantity, body.unit, body.category)
    except KeyError:
        raise HTTPException(404, "not found")
    return {"project": p}


@router.post("/projects/{pid}/map")
def map_factors(pid: str):
    try:
        p = orchestrator.map_all(pid)
    except KeyError:
        raise HTTPException(404, "project not found")
    return {"project": p, "totals": orchestrator.totals(p)}


@router.post("/projects/{pid}/gaps")
def gaps(pid: str):
    try:
        p = orchestrator.gaps_all(pid)
    except KeyError:
        raise HTTPException(404, "project not found")
    return {"project": p}


@router.post("/projects/{pid}/draft")
def draft(pid: str):
    try:
        p = orchestrator.draft_all(pid)
    except KeyError:
        raise HTTPException(404, "project not found")
    return {"project": p, "totals": orchestrator.totals(p)}


@router.post("/projects/{pid}/ask")
def ask(pid: str, body: QuestionIn):
    try:
        return orchestrator.ask(pid, body.question)
    except KeyError:
        raise HTTPException(404, "project not found")


@router.get("/meta")
def meta():
    return {
        "mode": "mock" if settings.use_mock else "gemini",
        "models": {"extract": settings.model_extract, "fast": settings.model_fast},
        "factors": {"count": len(all_factors()), "meta": ef_meta()},
    }
