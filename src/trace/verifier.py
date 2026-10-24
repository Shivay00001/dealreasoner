"""Trace verifier: the anti-hallucination gate.

Every claim the agent makes in its reasoning must cite at least one evidence
ID ([E1]...) from the ACT bundle. Claims with no citation are dropped before
the verdict is shown — this is what makes the reasoning *verifiable* and the
decisions *reliable* (the Track 03 ask).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_CITE_RE = re.compile(r"\[E(\d+)\]")


@dataclass(frozen=True)
class VerifiedTrace:
    kept_claims: tuple[str, ...]
    dropped_claims: tuple[str, ...]
    evidence_ids: frozenset[str] = field(default_factory=frozenset)


def verify(text: str, valid_ids: set[str]) -> VerifiedTrace:
    kept: list[str] = []
    dropped: list[str] = []
    for line in (l.strip() for l in text.splitlines()):
        if not line:
            continue
        cited = {f"E{m}" for m in _CITE_RE.findall(line)}
        if cited and cited <= valid_ids:
            kept.append(line)
        else:
            dropped.append(line)
    return VerifiedTrace(
        kept_claims=tuple(kept),
        dropped_claims=tuple(dropped),
        evidence_ids=frozenset(valid_ids),
    )
