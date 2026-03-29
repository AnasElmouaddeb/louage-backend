import asyncio
import sys
import os
import random
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scraper import scrape_louages, scrape_detail

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = {
    "data": [],
    "last_updated": None
}

def is_peak_hours():
    hour = datetime.now().hour
    return 4 <= hour < 21

async def refresh_data():
    # Random delay 1-5 seconds to avoid detection
    await asyncio.sleep(random.uniform(1, 5))
    print(f"[{datetime.now()}] Refreshing louage data...")
    try:
        cache["data"] = await scrape_louages()
        cache["last_updated"] = datetime.now().isoformat()
        print(f"Done. {len(cache['data'])} destinations loaded.")
    except Exception as e:
        print(f"Scraping error: {e}")

async def smart_scheduler():
    while True:
        await refresh_data()
        if is_peak_hours():
            interval = 60        # 1 minute during the day
            print("Next refresh in 1 minute (peak hours)")
        else:
            interval = 600       # 10 minutes at night
            print("Next refresh in 10 minutes (night hours)")
        await asyncio.sleep(interval)

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Louage API is running",
        "peak_hours": is_peak_hours()
    }

@app.get("/louages")
def get_louages():
    return {
        "last_updated": cache["last_updated"],
        "count": len(cache["data"]),
        "peak_hours": is_peak_hours(),
        "data": cache["data"]
    }

@app.get("/louages/{city}/detail")
async def get_city_detail(city: str):
    louage = next(
        (item for item in cache["data"] if item["city"].lower() == city.lower()),
        None
    )
    if not louage:
        return {"error": f"City '{city}' not found"}

    slug = louage.get("slug", city.lower())
    detail = await scrape_detail(slug)

    return {
        "city": louage["city"],
        "info": louage["info"],
        "available_seats": louage["available_seats"],
        "last_update": louage["last_update"],
        "louages": detail
    }

@app.get("/louages/{city}")
def get_city(city: str):
    result = [
        item for item in cache["data"]
        if item["city"].lower() == city.lower()
    ]
    if not result:
        return {"error": f"City '{city}' not found"}
    return result[0]

@app.on_event("startup")
async def startup():
    asyncio.create_task(smart_scheduler())