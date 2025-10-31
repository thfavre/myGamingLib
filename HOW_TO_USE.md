# ✅ HOW TO USE - SIMPLE GUIDE

## Exactly What You'll See:

### 1. Click "Parse Epic Games" Button

The main button at the top.

### 2. Chrome Opens + Status Panel Appears

**Chrome Window:** Opens to Epic Games homepage

**Status Panel:** Shows logs like:
```
Opening Chrome...
Starting Chrome (10-20 seconds)...
✓ Chrome opened!

NOW YOU DO:
1. Log into Epic Games (if not already logged in)
2. Click the green 'Continue' button when ready

The scraper will automatically navigate to your purchases page
and start parsing all your games.
```

### 3. Green Box with "Continue" Button Appears

After a few seconds, you'll see a **green highlighted box** in the status panel:

```
┌─────────────────────────────────────────────────────────┐
│ ✓ Chrome opened! Please log into Epic Games and        │
│   navigate to your purchases page.                     │
│                                                         │
│              [▶️ Continue]  (GREEN BUTTON)              │
└─────────────────────────────────────────────────────────┘
```

### 4. YOU Log In

In the Chrome window:
- Log into Epic Games (if not already logged in)
- Solve CAPTCHA if it appears

### 5. Click the Green "Continue" Button

**When you're ready and logged in**, click the green "Continue" button in the status panel.

The scraper will automatically navigate to your purchases page and start parsing.

### 6. Parsing Starts Automatically

The green box disappears and you see:
```
STARTING TO PARSE

Navigating to purchases page...
Current URL: https://www.epicgames.com/account/transactions/purchases
✓ You're on the purchases page!

📄 Page 1...
   Found 10 games
📄 Page 2...
   Found 10 games
✓ Last page reached!

Saving to database...
✓ [NEW] Five Nights at Freddy's
✓ [EXISTS] Bendy and the Ink Machine
✓ [NEW] Samorost 3
✓ [EXISTS] Amnesia: The Bunker
...

SUCCESS!
Total games found: 47
NEW games added: 5
Already in database: 42
Total saved: 47
```

**Note**:
- **[NEW]** = Game just added to your database (first time seeing it)
- **[EXISTS]** = Game was already in your database from previous scrapes


### 7. Done!

Chrome closes automatically after 5 seconds.

## Visual Flow:

```
Click "Parse Epic Games"
         ↓
Chrome Opens + Panel Shows
         ↓
GREEN "Continue" Button Appears
         ↓
YOU Log In Manually
         ↓
Click Green "Continue"
         ↓
Auto-Parse All Pages
         ↓
Done!
```

## Key Points:

✅ **ONE button** at the top: "Parse Epic Games"
✅ **Green Continue button** appears in the status panel (not at the top!)
✅ **You control** when parsing starts by clicking Continue
✅ **Clear visual cue** - green button in green box
✅ **Simple flow** - click, login, click continue, done!

## Screenshots of What You'll See:

**Top Buttons:**
```
[🎮 Parse Epic Games]  [🔄 Sync with RAWG]  [♻️ Refresh Library]
```

**Status Panel After Clicking Parse Epic Games:**
```
┌─────────────────────────────────────────────────────────┐
│ Epic Games Scraping                                  ✕  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─────────────────────────────────────────────────────┐│
│ │ ✓ Chrome opened! Please log into Epic Games and    ││
│ │   navigate to your purchases page.                 ││
│ │                                                     ││
│ │              [▶️ Continue]  (GREEN)                 ││
│ └─────────────────────────────────────────────────────┘│
│                                                         │
│ Opening Chrome...                                       │
│ Starting Chrome (10-20 seconds)...                      │
│ ✓ Chrome opened!                                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**After Clicking Continue:**
```
┌─────────────────────────────────────────────────────────┐
│ Epic Games Scraping                                  ✕  │
├─────────────────────────────────────────────────────────┤
│ STARTING TO PARSE                                       │
│ Current URL: https://...purchases                       │
│ ✓ You're on the purchases page!                         │
│                                                         │
│ 📄 Page 1...                                            │
│    Found 10 games                                       │
│ 📄 Page 2...                                            │
│    Found 10 games                                       │
│ ...                                                     │
└─────────────────────────────────────────────────────────┘
```

Perfect workflow! 🎉
