"""
Database module for Epic Games Library Manager
Clean separation: Epic data vs RAWG data vs IGDB data
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# Get the project root directory (two levels up from this file: src/database.py -> src/ -> myGamingLib/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DATABASE_NAME = os.path.join(DATA_DIR, "epic_games_library.db")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with clean schema."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create table only if it doesn't exist (preserves existing data)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            -- Primary Key
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            -- ===== EPIC GAMES DATA (from parser) =====
            title TEXT NOT NULL UNIQUE,
            epic_id TEXT,
            epic_added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            -- ===== RAWG API DATA (from sync) =====
            -- Basic Info
            rawg__id INTEGER,
            rawg__slug TEXT,
            rawg__name TEXT,
            rawg__name_original TEXT,
            rawg__description TEXT,
            rawg__description_raw TEXT,

            -- Dates
            rawg__released TEXT,
            rawg__tba BOOLEAN,
            rawg__updated TEXT,

            -- Ratings & Reviews
            rawg__rating REAL,
            rawg__rating_top INTEGER,
            rawg__ratings TEXT,
            rawg__ratings_count INTEGER,
            rawg__reviews_count INTEGER,
            rawg__reviews_text_count INTEGER,
            rawg__metacritic INTEGER,
            rawg__metacritic_url TEXT,
            rawg__metacritic_platforms TEXT,

            -- Player Counts (KEY FEATURE!)
            rawg__local_players_min INTEGER,
            rawg__local_players_max INTEGER,
            rawg__online_players_min INTEGER,
            rawg__online_players_max INTEGER,

            -- Statistics
            rawg__playtime INTEGER,
            rawg__added INTEGER,
            rawg__added_by_status TEXT,
            rawg__suggestions_count INTEGER,

            -- Content Counts
            rawg__achievements_count INTEGER,
            rawg__screenshots_count INTEGER,
            rawg__movies_count INTEGER,
            rawg__creators_count INTEGER,
            rawg__additions_count INTEGER,
            rawg__game_series_count INTEGER,
            rawg__parents_count INTEGER,

            -- Media & Images
            rawg__background_image TEXT,
            rawg__background_image_additional TEXT,
            rawg__screenshots TEXT,
            rawg__trailers TEXT,

            -- Classifications
            rawg__genres TEXT,
            rawg__tags TEXT,
            rawg__platforms TEXT,
            rawg__parent_platforms TEXT,
            rawg__esrb_rating TEXT,

            -- Achievements
            rawg__achievements TEXT,

            -- Store Links
            rawg__stores TEXT,
            rawg__website TEXT,

            -- Development
            rawg__developers TEXT,
            rawg__publishers TEXT,
            rawg__creators TEXT,

            -- Community
            rawg__reddit_url TEXT,
            rawg__reddit_name TEXT,
            rawg__reddit_description TEXT,
            rawg__reddit_logo TEXT,
            rawg__reddit_count INTEGER,
            rawg__twitch_count INTEGER,
            rawg__youtube_count INTEGER,

            -- Additional Data
            rawg__alternative_names TEXT,
            rawg__reactions TEXT,

            -- Sync Status
            rawg__synced BOOLEAN DEFAULT 0,
            rawg__synced_at TIMESTAMP,

            -- ===== IGDB API DATA =====
            -- Basic Info
            igdb__id INTEGER,
            igdb__name TEXT,
            igdb__slug TEXT,
            igdb__summary TEXT,
            igdb__storyline TEXT,
            igdb__url TEXT,

            -- Dates
            igdb__first_release_date INTEGER,
            igdb__created_at INTEGER,
            igdb__updated_at INTEGER,

            -- Ratings
            igdb__rating REAL,
            igdb__rating_count INTEGER,
            igdb__total_rating REAL,
            igdb__total_rating_count INTEGER,
            igdb__aggregated_rating REAL,
            igdb__aggregated_rating_count INTEGER,
            igdb__hypes INTEGER,
            igdb__follows INTEGER,

            -- Classification
            igdb__category INTEGER,
            igdb__status INTEGER,
            igdb__version_title TEXT,

            -- Media
            igdb__cover TEXT,
            igdb__artworks TEXT,
            igdb__screenshots TEXT,
            igdb__videos TEXT,

            -- Game Info
            igdb__genres TEXT,
            igdb__themes TEXT,
            igdb__game_modes TEXT,
            igdb__player_perspectives TEXT,
            igdb__keywords TEXT,
            igdb__platforms TEXT,
            igdb__alternative_names TEXT,

            -- Multiplayer
            igdb__multiplayer_modes TEXT,

            -- Companies
            igdb__involved_companies TEXT,
            igdb__developers TEXT,
            igdb__publishers TEXT,

            -- Ratings & Age
            igdb__age_ratings TEXT,
            igdb__esrb_rating TEXT,
            igdb__pegi_rating TEXT,

            -- Release Info
            igdb__release_dates TEXT,

            -- Related Games
            igdb__similar_games TEXT,
            igdb__dlcs TEXT,
            igdb__expansions TEXT,
            igdb__bundles TEXT,
            igdb__remakes TEXT,
            igdb__remasters TEXT,
            igdb__franchise TEXT,
            igdb__franchises TEXT,
            igdb__collection TEXT,
            igdb__collections TEXT,
            igdb__parent_game TEXT,

            -- External Links
            igdb__websites TEXT,
            igdb__external_games TEXT,

            -- Game Engines & Localization
            igdb__game_engines TEXT,
            igdb__language_supports TEXT,

            -- Sync Status
            igdb__synced BOOLEAN DEFAULT 0,
            igdb__synced_at TIMESTAMP,

            -- ===== TIMESTAMPS =====
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("[OK] Database initialized with clean Epic/RAWG separation schema")


# ===== EPIC GAMES FUNCTIONS =====

def add_game(title: str, epic_id: Optional[str] = None) -> Tuple[int, bool]:
    """
    Add a new game from Epic Games parser.
    Only stores title and epic_id - RAWG data added later via sync.

    Args:
        title: Game title from Epic Games
        epic_id: Epic Games ID (optional)

    Returns:
        tuple[int, bool]: (game_id, was_new) where was_new is True if newly added
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    was_new = False
    try:
        cursor.execute(
            "INSERT INTO games (title, epic_id, epic_added_at) VALUES (?, ?, ?)",
            (title, epic_id, datetime.now())
        )
        conn.commit()
        game_id = cursor.lastrowid
        was_new = True
    except sqlite3.IntegrityError:
        # Game already exists, get its ID
        cursor.execute("SELECT id FROM games WHERE title = ?", (title,))
        game_id = cursor.fetchone()[0]
        was_new = False
    finally:
        conn.close()

    return (game_id, was_new)


# ===== RAWG SYNC FUNCTIONS =====

def update_game_with_rawg_data(game_id: int, rawg_data: Dict) -> bool:
    """
    Update game with comprehensive RAWG metadata.

    Args:
        game_id: Database game ID
        rawg_data: Dictionary with all RAWG fields (with rawg__ prefix)

    Returns:
        bool: True if successful
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Build dynamic UPDATE query from rawg_data keys
    set_clauses = []
    values = []

    for key, value in rawg_data.items():
        if key.startswith('rawg__'):
            set_clauses.append(f"{key} = ?")
            # Convert lists/dicts to JSON strings
            if isinstance(value, (list, dict)):
                values.append(json.dumps(value))
            else:
                values.append(value)

    # Add sync status and timestamp
    set_clauses.append("rawg__synced = ?")
    set_clauses.append("rawg__synced_at = ?")
    set_clauses.append("updated_at = ?")
    values.extend([1, datetime.now(), datetime.now()])

    # Add game_id for WHERE clause
    values.append(game_id)

    query = f"UPDATE games SET {', '.join(set_clauses)} WHERE id = ?"

    try:
        cursor.execute(query, values)
        conn.commit()
        success = cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating game {game_id}: {e}")
        success = False
    finally:
        conn.close()

    return success


def get_games_without_rawg_sync() -> List[Dict]:
    """Get all games that haven't been synced with RAWG yet."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, epic_id
        FROM games
        WHERE rawg__synced = 0 OR rawg__synced IS NULL
    """)

    games = []
    for row in cursor.fetchall():
        games.append({
            'id': row['id'],
            'title': row['title'],
            'epic_id': row['epic_id']
        })

    conn.close()
    return games


# ===== IGDB FUNCTIONS =====

def update_game_with_igdb_data(game_id: int, igdb_data: Dict) -> bool:
    """
    Update game with comprehensive IGDB metadata.

    Args:
        game_id: Database game ID
        igdb_data: Dictionary with all IGDB fields (with igdb__ prefix)

    Returns:
        bool: True if successful
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Build dynamic UPDATE query from igdb_data keys
    set_clauses = []
    values = []

    for key, value in igdb_data.items():
        if key.startswith('igdb__'):
            set_clauses.append(f"{key} = ?")
            # Convert lists/dicts to JSON strings
            if isinstance(value, (list, dict)):
                values.append(json.dumps(value))
            else:
                values.append(value)

    # Add sync status and timestamp
    set_clauses.append("igdb__synced = ?")
    set_clauses.append("igdb__synced_at = ?")
    set_clauses.append("updated_at = ?")
    values.extend([1, datetime.now(), datetime.now()])

    # Add game_id for WHERE clause
    values.append(game_id)

    query = f"UPDATE games SET {', '.join(set_clauses)} WHERE id = ?"

    try:
        cursor.execute(query, values)
        conn.commit()
        success = cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating game {game_id} with IGDB data: {e}")
        success = False
    finally:
        conn.close()

    return success


def get_games_without_igdb_sync() -> List[Dict]:
    """Get all games that haven't been synced with IGDB yet."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, epic_id
        FROM games
        WHERE igdb__synced = 0 OR igdb__synced IS NULL
    """)

    games = []
    for row in cursor.fetchall():
        games.append({
            'id': row['id'],
            'title': row['title'],
            'epic_id': row['epic_id']
        })

    conn.close()
    return games


def get_igdb_synced_count() -> int:
    """Get count of games synced with IGDB."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) as count
        FROM games
        WHERE igdb__synced = 1
    """)

    count = cursor.fetchone()['count']
    conn.close()
    return count


# ===== QUERY FUNCTIONS =====

def get_all_games() -> List[Dict]:
    """Get all games with all their data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM games ORDER BY title")

    games = []
    for row in cursor.fetchall():
        game_dict = dict(row)

        # Parse JSON fields
        json_fields = [
            # RAWG fields
            'rawg__ratings', 'rawg__metacritic_platforms', 'rawg__added_by_status',
            'rawg__screenshots', 'rawg__trailers', 'rawg__genres', 'rawg__tags',
            'rawg__platforms', 'rawg__parent_platforms', 'rawg__esrb_rating',
            'rawg__achievements', 'rawg__stores', 'rawg__developers', 'rawg__publishers',
            'rawg__creators', 'rawg__alternative_names', 'rawg__reactions',
            # IGDB fields
            'igdb__metadata', 'igdb__artworks', 'igdb__screenshots', 'igdb__videos',
            'igdb__genres', 'igdb__themes', 'igdb__game_modes', 'igdb__player_perspectives',
            'igdb__keywords', 'igdb__platforms', 'igdb__alternative_names',
            'igdb__multiplayer_modes', 'igdb__involved_companies', 'igdb__developers',
            'igdb__publishers', 'igdb__age_ratings', 'igdb__release_dates',
            'igdb__similar_games', 'igdb__dlcs', 'igdb__expansions', 'igdb__bundles',
            'igdb__remakes', 'igdb__remasters', 'igdb__franchises', 'igdb__collections',
            'igdb__websites', 'igdb__external_games', 'igdb__game_engines',
            'igdb__language_supports'
        ]

        for field in json_fields:
            if game_dict.get(field):
                try:
                    game_dict[field] = json.loads(game_dict[field])
                except:
                    pass

        games.append(game_dict)

    conn.close()
    return games


def get_game_by_id(game_id: int) -> Optional[Dict]:
    """Get a single game by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM games WHERE id = ?", (game_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    game_dict = dict(row)

    # Parse JSON fields
    json_fields = [
        # RAWG fields
        'rawg__ratings', 'rawg__metacritic_platforms', 'rawg__added_by_status',
        'rawg__screenshots', 'rawg__trailers', 'rawg__genres', 'rawg__tags',
        'rawg__platforms', 'rawg__parent_platforms', 'rawg__esrb_rating',
        'rawg__achievements', 'rawg__stores', 'rawg__developers', 'rawg__publishers',
        'rawg__creators', 'rawg__alternative_names', 'rawg__reactions',
        # IGDB fields
        'igdb__metadata', 'igdb__artworks', 'igdb__screenshots', 'igdb__videos',
        'igdb__genres', 'igdb__themes', 'igdb__game_modes', 'igdb__player_perspectives',
        'igdb__keywords', 'igdb__platforms', 'igdb__alternative_names',
        'igdb__multiplayer_modes', 'igdb__involved_companies', 'igdb__developers',
        'igdb__publishers', 'igdb__age_ratings', 'igdb__release_dates',
        'igdb__similar_games', 'igdb__dlcs', 'igdb__expansions', 'igdb__bundles',
        'igdb__remakes', 'igdb__remasters', 'igdb__franchises', 'igdb__collections',
        'igdb__websites', 'igdb__external_games', 'igdb__game_engines',
        'igdb__language_supports'
    ]

    for field in json_fields:
        if game_dict.get(field):
            try:
                game_dict[field] = json.loads(game_dict[field])
            except:
                pass

    conn.close()
    return game_dict


def get_game_count() -> int:
    """Get total number of games in library."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM games")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_rawg_synced_count() -> int:
    """Get number of games synced with RAWG."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM games WHERE rawg__synced = 1")
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ===== LEGACY COMPATIBILITY FUNCTIONS =====
# These provide backwards compatibility with old code

def update_game_metadata(game_id: int, metadata: Dict) -> bool:
    """
    Legacy function for backwards compatibility.
    Converts old format metadata to new rawg__ prefixed format.
    """
    # Convert old metadata format to new format
    rawg_data = {}

    # Map old keys to new rawg__ prefixed keys
    key_mapping = {
        'rawg_id': 'rawg__id',
        'rawg_slug': 'rawg__slug',
        'name': 'rawg__name',
        'name_original': 'rawg__name_original',
        'description': 'rawg__description',
        'description_raw': 'rawg__description_raw',
        'released': 'rawg__released',
        'tba': 'rawg__tba',
        'updated': 'rawg__updated',
        'rating': 'rawg__rating',
        'rating_top': 'rawg__rating_top',
        'ratings': 'rawg__ratings',
        'ratings_count': 'rawg__ratings_count',
        'reviews_count': 'rawg__reviews_count',
        'reviews_text_count': 'rawg__reviews_text_count',
        'metacritic': 'rawg__metacritic',
        'metacritic_url': 'rawg__metacritic_url',
        'metacritic_platforms': 'rawg__metacritic_platforms',
        'local_players_min': 'rawg__local_players_min',
        'local_players_max': 'rawg__local_players_max',
        'online_players_min': 'rawg__online_players_min',
        'online_players_max': 'rawg__online_players_max',
        'playtime': 'rawg__playtime',
        'added': 'rawg__added',
        'added_by_status': 'rawg__added_by_status',
        'suggestions_count': 'rawg__suggestions_count',
        'achievements_count': 'rawg__achievements_count',
        'screenshots_count': 'rawg__screenshots_count',
        'movies_count': 'rawg__movies_count',
        'creators_count': 'rawg__creators_count',
        'additions_count': 'rawg__additions_count',
        'game_series_count': 'rawg__game_series_count',
        'parents_count': 'rawg__parents_count',
        'background_image': 'rawg__background_image',
        'background_image_additional': 'rawg__background_image_additional',
        'screenshots': 'rawg__screenshots',
        'trailers': 'rawg__trailers',
        'genres': 'rawg__genres',
        'tags': 'rawg__tags',
        'platforms': 'rawg__platforms',
        'parent_platforms': 'rawg__parent_platforms',
        'esrb_rating': 'rawg__esrb_rating',
        'achievements': 'rawg__achievements',
        'stores': 'rawg__stores',
        'website': 'rawg__website',
        'developers': 'rawg__developers',
        'publishers': 'rawg__publishers',
        'creators': 'rawg__creators',
        'reddit_url': 'rawg__reddit_url',
        'reddit_name': 'rawg__reddit_name',
        'reddit_description': 'rawg__reddit_description',
        'reddit_logo': 'rawg__reddit_logo',
        'reddit_count': 'rawg__reddit_count',
        'twitch_count': 'rawg__twitch_count',
        'youtube_count': 'rawg__youtube_count',
        'alternative_names': 'rawg__alternative_names',
        'reactions': 'rawg__reactions',
    }

    for old_key, new_key in key_mapping.items():
        if old_key in metadata:
            rawg_data[new_key] = metadata[old_key]

    return update_game_with_rawg_data(game_id, rawg_data)


# Initialize database on import
init_db()
