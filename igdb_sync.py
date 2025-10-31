import requests
import time
import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# IGDB API configuration
IGDB_CLIENT_ID = os.getenv("IGDB_CLIENT_ID", "")
IGDB_CLIENT_SECRET = os.getenv("IGDB_CLIENT_SECRET", "")
IGDB_BASE_URL = "https://api.igdb.com/v4"
TWITCH_AUTH_URL = "https://id.twitch.tv/oauth2/token"

class IGDBSyncer:
    def __init__(self, client_id: str = None, client_secret: str = None, callback=None):
        """
        Initialize the IGDB API syncer.

        Args:
            client_id: IGDB Client ID (from Twitch Developer Portal)
            client_secret: IGDB Client Secret (from Twitch Developer Portal)
            callback: Optional function to call with status updates
        """
        self.client_id = client_id or IGDB_CLIENT_ID
        self.client_secret = client_secret or IGDB_CLIENT_SECRET
        self.callback = callback
        self.access_token = None
        self.token_expires_at = 0
        self.session = requests.Session()

    def _log(self, message):
        """Send status updates via callback."""
        print(message)
        if self.callback:
            self.callback(message)

    def authenticate(self) -> bool:
        """
        Authenticate with IGDB using Twitch OAuth2.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self.client_id or not self.client_secret:
            self._log("ERROR: IGDB Client ID and Secret not configured in .env file")
            return False

        if self.access_token and time.time() < self.token_expires_at:
            return True  # Token still valid

        self._log("Authenticating with IGDB...")

        try:
            response = requests.post(
                TWITCH_AUTH_URL,
                params={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'client_credentials'
                },
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            self.access_token = data.get('access_token')
            expires_in = data.get('expires_in', 0)
            self.token_expires_at = time.time() + expires_in

            self._log(f"✓ Authenticated successfully (token expires in {expires_in} seconds)")
            return True

        except Exception as e:
            self._log(f"ERROR: Authentication failed: {str(e)}")
            return False

    def get_game_details(self, game_id: int) -> Optional[Dict]:
        """
        Get ALL detailed information about a game from IGDB with expanded fields.

        Args:
            game_id: IGDB game ID

        Returns:
            dict: Complete game information with all fields expanded, or None if error
        """
        if not self.authenticate():
            return None

        self._log(f"Fetching ALL details for IGDB game ID: {game_id}")

        try:
            url = f"{IGDB_BASE_URL}/games"
            headers = {
                'Client-ID': self.client_id,
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json'
            }

            # Get ALL fields with FULL expansion of all related entities
            # Use wildcard (*) for base fields and expand all arrays/references
            body = f"""
                fields *,
                age_ratings.*,
                age_ratings.content_descriptions.*,
                age_ratings.rating_cover_url,
                alternative_names.*,
                artworks.*,
                bundles.*,
                category,
                checksum,
                collection.*,
                collections.*,
                cover.*,
                created_at,
                dlcs.*,
                expanded_games.*,
                expansions.*,
                external_games.*,
                first_release_date,
                follows,
                forks.*,
                franchise.*,
                franchises.*,
                game_engines.*,
                game_localizations.*,
                game_modes.*,
                genres.*,
                hypes,
                involved_companies.*,
                involved_companies.company.*,
                keywords.*,
                language_supports.*,
                language_supports.language.*,
                language_supports.language_support_type.*,
                multiplayer_modes.*,
                name,
                parent_game.*,
                platforms.*,
                platforms.platform_logo.*,
                player_perspectives.*,
                ports.*,
                rating,
                rating_count,
                release_dates.*,
                release_dates.platform.*,
                remakes.*,
                remasters.*,
                screenshots.*,
                similar_games.*,
                slug,
                standalone_expansions.*,
                status,
                storyline,
                summary,
                tags,
                themes.*,
                total_rating,
                total_rating_count,
                updated_at,
                url,
                version_parent.*,
                version_title,
                videos.*,
                websites.*;
                where id = {game_id};
            """

            response = requests.post(url, headers=headers, data=body, timeout=15)
            response.raise_for_status()

            data = response.json()

            if data and len(data) > 0:
                self._log(f"✓ Successfully fetched ALL game details with expanded fields")
                return data[0]
            else:
                self._log(f"No game found with ID {game_id}")
                return None

        except Exception as e:
            self._log(f"ERROR: Failed to fetch game details: {str(e)}")
            return None

    def search_game(self, game_title: str) -> Optional[Dict]:
        """
        Search for a game on IGDB by title and return the best match (preferring main games).

        Args:
            game_title: The name of the game to search for

        Returns:
            dict: Game data with just ID and name, or None if not found
        """
        if not self.authenticate():
            return None

        self._log(f"Searching IGDB for: {game_title}")

        try:
            url = f"{IGDB_BASE_URL}/games"
            headers = {
                'Client-ID': self.client_id,
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json'
            }

            # Simple search - get top 5 results with just basic info
            # We'll filter for main games and fetch full details separately
            body = f'search "{game_title}"; fields id,name,category,version_parent; limit 5;'

            response = requests.post(url, headers=headers, data=body, timeout=10)
            response.raise_for_status()

            data = response.json()

            if not data or len(data) == 0:
                self._log(f"No results found for: {game_title}")
                return None

            # Prefer main games (category = 0) without version_parent
            main_games = [g for g in data if g.get('category') == 0 and not g.get('version_parent')]

            # If no main games, try bundles or standalone games
            if not main_games:
                main_games = [g for g in data if not g.get('version_parent')]

            # If still nothing, just take the first result
            if not main_games:
                main_games = data

            best_match = main_games[0]
            self._log(f"✓ Found game: {best_match.get('name', 'Unknown')} (ID: {best_match.get('id')})")
            return best_match

        except Exception as e:
            self._log(f"ERROR: Search failed: {str(e)}")
            return None


def sync_game_with_igdb(game_id: int, callback=None) -> Dict:
    """
    Sync a single game with IGDB API.

    Args:
        game_id: IGDB game ID
        callback: Optional callback function for status updates

    Returns:
        dict: Result with success status and game data
    """
    syncer = IGDBSyncer(callback=callback)

    game_details = syncer.get_game_details(game_id)

    if game_details:
        return {
            'success': True,
            'data': game_details,
            'message': f"Successfully fetched game details from IGDB"
        }
    else:
        return {
            'success': False,
            'error': 'Failed to fetch game details from IGDB',
            'message': 'Check credentials and game ID'
        }
