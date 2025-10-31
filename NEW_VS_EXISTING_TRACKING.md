# New vs Existing Games Tracking

## What Changed

The parsing process now tracks and displays which games are NEW additions vs which are ALREADY IN DATABASE.

## Changes Made

### 1. database.py - `add_game()` function

**Before:**
```python
def add_game(title: str) -> int:
    # Returns just the game_id
    return game_id
```

**After:**
```python
def add_game(title: str) -> tuple[int, bool]:
    # Returns (game_id, was_new)
    # was_new = True if newly added
    # was_new = False if already existed
    return (game_id, was_new)
```

### 2. scraper_simple.py - Tracking

**Before:**
```python
saved_count = 0
for game_title in unique_games:
    add_game(game_title)
    saved_count += 1
    self._log(f"✓ {game_title}")
```

**After:**
```python
new_games_count = 0
existing_games_count = 0

for game_title in unique_games:
    game_id, was_new = add_game(game_title)

    if was_new:
        new_games_count += 1
        self._log(f"✓ [NEW] {game_title}")
    else:
        existing_games_count += 1
        self._log(f"✓ [EXISTS] {game_title}")
```

### 3. Improved Summary

**Before:**
```
SUCCESS!
Games found: 47
Games saved: 47
```

**After:**
```
SUCCESS!
Total games found: 47
NEW games added: 5
Already in database: 42
Total saved: 47
```

## Example Output

### Parsing Process

```
📄 Page 1...
   Found 10 games
📄 Page 2...
   Found 8 games
📄 Page 3...
   Found 12 games

✓ Last page reached!
✓ Total unique games: 28

Saving to database...
✓ [NEW] Five Nights at Freddy's: Into the Pit
✓ [EXISTS] Bendy and the Ink Machine
✓ [NEW] Samorost 3
✓ [EXISTS] Amnesia: The Bunker
✓ [NEW] Gravity Circuit
✓ [EXISTS] Nightingale
✓ [NEW] Eastern Exorcist
✓ [EXISTS] Project Zomboid
...

============================================================
SUCCESS!
============================================================
Total games found: 28
NEW games added: 5
Already in database: 23
Total saved: 28
```

## What Each Label Means

- **[NEW]**: This game was just added to your database (first time seeing it)
- **[EXISTS]**: This game was already in your database (you've scraped it before)

## Benefits

1. **See new discoveries** - Instantly know which games are new additions
2. **Track progress** - Know if you've already scraped most of your library
3. **Useful for re-running** - If you run the scraper again, you'll see how many games you already have
4. **Better insights** - Understand the composition of your scraping results

## When Running Multiple Times

**First Run:**
```
Total games found: 50
NEW games added: 50
Already in database: 0
```

**Second Run (after adding more games to Epic):**
```
Total games found: 52
NEW games added: 2
Already in database: 50
```

This clearly shows you added 2 new games to your Epic library since last time!
