"""Deal memory: won/lost history with similarity retrieval.

The 'memory' in the Track 03 loop. Day 2: in-memory over the local seed KB.
Day 3+: backed by Zetaris (ZetarisClient.similar_deals). Retrieval key is
(niche, service) with budget-band as a secondary signal.
"""
from __future__ import annotations

from ..data.zetaris_client import DealRecord


class DealsMemory:
    def __init__(self, deals: list[DealRecord]):
        self._deals = deals

    def recall(self, niche: str, service: str, limit: int = 5) -> list[DealRecord]:
        def score(d: DealRecord) -> int:
            s = 0
            if d.niche.lower() == niche.lower():
                s += 2
            if d.service.lower() == service.lower():
                s += 2
            return s
        ranked = sorted(self._deals, key=score, reverse=True)
        hits = [d for d in ranked if score(d) > 0][:limit]
        return hits or ranked[:limit]

    def win_rate(self, niche: str) -> float | None:
        rel = [d for d in self._deals if d.niche.lower() == niche.lower()]
        if not rel:
            return None
        return sum(1 for d in rel if d.outcome == "won") / len(rel)
