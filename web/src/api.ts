import type { Transcript } from "./types";

const BASE = import.meta.env.VITE_API_BASE ?? "/api";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`request failed: ${res.status}`);
  return (await res.json()) as T;
}

export async function fetchQueue(): Promise<Transcript[]> {
  const data = await getJson<{ requests: Transcript[] }>("/queue");
  return data.requests;
}

export async function fetchEscalations(): Promise<Transcript[]> {
  const data = await getJson<{ escalations: Transcript[] }>("/escalations");
  return data.escalations;
}

export async function resolveEscalation(
  requestId: string,
  decision: "approve" | "override",
  note: string,
): Promise<Transcript> {
  const res = await fetch(`${BASE}/escalations/${requestId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision, note }),
  });
  if (!res.ok) throw new Error(`request failed: ${res.status}`);
  return (await res.json()) as Transcript;
}
