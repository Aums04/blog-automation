"""
Selenium Blog Publisher - Dev.to
Dev.to has a simple textarea editor with no bot detection.
Steps: Launch Chrome -> Log in -> New post -> Type title + content -> Publish

PREREQUISITE: Run login_once.py first to save your Dev.to session.
"""
import os
import sys
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SELENIUM_PROFILE = "C:/Temp/selenium_devto_profile"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEBUG_PORT = 9222
DEVTO_NEW_POST = "https://dev.to/new"


def launch_chrome_with_debug_port():
    """Launch Chrome with remote debugging — attaching Selenium to a real browser."""
    print(f"[Setup] Launching Chrome with remote debugging on port {DEBUG_PORT}...")
    cmd = [
        CHROME_PATH,
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={SELENIUM_PROFILE}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-notifications",
        "--start-maximized",
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(4)
    print("[Setup] Chrome launched.")
    return process


def attach_selenium_to_chrome():
    """Attach Selenium to the already-running Chrome via debug port."""
    print(f"[Setup] Attaching Selenium to Chrome on port {DEBUG_PORT}...")
    opts = Options()
    opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{DEBUG_PORT}")
    driver = webdriver.Chrome(options=opts)
    print("[Setup] Selenium attached.")
    return driver


def load_blog_content():
    """Read the generated blog title and content from the data folder."""
    data_dir = os.path.join(SCRIPT_DIR, "..", "data")
    title_path = os.path.join(data_dir, "blog_title.txt")
    content_path = os.path.join(data_dir, "blog_content.txt")
    if not os.path.exists(title_path) or not os.path.exists(content_path):
        raise FileNotFoundError("blog_title.txt or blog_content.txt not found in 'data/'. Run generate_blog.py first.")
    with open(title_path, "r", encoding="utf-8") as f:
        title = f.read().strip()
    with open(content_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    return title, content


def login_check(driver):
    """Navigate to Dev.to and verify we are logged in."""
    print("[Selenium] Step 1: Checking login on Dev.to...")
    driver.get("https://dev.to")
    time.sleep(4)

    # If user avatar / profile icon is in the page, we are logged in
    if "Log in" in driver.page_source and "Create account" in driver.page_source:
        print("[Selenium] Not logged in. Run login_once.py to log into Dev.to first.")
        return False

    print("[Selenium] Logged into Dev.to successfully.")
    return True


def write_and_publish(driver, title, content):
    """Open Dev.to editor, fill in the post, and publish."""
    wait = WebDriverWait(driver, 20)

    # Step 2: Navigate to new post editor
    print("[Selenium] Step 2: Opening Dev.to new post editor...")
    driver.get(DEVTO_NEW_POST)
    time.sleep(5)

    # Step 3: Type the title
    # Dev.to title field has id="article-form-title" or class contains "title"
    print(f"[Selenium] Step 3: Typing title: {title[:50]}...")
    try:
        title_field = wait.until(EC.presence_of_element_located(
            (By.ID, "article-form-title")
        ))
        # Scroll into view and activate via JS click (avoids overlay issues)
        driver.execute_script("arguments[0].scrollIntoView(true);", title_field)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", title_field)
        time.sleep(0.5)
        title_field.clear()
        clean_title = title.lstrip('#').strip()
        # Type character by character for reliability
        for char in clean_title:
            title_field.send_keys(char)
        print("[Selenium] Title typed successfully.")
    except Exception as e:
        print(f"[Selenium] Could not find title field: {e}")
        return False

    # Step 4: Type the content in the markdown editor
    # Dev.to body is a CodeMirror/plain textarea with id="article-body"
    print("[Selenium] Step 4: Typing blog content...")
    try:
        # Try CodeMirror editor first (newer Dev.to)
        content_selectors = [
            (By.ID, "article-body"),
            (By.CSS_SELECTOR, ".CodeMirror textarea"),
            (By.CSS_SELECTOR, "[aria-label='Post Content']"),
            (By.CSS_SELECTOR, "textarea.article-form__body"),
            (By.CSS_SELECTOR, ".cm-content"),
            (By.CSS_SELECTOR, "[contenteditable='true'].cm-content"),
        ]

        content_field = None
        for by, selector in content_selectors:
            try:
                content_field = driver.find_element(by, selector)
                if content_field:
                    print(f"[Selenium] Found content field: {selector}")
                    break
            except:
                continue

        if content_field:
            driver.execute_script("arguments[0].click();", content_field)
            time.sleep(0.5)
            content_field.send_keys(content)
            print("[Selenium] Content typed successfully.")
        else:
            # Fallback: click in the editor area visually
            editor_area = driver.find_element(By.CSS_SELECTOR, ".editor-area, .CodeMirror, article")
            editor_area.click()
            driver.switch_to.active_element.send_keys(content)
            print("[Selenium] Content typed via fallback method.")

    except Exception as e:
        print(f"[Selenium] Could not type content: {e}")
        return False

    time.sleep(2)

    # Step 5: Click Publish
    print("[Selenium] Step 5: Clicking Publish button...")
    try:
        publish_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Publish') and not(contains(., 'Save'))]")
        ))
        publish_btn.click()
        time.sleep(4)

        # Handle any confirmation dialog
        try:
            confirm_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Publish') or contains(., 'Confirm')]")
            ))
            confirm_btn.click()
            time.sleep(3)
        except:
            pass

        print("[Selenium] Publish button clicked!")
        time.sleep(3)

        # Verify: check if we are redirected to a published article URL
        current_url = driver.current_url
        if "dev.to" in current_url and "/new" not in current_url:
            print(f"[Selenium] Published! Article URL: {current_url}")
        else:
            print("[Selenium] Publishing may still be in progress.")

        return True

    except Exception as e:
        print(f"[Selenium] Could not click Publish: {e}")
        return False


def main():
    print("=" * 60)
    print("  Selenium Blog Publisher - Dev.to")
    print("  Experiment 6: End-to-End Automation Pipeline")
    print("=" * 60)

    title, content = load_blog_content()
    print(f"Loaded post: '{title[:60]}...'")
    print(f"Content length: {len(content)} chars\n")

    chrome_process = None
    driver = None

    try:
        chrome_process = launch_chrome_with_debug_port()
        driver = attach_selenium_to_chrome()

        if not login_check(driver):
            print("\nRun 'python login_once.py' and choose Dev.to to log in first.")
            return

        success = write_and_publish(driver, title, content)

        if success:
            print("\n[RESULT] Blog post published to Dev.to!")
        else:
            print("\n[RESULT] Could not complete publishing. Check the browser window.")

    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if driver:
            time.sleep(3)
            try:
                driver.quit()
            except:
                pass
        if chrome_process:
            chrome_process.terminate()
        print("[Selenium] Browser closed.")


if __name__ == "__main__":
    main()
