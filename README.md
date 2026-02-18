<div align="center">

# AgentMesh Integrations

**Platform Plugins & Trust Providers for AgentMesh**

*Dify · LangChain · LangGraph · LlamaIndex · Agent Lightning · OpenAI Agents · OpenClaw · Nostr WoT · Moltbook*

[![GitHub Stars](https://img.shields.io/github/stars/imran-siddique/agentmesh-integrations?style=social)](https://github.com/imran-siddique/agentmesh-integrations/stargazers)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![AgentMesh](https://img.shields.io/badge/agentmesh-compatible-green.svg)](https://github.com/imran-siddique/agent-mesh)

> ⭐ **If this project helps you, please star it!** It helps others discover AgentMesh integrations.

> 🔗 **Part of the Agent Ecosystem** — [AgentMesh](https://github.com/imran-siddique/agent-mesh) (identity & trust) · [Agent OS](https://github.com/imran-siddique/agent-os) (governance) · [Agent SRE](https://github.com/imran-siddique/agent-sre) (reliability)

[Integrations](#available-integrations) • [Quick Start](#quick-start) • [Contributing](#contributing-a-new-integration) • [AgentMesh Core](https://github.com/imran-siddique/agent-mesh)

</div>

---

## Why a Separate Repo?

AgentMesh core is a lean, zero-external-dependency library. Platform integrations live here because they:

- **Have their own dependencies** — Dify, LangChain, Nostr libraries shouldn't bloat the core
- **Release independently** — A Dify plugin update shouldn't require a core release
- **Accept community contributions** — Lower barrier than modifying core

> **Note:** Framework adapters that wrap agent frameworks with governance (LangChain, CrewAI, LlamaIndex) live inside [Agent OS](https://github.com/imran-siddique/agent-os/tree/main/src/agent_os/integrations) because they are tightly coupled to the kernel. This repo contains platform-specific *plugins* and external *trust providers*.

## Available Integrations

| Integration | Package | Status | Description |
|---|---|---|---|
| [LangChain](langchain-agentmesh/) | `langchain-agentmesh` | ✅ Stable | Ed25519 identity, trust-gated tools, delegation chains, callbacks |
| [LangGraph](langgraph-trust/) | [`langgraph-trust`](https://pypi.org/project/langgraph-trust/) | ✅ Published (PyPI) | Trust-gated checkpoint nodes, governance policy enforcement, trust-aware routing |
| [LlamaIndex](llamaindex-agentmesh/) | `llama-index-agent-agentmesh` | ✅ Merged Upstream | Trust-verified workers, identity-aware query engines, delegation chains |
| [Agent Lightning](agent-lightning/) | — | ✅ Merged Upstream | Agent-OS governance adapters, reward shaping, governed RL training |
| [Dify Plugin](dify-plugin/) | `agentmesh-trust-layer` | ✅ Stable | Packaged `.difypkg` with peer verification, step auth, trust scoring |
| [Dify Middleware](dify/) | — | 📦 Archived | Flask middleware (archived — use the plugin instead) |
| [Moltbook](moltbook/) | — | ✅ Stable | AgentMesh governance skill for [Moltbook](https://moltbook.com) agent registry |
| [Nostr Web of Trust](nostr-wot/) | `agentmesh-nostr-wot` | 🚧 Scaffold | Trust scoring via [MaximumSats](https://github.com/joelklabo/maximumsats-mcp) NIP-85 WoT |
| [OpenAI Agents](openai-agents-trust/) | [`openai-agents-trust`](https://pypi.org/project/openai-agents-trust/) | ✅ Published (PyPI) | Trust guardrails, policy enforcement, governance hooks, trust-gated handoffs for OpenAI Agents SDK |
| [OpenClaw Skill](openclaw-skill/) | [`agentmesh-governance`](https://clawhub.ai/imran-siddique/agentmesh-governance) | ✅ Published (ClawHub) | Governance skill for [OpenClaw](https://openclaw.im) agents — policy enforcement, trust scoring, Ed25519 DIDs, Merkle audit |

## Quick Start

### LangChain — Trust-Gated Tool Execution

```bash
pip install langchain-agentmesh
```

```python
from langchain_agentmesh import CMVKIdentity, TrustGatedTool, TrustedToolExecutor

# Generate cryptographic identity (Ed25519)
identity = CMVKIdentity.generate("research-agent", capabilities=["search", "summarize"])

# Wrap any tool with trust requirements
gated_tool = TrustGatedTool(
    tool=search_tool,
    required_capabilities=["search"],
    min_trust_score=0.8,
)

# Execute with automatic identity verification
executor = TrustedToolExecutor(identity=identity)
result = executor.invoke(gated_tool, "query")
```

### Dify Plugin — Trust Verification in Workflows

1. Download `agentmesh-trust-layer.difypkg` from [`dify-plugin/`](dify-plugin/)
2. Upload via **Settings → Plugins → Install from Package** in Dify
3. Use the trust tools in your workflows:
   - **Verify Peer Agent** — Check identity before trusting data
   - **Verify Workflow Step** — Authorize each step by capability
   - **Record Interaction** — Update trust scores after collaboration
   - **Get Agent Identity** — Share your DID with other agents

### Nostr Web of Trust — Decentralized Trust Scoring

```bash
pip install agentmesh-nostr-wot
```

```python
from agentmesh.trust import TrustEngine
from agentmesh_nostr_wot import NostrWoTProvider

# Bridge Nostr WoT scores into AgentMesh trust engine
provider = NostrWoTProvider(wot_api="https://wot.klabo.world")
engine = TrustEngine(external_providers=[provider])

# Composite score: AgentMesh CMVK + Nostr WoT
score = await engine.get_trust_score("agent-123")
```

---

## Architecture

```
agentmesh (core library)              agentmesh-integrations (this repo)
┌──────────────────────┐             ┌─────────────────────────────────┐
│  TrustProvider       │◄─implements─│  NostrWoTProvider               │
│  CMVKIdentity        │◄─uses───────│  LangChain identity.py          │
│  TrustEngine         │◄─extends────│  Dify trust_manager.py          │
│  TransportLayer      │◄─implements─│  (future: NATS, gRPC, etc.)     │
│  StorageProvider     │◄─implements─│  (future: Redis, Postgres, etc.)│
└──────────────────────┘             └─────────────────────────────────┘
                                              │
                                     Depends on agentmesh core.
                                     Core NEVER imports from here.
```

### Where Do Integrations Live?

| Type | Location | Example |
|---|---|---|
| **Framework adapters** (wrap agent frameworks with governance) | [Agent OS `integrations/`](https://github.com/imran-siddique/agent-os/tree/main/src/agent_os/integrations) | LangChainKernel, CrewAIKernel |
| **Ecosystem bridges** (connect sibling projects) | [Agent SRE `integrations/`](https://github.com/imran-siddique/agent-sre/tree/main/src/agent_sre/integrations) | Agent OS bridge, AgentMesh bridge |
| **Platform plugins & trust providers** | **This repo** | Dify plugin, Nostr WoT, Moltbook |

---

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

### Integration Ideas We'd Love to See

- **Redis/PostgreSQL storage** — Persistent trust scores and audit logs
- **NATS/gRPC transport** — High-performance agent-to-agent messaging
- **OpenAI Agents SDK** — Trust-gated function calling for OpenAI agents
- **Autogen** — Trust verification in multi-agent conversations
- **A2A Protocol** — Google's Agent-to-Agent protocol bridge

---

## License

MIT — same as AgentMesh core.

---

<div align="center">

**Trust is the foundation. These integrations bring it to your platform.**

[AgentMesh](https://github.com/imran-siddique/agent-mesh) · [Agent OS](https://github.com/imran-siddique/agent-os) · [Agent SRE](https://github.com/imran-siddique/agent-sre)

</div>
