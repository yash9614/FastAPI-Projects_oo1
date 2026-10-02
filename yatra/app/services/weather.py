import os
from collections import defaultdict
from datetime import date

import httpx
from dotenv import load_dotenv

from app.model import WeatherResponseModel
from app.services.cache import get_cache, set_cache

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


async def fetch_weather(
    destination: str,
    start_date: date,
    end_date: date,
) -> list[WeatherResponseModel]:
    if not OPENWEATHER_API_KEY:
        raise RuntimeError("OPENWEATHER_API_KEY is missing from .env")

    cache_key = f"{destination}_{start_date}_{end_date}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "q": destination,
                "appid": OPENWEATHER_API_KEY,
                "units": "metric",
            },
        )
        if response.status_code != 200:
            raise RuntimeError(f"weather {response.status_code}: {response.text}")
        data = response.json()

    by_day: dict[str, list] = defaultdict(list)
    for slot in data["list"]:
        day = slot["dt_txt"][:10]
        if start_date.isoformat() <= day <= end_date.isoformat():
            by_day[day].append(slot)

    forcasts = []
    for day, slots in sorted(by_day.items()):
        forcasts.append(
            WeatherResponseModel(
                date=day,
                condition=slots[0]["weather"][0]["description"],
                temperature_high=max(s["main"]["temp_max"] for s in slots),
                temperature_low=min(s["main"]["temp_min"] for s in slots),
                humidity=sum(s["main"]["humidity"] for s in slots) / len(slots),
                rain_chance=max(s.get("pop", 0) for s in slots) * 100,
            )
        )

    set_cache(cache_key, forcasts, ttl=3600)
    return forcasts
