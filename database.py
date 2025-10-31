import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

DATABASE_NAME = "epic_games_library.db"

def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            epic_id TEXT,
            description TEXT,
            genres TEXT,
            local_players_min INTEGER,
            local_players_max INTEGER,
            online_players_min INTEGER,
            online_players_max INTEGER,
            release_date TEXT,
            rating REAL,
            metacritic_score INTEGER,
            screenshots TEXT,
            cover_image TEXT,
            background_image TEXT,
            rawg_id INTEGER,
            rawg_slug TEXT,
            platforms TEXT,
            tags TEXT,
            esrb_rating TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            synced_with_rawg BOOLEAN DEFAULT 0
        )
    """)

    # Add new columns for extended RAWG metadata (if they don't exist)
    new_columns = [
        ("name_original", "TEXT"),
        ("website", "TEXT"),
        ("rating_top", "INTEGER"),
        ("playtime", "INTEGER"),
        ("achievements_count", "INTEGER"),
        ("screenshots_count", "INTEGER"),
        ("movies_count", "INTEGER"),
        ("creators_count", "INTEGER"),
        ("reddit_url", "TEXT"),
        ("reddit_name", "TEXT"),
        ("reddit_description", "TEXT"),
        ("reddit_logo", "TEXT"),
        ("reddit_count", "INTEGER"),
        ("metacritic_url", "TEXT"),
        ("ratings_count", "INTEGER"),
        ("reviews_count", "INTEGER"),
        ("alternative_names", "TEXT"),  # JSON
        ("achievements", "TEXT"),  # JSON
        ("trailers", "TEXT"),  # JSON
        ("stores", "TEXT"),  # JSON
        ("developers", "TEXT"),  # JSON
        ("publishers", "TEXT"),  # JSON
        ("parent_platforms", "TEXT"),  # JSON
        ("background_image_additional", "TEXT"),
        ("tba", "BOOLEAN"),  # To Be Announced
        ("updated_at_rawg", "TEXT"),  # Last updated on RAWG
        ("added_count", "INTEGER"),  # Number of users who added this game
        ("suggestions_count", "INTEGER")
    ]

    # Try to add each column (will silently fail if column already exists)
    for column_name, column_type in new_columns:
        try:
            cursor.execute(f"ALTER TABLE games ADD COLUMN {column_name} {column_type}")
        except Exception:
            # Column already exists, skip
            pass

    conn.commit()
    conn.close()

def add_game(title: str, epic_id: Optional[str] = None) -> tuple[int, bool]:
    """
    Add a new game to the database.

    Returns:
        tuple[int, bool]: (game_id, was_new) where was_new is True if game was newly added,
                         False if game already existed
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    was_new = False
    try:
        cursor.execute(
            "INSERT INTO games (title, epic_id) VALUES (?, ?)",
            (title, epic_id)
        )
        conn.commit()
        game_id = cursor.lastrowid
        was_new = True  # Game was newly inserted
    except sqlite3.IntegrityError:
        # Game already exists, get its ID
        cursor.execute("SELECT id FROM games WHERE title = ?", (title,))
        game_id = cursor.fetchone()[0]
        was_new = False  # Game already existed
    finally:
        conn.close()

    return (game_id, was_new)

def update_game_metadata(game_id: int, metadata: Dict) -> bool:
    """Update game with RAWG metadata."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Convert lists to JSON strings for storage
    screenshots_json = json.dumps(metadata.get('screenshots', []))
    genres_json = json.dumps(metadata.get('genres', []))
    platforms_json = json.dumps(metadata.get('platforms', []))
    tags_json = json.dumps(metadata.get('tags', []))
    alternative_names_json = json.dumps(metadata.get('alternative_names', []))
    achievements_json = json.dumps(metadata.get('achievements', []))
    trailers_json = json.dumps(metadata.get('trailers', []))
    stores_json = json.dumps(metadata.get('stores', []))
    developers_json = json.dumps(metadata.get('developers', []))
    publishers_json = json.dumps(metadata.get('publishers', []))
    parent_platforms_json = json.dumps(metadata.get('parent_platforms', []))

    cursor.execute("""
        UPDATE games SET
            description = ?,
            genres = ?,
            local_players_min = ?,
            local_players_max = ?,
            online_players_min = ?,
            online_players_max = ?,
            release_date = ?,
            rating = ?,
            metacritic_score = ?,
            screenshots = ?,
            cover_image = ?,
            background_image = ?,
            rawg_id = ?,
            rawg_slug = ?,
            platforms = ?,
            tags = ?,
            esrb_rating = ?,
            name_original = ?,
            website = ?,
            rating_top = ?,
            playtime = ?,
            achievements_count = ?,
            screenshots_count = ?,
            movies_count = ?,
            creators_count = ?,
            reddit_url = ?,
            reddit_name = ?,
            reddit_description = ?,
            reddit_logo = ?,
            reddit_count = ?,
            metacritic_url = ?,
            ratings_count = ?,
            reviews_count = ?,
            alternative_names = ?,
            achievements = ?,
            trailers = ?,
            stores = ?,
            developers = ?,
            publishers = ?,
            parent_platforms = ?,
            background_image_additional = ?,
            tba = ?,
            updated_at_rawg = ?,
            added_count = ?,
            suggestions_count = ?,
            updated_at = ?,
            synced_with_rawg = 1
        WHERE id = ?
    """, (
        metadata.get('description'),
        genres_json,
        metadata.get('local_players_min'),
        metadata.get('local_players_max'),
        metadata.get('online_players_min'),
        metadata.get('online_players_max'),
        metadata.get('release_date'),
        metadata.get('rating'),
        metadata.get('metacritic_score'),
        screenshots_json,
        metadata.get('cover_image'),
        metadata.get('background_image'),
        metadata.get('rawg_id'),
        metadata.get('rawg_slug'),
        platforms_json,
        tags_json,
        metadata.get('esrb_rating'),
        metadata.get('name_original'),
        metadata.get('website'),
        metadata.get('rating_top'),
        metadata.get('playtime'),
        metadata.get('achievements_count'),
        metadata.get('screenshots_count'),
        metadata.get('movies_count'),
        metadata.get('creators_count'),
        metadata.get('reddit_url'),
        metadata.get('reddit_name'),
        metadata.get('reddit_description'),
        metadata.get('reddit_logo'),
        metadata.get('reddit_count'),
        metadata.get('metacritic_url'),
        metadata.get('ratings_count'),
        metadata.get('reviews_count'),
        alternative_names_json,
        achievements_json,
        trailers_json,
        stores_json,
        developers_json,
        publishers_json,
        parent_platforms_json,
        metadata.get('background_image_additional'),
        metadata.get('tba'),
        metadata.get('updated_at_rawg'),
        metadata.get('added_count'),
        metadata.get('suggestions_count'),
        datetime.now().isoformat(),
        game_id
    ))

    conn.commit()
    conn.close()
    return True

def get_all_games() -> List[Dict]:
    """Retrieve all games from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM games ORDER BY title")
    rows = cursor.fetchall()
    conn.close()

    games = []
    for row in rows:
        game = dict(row)
        # Parse JSON fields
        json_fields = [
            'screenshots', 'genres', 'platforms', 'tags',
            'alternative_names', 'achievements', 'trailers',
            'stores', 'developers', 'publishers', 'parent_platforms'
        ]
        for field in json_fields:
            if field in game and game[field]:
                try:
                    game[field] = json.loads(game[field])
                except:
                    game[field] = []
        games.append(game)

    return games

def get_games_without_rawg_sync() -> List[Dict]:
    """Get games that haven't been synced with RAWG yet."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM games WHERE synced_with_rawg = 0")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

def clear_all_games():
    """Clear all games from the database (for testing)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM games")
    conn.commit()
    conn.close()

def get_game_count() -> int:
    """Get total number of games in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM games")
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Initialize database on import
init_db()
