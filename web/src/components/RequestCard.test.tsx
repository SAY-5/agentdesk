import { fireEvent, render, screen } from "@testing-library/react";
import { RequestCard } from "./RequestCard";
import type { Transcript } from "../types";

const escalated: Transcript = {
  request_id: "R6",
  request: { intent: "complaint", text: "I want a person" },
  tool_calls: [],
  provider_signals: [0.2],
  resolution: {
    request_id: "R6",
    status: "escalated",
    proposal: "",
    confidence: 0.2,
    reason: "confidence below threshold",
  },
  human_decision: null,
};

test("renders the escalated badge and offers approve", () => {
  const onApprove = vi.fn();
  render(
    <RequestCard transcript={escalated} onApprove={onApprove} onOverride={vi.fn()} />,
  );
  expect(screen.getByText("escalated")).toBeInTheDocument();
  fireEvent.click(screen.getByText("Approve"));
  expect(onApprove).toHaveBeenCalledWith("R6");
});

test("hides actions once a human has decided", () => {
  const decided = { ...escalated, human_decision: { decision: "approve" as const, note: "" } };
  render(<RequestCard transcript={decided} onApprove={vi.fn()} onOverride={vi.fn()} />);
  expect(screen.queryByText("Approve")).toBeNull();
  expect(screen.getByText(/human approve/)).toBeInTheDocument();
});
