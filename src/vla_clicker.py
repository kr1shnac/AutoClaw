import asyncio
import os
import re
import base64
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from google import genai

# Import our Set-of-Mark module from Task 3.1
import sys
sys.path.insert(0, os.path.dirname(__file__))
from vla_marker import inject_markers, remove_markers

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Initialize Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def _get_gemini_client():
    """Returns a configured Gemini client, or None if no API key is set."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_google_ai_studio_key_here":
        print("[VLA] WARNING: No valid GEMINI_API_KEY found in .env. Running in mock mode.")
        return None
    return genai.Client(api_key=GEMINI_API_KEY)

async def identify_element(screenshot_path: str, target_description: str) -> int | None:
    """
    Sends a Set-of-Mark screenshot to Gemini 1.5 Flash Vision API
    and asks it to identify which numbered element matches the target.
    
    Returns the element number (int), or None if identification fails.
    """
    client = _get_gemini_client()
    
    if client is None:
        # Mock mode: return element 1 as fallback for testing
        print(f"[VLA Mock] Would ask Gemini: 'Which number is the {target_description}?'")
        print("[VLA Mock] Returning element 1 as fallback.")
        return 1
    
    # Read the screenshot and encode as base64
    with open(screenshot_path, "rb") as f:
        image_bytes = f.read()
    
    prompt = f"""You are an AI assistant helping an automation agent interact with web pages.

This screenshot has numbered red bounding boxes drawn over every interactive element on the page. Each box has a small red number label above it.

**Task:** Identify which numbered element corresponds to: "{target_description}"

**Rules:**
1. Respond with ONLY the number. No explanation, no text, just the number.
2. If no element matches, respond with "0".

Which number is the "{target_description}"?"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"inline_data": {"mime_type": "image/png", "data": base64.b64encode(image_bytes).decode()}},
                        {"text": prompt}
                    ]
                }
            ]
        )
        
        # Parse the response — we expect just a number
        answer = response.text.strip()
        print(f"[VLA] Gemini response: '{answer}'")
        
        # Extract the first number from the response
        match = re.search(r'\d+', answer)
        if match:
            element_num = int(match.group())
            return element_num if element_num > 0 else None
        return None
        
    except Exception as e:
        print(f"[VLA] Gemini API error: {e}")
        return None

async def vla_click(page, target_description: str) -> bool:
    """
    The full VLA pipeline:
    1. Inject Set-of-Mark numbered bounding boxes onto the page
    2. Take a screenshot
    3. Send to Gemini Vision to identify the target element
    4. Look up the X/Y coordinates from the element map
    5. Execute a hardware-level mouse click at those coordinates
    6. Clean up markers
    
    Returns True if click was executed, False otherwise.
    """
    screenshot_path = "/tmp/autoclaw_vla_screenshot.png"
    
    # Step 1 & 2: Inject markers and capture screenshot
    print(f"[VLA] Target: '{target_description}'")
    element_map = await inject_markers(page)
    await page.screenshot(path=screenshot_path, full_page=False)
    print(f"[VLA] Marked {len(element_map)} elements. Screenshot saved.")
    
    if not element_map:
        print("[VLA] No interactive elements found on page.")
        await remove_markers(page)
        return False
    
    # Step 3: Ask Gemini to identify the target
    element_num = await identify_element(screenshot_path, target_description)
    
    if element_num is None:
        print("[VLA] Gemini could not identify the target element.")
        await remove_markers(page)
        return False
    
    # Step 4: Look up coordinates
    str_num = str(element_num)
    if str_num not in element_map:
        print(f"[VLA] Element #{element_num} not found in element map (max: {max(int(k) for k in element_map.keys())}).")
        await remove_markers(page)
        return False
    
    target = element_map[str_num]
    x, y = target['x'], target['y']
    print(f"[VLA] Clicking element #{element_num} <{target['tag']}> \"{target['text'][:40]}\" at ({x}, {y})")
    
    # Step 5: Remove markers before clicking (don't want to click the overlay)
    await remove_markers(page)
    
    # Step 6: Hardware-level mouse click
    await page.mouse.click(x, y)
    print(f"[VLA] Click executed at ({x}, {y})!")
    
    # Clean up temp screenshot
    try:
        os.remove(screenshot_path)
    except OSError:
        pass
    
    return True

# --- TEST ---
if __name__ == "__main__":
    async def test_vla_pipeline():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = await context.new_page()
            
            print("[Test] Navigating to https://example.com ...")
            await page.goto("https://example.com", wait_until="networkidle")
            
            # Run the full VLA pipeline to find and click "More information..."
            success = await vla_click(page, "More information link")
            
            if success:
                print(f"[Test] VLA click succeeded! Current URL: {page.url}")
            else:
                print("[Test] VLA click failed.")
            
            await browser.close()
    
    asyncio.run(test_vla_pipeline())
