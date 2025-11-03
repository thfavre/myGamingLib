# Epic Games Library Dashboard

A local web application that displays your complete Epic Games library with rich metadata from RAWG API.

<img width="2036" height="1018" alt="image" src="https://github.com/user-attachments/assets/baef49ee-b1d5-403e-ac26-ec9e91d214e8" />


## Features

- Parse Epic Games library using Chrome profile (avoids CAPTCHA)
- Add games manually from RAWG database (350,000+ games)
- Sync comprehensive metadata: ratings, screenshots, achievements, player counts, trailers
- Rich dashboard to browse, search, and filter your library
- Local SQLite storage

## Quick Start

1. **Install dependencies**:
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

2. **Setup RAWG API Key**:
   - Get free API key at https://rawg.io/apidocs
   - Copy `.env.example` to `.env`
   - Add your API key to `.env`

3. **Run the app**:
```bash
python app.py
```

4. **Open browser**: Navigate to http://localhost:5000

5. **Parse Epic Games**:
   - Click "Parse Epic Games"
   - Log into Epic if needed
   - Click "Continue" when ready
   - Games auto-parsed and saved

6. **Sync metadata**: Click "Sync with RAWG" to fetch full metadata

## Project Structure

```
myGamingLib/
├── src/                      # Source code
│   ├── scrapers/             # Epic Games scraper
│   ├── sync/                 # RAWG & IGDB API sync
│   ├── database.py           # Database operations
│   └── app.py                # Flask application (temp location)
├── static/                   # Frontend assets (CSS, JS)
├── templates/                # HTML templates
├── docs/                     # Documentation
│   ├── README.md             # Detailed documentation
│   ├── user-guide.md         # Usage guide
│   └── features/             # Feature-specific docs
├── scripts/                  # Utility scripts
├── data/                     # Database storage
├── .env                      # Environment variables (API keys)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Documentation

- [Full Documentation](docs/README.md) - Complete installation and usage guide
- [User Guide](docs/user-guide.md) - Step-by-step workflows
- [Manual Game Addition](docs/features/manual-game-addition.md) - Adding games manually
- [RAWG Sync Details](docs/features/rawg-sync.md) - Metadata sync information
- [Terminal Info Feature](docs/features/terminal-info.md) - Game information display

## Technologies

- **Backend**: Flask, SQLite
- **Scraper**: Selenium with undetected-chromedriver
- **APIs**: RAWG Video Games Database, IGDB (in development)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3

## Troubleshooting

**CAPTCHA issues**: The app uses Chrome Profile Method to avoid CAPTCHA. Make sure:
- You're logged into Epic in Chrome before running
- Chrome is completely closed when starting the scraper

**Database not found**: The database is now in `data/epic_games_library.db`

**Import errors**: Make sure you're in the project root when running `python app.py`

See [Full Documentation](docs/README.md) for more troubleshooting tips.

## License

Personal project for managing your own game library. Use responsibly and respect Epic Games and RAWG API terms of service.
