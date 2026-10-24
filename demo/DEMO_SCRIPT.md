# DealReasoner demo script (video: dealreasoner-demo.mp4, 126 s)

Frames are rendered from REAL CLI output — re-running the commands below
reproduces the video's terminal frames (Jev scores vary slightly run to
run; verdicts on these two briefs are stable).

## Frame 1 — Title (7 s)
DealReasoner. Verifiable reasoning for freelancer client go/no-go
decisions. Track 03, Reasoning Architecture.

## Frame 2 — Problem (9 s)
A freelancer gets vague inbound briefs every week. Each discovery call
costs an hour; most of them were never a fit.

## Frame 3 — The brief (11 s)
```
python -m src.ui.cli --brief "Hi, I run a real estate agency in Dubai
with 40 agents. We spend $6k/month on ads but lead follow-up is manual
and slow. Looking for an AI agent to qualify leads on WhatsApp. Budget
around $5k for setup plus monthly. Can you do a quick call this week?"
```

## Frame 4 — Pipeline (11 s)
ACT gathers evidence (brief signals, deal memory, profile constraints —
each item gets a stable ID) → THINK proposes 3 competing hypotheses,
each citing evidence IDs → TRACE VERIFIER drops uncited claims →
DECIDE scores deal-fit and calibrates the verdict.

## Frames 5–6 — GO verdict (30 s, verbatim CLI output)
VERDICT: GO, confidence 0.89, scorer Jev. Deal-fit 0.77 over 9 evidence
items. 3 cited claims kept, 0 dropped. Hypotheses with [E#] citations.

## Frames 7–8 — ESCALATE case (30 s, verbatim CLI output)
Brief: "Clinic chain exploring ad management. No marketing budget
approved yet, maybe next quarter we revisit."
→ VERDICT: ESCALATE — not enough evidence to decide; human reviews.
This is the reliability behaviour: abstain instead of guessing.

## Frame 9 — Measured, not claimed (12 s)
Eval set: 12 briefs with expected verdicts. Latest runs 12/12; one
earlier run 11/12 — live Jev scoring varies slightly near thresholds.

## Frame 10 — Sponsor tech, real status (15 s)
Zetaris client implemented + tested (live Cloud dataset + token
pending console access). Nemotron via Meterless client implemented +
tested (planner + fast models; API key issued in the HackOS workspace).
Jev scoring LIVE in every run. Local fallback: offline only, labeled.

## Frame 11 — Close (8 s)
github.com/Shivay00001/dealreasoner — stdlib only, one command
reproduces the demo.
