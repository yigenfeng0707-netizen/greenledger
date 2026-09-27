import { useEffect, useRef, useState } from "react";
import { api } from "./api";
import type { Meta, Project, Totals } from "./types";
import UploadStep from "./components/UploadStep";
import ReviewStep from "./components/ReviewStep";
import EmissionsStep from "./components/EmissionsStep";
import GapsStep from "./components/GapsStep";
import ReportStep from "./components/ReportStep";
import AskStep from "./components/AskStep";
import AuditDrawer from "./components/AuditDrawer";

const STEPS = ["Upload", "Review", "Emissions", "Gaps", "Report", "Ask"];

export default function App() {
  const [pid, setPid] = useState<string>("");
  const [project, setProject] = useState<Project | null>(null);
  const [totals, setTotals] = useState<Totals | null>(null);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [step, setStep] = useState(0);
  const [busy, setBusy] = useState<string | null>(null);
  const [err, setErr] = useState("");
  const [auditOpen, setAuditOpen] = useState(false);
  const initRef = useRef(false);

  useEffect(() => {
    api.meta().then(setMeta).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;
    (async () => {
      const saved = localStorage.getItem("gl_pid");
      if (saved) {
        const d = await api.getProject(saved).catch(() => null);
        if (d) {
          setPid(saved);
          setProject(d.project);
          setTotals(d.totals);
          setStep(initialStep(d.project));
          return;
        }
      }
      const d = await api.createProject("GHG Inventory").catch((e) => {
        setErr(String(e));
        return null;
      });
      if (d) {
        localStorage.setItem("gl_pid", d.project.id);
        setPid(d.project.id);
        setProject(d.project);
      }
    })();
  }, []);

  function apply(d: { project: Project; totals?: Totals }) {
    setProject(d.project);
    if (d.totals) setTotals(d.totals);
  }

  async function run(key: string, fn: () => Promise<{ project: Project; totals?: Totals }>, nextStep?: number) {
    setBusy(key);
    setErr("");
    try {
      apply(await fn());
      if (nextStep !== undefined) setStep(nextStep);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(null);
    }
  }

  if (!project) {
    return (
      <div className="loading">
        <div className="spinner" />
        <p>Connecting to GreenLedger API…</p>
        {err && <p className="error">{err}</p>}
      </div>
    );
  }

  const done = [
    project.documents.length > 0,
    project.activities.length > 0,
    project.emissions.length > 0,
    project.gaps.length > 0,
    project.report !== null,
    project.report !== null,
  ];

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="logo">
          <span className="logo-mark">GL</span>
          <div>
            <div className="logo-name">GreenLedger</div>
            <div className="logo-sub">ESG Disclosure Agent</div>
          </div>
        </div>
        <nav className="steps">
          {STEPS.map((label, i) => (
            <button key={label} className={"step" + (i === step ? " active" : "") + (done[i] ? " done" : "")} onClick={() => setStep(i)}>
              <span className="step-num">{done[i] && i < 5 ? "✓" : i + 1}</span>
              {label}
            </button>
          ))}
        </nav>
        <div className="sidebar-foot">
          <div className={"mode " + (meta?.mode ?? "")}>
            {meta?.mode === "gemini" ? `Gemini · ${meta.models.extract}` : "Mock mode (no API key)"}
          </div>
          <button className="ghost w-full" onClick={() => setAuditOpen(true)}>
            Audit trail ({project.audit.length})
          </button>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h1>{stepTitle(step)}</h1>
            <p className="topbar-sub">{stepSub(step)}</p>
          </div>
          <div className="pill">Track: Sustainability &amp; Social Impact</div>
        </header>

        {err && <div className="banner error">{err}</div>}

        {step === 0 && (
          <UploadStep
            project={project}
            busy={busy}
            onLoadSample={() => run("sample", () => api.loadSample(pid))}
            onUpload={(files) => run("upload", () => api.upload(pid, files))}
            onExtract={() => run("extract", () => api.extract(pid), 1)}
          />
        )}
        {step === 1 && (
          <ReviewStep
            project={project}
            busy={busy}
            onPatch={(itemId, body) => run(`patch-${itemId}`, () => api.patchActivity(pid, itemId, body))}
            onConfirmAll={() => run("confirm-all", async () => {
              let p = project;
              for (const a of p.activities.filter((x) => x.status === "pending")) {
                p = (await api.patchActivity(pid, a.id, { status: "confirmed" })).project;
              }
              return { project: p };
            })}
            onMap={() => run("map", () => api.map(pid), 2)}
          />
        )}
        {step === 2 && (
          <EmissionsStep
            project={project}
            totals={totals}
            busy={busy}
            onGaps={() => run("gaps", () => api.gaps(pid), 3)}
          />
        )}
        {step === 3 && (
          <GapsStep project={project} busy={busy} onDraft={() => run("draft", () => api.draft(pid), 4)} />
        )}
        {step === 4 && <ReportStep project={project} />}
        {step === 5 && <AskStep pid={pid} project={project} busy={busy} />}
      </main>

      {auditOpen && <AuditDrawer project={project} onClose={() => setAuditOpen(false)} />}
    </div>
  );
}

function initialStep(p: Project): number {
  if (p.report) return 4;
  if (p.gaps.length) return 3;
  if (p.emissions.length) return 2;
  if (p.activities.length) return 1;
  return 0;
}

function stepTitle(i: number): string {
  return [
    "Upload source documents",
    "Human-in-the-loop review",
    "Emission factors & results",
    "Disclosure gap analysis",
    "IFRS S2-aligned draft",
    "Assurance Q&A (cited)",
  ][i];
}

function stepSub(i: number): string {
  return [
    "Drop utility bills, fuel logs, travel records — PDF, images, CSV or text. Every number will stay traceable to its source.",
    "Confirm, correct or reject each extracted record before it enters the inventory. This is what makes the output audit-grade.",
    "The Mapping Agent matched each record to a curated emission factor. Totals update per scope.",
    "The Gap Agent checks the inventory against IFRS S2 / GHG Protocol disclosure requirements.",
    "The Drafting Agent writes the disclosure — every figure cites the activity record it came from.",
    "Answer auditor questions strictly from the inventory, with citations.",
  ][i];
}
