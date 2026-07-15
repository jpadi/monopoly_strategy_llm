from __future__ import annotations

from Monopoly.StaticEvaluation.Domain.Model.Algorithm.DangerousMonopolyAvailabilityEvidence import (
    DangerousMonopolyAvailabilityEvidence,
    buildDangerousMonopolyAvailabilityEvidence,
)
from Monopoly.StaticEvaluation.Domain.Model.BoardContext import BoardContext


def isDangerousMonopolyAvailable(
    ctx: BoardContext,
    opponentId: str,
    groupId: str,
    *,
    boardStateKey: str = "board_state_before",
) -> tuple[bool, DangerousMonopolyAvailabilityEvidence]:
    """Dangerous Monopoly Available predicate with auditable evidence."""
    evidence = buildDangerousMonopolyAvailabilityEvidence(
        ctx,
        opponentId,
        groupId,
        boardStateKey=boardStateKey,
    )
    return evidence.result, evidence


def isFullyBlockedBoard(ctx: BoardContext, playerId: str) -> bool:
    """Fully Blocked Board: no opponent has Dangerous Monopoly Available."""
    for opponentId in ctx.opponentIds(playerId):
        for gid in ctx.streetGroups():
            avail, _ = isDangerousMonopolyAvailable(ctx, opponentId, gid)
            if avail:
                return False
    return True
