"""Weather proxy application.

Proxies requests to the Open-Meteo API and normalises the responses.

Endpoints:
    GET /health                 - health check
    GET /weather                - current weather for a location
    GET /forecast               - multi-day forecast for a location

Run:
    uv run uvicorn main:app --reload
"""

import os
from contextlib import asynccontextmanager
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

load_dotenv()

BASE_URL = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1/forecast")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "10.0"))

client: httpx.AsyncClient | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Create a shared AsyncClient on startup and close it on shutdown."""
    global client
    client = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)
    try:
        yield
    finally:
        if client is not None:
            await client.aclose()
            client = None


app = FastAPI(title="Weather Proxy", version="0.1.0", lifespan=lifespan)


class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    temperature: float
    wind_speed: float
    source: str = "open-meteo"


class ForecastDay(BaseModel):
    date: str
    temperature_max: float | None = None
    temperature_min: float | None = None
    wind_speed_max: float | None = None


class ForecastResponse(BaseModel):
    latitude: float
    longitude: float
    days: int
    forecast: list[ForecastDay]
    source: str = "open-meteo"


def _require_client() -> httpx.AsyncClient:
    if client is None:
        raise HTTPException(status_code=503, detail="HTTP client not initialized")
    return client


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/test")
async def test() -> dict[str, str]:
    """Test endpoint returning 200 OK."""
    return {"status": "ok"}


@app.get("/weather", response_model=WeatherResponse)
async def weather(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude (-90 to 90)"),
    longitude: float = Query(
        ..., ge=-180, le=180, description="Longitude (-180 to 180)"
    ),
) -> Any:
    """Current weather for a location, proxied from Open-Meteo."""
    http_client = _require_client()
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m",
    }
    try:
        response = await http_client.get(BASE_URL, params=params)
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504, detail=f"Upstream request timed out: {exc}"
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502, detail=f"Upstream API unavailable: {exc}"
        ) from exc

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Upstream API returned status {response.status_code}",
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502, detail=f"Unknown response format: {exc}"
        ) from exc

    try:
        current = data["current"]
        return WeatherResponse(
            latitude=float(data["latitude"]),
            longitude=float(data["longitude"]),
            temperature=float(current["temperature_2m"]),
            wind_speed=float(current["wind_speed_10m"]),
            source="open-meteo",
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502, detail=f"Unknown response format: {exc}"
        ) from exc


@app.get("/forecast", response_model=ForecastResponse)
async def forecast(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude (-90 to 90)"),
    longitude: float = Query(
        ..., ge=-180, le=180, description="Longitude (-180 to 180)"
    ),
    days: int = Query(3, ge=1, le=7, description="Number of forecast days (1 to 7)"),
) -> Any:
    """Multi-day forecast for a location, proxied from Open-Meteo."""
    http_client = _require_client()
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,windspeed_10m_max",
        "forecast_days": days,
    }
    try:
        response = await http_client.get(BASE_URL, params=params)
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504, detail=f"Upstream request timed out: {exc}"
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502, detail=f"Upstream API unavailable: {exc}"
        ) from exc

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Upstream API returned status {response.status_code}",
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502, detail=f"Unknown response format: {exc}"
        ) from exc

    try:
        daily = data["daily"]
        forecast_days = [
            ForecastDay(
                date=daily["time"][i],
                temperature_max=daily["temperature_2m_max"][i],
                temperature_min=daily["temperature_2m_min"][i],
                wind_speed_max=daily["windspeed_10m_max"][i],
            )
            for i in range(len(daily["time"]))
        ]
        return ForecastResponse(
            latitude=float(data["latitude"]),
            longitude=float(data["longitude"]),
            days=days,
            forecast=forecast_days,
            source="open-meteo",
        )
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=502, detail=f"Unknown response format: {exc}"
        ) from exc
