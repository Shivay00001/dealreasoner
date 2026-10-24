# DealReasoner — HackOS submission packet (Open Agent Hackathon 2026, Track 03)

Prepared 2026-10-24. Deadline: 27 Oct 23:45 UTC = 28 Oct 05:15 IST.
Target: submit by 27 Oct EVENING IST. Registration already complete
(vqsaleschannel@gmail.com, Team VisionQuantech solo, Track 03).

## What to paste into HackOS
- **Project name:** DealReasoner (rename the existing draft, currently
  saved as "AI Receptionist" — do not create a second submission).
- **Track:** 03 Reasoning Architecture.
- **One-line pitch:** Verifiable reasoning for freelancer client go/no-go
  decisions — every claim cites its evidence; when evidence is thin, it
  escalates instead of guessing.
- **GitHub repo (PUBLIC):** https://github.com/Shivay00001/dealreasoner
- **Demo video:** `demo/dealreasoner-demo.mp4` in the repo (126 s, 1–4 min
  requirement met). If HackOS requires a hosted URL rather than a repo
  file, upload the mp4 to YouTube (unlisted) first and paste that URL —
  this is a browser step, not yet done.
- **Slide deck:** `demo/dealreasoner-deck.pdf` in the repo (8 slides).
- **Sponsor-tech explanation:** `SPONSOR_TECH.md` in the repo (Zetaris
  client + Meterless/Nemotron client implemented and mock-tested; live
  Cloud/HackOS credentials pending — stated honestly, with the exact
  wiring steps in docs/ZETARIS_SETUP.md and docs/METERLESS_SETUP.md).
- **Self-score:** 77/100 (SELF_SCORE.md) — Impact 23, Technical 17,
  Innovation 13, Demo 12, UX 6, Sponsor 6.

## Reproduction (for the judges, from the README)
- Stdlib only, Python 3.11+, $0: `python -m src.ui.cli --brief "..."`
- Eval: `python -m src.eval.run_eval` (12 briefs; latest runs 12/12, one
  earlier run 11/12 from live Jev variance — reported honestly).
- Sponsor-path tests: `python3 tests/test_sponsor_paths.py` (mock servers
  speaking the documented Zetaris REST + Meterless OpenAI-compatible
  shapes; proves client code paths, not live Cloud instances).

## Pre-submit upgrades (do these first if the credentials arrive)
1. Zetaris Cloud session → re-run CLI, confirm `data_layer: zetaris`,
   re-render the GO video frame, update SPONSOR_TECH.md + SELF_SCORE.md
   (Sponsor +2).
2. Meterless key + model IDs → re-run, confirm `llm:
   nemotron-via-meterless`, re-render, update docs (Sponsor +1, Demo +1).
3. Cursor API key → one genuine `cursor-agent` task on the repo, record
   output, update SPONSOR_TECH.md §3 (Sponsor +1).
4. Re-push the repo after any of 1–3 (push script in the build dir).

## Browser tasks still needed (parent — subagent cannot drive a browser)
- [ ] Zetaris Cloud session per docs/ZETARIS_SETUP.md (OTP via Gmail).
- [ ] HackOS Meterless creds per docs/METERLESS_SETUP.md.
- [ ] HackOS gated "How the Week Runs" checklist (repo visibility, video
      hosting, deck format) — confirm before submit.
- [ ] HackOS draft rename + final submit with the packet above.
- [ ] YouTube upload of the demo mp4 IF HackOS needs a hosted URL.
- [ ] Cursor login/key IF HackOS provides one.
