import { useState } from "react";
import type { ActivityItem, Project } from "../types";

interface Props {
  project: Project;
  busy: string | null;
  onPatch: (itemId: string, body: { status: string; quantity?: number; unit?: string; category?: string }) => void;
  onConfirmAll: () => void;
  onMap: () => void;
}

const CATEGORIES = [
  "electricity", "natural_gas", "diesel", "gasoline", "lpg", "air_travel", "rail",
  "road_passenger", "freight", "waste", "paper", "water", "hotel", "refrigerant", "commute", "other",
];

export default function ReviewStep({ project, busy, onPatch, onConfirmAll, onMap }: Props) {
  const [edits, setEdits] = useState<Record<string, { quantity?: number; unit?: string; category?: string }>>({});
  const pending = project.activities.filter((a) => a.status === "pending").length;

  return (
    <section className="card">
      <div className="row between">
        <h3>
          Extracted activity records <span className="count">{project.activities.length}</span>
        </h3>
        <div className="row gap">
          <button className="ghost" onClick={onConfirmAll} disabled={busy !== null || pending === 0}>
            Confirm all ({pending})
          </button>
          <button className="primary" onClick={onMap} disabled={busy !== null || project.activities.length === 0}>
            {busy === "map" ? "Mapping…" : "Run Mapping Agent →"}
          </button>
        </div>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Category</th>
              <th>Description / source</th>
              <th>Quantity</th>
              <th>Unit</th>
              <th>Conf.</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {project.activities.map((a) => (
              <Row key={a.id} a={a} busy={busy} onPatch={onPatch} edits={edits} setEdits={setEdits} />
            ))}
          </tbody>
        </table>
      </div>
      <p className="muted small">
        Rejected records are excluded from the inventory and from the report. Edits are logged in the audit trail.
      </p>
    </section>
  );
}

function Row({
  a,
  busy,
  onPatch,
  edits,
  setEdits,
}: {
  a: ActivityItem;
  busy: string | null;
  onPatch: Props["onPatch"];
  edits: Record<string, { quantity?: number; unit?: string; category?: string }>;
  setEdits: React.Dispatch<React.SetStateAction<Record<string, { quantity?: number; unit?: string; category?: string }>>>;
}) {
  const edit = edits[a.id] ?? {};
  const isEditing = a.status === "editing";
  const confirmed = a.status === "confirmed" || a.status === "edited";

  return (
    <tr className={"row-" + a.status}>
      <td>
        <span className="cite">{a.id}</span>
      </td>
      <td>
        {isEditing ? (
          <select
            value={edit.category ?? a.category}
            onChange={(e) => setEdits({ ...edits, [a.id]: { ...edit, category: e.target.value } })}
          >
            {CATEGORIES.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        ) : (
          <code>{a.category}</code>
        )}
      </td>
      <td>
        <div className="desc">{a.description}</div>
        <div className="muted small" title={a.source.excerpt}>
          📄 {a.source.file_name}
          {a.period ? ` · ${a.period}` : ""}
        </div>
      </td>
      <td>
        {isEditing ? (
          <input
            className="num"
            type="number"
            value={edit.quantity ?? a.quantity}
            onChange={(e) => setEdits({ ...edits, [a.id]: { ...edit, quantity: Number(e.target.value) } })}
          />
        ) : (
          a.quantity.toLocaleString()
        )}
      </td>
      <td>
        {isEditing ? (
          <input
            className="num"
            type="text"
            value={edit.unit ?? a.unit}
            onChange={(e) => setEdits({ ...edits, [a.id]: { ...edit, unit: e.target.value } })}
          />
        ) : (
          a.unit
        )}
      </td>
      <td>
        <span className={"conf c" + Math.min(3, Math.floor(a.confidence * 2.9))}>{(a.confidence * 100).toFixed(0)}%</span>
      </td>
      <td>
        <span className={"status s-" + a.status}>{a.status}</span>
      </td>
      <td className="actions">
        {a.status === "editing" ? (
          <>
            <button
              className="primary small"
              disabled={busy !== null}
              onClick={() => {
                onPatch(a.id, { status: "edited", ...edit });
                setEdits({ ...edits, [a.id]: {} });
              }}
            >
              Save
            </button>
            <button className="ghost small" onClick={() => onPatch(a.id, { status: a.status === "editing" ? "pending" : a.status })}>
              Cancel
            </button>
          </>
        ) : (
          <>
            {!confirmed && (
              <button className="ghost small" disabled={busy !== null} onClick={() => onPatch(a.id, { status: "confirmed" })}>
                ✓
              </button>
            )}
            <button className="ghost small" disabled={busy !== null} onClick={() => onPatch(a.id, { status: "editing" })}>
              ✎
            </button>
            <button className="danger small" disabled={busy !== null} onClick={() => onPatch(a.id, { status: "rejected" })}>
              ✕
            </button>
          </>
        )}
      </td>
    </tr>
  );
}
