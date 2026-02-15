# AgentMesh Integrations

Community-contributed integrations for [AgentMesh](https://github.com/imran-siddique/agent-mesh) — the trust-first multi-agent communication framework.

> **Why a separate repo?** AgentMesh core is a lean, zero-external-dependency library. Integrations live here so they can iterate independently, own their own release cadence, and keep the dependency graph clean.

## Available Integrations

| Integration | Package | Status | Description |
|---|---|---|---|
| [Nostr Web of Trust](nostr-wot/) | `agentmesh-nostr-wot` | 🚧 Scaffold | Trust scoring via [MaximumSats](https://github.com/joelklabo/maximumsats-mcp) NIP-85 WoT |

## Architecture

Each integration implements one or more AgentMesh interfaces:

```
agentmesh (core)                    agentmesh-integrations (this repo)
┌──────────────────┐               ┌──────────────────────────┐
│  TrustProvider   │◄──implements──│  NostrWoTProvider        │
│  TransportLayer  │◄──implements──│  (future transports)     │
│  StorageProvider │◄──implements──│  (future storage)        │
└──────────────────┘               └──────────────────────────┘
```

**Key principle**: Integrations depend on `agentmesh` — not the other way around. Core never imports from here.

## Contributing a New Integration

1. Create a directory: `your-integration/`
2. Implement the relevant AgentMesh interface (e.g., `TrustProvider`)
3. Include: `pyproject.toml`, `README.md`, `tests/`, and a working example
4. Open a PR — maintainers will review and help you get it published

### Directory Structure

```
your-integration/
├── agentmesh_your_integration/
│   ├── __init__.py
│   └── provider.py          # Implements AgentMesh interface
├── tests/
│   └── test_provider.py
├── pyproject.toml            # pip install agentmesh-your-integration
├── README.md
└── examples/
    └── basic_usage.py
```

### Interface Contract

All trust providers must implement:

```python
from agentmesh.trust import TrustProvider

class YourProvider(TrustProvider):
    async def get_trust_score(self, agent_id: str) -> float:
        """Return trust score between 0.0 and 1.0"""
        ...

    async def verify_identity(self, agent_id: str, credentials: dict) -> bool:
        """Verify agent identity via your system"""
        ...
```

## License

MIT — same as AgentMesh core.
