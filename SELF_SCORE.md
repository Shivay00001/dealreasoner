# DealReasoner — self-score against the official 100-point rubric

Targets set at build start: Impact 25+, Sponsor tech 9+, Demo 13+.
Honest scores below; the two missed targets are named, not hidden.

| Criterion (max) | Self-score | Reasoning |
| --------------- | ---------- | --------- |
| Impact (30) | 23 | Real, weekly, expensive pain (dead discovery calls) for millions of freelancers; decision is auditable. No real users or paid validation yet, so not 25+. |
| Technical (20) | 17 | Clean ACT→THINK→VERIFY→DECIDE pipeline, 12-brief eval set with measured accuracy, sponsor-path tests, stdlib-only reproducibility in one command. CLI-only keeps it from 20. |
| Innovation (15) | 13 | Verifiable traces (every claim cites an evidence ID) + calibrated abstention (ESCALATE instead of guessing) + pilot-first cap. Novel combination, not a novel model. |
| Demo (15) | 12 | 126-second video built from REAL terminal output (GO + ESCALATE cases), 8-slide deck, one-command reproduction. Loses points: no live sponsor run inside the video yet. |
| Product & UX (10) | 6 | CLI verdict card is clear and complete (verdict, confidence, why, risks, call questions, draft reply), but there is no web UI or onboarding flow. |
| Sponsor tech (10) | 6 | Zetaris + Meterless/Nemotron clients implemented and mock-tested against documented contracts; Jev scoring live. Live Cloud/HackOS runs and Cursor cloud runs pending credentials — see SPONSOR_TECH.md. |
| **Total (100)** | **77** | |

## What closes the gap before submission (in priority order)
1. Live Zetaris query (console session per docs/ZETARIS_SETUP.md) → CLI
   shows `data_layer: zetaris`; re-record the GO frame. Sponsor tech +2.
2. Live Meterless/Nemotron run (HackOS key per docs/METERLESS_SETUP.md)
   → CLI shows `llm: nemotron-via-meterless`; re-record. Sponsor tech +1,
   Demo +1.
3. One genuine `cursor-agent` task with a real API key → Sponsor tech +1.
4. A web verdict card (single HTML page over the CLI `--json`) → UX +2.
5. One real freelancer running a real brief → Impact +2.

With items 1–3 done, the honest total becomes ~82–84. Without them, 77 is
the number to stand behind.
