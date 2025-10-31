# Terminal Game Information Display

## Overview

When you click on any game in the web interface, **all comprehensive information** about that game is automatically printed to the terminal where `python app.py` is running.

## How It Works

### 1. Click Any Game
Click on any game card in your library grid.

### 2. View in Modal
The game details modal opens in the browser as usual.

### 3. Check Terminal
**Simultaneously**, all game information is printed to your terminal with beautiful formatting!

## What Gets Printed

The terminal output includes **every single piece of data** stored for the game:

### 📋 Basic Information
- Database ID
- Title (Epic Games name)
- Original Name (RAWG name)
- RAWG ID & Slug
- Epic ID
- Alternative Names

### 📅 Dates
- Release Date
- TBA Status
- Added to Database
- Last Updated
- RAWG Last Updated

### ⭐ Ratings & Reviews
- RAWG Rating (0-5 scale)
- Rating Top
- Total Ratings Count
- Reviews Count
- Metacritic Score (0-100)
- Metacritic URL
- ESRB Rating

### 👥 Player Counts (LOCAL & ONLINE)
- Local Players: Min - Max
- Online Players: Min - Max

### 📊 Statistics
- Average Playtime (hours)
- Users Who Added This Game
- Suggestions Count

### 📸 Content Counts
- Screenshots Count
- Achievements Count
- Movies/Trailers Count
- Creators Count

### 🎯 Genres
Complete list of genres

### 💻 Platforms
- All platforms
- Parent platforms

### 🏷️ Tags
First 20 tags (shows count if more)

### 👨‍💻 Developers
List of all developers with IDs

### 🏢 Publishers
List of all publishers with IDs

### 📷 Screenshots
- Total count
- First 5 screenshot URLs
- Shows count if more

### 🏆 Achievements
- Total count
- First 5 achievements with completion percentages
- Shows count if more

### 🎬 Trailers
- All trailers with names
- Preview image URLs

### 🛒 Where to Buy
- All store names
- Direct purchase URLs

### 🔗 Links
- Official Website
- Background Image URL
- Cover Image URL

### 💬 Reddit Community
- Subreddit Name
- Subreddit URL
- Post Count
- Description (first 100 chars)

### 📖 Description
Full game description (first 500 characters, with total count)

### ✅ Sync Status
Whether synced with RAWG or not

## Example Terminal Output

```
================================================================================
🎮 GAME DETAILS: Cyberpunk 2077
================================================================================

📋 BASIC INFORMATION
--------------------------------------------------------------------------------
  ID:              42
  Title:           Cyberpunk 2077
  Original Name:   Cyberpunk 2077
  RAWG ID:         41494
  RAWG Slug:       cyberpunk-2077
  Epic ID:         N/A

📅 DATES
--------------------------------------------------------------------------------
  Release Date:    2020-12-10
  TBA:             No
  Added to DB:     2025-10-31T10:30:45.123456
  Last Updated:    2025-10-31T10:35:22.654321
  RAWG Updated:    2025-10-15T08:20:15Z

⭐ RATINGS & REVIEWS
--------------------------------------------------------------------------------
  RAWG Rating:     4.21/5
  Rating Top:      5
  Ratings Count:   12543
  Reviews Count:   856
  Metacritic:      86/100
  Metacritic URL:  http://www.metacritic.com/game/pc/cyberpunk-2077
  ESRB Rating:     Mature

👥 PLAYER COUNTS (LOCAL & ONLINE)
--------------------------------------------------------------------------------
  Local Players:   1 - 1
  Online Players:  N/A - N/A

📊 STATISTICS
--------------------------------------------------------------------------------
  Playtime:        54 hours
  Added Count:     45678 users
  Suggestions:     234

📸 CONTENT COUNTS
--------------------------------------------------------------------------------
  Screenshots:     25
  Achievements:    44
  Movies/Trailers: 3
  Creators:        120

🎯 GENRES
--------------------------------------------------------------------------------
  Action, RPG

💻 PLATFORMS
--------------------------------------------------------------------------------
  PC, PlayStation 4, Xbox One, PlayStation 5, Xbox Series S/X
  Parent: PC, PlayStation, Xbox

🏷️ TAGS
--------------------------------------------------------------------------------
  Singleplayer, Open World, RPG, Sci-fi, Cyberpunk, Action, First-Person, FPS, Story Rich, Dystopian, Atmospheric, Futuristic, Choices Matter, Mature, Nudity, Gore, Character Customization, Sexual Content, Multiplayer, Third Person
  ... and 35 more

👨‍💻 DEVELOPERS
--------------------------------------------------------------------------------
  - CD PROJEKT RED (ID: 11111)

🏢 PUBLISHERS
--------------------------------------------------------------------------------
  - CD PROJEKT RED (ID: 11111)

📷 SCREENSHOTS
--------------------------------------------------------------------------------
  Total: 25
  1. https://media.rawg.io/media/games/26d/26d4437715bee60138dab4a7c8c59c92.jpg
  2. https://media.rawg.io/media/screenshots/817/817cc797659c5b0a583e...
  3. https://media.rawg.io/media/screenshots/cc0/cc0974f69e5c7caa9e1a...
  ... and 22 more

🏆 ACHIEVEMENTS
--------------------------------------------------------------------------------
  Total: 44
  1. The Fool - 95.2%
  2. The Lovers - 89.5%
  3. The Hermit - 76.3%
  ... and 41 more

🎬 TRAILERS
--------------------------------------------------------------------------------
  1. Cyberpunk 2077 — Official Launch Trailer
     Preview: https://media.rawg.io/media/trailers/preview.jpg

🛒 WHERE TO BUY
--------------------------------------------------------------------------------
  - Steam
    URL: https://store.steampowered.com/app/1091500
  - Epic Games
    URL: https://www.epicgames.com/store/en-US/p/cyberpunk-2077
  - GOG
    URL: https://www.gog.com/game/cyberpunk_2077

🔗 LINKS
--------------------------------------------------------------------------------
  Website:         https://www.cyberpunk.net
  Background Img:  https://media.rawg.io/media/games/26d/26d4437715bee60...
  Cover Image:     https://media.rawg.io/media/games/26d/26d4437715bee60...

💬 REDDIT COMMUNITY
--------------------------------------------------------------------------------
  Subreddit:       cyberpunkgame
  URL:             https://www.reddit.com/r/cyberpunkgame/
  Post Count:      15234
  Description:     A subreddit dedicated to Cyberpunk 2077, an open-world, action-adventure story set in Night City...

📖 DESCRIPTION
--------------------------------------------------------------------------------
  Cyberpunk 2077 is an open-world, action-adventure story set in Night City, a megalopolis obsessed with power, glamour and body modification. You play as V, a mercenary outlaw going after a one-of-a-kind implant that is the key to immortality. You can customize your character's cyberware, skillset and playstyle, and explore a vast city where the choices you make shape the story and the world around you...
  ... (2547 total characters)

✅ SYNC STATUS
--------------------------------------------------------------------------------
  Synced with RAWG: Yes

================================================================================
✓ Complete information for: Cyberpunk 2077
================================================================================
```

## Use Cases

### 1. **Debugging**
See exactly what data is stored for each game

### 2. **Data Verification**
Check if RAWG sync populated all fields correctly

### 3. **Quick Reference**
Get all URLs (screenshots, trailers, store links) in one place

### 4. **Export Data**
Copy terminal output for external use

### 5. **API Integration**
See the exact data structure for custom integrations

## How to View

1. **Run the app**:
   ```bash
   python app.py
   ```

2. **Keep terminal visible** while browsing

3. **Click any game** in the web interface

4. **Check terminal** for complete information dump

## Performance

- **Fast**: Instant terminal output
- **Non-blocking**: Doesn't slow down the web interface
- **Complete**: Shows 100% of stored data
- **Formatted**: Beautiful, easy-to-read output with emojis and sections

## Technical Details

- Endpoint: `POST /api/print-game-info/<game_id>`
- Called automatically when `showGameDetail()` is triggered
- Fetches complete game object from database
- Formats and prints to stdout (terminal)
- Works for all games (Epic-parsed and manually added)

Enjoy having complete game information at your fingertips! 🎮📊
