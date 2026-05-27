interface Props {
  value: number;
}

export function ConfidenceBar({ value }: Props) {
  const pct = Math.round(value * 100);
  const tone = value >= 0.7 ? "ok" : value >= 0.4 ? "warn" : "low";
  return (
    <div className="confidence" aria-label={`confidence ${pct} percent`}>
      <div className={`confidence-fill ${tone}`} style={{ width: `${pct}%` }} />
      <span className="confidence-label">{pct}%</span>
    </div>
  );
}
