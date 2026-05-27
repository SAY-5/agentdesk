import type { ToolCall } from "../types";

interface Props {
  calls: ToolCall[];
}

export function ToolTrace({ calls }: Props) {
  if (calls.length === 0) {
    return <p className="muted">No tool calls.</p>;
  }
  return (
    <ol className="trace">
      {calls.map((call, i) => (
        <li key={i} className={call.ok ? "trace-ok" : "trace-fail"}>
          <code>{call.name}</code>
          <span className="args">{JSON.stringify(call.arguments)}</span>
          <span className="outcome">{call.ok ? "ok" : `error: ${call.error}`}</span>
        </li>
      ))}
    </ol>
  );
}
