"""CLI demo: paste a brief, get a verdict card.

Usage:
    python -m src.ui.cli --brief "client message here"
    python -m src.ui.cli --file brief.txt
    python -m src.ui.cli --brief "..." --json   (machine-readable)

Pipeline: ACT (evidence) -> THINK (3 hypotheses, mock or Nemotron) ->
TRACE verify (drop uncited claims) -> DECIDE (Jev-scored verdict).
"""
from __future__ import annotations

import argparse
import json
import sys

from ..config import DEFAULT_PROFILE, Settings
from ..data import local_kb
from ..data.zetaris_client import ZetarisClient
from ..llm.local_fallback import LocalFallback
from ..llm.meterless_nemotron import MeterlessNemotron
from ..memory.deals_memory import DealsMemory
from ..reasoning import act, decide, respond, think
from ..trace import verifier


def build_llm(settings: Settings):
    if settings.llm_provider == "nemotron":
        if not settings.nemotron_configured:
            raise SystemExit("DEALREASONER_LLM=nemotron but Meterless creds missing "
                             "(METERLESS_API_URL/KEY/PLANNER_MODEL — see docs/METERLESS_SETUP.md)")
        return MeterlessNemotron(settings.meterless_api_url,
                                 settings.meterless_api_key,
                                 settings.meterless_planner_model,
                                 settings.meterless_fast_model)
    return LocalFallback()


def build_zetaris(settings: Settings):
    """Zetaris client when fully configured, else None (local KB fallback)."""
    if not settings.zetaris_configured:
        return None
    try:
        return ZetarisClient(
            api_url=settings.zetaris_api_url,
            id_token=settings.zetaris_id_token,
            open_path=settings.zetaris_open_path,
            page_path=settings.zetaris_page_path,
            close_path=settings.zetaris_close_path,
            deals_table=settings.zetaris_deals_table,
            prospects_table=settings.zetaris_prospects_table,
        )
    except ValueError:
        return None


def analyze(brief: str, settings: Settings) -> dict:
    """Run the full pipeline; return a structured result dict."""
    llm = build_llm(settings)
    zetaris = build_zetaris(settings)
    bundle = act.gather(brief, DEFAULT_PROFILE, zetaris=zetaris)
    memory = DealsMemory(local_kb.load_deals())  # Day 3: Zetaris-backed
    _ = memory  # retrieval used inside act.gather for now; wired here Day 3

    hyps = think.think(llm, brief, bundle.as_text())
    trace_text = "\n".join(f"{h.label} [{h.stance}] {h.text}" for h in hyps)
    trace = verifier.verify(trace_text, bundle.ids())
    verdict = decide.decide(hyps, bundle, settings)
    draft = respond.draft_reply(llm, brief, verdict)

    data_layer = "zetaris" if zetaris is not None else "local-fallback"
    return {
        "brief_excerpt": brief.strip()[:120],
        "verdict": verdict.verdict,
        "confidence": verdict.confidence,
        "reason": verdict.reason,
        "risk_flags": list(verdict.risk_flags),
        "call_questions": list(verdict.call_questions),
        "scorer": verdict.scorer,
        "data_layer": data_layer,
        "llm": llm.name,
        "draft_reply": draft,
        "evidence_count": len(bundle.items),
        "trace_kept": len(trace.kept_claims),
        "trace_dropped": len(trace.dropped_claims),
        "hypotheses": [
            {"label": h.label, "stance": h.stance, "text": h.text,
             "evidence_ids": list(h.evidence_ids)} for h in hyps
        ],
        "dropped_claims": list(trace.dropped_claims),
    }


def print_card(res: dict) -> None:
    import textwrap
    bar = "=" * 62
    print(bar)
    print(f"  VERDICT: {res['verdict']:8s}   confidence {res['confidence']:.2f}   "
          f"(scorer: {res['scorer']})")
    print(bar)
    for line in textwrap.wrap(f"Why: {res['reason']}", 62):
        print(line)
    if res["verdict"] == "ESCALATE":
        print(">>> Escalated: not enough evidence to decide — human reviews.")
    if res["risk_flags"]:
        print("Risks:")
        for r in res["risk_flags"]:
            print(f"  - {r}")
    print("Ask on the call:")
    for q in res["call_questions"]:
        print(f"  - {q}")
    if res.get("draft_reply"):
        print(f"\nDraft reply ({res['draft_reply']['model']}):")
        for line in textwrap.wrap(res['draft_reply']['text'], 60):
            print(f"  {line}")
    print(f"\nReasoning trace: {res['trace_kept']} cited claims kept, "
          f"{res['trace_dropped']} uncited dropped "
          f"({res['evidence_count']} evidence items).")
    print(f"Data layer: {res.get('data_layer', '?')} · LLM: {res.get('llm', '?')}")
    print("Hypotheses:")
    for h in res["hypotheses"]:
        cites = " ".join(f"[{e}]" for e in h["evidence_ids"]) or "(no citations)"
        body = f"{h['label']} [{h['stance']}] {h['text']}"
        for i, line in enumerate(textwrap.wrap(body, 58)):
            print(f"  {line}" if i == 0 else f"    {line}")
        print(f"    cites: {cites}")


def main() -> None:
    ap = argparse.ArgumentParser(description="DealReasoner — brief in, verdict out")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--brief", help="Inbound client brief text")
    g.add_argument("--file", help="File containing the brief")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of the card")
    args = ap.parse_args()
    brief = args.brief or open(args.file, encoding="utf-8").read()
    res = analyze(brief, Settings())
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print_card(res)


if __name__ == "__main__":
    main()
