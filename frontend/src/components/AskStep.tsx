import { useState } from "react";
import { api } from "../api";
import type { Project, QAResult } from "../types";
import Md from "./Md";

interface Msg {
  role: "user" | "agent";
  text: string;
  citations?: string[];
}

const SUGGESTIONS = [
  "What is our total footprint?",
  "Which records drive Scope 2?",
  "How large is business air travel?",
  "What gaps should we close before disclosing?",
];

export default function AskStep({ pid, project, busy }: { pid: string; project: Project; busy: string | null }) {
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");

  async function ask(q: string) {
    const question = q.trim();
    if (!question || busy) return;
    setInput("");
    setMsgs((m) => [...m, { role: "user", text: question }]);
    try {
      const r: QAResult = await api.ask(pid, question);
      setMsgs((m) => [...m, { role: "agent", text: r.answer, citations: r.citations }]);
    } catch (e) {
      setMsgs((m) => [...m, { role: "agent", text: `⚠ ${e instanceof Error ? e.message : String(e)}` }]);
    }
  }

  return (
    <section className="card ask">
      <h3>Assurance Q&amp;A</h3>
      <p className="muted small">
        The agent answers strictly from the {project.emissions.length} quantified records in this inventory and cites them.
      </p>

      <div className="chat">
        {msgs.length === 0 && (
          <div className="suggestions">
            {SUGGESTIONS.map((s) => (
              <button key={s} className="ghost" onClick={() => ask(s)} disabled={busy !== null}>
                {s}
              </button>
            ))}
          </div>
        )}
        {msgs.map((m, i) => (
          <div key={i} className={"msg " + m.role}>
            {m.role === "agent" ? <Md text={m.text} /> : m.text}
            {m.citations && m.citations.length > 0 && (
              <div className="cite-row">
                {m.citations.map((c) => (
                  <span key={c} className="cite">
                    {c}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <form
        className="row gap"
        onSubmit={(e) => {
          e.preventDefault();
          ask(input);
        }}
      >
        <input className="chat-input" value={input} placeholder="Ask an auditor-style question…" onChange={(e) => setInput(e.target.value)} />
        <button className="primary" type="submit" disabled={busy !== null || !input.trim()}>
          Ask
        </button>
      </form>
    </section>
  );
}
