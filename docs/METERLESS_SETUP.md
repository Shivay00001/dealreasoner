# Meterless / Nemotron setup — browser task spec (for the parent agent)

DealReasoner's THINK step must run on NVIDIA Nemotron via Meterless
(mandatory sponsor tech). The client code is done
(`src/llm/meterless_nemotron.py`, OpenAI-compatible
/v1/chat/completions, curl transport) and tested against a mock
(`tests/test_sponsor_paths.py`). What is missing is the live
credential set — issued inside the HackOS workspace, which a subagent
cannot open.

## Browser task (one session, ~5 min)
1. Open the HackOS dashboard (hackathon.genai.works/dashboard) as
   Team VisionQuantech (vqsaleschannel@gmail.com).
2. Find the Meterless workspace / API credentials section (per the
   academy: credentials are issued in the HackOS workspace).
3. Capture:
   - Meterless API base URL
   - Meterless API key
   - The planner (reasoning-class) Nemotron model ID
   - The fast small Nemotron model ID (for the draft-reply responder;
     if the workspace offers only one model, report that and the
     responder will use the planner model)
4. Hand those values back. Wiring is then:
   ```
   DEALREASONER_LLM=nemotron METERLESS_API_URL=<base>
   METERLESS_API_KEY=<key> METERLESS_PLANNER_MODEL=<planner>
   METERLESS_FAST_MODEL=<fast>
   ```
   then: `python -m src.ui.cli --brief "..."` must print
   `LLM: nemotron-via-meterless` and a draft reply.

## Fallback honesty
Until those creds arrive, the demo path uses the deterministic local
mock LLM (documented in README as offline-only) + live Jev scoring.
The submission must NOT claim a live Nemotron run that did not happen
— the demo video is recorded on the path that actually ran, and the
writeup states exactly which sponsor pieces are live vs wired.
