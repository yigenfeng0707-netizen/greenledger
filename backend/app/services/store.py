"""File-backed project store: one JSON per project + raw uploads on disk."""

from __future__ import annotations

import datetime
import json
import threading
import uuid
from typing import Dict, Optional

from ..config import UPLOAD_DIR, WORKSPACE_DIR
from ..models.schemas import AuditEvent, Document, Project

_lock = threading.RLock()
_projects: Dict[str, Project] = {}


def _path(pid: str):
    return WORKSPACE_DIR / f"{pid}.json"


def _persist(p: Project) -> None:
    with open(_path(p.id), "w", encoding="utf-8") as f:
        f.write(p.model_dump_json(indent=1))


def create_project(name: str) -> Project:
    with _lock:
        pid = uuid.uuid4().hex[:12]
        p = Project(
            id=pid,
            name=name or f"Inventory {datetime.date.today().isoformat()}",
            created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )
        _projects[pid] = p
        _persist(p)
        return p


def get_project(pid: str) -> Optional[Project]:
    with _lock:
        if pid in _projects:
            return _projects[pid]
        path = _path(pid)
        if path.exists():
            p = Project.model_validate_json(path.read_text(encoding="utf-8"))
            _projects[pid] = p
            return p
    return None


def save_project(p: Project) -> None:
    with _lock:
        _projects[p.id] = p
        _persist(p)


def add_document(pid: str, file_name: str, mime_type: str, size: int, raw: bytes, text: Optional[str]) -> Document:
    p = get_project(pid)
    if p is None:
        raise KeyError(f"project {pid} not found")
    with _lock:
        doc_dir = UPLOAD_DIR / pid
        doc_dir.mkdir(parents=True, exist_ok=True)
        (doc_dir / file_name).write_bytes(raw)
        doc = Document(
            id=uuid.uuid4().hex[:8],
            file_name=file_name,
            mime_type=mime_type,
            size=size,
            text=text,
        )
        p.documents.append(doc)
        _persist(p)
        return doc


def load_sample_documents(pid: str, sample_dir) -> int:
    """Copy the bundled sample files into the project as documents."""
    p = get_project(pid)
    if p is None:
        raise KeyError(f"project {pid} not found")
    count = 0
    for path in sorted(sample_dir.glob("*")):
        if path.name.lower() == "readme.md":
            continue
        if path.suffix.lower() not in (".txt", ".csv"):
            continue
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = None
        add_document(pid, path.name, "text/plain" if text else "application/octet-stream", len(raw), raw, text)
        count += 1
    return count


def add_audit(p: Project, stage: str, detail: str, duration_ms: Optional[int] = None) -> None:
    p.audit.append(
        AuditEvent(
            ts=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds"),
            stage=stage,
            detail=detail,
            duration_ms=duration_ms,
        )
    )
