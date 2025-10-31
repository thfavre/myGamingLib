"""
Simplest scraper ever:
1. Opens Chrome
2. You do EVERYTHING manually
3. You signal when ready
4. It starts parsing
"""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import random
from database import add_game

class SimpleEpicGamesScraper:
    def __init__(self):
        self.driver = None
        self.callback = None

    def set_callback(self, callback):
        """Set the callback for logging."""
        self.callback = callback

    def _log(self, message):
        """Send status updates."""
        print(message)
        if self.callback:
            self.callback(message)

    def open_chrome(self):
        """Just open Chrome - nothing else."""
        self._log("Opening Chrome...")
        self._log("")

        try:
            options = uc.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')

            self._log("Starting Chrome (10-20 seconds)...")
            self.driver = uc.Chrome(options=options, version_main=None)

            # Go to Epic Games homepage
            self.driver.get("https://www.epicgames.com")

            self._log("✓ Chrome opened!")
            self._log("")
            self._log("=" * 60)
            self._log("NOW YOU DO:")
            self._log("=" * 60)
            self._log("1. Log into Epic Games (if not already logged in)")
            self._log("2. Click the green 'Continue' button when ready")
            self._log("=" * 60)
            self._log("")
            self._log("The scraper will automatically navigate to your purchases page")
            self._log("and start parsing all your games.")
            self._log("")

            return {'success': True, 'message': 'Chrome opened'}

        except Exception as e:
            self._log(f"❌ Error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def start_parsing(self):
        """Start parsing from wherever the browser currently is."""
        if not self.driver:
            return {'success': False, 'message': 'Chrome not open. Click "Open Chrome" first.'}

        try:
            self._log("=" * 60)
            self._log("STARTING TO PARSE")
            self._log("=" * 60)
            self._log("")

            # Navigate to purchases page
            self._log("Navigating to purchases page...")
            self.driver.get("https://www.epicgames.com/account/transactions/purchases")

            # Wait for page to load
            time.sleep(5)

            current_url = self.driver.current_url
            self._log(f"Current URL: {current_url}")
            self._log("✓ You're on the purchases page!")
            self._log("")

            # Parse all pages
            all_games = []
            page_number = 1

            while True:
                self._log(f"📄 Page {page_number}...")

                # Wait a moment
                time.sleep(random.uniform(2, 3))

                # Extract games
                games_on_page = self._extract_games()
                all_games.extend(games_on_page)
                self._log(f"   Found {len(games_on_page)} games")

                # Try to click next
                try:
                    next_button = self.driver.find_element(By.ID, "next-btn")

                    # Check if disabled
                    button_classes = next_button.get_attribute("class")
                    if "Mui-disabled" in button_classes:
                        self._log("")
                        self._log("✓ Last page reached!")
                        break

                    # Click next
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
                    time.sleep(random.uniform(1, 2))
                    next_button.click()
                    time.sleep(random.uniform(3, 4))
                    page_number += 1

                except:
                    self._log("")
                    self._log("✓ No more pages")
                    break

            # Remove duplicates
            unique_games = list(dict.fromkeys(all_games))

            self._log("")
            self._log(f"✓ Total unique games: {len(unique_games)}")
            self._log("")

            # Save to database
            self._log("Saving to database...")
            new_games_count = 0
            existing_games_count = 0

            for game_title in unique_games:
                try:
                    game_id, was_new = add_game(game_title)

                    if was_new:
                        new_games_count += 1
                        self._log(f"✓ [NEW] {game_title}")
                    else:
                        existing_games_count += 1
                        self._log(f"✓ [EXISTS] {game_title}")

                except Exception as e:
                    self._log(f"✗ {game_title}: {str(e)}")

            total_saved = new_games_count + existing_games_count

            self._log("")
            self._log("=" * 60)
            self._log("SUCCESS!")
            self._log("=" * 60)
            self._log(f"Total games found: {len(unique_games)}")
            self._log(f"NEW games added: {new_games_count}")
            self._log(f"Already in database: {existing_games_count}")
            self._log(f"Total saved: {total_saved}")
            self._log("")

            return {
                'success': True,
                'games_found': len(unique_games),
                'games_saved': total_saved,
                'new_games': new_games_count,
                'existing_games': existing_games_count,
                'message': f'Successfully scraped {len(unique_games)} games! ({new_games_count} new, {existing_games_count} existing)'
            }

        except Exception as e:
            self._log("")
            self._log(f"❌ Error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _extract_games(self):
        """Extract game titles from current page."""
        games = []
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "span.am-hoct6b")
            for element in elements:
                try:
                    title = element.text.strip()
                    if title and len(title) > 1:
                        games.append(title)
                except:
                    continue
        except:
            pass
        return games

    def close_chrome(self):
        """Close the Chrome browser."""
        if self.driver:
            self._log("Closing Chrome...")
            self.driver.quit()
            self.driver = None
            self._log("✓ Chrome closed")
            return {'success': True, 'message': 'Chrome closed'}
        return {'success': False, 'message': 'Chrome not open'}

# Global scraper instance
_scraper = SimpleEpicGamesScraper()

def open_chrome_browser(callback=None):
    """Open Chrome - Step 1."""
    _scraper.set_callback(callback)
    return _scraper.open_chrome()

def start_parsing_now(callback=None):
    """Start parsing - Step 2."""
    _scraper.set_callback(callback)
    return _scraper.start_parsing()

def close_chrome_browser(callback=None):
    """Close Chrome."""
    _scraper.set_callback(callback)
    return _scraper.close_chrome()
