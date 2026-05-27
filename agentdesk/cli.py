"""Command-line demo: run the sample requests through the agent and print
each resolution. Used for a quick manual check; the API server and tests are
the primary interfaces.
"""

from __future__ import annotations

import json

from agentdesk.backend import Backend
from agentdesk.core import Agent
from agentdesk.provider import FakeProvider
from agentdesk.sample_requests import SAMPLE_REQUESTS
from agentdesk.tools import build_registry


def main() -> None:
    backend = Backend()
    registry = build_registry(backend)
    agent = Agent(registry, FakeProvider())
    for request in SAMPLE_REQUESTS:
        transcript = agent.handle(request)
        resolution = transcript.resolution
        assert resolution is not None
        print(
            json.dumps(
                {
                    "request_id": resolution.request_id,
                    "status": resolution.status,
                    "confidence": resolution.confidence,
                    "proposal": resolution.proposal,
                    "reason": resolution.reason,
                }
            )
        )


if __name__ == "__main__":
    main()
