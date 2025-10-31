import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import os
import sys
from database import add_game

class EpicGamesScraper:
    def __init__(self, callback=None):
        """
        Initialize the Epic Games scraper.

        Args:
            callback: Optional function to call with status updates
        """
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

    def _random_mouse_movement(self):
        """Perform random mouse movements to appear more human."""
        try:
            actions = ActionChains(self.driver)
            # Move to random positions
            for _ in range(random.randint(1, 3)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                actions.move_by_offset(x, y)
            actions.perform()
        except:
            pass  # Ignore errors in mouse movement

    def setup_driver(self):
        """Set up undetected Chrome browser with maximum stealth."""
        self._log("Setting up undetected Chrome with maximum stealth...")

        try:
            # Create undetected Chrome options with stealth settings
            options = uc.ChromeOptions()

            # Stealth arguments
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            options.add_argument('--disable-site-isolation-trials')
            options.add_argument('--start-maximized')

            # User agent to appear more human
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Additional preferences to avoid detection
            prefs = {
                'credentials_enable_service': False,
                'profile.password_manager_enabled': False,
                'profile.default_content_setting_values.notifications': 2
            }
            options.add_experimental_option('prefs', prefs)
            options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
            options.add_experimental_option('useAutomationExtension', False)

            self._log("Starting Chrome with advanced anti-detection...")

            # Create driver with undetected-chromedriver
            self.driver = uc.Chrome(
                options=options,
                use_subprocess=True,
                version_main=None,
                driver_executable_path=None,
                browser_executable_path=None,
                suppress_welcome=True
            )

            # Execute stealth scripts
            self._log("Applying stealth scripts...")
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            self.driver.execute_script("window.chrome = { runtime: {} };")

            self.driver.maximize_window()
            self._log("✓ Undetected Chrome browser ready with maximum stealth!")
            self._log("✓ Advanced anti-detection enabled")

            # Add a small delay to let the browser settle
            time.sleep(2)

        except Exception as e:
            self._log(f"Error setting up undetected Chrome: {str(e)}")
            self._log("Trying fallback method...")

            try:
                self.driver = uc.Chrome(use_subprocess=True, suppress_welcome=True)
                self.driver.maximize_window()
                self._log("✓ Browser ready with fallback method!")
            except Exception as e2:
                raise Exception(
                    f"Could not initialize undetected Chrome browser. "
                    f"Error: {str(e2)}. "
                    f"Please ensure Google Chrome is installed."
                )

    def navigate_to_library(self):
        """Navigate to Epic Games purchases page."""
        self._log("Navigating to Epic Games purchases page...")

        # Go to Epic Games purchases page
        self.driver.get("https://www.epicgames.com/account/transactions/purchases")

        self._log("Please log in to your Epic Games account if prompted...")
        self._log("Waiting for purchases page to load...")

        # Wait for user to login and page to load
        self._human_delay(3, 5)  # Initial wait for page load

    def wait_for_login(self):
        """Wait for user to manually log in."""
        self._log("Waiting for login... (Please log in manually in the browser)")
        self._log("IMPORTANT: After logging in, wait on the purchases page for 10 seconds")
        self._log("This helps avoid CAPTCHA detection!")

        # Wait up to 180 seconds for the purchases page to load
        try:
            WebDriverWait(self.driver, 180).until(
                EC.url_contains("/transactions/purchases")
            )
            self._log("✓ Login successful! Purchases page detected.")
            self._log("Waiting 10 seconds to avoid detection...")

            # Longer wait after login + random mouse movements
            for i in range(10):
                time.sleep(1)
                if i % 3 == 0:
                    self._random_mouse_movement()

            self._log("✓ Ready to start parsing!")
        except:
            self._log("Timeout waiting for login. Proceeding anyway...")

    def navigate_pages(self):
        """Navigate through all pages of purchases with human-like behavior."""
        self._log("Checking for multiple pages...")

        all_games = []
        page_number = 1

        while True:
            self._log(f"Processing page {page_number}...")

            # Add random delay before extracting (simulate reading)
            self._human_delay(2, 4)

            # Extract games from current page
            games_on_page = self.extract_games_from_current_page()
            all_games.extend(games_on_page)
            self._log(f"Found {len(games_on_page)} games on page {page_number}")

            # Random mouse movement to appear human
            if random.random() > 0.5:
                self._random_mouse_movement()

            # Try to find and click the next button
            try:
                next_button = self.driver.find_element(By.ID, "next-btn")

                # Check if button is disabled
                button_classes = next_button.get_attribute("class")
                if "Mui-disabled" in button_classes or "disabled" in button_classes:
                    self._log("✓ Reached last page!")
                    break

                # Scroll to button before clicking (more human-like)
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
                self._human_delay(0.5, 1.5)

                # Click the next button
                self._log("Moving to next page...")
                next_button.click()

                # Wait for next page to load with random delay
                self._human_delay(3, 5)
                page_number += 1

            except Exception as e:
                self._log(f"No more pages found or error clicking next: {str(e)}")
                break

        self._log(f"✓ Finished! Processed {page_number} page(s)")
        return all_games

    def extract_games_from_current_page(self):
        """Extract game titles from the current page."""
        games = []

        try:
            # Find all game title elements with the specific class
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
            self._log(f"Error extracting games from page: {str(e)}")

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
        """Main scraping method."""
        try:
            self.setup_driver()
            self.navigate_to_library()
            self.wait_for_login()
            games = self.navigate_pages()

            if games:
                # Remove duplicates while preserving order
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
                    'message': 'No games found. Please check the Epic Games purchases page manually.'
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
                time.sleep(2)  # Let user see final state
                self.driver.quit()
                self._log("Browser closed.")

def scrape_epic_games(callback=None):
    """
    Convenience function to scrape Epic Games library.

    Args:
        callback: Optional function to call with status updates

    Returns:
        dict: Result of the scraping operation
    """
    scraper = EpicGamesScraper(callback=callback)
    return scraper.scrape()

# For testing
if __name__ == "__main__":
    result = scrape_epic_games()
    print(result)
