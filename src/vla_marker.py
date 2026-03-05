import asyncio
import json
from playwright.async_api import async_playwright

# The Set-of-Mark JavaScript Payload
# This script is injected into the page to draw numbered red bounding boxes
# over every interactive/clickable element. The resulting screenshot is then
# sent to Gemini Vision API (Task 3.2) to identify which element to click.
SET_OF_MARK_JS = """
(() => {
    // Remove any previous markers
    document.querySelectorAll('.autoclaw-marker').forEach(el => el.remove());
    
    // All interactive element selectors
    const selectors = 'a, button, input, select, textarea, [role="button"], [role="link"], [role="menuitem"], [onclick], [tabindex]';
    const elements = document.querySelectorAll(selectors);
    
    const elementMap = {};
    let counter = 1;
    
    elements.forEach((el) => {
        const rect = el.getBoundingClientRect();
        
        // Skip invisible or zero-size elements
        if (rect.width === 0 || rect.height === 0) return;
        if (window.getComputedStyle(el).visibility === 'hidden') return;
        if (window.getComputedStyle(el).display === 'none') return;
        if (el.offsetParent === null && el.tagName !== 'BODY') return;
        
        // Skip elements that are off-screen
        if (rect.bottom < 0 || rect.top > window.innerHeight) return;
        if (rect.right < 0 || rect.left > window.innerWidth) return;
        
        // Draw the red bounding box
        const box = document.createElement('div');
        box.className = 'autoclaw-marker';
        box.style.cssText = `
            position: fixed;
            left: ${rect.left}px;
            top: ${rect.top}px;
            width: ${rect.width}px;
            height: ${rect.height}px;
            border: 2px solid red;
            background: rgba(255, 0, 0, 0.08);
            pointer-events: none;
            z-index: 999999;
            box-sizing: border-box;
        `;
        
        // Draw the number label
        const label = document.createElement('div');
        label.className = 'autoclaw-marker';
        label.textContent = counter;
        label.style.cssText = `
            position: fixed;
            left: ${rect.left - 2}px;
            top: ${rect.top - 18}px;
            background: red;
            color: white;
            font-size: 11px;
            font-weight: bold;
            font-family: Arial, sans-serif;
            padding: 1px 5px;
            border-radius: 3px;
            pointer-events: none;
            z-index: 1000000;
            line-height: 15px;
        `;
        
        document.body.appendChild(box);
        document.body.appendChild(label);
        
        // Build the coordinate map for this element
        elementMap[counter] = {
            tag: el.tagName.toLowerCase(),
            type: el.type || '',
            text: (el.textContent || el.value || el.placeholder || el.getAttribute('aria-label') || '').trim().substring(0, 80),
            x: Math.round(rect.left + rect.width / 2),
            y: Math.round(rect.top + rect.height / 2),
            width: Math.round(rect.width),
            height: Math.round(rect.height)
        };
        
        counter++;
    });
    
    return JSON.stringify(elementMap);
})();
"""

# JS to clean up injected markers
REMOVE_MARKERS_JS = """
(() => {
    document.querySelectorAll('.autoclaw-marker').forEach(el => el.remove());
})();
"""

async def inject_markers(page) -> dict:
    """
    Injects the Set-of-Mark JS into the page.
    Returns a dict mapping element numbers to their coordinates and metadata.
    """
    result_json = await page.evaluate(SET_OF_MARK_JS)
    return json.loads(result_json)

async def remove_markers(page):
    """
    Removes all injected marker overlays from the page.
    """
    await page.evaluate(REMOVE_MARKERS_JS)

async def capture_marked_screenshot(page, screenshot_path: str = "marked_page.png") -> dict:
    """
    Injects markers onto the page, takes a screenshot, and returns the element map.
    The screenshot can then be sent to Gemini Vision API for element identification.
    """
    element_map = await inject_markers(page)
    await page.screenshot(path=screenshot_path, full_page=False)
    print(f"[VLA] Screenshot saved to: {screenshot_path}")
    print(f"[VLA] Marked {len(element_map)} interactive elements.")
    return element_map

# --- TEST ---
if __name__ == "__main__":
    async def test_vla():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = await context.new_page()
            
            # Test on a real page with interactive elements
            print("[Test] Navigating to https://example.com ...")
            await page.goto("https://example.com", wait_until="networkidle")
            
            # Inject markers and capture screenshot
            element_map = await capture_marked_screenshot(page, "test_marked_screenshot.png")
            
            print("\n--- ELEMENT MAP ---")
            for num, info in element_map.items():
                print(f"  [{num}] <{info['tag']}> \"{info['text'][:40]}\" at ({info['x']}, {info['y']})")
            print("-------------------\n")
            
            # Clean up
            await remove_markers(page)
            await browser.close()
            print("[Test] Done. Check test_marked_screenshot.png")
    
    asyncio.run(test_vla())
