from playwright.async_api import async_playwright
from datetime import datetime
import httpx
import traceback

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

async def scrape_louages():
    results = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            print("Browser opened, navigating to site...")

            await page.goto("https://www.gabeslouages.tn/")
            print("Page loaded, waiting for data...")
            await page.wait_for_timeout(6000)

            print("Looking for cards...")
            cards = await page.query_selector_all(".details")
            print(f"Found {len(cards)} cards")

            for card in cards:
                try:
                    city_el = await card.query_selector("h2")
                    city = (await city_el.inner_text()).strip() if city_el else "Unknown"

                    update_el = await card.query_selector("p")
                    update_time = (await update_el.inner_text()).strip() if update_el else ""

                    count_el = await card.query_selector(".count")
                    info = (await count_el.inner_text()).strip() if count_el else ""

                    price_el = await card.query_selector(".price")
                    seats_text = (await price_el.inner_text()).strip() if price_el else "0"
                    seats = int(seats_text)

                    results.append({
                        "city": city,
                        "available_seats": seats,
                        "info": info,
                        "last_update": update_time,
                        "scraped_at": datetime.now().isoformat(),
                        "slug": CITY_SLUG.get(city, city.lower())
                    })
                    print(f"  Parsed: {city} → {seats} seats")

                except Exception as e:
                    print(f"Error parsing card: {e}")

            await browser.close()
            print(f"Done. Total: {len(results)} destinations")

    except Exception as e:
        print("=== FULL ERROR ===")
        traceback.print_exc()

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