# Zetaris Cloud setup — browser task spec (for the parent agent)

DealReasoner needs a REAL Zetaris data layer (mandatory sponsor tech).
The client code is done (`src/data/zetaris_client.py`) and tested
against a mock speaking the documented REST shape
(`tests/test_sponsor_paths.py`). What is missing is the live Cloud
instance's connection details — those live behind the Cloud console
login, which a subagent cannot drive.

## Browser task (one session, ~10 min)
1. Log in to Zetaris Cloud at cloud.enterprise.zetaris.com with
   vqsaleschannel@gmail.com (OTP arrives by Gmail — the parent can
   read it from the mailbox).
2. Load the deals dataset: upload `src/data/deals.csv` as a table
   named exactly `deals` (columns: deal_id, outcome, niche, service,
   budget_usd, reason). Optionally also load `src/data/prospects.csv`
   as table `prospects` (columns: prospect_hint, signal).
3. Run this test query in the Cloud query console and confirm 12 rows:
   `SELECT deal_id, outcome, niche, service, budget_usd, reason FROM deals`
4. Capture, from the Cloud console's API section (or its Postman
   collection / network tab):
   - API base URL (e.g. https://api.zetaris.app.com or the Cloud URL)
   - A working idToken / API token for the account
   - The exact paths for the Open / Page / Close SQL-query calls
5. Hand those five values back. Wiring is then:
   ```
   ZETARIS_API_URL=<base> ZETARIS_ID_TOKEN=<token>
   ZETARIS_OPEN_PATH=<open> ZETARIS_PAGE_PATH=<page> ZETARIS_CLOSE_PATH=<close>
   ```
   then: `python -m src.ui.cli --brief "..."` must print
   `Data layer: zetaris` and cite `zetaris:deals` evidence.

## Why paths are not hardcoded
The Zetaris knowledge-base article documents the request BODIES
({"select", "pageLimit"}, queryToken pagination) but the public
Postman collection repo (zetaris/zetaris-public) is 404 as of
2026-10-24, and Cloud enterprise paths may differ from the legacy
SAAS API. Guessing a path and shipping it as fact would be worse
than asking for the real one.
