# Epic Gaming Library

A modern web application for managing and exploring your Epic Games library with rich metadata from multiple gaming databases.

![Epic Gaming Library](https://github.com/user-attachments/assets/baef49ee-b1d5-403e-ac26-ec9e91d214e8)

## ✨ Features

### Core Functionality
- **Automatic Epic Games Parsing** - Import your entire Epic Games library automatically
- **Manual Game Addition** - Add games from any platform using RAWG database search
- **Dual Metadata Sources** - Sync with both RAWG and IGDB for comprehensive game information
  <img width="366" height="313" alt="image" src="https://github.com/user-attachments/assets/6900ec67-0e03-4714-8c79-f03bc24a7e14" />

- **Rich Game Data** - Ratings, screenshots, achievements, player counts, trailers, genres, and more

### User Interface
- **Modern Dashboard** - Clean, responsive interface with dark theme
- **Advanced Filtering** - Filter by genre, player count (local/online), and more
- **Real-time Search** - Instant filtering as you type
- **Detailed Game Views** - Modal popups with comprehensive game information
- **Statistics Overview** - Track your library size and sync status

### Data Management
- **Local SQLite Database** - All data stored locally for privacy and speed
- **Automatic Syncing** - Keep metadata up-to-date with external APIs
- **Export Capabilities** - Access your data programmatically

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Setup API Keys

#### RAWG API (Required)
1. Get a free API key at [RAWG.io](https://rawg.io/apidocs)
2. Copy `.env.example` to `.env`
3. Add your RAWG API key to `.env`:
   ```
   RAWG_API_KEY=your_rawg_api_key_here
   ```

#### IGDB API (Optional but Recommended)
1. Create account at [Twitch Developers](https://dev.twitch.tv/console)
2. Create a new application to get Client ID and Secret
3. Add IGDB credentials to `.env`:
   ```
   IGDB_CLIENT_ID=your_client_id_here
   IGDB_CLIENT_SECRET=your_client_secret_here
   ```

### 3. Run the Application
```bash
python app.py
```

### 4. Access the Dashboard
Open your browser and navigate to: **http://localhost:5000**

## 📖 How to Use

### Initial Setup
1. **Parse Epic Games Library**
   - Click "Parse Epic Games" button
   - Chrome will open automatically
   - Log into Epic Games if needed
   - Navigate to your library/purchases page
   - Click "Continue" in the web interface
   - Games will be automatically parsed and saved

2. **Sync Metadata**
   - Click "Sync with RAWG" to fetch comprehensive game data
   - Optionally click "Sync with IGDB" for additional metadata
   - View progress in the status panels

### Managing Your Library
- **Search Games**: Use the search bar for instant filtering
- **Filter by Genre**: Select from automatically detected genres
- **Filter by Player Count**: Find single-player, local co-op, or online multiplayer games
- **Sort Options**: Sort by title, rating, release date, or player counts
- **Add Manual Games**: Search and add games from any platform
- **View Details**: Click any game for detailed information

### Data Sources
- **Epic Games**: Your owned games library
- **RAWG**: Ratings, screenshots, descriptions, genres, platforms
- **IGDB**: Additional metadata, alternative ratings, detailed information

## 🛠️ Technical Details

### Built With
- **Backend**: Python Flask
- **Frontend**: Alpine.js, Modern CSS
- **Database**: SQLite
- **APIs**: RAWG, IGDB, Epic Games (web scraping)

### File Structure
```
├── app.py                 # Main Flask application
├── src/                   # Source code modules
│   ├── database.py        # Database operations
│   ├── scrapers/          # Epic Games scraping
│   └── sync/              # API synchronization
├── static/                # Frontend assets
│   ├── css/               # Modular stylesheets
│   └── js/                # JavaScript components
├── templates/             # HTML templates
└── data/                  # SQLite database storage
```

## 🔒 Privacy & Security

- **Local Storage**: All data stored locally on your machine
- **No Data Sharing**: Your game library information never leaves your computer
- **API Compliance**: Respects rate limits and terms of service for all APIs
- **Secure Scraping**: Uses legitimate web automation, no account compromise

## 🤝 Contributing

This is a personal project for managing your own game library. Feel free to fork and modify for your own use.

## ⚖️ License

Personal use project. Please respect the terms of service for Epic Games, RAWG, and IGDB APIs when using this software.
