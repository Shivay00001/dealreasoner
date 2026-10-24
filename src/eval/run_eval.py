"""Eval runner: 12-brief eval set with expected verdicts.

Usage:
    python -m src.eval.run_eval
    python -m src.eval.run_eval --out hidden_files/eval-results-2026-10-23.json

Runs the full pipeline (mock LLM + local KB + Jev-first DECIDE) per brief,
compares verdicts to expected, prints a per-item table + accuracy, and writes
a results JSON with the same name next to this module when --out is given.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from ..config import Settings
from ..ui.cli import analyze

_HERE = Path(__file__).parent


def load_eval_set() -> list[dict]:
    return json.loads((_HERE / "eval_set.json").read_text(encoding="utf-8"))


def run(items: list[dict], settings: Settings) -> dict:
    results = []
    correct = 0
    for i, item in enumerate(items):
        res = analyze(item["brief"], settings)
        got = res["verdict"]
        want = item["expected"]
        ok = got == want
        correct += ok
        results.append({
            "idx": i,
            "expected": want,
            "got": got,
            "correct": ok,
            "confidence": res["confidence"],
            "scorer": res["scorer"],
            "why": item.get("why", ""),
            "brief_excerpt": res["brief_excerpt"],
        })
    return {
        "total": len(items),
        "correct": correct,
        "accuracy": round(correct / len(items), 3) if items else 0.0,
        "results": results,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="",
                    help="Path for the results JSON (default: none, print only)")
    args = ap.parse_args()
    items = load_eval_set()
    summary = run(items, Settings())

    print(f"Eval set: {summary['total']} briefs | "
          f"correct {summary['correct']} | accuracy {summary['accuracy']:.1%}")
    print("-" * 100)
    for r in summary["results"]:
        mark = "OK " if r["correct"] else "MISS"
        print(f"[{mark}] #{r['idx']:2d} want={r['expected']:8s} got={r['got']:8s} "
              f"conf={r['confidence']:.2f} scorer={r['scorer']:15s} "
              f"brief: {r['brief_excerpt'][:60]}...")
    print("-" * 100)
    if not all(r["correct"] for r in summary["results"]):
        print("Misses:")
        for r in summary["results"]:
            if not r["correct"]:
                print(f"  #{r['idx']} ({r['why']}): want {r['expected']}, got {r['got']}")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"\nResults written to {out}")

    sys.exit(0 if summary["accuracy"] >= 0.75 else 1)


if __name__ == "__main__":
    main()
