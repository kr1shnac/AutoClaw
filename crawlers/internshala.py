import time
from .base import BaseCrawler

class InternshalaCrawler(BaseCrawler):
    """
    Crawler implementation for Internshala.
    """
    def __init__(self, headless: bool = True):
        super().__init__(headless)

    def apply_to_job(self, url: str, profile_data: dict, resume_path: str):
        """
        Executes the Internshala application flow using basic DOM navigation.
        """
        try:
            page = self.start_session()
            print(f"Navigating to Internshala job: {url}")
            page.goto(url, timeout=30000)
            
            # Step 1: Login if required (assuming session isn't persisted)
            # Internshala typically requires login before applying
            if page.locator("text='Login'").count() > 0 and page.locator("text='Login'").first.is_visible():
                print("Login required. Attempting login...")
                page.locator("text='Login'").first.click()
                
                # Wait for login modal
                page.wait_for_selector("input#modal_email", timeout=5000)
                page.locator("input#modal_email").fill(profile_data.get('email', ''))
                page.locator("input#modal_password").fill(profile_data.get('password', ''))
                page.locator("button#modal_login_submit").click()
                
                # Wait for navigation/reload after login
                page.wait_for_load_state('networkidle')
            
            # Step 2: Click 'Apply now'
            apply_buttons = page.locator("button:has-text('Apply now')")
            if apply_buttons.count() == 0:
                print("No 'Apply now' button found. Already applied or job closed.")
                return False
                
            apply_buttons.first.click()
            time.sleep(2) # Give UI time to transition
            
            # Step 3: Handle Cover Letter / Custom Questions if present
            # Internshala usually brings up an 'Application' modal/page
            cover_letter_box = page.locator("textarea[name='cover_letter']")
            if cover_letter_box.count() > 0:
                print("Filling cover letter...")
                cover_letter_box.fill(profile_data.get('cover_letter', 'I am excited to apply for this position.'))
                
            # Step 4: Submit Application
            submit_button = page.locator("input[type='submit'][value='Submit']")
            if submit_button.count() > 0:
                print("Submitting application...")
                # Note: In a real script, we actually click this. 
                # For safety during testing/development, we might just log it unless configured otherwise.
                submit_button.first.click()
                print("Internshala application submitted successfully!")
                return True
            else:
                print("Could not find final submit button.")
                return False
                
        except Exception as e:
            print(f"Internshala automation failed: {e}")
            return False
        finally:
            self.close_session()

