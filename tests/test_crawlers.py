import os
import sys

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crawlers.internshala import InternshalaCrawler
from crawlers.lever import LeverCrawler
from crawlers.greenhouse import GreenhouseCrawler

# Sample data for testing purposes
MOCK_PROFILE = {
    "first_name": "Nuhan",
    "last_name": "Test",
    "full_name": "Nuhan Test",
    "email": "nuhan.test@example.com",
    "phone": "9876543210",
    "linkedin_url": "https://linkedin.com/in/nuhan-test",
    "github_url": "https://github.com/nuhan-test",
    "portfolio_url": "https://nuhan.dev",
    "current_company": "AutoClaw Sandbox",
    "password": "FakePassword123",
    "cover_letter": "I am eager to join the team and contribute my skills in Python and automation.",
    # EEO fields
    "eeo_gender": "Decline To Self Identify",
    "eeo_race": "Decline To Self Identify",
    "eeo_veteran": "I don't wish to answer",
    "eeo_disability": "I don't wish to answer",
}

def test_internshala():
    print("Testing Internshala Crawler...")
    crawler = InternshalaCrawler(headless=False)
    test_url = "https://internshala.com/internship/detail/software-engineering-internship"
    result = crawler.apply_to_job(test_url, MOCK_PROFILE, "./resume.pdf")
    print(f"Internshala Test Finished. Script Returned: {result}")

def test_lever():
    print("Testing Lever Crawler...")
    crawler = LeverCrawler(headless=False)
    test_url = "https://jobs.lever.co/example/12345-abc-def-ghi"
    result = crawler.apply_to_job(test_url, MOCK_PROFILE, "./resume.pdf", "./resume.docx")
    print(f"Lever Test Finished. Script Returned: {result}")

def test_greenhouse():
    print("Testing Greenhouse Crawler...")
    crawler = GreenhouseCrawler(headless=False)
    # A real public Greenhouse posting can be used here for visual testing
    test_url = "https://boards.greenhouse.io/example/jobs/12345"
    result = crawler.apply_to_job(test_url, MOCK_PROFILE, "./resume.pdf", "./resume.docx")
    print(f"Greenhouse Test Finished. Script Returned: {result}")

if __name__ == "__main__":
    print("Running visual verification tests for ATS Crawlers...")

    # Uncomment the crawler you want to visually test:
    # test_internshala()
    # test_lever()
    # test_greenhouse()

    print("Tests completed (or skipped).")
