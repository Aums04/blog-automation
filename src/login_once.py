"""
One-time login helper — saves your Dev.to session to the Selenium profile.
Run this ONCE. After that, publish_blog.py will reuse this session automatically.
"""
import subprocess, time

SELENIUM_PROFILE = "C:/Temp/selenium_devto_profile"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

print("=" * 50)
print("  One-Time Login Setup for Dev.to")
print("=" * 50)
print("\nOpening Chrome with the Selenium profile...")
print("1. Log into https://dev.to (use GitHub or Email)")
print("2. Once logged in (you see your profile icon), come back here")
print("3. Press ENTER to save the session\n")

cmd = [
    CHROME_PATH,
    f"--user-data-dir={SELENIUM_PROFILE}",
    "--no-first-run",
    "--no-default-browser-check",
    "--start-maximized",
    "https://dev.to/enter"
]

process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
input(">>> Press ENTER after you have logged into Dev.to <<<")
process.terminate()
print("\nDone! Your Dev.to login is saved. You can now run: python publish_blog.py")
