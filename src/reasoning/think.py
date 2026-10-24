"""THINK: multi-hypothesis reasoning over the brief.

Generates competing hypotheses (good fit / weak fit / red-flag) instead of a
single chain-of-thought, so the later DECIDE step has something to adjudicate.
Every hypothesis must reference evidence IDs from the ACT step — the trace
verifier enforces this downstream. Evidence IDs cited in the model output are
parsed back into the Hypothesis records.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..llm.base import LLMProvider

THINK_SYSTEM = (
    "You are the THINK step of a deal-triage reasoning agent. "
    "Given an inbound client brief and evidence, propose exactly 3 competing "
    "hypotheses: H1 good fit, H2 weak fit, H3 red flags / scam risk. "
    "Each hypothesis must cite evidence IDs like [E1], [E2]. "
    "Keep each to 2 sentences. No verdict yet."
)

_CITE_RE = re.compile(r"\[E(\d+)\]")
_LINE_RE = re.compile(r"^\s*H([123])\s*:\s*(.*)$", re.IGNORECASE | re.DOTALL)


@dataclass(frozen=True)
class Hypothesis:
    label: str  # H1 | H2 | H3
    stance: str  # "good-fit" | "weak-fit" | "red-flag"
    text: str
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)


_STANCES = ("good-fit", "weak-fit", "red-flag")


def _parse(raw: str) -> list[Hypothesis]:
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    hyps: list[Hypothesis] = []
    for i, line in enumerate(lines[:3]):
        m = _LINE_RE.match(line)
        idx = int(m.group(1)) - 1 if m else i
        text = m.group(2).strip() if m else line
        cited = tuple(f"E{c}" for c in _CITE_RE.findall(text))
        hyps.append(Hypothesis(
            label=f"H{idx + 1}",
            stance=_STANCES[idx] if idx < 3 else "weak-fit",
            text=text,
            evidence_ids=cited,
        ))
    # Guarantee 3 hypotheses even if the model under-delivers.
    while len(hyps) < 3:
        i = len(hyps)
        hyps.append(Hypothesis(label=f"H{i + 1}", stance=_STANCES[i],
                               text="(no hypothesis generated)", evidence_ids=()))
    return hyps


def think(llm: LLMProvider, brief: str, evidence_text: str) -> list[Hypothesis]:
    raw = llm.generate(
        THINK_SYSTEM,
        f"BRIEF:\n{brief}\n\nEVIDENCE:\n{evidence_text}",
    ).text
    return _parse(raw)
