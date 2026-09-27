import { useRef, useState } from "react";
import type { Project } from "../types";

interface Props {
  project: Project;
  busy: string | null;
  onLoadSample: () => void;
  onUpload: (files: File[]) => void;
  onExtract: () => void;
}

export default function UploadStep({ project, busy, onLoadSample, onUpload, onExtract }: Props) {
  const [drag, setDrag] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="grid-2">
      <section className="card">
        <h3>Documents</h3>
        <div
          className={"dropzone" + (drag ? " drag" : "")}
          onDragOver={(e) => {
            e.preventDefault();
            setDrag(true);
          }}
          onDragLeave={() => setDrag(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDrag(false);
            if (e.dataTransfer.files.length) onUpload(Array.from(e.dataTransfer.files));
          }}
        >
          <p>
            <strong>Drag &amp; drop</strong> source documents here
          </p>
          <p className="muted">Utility bills · fuel logs · flight itineraries · waste memos — PDF, images, CSV, text</p>
          <button className="ghost" onClick={() => inputRef.current?.click()} disabled={busy !== null}>
            Choose files
          </button>
          <input
            ref={inputRef}
            type="file"
            multiple
            hidden
            accept=".pdf,.png,.jpg,.jpeg,.csv,.txt,.md"
            onChange={(e) => {
              if (e.target.files?.length) onUpload(Array.from(e.target.files));
              e.target.value = "";
            }}
          />
        </div>
        <div className="row gap">
          <button className="ghost" onClick={onLoadSample} disabled={busy !== null}>
            Load sample company
          </button>
          <button className="primary" onClick={onExtract} disabled={busy !== null || project.documents.length === 0}>
            {busy === "extract" ? "Extracting…" : "Run Ingestion Agent →"}
          </button>
        </div>
        {busy && busy !== "extract" && <p className="muted small">Uploading…</p>}
      </section>

      <section className="card">
        <h3>
          Uploaded <span className="count">{project.documents.length}</span>
        </h3>
        {project.documents.length === 0 ? (
          <p className="muted">No documents yet. Try “Load sample company” for a one-click demo.</p>
        ) : (
          <ul className="doclist">
            {project.documents.map((d) => (
              <li key={d.id}>
                <span className="doc-icon">{iconFor(d.mime_type, d.file_name)}</span>
                <span className="doc-name" title={d.file_name}>
                  {d.file_name}
                </span>
                <span className="muted small">{(d.size / 1024).toFixed(1)} KB</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function iconFor(mime: string, name: string): string {
  if (mime === "application/pdf" || name.endsWith(".pdf")) return "📕";
  if (mime.startsWith("image/")) return "🖼️";
  if (name.endsWith(".csv")) return "📊";
  return "📄";
}
