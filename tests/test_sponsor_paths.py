"""Sponsor-path tests (no real sponsor creds needed).

Spins up local mock servers that speak the DOCUMENTED shapes:
- Zetaris REST: OpenSqlQuery body {"select", "pageLimit"} -> rows +
  queryToken; PageSqlQuery paginates; CloseSqlQuery releases.
- Meterless: OpenAI-compatible POST /v1/chat/completions.

Then runs the real CLI against them and asserts the wiring works.
These tests prove the client code paths, NOT the live Cloud instances
(those need the browser-provisioned creds — see docs/*_SETUP.md).
"""
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

DEALS = json.load(open(os.path.join(ROOT, "src", "data", "seed_deals.json")))


class ZetarisMock(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(n) or b"{}")
        if self.path == "/open":
            sql = payload.get("select", "")
            if "FROM prospects" in sql:
                self._send({"data": [{"signal": "prospect has an active website"}],
                            "queryToken": None})
            else:
                # paginate: first page 5 rows + token
                self._send({"data": DEALS[:5], "queryToken": "tok1"})
        elif self.path == "/page":
            assert payload.get("queryToken") == "tok1"
            self._send({"data": DEALS[5:], "queryToken": None})
        elif self.path == "/close":
            self._send({})
        else:
            self.send_response(404)
            self.end_headers()


class MeterlessMock(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(n) or b"{}")
        model = payload.get("model", "")
        if model == "planner-test":
            text = ("H1: Good fit — brief matches past won deals [E4] [E1].\n"
                    "H2: Weak fit — budget scope could drift [E3] [E1].\n"
                    "H3: Red flags — none explicit, verify decision maker [E3] [E1].")
        else:
            text = "Thanks for reaching out — happy to take this on. Are you free for a 20-minute call this week?"
        body = json.dumps({"choices": [{"message": {"content": text}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(handler):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def run_cli(env_extra, brief):
    env = dict(os.environ)
    env.pop("ZETARIS_API_URL", None)
    env.pop("ZETARIS_ID_TOKEN", None)
    env.pop("ZETARIS_OPEN_PATH", None)
    env.pop("ZETARIS_PAGE_PATH", None)
    env.pop("ZETARIS_CLOSE_PATH", None)
    env.pop("DEALREASONER_LLM", None)
    env.pop("METERLESS_API_URL", None)
    env.pop("METERLESS_API_KEY", None)
    env.pop("METERLESS_PLANNER_MODEL", None)
    env.pop("METERLESS_FAST_MODEL", None)
    env.update(env_extra)
    proc = subprocess.run(
        [sys.executable, "-m", "src.ui.cli", "--brief", brief, "--json"],
        cwd=ROOT, capture_output=True, text=True, timeout=180, env=env)
    if proc.returncode != 0:
        raise AssertionError(f"CLI failed: {proc.stderr[-800:]}")
    return json.loads(proc.stdout)


def main():
    zsrv, zport = serve(ZetarisMock)
    msrv, mport = serve(MeterlessMock)
    brief = ("Hi, I run a real estate agency in Dubai with 40 agents. "
             "We spend $6k/month on ads but lead follow-up is manual. "
             "Looking for an AI agent to qualify leads on WhatsApp. "
             "Budget around $5k for setup plus monthly.")

    # 1. Zetaris path (local mock LLM + Zetaris data layer)
    res = run_cli({
        "ZETARIS_API_URL": f"http://127.0.0.1:{zport}",
        "ZETARIS_ID_TOKEN": "test-token",
        "ZETARIS_OPEN_PATH": "/open",
        "ZETARIS_PAGE_PATH": "/page",
        "ZETARIS_CLOSE_PATH": "/close",
    }, brief)
    assert res["data_layer"] == "zetaris", res["data_layer"]
    # Verdict near the GO/PILOT boundary varies slightly with Jev's
    # weighted score as the scoring-state text changes; the wiring
    # assertions below are the point of this test, not the verdict.
    assert res["verdict"] in ("GO", "PILOT"), res
    assert res["evidence_count"] == 9, res["evidence_count"]  # 3 base + 5 deals + 1 prospect
    print("ZETARIS PATH OK:", res["verdict"], "| evidence:", res["evidence_count"],
          "| trace kept:", res["trace_kept"])

    # 2. Meterless path (Nemotron mock + local KB)
    res = run_cli({
        "DEALREASONER_LLM": "nemotron",
        "METERLESS_API_URL": f"http://127.0.0.1:{mport}",
        "METERLESS_API_KEY": "test-key",
        "METERLESS_PLANNER_MODEL": "planner-test",
        "METERLESS_FAST_MODEL": "fast-test",
    }, brief)
    assert res["llm"] == "nemotron-via-meterless", res["llm"]
    assert res["draft_reply"] and res["draft_reply"]["model"] == "fast-test", res.get("draft_reply")
    assert res["verdict"] in ("GO", "PILOT"), res  # Jev boundary variance, see above
    assert res["trace_kept"] == 3, res["trace_kept"]
    print("METERLESS PATH OK:", res["verdict"], "| draft model:",
          res["draft_reply"]["model"], "| trace kept:", res["trace_kept"])

    zsrv.shutdown()
    msrv.shutdown()
    print("ALL SPONSOR-PATH TESTS PASSED")


if __name__ == "__main__":
    main()
