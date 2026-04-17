"""
Test Suite for Blog Automation Pipeline
Covers: Content generation, Selenium browser setup, login verification, and publishing flow.
Run with: python test_blog.py
"""
import os
import sys
import unittest
import json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(SCRIPT_DIR, "src")
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
sys.path.insert(0, SRC_DIR)

class TestContentGeneration(unittest.TestCase):
    """Test cases for the AI content generation module."""

    def test_gemini_api_key_exists(self):
        """TC-01: Verify GEMINI_API_KEY is set in environment."""
        from dotenv import load_dotenv
        load_dotenv(os.path.join(SCRIPT_DIR, ".env"))
        api_key = os.getenv("GEMINI_API_KEY")
        self.assertIsNotNone(api_key, "GEMINI_API_KEY must be set in .env")
        self.assertNotEqual(api_key, "your_gemini_api_key_here", "Replace placeholder with real API key")

    def test_generate_blog_creates_files(self):
        """TC-02: Verify generate_blog.py creates title and content files."""
        title_path = os.path.join(DATA_DIR, "blog_title.txt")
        content_path = os.path.join(DATA_DIR, "blog_content.txt")
        self.assertTrue(os.path.exists(title_path), "blog_title.txt must exist in 'data/' (run generate_blog.py first)")
        self.assertTrue(os.path.exists(content_path), "blog_content.txt must exist in 'data/' (run generate_blog.py first)")

    def test_generated_title_not_empty(self):
        """TC-03: Verify generated title is not empty."""
        title_path = os.path.join(DATA_DIR, "blog_title.txt")
        if os.path.exists(title_path):
            with open(title_path, "r", encoding="utf-8") as f:
                title = f.read().strip()
            self.assertTrue(len(title) > 0, "Title should not be empty")
            self.assertTrue(len(title) < 200, "Title should be reasonable length")

    def test_generated_content_not_empty(self):
        """TC-04: Verify generated content has substance."""
        content_path = os.path.join(DATA_DIR, "blog_content.txt")
        if os.path.exists(content_path):
            with open(content_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            self.assertTrue(len(content) > 50, "Content should have at least 50 characters")


class TestSeleniumSetup(unittest.TestCase):
    """Test cases for Selenium WebDriver configuration."""

    def test_chrome_binary_exists(self):
        """TC-05: Verify Chrome browser is installed."""
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        self.assertTrue(os.path.exists(chrome_path), "Google Chrome must be installed")

    def test_chrome_profile_exists(self):
        """TC-06: Verify Chrome user profile directory exists."""
        profile_path = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data")
        self.assertTrue(os.path.exists(profile_path), "Chrome user profile must exist")

    def test_selenium_import(self):
        """TC-07: Verify Selenium library is installed and importable."""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            self.assertTrue(True)
        except ImportError:
            self.fail("Selenium is not installed. Run: pip install selenium")


class TestPublishingWorkflow(unittest.TestCase):
    """Test cases for the publishing workflow logic."""

    def test_load_blog_content_function(self):
        """TC-08: Verify load_blog_content reads files correctly."""
        from publish_blog import load_blog_content
        try:
            title, content = load_blog_content()
            self.assertIsInstance(title, str)
            self.assertIsInstance(content, str)
            self.assertTrue(len(title) > 0)
            self.assertTrue(len(content) > 0)
        except FileNotFoundError:
            self.skipTest("Blog files not generated yet")

    def test_direct_publish_flag(self):
        """TC-09: Verify --direct-publish flag is accepted by generate_blog.py."""
        import subprocess
        result = subprocess.run(
            [sys.executable, os.path.join(SRC_DIR, "generate_blog.py"), "--help"],
            cwd=SCRIPT_DIR, capture_output=True, text=True
        )
        self.assertIn("--direct-publish", result.stdout, "Script must accept --direct-publish flag")


class TestJenkinsPipeline(unittest.TestCase):
    """Test cases for Jenkins pipeline configuration."""

    def test_jenkinsfile_exists(self):
        """TC-10: Verify Jenkinsfile exists in project."""
        jenkinsfile = os.path.join(SCRIPT_DIR, "Jenkinsfile")
        self.assertTrue(os.path.exists(jenkinsfile), "Jenkinsfile must exist")

    def test_jenkinsfile_has_required_stages(self):
        """TC-11: Verify Jenkinsfile contains required pipeline stages."""
        jenkinsfile = os.path.join(SCRIPT_DIR, "Jenkinsfile")
        with open(jenkinsfile, "r") as f:
            content = f.read()
        self.assertIn("pipeline", content, "Must be a declarative pipeline")
        self.assertIn("Generate", content, "Must have Generate stage")
        self.assertIn("Publish", content, "Must have Publish stage")
        self.assertIn("DIRECT_PUBLISH", content, "Must support DIRECT_PUBLISH parameter")
        self.assertIn("cron", content, "Must have scheduled trigger")

    def test_jenkinsfile_has_approval_stage(self):
        """TC-12: Verify Jenkinsfile has manual approval stage."""
        jenkinsfile = os.path.join(SCRIPT_DIR, "Jenkinsfile")
        with open(jenkinsfile, "r") as f:
            content = f.read()
        self.assertIn("input", content, "Must have manual approval (input step)")

    def test_jenkinsfile_has_reporting(self):
        """TC-13: Verify Jenkinsfile has reporting in post section."""
        jenkinsfile = os.path.join(SCRIPT_DIR, "Jenkinsfile")
        with open(jenkinsfile, "r") as f:
            content = f.read()
        self.assertIn("post", content, "Must have post section for reporting")


if __name__ == "__main__":
    # Run tests and generate report
    unittest.main(verbosity=2)
