"""Local fixture server for the Autocomplete Form assignment.

Serves the static form and a mock REST API implementing FR-01..FR-05.

Run:
    python fixture/server.py            # 127.0.0.1:5057 by default

Environment:
    HOST                 bind host (default 127.0.0.1)
    PORT                 bind port (default 5057)
    FILTER_MODE          prefix | anywhere        (default prefix, per FR-02)
    REQUIRE_SUGGESTION   0 | 1                      (default 0, per FR-01)

Test hooks:
    POST /api/config     change filter_mode / require_suggestion_selection at runtime
    POST /api/reset      restore config defaults and drop the stored response
    ?inject=<fault>      on POST/GET /api/response* -- return a deliberately broken
                         payload so the API negative tests have something real to catch
"""
from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

FIXTURE_DIR = Path(__file__).parent

SUGGESTIONS = [
    "agile methodology",
    "agile methodology process",
    "agile methodology process testing",
]

# Login is out of scope, so the "authenticated" user is fixed here.
SESSION_USER = {
    "account_id": "98765",
    "account_email": "test123@gmail.com",
}

INVALID_INPUT_MESSAGE = "Invalid input. Please select a valid suggestion."


def _default_config() -> dict:
    return {
        "filter_mode": os.environ.get("FILTER_MODE", "prefix"),
        "require_suggestion_selection": os.environ.get("REQUIRE_SUGGESTION", "0") == "1",
    }


app = Flask(__name__)
_state = {"config": _default_config(), "latest": None}


def match_suggestions(text: str, mode: str) -> list[str]:
    """Suggestions that match `text` under the active filter mode (FR-02 / FR-03)."""
    t = (text or "").strip().lower()
    if not t:
        return []
    if mode == "anywhere":
        return [s for s in SUGGESTIONS if t in s.lower()]
    return [s for s in SUGGESTIONS if s.lower().startswith(t)]


def apply_inject(record: dict, fault: str | None) -> dict:
    """Corrupt a good record in one specific way, for negative API tests."""
    if not fault:
        return record
    r = deepcopy(record)
    if fault == "bad_locale":
        r["locale"] = "en"                       # missing region -> not full BCP 47
    elif fault == "string_completed":
        r["completed"] = "true"                  # string instead of boolean
    elif fault == "missing_field":
        r.pop("end_date", None)                  # required field absent
    elif fault == "utc_timestamps":
        for k in ("start_date", "end_date"):
            if isinstance(r.get(k), str):
                r[k] = r[k].split("+")[0].split(".")[0] + "Z"   # UTC, not local time
    elif fault == "all_suggestions":
        r["suggestion_list"] = ", ".join(SUGGESTIONS)           # ignores the filter
    elif fault == "empty_text":
        r["text"] = ""
    return r


def build_record(body: dict) -> dict:
    text = (body.get("text") or "").strip()
    mode = _state["config"]["filter_mode"]
    return {
        "account_id": SESSION_USER["account_id"],
        "account_email": SESSION_USER["account_email"],
        "start_date": body.get("start_date"),
        "end_date": body.get("end_date"),
        "locale": body.get("locale"),
        "text": text,
        "suggestion_list": ", ".join(match_suggestions(text, mode)),
        "completed": True,
    }


# ---- static form ----------------------------------------------------------
@app.route("/")
@app.route("/autocomplete-form")
def index():
    return send_from_directory(FIXTURE_DIR, "index.html")


@app.route("/app.js")
def app_js():
    return send_from_directory(FIXTURE_DIR, "app.js", mimetype="application/javascript")


@app.route("/styles.css")
def styles_css():
    return send_from_directory(FIXTURE_DIR, "styles.css", mimetype="text/css")


# ---- config / test hooks ------------------------------------------------
@app.get("/api/config")
def get_config():
    return jsonify(_state["config"])


@app.post("/api/config")
def set_config():
    body = request.get_json(silent=True) or {}
    for key in ("filter_mode", "require_suggestion_selection"):
        if key in body:
            _state["config"][key] = body[key]
    return jsonify(_state["config"])


@app.post("/api/reset")
def reset():
    _state["config"] = _default_config()
    _state["latest"] = None
    return jsonify({"reset": True})


# ---- response persistence (FR-04 / FR-05) -----------------------------
@app.post("/api/response")
def submit_response():
    body = request.get_json(silent=True) or {}
    text = (body.get("text") or "").strip()
    require_sel = _state["config"]["require_suggestion_selection"]

    if not text or (require_sel and text not in SUGGESTIONS):
        return jsonify({"error": INVALID_INPUT_MESSAGE}), 400

    record = build_record(body)
    _state["latest"] = record
    return jsonify(apply_inject(record, request.args.get("inject"))), 200


@app.get("/api/response/latest")
def latest_response():
    if _state["latest"] is None:
        return jsonify({"error": "no response recorded"}), 404
    return jsonify(apply_inject(_state["latest"], request.args.get("inject"))), 200


def main() -> None:
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5057"))
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
