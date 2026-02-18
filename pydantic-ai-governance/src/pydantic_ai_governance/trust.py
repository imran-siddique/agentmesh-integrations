"""Trust scoring for PydanticAI agents.

Multi-dimensional trust tracking with decay, reward/penalty,
and threshold validation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TrustScore:
    """Multi-dimensional trust score for an agent.

    All dimensions are 0.0-1.0. The overall score is a weighted average.
    """

    overall: float = 0.5
    reliability: float = 0.5
    capability: float = 0.5
    security: float = 0.5
    compliance: float = 0.5
    history: float = 0.5
    last_updated: float = field(default_factory=time.time)

    _WEIGHTS: Dict[str, float] = field(
        default_factory=lambda: {
            "reliability": 0.25,
            "capability": 0.20,
            "security": 0.25,
            "compliance": 0.20,
            "history": 0.10,
        },
        repr=False,
    )

    def compute_overall(self) -> float:
        """Compute weighted overall score from dimensions."""
        total = 0.0
        for dim, weight in self._WEIGHTS.items():
            total += getattr(self, dim) * weight
        self.overall = round(min(max(total, 0.0), 1.0), 4)
        self.last_updated = time.time()
        return self.overall

    def to_dict(self) -> Dict[str, float]:
        """Serialize to dictionary."""
        return {
            "overall": self.overall,
            "reliability": self.reliability,
            "capability": self.capability,
            "security": self.security,
            "compliance": self.compliance,
            "history": self.history,
        }


class TrustScorer:
    """Manages trust scores for multiple agents.

    Tracks success/failure across dimensions with configurable
    reward/penalty rates and time-based decay.
    """

    def __init__(
        self,
        reward_rate: float = 0.05,
        penalty_rate: float = 0.10,
        decay_rate: float = 0.01,
    ) -> None:
        self._scores: Dict[str, TrustScore] = {}
        self.reward_rate = reward_rate
        self.penalty_rate = penalty_rate
        self.decay_rate = decay_rate

    def get_score(self, agent_id: str) -> TrustScore:
        """Get or create trust score for an agent."""
        if agent_id not in self._scores:
            self._scores[agent_id] = TrustScore()
            self._scores[agent_id].compute_overall()
        return self._scores[agent_id]

    def record_success(
        self,
        agent_id: str,
        dimensions: Optional[List[str]] = None,
    ) -> TrustScore:
        """Record a successful action, boosting specified dimensions."""
        score = self.get_score(agent_id)
        dims = dimensions or ["reliability"]
        for dim in dims:
            if hasattr(score, dim):
                current = getattr(score, dim)
                new_val = min(current + self.reward_rate, 1.0)
                setattr(score, dim, round(new_val, 4))
        score.compute_overall()
        return score

    def record_failure(
        self,
        agent_id: str,
        dimensions: Optional[List[str]] = None,
    ) -> TrustScore:
        """Record a failed action, penalizing specified dimensions."""
        score = self.get_score(agent_id)
        dims = dimensions or ["reliability"]
        for dim in dims:
            if hasattr(score, dim):
                current = getattr(score, dim)
                new_val = max(current - self.penalty_rate, 0.0)
                setattr(score, dim, round(new_val, 4))
        score.compute_overall()
        return score

    def apply_decay(self, agent_id: str, hours_elapsed: float = 1.0) -> TrustScore:
        """Apply time-based decay to trust scores."""
        score = self.get_score(agent_id)
        decay = self.decay_rate * hours_elapsed
        for dim in ["reliability", "capability", "security", "compliance", "history"]:
            current = getattr(score, dim)
            new_val = max(current - decay, 0.0)
            setattr(score, dim, round(new_val, 4))
        score.compute_overall()
        return score

    def check_trust(
        self,
        agent_id: str,
        min_overall: float = 0.3,
        min_dimensions: Optional[Dict[str, float]] = None,
    ) -> bool:
        """Check if an agent meets trust thresholds."""
        score = self.get_score(agent_id)
        if score.overall < min_overall:
            return False
        if min_dimensions:
            for dim, threshold in min_dimensions.items():
                if hasattr(score, dim) and getattr(score, dim) < threshold:
                    return False
        return True
