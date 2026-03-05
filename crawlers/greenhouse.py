import time
from .base import BaseCrawler

class GreenhouseCrawler(BaseCrawler):
    """
    Crawler implementation for Greenhouse ATS.
    Uses accessibility locators (get_by_label, get_by_role) as the primary
    navigation strategy before falling back to Krishna's VLA system.
    """
    def __init__(self, headless: bool = True):
        super().__init__(headless)

    def apply_to_job(self, url: str, profile_data: dict, resume_path_pdf: str, resume_path_docx: str = None):
        """
        Executes the Greenhouse application flow using accessibility-first locators.
        """
        try:
            page = self.start_session()
            print(f"Navigating to Greenhouse job: {url}")
            page.goto(url, timeout=30000)

            # Step 1: Click "Apply for this job" button if present (some Greenhouse pages embed the form)
            apply_button = page.get_by_role("link", name="Apply for this job")
            if apply_button.count() == 0:
                apply_button = page.get_by_role("button", name="Apply")

            if apply_button.count() > 0:
                apply_button.first.click()
                page.wait_for_load_state('networkidle', timeout=10000)

            # Step 2: Upload Resume (Dual-Format logic)
            self._handle_resume_upload(page, resume_path_pdf, resume_path_docx)

            # Step 3: Fill standard application fields using accessibility locators
            self._fill_greenhouse_fields(page, profile_data)

            # Step 4: Handle EEO (Equal Employment Opportunity) questions
            self._handle_eeo_questions(page, profile_data)

            # Step 5: Submit the application
            submit_button = page.get_by_role("button", name="Submit Application")
            if submit_button.count() > 0:
                print("Submit button found. Application ready.")
                # submit_button.first.click()  # Uncomment for live run
                print("Greenhouse application ready to submit!")
                return True
            else:
                print("Submit button not found. VLA fallback needed.")
                return False

        except Exception as e:
            print(f"Greenhouse automation failed: {e}")
            return False
        finally:
            self.close_session()

    def _handle_resume_upload(self, page, resume_path_pdf: str, resume_path_docx: str = None):
        """
        Dual-format resume upload: checks the file input's 'accept' attribute
        to determine whether to upload PDF or DOCX.
        """
        file_input = page.locator("input[type='file']")
        if file_input.count() == 0:
            print("No file upload input found on page.")
            return

        # Check the 'accept' attribute to determine preferred file type
        accept_attr = file_input.first.get_attribute("accept") or ""

        if ".doc" in accept_attr and resume_path_docx:
            # Site prefers Word documents
            print("Site prefers DOCX. Uploading DOCX resume...")
            self.upload_resume(page, "input[type='file']", resume_path_docx)
        else:
            # Default to PDF (universally accepted)
            print("Uploading PDF resume...")
            self.upload_resume(page, "input[type='file']", resume_path_pdf)

        # Wait for Greenhouse to parse and auto-fill fields from the resume
        time.sleep(3)

    def _fill_greenhouse_fields(self, page, profile_data: dict):
        """
        Fills standard Greenhouse form fields using accessibility-based locators.
        get_by_label is the most resilient approach as labels rarely change.
        """
        print("Filling standard Greenhouse fields...")

        field_map = [
            ("First name",    profile_data.get("first_name")),
            ("Last name",     profile_data.get("last_name")),
            ("Email",         profile_data.get("email")),
            ("Phone",         profile_data.get("phone")),
            ("LinkedIn Profile", profile_data.get("linkedin_url")),
            ("Website",       profile_data.get("portfolio_url")),
            ("GitHub",        profile_data.get("github_url")),
        ]

        for label_text, value in field_map:
            if not value:
                continue
            try:
                field = page.get_by_label(label_text, exact=False)
                if field.count() > 0:
                    field.first.fill(value)
                    print(f"  Filled: {label_text}")
            except Exception as e:
                print(f"  Could not fill '{label_text}': {e}")

    def _handle_eeo_questions(self, page, profile_data: dict):
        """
        Handles optional EEO (Equal Employment Opportunity) dropdown questions.
        These are standard Greenhouse questions about gender, ethnicity, veteran status.
        """
        print("Handling optional EEO questions...")

        eeo_field_map = [
            ("Gender",          profile_data.get("eeo_gender", "Decline To Self Identify")),
            ("Race",            profile_data.get("eeo_race", "Decline To Self Identify")),
            ("Veteran Status",  profile_data.get("eeo_veteran", "I don't wish to answer")),
            ("Disability Status", profile_data.get("eeo_disability", "I don't wish to answer")),
        ]

        for label_text, value in eeo_field_map:
            if not value:
                continue
            try:
                # EEO questions in Greenhouse are typically <select> dropdowns
                dropdown = page.get_by_label(label_text, exact=False)
                if dropdown.count() > 0:
                    dropdown.first.select_option(label=value)
                    print(f"  Set EEO '{label_text}' to: {value}")
            except Exception as e:
                print(f"  Could not set EEO '{label_text}': {e}")
