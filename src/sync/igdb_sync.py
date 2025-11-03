import requests
import time
import os
from typing import Dict, Optional, List, Callable
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

    def extract_all_metadata(self, game_data: Dict) -> Dict:
        """
        Extract ALL available metadata from IGDB game data and format it for database.

        Args:
            game_data: Complete game data from IGDB API

        Returns:
            dict: Dictionary with igdb__ prefixed fields ready for database
        """
        metadata = {}

        # Basic Info
        metadata['igdb__id'] = game_data.get('id')
        metadata['igdb__name'] = game_data.get('name')
        metadata['igdb__slug'] = game_data.get('slug')
        metadata['igdb__summary'] = game_data.get('summary')
        metadata['igdb__storyline'] = game_data.get('storyline')
        metadata['igdb__url'] = game_data.get('url')

        # Dates (IGDB uses Unix timestamps)
        metadata['igdb__first_release_date'] = game_data.get('first_release_date')
        metadata['igdb__created_at'] = game_data.get('created_at')
        metadata['igdb__updated_at'] = game_data.get('updated_at')

        # Ratings
        metadata['igdb__rating'] = game_data.get('rating')
        metadata['igdb__rating_count'] = game_data.get('rating_count')
        metadata['igdb__total_rating'] = game_data.get('total_rating')
        metadata['igdb__total_rating_count'] = game_data.get('total_rating_count')
        metadata['igdb__aggregated_rating'] = game_data.get('aggregated_rating')
        metadata['igdb__aggregated_rating_count'] = game_data.get('aggregated_rating_count')
        metadata['igdb__hypes'] = game_data.get('hypes')
        metadata['igdb__follows'] = game_data.get('follows')

        # Classification
        metadata['igdb__category'] = game_data.get('category')
        metadata['igdb__status'] = game_data.get('status')
        metadata['igdb__version_title'] = game_data.get('version_title')

        # Cover Image (convert IGDB image URL to full URL)
        if game_data.get('cover'):
            cover = game_data['cover']
            if isinstance(cover, dict) and cover.get('image_id'):
                # IGDB image URL format: https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.jpg
                metadata['igdb__cover'] = f"https://images.igdb.com/igdb/image/upload/t_cover_big/{cover['image_id']}.jpg"
            elif isinstance(cover, dict):
                metadata['igdb__cover'] = cover

        # Artworks
        if game_data.get('artworks'):
            artworks = []
            for artwork in game_data['artworks']:
                if isinstance(artwork, dict) and artwork.get('image_id'):
                    artworks.append({
                        'url': f"https://images.igdb.com/igdb/image/upload/t_screenshot_big/{artwork['image_id']}.jpg",
                        'id': artwork.get('id')
                    })
            metadata['igdb__artworks'] = artworks

        # Screenshots
        if game_data.get('screenshots'):
            screenshots = []
            for screenshot in game_data['screenshots']:
                if isinstance(screenshot, dict) and screenshot.get('image_id'):
                    screenshots.append({
                        'url': f"https://images.igdb.com/igdb/image/upload/t_screenshot_big/{screenshot['image_id']}.jpg",
                        'id': screenshot.get('id')
                    })
            metadata['igdb__screenshots'] = screenshots

        # Videos
        if game_data.get('videos'):
            videos = []
            for video in game_data['videos']:
                if isinstance(video, dict):
                    videos.append({
                        'name': video.get('name'),
                        'video_id': video.get('video_id'),
                        'url': f"https://www.youtube.com/watch?v={video.get('video_id')}" if video.get('video_id') else None
                    })
            metadata['igdb__videos'] = videos

        # Genres
        if game_data.get('genres'):
            metadata['igdb__genres'] = [g.get('name') if isinstance(g, dict) else g for g in game_data['genres']]

        # Themes
        if game_data.get('themes'):
            metadata['igdb__themes'] = [t.get('name') if isinstance(t, dict) else t for t in game_data['themes']]

        # Game Modes
        if game_data.get('game_modes'):
            metadata['igdb__game_modes'] = [gm.get('name') if isinstance(gm, dict) else gm for gm in game_data['game_modes']]

        # Player Perspectives
        if game_data.get('player_perspectives'):
            metadata['igdb__player_perspectives'] = [pp.get('name') if isinstance(pp, dict) else pp for pp in game_data['player_perspectives']]

        # Keywords
        if game_data.get('keywords'):
            metadata['igdb__keywords'] = [k.get('name') if isinstance(k, dict) else k for k in game_data['keywords']]

        # Platforms
        if game_data.get('platforms'):
            metadata['igdb__platforms'] = [p.get('name') if isinstance(p, dict) else p for p in game_data['platforms']]

        # Alternative Names
        if game_data.get('alternative_names'):
            metadata['igdb__alternative_names'] = [an.get('name') if isinstance(an, dict) else an for an in game_data['alternative_names']]

        # Multiplayer Modes
        if game_data.get('multiplayer_modes'):
            metadata['igdb__multiplayer_modes'] = game_data['multiplayer_modes']

        # Companies
        if game_data.get('involved_companies'):
            metadata['igdb__involved_companies'] = game_data['involved_companies']

            # Extract developers and publishers separately
            developers = []
            publishers = []
            for company in game_data['involved_companies']:
                if isinstance(company, dict):
                    company_name = company.get('company', {}).get('name') if isinstance(company.get('company'), dict) else None
                    if company_name:
                        if company.get('developer'):
                            developers.append(company_name)
                        if company.get('publisher'):
                            publishers.append(company_name)

            metadata['igdb__developers'] = developers if developers else None
            metadata['igdb__publishers'] = publishers if publishers else None

        # Age Ratings
        if game_data.get('age_ratings'):
            metadata['igdb__age_ratings'] = game_data['age_ratings']

            # Extract specific ratings
            for rating in game_data['age_ratings']:
                if isinstance(rating, dict):
                    category = rating.get('category')
                    rating_value = rating.get('rating')

                    # ESRB (1)
                    if category == 1:
                        esrb_map = {1: 'RP', 2: 'EC', 3: 'E', 4: 'E10+', 5: 'T', 6: 'M', 7: 'AO'}
                        metadata['igdb__esrb_rating'] = esrb_map.get(rating_value, f'ESRB_{rating_value}')

                    # PEGI (2)
                    elif category == 2:
                        pegi_map = {1: 'PEGI 3', 2: 'PEGI 7', 3: 'PEGI 12', 4: 'PEGI 16', 5: 'PEGI 18'}
                        metadata['igdb__pegi_rating'] = pegi_map.get(rating_value, f'PEGI_{rating_value}')

        # Release Dates
        if game_data.get('release_dates'):
            metadata['igdb__release_dates'] = game_data['release_dates']

        # Similar Games
        if game_data.get('similar_games'):
            metadata['igdb__similar_games'] = [sg.get('id') if isinstance(sg, dict) else sg for sg in game_data['similar_games']]

        # DLCs, Expansions, Bundles
        metadata['igdb__dlcs'] = game_data.get('dlcs')
        metadata['igdb__expansions'] = game_data.get('expansions')
        metadata['igdb__bundles'] = game_data.get('bundles')
        metadata['igdb__remakes'] = game_data.get('remakes')
        metadata['igdb__remasters'] = game_data.get('remasters')

        # Franchise & Collections
        if game_data.get('franchise'):
            metadata['igdb__franchise'] = game_data['franchise'].get('name') if isinstance(game_data['franchise'], dict) else game_data['franchise']

        if game_data.get('franchises'):
            metadata['igdb__franchises'] = [f.get('name') if isinstance(f, dict) else f for f in game_data['franchises']]

        if game_data.get('collection'):
            metadata['igdb__collection'] = game_data['collection'].get('name') if isinstance(game_data['collection'], dict) else game_data['collection']

        if game_data.get('collections'):
            metadata['igdb__collections'] = [c.get('name') if isinstance(c, dict) else c for c in game_data['collections']]

        # Parent Game
        if game_data.get('parent_game'):
            metadata['igdb__parent_game'] = game_data['parent_game'].get('name') if isinstance(game_data['parent_game'], dict) else game_data['parent_game']

        # Websites
        if game_data.get('websites'):
            websites = []
            for website in game_data['websites']:
                if isinstance(website, dict):
                    websites.append({
                        'category': website.get('category'),
                        'url': website.get('url')
                    })
            metadata['igdb__websites'] = websites

        # External Games (Steam, GOG, etc.)
        if game_data.get('external_games'):
            metadata['igdb__external_games'] = game_data['external_games']

        # Game Engines
        if game_data.get('game_engines'):
            metadata['igdb__game_engines'] = [ge.get('name') if isinstance(ge, dict) else ge for ge in game_data['game_engines']]

        # Language Supports
        if game_data.get('language_supports'):
            metadata['igdb__language_supports'] = game_data['language_supports']

        return metadata


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


def sync_all_games_with_igdb(callback: Callable[[str], None] = None) -> Dict:
    """
    Sync all unsynced games with IGDB API.

    Args:
        callback: Optional callback function for progress updates

    Returns:
        dict: Result summary with success count and errors
    """
    from src.database import get_games_without_igdb_sync, update_game_with_igdb_data

    def log(message: str):
        print(message)
        if callback:
            callback(message)

    syncer = IGDBSyncer(callback=log)

    # Get games that need syncing
    games_to_sync = get_games_without_igdb_sync()

    if not games_to_sync:
        log("No games found that need IGDB syncing")
        return {
            'success': True,
            'synced_count': 0,
            'failed_count': 0,
            'message': 'No games to sync'
        }

    log(f"Found {len(games_to_sync)} games to sync with IGDB")

    synced_count = 0
    failed_count = 0
    failed_games = []

    for i, game in enumerate(games_to_sync, 1):
        game_id = game['id']
        game_title = game['title']

        log(f"\n[{i}/{len(games_to_sync)}] Syncing: {game_title}")

        try:
            # Search for the game
            search_result = syncer.search_game(game_title)

            if not search_result:
                log(f"  ✗ Could not find '{game_title}' on IGDB")
                failed_count += 1
                failed_games.append(game_title)
                time.sleep(0.5)  # Rate limiting
                continue

            # Get full details
            igdb_game_id = search_result.get('id')
            game_data = syncer.get_game_details(igdb_game_id)

            if not game_data:
                log(f"  ✗ Failed to fetch details for '{game_title}'")
                failed_count += 1
                failed_games.append(game_title)
                time.sleep(0.5)
                continue

            # Extract all metadata
            metadata = syncer.extract_all_metadata(game_data)

            # Update database
            success = update_game_with_igdb_data(game_id, metadata)

            if success:
                log(f"  ✓ Successfully synced '{game_title}'")
                synced_count += 1
            else:
                log(f"  ✗ Failed to update database for '{game_title}'")
                failed_count += 1
                failed_games.append(game_title)

            # Rate limiting (IGDB allows 4 requests per second)
            time.sleep(0.3)

        except Exception as e:
            log(f"  ✗ Error syncing '{game_title}': {str(e)}")
            failed_count += 1
            failed_games.append(game_title)
            time.sleep(0.5)

    log(f"\n{'='*60}")
    log(f"IGDB Sync Complete!")
    log(f"Successfully synced: {synced_count}")
    log(f"Failed: {failed_count}")
    if failed_games:
        log(f"Failed games: {', '.join(failed_games)}")
    log(f"{'='*60}\n")

    return {
        'success': True,
        'synced_count': synced_count,
        'failed_count': failed_count,
        'failed_games': failed_games,
        'message': f'Synced {synced_count} games, {failed_count} failed'
    }
