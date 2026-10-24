# DealReasoner — Verifiable Reasoning Agent for Client Go/No-Go Decisions

**Track 03 — Reasoning Architecture** · Open Agent Hackathon 2026 · Team VisionQuantech (solo)
· Repo: https://github.com/Shivay00001/dealreasoner

## The 5 kickoff questions (answered Day 1)

**1. Who is the user?**
A solo freelancer / small-agency owner who receives vague inbound client briefs
over email and DM every week. (Role, not category: the person who personally
decides which discovery calls are worth their time.)

**2. What is the problem? (one sentence)**
Freelancers waste hours on discovery calls with prospects who were never a fit,
because there is no structured way to turn a vague inbound brief into a reliable
go / no-go decision.

**3. What goes in?**
- The raw inbound brief (pasted text: the client's message as received)
- The freelancer's service profile (services offered, price band, red flags, past niches)
- Deal memory: past won/lost deals with reasons (queried from the Zetaris data layer)
- Prospect evidence: firmographic / public signals about the prospect (via Zetaris)

**4. What comes out?**
- A scored verdict: **GO / PILOT / NO-GO / ESCALATE** with calibrated confidence
- A **verifiable reasoning trace**: every claim in the reasoning cites the
  evidence source it came from (brief quote, deal-memory record, Zetaris row)
- Risk flags + the 3 best questions to ask on the discovery call
- A draft reply tailored to the verdict (accept / propose pilot / decline / hold)
- If confidence is below threshold or evidence is thin: **escalation to the human
  instead of a guess** ("Not enough evidence — here's what's missing")

**5. Why does this need an agent?**
Because the decision requires evidence gathered from fragmented sources
(brief + deal memory + external prospect data), multi-step reasoning across
uncertain signals, memory of what worked before, and an auditable decision
that can abstain when evidence is thin. A single static prompt cannot gather
evidence, weigh it, cite it, and refuse to decide when it shouldn't.

## Why this wins Track 03
The track asks for "a novel ability to turn data, knowledge, memory, and
reasoning into reliable decisions and actions." DealReasoner maps 1:1:
- **Data** → Zetaris data layer (deal history + prospect signals, SQL-queried)
- **Knowledge** → freelancer service profile (structured constraints)
- **Memory** → won/lost deal memory with retrieval of similar past deals
- **Reasoning** → ACT (evidence) → THINK (3 competing hypotheses) →
  TRACE VERIFY (drop uncited claims) → DECIDE (scored, calibrated)
- **Reliable decisions** → every claim cited; confidence-calibrated verdict;
  explicit abstention/escalation instead of hallucinated certainty
- **Actions** → call questions + draft reply the freelancer can actually use

Judging map: Impact 30 (real weekly pain for millions of freelancers) ·
Technical 20 (clean pipeline + eval set with measured accuracy) ·
Innovation 15 (verifiable traces + calibrated abstention — agents that show
their receipts) · Demo 15 (2-min: messy brief in → verdict card out) ·
Sponsor Tech 10 (Zetaris / Meterless / Nemotron / Cursor — see SPONSOR_TECH.md
for the honest live-vs-wired status of each).

## Architecture: ACT → THINK → VERIFY → DECIDE

```
brief text ──▶ ACT ──▶ THINK ──▶ TRACE VERIFY ──▶ DECIDE ──▶ verdict card
               │         │            │              │
        evidence with  3 competing  drop uncited   Jev score +
        stable IDs     hypotheses   claims         calibration
        (brief, deal   (each cites  before the     → GO / PILOT /
        memory,        evidence     verdict        NO-GO / ESCALATE
        Zetaris)       IDs)
```

Module map (`src/`):
- `llm/base.py` — provider interface
- `llm/meterless_nemotron.py` — Nemotron via Meterless (planner model for
  THINK, fast model for the responder draft); OpenAI-compatible chat API
- `llm/local_fallback.py` — deterministic mock for offline testing only.
  It is labeled `local-fallback` in every output it appears in and is never
  presented as a live model run.
- `data/zetaris_client.py` — Zetaris REST client (OpenSqlQuery + pagination),
  with a transparent local-KB fallback that is labeled in the output
- `data/local_kb.py` + `data/deals.csv` — 12 verified seed deals (6 won / 6 lost)
- `memory/deals_memory.py` — won/lost deal store + similarity retrieval
- `reasoning/act.py` — evidence gathering (brief signals, deal memory, Zetaris)
- `reasoning/think.py` — multi-hypothesis generation (exactly 3 hypotheses)
- `reasoning/decide.py` — Jev scoring + calibration + escalation policy +
  pilot-first cap (cold deals at or under $2,000 start as PILOT, never GO)
- `reasoning/respond.py` — verdict-tailored draft reply (fast model only)
- `trace/verifier.py` — claim↔evidence citation checker
- `ui/cli.py` — demo interface (`--json` for machine-readable output)
- `eval/` — 12-brief eval set with expected verdicts (proves "reliable")

## Run it (stdlib only — no install, $0, Python 3.11+)

```
python -m src.ui.cli --brief "Hi, I run a real estate agency in Dubai with 40 agents. We spend $6k/month on ads but lead follow-up is manual and slow. Looking for an AI agent to qualify leads on WhatsApp. Budget around $5k for setup plus monthly. Can you do a quick call this week?"
```

Expected output (real run, 2026-10-24; Jev scores vary slightly run to run):

```
==============================================================
  VERDICT: GO         confidence 0.89   (scorer: jev)
==============================================================
Why: Deal-fit 0.77 via jev over 9 evidence items [E1]. Leading
hypothesis: Good fit — past wins [E4] [E6] resemble this brief
[E3] [E1].
Ask on the call:
  - What does success look like in the first 30 days?
  - Is there a hard deadline driving this timeline?
  - Have you tried solving this with another vendor or tool before?

Reasoning trace: 3 cited claims kept, 0 uncited dropped (9 evidence items).
Data layer: local-fallback · LLM: local-fallback
Hypotheses:
  H1 [good-fit] Good fit — past wins [E4] [E6] resemble this
    brief [E3] [E1].
    cites: [E4] [E6] [E3] [E1]
  H2 [weak-fit] Weak fit — similar past deals were lost [E5]
    [E7], so scope or budget mismatch is plausible [E1].
    cites: [E5] [E7] [E1]
  H3 [red-flag] Red flags — no explicit red-flag signals;
    verify budget authority and decision maker before a call
    [E3] [E1].
    cites: [E3] [E1]
```

Escalation case (thin evidence — the honest abstention):

```
python -m src.ui.cli --brief "Clinic chain exploring ad management. No marketing budget approved yet, maybe next quarter we revisit."
```

→ `VERDICT: ESCALATE`, "Not enough evidence to decide [E1]: budget
undisclosed and no red flags to rule on — human review needed."

Run the eval set:

```
python -m src.eval.run_eval   # exit 1 if accuracy < 75%
```

## Measured results (honest)

- Eval set: 12 briefs with expected verdicts (`src/eval/eval_set.json`).
- Latest runs: **12/12 correct**. One earlier run: **11/12** — live Jev
  scoring varies slightly near thresholds (e.g. one brief's confidence
  hovered near the 0.55 escalation threshold across runs). Both numbers are
  reported here; the 12/12 is not presented as variance-free.
- Sponsor-path tests (`tests/test_sponsor_paths.py`): local mock servers
  speaking the documented Zetaris REST and Meterless OpenAI-compatible
  shapes — both paths pass end-to-end. These prove the client code paths,
  NOT the live Cloud instances (see SPONSOR_TECH.md).

## Sponsor tech — honest status (full detail: SPONSOR_TECH.md)

| Tech | Status |
| ---- | ------ |
| Zetaris (data layer) | Client implemented + mock-tested; live Cloud dataset + token pending console access. Until then the CLI labels its data layer `local-fallback`. |
| NVIDIA Nemotron via Meterless | Client implemented + mock-tested (planner + fast responder models); API key issued in the HackOS workspace. Until wired, the CLI labels its LLM `local-fallback`. |
| Cursor | Agent CLI installed (2026.10.22-27dcf5f) in the build environment; cloud runs need a Cursor API key / login, not available on the $0 budget. |
| Jev scoring | LIVE in every run above (the DECIDE scorer). |

No output in this repo claims a live Zetaris query, a live Nemotron run, or
Cursor-driven development that did not happen. When the live credentials
arrive, set the env vars in `docs/ZETARIS_SETUP.md` /
`docs/METERLESS_SETUP.md` and re-run — the CLI will show
`data_layer: zetaris` / `llm: nemotron-via-meterless` in its output.

## Build status
Day 1 (22 Oct): brief research + concept + scaffold ✅
Day 2 (23 Oct): core pipeline, CLI end-to-end, eval 11/12 ✅
Day 3 (24 Oct): calibration fix (12/12), Zetaris + Meterless clients,
  sponsor-path tests, dataset CSVs, setup docs ✅
Day 4 (24 Oct): demo video (126 s) + slide deck + README ✅
Day 5 (27 Oct): HackOS submission (rename draft "AI Receptionist" →
  "DealReasoner", attach repo + video + deck) — browser step, pending

## Submission checklist (official)
- [x] 1–4 min demo video (`demo/dealreasoner-demo.mp4`, 126 s)
- [x] Slide deck (`demo/dealreasoner-deck.pdf`, 8 slides)
- [x] GitHub repo + README (public: https://github.com/Shivay00001/dealreasoner)
- [x] Sponsor-tech usage explanation (`SPONSOR_TECH.md`)
- [ ] Submitted on HackOS before 27 Oct 23:45 UTC (28 Oct 05:15 IST)
