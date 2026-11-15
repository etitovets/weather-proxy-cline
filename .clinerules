# FastAPI-application to weather-proxy


## Stack

* Language: Python3.12
* Framework: FastAPI
* HTTP-Clirnt: httpx (AsyncClient)
* Packets manager: uv
* Formatter/Linter: ruff

## Specification

### Endpoints
* Health check:
    `GET /health`
  Returns:
    `{"status": "ok"}`
* Current weather (proxy request to Open-Meteo and normalise answer):
    `GET /weather?latitude=41.7151&longitude=44.8271`
  Request to:
    `https://api.open-meteo.com/v1/forecast?latitude=41.7151&longitude=44.8271&current=temperature_2m,wind_speed_10m`
  Returns:
    `{
      "latitude": 41.7151,
      "longitude": 44.8271,
      "temperature": 28.4,
      "wind_speed": 12.1,
      "source": "open-meteo"
    }`
* Forecast for several days:
  `GET /forecast?latitude=41.7151&longitude=44.8271&days=3`
  Returns:
    Forecast for the specified number of days.

## Additional Requirements

1. Use `httpx.AsyncClient` for external requests
2. Parameters validations (use FastAPI/Pydantic):
    * latitude — from -90 to 90
    * longitude — from -180 to 180
    * days — from 1 to 7
3. Error handling
    * External API unavailable or answers timeout
    * Unknown response format
    * Invalid user's request. Must answer 4xx with meaningful text
4. Configuration:
    `.env` or settings with base URL of external API
5. README.md with description and instructions how use and run

## Constrains

* Run `ruff format` and `ruff check` and fix all WARNINGS
* Local tests:
  run `uv run uvicorn main:app --reload`
  in another terminal run:
  `curl http://127.0.0.1:8000/health`. Must got `{"status":"ok"}`
  `curl "http://127.0.0.1:8000/weather?latitude=41.7151&longitude=44.8271"`. Must got `{"latitude":41.7151,"longitude":44.8271,"temperature":...,"wind_speed":...,"source":"open-meteo"}

## Documentation
https://open-meteo.com/en/docs
