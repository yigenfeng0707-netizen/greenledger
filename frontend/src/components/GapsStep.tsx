import type { Project } from "../types";

interface Props {
  project: Project;
  busy: string | null;
  onDraft: () => void;
}

export default function GapsStep({ project, busy, onDraft }: Props) {
  return (
    <section className="card">
      <div className="row between">
        <h3>
          Disclosure gaps <span className="count">{project.gaps.length}</span>
        </h3>
        <button className="primary" onClick={onDraft} disabled={busy !== null || project.emissions.length === 0}>
          {busy === "draft" ? "Drafting…" : "Run Drafting Agent →"}
        </button>
      </div>
      {project.gaps.length === 0 ? (
        <p className="muted">No gaps recorded yet.</p>
      ) : (
        <div className="gaplist">
          {project.gaps.map((g, i) => (
            <div key={i} className={"gap sev-" + g.severity}>
              <div className="gap-head">
                <span className={"sev " + g.severity}>{g.severity}</span>
                <strong>{g.requirement}</strong>
              </div>
              <p>{g.description}</p>
              <p className="suggestion">→ {g.suggestion}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
