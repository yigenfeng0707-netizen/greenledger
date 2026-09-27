import type { Project } from "../types";
import Md from "./Md";

export default function ReportStep({ project }: { project: Project }) {
  const report = project.report;
  if (!report) return <p className="muted">No draft generated yet.</p>;

  const download = () => {
    const md = [`# ${report.title}`, "", report.summary, "", ...report.sections.map((s) => `## ${s.heading}\n\n${s.content}`)].join("\n");
    const blob = new Blob([md], { type: "text/markdown" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "greenledger-disclosure-draft.md";
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <div className="stack">
      <div className="card report-head">
        <div className="row between">
          <div>
            <h3>{report.title}</h3>
            <p className="muted">{report.period} · GreenLedger agentic pipeline · every figure cites its source record</p>
          </div>
          <button className="ghost" onClick={download}>
            ⬇ Download .md
          </button>
        </div>
        <Md text={report.summary} />
      </div>

      {report.sections.map((s) => (
        <section className="card" key={s.heading}>
          <h3>{s.heading}</h3>
          <Md text={s.content} />
        </section>
      ))}
    </div>
  );
}
