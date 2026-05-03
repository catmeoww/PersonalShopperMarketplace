"""Progressive autonomy tiers. PRD §12.5."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AutonomyTier:
    tier: int
    name: str
    auto_approve_under: float
    requires_previous_approval: bool
    description: str


# PRD §12.5
TIERS: dict[int, AutonomyTier] = {
    1: AutonomyTier(1, "approve-every", 0.0, False, "approve every action"),
    2: AutonomyTier(2, "reorder-trusted-under-20", 20.0, True, "auto-approve re-orders of previously approved exact items under $20"),
    3: AutonomyTier(3, "staples-trusted-under-30", 30.0, False, "auto-approve staples from trusted merchants under $30"),
    4: AutonomyTier(4, "staples-under-75", 75.0, False, "auto-approve staples under $75; post-commit reversal window"),
    5: AutonomyTier(5, "auto-reorder-cap", 0.0, False, "auto-reorder staples under user-set cap; weekly digest review"),
}


def downgrade(current: int) -> int:
    """Misfire drops one tier. PRD §12.5."""
    return max(1, current - 1)


def restore(current: int, successful_corrections: int) -> int:
    """Restored after 3 successful corrections. PRD §12.5."""
    if successful_corrections >= 3:
        return min(5, current + 1)
    return current
