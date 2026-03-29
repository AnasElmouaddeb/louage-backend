from datetime import datetime
import httpx
import asyncio

CITY_INFO = {
    "El Hamma":            {"slug": "hamma",      "info": "36 min / 31 km / 3 TND"},
    "Tunis":               {"slug": "tunis",       "info": "4h30 / 410 km / 32.450 TND"},
    "Sfax":                {"slug": "sfax",        "info": "2h10 / 140 km / 12.250 TND"},
    "Sousse":              {"slug": "sousse",      "info": "3h / 280 km / 22.300 TND"},
    "Kairouan":            {"slug": "kairouan",    "info": "3h10 / 225 km / 17.450 TND"},
    "Tataouine":           {"slug": "tataouine",   "info": "1h50 / 130 km / 11.300 TND"},
    "Medenine":            {"slug": "medenine",    "info": "1h05 / 80 km / 7.050 TND"},
    "Zarzis":              {"slug": "zarzis",      "info": "2h / 140 km / 12.700 TND"},
    "Benguerdane":         {"slug": "benguerdane", "info": "1h45 / 155 km / 13.550 TND"},
    "Kebili":              {"slug": "kebili",      "info": "1h30 / 120 km / 10.650 TND"},
    "Douz":                {"slug": "douz",        "info": "1h50 / 135 km / 13.350 TND"},
    "Souk Lahad":          {"slug": "souklahad",   "info": "1h50 / 130 km / 11.900 TND"},
    "Gafsa":               {"slug": "gafsa",       "info": "2h15 / 145 km / 13.350 TND"},
    "Sidi Bouzid":         {"slug": "sidibouzid",  "info": "2h30 / 180 km / 15.100 TND"},
    "Tozeur":              {"slug": "tozeur",      "info": "2h50 / 210 km / 17.600 TND"},
    "Kasserine":           {"slug": "kasserine",   "info": "3h40 / 250 km / 20.650 TND"},
    "Sbeitla":             {"slug": "sbeitla",     "info": "3h10 / 217 km / 18.800 TND"},
    "Djerba (Khalfallah)": {"slug": "djerba",      "info": "2h45 / 180 km / 14.550 TND"},
    "Meknassi":            {"slug": "meknassi",    "info": "1h45 / 130 km / 10.550 TND"},
    "Skhira":              {"slug": "skhira",      "info": "0h55 / 55 km / 4.650 TND"},
}

async def fetch_city(client: httpx.AsyncClient, city: str, info: dict) -> dict:
    url = f"https://gabeslouages.tn/public/clients_gabes/detail-{info['slug']}.json"
    try:
        response = await client.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_seats = sum(item.get("placesdispo", 0) for item in data)
            return {
                "city": city,
                "available_seats": total_seats,
                "info": info["info"],
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "scraped_at": datetime.now().isoformat(),
                "slug": info["slug"]
            }
    except Exception as e:
        print(f"Error fetching {city}: {e}")
    return None

async def scrape_louages():
    results = []
    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_city(client, city, info)
            for city, info in CITY_INFO.items()
        ]
        responses = await asyncio.gather(*tasks)
        results = [r for r in responses if r is not None]
    print(f"Done. {len(results)} destinations loaded.")
    return results

async def scrape_detail(city_slug: str):
    url = f"https://gabeslouages.tn/public/clients_gabes/detail-{city_slug}.json"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                louages = []
                for item in data:
                    louages.append({
                        "number": item.get("N", 0),
                        "plate": item.get("fleet_registration_id", ""),
                        "seats": item.get("placesdispo", 0)
                    })
                return louages
            return []
    except Exception as e:
        print(f"Detail scrape error for {city_slug}: {e}")
        return []