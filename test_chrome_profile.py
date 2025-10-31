"""
Quick test script to check if Chrome profile method works.
Run this to diagnose issues before using the full scraper.
"""
import undetected_chromedriver as uc
import os
import time

def get_chrome_profile_path():
    """Get the Chrome profile path."""
    if os.name == 'nt':  # Windows
        base_path = os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data')
    elif os.name == 'posix':  # Mac/Linux
        if 'darwin' in os.sys.platform:  # Mac
            base_path = os.path.expanduser('~/Library/Application Support/Google/Chrome')
        else:  # Linux
            base_path = os.path.expanduser('~/.config/google-chrome')
    else:
        return None

    return base_path if os.path.exists(base_path) else None

print("=" * 60)
print("Chrome Profile Test Script")
print("=" * 60)
print()

# Step 1: Check if Chrome profile exists
print("Step 1: Checking for Chrome profile...")
profile_path = get_chrome_profile_path()

if not profile_path:
    print("❌ ERROR: Could not find Chrome profile!")
    print("Chrome may not be installed or profile is in a non-standard location.")
    input("Press Enter to exit...")
    exit(1)

print(f"✓ Found Chrome profile at: {profile_path}")
print()

# Step 2: Check if Chrome is running
print("Step 2: Checking if Chrome is running...")
print("⚠️  IMPORTANT: Close ALL Chrome windows now!")
print("⚠️  Chrome MUST be closed for this to work!")
print()
input("Press Enter when Chrome is closed...")
print()

# Step 3: Try to start Chrome with profile
print("Step 3: Attempting to start Chrome with your profile...")
print("This may take 10-30 seconds...")
print()

try:
    options = uc.ChromeOptions()
    options.add_argument(f'--user-data-dir={profile_path}')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--disable-blink-features=AutomationControlled')

    print("Starting Chrome...")
    driver = uc.Chrome(options=options, use_subprocess=False, version_main=None)

    print("✓ Chrome started successfully!")
    print()

    # Step 4: Try to navigate to Epic Games
    print("Step 4: Navigating to Epic Games...")
    driver.get("https://www.epicgames.com/account/transactions/purchases")
    time.sleep(5)

    print("✓ Navigation successful!")
    print()
    print("Check the Chrome window:")
    print("- Are you already logged into Epic Games?")
    print("- Do you see the purchases page?")
    print("- Is there any CAPTCHA?")
    print()

    input("Press Enter to close Chrome...")
    driver.quit()

    print()
    print("=" * 60)
    print("✓ SUCCESS! The Chrome profile method works!")
    print("=" * 60)
    print()
    print("You can now use the scraper with confidence.")

except Exception as e:
    print()
    print("=" * 60)
    print("❌ ERROR!")
    print("=" * 60)
    print()
    print(f"Error: {str(e)}")
    print()
    print("Common causes:")
    print("1. Chrome is still running (check Task Manager)")
    print("2. Chrome profile is locked by another process")
    print("3. Permissions issue with the Chrome profile folder")
    print()
    print("Solutions:")
    print("1. Open Task Manager (Ctrl+Shift+Esc)")
    print("2. Find all 'chrome.exe' processes")
    print("3. End all Chrome processes")
    print("4. Wait 10 seconds")
    print("5. Run this script again")
    print()
    input("Press Enter to exit...")
