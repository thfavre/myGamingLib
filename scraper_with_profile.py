"""
Alternative scraper that uses your existing Chrome profile.
This bypasses CAPTCHA by using a browser where you're already logged in.
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
from pathlib import Path
from database import add_game

class EpicGamesProfileScraper:
    def __init__(self, callback=None):
        self.callback = callback
        self.driver = None

    def _log(self, message):
        """Send status updates via callback."""
        print(message)
        if self.callback:
            self.callback(message)

    def _human_delay(self, min_seconds=1, max_seconds=3):
        """Add a random delay to simulate human behavior."""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def get_chrome_profile_path(self):
        """Get the default Chrome user data directory."""
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

    def setup_driver_with_profile(self):
        """Set up Chrome using your existing profile (where you're already logged in)."""
        self._log("Setting up Chrome with your existing profile...")
        self._log("This will use your logged-in Epic Games session!")
        self._log("")
        self._log("⚠️ IMPORTANT: Close ALL Chrome windows NOW!")
        self._log("⚠️ Chrome cannot start if it's already running!")
        self._log("")

        try:
            # Get Chrome profile path
            profile_path = self.get_chrome_profile_path()

            if not profile_path:
                raise Exception("Could not find Chrome profile directory")

            self._log(f"✓ Found Chrome profile at: {profile_path}")
            self._log("")

            # Create options
            options = uc.ChromeOptions()

            # CRITICAL: Use your existing Chrome profile
            options.add_argument(f'--user-data-dir={profile_path}')
            options.add_argument('--profile-directory=Default')  # Use "Default" profile

            # Additional stealth options
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--no-first-run')
            options.add_argument('--no-service-autorun')
            options.add_argument('--password-store=basic')

            self._log("Starting Chrome with your profile...")
            self._log("This may take 10-30 seconds...")
            self._log("")

            # Create driver with timeout handling
            import threading
            driver_created = {'success': False, 'driver': None, 'error': None}

            def create_driver():
                try:
                    driver_created['driver'] = uc.Chrome(
                        options=options,
                        use_subprocess=False,
                        version_main=None
                    )
                    driver_created['success'] = True
                except Exception as e:
                    driver_created['error'] = str(e)

            thread = threading.Thread(target=create_driver)
            thread.daemon = True
            thread.start()

            # Wait up to 60 seconds for Chrome to start
            for i in range(60):
                if driver_created['success']:
                    self.driver = driver_created['driver']
                    break
                if driver_created['error']:
                    raise Exception(driver_created['error'])
                if i % 5 == 0 and i > 0:
                    self._log(f"Still waiting... ({i}s)")
                time.sleep(1)

            if not self.driver:
                raise Exception(
                    "Timeout starting Chrome. "
                    "Make sure ALL Chrome windows are closed! "
                    "Check Task Manager and force close chrome.exe if needed."
                )

            self.driver.maximize_window()
            self._log("")
            self._log("✓ Chrome started successfully!")
            self._log("✓ Using your existing profile!")
            self._log("✓ You should already be logged into Epic Games!")
            self._log("")

            time.sleep(2)

        except Exception as e:
            self._log("")
            self._log(f"❌ Error: {str(e)}")
            self._log("")
            self._log("Troubleshooting:")
            self._log("1. Close ALL Chrome windows (check Task Manager)")
            self._log("2. Make sure Chrome isn't running in the background")
            self._log("3. Try restarting your computer")
            self._log("")
            raise

    def navigate_to_library(self):
        """Navigate to Epic Games purchases page."""
        self._log("Navigating to Epic Games purchases page...")

        try:
            self.driver.get("https://www.epicgames.com/account/transactions/purchases")
            self._log("✓ Page load initiated")
            self._log("Waiting for page to fully load...")
            self._human_delay(3, 5)

            current_url = self.driver.current_url
            self._log(f"✓ Current URL: {current_url}")

        except Exception as e:
            self._log(f"❌ Error navigating: {str(e)}")
            raise

    def check_if_logged_in(self):
        """Check if already logged in."""
        self._log("Checking login status...")

        # Wait for page to load
        self._log("Waiting 3 seconds for page to settle...")
        time.sleep(3)

        # Check current URL
        current_url = self.driver.current_url
        self._log(f"Current URL: {current_url}")

        # Check if we're on the purchases page (meaning we're logged in)
        if "/transactions/purchases" in current_url:
            self._log("✓ Already logged in! No CAPTCHA needed!")
            self._log("✓ You're on the purchases page!")
            return True
        else:
            self._log("⚠ Not on purchases page yet...")
            self._log(f"⚠ Current page: {current_url}")
            self._log("Waiting for you to log in or for redirect...")

            try:
                WebDriverWait(self.driver, 120).until(
                    EC.url_contains("/transactions/purchases")
                )
                self._log("✓ Login successful!")
                return True
            except Exception as e:
                self._log(f"⚠ Login timeout: {str(e)}")
                return False

    def navigate_pages(self):
        """Navigate through all pages of purchases."""
        self._log("✓ Ready to parse games!")
        self._log("Looking for game entries on the page...")

        all_games = []
        page_number = 1

        while True:
            self._log("")
            self._log(f"📄 Processing page {page_number}...")
            self._log("Waiting a moment before extracting (human-like behavior)...")
            self._human_delay(2, 3)

            # Extract games from current page
            games_on_page = self.extract_games_from_current_page()
            all_games.extend(games_on_page)
            self._log(f"Found {len(games_on_page)} games on page {page_number}")

            # Try to find and click the next button
            try:
                next_button = self.driver.find_element(By.ID, "next-btn")

                # Check if button is disabled
                button_classes = next_button.get_attribute("class")
                if "Mui-disabled" in button_classes or "disabled" in button_classes:
                    self._log("✓ Reached last page!")
                    break

                # Scroll and click
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
                self._human_delay(1, 2)

                self._log("Moving to next page...")
                next_button.click()
                self._human_delay(3, 4)
                page_number += 1

            except Exception as e:
                self._log(f"No more pages: {str(e)}")
                break

        self._log(f"✓ Finished! Processed {page_number} page(s)")
        return all_games

    def extract_games_from_current_page(self):
        """Extract game titles from the current page."""
        games = []

        try:
            # Find all game title elements
            game_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                "span.am-hoct6b"
            )

            for element in game_elements:
                try:
                    title = element.text.strip()
                    if title and len(title) > 1:
                        games.append(title)
                except:
                    continue

        except Exception as e:
            self._log(f"Error extracting games: {str(e)}")

        return games

    def save_games_to_db(self, games):
        """Save extracted games to the database."""
        self._log("Saving games to database...")

        saved_count = 0
        for game_title in games:
            try:
                add_game(game_title)
                saved_count += 1
                self._log(f"Saved: {game_title}")
            except Exception as e:
                self._log(f"Error saving {game_title}: {str(e)}")

        self._log(f"Successfully saved {saved_count} games to database!")
        return saved_count

    def scrape(self):
        """Main scraping method using existing Chrome profile."""
        try:
            self._log("=" * 50)
            self._log("STEP 1: Setting up Chrome with your profile...")
            self._log("=" * 50)
            self.setup_driver_with_profile()

            self._log("")
            self._log("=" * 50)
            self._log("STEP 2: Navigating to purchases page...")
            self._log("=" * 50)
            self.navigate_to_library()

            self._log("")
            self._log("=" * 50)
            self._log("STEP 3: Checking if logged in...")
            self._log("=" * 50)
            if not self.check_if_logged_in():
                return {
                    'success': False,
                    'message': 'Login failed or timeout'
                }

            self._log("")
            self._log("=" * 50)
            self._log("STEP 4: Starting to parse games...")
            self._log("=" * 50)
            games = self.navigate_pages()

            if games:
                # Remove duplicates
                unique_games = []
                seen = set()
                for game in games:
                    if game not in seen:
                        unique_games.append(game)
                        seen.add(game)

                self._log(f"Found {len(unique_games)} unique games total")
                saved_count = self.save_games_to_db(unique_games)
                return {
                    'success': True,
                    'games_found': len(unique_games),
                    'games_saved': saved_count,
                    'message': f'Successfully scraped {saved_count} games!'
                }
            else:
                return {
                    'success': False,
                    'games_found': 0,
                    'games_saved': 0,
                    'message': 'No games found.'
                }

        except Exception as e:
            self._log(f"Error during scraping: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Scraping failed: {str(e)}'
            }

        finally:
            if self.driver:
                self._log("Closing browser...")
                time.sleep(2)
                self.driver.quit()
                self._log("Browser closed.")

def scrape_epic_games_with_profile(callback=None):
    """Scrape using existing Chrome profile (best method to avoid CAPTCHA)."""
    scraper = EpicGamesProfileScraper(callback=callback)
    return scraper.scrape()

if __name__ == "__main__":
    result = scrape_epic_games_with_profile()
    print(result)
