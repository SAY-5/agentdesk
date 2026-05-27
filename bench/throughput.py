"""Request-handling throughput benchmark.

Runs a batch of requests through the agent loop with the fake provider and
reports requests per second. Output is JSON so the CI smoke gate can parse it.
No network and no randomness, so a number here reflects the agent and tool
machinery rather than an external service.
"""

from __future__ import annotations

import argparse
import json
import time

from agentdesk.backend import Backend
from agentdesk.core import Agent
from agentdesk.provider import FakeProvider
from agentdesk.sample_requests import SAMPLE_REQUESTS
from agentdesk.tools import build_registry


def run_batch(batch: int) -> dict:
    requests = []
    for i in range(batch):
        base = SAMPLE_REQUESTS[i % len(SAMPLE_REQUESTS)]
        requests.append({**base, "id": f"{base['id']}-{i}"})

    # a fresh backend per request keeps refunds independent across the batch
    start = time.perf_counter()
    handled = 0
    for request in requests:
        agent = Agent(build_registry(Backend()), FakeProvider())
        agent.handle(request)
        handled += 1
    elapsed = time.perf_counter() - start

    rps = handled / elapsed if elapsed > 0 else 0.0
    return {
        "requests": handled,
        "seconds": round(elapsed, 6),
        "requests_per_second": round(rps, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=2000)
    args = parser.parse_args()
    print(json.dumps(run_batch(args.batch)))


if __name__ == "__main__":
    main()
