import type { Meta, Project, QAResult, Totals } from "./types";

const BASE = "/api";

async function j<T>(r: Response): Promise<T> {
  if (!r.ok) {
    let detail = r.statusText;
    try {
      const body = await r.json();
      if (body?.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return r.json() as Promise<T>;
}

function post<T>(path: string, body?: unknown): Promise<T> {
  return fetch(`${BASE}${path}`, {
    method: "POST",
    headers: body !== undefined ? { "Content-Type": "application/json" } : undefined,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  }).then((r) => j<T>(r));
}

export const api = {
  meta: () => fetch(`${BASE}/meta`).then((r) => j<Meta>(r)),

  createProject: (name: string) => post<{ project: Project }>("/projects", { name }),

  getProject: (pid: string) =>
    fetch(`${BASE}/projects/${pid}`).then((r) => (r.ok ? j<{ project: Project; totals: Totals }>(r) : null)),

  loadSample: (pid: string) => post<{ project: Project }>(`/projects/${pid}/load-sample`),

  upload: (pid: string, files: File[]) => {
    const fd = new FormData();
    files.forEach((f) => fd.append("files", f));
    return fetch(`${BASE}/projects/${pid}/documents`, { method: "POST", body: fd }).then((r) =>
      j<{ project: Project }>(r)
    );
  },

  extract: (pid: string) => post<{ project: Project }>(`/projects/${pid}/extract`),

  patchActivity: (pid: string, itemId: string, body: { status: string; quantity?: number; unit?: string; category?: string }) =>
    fetch(`${BASE}/projects/${pid}/activities/${itemId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then((r) => j<{ project: Project }>(r)),

  map: (pid: string) => post<{ project: Project; totals: Totals }>(`/projects/${pid}/map`),

  gaps: (pid: string) => post<{ project: Project }>(`/projects/${pid}/gaps`),

  draft: (pid: string) => post<{ project: Project; totals: Totals }>(`/projects/${pid}/draft`),

  ask: (pid: string, question: string) => post<QAResult>(`/projects/${pid}/ask`, { question }),
};
