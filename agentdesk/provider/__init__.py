"""Model provider seam.

The agent talks to a provider through a small interface so the model can be
swapped without touching the agent loop. A deterministic fake is used in CI.
"""

from agentdesk.provider.base import Provider, ProviderStep
from agentdesk.provider.fake import FakeProvider

__all__ = ["Provider", "ProviderStep", "FakeProvider"]
