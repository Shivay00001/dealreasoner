"""ACT: evidence gathering.

Pulls every evidence item the reasoning needs and tags each with a stable ID
(E1, E2, ...). Sources: the brief itself, the service profile, structured
signals extracted from the brief (budget band, red flags, decision-maker,
urgency, referral), deal memory (similar past won/lost deals), and prospect
signals. The verifier later checks that every claim in the trace points at
one of these IDs.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from ..config import ServiceProfile
from ..data import local_kb
from ..data.zetaris_client import DealRecord

_BUDGET_RE = re.compile(r"\$\s*([\d,]+(?:\.\d+)?)\s*(k)?", re.IGNORECASE)

_DM_HINTS = (
    "i decide", "i can sign", "i'll decide", "my call", "owner", "founder",
    "ceo", "partner", "managing director", "md ", "gm decides", "marketing head",
    "i run", "we run", "decision maker",
)
_URGENCY_HINTS = ("urgent", "asap", "before", "season", "weeks", "rush", "fast", "quick")
_REFERRAL_HINTS = ("referr", "recommend", "introduced by", "via ")
_RED_FLAG_HINTS = {
    "unpaid trial work": ("free audit", "free trial", "free work", "unpaid", "free full", "sample work"),
    "equity-only pay": ("equity", "revenue share instead", "no cash", "can't pay cash", "cannot pay cash"),
    "guarantee demand": ("guarantee", "guaranteed"),
    "price shopping": ("cheapest", "5 vendors", "comparing", "lowest quote"),
    "no decision maker involved": ("committee", "no budget", "exploring options"),
}


@dataclass(frozen=True)
class Evidence:
    eid: str  # E1, E2, ...
    source: str
    text: str


@dataclass
class EvidenceBundle:
    items: list[Evidence]

    def as_text(self) -> str:
        return "\n".join(f"[{e.eid}] ({e.source}) {e.text}" for e in self.items)

    def ids(self) -> set[str]:
        return {e.eid for e in self.items}


def _extract_hints(brief: str, profile: ServiceProfile) -> tuple[str, str]:
    """Best-match (niche, service) with plural-tolerant token matching plus
    service keyword aliases (e.g. 'whatsapp bot' -> AI agents / automation)."""
    low = " " + brief.lower() + " "

    def norm(s: str) -> set[str]:
        return {t.rstrip("s") for t in re.sub(r"[^a-z ]", " ", s.lower()).split()}

    niche = "unknown"
    for n in profile.preferred_niches:
        if n.lower() in low:
            niche = n
            break
    if niche == "unknown":
        for n in profile.preferred_niches:
            toks = norm(n)
            if toks and all(t in norm(brief) for t in toks):
                niche = n
                break

    aliases: dict[str, tuple[str, ...]] = {
        "AI agents / automation": ("ai agent", "chatbot", "whatsapp bot", "bot ",
                                   "automation", "intake agent", "receptionist",
                                   "lead qualif"),
        "websites": ("website", "web site", "landing page", "5-page", "5 page"),
        "SEO": ("seo", "google ranking", "rank on google", "#1 on google"),
        "ad management": ("ad management", "roas", "ad spend", "running ads", "ads management"),
    }
    service, best = "unknown", 0
    for s in profile.services:
        keywords = aliases.get(s, ()) + tuple(norm(s))
        hits = sum(1 for k in keywords if k and k in low)
        if hits > best:
            best, service = hits, s
    return niche, service


def extract_budget_usd(brief: str) -> int | None:
    m = _BUDGET_RE.search(brief)
    if not m:
        return None
    amt = float(m.group(1).replace(",", ""))
    if m.group(2):
        amt *= 1000
    return int(amt)


def extract_signals(brief: str, profile: ServiceProfile) -> list[str]:
    """Deterministic structured signals from the brief text."""
    low = brief.lower()
    signals: list[str] = []

    budget = extract_budget_usd(brief)
    lo, hi = profile.price_band_usd
    if budget is None:
        signals.append("budget: not disclosed")
    elif budget < lo:
        signals.append(f"budget: ${budget:,} below price band (${lo:,}-${hi:,})")
    elif budget > hi:
        signals.append(f"budget: ${budget:,} above price band (${lo:,}-${hi:,})")
    else:
        signals.append(f"budget: ${budget:,} inside price band (${lo:,}-${hi:,})")

    if any(h in low for h in _DM_HINTS):
        signals.append("decision maker: present in thread")
    else:
        signals.append("decision maker: unclear")

    flags = [f for f, hints in _RED_FLAG_HINTS.items() if any(h in low for h in hints)]
    for f in flags:
        signals.append(f"red flag: {f}")

    if any(h in low for h in _URGENCY_HINTS):
        signals.append("urgency: time pressure mentioned")
    if any(h in low for h in _REFERRAL_HINTS):
        signals.append("trust: referral or warm introduction")

    return signals


def gather(brief: str, profile: ServiceProfile,
           zetaris=None) -> EvidenceBundle:
    """Gather evidence. When a Zetaris client is passed, deals + prospect
    signals come from Zetaris SQL; on any Zetaris error the local KB is
    used AND a transparent trace item records the fallback (never silent)."""
    items: list[Evidence] = []
    n = 0

    def add(source: str, text: str) -> None:
        nonlocal n
        n += 1
        items.append(Evidence(eid=f"E{n}", source=source, text=text))

    add("brief", brief.strip()[:600])
    niche, service = _extract_hints(brief, profile)
    add("profile", f"services={list(profile.services)} price_band=${profile.price_band_usd[0]}-"
                   f"${profile.price_band_usd[1]} red_flags={list(profile.red_flags)}")

    signals = extract_signals(brief, profile)
    add("signals", " | ".join(signals))

    deals = None
    if zetaris is not None:
        try:
            deals = zetaris.similar_deals(niche, service)
        except Exception as exc:  # noqa: BLE001 — fallback must never hide
            add("zetaris:status",
                f"Zetaris query failed ({exc}); local KB fallback used.")
    if deals is None:
        deals = local_kb.similar_deals(local_kb.load_deals(), niche, service)
    for d in deals:
        add(d.source, f"deal {d.deal_id} {d.outcome}: {d.niche}/{d.service} "
                      f"budget={d.budget_usd} — {d.reason}")

    pe = None
    if zetaris is not None:
        try:
            pe = zetaris.prospect_evidence("")
        except Exception as exc:  # noqa: BLE001
            add("zetaris:status",
                f"Zetaris prospect query failed ({exc}); brief-only signals used.")
    if pe is None:
        pe = local_kb.prospect_evidence("")
    for sig in pe.signals:
        add(pe.source, sig)

    return EvidenceBundle(items=items)
