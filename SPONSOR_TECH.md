# Sponsor-tech usage — DealReasoner (Open Agent Hackathon 2026, Track 03)

This page states exactly what is live, what is implemented-and-tested, and
what is still pending for each mandatory sponsor technology. Nothing here
claims a live run that did not happen.

## 1. Zetaris — data layer (mandatory)

**What it does in DealReasoner:** the deal-history and prospect-signal
store behind every verdict. `src/data/zetaris_client.py` queries a deals
table (`SELECT deal_id, outcome, niche, service, budget_usd, reason FROM
<deals_table>`) and a prospects table, ranks past deals with the same
scoring as the local KB, and feeds them into the ACT evidence set with
stable IDs and `zetaris:deals` / `zetaris:prospects` sources.

**Implemented (real code, tested):**
- REST client against the documented Zetaris API contract (login →
  idToken + refreshToken; OpenSqlQuery body `{"select", "pageLimit"}`;
  queryToken pagination; CloseSqlQuery; requestId UUID header).
- Pagination (guard: 20 pages), defensive row parsing (rows under
  data/rows/results/records, dicts or lists + columns list).
- Transparent failure behaviour: on ANY Zetaris error the CLI falls back
  to the local KB **and adds a trace evidence item saying so** — never
  silent, never a fake `zetaris` label. The output's `data_layer` field
  reads `zetaris` only when a Zetaris query actually succeeded.
- Mock-server tests (`tests/test_sponsor_paths.py`): a local server
  speaking the documented shape returns 12 paginated rows; the pipeline
  produces verdict GO, `data_layer=zetaris`, 9 evidence items (3 base +
  5 deals + 1 prospect), 3 cited claims kept.
- Dataset CSVs ready to upload: `src/data/deals.csv` (12 seed deals),
  `src/data/prospects.csv`. Upload + verification steps:
  `docs/ZETARIS_SETUP.md`.

**Still pending (needs console access, not code):** a Zetaris Cloud
session (login at cloud.enterprise.zetaris.com with the HackOS-provisioned
account), the datasets uploaded as tables `deals` / `prospects`, and the
live API base URL + idToken + Open/Page/Close paths. Endpoint paths are
constructor/env parameters and are NEVER guessed — the public Postman
collection repo returned 404, and Cloud enterprise paths may differ from
the legacy SAAS API. Until those values arrive, every demo run honestly
shows `data_layer: local-fallback`.

## 2. NVIDIA Nemotron via Meterless (mandatory)

**What it does in DealReasoner:** the reasoning model, model-per-step.
`src/llm/meterless_nemotron.py` speaks the OpenAI-compatible
`/v1/chat/completions` shape: the planner model (a reasoning-class
Nemotron) generates the 3 hypotheses for THINK; the fast model (a small
fast Nemotron) drafts the verdict-tailored reply in
`src/reasoning/respond.py`. The responder returns None when unconfigured
— it never falls back to a template and calls it a model run.

**Implemented (real code, tested):**
- curl transport (urllib proxy-tunnels time out in this sandbox),
  `--noproxy 127.0.0.1,localhost` so local mock servers bypass the egress
  proxy while real hosts still use it.
- Mock-server tests: OpenAI-compatible mock returns planner + fast
  completions; pipeline produces verdict GO, `llm=nemotron-via-meterless`,
  draft reply from the fast model, 3 cited claims kept.
- Wiring steps: `docs/METERLESS_SETUP.md`.

**Still pending (needs HackOS workspace access):** the Meterless base URL
+ API key + planner model ID + fast model ID (or a single-model
confirmation). Until those arrive, every demo run honestly shows
`llm: local-fallback`, and the deterministic mock is used only for
offline testing — never in a claimed live run.

**In-kind prize relevance:** Best use of NVIDIA Nemotron → NVIDIA DGX
Spark AI Supercomputer. The planner/fast split is the Nemotron-specific
design choice: reasoning-class model where reasoning quality matters
(THINK), small fast model where latency matters (responder draft).

## 3. Cursor (mandatory for development)

**Status — partially met, stated honestly:**
- Cursor Agent CLI **installed and verified** in the build environment:
  version `2026.10.22-27dcf5f`, `--version` and `--help` confirmed
  working. The initial installer failed on tar ownership; the retry with
  `--no-same-owner` succeeded (176 MB package, extracted + symlinked to
  `~/.local/bin/cursor-agent`).
- Cloud runs are **blocked on authentication**: `cursor-agent` requires
  `agent login` or a `CURSOR_API_KEY`, neither available on the $0
  budget in this sandbox. A test prompt returns the auth error, not a
  hallucinated answer.
- Consequence: the code in this repo was written and tested directly in
  this environment. If a Cursor API key becomes available (HackOS
  workspace or the developer's own Cursor account), the honest next step
  is to run at least one genuine `cursor-agent` task against this repo
  (e.g. README polish or test expansion) and record its output — then
  this section can claim Cursor-driven work truthfully. Until then it
  claims only the installed tooling.

## 4. Jev scoring (project's own decision scorer — not a hackathon sponsor)

DECIDE scores deal-fit through Jev (weighted rubric poor→perfect fit,
normalised 0..1; ≥0.75 GO, ≥0.60 PILOT, else NO-GO). Jev is **live** in
every run shown in the video and README — this is the one scoring path
that needs no pending credential. A documented local-heuristic fallback
(fixed 0.55 confidence) exists only when Jev is unreachable, and the
output names its scorer in every verdict card.

## What "sponsor tech" means for judging (self-assessment)

- Zetaris: integration code is complete and proven against the
  documented contract; the live Cloud query is one console session away.
- Meterless/Nemotron: integration code is complete and proven against
  the OpenAI-compatible shape; the live key is one HackOS lookup away.
- Cursor: tooling installed; cloud-driven development pending a key.
- Net: this submission scores itself 6/10 on Sponsor tech (see
  SELF_SCORE.md) — it does not claim the 9+ it targets until the live
  sponsor paths run for real.
