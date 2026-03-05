import os
from playwright.sync_api import sync_playwright, Page, BrowserContext

class BaseCrawler:
    """
    Abstract base class for all Applicant Tracking System (ATS) crawlers.
    Provides standard Playwright initialization and utility methods.
    """
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start_session(self):
        """Initializes the Playwright browser session."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = self.context.new_page()
        return self.page

    def close_session(self):
        """Closes the Playwright browser session."""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def upload_resume(self, page: Page, input_selector: str, resume_path_pdf: str, resume_path_docx: str = None):
        """
        Handles uploading a resume file. 
        Tries PDF first, falls back to DOCX if provided and requested by the site.
        """
        # In a generic ATS, we just upload the primary file (PDF usually preferred)
        # The specific scraper can decide which one to pass based on text hints.
        
        path_to_use = resume_path_pdf
        
        if not os.path.exists(path_to_use):
            print(f"Resume not found at {path_to_use}")
            return False
            
        try:
            # wait for the input element to be available (but it might be hidden visually)
            page.wait_for_selector(input_selector, state='attached', timeout=5000)
            page.set_input_files(input_selector, path_to_use)
            print(f"Successfully uploaded: {path_to_use}")
            return True
        except Exception as e:
            print(f"Failed to upload resume: {e}")
            return False

    def fill_input_if_exists(self, page: Page, selector: str, value: str):
        """Safely attempts to fill an input if it exists."""
        if not value:
            return False
            
        try:
            # We use a short timeout because these points are optional or might not exist
            element_exists = page.locator(selector).count() > 0
            if element_exists:
                page.locator(selector).first.fill(value)
                return True
        except Exception:
            pass
            
        return False
