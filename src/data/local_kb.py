"""Local JSON knowledge base — Day 2 stand-in for Zetaris.

Same record shapes as ZetarisClient so the pipeline is swappable.
Demoted to fallback-only once real Zetaris wiring lands (Day 3).
"""
from __future__ import annotations

import json
from pathlib import Path

from .zetaris_client import DealRecord, ProspectEvidence

_SEED = Path(__file__).with_name("seed_deals.json")


def load_deals() -> list[DealRecord]:
    if not _SEED.exists():
        return []
    raw = json.loads(_SEED.read_text())
    return [DealRecord(**{**d, "source": "local:seed_deals"}) for d in raw]


def similar_deals(deals: list[DealRecord], niche: str, service: str,
                  limit: int = 5) -> list[DealRecord]:
    def score(d: DealRecord) -> int:
        s = 0
        if d.niche.lower() == niche.lower():
            s += 2
        if d.service.lower() == service.lower():
            s += 2
        return s
    ranked = sorted(deals, key=score, reverse=True)
    return [d for d in ranked if score(d) > 0][:limit] or ranked[:limit]


def prospect_evidence(prospect_hint: str) -> ProspectEvidence:
    # Day 2: no external lookup; the brief itself is the only prospect signal.
    return ProspectEvidence(
        prospect=prospect_hint or "unknown",
        signals=("no external prospect data in offline mode",),
        source="local:brief-only",
    )
