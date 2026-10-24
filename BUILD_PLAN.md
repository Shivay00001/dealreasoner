# DealReasoner — Build Plan, Oct 22–27 (Day 1 → Day 6)

Rules of the week: ₹0 only (no paid APIs, no cards). Sponsor stack is free for
participants: Zetaris Cloud (provisioned), Meterless engine, NVIDIA Nemotron via
Meterless, Cursor (sponsor-provided dev access — verify free on Day 2).
One working agent beats an ambitious design. Submit early on Day 6.

## Day 1 — Thu Oct 22 (TODAY) ✅ research + concept + scaffold
- [x] Research official Track 03 brief, scoring, submission requirements → BRIEF.md
- [x] Answer 5 kickoff questions, lock concept (DealReasoner) → README.md
- [x] Repo scaffold: module structure, requirements, eval-set shape
- [ ] Append run notes to ~/memory/2026-10-22.md

## Day 2 — Fri Oct 23 · CORE PIPELINE (no sponsor creds needed)
Goal: end-to-end CLI demo with mock LLM + local JSON KB. No logins required.
- [ ] `llm/base.py` provider interface + `local_fallback.py` deterministic mock
- [ ] `data/local_kb.py`: 12-deal seed KB (JSON) — 6 won / 6 lost with reasons
- [ ] `memory/deals_memory.py`: similarity retrieval over past deals
- [ ] `reasoning/think.py` → 3 hypotheses; `act.py` → evidence bundle;
      `decide.py` → Jev-scored verdict + escalation threshold
- [ ] `trace/verifier.py`: claim↔evidence citation check, drop uncited claims
- [ ] `ui/cli.py`: paste brief → verdict card (GO/NO-GO/PILOT/ESCALATE)
- [ ] `eval/eval_set.json`: 12 briefs with expected verdicts; run, record accuracy
- [ ] Verify: Cursor installed/accessible for dev (sponsor requirement)

## Day 3 — Sat Oct 24 · ZETARIS INTEGRATION (needs logins)
Goal: real Zetaris data layer; local KB becomes fallback only.
Needs (browser-session / his-step items — see DAY1_NOTES.md):
- [ ] Zetaris Cloud OTP login (email OTP — extractable from Gmail)
- [ ] Deals KB loaded into Zetaris; `data/zetaris_client.py` runs real SQL
- [ ] Prospect-evidence query path working (or documented sample-data path)
- [ ] Sponsor-tech usage doc started (what Zetaris does in the architecture)
- [ ] Verify: Meterless/Nemotron credentials issued in HackOS workspace

## Day 4 — Sun Oct 25 · REAL REASONING (needs Meterless/Nemotron)
Goal: THINK/ACT run on NVIDIA Nemotron via Meterless; no mocks in demo path.
- [ ] `llm/meterless_nemotron.py` wired; prompt library from Meterless used
- [ ] DECIDE calibration: tune escalation threshold on eval set
- [ ] Accuracy re-run on eval set with real model; record numbers for deck
- [ ] Reliability pass: timeouts, retries, graceful degradation if Zetaris down

## Day 5 — Mon Oct 26 · DEMO + DECK + REPO
Goal: everything a judge touches is polished.
- [ ] Demo script (≤2 min spoken): messy brief → evidence → trace → verdict card
- [ ] Record 1–4 min demo video (screen capture + captions; voiceover optional)
- [ ] Slide deck: problem, user, architecture, sponsor-tech usage, eval numbers
- [ ] README final: setup, architecture diagram, sponsor-tech explanation
- [ ] Push to public GitHub repo (judges need access — verify HackOS requirement)

## Day 6 — Tue Oct 27 · SUBMIT
Goal: submitted with margin, not at the wire.
- [ ] Morning: full dry run (video plays, repo clones, CLI runs, links work)
- [ ] Submit on HackOS: video + deck + repo + sponsor-tech explanation
- [ ] Target: submit by 18:00 IST (hard deadline 23:45 UTC = 05:15 IST Oct 28)
- [ ] Log submission receipt; report done

## Tech stack
Python 3.11 · stdlib + `requests` only (Day 2–4). Zetaris: REST/SQL client per
their getting-started repo. LLM: NVIDIA Nemotron via Meterless (sponsor).
Dev: Cursor (sponsor requirement). No paid services anywhere.

## What "done" looks like (judge's view)
1. Watches ≤4-min video: real brief → cited reasoning → verdict. Clear.
2. Opens repo: README explains in 2 min, `pip install -r requirements.txt`
   + one command reproduces the demo.
3. Sees sponsor tech genuinely used: Zetaris queries in code, Nemotron
   powering reasoning, built in Cursor.
4. Sees reliability proof: eval set with measured accuracy + abstention policy.
