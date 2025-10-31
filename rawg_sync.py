import requests
import time
import os
from typing import Dict, Optional, List
from dotenv import load_dotenv
from database import get_games_without_rawg_sync, update_game_metadata, get_all_games

# Load environment variables
load_dotenv()

# RAWG API configuration
# Get your free API key at: https://rawg.io/apidocs
RAWG_API_KEY = os.getenv("RAWG_API_KEY", "")
RAWG_BASE_URL = "https://api.rawg.io/api"
REQUEST_DELAY = 1.0  # Delay between requests to respect rate limits

class RAWGSyncer:
    def __init__(self, api_key: str = None, callback=None):
        """
        Initialize the RAWG API syncer.

        Args:
            api_key: RAWG API key (get from https://rawg.io/apidocs)
            callback: Optional function to call with status updates
        """
        self.api_key = api_key or RAWG_API_KEY
        self.callback = callback
        self.session = requests.Session()

    def _log(self, message):
        """Send status updates via callback."""
        print(message)
        if self.callback:
            self.callback(message)

    def search_game(self, game_title: str) -> Optional[Dict]:
        """
        Search for a game on RAWG by title.

        Args:
            game_title: The name of the game to search for

        Returns:
            dict: Game data if found, None otherwise
        """
        self._log(f"Searching RAWG for: {game_title}")

        try:
            url = f"{RAWG_BASE_URL}/games"
            params = {
                'key': self.api_key,
                'search': game_title,
                'page_size': 1
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data['results']:
                return data['results'][0]
            else:
                self._log(f"No results found for: {game_title}")
                return None

        except Exception as e:
            self._log(f"Error searching for {game_title}: {str(e)}")
            return None

    def get_game_details(self, game_id: int) -> Optional[Dict]:
        """
        Get detailed information about a game from RAWG.

        Args:
            game_id: RAWG game ID

        Returns:
            dict: Detailed game information
        """
        try:
            url = f"{RAWG_BASE_URL}/games/{game_id}"
            params = {'key': self.api_key}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            self._log(f"Error getting details for game ID {game_id}: {str(e)}")
            return None

    def extract_metadata(self, game_data: Dict) -> Dict:
        """
        Extract and format relevant metadata from RAWG game data.

        Args:
            game_data: Raw game data from RAWG API

        Returns:
            dict: Formatted metadata for database storage
        """
        metadata = {
            'rawg_id': game_data.get('id'),
            'rawg_slug': game_data.get('slug'),
            'description': game_data.get('description_raw', ''),
            'release_date': game_data.get('released'),
            'rating': game_data.get('rating'),
            'metacritic_score': game_data.get('metacritic'),
            'background_image': game_data.get('background_image'),
            'cover_image': game_data.get('background_image'),  # RAWG doesn't have separate cover
        }

        # Extract genres
        genres = []
        for genre in game_data.get('genres', []):
            genres.append(genre['name'])
        metadata['genres'] = genres

        # Extract platforms
        platforms = []
        for platform_info in game_data.get('platforms', []):
            platforms.append(platform_info['platform']['name'])
        metadata['platforms'] = platforms

        # Extract tags
        tags = []
        for tag in game_data.get('tags', [])[:10]:  # Limit to top 10 tags
            tags.append(tag['name'])
        metadata['tags'] = tags

        # Extract ESRB rating
        esrb = game_data.get('esrb_rating')
        if esrb:
            metadata['esrb_rating'] = esrb['name']

        # Extract screenshots
        screenshots = []
        for screenshot in game_data.get('short_screenshots', []):
            screenshots.append(screenshot['image'])
        metadata['screenshots'] = screenshots

        # Extract player counts (CRITICAL REQUIREMENT)
        # RAWG provides this in the tags or description
        metadata['local_players_min'] = None
        metadata['local_players_max'] = None
        metadata['online_players_min'] = None
        metadata['online_players_max'] = None

        # Check tags for multiplayer information
        for tag in game_data.get('tags', []):
            tag_name = tag['name'].lower()

            # Local multiplayer detection
            if 'local multiplayer' in tag_name or 'local co-op' in tag_name:
                metadata['local_players_min'] = 1
                metadata['local_players_max'] = 4  # Common default

            if 'split screen' in tag_name or 'couch co-op' in tag_name:
                metadata['local_players_min'] = 1
                metadata['local_players_max'] = 4

            # Online multiplayer detection
            if 'multiplayer' in tag_name or 'online co-op' in tag_name:
                metadata['online_players_min'] = 1
                metadata['online_players_max'] = 100  # Generic online multiplayer

            if 'mmo' in tag_name or 'massively multiplayer' in tag_name:
                metadata['online_players_min'] = 1
                metadata['online_players_max'] = 1000  # MMO games

            # Specific player counts from tags
            if 'pvp' in tag_name:
                if not metadata['online_players_max']:
                    metadata['online_players_min'] = 2
                    metadata['online_players_max'] = 100

            # Single player
            if tag_name == 'singleplayer' or tag_name == 'single-player':
                if metadata['local_players_min'] is None:
                    metadata['local_players_min'] = 1
                    metadata['local_players_max'] = 1

        return metadata

    def sync_game(self, game_db_id: int, game_title: str) -> bool:
        """
        Sync a single game with RAWG metadata.

        Args:
            game_db_id: Database ID of the game
            game_title: Title of the game to search

        Returns:
            bool: True if sync was successful
        """
        # Search for the game
        search_result = self.search_game(game_title)

        if not search_result:
            self._log(f"Could not find {game_title} on RAWG")
            return False

        # Get detailed information
        game_id = search_result['id']
        game_details = self.get_game_details(game_id)

        if not game_details:
            self._log(f"Could not fetch details for {game_title}")
            return False

        # Extract and format metadata
        metadata = self.extract_metadata(game_details)

        # Update database
        update_game_metadata(game_db_id, metadata)
        self._log(f"Successfully synced: {game_title}")

        return True

    def sync_all_games(self, force_resync: bool = False):
        """
        Sync all games that haven't been synced with RAWG yet.

        Args:
            force_resync: If True, re-sync all games regardless of sync status

        Returns:
            dict: Summary of the sync operation
        """
        if not self.api_key or self.api_key == "":
            self._log("ERROR: Please set your RAWG API key in the .env file!")
            self._log("Get a free API key at: https://rawg.io/apidocs")
            return {
                'success': False,
                'error': 'API key not configured',
                'message': 'Please set your RAWG API key in the .env file'
            }

        # Get games to sync
        if force_resync:
            games = get_all_games()
            self._log(f"Force re-syncing all {len(games)} games...")
        else:
            games = get_games_without_rawg_sync()
            self._log(f"Found {len(games)} games to sync with RAWG...")

        if not games:
            self._log("No games to sync!")
            return {
                'success': True,
                'synced': 0,
                'failed': 0,
                'message': 'No games to sync'
            }

        synced = 0
        failed = 0

        for i, game in enumerate(games, 1):
            self._log(f"Processing {i}/{len(games)}: {game['title']}")

            if self.sync_game(game['id'], game['title']):
                synced += 1
            else:
                failed += 1

            # Rate limiting delay
            if i < len(games):
                time.sleep(REQUEST_DELAY)

        message = f"Sync complete! Synced: {synced}, Failed: {failed}"
        self._log(message)

        return {
            'success': True,
            'synced': synced,
            'failed': failed,
            'total': len(games),
            'message': message
        }

def sync_with_rawg(api_key: str = None, callback=None, force_resync: bool = False):
    """
    Convenience function to sync games with RAWG.

    Args:
        api_key: Optional RAWG API key
        callback: Optional function to call with status updates
        force_resync: If True, re-sync all games

    Returns:
        dict: Result of the sync operation
    """
    syncer = RAWGSyncer(api_key=api_key, callback=callback)
    return syncer.sync_all_games(force_resync=force_resync)

# For testing
if __name__ == "__main__":
    result = sync_with_rawg()
    print(result)
