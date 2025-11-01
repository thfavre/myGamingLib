"""
Helper script to fix ChromeDriver issues on Windows.
Run this if you're getting ChromeDriver errors.
"""
import os
import shutil
import sys

def clear_webdriver_cache():
    """Clear the webdriver-manager cache."""
    print("Clearing webdriver-manager cache...")

    # Common cache locations
    if sys.platform == 'win32':
        cache_paths = [
            os.path.expanduser(r"~\.wdm"),
            os.path.expanduser(r"~\AppData\Local\.wdm"),
            os.path.expanduser(r"~\AppData\Roaming\.wdm"),
        ]
    else:
        cache_paths = [
            os.path.expanduser("~/.wdm"),
        ]

    cleared = False
    for cache_path in cache_paths:
        if os.path.exists(cache_path):
            try:
                shutil.rmtree(cache_path)
                print(f"✓ Cleared cache at: {cache_path}")
                cleared = True
            except Exception as e:
                print(f"✗ Could not clear {cache_path}: {e}")

    if not cleared:
        print("No cache found to clear.")
    else:
        print("\nCache cleared! Try running the scraper again.")

def check_chrome_installation():
    """Check if Chrome is installed."""
    print("\nChecking for Chrome installation...")

    if sys.platform == 'win32':
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
    elif sys.platform == 'darwin':
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ]
    else:
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]

    found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✓ Found Chrome at: {path}")
            found = True
            break

    if not found:
        print("✗ Chrome not found!")
        print("\nPlease install Google Chrome:")
        print("https://www.google.com/chrome/")
    else:
        print("\n✓ Chrome is installed correctly!")

if __name__ == "__main__":
    print("=" * 60)
    print("ChromeDriver Troubleshooting Tool")
    print("=" * 60)

    check_chrome_installation()
    print("\n" + "=" * 60)
    clear_webdriver_cache()
    print("=" * 60)

    print("\nSteps completed!")
    print("\nIf you still have issues:")
    print("1. Make sure Chrome is fully closed")
    print("2. Restart your terminal/command prompt")
    print("3. Reactivate your virtual environment")
    print("4. Try running the app again")
