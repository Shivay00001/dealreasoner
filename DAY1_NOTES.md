# Day 1 notes → what Day 2 needs (2026-10-22)

## Done today
- Official brief researched (BRIEF.md): Track 03 = "turn data, knowledge,
  memory, and reasoning into reliable decisions and actions"; $3,600 prize
  (1st $1,500); scoring Impact 30 / Technical 20 / Innovation 15 / Demo 15 /
  Product UX 10 / Sponsor Tech 10; submission = 1–4 min video + slide deck +
  GitHub repo + README + sponsor-tech explanation, on HackOS, by
  27 Oct 23:45 UTC.
- Concept locked: **DealReasoner** — verifiable reasoning agent for
  freelancer client go/no-go decisions (5 questions answered in README.md).
- Scaffold created under this dir: README, BRIEF, BUILD_PLAN, src/ modules,
  requirements.txt, .gitignore, eval-set shape.

## Day 2 can start with ZERO logins
Core pipeline (mock LLM + local JSON KB + CLI + eval set) needs no credentials.
Start there; sponsor wiring is Day 3–4.

## Items needing a logged-in browser session / his step (DO NOT attempt from sandbox)
1. **Zetaris Cloud OTP login** — free Cloud account already provisioned to his
   email. OTP arrives by email; extractable via Gmail connector under the
   hackathon delegation. Needed Day 3 to load the deals KB + run real SQL.
   Zetaris getting-started: zetaris/getting-started repo (public).
2. **HackOS dashboard** (hackathon.genai.works/dashboard) — verify submission
   checklist fields: is the GitHub repo required PUBLIC? video hosting rules?
   deck format? Also confirm final required-tech list ("How the Week Runs"
   lesson). Needed before Day 5.
3. **Meterless / NVIDIA Nemotron credentials** — issued in the HackOS workspace
   per the academy. Needed Day 4. Verify they work from the sandbox egress
   (proxy!) before committing the demo path to them.
4. **Cursor for development** — teams "must use Cursor". Verify sponsor access
   is free (no card). If Cursor needs payment → ₹0 conflict → escalate to
   Shivay immediately; do not pay.
5. **GitHub repo visibility** — his standing rule is PRIVATE repos, but judges
   likely need access. Decision needed Day 5: public repo vs private+collaborator.
   Check HackOS checklist first; do not guess.
6. **Demo video voiceover** — his content rule: cloned voice for videos.
   Day 5: generate voiceover with his cloned voice (Chatterbox) or ship with
   captions only if time is short. His call.

## Open / UNVERIFIED items (from gated lessons)
- Full 10-section official rules (only 1.1–1.3 visible publicly).
- Exact HackOS submission field checklist (video host, deck format, repo visibility).
- Final required-technology list ("How the Week Runs" lesson).
- Prize-split discrepancy: academy snippet said $2,000/$1,350/$1,300 per track;
  event page says $1,500/$1,200/$900 for Track 03 → event page treated as truth.

## Risks
- Zetaris integration is MANDATORY (not just 10% of score). A mock Zetaris
  risks disqualification — real wiring is a must-have, not a stretch goal.
- Sandbox proxy quirks (unset no_proxy/NO_PROXY, keep *_proxy) apply to
  Zetaris/Meterless API calls — test connectivity early Day 3.
- Deadline is 05:15 IST Oct 28; plan submission for evening of Oct 27 IST.
