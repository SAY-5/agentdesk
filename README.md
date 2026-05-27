# AgentDesk

AgentDesk is a customer-operations agent. It takes an inbound customer request,
runs a tool-calling loop against a backend to gather what it needs, and either
resolves the request on its own or hands it to a human when its confidence is
too low. A React console gives an operator oversight of the queue, the tool
trace behind each request, the proposed resolution and its confidence, and the
escalations awaiting a decision.

## How it works

A request flows through four pieces:

- **Model provider seam.** The agent asks a provider for the next step: either
  a tool to call or a final proposal with a signal score in `[0, 1]`. The
  provider sits behind a small interface so it can be swapped. A deterministic
  fake provider drives the tests and the demo, so the whole system runs offline.
- **Tool interface.** A registry of named tools (`lookup_order`,
  `check_refund_eligibility`, `issue_refund`, `update_address`, `get_account`),
  each with a parameter schema. Every call is validated against its schema, and
  the agent can only call tools on the allowlist. A tool error is captured, not
  raised through the loop.
- **Mock backend.** An in-memory order and account store that the tools run
  against, seeded with deterministic data.
- **Agent loop.** Drives the provider and the tools, builds a transcript, scores
  confidence, and decides between resolving and escalating.

## Confidence-gated handoff

The agent does not act when it is unsure. Confidence is the product of two
observable quantities:

- the provider's signal for its final proposal, and
- the fraction of the agent's tool calls that succeeded (completeness).

Taking the product means a weak signal or any failed tool call pulls confidence
down. A request whose confidence is at or above the threshold (default `0.7`)
is resolved automatically; below it the request escalates to a human. The
threshold is tunable, so an operator can trade automation rate against the risk
of acting when the picture is incomplete. See `agentdesk/core/confidence.py`.

## Audit trail and human-in-loop

Every handled request keeps a full transcript: each tool call with its result
or error, each provider signal, and the final decision with its confidence. A
human can replay an escalation from that transcript and approve or override it;
the decision is recorded back onto the transcript. See `agentdesk/audit.py`.

## Running it

Python core and API:

```bash
pip install -e ".[dev]"
agentdesk          # run the sample requests through the agent and print results
agentdesk-serve    # start the JSON API on port 8000
```

Console:

```bash
cd web
npm install
npm run dev        # proxies /api to the Python service on port 8000
```

Both together with Docker:

```bash
docker compose up --build
# console on http://localhost:5173
```

## Tests

```bash
pytest                         # Python unit tests
cd web && npm run test         # console component tests
cd e2e && npx playwright test  # end-to-end against the compose stack
```

## How this differs

This is one of a few separate agent projects, each with a distinct shape:

- **agentdesk** (this repo) is the customer-operations agent: tool calling into
  a backend, calibrated confidence, and a human-in-loop escalation with an
  oversight console.
- **reviewmate** focuses on code review.
- **talentagent** focuses on candidate matching.
- **mcp-agentlab** is a general framework.

The angle here is customer-ops tool calling with a calibrated confidence score
and a human handoff, rather than a general framework or a single-domain
reviewer.

## License

MIT. See `LICENSE`.
