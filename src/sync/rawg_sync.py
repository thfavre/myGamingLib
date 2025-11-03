"""
RAWG API Sync Module
Fetches comprehensive game metadata from RAWG API and stores with rawg__ prefix
"""

import requests
import time
import os
from typing import Dict, Optional, List
from dotenv import load_dotenv
from src.database import get_games_without_rawg_sync, update_game_with_rawg_data, get_all_games

# Load environment variables
load_dotenv()

# RAWG API configuration
RAWG_API_KEY = os.getenv("RAWG_API_KEY", "")
RAWG_BASE_URL = "https://api.rawg.io/api"
REQUEST_DELAY = 1.0  # Delay between requests to respect rate limits


class RAWGSyncer:
    def __init__(self, api_key: str = None, callback=None):
        """Initialize the RAWG API syncer."""
        self.api_key = api_key or RAWG_API_KEY
        self.callback = callback
        self.session = requests.Session()

    def _log(self, message):
        """Send status updates via callback."""
        print(message)
        if self.callback:
            self.callback(message)

    def search_game(self, game_title: str) -> Optional[Dict]:
        """Search for a game on RAWG by title."""
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
        """Get detailed information about a game from RAWG."""
        try:
            url = f"{RAWG_BASE_URL}/games/{game_id}"
            params = {'key': self.api_key}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            self._log(f"Error getting details for game ID {game_id}: {str(e)}")
            return None

    def get_game_screenshots(self, game_id: int) -> List[Dict]:
        """Get screenshots for a game from RAWG."""
        try:
            url = f"{RAWG_BASE_URL}/games/{game_id}/screenshots"
            params = {'key': self.api_key}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data.get('results', [])

        except Exception as e:
            self._log(f"Error getting screenshots: {str(e)}")
            return []

    def get_game_achievements(self, game_id: int) -> List[Dict]:
        """Get achievements for a game from RAWG."""
        try:
            url = f"{RAWG_BASE_URL}/games/{game_id}/achievements"
            params = {'key': self.api_key}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data.get('results', [])

        except Exception as e:
            self._log(f"Error getting achievements: {str(e)}")
            return []

    def get_game_trailers(self, game_id: int) -> List[Dict]:
        """Get trailers for a game from RAWG."""
        try:
            url = f"{RAWG_BASE_URL}/games/{game_id}/movies"
            params = {'key': self.api_key}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data.get('results', [])

        except Exception as e:
            self._log(f"Error getting trailers: {str(e)}")
            return []

    def get_game_stores(self, game_id: int) -> List[Dict]:
        """Get store links for a game from RAWG."""
        try:
            url = f"{RAWG_BASE_URL}/games/{game_id}/stores"
            params = {'key': self.api_key}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data.get('results', [])

        except Exception as e:
            self._log(f"Error getting stores: {str(e)}")
            return []

    def extract_all_metadata(self, game_details: Dict, screenshots: List, achievements: List,
                            trailers: List, stores: List) -> Dict:
        """
        Extract ALL available metadata from RAWG API responses.
        Returns dictionary with rawg__ prefixed keys.
        """
        metadata = {}

        # Basic Info
        metadata['rawg__id'] = game_details.get('id')
        metadata['rawg__slug'] = game_details.get('slug')
        metadata['rawg__name'] = game_details.get('name')
        metadata['rawg__name_original'] = game_details.get('name_original')
        metadata['rawg__description'] = game_details.get('description')
        metadata['rawg__description_raw'] = game_details.get('description_raw')

        # Dates
        metadata['rawg__released'] = game_details.get('released')
        metadata['rawg__tba'] = game_details.get('tba')
        metadata['rawg__updated'] = game_details.get('updated')

        # Ratings & Reviews
        metadata['rawg__rating'] = game_details.get('rating')
        metadata['rawg__rating_top'] = game_details.get('rating_top')
        metadata['rawg__ratings'] = game_details.get('ratings')  # Full ratings breakdown
        metadata['rawg__ratings_count'] = game_details.get('ratings_count')
        metadata['rawg__reviews_count'] = game_details.get('reviews_count')
        metadata['rawg__reviews_text_count'] = game_details.get('reviews_text_count')
        metadata['rawg__metacritic'] = game_details.get('metacritic')
        metadata['rawg__metacritic_url'] = game_details.get('metacritic_url')
        metadata['rawg__metacritic_platforms'] = game_details.get('metacritic_platforms')

        # Extract player counts from tags
        # RAWG stores multiplayer info in tags
        tags = game_details.get('tags', [])
        local_min, local_max, online_min, online_max = self._extract_player_counts(tags)
        metadata['rawg__local_players_min'] = local_min
        metadata['rawg__local_players_max'] = local_max
        metadata['rawg__online_players_min'] = online_min
        metadata['rawg__online_players_max'] = online_max

        # Statistics
        metadata['rawg__playtime'] = game_details.get('playtime')
        metadata['rawg__added'] = game_details.get('added')
        metadata['rawg__added_by_status'] = game_details.get('added_by_status')
        metadata['rawg__suggestions_count'] = game_details.get('suggestions_count')

        # Content Counts
        metadata['rawg__achievements_count'] = game_details.get('achievements_count')
        metadata['rawg__screenshots_count'] = game_details.get('screenshots_count')
        metadata['rawg__movies_count'] = game_details.get('movies_count')
        metadata['rawg__creators_count'] = game_details.get('creators_count')
        metadata['rawg__additions_count'] = game_details.get('additions_count')
        metadata['rawg__game_series_count'] = game_details.get('game_series_count')
        metadata['rawg__parents_count'] = game_details.get('parents_count')

        # Media & Images
        metadata['rawg__background_image'] = game_details.get('background_image')
        metadata['rawg__background_image_additional'] = game_details.get('background_image_additional')
        metadata['rawg__screenshots'] = screenshots  # Full screenshot data
        metadata['rawg__trailers'] = trailers  # Full trailer data

        # Classifications
        metadata['rawg__genres'] = [{'id': g.get('id'), 'name': g.get('name'), 'slug': g.get('slug')}
                                    for g in game_details.get('genres', [])]
        metadata['rawg__tags'] = [{'id': t.get('id'), 'name': t.get('name'), 'slug': t.get('slug')}
                                  for t in game_details.get('tags', [])]
        metadata['rawg__platforms'] = [{'platform': p.get('platform', {}).get('name')}
                                       for p in game_details.get('platforms', [])]
        metadata['rawg__parent_platforms'] = [{'platform': p.get('platform', {}).get('name')}
                                              for p in game_details.get('parent_platforms', [])]
        metadata['rawg__esrb_rating'] = game_details.get('esrb_rating')

        # Achievements
        metadata['rawg__achievements'] = achievements

        # Store Links
        metadata['rawg__stores'] = [
            {
                'store_id': s.get('store', {}).get('id'),
                'store_name': s.get('store', {}).get('name'),
                'url': s.get('url')
            }
            for s in stores
        ]
        metadata['rawg__website'] = game_details.get('website')

        # Development
        metadata['rawg__developers'] = [{'id': d.get('id'), 'name': d.get('name'), 'slug': d.get('slug')}
                                       for d in game_details.get('developers', [])]
        metadata['rawg__publishers'] = [{'id': p.get('id'), 'name': p.get('name'), 'slug': p.get('slug')}
                                        for p in game_details.get('publishers', [])]
        metadata['rawg__creators'] = game_details.get('creators')

        # Community
        metadata['rawg__reddit_url'] = game_details.get('reddit_url')
        metadata['rawg__reddit_name'] = game_details.get('reddit_name')
        metadata['rawg__reddit_description'] = game_details.get('reddit_description')
        metadata['rawg__reddit_logo'] = game_details.get('reddit_logo')
        metadata['rawg__reddit_count'] = game_details.get('reddit_count')
        metadata['rawg__twitch_count'] = game_details.get('twitch_count')
        metadata['rawg__youtube_count'] = game_details.get('youtube_count')

        # Additional Data
        metadata['rawg__alternative_names'] = game_details.get('alternative_names', [])
        metadata['rawg__reactions'] = game_details.get('reactions')

        return metadata

    def _extract_player_counts(self, tags: List[Dict]) -> tuple:
        """
        Extract player count information from RAWG tags.

        Returns:
            tuple: (local_min, local_max, online_min, online_max)
        """
        local_min, local_max = None, None
        online_min, online_max = None, None

        tag_names = [tag.get('name', '').lower() for tag in tags]

        # Check for multiplayer tags
        if 'singleplayer' in tag_names or 'single-player' in tag_names:
            local_min, local_max = 1, 1

        if 'local co-op' in tag_names or 'local multiplayer' in tag_names or 'split screen' in tag_names or 'co-op' in tag_names:
            if local_min is None:
                local_min = 1
            local_max = 4  # Default assumption

        if 'multiplayer' in tag_names or 'online co-op' in tag_names or 'mmo' in tag_names or 'massively multiplayer' in tag_names:
            online_min = 1
            if 'mmo' in tag_names or 'massively multiplayer' in tag_names:
                online_max = 1000  # MMO
            else:
                online_max = 64  # Standard multiplayer

        return local_min, local_max, online_min, online_max

    def sync_game(self, game_id: int, game_title: str) -> bool:
        """
        Sync a single game with RAWG API - fetches ALL available data.

        Args:
            game_id: Database game ID
            game_title: Game title to search for

        Returns:
            bool: True if successful
        """
        self._log(f"\n--- Syncing: {game_title} ---")

        # Step 1: Search for the game
        search_result = self.search_game(game_title)
        if not search_result:
            self._log(f"[SKIP] Could not find '{game_title}' on RAWG")
            return False

        rawg_id = search_result.get('id')
        self._log(f"[FOUND] RAWG ID: {rawg_id}")

        # Step 2: Get game details
        self._log("[API] Fetching game details...")
        game_details = self.get_game_details(rawg_id)
        if not game_details:
            return False

        time.sleep(REQUEST_DELAY)

        # Step 3: Get screenshots
        self._log("[API] Fetching screenshots...")
        screenshots = self.get_game_screenshots(rawg_id)
        self._log(f"  → {len(screenshots)} screenshots found")
        time.sleep(REQUEST_DELAY)

        # Step 4: Get achievements
        self._log("[API] Fetching achievements...")
        achievements = self.get_game_achievements(rawg_id)
        self._log(f"  → {len(achievements)} achievements found")
        time.sleep(REQUEST_DELAY)

        # Step 5: Get trailers
        self._log("[API] Fetching trailers...")
        trailers = self.get_game_trailers(rawg_id)
        self._log(f"  → {len(trailers)} trailers found")
        time.sleep(REQUEST_DELAY)

        # Step 6: Get store links
        self._log("[API] Fetching store links...")
        stores = self.get_game_stores(rawg_id)
        self._log(f"  → {len(stores)} stores found")

        # Step 7: Extract all metadata
        self._log("[PROCESS] Extracting metadata...")
        metadata = self.extract_all_metadata(game_details, screenshots, achievements, trailers, stores)

        # Step 8: Update database
        self._log("[DB] Saving to database...")
        success = update_game_with_rawg_data(game_id, metadata)

        if success:
            self._log(f"[SUCCESS] '{game_title}' synced successfully!\n")
        else:
            self._log(f"[ERROR] Failed to save '{game_title}' to database\n")

        return success


def sync_with_rawg(callback=None, force_resync=False) -> Dict:
    """
    Sync all unsynced games with RAWG API.

    Args:
        callback: Optional callback function for status updates
        force_resync: If True, re-sync all games

    Returns:
        dict: Summary of sync operation
    """
    syncer = RAWGSyncer(callback=callback)

    if not syncer.api_key:
        return {
            'success': False,
            'error': 'RAWG API key not configured. Add it to your .env file.'
        }

    # Get games that need syncing
    if force_resync:
        games = get_all_games()
        syncer._log(f"Force re-syncing ALL {len(games)} games...")
    else:
        games = get_games_without_rawg_sync()
        syncer._log(f"Found {len(games)} games to sync with RAWG")

    if not games:
        syncer._log("No games to sync!")
        return {
            'success': True,
            'synced_count': 0,
            'failed_count': 0,
            'message': 'No games to sync'
        }

    synced = 0
    failed = 0

    for game in games:
        try:
            success = syncer.sync_game(game['id'], game['title'])
            if success:
                synced += 1
            else:
                failed += 1

            # Rate limiting
            time.sleep(REQUEST_DELAY)

        except Exception as e:
            syncer._log(f"[ERROR] Exception syncing '{game['title']}': {str(e)}")
            failed += 1

    syncer._log("\n" + "="*60)
    syncer._log(f"SYNC COMPLETE: {synced} synced, {failed} failed")
    syncer._log("="*60)

    return {
        'success': True,
        'synced_count': synced,
        'failed_count': failed,
        'total_games': len(games)
    }
