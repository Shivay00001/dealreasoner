"""Zetaris data-layer client (MANDATORY sponsor integration).

Owns the 'data' in the Track 03 loop: deal history and prospect evidence
are queried from Zetaris via SQL, not held in app memory.

API contract (from the Zetaris knowledge base, "Accessing Zetaris through
Rest API", kbase.zetaris.com):
- Auth: a login call returns an idToken (bearer token for later calls)
  plus a refreshToken; every API call also carries a requestId UUID header.
- Query: an "OpenSqlQuery"-style call takes a body of
  {"select": "<SQL>", "pageLimit": <1..100>} and returns result rows plus
  a queryToken; "PageSqlQuery" paginates with that token and
  "CloseSqlQuery" releases the server-side query.

Endpoint paths differ between Zetaris deployments (legacy SAAS vs the
Cloud enterprise instance provisioned for this hackathon), and the public
Postman collection repo is gone (404, checked 2026-10-24). So paths are
EXPLICIT constructor/env parameters — never guessed here. The browser
task in docs/ZETARIS_SETUP.md captures the real paths from the Cloud
console session; `from_env()` reads them. Until then the pipeline uses
the local JSON KB and says so in the trace (see act.gather).
"""
from __future__ import annotations

import json
import os
import subprocess
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class DealRecord:
    deal_id: str
    outcome: str  # "won" | "lost"
    niche: str
    service: str
    budget_usd: int | None
    reason: str
    source: str = "zetaris:deals"


@dataclass(frozen=True)
class ProspectEvidence:
    prospect: str
    signals: tuple[str, ...]
    source: str = "zetaris:prospects"


class ZetarisError(RuntimeError):
    """Raised when the Zetaris API call fails (auth, transport, bad SQL)."""


def _curl_post(url: str, token: str, payload: dict, timeout: int = 60) -> dict:
    """POST JSON via curl (urllib proxy-tunnels time out in this sandbox;
    the Jev client already uses the curl path for the same reason)."""
    env = {k: v for k, v in os.environ.items()
           if k not in ("no_proxy", "NO_PROXY")}
    proc = subprocess.run(
        ["curl", "-sS", "--max-time", str(timeout), "-X", "POST", url,
         "--noproxy", "127.0.0.1,localhost",
         "-H", f"Authorization: Bearer {token}",
         "-H", "Content-Type: application/json",
         "-H", f"requestId: {uuid.uuid4()}",
         "--data", json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout + 10, env=env,
    )
    if proc.returncode != 0:
        raise ZetarisError(f"curl to {url} failed: {proc.stderr.strip()[:300]}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise ZetarisError(f"non-JSON response from {url}: {proc.stdout[:300]}")


def _rows_of(body: dict) -> tuple[list, str | None]:
    """Extract result rows + next queryToken from a query response.

    Response shapes vary by deployment; accept rows under data/rows/
    results/records, as dicts or as lists paired with a columns list.
    """
    token = body.get("queryToken") or body.get("query_token")
    for key in ("data", "rows", "results", "records"):
        val = body.get(key)
        if isinstance(val, list):
            cols = body.get("columns") or body.get("schema") or []
            out = []
            for r in val:
                if isinstance(r, dict):
                    out.append(r)
                elif isinstance(r, list) and cols:
                    out.append(dict(zip(cols, r)))
            return out, token
    return [], token


class ZetarisClient:
    """Thin SQL client over the Zetaris data layer."""

    def __init__(self, api_url: str, id_token: str,
                 open_path: str, page_path: str, close_path: str,
                 deals_table: str = "deals",
                 prospects_table: str = "prospects"):
        if not api_url or not id_token:
            raise ValueError("ZetarisClient needs api_url + id_token")
        if not (open_path and page_path and close_path):
            raise ValueError(
                "ZetarisClient needs open/page/close query paths "
                "(see docs/ZETARIS_SETUP.md — paths come from the Cloud "
                "console session, they are not guessed here)")
        self.api_url = api_url.rstrip("/")
        self.id_token = id_token
        self.open_path = open_path
        self.page_path = page_path
        self.close_path = close_path
        self.deals_table = deals_table
        self.prospects_table = prospects_table

    @classmethod
    def from_env(cls) -> "ZetarisClient":
        """Build from env. Raises ValueError listing exactly what's missing."""
        missing = [k for k in ("ZETARIS_API_URL", "ZETARIS_ID_TOKEN",
                               "ZETARIS_OPEN_PATH", "ZETARIS_PAGE_PATH",
                               "ZETARIS_CLOSE_PATH")
                   if not os.getenv(k)]
        if missing:
            raise ValueError(f"Zetaris env missing: {', '.join(missing)} "
                             f"(see docs/ZETARIS_SETUP.md)")
        return cls(
            api_url=os.environ["ZETARIS_API_URL"],
            id_token=os.environ["ZETARIS_ID_TOKEN"],
            open_path=os.environ["ZETARIS_OPEN_PATH"],
            page_path=os.environ["ZETARIS_PAGE_PATH"],
            close_path=os.environ["ZETARIS_CLOSE_PATH"],
            deals_table=os.getenv("ZETARIS_DEALS_TABLE", "deals"),
            prospects_table=os.getenv("ZETARIS_PROSPECTS_TABLE", "prospects"),
        )

    def query(self, sql: str, page_limit: int = 100) -> list[dict]:
        """Run SQL against Zetaris, following pagination to completion."""
        body = _curl_post(f"{self.api_url}{self.open_path}", self.id_token,
                          {"select": sql, "pageLimit": page_limit})
        rows, token = _rows_of(body)
        guard = 0
        while token and guard < 20:
            guard += 1
            body = _curl_post(f"{self.api_url}{self.page_path}", self.id_token,
                              {"queryToken": token, "pageLimit": page_limit})
            more, token = _rows_of(body)
            rows.extend(more)
            if not more:
                break
        if token:
            try:
                _curl_post(f"{self.api_url}{self.close_path}", self.id_token,
                           {"queryToken": token})
            except ZetarisError:
                pass  # close is best-effort; rows are already collected
        return rows

    def similar_deals(self, niche: str, service: str, limit: int = 5) -> list[DealRecord]:
        rows = self.query(
            f"SELECT deal_id, outcome, niche, service, budget_usd, reason "
            f"FROM {self.deals_table}")
        deals = []
        for r in rows:
            try:
                deals.append(DealRecord(
                    deal_id=str(r["deal_id"]),
                    outcome=str(r["outcome"]).lower(),
                    niche=str(r["niche"]),
                    service=str(r["service"]),
                    budget_usd=(int(r["budget_usd"]) if r.get("budget_usd") not in (None, "") else None),
                    reason=str(r["reason"]),
                ))
            except (KeyError, TypeError, ValueError):
                continue
        if not deals:
            raise ZetarisError(f"no rows returned from {self.deals_table}")

        def score(d: DealRecord) -> int:
            s = 0
            if d.niche.lower() == niche.lower():
                s += 2
            if d.service.lower() == service.lower():
                s += 2
            return s

        ranked = sorted(deals, key=score, reverse=True)
        return [d for d in ranked if score(d) > 0][:limit] or ranked[:limit]

    def prospect_evidence(self, prospect_hint: str) -> ProspectEvidence:
        rows = self.query(
            f"SELECT signal FROM {self.prospects_table} LIMIT 20")
        signals = tuple(str(r.get("signal", "")) for r in rows if r.get("signal"))
        if not signals:
            signals = ("no external prospect data in Zetaris for this brief",)
        return ProspectEvidence(prospect=prospect_hint or "unknown",
                                signals=signals)
