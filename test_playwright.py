from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://www.gabeslouages.tn/")
    
    # Wait longer and for a specific element that contains the data
    page.wait_for_timeout(6000)
    
    content = page.content()
    
    # Search for city names we know exist from the site
    keywords = ["Tunis", "Sfax", "Sousse", "Médenine", "tunis", "sfax", "louage", "place", "siège", "siege", "voiture", "taxi"]
    
    for kw in keywords:
        idx = content.find(kw)
        if idx != -1:
            print(f"\n=== KEYWORD '{kw}' FOUND AT {idx} ===")
            print(content[max(0, idx-200):idx+500])
            print("...")
            break
    
    # Also print the last 3000 chars (data is usually at the bottom)
    print("\n\n=== LAST 3000 CHARS OF PAGE ===")
    print(content[-3000:])
    
    browser.close()