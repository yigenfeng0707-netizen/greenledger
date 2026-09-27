import type { Project } from "../types";

const STAGE_COLORS: Record<string, string> = {
  upload: "#5f6368",
  extract: "#1a73e8",
  review: "#0f9d58",
  map: "#0f9d58",
  gaps: "#f9ab00",
  draft: "#a142f4",
  ask: "#e37400",
};

export default function AuditDrawer({ project, onClose }: { project: Project; onClose: () => void }) {
  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <aside className="drawer" onClick={(e) => e.stopPropagation()}>
        <div className="row between">
          <h3>Audit trail</h3>
          <button className="ghost small" onClick={onClose}>
            ✕
          </button>
        </div>
        <p className="muted small">Every pipeline action is logged with timestamps and durations — the auditability that differentiates GreenLedger.</p>
        <ol className="audit-list">
          {project.audit.map((e, i) => (
            <li key={i}>
              <span className="stage-chip" style={{ background: STAGE_COLORS[e.stage] ?? "#5f6368" }}>
                {e.stage}
              </span>
              <div>
                <div>{e.detail}</div>
                <div className="muted small">
                  {new Date(e.ts).toLocaleTimeString()}
                  {e.duration_ms != null ? ` · ${e.duration_ms} ms` : ""}
                </div>
              </div>
            </li>
          ))}
        </ol>
      </aside>
    </div>
  );
}
