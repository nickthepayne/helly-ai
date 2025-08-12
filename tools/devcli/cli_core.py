#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
from typing import List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# Paths and defaults
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
APP_DIR = os.path.join(ROOT, "app")
AI_DIR = os.path.join(ROOT, "ai")
DEFAULT_APP_URL = os.getenv("APP_URL", "http://localhost:8080")


# ----- Process helpers -----

def run_cmd(cmd: List[str], cwd: str) -> subprocess.Popen:
    return subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        start_new_session=True,  # kill process group on shutdown
    )


def choose_ai_cmd() -> List[str]:
    override = os.getenv("AI_CMD")
    if override:
        return override.split()
    if os.path.exists(os.path.join(AI_DIR, "package.json")):
        return ["npm", "run", "dev"]
    return ["make", "run"]


def choose_app_cmd() -> List[str]:
    override = os.getenv("APP_CMD")
    if override:
        return override.split()
    return ["./gradlew", "bootRun"]


def stop_proc(proc: subprocess.Popen):
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except Exception:
        try:
            proc.terminate()
        except Exception:
            pass


# ----- HTTP helpers -----

def http_post(path: str, body: dict, base_url: Optional[str] = None):
    url = (base_url or DEFAULT_APP_URL).rstrip("/") + path
    data = json.dumps(body).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req) as resp:
            payload = resp.read().decode("utf-8")
            try:
                return json.loads(payload)
            except json.JSONDecodeError:
                return {"raw": payload}
    except HTTPError as e:
        print(f"HTTP {e.code} calling {url}: {e.read().decode('utf-8')}")
        sys.exit(1)
    except URLError as e:
        print(f"Error calling {url}: {e}")
        sys.exit(1)


def http_get(path: str, query: dict | None = None, base_url: Optional[str] = None):
    url = (base_url or DEFAULT_APP_URL).rstrip("/") + path
    if query:
        url += "?" + urlencode({k: v for k, v in query.items() if v is not None})
    req = Request(url, method="GET")
    try:
        with urlopen(req) as resp:
            payload = resp.read().decode("utf-8")
            try:
                return json.loads(payload)
            except json.JSONDecodeError:
                return {"raw": payload}
    except HTTPError as e:
        print(f"HTTP {e.code} calling {url}: {e.read().decode('utf-8')}")
        sys.exit(1)
    except URLError as e:
        print(f"Error calling {url}: {e}")
        sys.exit(1)


# ----- Commands -----

def cmd_up(args):
    app_cmd = choose_app_cmd()
    ai_cmd = choose_ai_cmd()

    print(f"Starting /app: {' '.join(app_cmd)} (cwd={APP_DIR})")
    app = run_cmd(app_cmd, cwd=APP_DIR)

    time.sleep(2)

    ai = None
    if not getattr(args, "skip_ai", False):
        print(f"Starting /ai: {' '.join(ai_cmd)} (cwd={AI_DIR})")
        ai = run_cmd(ai_cmd, cwd=AI_DIR)

    try:
        while True:
            if app.poll() is not None:
                print("/app stopped. Exiting...")
                break
            if ai is not None and ai.poll() is not None:
                print("/ai stopped. Exiting...")
                break
            if app.stdout and not app.stdout.closed:
                while True:
                    line = app.stdout.readline()
                    if not line:
                        break
                    sys.stdout.write(f"[app] {line}")
            if ai is not None and ai.stdout and not ai.stdout.closed:
                while True:
                    line = ai.stdout.readline()
                    if not line:
                        break
                    sys.stdout.write(f"[ai ] {line}")
            sys.stdout.flush()
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        if ai is not None:
            stop_proc(ai)
        stop_proc(app)


def cmd_wipe(args):
    # Clear all tables in SQLite DB (keep schema)
    db_path = os.path.join(APP_DIR, "build", "helly.db")
    if not os.path.exists(db_path):
        print(f"No DB file found at {db_path}")
        return
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'flyway_%'")
        tables = cursor.fetchall()
        cleared = []
        for (table_name,) in tables:
            cursor.execute(f"DELETE FROM {table_name}")
            cleared.append(table_name)
        conn.commit()
        conn.close()
        if cleared:
            print("Cleared tables:\n" + "\n".join(cleared))
        else:
            print("No tables found to clear.")
    except Exception as e:
        print(f"Failed to clear tables: {e}")
        sys.exit(1)


def cmd_create_member(args):
    payload = {
        "name": args.name,
        "role": args.role,
        "relationshipToManager": args.relationship,
        "startDate": args.start_date,
    }
    resp = http_post("/v1/team-members", payload, args.base_url)
    print(json.dumps(resp, indent=2))


def cmd_add_feedback(args):
    payload = {
        "content": args.content,
        "personHint": args.member_id,
        "createdAt": args.created_at,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    resp = http_post("/v1/feedback", payload, args.base_url)
    print(json.dumps(resp, indent=2))


def cmd_ask(args):
    payload = {"text": args.text}
    resp = http_post("/v1/ask", payload, args.base_url)
    print(json.dumps(resp, indent=2))


def cmd_list_feedback(args):
    query = {"memberId": args.member_id, "from": args.from_ts, "to": args.to_ts}
    resp = http_get("/v1/feedback", query, args.base_url)
    print(json.dumps(resp, indent=2))

