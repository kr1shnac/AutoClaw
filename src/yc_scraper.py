import asyncio
import random
import os
import json
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# Path to pre-authenticated session cookies (Session Sweeping)
AUTH_STATE_PATH = os.path.join(os.path.dirname(__file__), "..", "auth", "state.json")

async def human_delay(min_seconds: float = 2.0, max_seconds: float = 5.0):
    """
    Randomized delay to mimic human browsing behavior.
    YC is less aggressive than LinkedIn, so we can use shorter delays.
    """
    delay = random.uniform(min_seconds, max_seconds)
    print(f"[Stealth] Sleeping for {delay:.2f} seconds...")
    await asyncio.sleep(delay)

async def scrape_yc_jobs(keyword: str = "", max_jobs: int = 10) -> list[dict]:
    """
    Navigates workatastartup.com, handles React lazy-loading via scrolling,
    and extracts job listings with their URLs and titles.
    
    Uses storageState cookies if available (auth/state.json), 
    otherwise falls back to unauthenticated public browsing.
    """
    # YC Work at a Startup public companies page
    base_url = "https://www.workatastartup.com/companies"
    if keyword:
        base_url += f"?query={keyword}"
    
    job_listings = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Load authenticated session if available (Session Sweeping)
        context_options = {
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        if os.path.exists(AUTH_STATE_PATH):
            print(f"[Auth] Loading session cookies from {AUTH_STATE_PATH}")
            context_options['storage_state'] = AUTH_STATE_PATH
        else:
            print("[Auth] No session cookies found. Running in unauthenticated (public) mode.")
        
        context = await browser.new_context(**context_options)
        page = await context.new_page()
        
        # Apply stealth patches
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        print(f"[Navigate] Going to: {base_url}")
        await page.goto(base_url, wait_until="networkidle")
        await human_delay(3.0, 5.0)
        
        # Incremental scrolling to trigger React lazy-loading
        # Instead of jumping to the bottom, we scroll in 800px increments
        # to simulate natural human reading behavior.
        scrolls = 0
        max_scrolls = 10
        previous_count = 0
        
        while len(job_listings) < max_jobs and scrolls < max_scrolls:
            # Extract company/job cards currently in the DOM
            # YC uses different selectors — we target the company listing links
            cards = await page.query_selector_all("a[href*='/companies/']")
            
            for card in cards:
                href = await card.get_attribute("href")
                title = await card.inner_text()
                
                if href and "/companies/" in href:
                    # Build full URL if relative
                    full_url = href if href.startswith("http") else f"https://www.workatastartup.com{href}"
                    # Clean the URL
                    clean_url = full_url.split('?')[0]
                    
                    # Deduplicate
                    if not any(j['url'] == clean_url for j in job_listings):
                        clean_title = title.strip().split('\n')[0]  # Take first line as title
                        if clean_title:
                            job_listings.append({
                                'url': clean_url,
                                'title': clean_title
                            })
                
                if len(job_listings) >= max_jobs:
                    break
            
            # Check if we found new listings
            if len(job_listings) == previous_count and scrolls > 2:
                print("[Scroll] No new listings found. Stopping scroll loop.")
                break
            previous_count = len(job_listings)
            
            if len(job_listings) >= max_jobs:
                break
            
            # Scroll down incrementally (800px at a time, like a human reading)
            print(f"[Scroll] Found {len(job_listings)} listings so far. Scrolling down...")
            await page.evaluate("window.scrollBy(0, 800);")
            await human_delay(1.5, 3.0)
            scrolls += 1
        
        # Save session state for future runs (Session Sweeping persistence)
        if not os.path.exists(AUTH_STATE_PATH):
            os.makedirs(os.path.dirname(AUTH_STATE_PATH), exist_ok=True)
            storage = await context.storage_state()
            with open(AUTH_STATE_PATH, 'w') as f:
                json.dump(storage, f)
            print(f"[Auth] Session state saved to {AUTH_STATE_PATH}")
        
        await browser.close()
    
    return job_listings[:max_jobs]

if __name__ == "__main__":
    print("Starting YC (Work at a Startup) Scraper...\n")
    listings = asyncio.run(scrape_yc_jobs(keyword="python", max_jobs=5))
    
    print("\n--- EXTRACTED YC LISTINGS ---")
    for i, listing in enumerate(listings, 1):
        print(f"{i}. {listing['title']}")
        print(f"   {listing['url']}")
    print("-----------------------------\n")
    print(f"Total: {len(listings)} listings extracted.")
