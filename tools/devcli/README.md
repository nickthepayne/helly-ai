# Helly Dev CLI

Minimal helper to run both backends and call the /app APIs. No external deps.

## Usage

- Start both services (Ctrl+C to stop):
  - `python3 tools/devcli/devcli.py up`
    - Uses `./app/gradlew bootRun` and, for /ai, `npm run dev` (fallback: `make run`).
    - Override with env: `APP_CMD`, `AI_CMD`.

- Create a team member:
  - `python3 tools/devcli/devcli.py create-member --name "Max" --role "Engineer" --relationship "reports" --start-date 2024-01-01`

- Add feedback (optionally pass member id):
  - `python3 tools/devcli/devcli.py add-feedback --content "Max improved the API performance" --member-id <uuid>`

- Ask a question:
  - `python3 tools/devcli/devcli.py ask --text "What should I discuss with Max?"`

Base URL defaults to `http://localhost:8080`. Override with `--base-url` or env `APP_URL`.
- List feedback (optionally filter by member/time):
  - `python3 tools/devcli/devcli.py list-feedback [--member-id <uuid>] [--from-ts 2024-06-01T00:00:00Z] [--to-ts 2024-06-30T23:59:59Z]`




## Example: no-AI member create & feedback

Start only the app, then create a member and add feedback using the CLI.

```bash
# Start only /app (no /ai)
python3 tools/devcli/devcli.py up --skip-ai
# In another terminal:
python3 tools/devcli/devcli.py create-member \
  --name "Max Muster" \
  --role "Engineer" \
  --relationship "reports" \
  --start-date 2024-01-01
# Use the printed member id below
python3 tools/devcli/devcli.py add-feedback \
  --content "Max improved the API performance significantly." \
  --member-id <member-id>
```

To start fresh, you can wipe local DBs:

```bash
python3 tools/devcli/devcli.py wipe
```
