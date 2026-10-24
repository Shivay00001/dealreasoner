# Day 4 notes (2026-10-24) — demo, deck, docs, public repo

## Public repo — DONE
- Created PUBLIC: https://github.com/Shivay00001/dealreasoner (201,
  private:false, visibility:public). Explicit task authorization overrides
  the standing PRIVATE rule for this submission.
- Pushed 37 files via Contents API (sequential, base64, branch main):
  .gitignore, BRIEF/BUILD_PLAN/DAY1/DAY2/DAY3 notes, README, docs/
  (ZETARIS_SETUP, METERLESS_SETUP), requirements.txt (fixed: stdlib-only —
  no `requests` import exists anywhere in src/ or tests/), src/ (35 files
  incl. data CSVs + eval set), tests/test_sponsor_paths.py.
- Secret scan before push: no hardcoded keys/tokens (only env-var reads
  and test placeholders "test-token"/"test-key").
- Push script kept in the build dir (push_to_github.py); it is NOT pushed
  to the repo (it contains the repo name only, but the demo/ push below
  covers the deliverables; the script itself is a local tool).

## Demo video — DONE (126 s, within the 1–4 min requirement)
- `demo/dealreasoner-demo.mp4` (291,994 bytes, 1280x720, yuv420p,
  ffprobe duration 126.04 s), 11 frames via PIL + ffmpeg concat.
- Frames 5–8 show VERBATIM CLI output (from real runs saved to
  demo/demo-go.txt + demo-escalate.txt, now workspace-persistent — the
  /tmp originals are ephemeral and must not be relied on).
- Frame 10 (sponsor status) fixed after visual check: last line had
  overlapped the footer; text shortened + y-guard added; re-rendered and
  visually re-verified clean.
- Narration: captions are the frame text (no voiceover — captions-only
  was the Day-1 fallback if time was short; cloned-voice voiceover was
  never authorized for this build).
- Script: demo/make_video.py, narration map: demo/DEMO_SCRIPT.md.

## Slide deck — DONE (8 slides)
- `demo/dealreasoner-deck.pdf` (9,002 bytes, 16:9, reportlab), built by
  demo/make_deck.py. Covers problem, pipeline, GO case, ESCALATE case,
  measured results, honest sponsor status, why-it-wins.

## Cursor — installed, auth-blocked (honest status)
- Backgrounded find resolved: `~/.local/share/cursor-agent/versions/` was
  EMPTY after the first installer failure (tar ownership error).
- Retry with the real fix: download the 176 MB tarball, extract with
  `--no-same-owner`, symlink to `~/.local/bin/cursor-agent`.
- Verified: `--version` → 2026.10.22-27dcf5f, `--help` works.
- Cloud runs blocked: test prompt returns "Authentication required.
  Please run 'agent login' first, or set CURSOR_API_KEY". No key on the
  $0 budget. Submission claims the installed tooling only — see
  SPONSOR_TECH.md §3 for the exact wording and the one-step upgrade path.

## Docs finalized
- README.md rewritten: architecture order corrected (ACT → THINK →
  VERIFY → DECIDE, was THINK → ACT), run section fixed (stdlib-only, no
  pip install), expected output now VERBATIM from demo-go.txt (H2/H3
  lines corrected after a diff check), eval honesty section, sponsor
  status table, submission checklist with video/deck/repo/SPONSOR_TECH
  checked and HackOS submit pending.
- SPONSOR_TECH.md (new): per-sponsor live vs implemented vs pending.
- SELF_SCORE.md (new): honest total 77/100 (Impact 23, Technical 17,
  Innovation 13, Demo 12, UX 6, Sponsor 6); targets missed: Impact 25+
  and Sponsor 9+; gap-closers listed in priority order.

## Still pending (parent browser tasks — see SUBMISSION_PACKET.md)
1. Zetaris Cloud session (docs/ZETARIS_SETUP.md) → live dataset + token.
2. HackOS Meterless creds (docs/METERLESS_SETUP.md) → live Nemotron run.
3. HackOS checklist from the gated "How the Week Runs" lesson (repo
   visibility rule, video hosting rule, deck format).
4. Cursor API key if HackOS provides one (one genuine cursor-agent task).
5. HackOS draft rename "AI Receptionist" → "DealReasoner" + final submit
   with repo URL + video + deck + SPONSOR_TECH.md.
6. Video hosting: if HackOS needs a hosted URL (not a repo file), a
   YouTube upload is a parent/browser item — do not assume the repo-file
   link suffices.
