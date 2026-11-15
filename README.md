# Weather Proxy

A small FastAPI application that proxies weather requests to the [Open-Meteo API](https://open-meteo.com/en/docs) and normalises the responses.

## Stack

* Python 3.12+
* [FastAPI](https://fastapi.tiangolo.com/)
* [uvicorn](https://www.uvicorn.org/)
* [httpx](https://www.python-httpx.org/) (AsyncClient)
* [uv](https://github.com/astral-sh/uv) (package manager & venv)
* [ruff](https://github.com/astral-sh/ruff) (formatter / linter)

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check. Returns `{"status": "ok"}`. |
| `GET` | `/weather?latitude=41.7151&longitude=44.8271` | Current weather, normalised from Open-Meteo. |
| `GET` | `/forecast?latitude=41.7151&longitude=44.8271&days=3` | Forecast for the given number of days (1–7). |

### Query parameter validation

* `latitude` — required, `-90` to `90`
* `longitude` — required, `-180` to `180`
* `days` — optional, `1` to `7` (default `3`)

Invalid requests are answered with `4xx` (FastAPI/Pydantic returns `422` with a meaningful message).

## Configuration

Configuration is read from a `.env` file (loaded via `python-dotenv`):

| Variable | Default | Description |
|----------|---------|-------------|
| `OPEN_METEO_BASE_URL` | `https://api.open-meteo.com/v1/forecast` | Base URL of the external weather API |
| `REQUEST_TIMEOUT` | `10.0` | Upstream request timeout in seconds |

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```

## Error handling

| Situation | Status | Detail |
|-----------|--------|--------|
| Upstream API unavailable / network error | `502` | "Upstream API unavailable: ..." |
| Upstream request timeout | `504` | "Upstream request timed out: ..." |
| Upstream non-2xx response | `502` | "Upstream API returned status N" |
| Unknown / malformed response format | `502` | "Unknown response format: ..." |
| Invalid query parameters | `422` | Pydantic validation error |

## How to run

Prerequisites: [uv](https://github.com/astral-sh/uv) installed.

```bash
# 1. Create the virtual environment (Python 3.12 pinned via .python-version)
uv venv

# 2. Install dependencies
uv add fastapi uvicorn httpx python-dotenv
uv add --dev ruff

# 3. Configure
cp .env.example .env

# 4. Run the server
uv run uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Quick checks

```bash
# Health check
curl http://127.0.0.1:8000/health
# => {"status":"ok"}

# Current weather
curl "http://127.0.0.1:8000/weather?latitude=41.7151&longitude=44.8271"
# => {"latitude":41.7151,"longitude":44.8271,"temperature":...,"wind_speed":...,"source":"open-meteo"}

# Forecast for 3 days
curl "http://127.0.0.1:8000/forecast?latitude=41.7151&longitude=44.8271&days=3"
```

## Linting / formatting

```bash
uv run ruff format
uv run ruff check
```
