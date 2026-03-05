import time
from .base import BaseCrawler

class LeverCrawler(BaseCrawler):
    """
    Crawler implementation for Lever ATS.
    """
    def __init__(self, headless: bool = True):
        super().__init__(headless)

    def apply_to_job(self, url: str, profile_data: dict, resume_path_pdf: str, resume_path_docx: str = None):
        """
        Executes the Lever application flow, handling recursive multi-page forms.
        """
        try:
            page = self.start_session()
            print(f"Navigating to Lever job: {url}")
            page.goto(url, timeout=30000)
            
            # Step 1: Click 'Apply for this job'
            # Lever has a standard "Apply for this job" button usually at the top or bottom
            apply_button = page.get_by_text("Apply for this job", exact=False)
            if apply_button.count() > 0:
                apply_button.first.click()
                # Wait for the application form section to become visible
                page.wait_for_selector("form", timeout=5000)
            else:
                print("Apply button not found. May already be on the application form.")
            
            # Step 2: Upload Resume
            # Lever uses an input element with name or id usually containing 'resume'
            # We use our utility to try uploading the PDF, or fallback to DOCX
            file_input = "input[type='file']"
            if page.locator(file_input).count() > 0:
                print("Attempting to upload resume...")
                self.upload_resume(page, file_input, resume_path_pdf, resume_path_docx)
                # Wait for parsing to finish (Lever often auto-fills after upload)
                time.sleep(3)
                
            # Step 3: Loop through the Application Form
            # Lever can sometimes split forms, so we use a while loop
            max_pages = 5
            current_page = 0
            
            while current_page < max_pages:
                current_page += 1
                
                # Fill basic standard details using semantic locators where possible
                self._fill_standard_lever_fields(page, profile_data)
                
                # Check for "Submit application" button
                submit_button = page.locator("button:has-text('Submit application')")
                if submit_button.count() > 0:
                    print(f"Found submit button on page {current_page}.")
                    # submit_button.first.click()  # Uncomment to actually submit
                    print("Lever application ready to be submitted successfully!")
                    return True
                
                # Check for a "Next" or "Continue" button if it's a multi-page form
                next_button = page.locator("button:has-text('Next'), button:has-text('Continue')")
                if next_button.count() > 0:
                    print(f"Clicking Next to proceed to page {current_page + 1}...")
                    next_button.first.click()
                    time.sleep(2) # Give UI time to transition
                else:
                    print("Neither Submit nor Next button found. Halting loop.")
                    break
                    
            print("Lever automation halted without submitting.")
            return False
            
        except Exception as e:
            print(f"Lever automation failed: {e}")
            return False
        finally:
            self.close_session()

    def _fill_standard_lever_fields(self, page, profile_data):
        """Fills common Lever input fields."""
        
        # Lever usually uses 'name' attributes matching these general patterns
        fields_to_try = [
            ("input[name='name']", profile_data.get('full_name')),
            ("input[name='email']", profile_data.get('email')),
            ("input[name='phone']", profile_data.get('phone')),
            ("input[name='urls[LinkedIn]']", profile_data.get('linkedin_url')),
            ("input[name='urls[GitHub]']", profile_data.get('github_url')),
            ("input[name='urls[Portfolio]']", profile_data.get('portfolio_url'))
        ]
        
        for selector, value in fields_to_try:
            if value:
                self.fill_input_if_exists(page, selector, value)
                
        # Handle 'org' or 'company' field if present
        self.fill_input_if_exists(page, "input[name='org']", profile_data.get('current_company'))
