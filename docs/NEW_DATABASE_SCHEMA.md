# New Database Schema Design

## Design Philosophy

**Clear Separation**: Epic Games data vs RAWG data vs IGDB data
- Epic parser creates minimal entry (title + epic_id only)
- RAWG sync adds comprehensive metadata with `rawg__` prefix
- IGDB sync adds its own metadata with `igdb__` prefix (future)

## New Table Structure

```sql
CREATE TABLE games (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- ===== EPIC GAMES DATA (from parser) =====
    title TEXT NOT NULL UNIQUE,           -- Game title from Epic
    epic_id TEXT,                         -- Epic Games ID (if available)
    epic_added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- ===== RAWG API DATA (from sync) =====
    -- Basic Info
    rawg__id INTEGER,                     -- RAWG game ID
    rawg__slug TEXT,                      -- RAWG URL slug
    rawg__name TEXT,                      -- Name on RAWG
    rawg__name_original TEXT,             -- Original name
    rawg__description TEXT,               -- Full description (HTML)
    rawg__description_raw TEXT,           -- Raw text description

    -- Dates
    rawg__released TEXT,                  -- Release date (YYYY-MM-DD)
    rawg__tba BOOLEAN,                    -- To Be Announced
    rawg__updated TEXT,                   -- Last updated on RAWG

    -- Ratings & Reviews
    rawg__rating REAL,                    -- RAWG rating (0-5)
    rawg__rating_top INTEGER,             -- Top rating category
    rawg__ratings JSON,                   -- Detailed ratings breakdown
    rawg__ratings_count INTEGER,          -- Number of ratings
    rawg__reviews_count INTEGER,          -- Number of reviews
    rawg__reviews_text_count INTEGER,     -- Text reviews count
    rawg__metacritic INTEGER,             -- Metacritic score (0-100)
    rawg__metacritic_url TEXT,            -- Metacritic page URL
    rawg__metacritic_platforms JSON,      -- Per-platform Metacritic scores

    -- Player Counts (KEY FEATURE!)
    rawg__local_players_min INTEGER,      -- Min local players
    rawg__local_players_max INTEGER,      -- Max local players
    rawg__online_players_min INTEGER,     -- Min online players
    rawg__online_players_max INTEGER,     -- Max online players

    -- Statistics
    rawg__playtime INTEGER,               -- Average playtime (hours)
    rawg__added INTEGER,                  -- Users who added this game
    rawg__added_by_status JSON,           -- Breakdown by status
    rawg__suggestions_count INTEGER,      -- Similar games count

    -- Content Counts
    rawg__achievements_count INTEGER,     -- Total achievements
    rawg__screenshots_count INTEGER,      -- Screenshots count
    rawg__movies_count INTEGER,           -- Trailers/videos count
    rawg__creators_count INTEGER,         -- Creators count
    rawg__additions_count INTEGER,        -- DLC count
    rawg__game_series_count INTEGER,      -- Series games count
    rawg__parents_count INTEGER,          -- Parent games count

    -- Media & Images
    rawg__background_image TEXT,          -- Main background image URL
    rawg__background_image_additional TEXT, -- Additional background
    rawg__screenshots JSON,               -- Array of screenshot objects
    rawg__trailers JSON,                  -- Array of trailer objects

    -- Classifications
    rawg__genres JSON,                    -- Array of genre objects
    rawg__tags JSON,                      -- Array of tag objects
    rawg__platforms JSON,                 -- Array of platform objects
    rawg__parent_platforms JSON,          -- Array of parent platforms
    rawg__esrb_rating JSON,               -- ESRB rating object

    -- Achievements
    rawg__achievements JSON,              -- Array of achievement objects

    -- Store Links
    rawg__stores JSON,                    -- Array of store objects with URLs
    rawg__website TEXT,                   -- Official website

    -- Development
    rawg__developers JSON,                -- Array of developer objects
    rawg__publishers JSON,                -- Array of publisher objects
    rawg__creators JSON,                  -- Individual creators

    -- Community
    rawg__reddit_url TEXT,                -- Subreddit URL
    rawg__reddit_name TEXT,               -- Subreddit name
    rawg__reddit_description TEXT,        -- Subreddit description
    rawg__reddit_logo TEXT,               -- Subreddit logo URL
    rawg__reddit_count INTEGER,           -- Reddit posts count
    rawg__twitch_count INTEGER,           -- Twitch streams count
    rawg__youtube_count INTEGER,          -- YouTube videos count

    -- Additional Data
    rawg__alternative_names JSON,         -- Alternative names array
    rawg__reactions JSON,                 -- Emoji reactions

    -- Sync Status
    rawg__synced BOOLEAN DEFAULT 0,       -- Synced with RAWG?
    rawg__synced_at TIMESTAMP,            -- When synced
    rawg__sync_version INTEGER DEFAULT 1, -- Sync version (for re-sync)

    -- ===== IGDB API DATA (future) =====
    igdb__id INTEGER,
    igdb__synced BOOLEAN DEFAULT 0,
    igdb__synced_at TIMESTAMP,
    igdb__metadata JSON,                  -- Full IGDB data

    -- ===== TIMESTAMPS =====
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## RAWG API Endpoints Used

Based on `/games/{id}` endpoint, we fetch:

### 1. Game Details (`/games/{id}`)
- Basic info (name, description, dates)
- Ratings (RAWG, Metacritic)
- Statistics (playtime, user counts)
- Content counts
- Images
- Classifications (genres, tags, platforms)
- Development info
- Community data

### 2. Screenshots (`/games/{id}/screenshots`)
- Array of high-quality screenshots with dimensions
- Stored as JSON array

### 3. Achievements (`/games/{id}/achievements`)
- Achievement name, description, icon
- Completion percentage
- Stored as JSON array

### 4. Trailers (`/games/{id}/movies`)
- Trailer name, preview image
- Video data (URLs, formats)
- Stored as JSON array

### 5. Store Links (`/games/{id}/stores`)
- Store name (Steam, Epic, GOG, etc.)
- Purchase URL
- Stored as JSON array

## JSON Field Formats

### Screenshots JSON
```json
[
  {
    "id": 123,
    "image": "https://...",
    "width": 1920,
    "height": 1080,
    "is_deleted": false
  }
]
```

### Achievements JSON
```json
[
  {
    "id": 456,
    "name": "Achievement Name",
    "description": "How to unlock",
    "image": "https://...",
    "percent": "45.2"
  }
]
```

### Trailers JSON
```json
[
  {
    "id": 789,
    "name": "Official Trailer",
    "preview": "https://preview.jpg",
    "data": {
      "480": "https://video-480p.mp4",
      "max": "https://video-hd.mp4"
    }
  }
]
```

### Stores JSON
```json
[
  {
    "id": 1,
    "store_name": "Steam",
    "url": "https://store.steampowered.com/app/..."
  }
]
```

### Genres JSON
```json
[
  {
    "id": 4,
    "name": "Action",
    "slug": "action"
  }
]
```

### Developers/Publishers JSON
```json
[
  {
    "id": 123,
    "name": "Valve",
    "slug": "valve",
    "games_count": 42
  }
]
```

## Migration Strategy

1. **Backup current database**
2. **Create new table structure**
3. **Migrate existing data**:
   - Map old columns to new `rawg__*` columns
   - Keep Epic data in `title` and `epic_id`
4. **Drop old columns** (or keep for safety)
5. **Update all queries** in code

## Benefits

1. **Clear Data Source**: Know exactly where each field came from
2. **Easy to Extend**: Add IGDB with `igdb__*` prefix without conflicts
3. **Re-sync Friendly**: Can re-sync RAWG data without touching Epic data
4. **Queryable**: Can filter by sync status, data source
5. **Maintainable**: Easy to see what data we're storing from each API

## Column Count

- Epic: 3 columns
- RAWG: ~50 columns (including JSON fields)
- IGDB: ~5 columns (reserved for future)
- System: 3 columns (id, created_at, updated_at)
- **Total: ~61 columns**
