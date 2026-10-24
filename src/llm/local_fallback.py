"""Offline deterministic mock LLM for Day 2 pipeline development and evals.

Rule-shaped, fully deterministic outputs so the THINK plumbing runs end to
end without credentials. Parses the EVIDENCE block it is given, classifies
deal records and signals, and emits exactly 3 hypotheses with real evidence
IDs as citations. NEVER used in the submitted demo path (NVIDIA Nemotron via
Meterless takes over on Day 4).
"""
from __future__ import annotations

import re

from .base import LLMProvider, LLMResponse

_EVID_LINE_RE = re.compile(r"\[(E\d+)\]\s*\(([^)]*)\)\s*(.*)")


def _classify_evidence(user: str):
    brief_id, won, lost, flags, budget_id, dm_id = None, [], [], [], None, None
    for m in _EVID_LINE_RE.finditer(user):
        eid, source, text = m.group(1), m.group(2), m.group(3)
        low = text.lower()
        if source == "brief":
            brief_id = eid
        if "deal memory" in source or source.startswith(("local:", "zetaris:")):
            if "won:" in low or " won " in low or low.startswith("deal d"):
                if " won" in low or "won:" in low:
                    won.append((eid, text))
                elif " lost" in low or "lost:" in low:
                    lost.append((eid, text))
        if source == "signals":
            if "red flag:" in low:
                flags.append((eid, text))
            if low.startswith("budget:"):
                budget_id = eid
            if "decision maker:" in low:
                dm_id = eid
    return brief_id, won, lost, flags, budget_id, dm_id


def _mk_hypotheses(user: str) -> str:
    brief_id, won, lost, flags, budget_id, dm_id = _classify_evidence(user)
    brief_id = brief_id or "E1"
    won_ids = " ".join(f"[{e}]" for e, _ in won[:2])
    lost_ids = " ".join(f"[{e}]" for e, _ in lost[:2])
    flag_ids = " ".join(f"[{e}]" for e, _ in flags[:2])
    budget_cite = f"[{budget_id}]" if budget_id else f"[{brief_id}]"

    if won and not lost:
        h1 = (f"H1: Good fit — brief matches the service demand and past won "
              f"deals show this pattern closes {won_ids} [{brief_id}].")
    elif won:
        h1 = (f"H1: Good fit — past wins {won_ids} resemble this brief "
              f"{budget_cite} [{brief_id}].")
    else:
        h1 = (f"H1: Possible fit — brief describes a real need but no close "
              f"past win in memory {budget_cite} [{brief_id}].")

    if lost:
        h2 = (f"H2: Weak fit — similar past deals were lost {lost_ids}, "
              f"so scope or budget mismatch is plausible [{brief_id}].")
    else:
        h2 = (f"H2: Uncertain fit — no comparable lost deal, but the brief is "
              f"thin on scope detail {budget_cite} [{brief_id}].")

    if flags:
        h3 = (f"H3: Red flags — signals match known bad patterns: {flag_ids} "
              f"[{brief_id}].")
    else:
        h3 = (f"H3: Red flags — no explicit red-flag signals; verify budget "
              f"authority and decision maker before a call {budget_cite} "
              f"[{brief_id}].")

    return "\n".join([h1, h2, h3])


class LocalFallback(LLMProvider):
    name = "local-fallback"

    def generate(self, system: str, user: str, max_tokens: int = 800) -> LLMResponse:
        if "hypothes" in system.lower():
            return LLMResponse(text=_mk_hypotheses(user), model=self.name)
        return LLMResponse(text="fallback: no signal", model=self.name)
