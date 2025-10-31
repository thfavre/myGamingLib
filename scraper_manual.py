"""
Manual scraper - YOU control when to start parsing.
1. Opens Chrome
2. You log in manually
3. You press Enter when ready
4. It starts parsing
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import random
from database import add_game

class ManualEpicGamesScraper:
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

    def setup_driver(self):
        """Set up a simple Chrome browser - no profile complications."""
        self._log("=" * 60)
        self._log("Opening Chrome browser...")
        self._log("=" * 60)
        self._log("")

        try:
            options = uc.ChromeOptions()

            # Basic stealth options
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--start-maximized')

            self._log("Starting Chrome (this may take 10-20 seconds)...")

            # Simple Chrome without profile
            self.driver = uc.Chrome(options=options, version_main=None)

            self._log("✓ Chrome opened successfully!")
            self._log("")
            return True

        except Exception as e:
            self._log(f"❌ Error opening Chrome: {str(e)}")
            self._log("")
            return False

    def wait_for_manual_login(self):
        """Open purchases page and wait for user to log in manually."""
        self._log("=" * 60)
        self._log("MANUAL LOGIN REQUIRED")
        self._log("=" * 60)
        self._log("")
        self._log("Opening Epic Games purchases page...")

        self.driver.get("https://www.epicgames.com/account/transactions/purchases")

        self._log("")
        self._log("✓ Page opened!")
        self._log("")
        self._log("=" * 60)
        self._log("PLEASE DO THE FOLLOWING:")
        self._log("=" * 60)
        self._log("1. Log into Epic Games in the Chrome window")
        self._log("2. Solve any CAPTCHA if it appears")
        self._log("3. Navigate to: https://www.epicgames.com/account/transactions/purchases")
        self._log("4. Make sure you can see your games list")
        self._log("5. When ready, come back here and press ENTER")
        self._log("=" * 60)
        self._log("")

        # Wait for user to press Enter (this will block the thread)
        # Since we're in a Flask thread, we can't use input()
        # Instead, we'll check the URL periodically
        self._log("Waiting for you to be on the purchases page...")
        self._log("(This checks automatically every 5 seconds)")
        self._log("")

        max_wait = 300  # 5 minutes max
        waited = 0

        while waited < max_wait:
            time.sleep(5)
            waited += 5

            current_url = self.driver.current_url

            if "/transactions/purchases" in current_url:
                self._log("✓ You're on the purchases page!")
                self._log("✓ Ready to start parsing!")
                self._log("")
                return True

            if waited % 30 == 0:  # Log every 30 seconds
                self._log(f"Still waiting... ({waited}s elapsed)")
                self._log(f"Current URL: {current_url}")
                self._log("Please navigate to the purchases page...")
                self._log("")

        self._log("❌ Timeout - took too long")
        return False

    def navigate_pages(self):
        """Navigate through all pages of purchases."""
        self._log("=" * 60)
        self._log("STARTING TO PARSE GAMES")
        self._log("=" * 60)
        self._log("")

        all_games = []
        page_number = 1

        while True:
            self._log(f"📄 Page {page_number}...")

            # Wait a bit for page to settle
            self._human_delay(2, 3)

            # Extract games from current page
            games_on_page = self.extract_games_from_current_page()
            all_games.extend(games_on_page)
            self._log(f"   Found {len(games_on_page)} games on this page")

            # Try to find and click the next button
            try:
                next_button = self.driver.find_element(By.ID, "next-btn")

                # Check if button is disabled
                button_classes = next_button.get_attribute("class")
                if "Mui-disabled" in button_classes or "disabled" in button_classes:
                    self._log("")
                    self._log("✓ Reached last page!")
                    break

                # Scroll and click
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
                self._human_delay(1, 2)

                self._log("   Moving to next page...")
                next_button.click()
                self._human_delay(3, 4)
                page_number += 1

            except Exception as e:
                self._log(f"   No more pages: {str(e)}")
                break

        self._log("")
        self._log(f"✓ Finished! Processed {page_number} page(s)")
        self._log("")
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
            self._log(f"   Error extracting games: {str(e)}")

        return games

    def save_games_to_db(self, games):
        """Save extracted games to the database."""
        self._log("=" * 60)
        self._log("SAVING TO DATABASE")
        self._log("=" * 60)
        self._log("")

        saved_count = 0
        for game_title in games:
            try:
                add_game(game_title)
                saved_count += 1
                self._log(f"✓ {game_title}")
            except Exception as e:
                self._log(f"✗ {game_title}: {str(e)}")

        self._log("")
        self._log(f"✓ Successfully saved {saved_count} games!")
        self._log("")
        return saved_count

    def scrape(self):
        """Main scraping method with manual login."""
        try:
            # Step 1: Open Chrome
            if not self.setup_driver():
                return {
                    'success': False,
                    'message': 'Failed to open Chrome'
                }

            # Step 2: Wait for manual login
            if not self.wait_for_manual_login():
                return {
                    'success': False,
                    'message': 'Login timeout or user did not navigate to purchases page'
                }

            # Step 3: Parse all pages
            games = self.navigate_pages()

            # Step 4: Save to database
            if games:
                # Remove duplicates
                unique_games = []
                seen = set()
                for game in games:
                    if game not in seen:
                        unique_games.append(game)
                        seen.add(game)

                saved_count = self.save_games_to_db(unique_games)

                self._log("=" * 60)
                self._log("SUCCESS!")
                self._log("=" * 60)
                self._log(f"Total games found: {len(unique_games)}")
                self._log(f"Games saved: {saved_count}")
                self._log("")

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
            self._log("")
            self._log("=" * 60)
            self._log("ERROR!")
            self._log("=" * 60)
            self._log(f"Error: {str(e)}")
            self._log("")

            return {
                'success': False,
                'error': str(e),
                'message': f'Scraping failed: {str(e)}'
            }

        finally:
            if self.driver:
                self._log("Closing browser in 5 seconds...")
                time.sleep(5)
                self.driver.quit()
                self._log("✓ Browser closed.")

def scrape_epic_games_manual(callback=None):
    """Scrape with manual login - user controls when to start."""
    scraper = ManualEpicGamesScraper(callback=callback)
    return scraper.scrape()

if __name__ == "__main__":
    result = scrape_epic_games_manual()
    print(result)
