# DealReasoner — Verifiable Reasoning Agent for Client Go/No-Go Decisions

**Track 03 — Reasoning Architecture** · Open Agent Hackathon 2026 · Team VisionQuantech (solo)

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
- Deal memory: past won/lost deals with reasons (queried from Zetaris data layer)
- Prospect evidence: firmographic / public signals about the prospect (via Zetaris)

**4. What comes out?**
- A scored verdict: **GO / NO-GO / PILOT** with calibrated confidence
- A **verifiable reasoning trace**: every claim in the reasoning cites the
  evidence source it came from (brief quote, deal-memory record, Zetaris row)
- Risk flags + the 3 best questions to ask on the discovery call
- If confidence is below threshold: **escalation to the human instead of a guess**
  ("Not enough evidence — here's what's missing")

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
- **Reasoning** → THINK (multi-hypothesis) → ACT (evidence gathering) → DECIDE (scored, calibrated)
- **Reliable decisions** → every claim cited; confidence-calibrated verdict;
  explicit abstention/escalation instead of hallucinated certainty
- **Actions** → call questions + draft reply the freelancer can actually use

Judging map: Impact 30 (real weekly pain for millions of freelancers) ·
Technical 20 (clean pipeline + eval set with measured accuracy) ·
Innovation 15 (verifiable traces + calibrated abstention — agents that show
their receipts) · Demo 15 (2-min: messy brief in → verdict card out) ·
Sponsor Tech 10 (Zetaris / Meterless / Nemotron / Cursor, all real).

## Architecture (VQ Agent Core: THINK → ACT → DECIDE)

```
brief text ──▶ THINK ──▶ ACT ──▶ DECIDE ──▶ verdict card
               │          │         │
        3 competing   Zetaris SQL   Jev score +
        hypotheses    deal memory   calibration
        (Nemotron     prospect      → GO/NO-GO/
        via Meterless) evidence     PILOT or
                                    ESCALATE
                      ▼
              TRACE VERIFIER: every claim cites a source;
              uncited claims are dropped before the verdict
```

Module map (`src/`):
- `llm/` — provider interface; `meterless_nemotron.py` (primary, per rules),
  `local_fallback.py` (offline testing only — never in the submitted demo path)
- `data/zetaris_client.py` — SQL over the deals KB + prospect data (mandatory integration)
- `memory/deals_memory.py` — won/lost deal store + similarity retrieval
- `reasoning/think.py` — multi-hypothesis generation
- `reasoning/act.py` — evidence-gathering tool calls
- `reasoning/decide.py` — Jev scoring + calibration + escalation policy
- `trace/verifier.py` — claim↔evidence citation checker
- `ui/cli.py` — demo interface (Day 2); web card later if time
- `eval/` — 12-brief eval set with expected verdicts (proves "reliable")

## Build plan (1-page): see BUILD_PLAN.md
Day 1 (today): brief research + concept + scaffold ✅
Day 2: core pipeline with mock LLM + local KB, CLI end-to-end, eval set
Day 3: real Zetaris integration (deals KB in Zetaris)
Day 4: Meterless/Nemotron wiring, DECIDE calibration
Day 5: demo video + slide deck + README polish, repo public
Day 6: buffer + submit on HackOS before 27 Oct 23:45 UTC (28 Oct 05:15 IST)

## Run (Day 2+)
```
pip install -r requirements.txt
python -m src.ui.cli --brief "paste client message here"
```

## Submission checklist (official)
- [ ] 1–4 min demo video
- [ ] Slide deck
- [ ] GitHub repo + README
- [ ] Sponsor-tech usage explanation
- [ ] Submitted on HackOS before 27 Oct 23:45 UTC
