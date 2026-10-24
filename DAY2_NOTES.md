# Day 2 notes — CORE PIPELINE done (2026-10-23, Fri)

## Built today (all inside this work dir; stdlib-only, no network except Jev)
1. **`llm/base.py`** — provider interface (LLMProvider + LLMResponse). Already scaffolded; kept.
2. **`llm/local_fallback.py`** — deterministic mock, REWRITTEN: parses the ACT
   evidence block, classifies won/lost deals + red-flag signals + budget, emits
   exactly 3 hypotheses (H1 good-fit / H2 weak-fit / H3 red-flag) with REAL
   evidence-ID citations. Fully deterministic. Never in the demo path.
3. **`data/local_kb.py` + `seed_deals.json`** — verified 12 deals, 6 won / 6 lost
   with reasons (was already in scaffold). Same record shape as ZetarisClient.
4. **`memory/deals_memory.py`** — recall(niche, service) tested:
   hotels/websites → [d02, d07, d08, d10]; win_rate() works.
5. **`reasoning/act.py`** — REWRITTEN: stable evidence IDs; `_extract_hints`
   now uses service keyword aliases (whatsapp bot/chatbot/receptionist/intake
   agent → AI agents; roas/ad spend → ad management) + plural-tolerant niche
   matching; `extract_signals` derives budget-band / red-flag / decision-maker /
   urgency / referral signals as evidence items.
6. **`reasoning/think.py`** — parser now extracts `[E#]` citations back into
   Hypothesis.evidence_ids; guarantees exactly 3 hypotheses.
7. **`reasoning/decide.py`** — REWRITTEN: **Jev-first scoring** (tried
   `jev_curl.py` once → reachable, score 3.56/4 conf 0.64 on the probe).
   `score` rubric poor→perfect fit, normalised 0..1; verdicts ≥0.75 GO,
   ≥0.60 PILOT, else NO-GO. Abstention: thin evidence (budget undisclosed AND
   no red flags) → ESCALATE; scorer confidence < escalate_below (0.55) →
   ESCALATE. **Documented local-heuristic fallback** when Jev unreachable
   (feature-weighted, fixed 0.55 confidence — never claims certainty).
   Risk flags + 3 distinct call questions derived from missing signals.
8. **`trace/verifier.py`** — tested: keeps only claims citing valid IDs,
   drops uncited claims and claims citing non-existent IDs.
9. **`ui/cli.py`** — verdict card (VERDICT/confidence/scorer, why with
   citations, ESCALATE banner, risks, 3 call questions, trace stats,
   hypotheses with citations) + `--json` + `analyze()` for eval reuse.
10. **`eval/run_eval.py`** — runs all 12, per-item table, accuracy gate
    (exit 1 if < 75%), results JSON.

## Test results
- **Eval: 11/12 correct = 91.7%** (scorer: jev for all 12; confidences 0.54–0.93).
  Results: `hidden_files/eval-results-2026-10-23.json`.
  - One MISS: #8 cloud-kitchen WhatsApp bot ($2k, owner decides) — expected
    PILOT, got GO. Jev judged strong fit (matches won deal d09 closely).
    This is a calibration judgment call, not a pipeline bug → Day 4
    DECIDE-calibration item.
- Fallback-path test (Jev forced unreachable): GO/NO-GO/ESCALATE all correct
  on 3 representative briefs, scorer=local-heuristic. Offline pipeline works.
- End-to-end CLI smoke test on the Dubai real-estate brief: GO, conf 0.87,
  3 cited claims kept, 0 dropped, 9 evidence items. Clean card output.

## Cursor (sponsor requirement) — STATUS: NOT installed on this sandbox VM
No `cursor`/`cursor-agent` binary on PATH, ~/Applications, /opt, or find
sweep. Sponsor-provided dev access is presumably issued via HackOS, not this
VM — verification must happen on Shivay's side / Day 3–5. Not a Day-2 blocker.

## Jev status
REACHABLE via jev_curl.py (curl path; urllib is broken in sandbox per notes).
Used live for all 12 eval scores. Keep Jev-first; fallback documented.

## Open items / unverified
- Day 4 calibration: tune GO/PILOT boundary (#8 case); consider a `choice`
  question for PILOT vs GO instead of pure score thresholds.
- Zetaris (Day 3), Meterless/Nemotron (Day 4) still pending — his-step logins.
- Cursor dev access — verify via HackOS.
- GitHub repo visibility decision — Day 5, pending HackOS checklist.
