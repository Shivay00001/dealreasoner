"""DECIDE: scored, calibrated verdict with abstention.

Adjudicates the THINK hypotheses against the evidence and returns one of
GO / NO-GO / PILOT / ESCALATE.

Scoring backend priority (Shivay's standing rule: Jev first):
1. Jev API (via jev_curl.py) — `score` rubric over deal-fit levels, mapped to
   verdicts by calibrated thresholds.
2. If Jev is unreachable: documented deterministic local heuristic scorer
   (_local_score). Same verdict mapping, coarser confidence.

Abstention policy (the "reliable" behaviour of the track): when the evidence
is too thin to decide (no budget signal AND no red flags) or the scorer is
uncertain (confidence < escalate_below), the agent ESCALATES to the human
with the missing information instead of guessing.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from ..config import Settings
from .act import EvidenceBundle
from .think import Hypothesis

VERDICTS = ("GO", "NO-GO", "PILOT", "ESCALATE")

_JEV_CLI = Path.home() / "workspace/custom-connectors/custom.legacy-typesafe/bin/jev_curl.py"

_FIT_LEVELS = ["poor fit", "weak fit", "decent fit", "strong fit", "perfect fit"]

# Verdict mapping over the normalised Jev deal-fit score (0..1).
_GO_AT = 0.75
_PILOT_AT = 0.60

# Pilot-first policy (calibrated on the 12-brief eval set, 2026-10-24):
# a cold micro-budget first engagement (budget <= $2,000, no warm intro)
# starts as a PILOT, not a full GO — prove value on a small step first.
# Boundary evidence: #8 ($2k, no referral) was the only eval GO that should
# have been PILOT; #6 ($2.5k + referral) and #1 ($3k) stay GO, so the cap
# needs BOTH conditions (small budget AND no referral).
_PILOT_FIRST_BELOW_USD = 2000


@dataclass(frozen=True)
class Verdict:
    verdict: str
    confidence: float
    reason: str
    risk_flags: tuple[str, ...] = field(default_factory=tuple)
    call_questions: tuple[str, ...] = field(default_factory=tuple)
    scorer: str = "jev"  # "jev" | "local-heuristic"


DECIDE_SYSTEM_NOTE = (
    "Deal-fit rubric: poor fit (0) / weak fit (1) / decent fit (2) / "
    "strong fit (3) / perfect fit (4) for a freelance services deal."
)


def _scoring_state(hyps: list[Hypothesis], evidence: EvidenceBundle) -> str:
    lines = ["EVIDENCE FOR DEAL-FIT SCORING:"]
    for e in evidence.items:
        lines.append(f"[{e.eid}] ({e.source}) {e.text[:220]}")
    lines.append("COMPETING HYPOTHESES:")
    for h in hyps:
        lines.append(f"{h.label} ({h.stance}): {h.text[:200]}")
    return "\n".join(lines)


def _jev_score(state: str) -> tuple[float, float] | None:
    """Ask Jev for a deal-fit score. Returns (score01, confidence) or None."""
    if not _JEV_CLI.exists():
        return None
    req = {
        "state": state[:6000],
        "model": "jev-latest",
        "questions": {
            "deal_fit": {
                "type": "score",
                "instructions": "Rate how good a fit this inbound client brief is "
                                "for the freelancer as a services deal.",
                "criteria": _FIT_LEVELS,
            }
        },
    }
    env = {k: v for k, v in os.environ.items()
           if k.lower() not in ("no_proxy",)}  # sandbox quirk: drop bad patterns
    env.pop("NO_PROXY", None)
    try:
        proc = subprocess.run(
            ["python3", str(_JEV_CLI)],
            input=json.dumps(req), capture_output=True, text=True,
            timeout=90, env=env,
        )
        if proc.returncode != 0:
            return None
        ans = json.loads(proc.stdout)["answers"]["deal_fit"]
        return float(ans["score"]) / 4.0, float(ans["confidence"])
    except Exception:
        return None


def _local_score(hyps: list[Hypothesis], evidence: EvidenceBundle) -> tuple[float, float]:
    """Deterministic local heuristic (fallback when Jev is unreachable).

    Feature-weighted deal fit in 0..1. Coarse by design — documented here so
    the fallback is reproducible, not a guess:
      +0.25 budget inside price band; -0.25 budget disclosed below band;
      -0.10 budget above band; -0.25 per red flag (cap -0.50);
      +0.10 decision maker present; +0.05 urgency; +0.05 referral;
      +0.10 if majority of recalled deals won; -0.15 if majority lost.
    Confidence is fixed 0.55 (coarse heuristic) — it never claims certainty.
    """
    text = evidence.as_text().lower()
    s = 0.5
    if "inside price band" in text:
        s += 0.25
    elif "below price band" in text:
        s -= 0.25
    elif "above price band" in text:
        s -= 0.10
    flags = text.count("red flag:")
    s -= min(0.50, 0.25 * flags)
    if "decision maker: present" in text:
        s += 0.10
    if "urgency: time pressure" in text:
        s += 0.05
    if "trust: referral" in text:
        s += 0.05
    deals = [e for e in evidence.items if e.source.startswith("local:")
             or e.source.startswith("zetaris:")]
    won = sum(1 for e in deals if " won" in e.text.lower())
    lost = sum(1 for e in deals if " lost" in e.text.lower())
    if won + lost > 0:
        s += 0.10 if won > lost else (-0.15 if lost > won else 0.0)
    return max(0.05, min(0.95, s)), 0.55


def _signals_text(evidence: EvidenceBundle) -> str:
    for e in evidence.items:
        if e.source == "signals":
            return e.text
    return ""


def _brief_eid(evidence: EvidenceBundle) -> str:
    for e in evidence.items:
        if e.source == "brief":
            return e.eid
    return "E1"


def _pilot_first_cap(evidence: EvidenceBundle) -> bool:
    """True when the pilot-first policy caps a GO verdict at PILOT."""
    signals = _signals_text(evidence)
    if "trust: referral" in signals:
        return False
    m = re.search(r"budget: \$([\d,]+)", signals)
    if not m:
        return False
    try:
        budget = int(m.group(1).replace(",", ""))
    except ValueError:
        return False
    return budget <= _PILOT_FIRST_BELOW_USD


def decide(hyps: list[Hypothesis], evidence: EvidenceBundle,
           settings: Settings) -> Verdict:
    signals = _signals_text(evidence).lower()
    brief_eid = _brief_eid(evidence)

    red_flags = [p.strip() for p in _signals_text(evidence).split("|")
                 if p.strip().lower().startswith("red flag:")]
    budget_unknown = "budget: not disclosed" in signals
    thin_evidence = budget_unknown and not red_flags

    scorer = "jev"
    scored = _jev_score(_scoring_state(hyps, evidence))
    if scored is None:
        score01, conf = _local_score(hyps, evidence)
        scorer = "local-heuristic"
    else:
        score01, conf = scored

    score01 = max(0.0, min(1.0, score01))
    conf = max(0.0, min(1.0, conf))

    if thin_evidence:
        return Verdict(
            verdict="ESCALATE",
            confidence=round(conf, 2),
            reason=(f"Not enough evidence to decide [{brief_eid}]: budget undisclosed "
                    f"and no red flags to rule on — human review needed."),
            call_questions=(
                "What is the approved budget range for this work?",
                "Who is the final decision maker?",
                "What does success look like in the first 30 days?",
            ),
            scorer=scorer,
        )
    if conf < settings.escalate_below:
        return Verdict(
            verdict="ESCALATE",
            confidence=round(conf, 2),
            reason=(f"Scorer confidence {conf:.2f} below threshold "
                    f"{settings.escalate_below} [{brief_eid}] — escalating rather than guessing."),
            call_questions=(
                "What is the approved budget range for this work?",
                "Who is the final decision maker?",
                "What does success look like in the first 30 days?",
            ),
            scorer=scorer,
        )
    if score01 >= _GO_AT:
        verdict = "GO"
    elif score01 >= _PILOT_AT:
        verdict = "PILOT"
    else:
        verdict = "NO-GO"

    pilot_capped = False
    if verdict == "GO" and _pilot_first_cap(evidence):
        verdict = "PILOT"
        pilot_capped = True

    lead = hyps[0].text[:140] if hyps else ""
    reason = (f"Deal-fit {score01:.2f} via {scorer} over {len(evidence.items)} "
              f"evidence items [{brief_eid}]. Leading hypothesis: {lead}")
    if pilot_capped:
        reason += (" Pilot-first policy applied: cold micro-budget engagement "
                   f"(<=${_PILOT_FIRST_BELOW_USD:,}) starts as a pilot.")

    questions = []
    if budget_unknown:
        questions.append("What is the approved budget range for this work?")
    if "decision maker: unclear" in signals:
        questions.append("Who is the final decision maker and are they on the call?")
    if red_flags:
        questions.append(f"Can you clarify the '{red_flags[0][10:]}' concern before we proceed?")
    for fallback_q in (
        "What does success look like in the first 30 days?",
        "Is there a hard deadline driving this timeline?",
        "Have you tried solving this with another vendor or tool before?",
    ):
        if len(questions) >= 3:
            break
        if fallback_q not in questions:
            questions.append(fallback_q)

    return Verdict(
        verdict=verdict,
        confidence=round(conf, 2),
        reason=reason,
        risk_flags=tuple(f"Check red flag: {f[10:]}" for f in red_flags),
        call_questions=tuple(questions[:3]),
        scorer=scorer,
    )
