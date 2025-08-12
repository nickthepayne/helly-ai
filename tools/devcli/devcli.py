#!/usr/bin/env python3
"""
Minimal dev CLI to run both backends and call /app APIs.
- No external deps (stdlib only): argparse, subprocess, urllib
- 'up' starts /app and /ai, streaming logs; Ctrl+C stops both
- Simple API commands: create-member, add-feedback, ask

Environment:
- APP_URL (default http://localhost:8080)
- AI_CMD (optional) override command to run /ai (default: tries 'npm run dev', then 'make run')
- APP_CMD (optional) override command to run /app (default: './gradlew bootRun')
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from typing import List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
APP_DIR = os.path.join(ROOT, "app")
AI_DIR = os.path.join(ROOT, "ai")
DEFAULT_APP_URL = os.getenv("APP_URL", "http://localhost:8080")


def run_cmd(cmd: List[str], cwd: str) -> subprocess.Popen:
    return subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        start_new_session=True,  # so we can kill the whole group
    )


def choose_ai_cmd() -> List[str]:
    override = os.getenv("AI_CMD")
    if override:
        return override.split()
    # Prefer npm run dev if package.json present; fallback to make run
    if os.path.exists(os.path.join(AI_DIR, "package.json")):
        return ["npm", "run", "dev"]
    return ["make", "run"]


def choose_app_cmd() -> List[str]:
    override = os.getenv("APP_CMD")
    if override:
        return override.split()
    # Wrapper script is committed under /app
    return ["./gradlew", "bootRun"]


def stream_output(name: str, proc: subprocess.Popen):
    assert proc.stdout is not None
    for line in proc.stdout:
        sys.stdout.write(f"[{name}] {line}")
        sys.stdout.flush()


def stop_proc(proc: subprocess.Popen):
    try:
        # Kill the process group started by start_new_session
        os.killpg(proc.pid, signal.SIGTERM)
    except Exception:
        try:
            proc.terminate()
        except Exception:
            pass


def cmd_up(args):
    app_cmd = choose_app_cmd()
    ai_cmd = choose_ai_cmd()

    print(f"Starting /app: {' '.join(app_cmd)} (cwd={APP_DIR})")
    app = run_cmd(app_cmd, cwd=APP_DIR)

    # Give the app a head start to build
    time.sleep(2)

    ai = None
    if not getattr(args, "skip_ai", False):
        print(f"Starting /ai: {' '.join(ai_cmd)} (cwd={AI_DIR})")
        ai = run_cmd(ai_cmd, cwd=AI_DIR)

    try:
        # Stream both until Ctrl+C
        while True:
            if app.poll() is not None:
                print("/app stopped. Exiting...")
                break
            if ai is not None and ai.poll() is not None:
                print("/ai stopped. Exiting...")
                break
            # Non-blocking read; rely on line-buffered pipes
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
    # Remove SQLite DB files created by the app
    to_remove = [
        os.path.join(APP_DIR, "build", "helly.db"),
        os.path.join(APP_DIR, "build", "test-helly.db"),
    ]
    removed = []
    for path in to_remove:
        try:
            if os.path.exists(path):
                os.remove(path)
                removed.append(path)
        except Exception as e:
            print(f"Failed to remove {path}: {e}")
            sys.exit(1)
    if removed:
        print("Removed:\n" + "\n".join(removed))
    else:
        print("No DB files found to remove.")


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
    # remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    resp = http_post("/v1/feedback", payload, args.base_url)
    print(json.dumps(resp, indent=2))


def cmd_ask(args):
    payload = {"text": args.text}
    resp = http_post("/v1/ask", payload, args.base_url)
    print(json.dumps(resp, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Helly dev CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    up = sub.add_parser("up", help="Start both /app and /ai (Ctrl+C to stop)")
    up.add_argument("--skip-ai", action="store_true", help="Do not start /ai")
    up.set_defaults(func=cmd_up)

    cm = sub.add_parser("create-member", help="POST /v1/team-members")
    cm.add_argument("--name", required=True)
    cm.add_argument("--role", required=True)
    cm.add_argument("--relationship", required=True, help="relationshipToManager")
    cm.add_argument("--start-date", required=True)
    cm.add_argument("--base-url", default=DEFAULT_APP_URL)
    cm.set_defaults(func=cmd_create_member)

    af = sub.add_parser("add-feedback", help="POST /v1/feedback")
    af.add_argument("--content", required=True)
    af.add_argument("--member-id", required=False, help="optional personHint")
    af.add_argument("--created-at", required=False)
    af.add_argument("--base-url", default=DEFAULT_APP_URL)
    af.set_defaults(func=cmd_add_feedback)

    ask = sub.add_parser("ask", help="POST /v1/ask")
    ask.add_argument("--text", required=True)
    ask.add_argument("--base-url", default=DEFAULT_APP_URL)
    ask.set_defaults(func=cmd_ask)

    wipe = sub.add_parser("wipe", help="Remove local SQLite DB files to start fresh")
    wipe.set_defaults(func=cmd_wipe)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

