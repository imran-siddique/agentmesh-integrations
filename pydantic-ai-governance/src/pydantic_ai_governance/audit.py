"""Audit trail for governance decisions."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from pydantic_ai_governance.policy import GovernanceEventType


@dataclass
class AuditEntry:
    """Single governance decision record."""

    timestamp: float
    event_type: GovernanceEventType
    tool_name: str
    allowed: bool
    reason: Optional[str] = None
    agent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "tool_name": self.tool_name,
            "allowed": self.allowed,
            "reason": self.reason,
            "agent_id": self.agent_id,
            "metadata": self.metadata,
        }


class AuditTrail:
    """Append-only audit trail for governance decisions.

    Records every policy check, violation, and tool call decision
    for compliance and forensics.
    """

    def __init__(self) -> None:
        self._entries: List[AuditEntry] = []

    def record(
        self,
        event_type: GovernanceEventType,
        tool_name: str,
        allowed: bool,
        reason: Optional[str] = None,
        agent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        """Record a governance decision."""
        entry = AuditEntry(
            timestamp=time.time(),
            event_type=event_type,
            tool_name=tool_name,
            allowed=allowed,
            reason=reason,
            agent_id=agent_id,
            metadata=metadata or {},
        )
        self._entries.append(entry)
        return entry

    @property
    def entries(self) -> List[AuditEntry]:
        """Get all audit entries."""
        return list(self._entries)

    @property
    def violations(self) -> List[AuditEntry]:
        """Get only violation entries."""
        return [e for e in self._entries if not e.allowed]

    def summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        total = len(self._entries)
        blocked = len(self.violations)
        return {
            "total_checks": total,
            "allowed": total - blocked,
            "blocked": blocked,
            "block_rate": round(blocked / total, 4) if total > 0 else 0.0,
            "by_event_type": self._count_by_event_type(),
        }

    def _count_by_event_type(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for entry in self._entries:
            key = entry.event_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts
