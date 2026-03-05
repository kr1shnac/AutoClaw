import asyncio
import random
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import urllib.parse

async def human_delay(min_seconds: float = 3.0, max_seconds: float = 8.0):
    """
    Introduces a randomized delay to mimic human behavior and avoid rate limits/bans.
    """
    delay = random.uniform(min_seconds, max_seconds)
    print(f"[Stealth] Sleeping for {delay:.2f} seconds...")
    await asyncio.sleep(delay)

async def scrape_linkedin_jobs(keyword: str, location: str, max_jobs: int = 10) -> list[str]:
    """
    Stealthily navigates LinkedIn's public job search and extracts job URLs.
    """
    encoded_keyword = urllib.parse.quote(keyword)
    encoded_location = urllib.parse.quote(location)
    
    # Using the public Jobs search URL (no login required for browsing these results initially)
    url = f"https://www.linkedin.com/jobs/search?keywords={encoded_keyword}&location={encoded_location}&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"
    
    job_links = []
    
    async with async_playwright() as p:
        # Launching Chromium. Headless=True for linux testing environment.
        browser = await p.chromium.launch(headless=True)
        
        # Set a realistic viewport and user agent
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        # Apply playwright-stealth to hide WebDriver flags
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        print(f"Navigating to LinkedIn Jobs: {keyword} in {location}")
        await page.goto(url)
        await human_delay(4.0, 7.0)
        
        # Wait for the main job container to appear
        try:
            await page.wait_for_selector("ul.jobs-search__results-list", timeout=10000)
            print("Job list loaded.")
        except Exception as e:
            print(f"Error finding job list container: {e}. Check if blocked by CAPTCHA.")
            await browser.close()
            return []

        # LinkedIn lazily loads jobs as you scroll down.
        # We need to scroll the window multiple times to reveal enough jobs.
        scrolls = 0
        max_scrolls = 5
        
        while len(job_links) < max_jobs and scrolls < max_scrolls:
            # Extract links currently in the DOM
            elements = await page.query_selector_all(".base-card__full-link")
            
            for elem in elements:
                link = await elem.get_attribute("href")
                if link and link not in job_links:
                    # Clean the URL (remove tracking parameters after the '?')
                    clean_link = link.split('?')[0] if '?' in link else link
                    job_links.append(clean_link)
                    if len(job_links) >= max_jobs:
                        break
            
            if len(job_links) >= max_jobs:
                break
                
            # Scroll down to trigger lazy loading
            print(f"Extracted {len(job_links)} links so far. Scrolling down...")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            await human_delay(3.0, 6.0)
            scrolls += 1
            
            # Occasionally try to click the "See more jobs" button if it appears
            try:
                see_more_btn = await page.query_selector("button.infinite-scroller__show-more-button--visible")
                if see_more_btn:
                    print("Clicking 'See more jobs' button...")
                    await see_more_btn.click()
                    await human_delay(2.0, 4.0)
            except Exception:
                pass

        await browser.close()
        
    return job_links[:max_jobs]

if __name__ == "__main__":
    print("Starting Stealth LinkedIn Scraper...")
    # Attempting to fetch 5 Python Developer jobs in New York
    links = asyncio.run(scrape_linkedin_jobs("Python Developer", "New York", max_jobs=5))
    
    print("\n--- EXTRACTED JOB LINKS ---")
    for i, link in enumerate(links, 1):
        print(f"{i}. {link}")
    print("---------------------------\n")
