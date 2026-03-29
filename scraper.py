from datetime import datetime
import httpx
import asyncio

CITY_SLUG = {
    "El Hamma": "hamma",
    "Tunis": "tunis",
    "Sfax": "sfax",
    "Sousse": "sousse",
    "Kairouan": "kairouan",
    "Tataouine": "tataouine",
    "Medenine": "medenine",
    "Zarzis": "zarzis",
    "Benguerdane": "benguerdane",
    "Kebili": "kebili",
    "Douz": "douz",
    "Souk Lahad": "souklahad",
    "Gafsa": "gafsa",
    "Sidi Bouzid": "sidibouzid",
    "Tozeur": "tozeur",
    "Kasserine": "kasserine",
    "Sbeitla": "sbeitla",
    "Djerba (Khalfallah)": "djerba",
    "Meknassi": "meknassi",
    "Skhira": "skhira",
}

async def fetch_city(client: httpx.AsyncClient, city: str, slug: str) -> dict:
    url = f"https://gabeslouages.tn/public/clients_gabes/detail-{slug}.json"
    try:
        response = await client.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_seats = sum(item.get("placesdispo", 0) for item in data)
            info_parts = list(set(
                item.get("ligne", "") for item in data if item.get("ligne")
            ))
            info = " / ".join(info_parts[:3]) if info_parts else city
            return {
                "city": city,
                "available_seats": total_seats,
                "info": info,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "scraped_at": datetime.now().isoformat(),
                "slug": slug
            }
    except Exception as e:
        print(f"Error fetching {city}: {e}")
    return None

async def scrape_louages():
    results = []
    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_city(client, city, slug)
            for city, slug in CITY_SLUG.items()
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