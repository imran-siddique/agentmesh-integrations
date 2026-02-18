"""Semantic intent classification for tool calls.

Deterministic, weighted-signal classifier — no LLM dependency.
Categorizes tool call intent into threat categories with confidence scores.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple


class SemanticIntent(Enum):
    """Threat categories for tool call classification."""

    DESTRUCTIVE_DATA = "destructive_data"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SYSTEM_MODIFICATION = "system_modification"
    CODE_EXECUTION = "code_execution"
    NETWORK_ACCESS = "network_access"
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    BENIGN = "benign"


@dataclass
class IntentClassification:
    """Result of semantic intent classification."""

    intent: SemanticIntent
    confidence: float
    signals: List[str] = field(default_factory=list)


# Weighted signal patterns: (regex, weight, intent, signal_description)
_SIGNALS: List[Tuple[re.Pattern, float, SemanticIntent, str]] = [
    # Destructive data operations
    (re.compile(r"drop\s+table", re.I), 0.9, SemanticIntent.DESTRUCTIVE_DATA, "DROP TABLE"),
    (re.compile(r"delete\s+from\s+\w+\s*$", re.I), 0.85, SemanticIntent.DESTRUCTIVE_DATA, "DELETE without WHERE"),
    (re.compile(r"truncate\s+", re.I), 0.9, SemanticIntent.DESTRUCTIVE_DATA, "TRUNCATE"),
    (re.compile(r"rm\s+-rf", re.I), 0.95, SemanticIntent.DESTRUCTIVE_DATA, "rm -rf"),
    (re.compile(r"format\s+[a-z]:", re.I), 0.9, SemanticIntent.DESTRUCTIVE_DATA, "format drive"),
    (re.compile(r"wipe|destroy|nuke|obliterate", re.I), 0.7, SemanticIntent.DESTRUCTIVE_DATA, "destructive keyword"),
    # Data exfiltration
    (re.compile(r"curl.*\|\s*bash", re.I), 0.9, SemanticIntent.DATA_EXFILTRATION, "curl pipe to bash"),
    (re.compile(r"(wget|curl).*(-o|>)\s*\S+", re.I), 0.6, SemanticIntent.DATA_EXFILTRATION, "download to file"),
    (re.compile(r"base64.*encode", re.I), 0.5, SemanticIntent.DATA_EXFILTRATION, "base64 encoding"),
    (re.compile(r"scp\s|rsync\s|ftp\s", re.I), 0.7, SemanticIntent.DATA_EXFILTRATION, "file transfer"),
    # Privilege escalation
    (re.compile(r"sudo\s", re.I), 0.8, SemanticIntent.PRIVILEGE_ESCALATION, "sudo"),
    (re.compile(r"chmod\s+[0-7]*7", re.I), 0.7, SemanticIntent.PRIVILEGE_ESCALATION, "chmod world-writable"),
    (re.compile(r"chown\s+root", re.I), 0.8, SemanticIntent.PRIVILEGE_ESCALATION, "chown to root"),
    (re.compile(r"su\s+-?\s*root", re.I), 0.9, SemanticIntent.PRIVILEGE_ESCALATION, "switch to root"),
    # System modification
    (re.compile(r"/etc/(passwd|shadow|sudoers)", re.I), 0.9, SemanticIntent.SYSTEM_MODIFICATION, "system config file"),
    (re.compile(r"systemctl\s+(stop|disable|mask)", re.I), 0.7, SemanticIntent.SYSTEM_MODIFICATION, "service control"),
    (re.compile(r"registry|regedit", re.I), 0.6, SemanticIntent.SYSTEM_MODIFICATION, "registry access"),
    # Code execution
    (re.compile(r"eval\s*\(?", re.I), 0.8, SemanticIntent.CODE_EXECUTION, "eval()"),
    (re.compile(r"exec\s*\(?", re.I), 0.8, SemanticIntent.CODE_EXECUTION, "exec()"),
    (re.compile(r"__import__\s*\(", re.I), 0.7, SemanticIntent.CODE_EXECUTION, "__import__()"),
    (re.compile(r"subprocess\.(run|call|Popen)", re.I), 0.7, SemanticIntent.CODE_EXECUTION, "subprocess"),
    # Network access
    (re.compile(r"0\.0\.0\.0|INADDR_ANY", re.I), 0.6, SemanticIntent.NETWORK_ACCESS, "bind all interfaces"),
    (re.compile(r"socket\.(listen|bind)", re.I), 0.5, SemanticIntent.NETWORK_ACCESS, "socket server"),
]


def classify_intent(
    text: str,
    tool_name: str = "",
    arguments: Dict[str, str] | None = None,
) -> IntentClassification:
    """Classify the semantic intent of a tool call.

    Combines tool name, argument values, and text content to produce
    a weighted classification. Returns the highest-confidence match.

    Args:
        text: The primary text content to classify.
        tool_name: Name of the tool being called.
        arguments: Tool call arguments as key-value pairs.

    Returns:
        IntentClassification with intent, confidence, and matched signals.
    """
    combined = text
    if tool_name:
        combined = f"{tool_name} {combined}"
    if arguments:
        combined = f"{combined} {' '.join(str(v) for v in arguments.values())}"

    matches: Dict[SemanticIntent, List[Tuple[float, str]]] = {}

    for pattern, weight, intent, description in _SIGNALS:
        if pattern.search(combined):
            if intent not in matches:
                matches[intent] = []
            matches[intent].append((weight, description))

    if not matches:
        return IntentClassification(
            intent=SemanticIntent.BENIGN,
            confidence=1.0,
            signals=["no threat signals detected"],
        )

    # Pick the intent with the highest aggregate confidence
    best_intent = SemanticIntent.BENIGN
    best_score = 0.0
    best_signals: List[str] = []

    for intent, signals in matches.items():
        # Combine signals: max weight + diminishing returns for additional signals
        weights = sorted([w for w, _ in signals], reverse=True)
        score = weights[0]
        for w in weights[1:]:
            score += w * 0.2  # Additional signals add 20% of their weight
        score = min(score, 1.0)

        if score > best_score:
            best_score = score
            best_intent = intent
            best_signals = [desc for _, desc in signals]

    return IntentClassification(
        intent=best_intent,
        confidence=best_score,
        signals=best_signals,
    )
