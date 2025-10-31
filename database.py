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
        if game['screenshots']:
            game['screenshots'] = json.loads(game['screenshots'])
        if game['genres']:
            game['genres'] = json.loads(game['genres'])
        if game['platforms']:
            game['platforms'] = json.loads(game['platforms'])
        if game['tags']:
            game['tags'] = json.loads(game['tags'])
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
