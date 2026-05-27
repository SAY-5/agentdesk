"""bench-regress smoke gate.

Runs the throughput benchmark and compares it against the recorded baseline in
bench/baseline.json. If throughput drops by more than the allowed fraction
(30% by default) the gate fails. This is a smoke check against a large
regression, not a precise timing assertion, so it tolerates normal variance.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bench.throughput import run_batch

BASELINE = Path(__file__).parent / "baseline.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=2000)
    parser.add_argument("--max-drop", type=float, default=0.30)
    args = parser.parse_args()

    baseline = json.loads(BASELINE.read_text())["requests_per_second"]
    result = run_batch(args.batch)
    current = result["requests_per_second"]
    floor = baseline * (1.0 - args.max_drop)

    print(json.dumps({"baseline": baseline, "current": current, "floor": round(floor, 2)}))

    if current < floor:
        print(f"regression: {current} rps is below floor {floor:.2f} rps", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
