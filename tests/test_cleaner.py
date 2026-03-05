import os
import sys
import unittest

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.cleaner import extract_clean_text

class TestCleaner(unittest.TestCase):

    def test_strip_basic_noise_tags(self):
        """Test that scripts, styles, and navs are completely removed."""
        html = """
        <html>
        <head><style>body { color: red; }</style></head>
        <body>
            <nav><ul><li>Home</li><li>About</li></ul></nav>
            <main>
                <h1>Software Engineer</h1>
                <p>We are hiring.</p>
            </main>
            <script>alert("tracker");</script>
            <footer>Copyright 2026</footer>
        </body>
        </html>
        """
        clean_text = extract_clean_text(html)
        
        self.assertNotIn("body { color: red; }", clean_text)
        self.assertNotIn("Home", clean_text)
        self.assertNotIn("alert", clean_text)
        self.assertNotIn("Copyright", clean_text)
        
        # Verify core content is preserved and formatted
        self.assertIn("# Software Engineer", clean_text)
        self.assertIn("We are hiring.", clean_text)

    def test_strip_noise_by_class_and_id(self):
        """Test removing elements based on common noise classes like 'sidebar' and 'cookie-banner'."""
        html = """
        <div>
            <div id="cookie-banner-123">Accept our cookies!</div>
            <div class="main-content">
                <h2>Requirements</h2>
                <ul>
                    <li>Python proficiency</li>
                </ul>
            </div>
            <div class="right-sidebar-promo">Buy our product!</div>
        </div>
        """
        clean_text = extract_clean_text(html)
        
        self.assertNotIn("Accept our cookies!", clean_text)
        self.assertNotIn("Buy our product!", clean_text)
        
        self.assertIn("## Requirements", clean_text)
        self.assertIn("* Python proficiency", clean_text)

    def test_link_and_image_stripping(self):
        """Test that markdownify strips raw URLs and images as requested in the config."""
        html = """
        <article>
            <p>Apply <a href="https://example.com/spam">here</a>!</p>
            <img src="tracker.gif" alt="tracking pixel"/>
        </article>
        """
        clean_text = extract_clean_text(html)
        
        self.assertNotIn("https://example.com/spam", clean_text)
        self.assertNotIn("tracker.gif", clean_text)
        self.assertIn("Apply here!", clean_text)

if __name__ == '__main__':
    unittest.main()
