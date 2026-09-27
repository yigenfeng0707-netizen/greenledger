import type { Project, Totals } from "../types";

interface Props {
  project: Project;
  totals: Totals | null;
  busy: string | null;
  onGaps: () => void;
}

const SCOPE_COLORS: Record<number, string> = { 1: "#d93025", 2: "#1a73e8", 3: "#f9ab00" };

export default function EmissionsStep({ project, totals, busy, onGaps }: Props) {
  const byScope: Record<number, number> = { 1: 0, 2: 0, 3: 0 };
  project.emissions.forEach((e) => {
    byScope[e.scope] = (byScope[e.scope] ?? 0) + e.co2e_kg;
  });
  const total = totals?.total_co2e_kg ?? Object.values(byScope).reduce((a, b) => a + b, 0);
  const maxScope = Math.max(1, ...Object.values(byScope));

  return (
    <div className="stack">
      <div className="cards">
        <div className="card stat">
          <div className="stat-label">Total inventory</div>
          <div className="stat-value">{(total / 1000).toFixed(2)} <small>tCO₂e</small></div>
        </div>
        {([1, 2, 3] as const).map((s) => (
          <div className="card stat" key={s}>
            <div className="stat-label">
              <span className="dot" style={{ background: SCOPE_COLORS[s] }} /> Scope {s}
            </div>
            <div className="stat-value">
              {((byScope[s] ?? 0) / 1000).toFixed(2)} <small>tCO₂e</small>
            </div>
            <div className="bar">
              <div className="bar-fill" style={{ width: `${((byScope[s] ?? 0) / maxScope) * 100}%`, background: SCOPE_COLORS[s] }} />
            </div>
          </div>
        ))}
      </div>

      <section className="card">
        <h3>
          Mapped records <span className="count">{project.emissions.length}</span>
        </h3>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Record</th>
                <th>Emission factor</th>
                <th>Quantity</th>
                <th>× factor</th>
                <th>kgCO₂e</th>
                <th>Scope</th>
              </tr>
            </thead>
            <tbody>
              {project.emissions.map((e) => (
                <tr key={e.item_id}>
                  <td>
                    <span className="cite">{e.item_id}</span>
                  </td>
                  <td>
                    <div>{e.factor_name}</div>
                    <div className="muted small" title={e.rationale}>
                      {e.factor_id}
                    </div>
                  </td>
                  <td>
                    {e.quantity_in_factor_unit.toLocaleString()} {e.factor_unit}
                  </td>
                  <td>{e.factor_value}</td>
                  <td>
                    <strong>{e.co2e_kg.toLocaleString()}</strong>
                  </td>
                  <td>
                    <span className="scope-chip" style={{ background: SCOPE_COLORS[e.scope] }}>
                      S{e.scope}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="row gap end">
          <button className="primary" onClick={onGaps} disabled={busy !== null}>
            {busy === "gaps" ? "Analyzing…" : "Run Gap Analysis Agent →"}
          </button>
        </div>
      </section>
    </div>
  );
}
