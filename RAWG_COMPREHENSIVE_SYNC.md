# Comprehensive RAWG Metadata Sync

## Overview

The RAWG sync now fetches **ALL available information** from the RAWG API for each game. This provides the most complete gaming library database possible.

## What Information is Fetched

### 🎮 Basic Game Information
- **Title** (original and localized)
- **Description** (full text)
- **Alternative Names**
- **Release Date**
- **TBA Status** (To Be Announced)

### ⭐ Ratings & Reviews
- **RAWG Rating** (0-5 scale)
- **Rating Top** (maximum rating tier)
- **Metacritic Score** (0-100)
- **Metacritic URL** (direct link)
- **Ratings Count** (number of user ratings)
- **Reviews Count** (number of text reviews)

### 🖼️ Visual Assets
- **Background Image** (high quality)
- **Additional Background Image**
- **Cover Image**
- **Screenshots** (full collection with dimensions)
  - Image URLs
  - Width & Height
  - Screenshot IDs

### 🎬 Media
- **Trailers** (gameplay videos & trailers)
  - Trailer name
  - Preview image
  - Video data (URLs, formats)

### 🏆 Achievements
- **Achievement List** (up to 20 achievements)
  - Achievement name
  - Description
  - Icon/Image
  - Completion percentage
- **Total Achievement Count**

### 🎯 Categories
- **Genres** (Action, RPG, Adventure, etc.)
- **Tags** (Single-player, Multiplayer, Co-op, etc.)
- **ESRB Rating** (Everyone, Teen, Mature, etc.)

### 💻 Platform Information
- **Platforms** (PC, PlayStation, Xbox, Switch, etc.)
- **Parent Platforms** (PlayStation, Xbox, PC, etc.)

### 👥 Player Counts
- **Local Players**
  - Minimum players
  - Maximum players
  - Detected from tags: "Split Screen", "Local Co-op", etc.

- **Online Players**
  - Minimum players
  - Maximum players
  - Detected from tags: "Multiplayer", "MMO", "PvP", etc.

### 🏢 Development Information
- **Developers**
  - Developer name
  - Developer ID
  - Developer slug

- **Publishers**
  - Publisher name
  - Publisher ID
  - Publisher slug

### 🛒 Store Links
- **Where to Buy**
  - Store name (Steam, Epic, GOG, etc.)
  - Direct purchase URL
  - Store ID

### 📊 Community & Statistics
- **Website** (official game website)
- **Average Playtime** (in hours)
- **Added Count** (users who added this game)
- **Suggestions Count** (similar game suggestions)

### 💬 Reddit Integration
- **Reddit URL** (game's subreddit)
- **Reddit Name**
- **Reddit Description**
- **Reddit Logo**
- **Reddit Post Count**

### 📈 Content Counts
- **Screenshots Count**
- **Movies/Trailers Count**
- **Creators Count** (developers involved)

### 🔄 Update Information
- **Last Updated on RAWG** (when metadata was last updated)
- **Synced with RAWG** (sync status flag)

## API Endpoints Used

The sync now makes **5 API calls per game** to fetch complete information:

1. **GET /games?search={title}** - Search for the game
2. **GET /games/{id}** - Get detailed game information
3. **GET /games/{id}/screenshots** - Get all screenshots
4. **GET /games/{id}/achievements** - Get achievement list
5. **GET /games/{id}/movies** - Get trailers and videos
6. **GET /games/{id}/stores** - Get store purchase links

## Rate Limiting

The sync includes intelligent rate limiting:
- **1 second delay** between games
- **0.3 second delay** between API calls for the same game
- Respects RAWG API free tier limits

## Storage

All metadata is stored in a local SQLite database with proper JSON encoding for complex fields:
- **Simple fields**: Stored as-is (text, numbers, booleans)
- **Lists & Objects**: Stored as JSON strings, parsed when retrieved

## Benefits

### For Users
- **Rich Game Details**: Complete information about each game
- **Visual Gallery**: Full screenshot collections
- **Achievement Tracking**: See all achievements for each game
- **Purchase Options**: Direct links to buy the game
- **Community Info**: Reddit integration for discussions

### For Developers
- **Comprehensive Dataset**: All RAWG data available for analysis
- **Offline Access**: Everything stored locally
- **Extensible**: Easy to add more features using the rich metadata

## Example Output

When syncing a game, you'll see:

```
[1/50] Cyberpunk 2077
Searching RAWG for: Cyberpunk 2077
  → Fetching game details...
  → Fetching screenshots...
  → Fetching achievements...
  → Fetching trailers...
  → Fetching store links...
  → Processing metadata...
  ✓ Synced: 15 screenshots, 44 achievements, 3 trailers, 6 stores

[2/50] The Witcher 3: Wild Hunt
...
```

## Database Schema

All new fields added to the `games` table:
- `name_original`
- `website`
- `rating_top`
- `playtime`
- `achievements_count`
- `screenshots_count`
- `movies_count`
- `creators_count`
- `reddit_url`, `reddit_name`, `reddit_description`, `reddit_logo`, `reddit_count`
- `metacritic_url`
- `ratings_count`
- `reviews_count`
- `alternative_names` (JSON)
- `achievements` (JSON)
- `trailers` (JSON)
- `stores` (JSON)
- `developers` (JSON)
- `publishers` (JSON)
- `parent_platforms` (JSON)
- `background_image_additional`
- `tba`
- `updated_at_rawg`
- `added_count`
- `suggestions_count`

## Performance

**Time per game**: ~3-5 seconds (with rate limiting)
**For 50 games**: ~3-4 minutes
**For 100 games**: ~6-8 minutes

The comprehensive sync is slower but provides **maximum information** for your library!

## Future Enhancements

Possible additions:
- Development team members (individual creators)
- Game series information
- DLC and expansion detection
- Community reviews
- YouTube/Twitch integration (business tier only)
