import { useCallback, useEffect, useState } from "react";
import { fetchEscalations, fetchQueue, resolveEscalation } from "./api";
import { RequestCard } from "./components/RequestCard";
import type { Transcript } from "./types";

type Tab = "queue" | "escalations";

export function App() {
  const [tab, setTab] = useState<Tab>("queue");
  const [queue, setQueue] = useState<Transcript[]>([]);
  const [escalations, setEscalations] = useState<Transcript[]>([]);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [q, e] = await Promise.all([fetchQueue(), fetchEscalations()]);
      setQueue(q);
      setEscalations(e);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const approve = useCallback(
    async (id: string) => {
      await resolveEscalation(id, "approve", "");
      await refresh();
    },
    [refresh],
  );

  const override = useCallback(
    async (id: string, note: string) => {
      await resolveEscalation(id, "override", note);
      await refresh();
    },
    [refresh],
  );

  const shown = tab === "queue" ? queue : escalations;

  return (
    <main className="app">
      <h1>AgentDesk Console</h1>
      <p className="sub">Customer-operations agent with confidence-gated handoff.</p>
      <nav className="tabs">
        <button className={tab === "queue" ? "active" : ""} onClick={() => setTab("queue")}>
          Queue ({queue.length})
        </button>
        <button
          className={tab === "escalations" ? "active" : ""}
          onClick={() => setTab("escalations")}
        >
          Escalations ({escalations.length})
        </button>
      </nav>
      {error && <p className="error">Cannot reach the service: {error}</p>}
      <section className="list">
        {shown.map((t) => (
          <RequestCard
            key={t.request_id}
            transcript={t}
            onApprove={approve}
            onOverride={override}
          />
        ))}
        {shown.length === 0 && !error && <p className="muted">Nothing here.</p>}
      </section>
    </main>
  );
}
