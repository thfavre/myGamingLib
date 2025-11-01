# Manual Game Addition Feature

## Overview

You can now manually add games to your library by searching the RAWG database! This is perfect for adding games that weren't found during Epic Games parsing, or for adding games you own on other platforms.

## How to Use

### Step 1: Click "Add Game Manually"

Click the green **"➕ Add Game Manually"** button in the action buttons row at the top of the page.

### Step 2: Search for a Game

1. A modal window will appear with a search box
2. Type the name of the game you want to add
3. Click **"🔍 Search RAWG"** or press Enter

### Step 3: Browse Search Results

The search will return up to 5 results from RAWG. Each result shows:

- **Game Cover Image**
- **Game Title** (original name)
- **Release Date** 📅
- **RAWG Rating** ⭐ (out of 5)
- **Metacritic Score** 🎮 (out of 100)
- **Genres** (Action, RPG, etc.)
- **Platforms** (PC, PlayStation, Xbox, etc.)

### Step 4: Add to Library

Click the **"➕ Add to Library"** button on the game you want to add.

### Step 5: Automatic Metadata Fetch

When you click "Add to Library", the app automatically:

1. Adds the game to your database
2. Fetches **comprehensive metadata** from RAWG:
   - Screenshots (full quality collection)
   - Achievements (with completion %)
   - Trailers & gameplay videos
   - Store purchase links
   - Developers & publishers
   - All ratings, genres, tags
   - Player counts (local/online)

3. Shows you a summary of what was added:
   ```
   ✅ 15 screenshots
   ✅ 44 achievements
   ✅ 3 trailers
   ✅ 6 store links
   ```

4. Refreshes your library automatically
5. Closes the modal

## Features

### ✅ Smart Search
- Searches the entire RAWG database (350,000+ games)
- Shows top 5 most relevant results
- Displays key information to help you choose the right game

### ✅ Duplicate Detection
- Won't add a game if it's already in your library
- Shows "Already Added" message if you try to add a duplicate

### ✅ Full Metadata
- Fetches **all available information** just like the RAWG sync
- Same 5 API calls per game (details, screenshots, achievements, trailers, stores)
- Completely synced and ready to browse

### ✅ Instant Updates
- Library refreshes automatically after adding
- Game appears immediately in your collection
- Statistics update in real-time

## Use Cases

### 1. **Add Missing Games**
If the Epic Games parser missed some games (due to parsing issues or website changes), you can manually add them.

### 2. **Add Games from Other Platforms**
Want to track games you own on Steam, GOG, or other platforms? Add them manually!

### 3. **Add Upcoming Games**
Add games you're interested in before they're released (TBA games).

### 4. **Build a Wishlist**
Add games you want to buy in the future to keep track of them.

## Example Workflow

```
1. Click "Add Game Manually"
   ↓
2. Search for "Cyberpunk 2077"
   ↓
3. Browse 5 results
   ↓
4. Click "Add to Library" on the correct one
   ↓
5. Wait ~3-5 seconds while metadata is fetched
   ↓
6. See success message with metadata counts
   ↓
7. Game appears in your library with full details!
```

## Tips

### 🎯 Search Tips
- Use the full game name for best results
- If you get too many results, add more specific terms
- Try different variations of the name if you don't see what you want

### 📝 Name Variations
Some games have different names in different regions:
- "Final Fantasy VII Remake" vs "FFVII Remake"
- "Grand Theft Auto V" vs "GTA V"
- "The Witcher 3: Wild Hunt" vs "Witcher 3"

Try the official full name first for most accurate results.

### ⚠️ Duplicate Check
The system checks by **exact title match**. If the Epic Games parser added "Cyberpunk 2077" and you try to add "Cyberpunk 2077: Phantom Liberty", it will allow it as they're different titles.

## Performance

- **Search**: ~1 second
- **Add + Metadata Fetch**: ~3-5 seconds per game
- **Metadata Included**: Same comprehensive data as RAWG sync

## Behind the Scenes

When you add a game manually, the app:

1. Searches RAWG API with your query
2. Returns top 5 results with preview info
3. When you click "Add to Library":
   - Adds game title to database
   - Fetches game details from RAWG
   - Fetches screenshots (endpoint: `/games/{id}/screenshots`)
   - Fetches achievements (endpoint: `/games/{id}/achievements`)
   - Fetches trailers (endpoint: `/games/{id}/movies`)
   - Fetches store links (endpoint: `/games/{id}/stores`)
   - Processes all metadata
   - Saves everything to local database

Same quality and completeness as automatic Epic Games sync + RAWG sync!

## Screenshot Preview

**Add Game Modal:**
```
┌─────────────────────────────────────────────┐
│  Add Game to Library                     ×  │
├─────────────────────────────────────────────┤
│  [Search for a game...           ]          │
│  [🔍 Search RAWG]                           │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ [Image] Cyberpunk 2077              │   │
│  │         📅 2020-12-10               │   │
│  │         ⭐ 4.21/5  🎮 86/100        │   │
│  │         RPG, Action                  │   │
│  │         [➕ Add to Library]          │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ [Image] The Witcher 3               │   │
│  │         📅 2015-05-18               │   │
│  │         ⭐ 4.66/5  🎮 92/100        │   │
│  │         RPG, Action                  │   │
│  │         [➕ Add to Library]          │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

Enjoy building your complete gaming library! 🎮
