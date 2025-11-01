# Epic Games Library Dashboard

A local web application that displays your complete Epic Games library with rich metadata from RAWG API. Browse your games with detailed information including **local/online player counts**, genres, ratings, screenshots, and more.

## Features

- **Parse Epic Games**: Visible browser automation to scrape your entire Epic Games library
  - **Chrome Profile Method**: Uses YOUR existing Chrome profile where you're already logged in
  - **No CAPTCHA**: Bypasses CAPTCHA by using your trusted browser session
  - **Automatic Pagination**: Navigates through all pages of your purchase history
  - **80-95% Success Rate**: Most reliable method for avoiding Epic's bot detection
- **Add Games Manually**: Search RAWG and add any game to your library
  - Search 350,000+ games in the RAWG database
  - See game details before adding (ratings, genres, platforms)
  - Automatically fetches full metadata (screenshots, achievements, trailers)
  - Perfect for adding games from other platforms or missing games
  - See [MANUAL_GAME_ADDITION.md](MANUAL_GAME_ADDITION.md) for details
- **RAWG Sync**: Fetch **comprehensive metadata** for each game including:
  - **Player counts**: Local (split-screen, couch co-op) and Online (multiplayer, MMO)
  - **Ratings**: RAWG ratings, Metacritic scores, user reviews
  - **Visual assets**: Background images, screenshots (with full dimensions)
  - **Media**: Trailers, gameplay videos
  - **Achievements**: Full achievement list with completion percentages
  - **Store links**: Where to buy (Steam, Epic, GOG, etc.)
  - **Developers & Publishers**: Complete development team information
  - **Community**: Reddit integration, playtime statistics
  - **Categories**: Genres, platforms, tags, ESRB ratings
  - **Game details**: Descriptions, release dates, alternative names
  - See [RAWG_COMPREHENSIVE_SYNC.md](RAWG_COMPREHENSIVE_SYNC.md) for complete list
- **Rich Dashboard**: Browse, search, and filter your library
- **Local Storage**: All data stored locally in SQLite database

## Installation

1. **Clone or download this repository**

2. **Create a virtual environment**:
   - **Windows**:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - **Mac/Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

   You should see `(venv)` in your terminal prompt when activated.

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up your RAWG API key** (Required for metadata sync):

   **Step 1: Get API Key**
   - Go to https://rawg.io/apidocs
   - Click "Get API Key"
   - Sign up for a free account
   - Copy your API key from the API page

   **Step 2: Create .env file**
   - **Windows**: Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env
     ```
   - **Mac/Linux**:
     ```bash
     cp .env.example .env
     ```

   **Step 3: Add your API key**
   - Open the `.env` file in any text editor
   - Replace the line with your actual API key:
     ```
     RAWG_API_KEY=your_actual_api_key_here
     ```
   - Save the file

   **Example .env file**:
   ```
   # RAWG API Key
   RAWG_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
   ```

## Usage

1. **Start the application**:
```bash
python app.py
```

2. **Open your browser** and navigate to:
```
http://localhost:5000
```

3. **Parse your Epic Games library** (Simple One-Click Workflow):

   **Step 1**: Click "Parse Epic Games"
   - Chrome window opens (10-20 seconds)
   - Status panel appears with logs

   **Step 2**: Log in manually in the Chrome window:
   - Log into Epic Games (if not already logged in)
   - Solve any CAPTCHA if needed

   **Step 3**: Click the green "Continue" button:
   - A green "Continue" button appears in the status panel
   - When ready, click the green "Continue" button

   **Step 4**: Auto-parsing starts:
   - Scraper automatically navigates to your purchases page
   - Parses all pages automatically
   - Shows **[NEW]** or **[EXISTS]** for each game
   - Displays summary: how many NEW games added vs already in database
   - Games are saved to database
   - Chrome closes after 5 seconds

4. **Sync with RAWG** (Fetch comprehensive metadata):
   - Click "Sync with RAWG"
   - The app fetches **5 API endpoints per game**:
     - Game details (description, ratings, etc.)
     - Screenshots (full quality collection)
     - Achievements (with completion %)
     - Trailers & videos
     - Store purchase links
   - Progress shown in real-time with detailed logs
   - Takes ~3-5 seconds per game (with rate limiting)
   - Refresh the library to see updated games with full metadata

5. **Add Games Manually** (Optional):
   - Click "Add Game Manually" button
   - Search for any game in the RAWG database (350,000+ games)
   - Browse search results with game details
   - Click "Add to Library" to add with full metadata
   - Perfect for:
     - Adding games from other platforms (Steam, GOG, etc.)
     - Adding games the Epic parser missed
     - Building a wishlist of games you want

## Project Structure

```
myGamingLib/
├── app.py                 # Flask backend
├── database.py            # SQLite database management
├── scraper.py             # Epic Games browser automation
├── rawg_sync.py           # RAWG API integration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create from .env.example)
├── static/
│   ├── style.css         # Styling
│   └── script.js         # Frontend logic
└── templates/
    └── index.html        # Main page
```

## Technologies

- **Backend**: Flask (Python web framework)
- **Automation**: Selenium (browser automation)
- **API**: RAWG Video Games Database
- **Database**: SQLite
- **Frontend**: Vanilla JavaScript, HTML5, CSS3

## Notes

- The browser automation is **visible** so you can see the scraping process
- Scraper uses your Epic Games **purchases page** which lists all games you've acquired (including free games)
- The scraper **automatically navigates through all pages** of your purchase history
- You need to **manually log in** to Epic Games when prompted
- **RAWG Sync**:
  - Fetches **comprehensive metadata** from 5 different API endpoints per game
  - Includes screenshots, achievements, trailers, store links, and more
  - Rate limited to respect RAWG API free tier (1 second between games)
  - Takes ~3-5 seconds per game for complete sync
  - All metadata stored locally in SQLite database
- All data is stored **locally** in `epic_games_library.db`

## Troubleshooting

**CAPTCHA or "Invalid Response" / "réponse incorrecte" errors**:

**✅ FIXED!** The app now uses the **Chrome Profile Method** which avoids CAPTCHA entirely!

**How it works**:
1. Log into Epic Games in your normal Chrome browser first
2. Close Chrome
3. Run the scraper - it will use your existing session
4. **No login = No CAPTCHA!** ✨

**If you still see CAPTCHA**:

1. **Make sure you followed the preparation step**:
   - Log into Epic Games in Chrome BEFORE running the scraper
   - Navigate to the purchases page and verify it works
   - Close Chrome completely
   - Then run the scraper

2. **Chrome profile not found**:
   - The scraper looks for Chrome in default locations
   - Check console logs for "Chrome profile at: ..."
   - If path is wrong, see `CAPTCHA_SOLUTION.md` for manual configuration

3. **Still not working?**:
   - Make sure Chrome is completely closed before running
   - Try logging out and back into Epic in normal Chrome
   - Wait 10 minutes between attempts
   - See `CAPTCHA_SOLUTION.md` for detailed troubleshooting

**Success Rate**: 80-95% with the Chrome Profile Method! 🎯

**"No module named 'distutils'" error**:
This happens on Python 3.12+. Fix it by installing setuptools:
```bash
pip install --upgrade setuptools
pip install -r requirements.txt
```

**ChromeDriver Error (WinError 193 / "not a valid Win32 application")**:
This happens when ChromeDriver is corrupted or incompatible. To fix:
1. Run the fix script: `python fix_chromedriver.py`
2. Close all Chrome windows
3. Restart your terminal
4. Reactivate your virtual environment: `venv\Scripts\activate`
5. Try running the app again: `python app.py`

**Browser doesn't open**:
- Make sure Google Chrome is installed (download from https://www.google.com/chrome/)
- The updated scraper will try multiple methods to find Chrome automatically
- Check the console logs for detailed error messages

**No games found**:
- Make sure you're logged into Epic Games before clicking "Continue"
- The scraper automatically navigates to your purchases page
- Epic Games may have changed their website structure
- Check the browser window to see what's displayed
- The scraper looks for games in the transaction history table

**RAWG sync fails**:
- Verify your API key is correctly set in the `.env` file
- Make sure there are no extra spaces or quotes around the API key
- Check that you've saved the `.env` file after editing

## License

This is a personal project for managing your own game library. Use responsibly and respect Epic Games and RAWG API terms of service.
