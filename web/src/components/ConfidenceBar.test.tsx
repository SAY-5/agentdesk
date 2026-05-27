import { render, screen } from "@testing-library/react";
import { ConfidenceBar } from "./ConfidenceBar";

test("shows the percentage", () => {
  render(<ConfidenceBar value={0.42} />);
  expect(screen.getByText("42%")).toBeInTheDocument();
});

test("marks low confidence", () => {
  const { container } = render(<ConfidenceBar value={0.2} />);
  expect(container.querySelector(".confidence-fill.low")).not.toBeNull();
});
