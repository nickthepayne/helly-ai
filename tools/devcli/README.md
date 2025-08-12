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

