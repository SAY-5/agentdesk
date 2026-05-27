export interface ToolCall {
  name: string;
  arguments: Record<string, unknown>;
  ok: boolean;
  result: Record<string, unknown> | null;
  error: string | null;
}

export interface Resolution {
  request_id: string;
  status: "resolved" | "escalated";
  proposal: string;
  confidence: number;
  reason: string;
}

export interface HumanDecision {
  decision: "approve" | "override";
  note: string;
}

export interface Transcript {
  request_id: string;
  request: Record<string, unknown>;
  tool_calls: ToolCall[];
  provider_signals: number[];
  resolution: Resolution | null;
  human_decision: HumanDecision | null;
}
