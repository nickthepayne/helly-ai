#!/usr/bin/env python3
"""
Minimal dev CLI to run both backends and call /app APIs.
- No external deps (stdlib only)
- Focuses on command definitions; implementation lives in cli_core.py

Environment overrides:
- APP_URL (default http://localhost:8080)
- AI_CMD (optional) override command to run /ai
- APP_CMD (optional) override command to run /app
"""
from __future__ import annotations

import argparse
from cli_core import (
    DEFAULT_APP_URL,
    cmd_up,
    cmd_wipe,
    cmd_create_member,
    cmd_add_feedback,
    cmd_ask,
    cmd_list_feedback,
)


def main():
    parser = argparse.ArgumentParser(description="Helly dev CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # Processes
    up = sub.add_parser("up", help="Start both /app and /ai (Ctrl+C to stop)")
    up.add_argument("--skip-ai", action="store_true", help="Do not start /ai")
    up.set_defaults(func=cmd_up)

    # APIs
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

    lf = sub.add_parser("list-feedback", help="GET /v1/feedback")
    lf.add_argument("--member-id", required=False)
    lf.add_argument("--from-ts", required=False)
    lf.add_argument("--to-ts", required=False)
    lf.add_argument("--base-url", default=DEFAULT_APP_URL)
    lf.set_defaults(func=cmd_list_feedback)

    # Utilities
    wipe = sub.add_parser("wipe", help="Clear all tables (keep schema)")
    wipe.set_defaults(func=cmd_wipe)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

