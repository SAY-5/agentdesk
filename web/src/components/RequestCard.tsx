import type { Transcript } from "../types";
import { ConfidenceBar } from "./ConfidenceBar";
import { ToolTrace } from "./ToolTrace";

interface Props {
  transcript: Transcript;
  onApprove?: (id: string) => void;
  onOverride?: (id: string, note: string) => void;
}

export function RequestCard({ transcript, onApprove, onOverride }: Props) {
  const res = transcript.resolution;
  const status = res?.status ?? "pending";
  const escalated = status === "escalated";
  const text = String(transcript.request.text ?? transcript.request.intent ?? "");

  return (
    <article className={`card status-${status}`}>
      <header>
        <span className="rid">{transcript.request_id}</span>
        <span className={`badge badge-${status}`}>{status}</span>
      </header>
      <p className="request-text">{text}</p>
      <ToolTrace calls={transcript.tool_calls} />
      {res && (
        <div className="resolution">
          <ConfidenceBar value={res.confidence} />
          <p className="proposal">{res.proposal || res.reason}</p>
          {transcript.human_decision && (
            <p className="human">
              human {transcript.human_decision.decision}
              {transcript.human_decision.note ? `: ${transcript.human_decision.note}` : ""}
            </p>
          )}
        </div>
      )}
      {escalated && onApprove && onOverride && !transcript.human_decision && (
        <div className="actions">
          <button onClick={() => onApprove(transcript.request_id)}>Approve</button>
          <button
            onClick={() => onOverride(transcript.request_id, "handled manually")}
          >
            Override
          </button>
        </div>
      )}
    </article>
  );
}
