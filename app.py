from flask import Flask, render_template, jsonify, request
from threading import Thread
import traceback
from src.database import get_all_games, get_game_count, add_game, update_game_metadata
from src.scrapers.epic_scraper import open_chrome_browser, start_parsing_now, close_chrome_browser
from src.sync.rawg_sync import sync_with_rawg, RAWGSyncer
from src.sync.igdb_sync import IGDBSyncer

app = Flask(__name__)

# Store task status and logs
task_status = {
    'scraping': {
        'running': False,
        'logs': [],
        'result': None,
        'chrome_open': False
    },
    'syncing': {
        'running': False,
        'logs': [],
        'result': None
    },
    'igdb': {
        'running': False,
        'logs': [],
        'result': None
    }
}

def scraping_callback(message):
    """Callback to receive scraping status updates."""
    task_status['scraping']['logs'].append(message)

def syncing_callback(message):
    """Callback to receive syncing status updates."""
    task_status['syncing']['logs'].append(message)

def run_open_chrome():
    """Open Chrome browser - Step 1."""
    try:
        task_status['scraping']['logs'] = []
        task_status['scraping']['result'] = None

        result = open_chrome_browser(callback=scraping_callback)

        if result['success']:
            task_status['scraping']['chrome_open'] = True

        task_status['scraping']['result'] = result

    except Exception as e:
        error_msg = f"Error opening Chrome: {str(e)}\n{traceback.format_exc()}"
        task_status['scraping']['logs'].append(error_msg)
        task_status['scraping']['result'] = {
            'success': False,
            'error': str(e)
        }

def run_start_parsing():
    """Start parsing - Step 2."""
    try:
        task_status['scraping']['running'] = True
        task_status['scraping']['logs'] = []
        task_status['scraping']['result'] = None

        result = start_parsing_now(callback=scraping_callback)

        task_status['scraping']['result'] = result
        task_status['scraping']['running'] = False

    except Exception as e:
        error_msg = f"Parsing error: {str(e)}\n{traceback.format_exc()}"
        task_status['scraping']['logs'].append(error_msg)
        task_status['scraping']['result'] = {
            'success': False,
            'error': str(e)
        }
        task_status['scraping']['running'] = False

def run_syncing(force_resync=False):
    """Run RAWG syncing in a background thread."""
    try:
        task_status['syncing']['running'] = True
        task_status['syncing']['logs'] = []
        task_status['syncing']['result'] = None

        result = sync_with_rawg(callback=syncing_callback, force_resync=force_resync)

        task_status['syncing']['result'] = result
        task_status['syncing']['running'] = False

    except Exception as e:
        error_msg = f"Syncing error: {str(e)}\n{traceback.format_exc()}"
        task_status['syncing']['logs'].append(error_msg)
        task_status['syncing']['result'] = {
            'success': False,
            'error': str(e)
        }
        task_status['syncing']['running'] = False

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/api/games', methods=['GET'])
def get_games():
    """Get all games from the database with optional filtering."""
    try:
        # Get filter parameters
        min_local_players = request.args.get('min_local_players', type=int)
        min_online_players = request.args.get('min_online_players', type=int)
        max_local_players = request.args.get('max_local_players', type=int)
        max_online_players = request.args.get('max_online_players', type=int)
        multiplayer_type = request.args.get('multiplayer_type', '')
        
        games = get_all_games()
        
        # Apply player count filters
        if min_local_players is not None:
            games = [g for g in games if g.get('rawg__local_players_max') and g.get('rawg__local_players_max') >= min_local_players]
        
        if max_local_players is not None:
            games = [g for g in games if g.get('rawg__local_players_max') and g.get('rawg__local_players_max') <= max_local_players]
            
        if min_online_players is not None:
            games = [g for g in games if g.get('rawg__online_players_max') and g.get('rawg__online_players_max') >= min_online_players]
            
        if max_online_players is not None:
            games = [g for g in games if g.get('rawg__online_players_max') and g.get('rawg__online_players_max') <= max_online_players]
        
        # Apply multiplayer type filter
        if multiplayer_type == 'local':
            games = [g for g in games if g.get('rawg__local_players_max') and g.get('rawg__local_players_max') > 1]
        elif multiplayer_type == 'online':
            games = [g for g in games if g.get('rawg__online_players_max') and g.get('rawg__online_players_max') > 1]
        elif multiplayer_type == 'singleplayer':
            games = [g for g in games if (not g.get('rawg__local_players_max') or g.get('rawg__local_players_max') <= 1) and 
                     (not g.get('rawg__online_players_max') or g.get('rawg__online_players_max') <= 1)]
        elif multiplayer_type == 'coop_local':
            games = [g for g in games if g.get('rawg__local_players_max') and g.get('rawg__local_players_max') >= 2]
        elif multiplayer_type == 'coop_online':
            games = [g for g in games if g.get('rawg__online_players_max') and g.get('rawg__online_players_max') >= 2]
        elif multiplayer_type == 'party_local':
            games = [g for g in games if g.get('rawg__local_players_max') and g.get('rawg__local_players_max') >= 4]
        elif multiplayer_type == 'party_online':
            games = [g for g in games if g.get('rawg__online_players_max') and g.get('rawg__online_players_max') >= 4]
        elif multiplayer_type == 'large_online':
            games = [g for g in games if g.get('rawg__online_players_max') and g.get('rawg__online_players_max') >= 10]

        return jsonify({
            'success': True,
            'games': games,
            'count': len(games)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get library statistics."""
    try:
        total_games = get_game_count()
        games = get_all_games()

        synced_games_rawg = sum(1 for g in games if g.get('rawg__synced'))
        synced_games_igdb = sum(1 for g in games if g.get('igdb__synced'))

        # Count games with local multiplayer
        local_mp_games = sum(1 for g in games
                           if g.get('rawg__local_players_max') and g.get('rawg__local_players_max') > 1)

        # Count games with online multiplayer
        online_mp_games = sum(1 for g in games
                            if g.get('rawg__online_players_max') and g.get('rawg__online_players_max') > 1)

        return jsonify({
            'success': True,
            'total_games': total_games,
            'synced_games_rawg': synced_games_rawg,
            'synced_games_igdb': synced_games_igdb,
            'unsynced_games_rawg': total_games - synced_games_rawg,
            'unsynced_games_igdb': total_games - synced_games_igdb,
            'local_multiplayer_games': local_mp_games,
            'online_multiplayer_games': online_mp_games
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/open-chrome', methods=['POST'])
def open_chrome():
    """Open Chrome browser - Step 1."""
    # Open Chrome in background thread
    thread = Thread(target=run_open_chrome)
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'message': 'Opening Chrome...'
    })

@app.route('/api/start-parsing', methods=['POST'])
def start_parsing():
    """Start parsing - Step 2."""
    if task_status['scraping']['running']:
        return jsonify({
            'success': False,
            'message': 'Parsing is already in progress'
        }), 400

    if not task_status['scraping']['chrome_open']:
        return jsonify({
            'success': False,
            'message': 'Chrome not open. Click "Open Chrome" first.'
        }), 400

    # Start parsing in background thread
    thread = Thread(target=run_start_parsing)
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'message': 'Parsing started'
    })

@app.route('/api/sync', methods=['POST'])
def start_syncing():
    """Start RAWG metadata syncing."""
    if task_status['syncing']['running']:
        return jsonify({
            'success': False,
            'message': 'Syncing is already in progress'
        }), 400

    # Get optional force_resync parameter
    data = request.get_json() or {}
    force_resync = data.get('force_resync', False)

    # Start syncing in background thread
    thread = Thread(target=run_syncing, args=(force_resync,))
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'message': 'Syncing started'
    })

@app.route('/api/status/<task_type>', methods=['GET'])
def get_task_status(task_type):
    """
    Get status of a background task.

    Args:
        task_type: 'scraping', 'syncing', or 'igdb'
    """
    if task_type not in ['scraping', 'syncing', 'igdb']:
        return jsonify({
            'success': False,
            'error': 'Invalid task type'
        }), 400

    status = task_status[task_type]

    return jsonify({
        'success': True,
        'running': status['running'],
        'logs': status['logs'],
        'result': status['result']
    })

@app.route('/api/clear-logs/<task_type>', methods=['POST'])
def clear_logs(task_type):
    """Clear logs for a specific task."""
    if task_type not in ['scraping', 'syncing', 'igdb']:
        return jsonify({
            'success': False,
            'error': 'Invalid task type'
        }), 400

    task_status[task_type]['logs'] = []
    task_status[task_type]['result'] = None

    return jsonify({
        'success': True,
        'message': f'{task_type.capitalize()} logs cleared'
    })

@app.route('/api/search-game', methods=['POST'])
def search_game():
    """Search for a game on RAWG."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query:
            return jsonify({
                'success': False,
                'error': 'No search query provided'
            }), 400

        # Use RAWG syncer to search
        syncer = RAWGSyncer()

        # Search for games (get top 5 results)
        import requests
        url = "https://api.rawg.io/api/games"
        params = {
            'key': syncer.api_key,
            'search': query,
            'page_size': 5
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for game in data.get('results', []):
            results.append({
                'id': game.get('id'),
                'name': game.get('name'),
                'released': game.get('released'),
                'background_image': game.get('background_image'),  # Direct from RAWG API
                'rating': game.get('rating'),
                'metacritic': game.get('metacritic'),
                'genres': [g['name'] for g in game.get('genres', [])],
                'platforms': [p['platform']['name'] for p in game.get('platforms', [])]
            })

        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/add-manual-game', methods=['POST'])
def add_manual_game():
    """Add a game manually with full RAWG metadata."""
    try:
        data = request.get_json()
        rawg_id = data.get('rawg_id')
        game_name = data.get('game_name')

        if not rawg_id or not game_name:
            return jsonify({
                'success': False,
                'error': 'Missing rawg_id or game_name'
            }), 400

        # Add game to database
        game_db_id, was_new = add_game(game_name)

        if not was_new:
            return jsonify({
                'success': False,
                'error': f'{game_name} is already in your library',
                'already_exists': True
            }), 400

        # Fetch full metadata from RAWG
        syncer = RAWGSyncer()

        # Get detailed information
        game_details = syncer.get_game_details(rawg_id)
        if not game_details:
            return jsonify({
                'success': False,
                'error': 'Could not fetch game details from RAWG'
            }), 500

        # Fetch additional data
        screenshots = syncer.get_game_screenshots(rawg_id)
        achievements = syncer.get_game_achievements(rawg_id)
        trailers = syncer.get_game_trailers(rawg_id)
        stores = syncer.get_game_stores(rawg_id)

        # Extract ALL metadata with rawg__ prefix
        metadata = syncer.extract_all_metadata(
            game_details,
            screenshots,
            achievements,
            trailers,
            stores
        )

        # Update database with RAWG data
        from src.database import update_game_with_rawg_data
        update_game_with_rawg_data(game_db_id, metadata)

        return jsonify({
            'success': True,
            'message': f'{game_name} added to your library!',
            'game_id': game_db_id,
            'metadata': {
                'screenshots_count': len(screenshots),
                'achievements_count': len(achievements),
                'trailers_count': len(trailers),
                'stores_count': len(stores)
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/print-game-info/<int:game_id>', methods=['POST'])
def print_game_info(game_id):
    """Print all game information to the terminal."""
    try:
        games = get_all_games()
        game = next((g for g in games if g['id'] == game_id), None)

        if not game:
            print(f"\n❌ Game with ID {game_id} not found")
            return jsonify({'success': False, 'error': 'Game not found'}), 404

        # Print to terminal with beautiful formatting
        print("\n" + "=" * 80)
        print(f"🎮 GAME DETAILS: {game.get('title', 'Unknown')}")
        print("=" * 80)

        # Basic Information
        print("\n📋 BASIC INFORMATION")
        print("-" * 80)
        print(f"  ID:              {game.get('id')}")
        print(f"  Title:           {game.get('title')}")
        print(f"  Original Name:   {game.get('rawg__name_original', 'N/A')}")
        print(f"  RAWG ID:         {game.get('rawg__id', 'N/A')}")
        print(f"  RAWG Slug:       {game.get('rawg__slug', 'N/A')}")
        print(f"  Epic ID:         {game.get('epic_id', 'N/A')}")

        # Alternative Names
        if game.get('rawg__alternative_names'):
            alt_names = game.get('rawg__alternative_names')
            if isinstance(alt_names, list) and len(alt_names) > 0:
                print(f"  Alt Names:       {', '.join(alt_names)}")

        # Dates
        print("\n📅 DATES")
        print("-" * 80)
        print(f"  Release Date:    {game.get('rawg__released', 'N/A')}")
        print(f"  TBA:             {'Yes' if game.get('rawg__tba') else 'No'}")
        print(f"  Added to DB:     {game.get('created_at', 'N/A')}")
        print(f"  Last Updated:    {game.get('updated_at', 'N/A')}")
        print(f"  RAWG Updated:    {game.get('rawg__updated', 'N/A')}")

        # Ratings
        print("\n⭐ RATINGS & REVIEWS")
        print("-" * 80)
        print(f"  RAWG Rating:     {game.get('rawg__rating', 'N/A')}/5")
        print(f"  Rating Top:      {game.get('rawg__rating_top', 'N/A')}")
        print(f"  Ratings Count:   {game.get('rawg__ratings_count', 'N/A')}")
        print(f"  Reviews Count:   {game.get('rawg__reviews_count', 'N/A')}")
        print(f"  Metacritic:      {game.get('rawg__metacritic', 'N/A')}/100")
        print(f"  Metacritic URL:  {game.get('rawg__metacritic_url', 'N/A')}")
        print(f"  ESRB Rating:     {game.get('rawg__esrb_rating', 'N/A')}")

        # Player Counts (CRITICAL FEATURE)
        print("\n👥 PLAYER COUNTS (LOCAL & ONLINE)")
        print("-" * 80)
        local_min = game.get('rawg__local_players_min', 'N/A')
        local_max = game.get('rawg__local_players_max', 'N/A')
        online_min = game.get('rawg__online_players_min', 'N/A')
        online_max = game.get('rawg__online_players_max', 'N/A')

        print(f"  Local Players:   {local_min} - {local_max}")
        print(f"  Online Players:  {online_min} - {online_max}")

        # Statistics
        print("\n📊 STATISTICS")
        print("-" * 80)
        print(f"  Playtime:        {game.get('rawg__playtime', 'N/A')} hours")
        print(f"  Added Count:     {game.get('rawg__added', 'N/A')} users")
        print(f"  Suggestions:     {game.get('rawg__suggestions_count', 'N/A')}")

        # Content Counts
        print("\n📸 CONTENT COUNTS")
        print("-" * 80)
        print(f"  Screenshots:     {game.get('rawg__screenshots_count', 'N/A')}")
        print(f"  Achievements:    {game.get('rawg__achievements_count', 'N/A')}")
        print(f"  Movies/Trailers: {game.get('rawg__movies_count', 'N/A')}")
        print(f"  Creators:        {game.get('rawg__creators_count', 'N/A')}")

        # Genres
        if game.get('rawg__genres'):
            genres = game.get('rawg__genres')
            if isinstance(genres, list):
                print("\n🎯 GENRES")
                print("-" * 80)
                genre_names = [g.get('name', g) if isinstance(g, dict) else g for g in genres]
                print(f"  {', '.join(genre_names)}")

        # Platforms
        if game.get('rawg__platforms'):
            platforms = game.get('rawg__platforms')
            if isinstance(platforms, list):
                print("\n💻 PLATFORMS")
                print("-" * 80)
                platform_names = [p.get('platform', p) if isinstance(p, dict) else p for p in platforms]
                print(f"  {', '.join(platform_names)}")

        if game.get('rawg__parent_platforms'):
            parent_plat = game.get('rawg__parent_platforms')
            if isinstance(parent_plat, list):
                platform_names = [p.get('platform', p) if isinstance(p, dict) else p for p in parent_plat]
                print(f"  Parent: {', '.join(platform_names)}")

        # Tags
        if game.get('rawg__tags'):
            tags = game.get('rawg__tags')
            if isinstance(tags, list) and len(tags) > 0:
                print("\n🏷️  TAGS")
                print("-" * 80)
                tag_names = [t.get('name', t) if isinstance(t, dict) else t for t in tags]
                print(f"  {', '.join(tag_names[:30])}")  # First 30 tags
                if len(tags) > 30:
                    print(f"  ... and {len(tags) - 30} more")

        # Developers
        if game.get('rawg__developers'):
            devs = game.get('rawg__developers')
            if isinstance(devs, list) and len(devs) > 0:
                print("\n👨‍💻 DEVELOPERS")
                print("-" * 80)
                for dev in devs:
                    print(f"  - {dev.get('name', 'Unknown')} (ID: {dev.get('id', 'N/A')})")

        # Publishers
        if game.get('rawg__publishers'):
            pubs = game.get('rawg__publishers')
            if isinstance(pubs, list) and len(pubs) > 0:
                print("\n🏢 PUBLISHERS")
                print("-" * 80)
                for pub in pubs:
                    print(f"  - {pub.get('name', 'Unknown')} (ID: {pub.get('id', 'N/A')})")

        # Screenshots
        if game.get('rawg__screenshots'):
            screens = game.get('rawg__screenshots')
            if isinstance(screens, list) and len(screens) > 0:
                print("\n📷 SCREENSHOTS")
                print("-" * 80)
                print(f"  Total: {len(screens)}")
                for i, screen in enumerate(screens[:5], 1):  # Show first 5
                    if isinstance(screen, dict):
                        print(f"  {i}. {screen.get('image', 'N/A')}")
                    else:
                        print(f"  {i}. {screen}")
                if len(screens) > 5:
                    print(f"  ... and {len(screens) - 5} more")

        # Achievements
        if game.get('rawg__achievements'):
            achs = game.get('rawg__achievements')
            if isinstance(achs, list) and len(achs) > 0:
                print("\n🏆 ACHIEVEMENTS")
                print("-" * 80)
                print(f"  Total: {len(achs)}")
                for i, ach in enumerate(achs[:5], 1):  # Show first 5
                    print(f"  {i}. {ach.get('name', 'Unknown')} - {ach.get('percent', 'N/A')}%")
                if len(achs) > 5:
                    print(f"  ... and {len(achs) - 5} more")

        # Trailers
        if game.get('rawg__trailers'):
            trails = game.get('rawg__trailers')
            if isinstance(trails, list) and len(trails) > 0:
                print("\n🎬 TRAILERS")
                print("-" * 80)
                for i, trailer in enumerate(trails, 1):
                    print(f"  {i}. {trailer.get('name', 'Unknown')}")
                    print(f"     Preview: {trailer.get('preview', 'N/A')}")

        # Stores
        if game.get('rawg__stores'):
            stores = game.get('rawg__stores')
            if isinstance(stores, list) and len(stores) > 0:
                print("\n🛒 WHERE TO BUY")
                print("-" * 80)
                for store in stores:
                    print(f"  - {store.get('store_name', 'Unknown')}")
                    print(f"    URL: {store.get('url', 'N/A')}")

        # Links
        print("\n🔗 LINKS")
        print("-" * 80)
        print(f"  Website:         {game.get('rawg__website', 'N/A')}")
        print(f"  Background Img:  {game.get('rawg__background_image', 'N/A')}")

        # Reddit
        if game.get('rawg__reddit_url'):
            print("\n💬 REDDIT COMMUNITY")
            print("-" * 80)
            print(f"  Subreddit:       {game.get('rawg__reddit_name', 'N/A')}")
            print(f"  URL:             {game.get('rawg__reddit_url', 'N/A')}")
            print(f"  Post Count:      {game.get('rawg__reddit_count', 'N/A')}")
            if game.get('rawg__reddit_description'):
                print(f"  Description:     {game.get('rawg__reddit_description', 'N/A')[:100]}...")

        # Description
        if game.get('rawg__description'):
            print("\n📖 DESCRIPTION")
            print("-" * 80)
            desc = game.get('rawg__description', '')
            # Print first 500 chars
            if len(desc) > 500:
                print(f"  {desc[:500]}...")
                print(f"  ... ({len(desc)} total characters)")
            else:
                print(f"  {desc}")

        # Sync Status
        print("\n✅ SYNC STATUS")
        print("-" * 80)
        print(f"  Synced with RAWG: {'Yes' if game.get('rawg__synced') else 'No'}")

        print("\n" + "=" * 80)
        print(f"✓ Complete information for: {game.get('title')}")
        print("=" * 80 + "\n")

        return jsonify({'success': True, 'message': 'Game info printed to terminal'})

    except Exception as e:
        print(f"\n❌ Error printing game info: {str(e)}\n")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sync-single-game/<int:game_id>', methods=['POST'])
def sync_single_game(game_id):
    """Sync a single game with RAWG or IGDB."""
    try:
        data = request.get_json()
        source = data.get('source', 'rawg').lower()

        # Get the game
        games = get_all_games()
        game = next((g for g in games if g['id'] == game_id), None)

        if not game:
            return jsonify({
                'success': False,
                'message': 'Game not found'
            }), 404

        game_title = game.get('title')

        if source == 'rawg':
            # Sync with RAWG
            from src.sync.rawg_sync import RAWGSyncer
            syncer = RAWGSyncer()

            # Search for the game
            search_results = syncer.search_game(game_title)

            if not search_results:
                return jsonify({
                    'success': False,
                    'message': f'Could not find "{game_title}" on RAWG'
                }), 404

            # Use first result
            rawg_game_id = search_results[0].get('id')

            # Fetch all metadata
            game_details = syncer.fetch_game_details(rawg_game_id)
            screenshots = syncer.fetch_screenshots(rawg_game_id)
            achievements = syncer.fetch_achievements(rawg_game_id)
            trailers = syncer.fetch_trailers(rawg_game_id)
            stores = syncer.fetch_stores(rawg_game_id)

            # Extract metadata
            metadata = syncer.extract_all_metadata(
                game_details, screenshots, achievements, trailers, stores
            )

            # Update database
            from src.database import update_game_with_rawg_data
            update_game_with_rawg_data(game_id, metadata)

            return jsonify({
                'success': True,
                'message': f'Successfully synced "{game_title}" with RAWG'
            })

        elif source == 'igdb':
            # Sync with IGDB - Print debug info to terminal
            print("\n" + "=" * 80)
            print(f"🎮 IGDB SYNC STARTED FOR: {game_title}")
            print("=" * 80)
            print(f"Game ID: {game_id}")
            print(f"Game Title: {game_title}")

            from src.sync.igdb_sync import IGDBSyncer
            from src.database import update_game_with_igdb_data

            syncer = IGDBSyncer()

            # Search for the game
            print(f"\n🔍 Searching IGDB for: {game_title}")
            search_result = syncer.search_game(game_title)

            if not search_result:
                print(f"❌ Could not find '{game_title}' on IGDB")
                print("=" * 80 + "\n")
                return jsonify({
                    'success': False,
                    'message': f'Could not find "{game_title}" on IGDB'
                }), 404

            # Get full details
            igdb_game_id = search_result.get('id')
            igdb_game_name = search_result.get('name')
            print(f"✓ Found match: {igdb_game_name} (IGDB ID: {igdb_game_id})")

            print(f"\n📥 Fetching complete game details from IGDB...")
            game_data = syncer.get_game_details(igdb_game_id)

            if not game_data:
                print("❌ Failed to fetch game data from IGDB")
                print("=" * 80 + "\n")
                return jsonify({
                    'success': False,
                    'message': 'Failed to fetch game data from IGDB'
                }), 500

            print("✓ Game data retrieved successfully")

            # Print some key details
            print(f"\n📊 Game Details:")
            print(f"  Name: {game_data.get('name', 'N/A')}")
            print(f"  IGDB ID: {game_data.get('id', 'N/A')}")
            print(f"  Summary: {game_data.get('summary', 'N/A')[:100]}..." if game_data.get('summary') else "  Summary: N/A")
            if game_data.get('genres'):
                genres = [g.get('name') if isinstance(g, dict) else g for g in game_data['genres']]
                print(f"  Genres: {', '.join(genres)}")
            if game_data.get('platforms'):
                platforms = [p.get('name') if isinstance(p, dict) else p for p in game_data['platforms']]
                print(f"  Platforms: {', '.join(platforms[:5])}")
            if game_data.get('rating'):
                print(f"  Rating: {game_data.get('rating', 0) / 20:.1f}/5.0")

            # Extract all metadata
            print(f"\n🔧 Extracting metadata...")
            metadata = syncer.extract_all_metadata(game_data)
            print(f"✓ Extracted {len(metadata)} metadata fields")

            # Update database
            print(f"\n💾 Updating database...")
            success = update_game_with_igdb_data(game_id, metadata)

            if success:
                print(f"✓ Database updated successfully!")
                print(f"\n✅ IGDB SYNC COMPLETE FOR: {game_title}")
                print("=" * 80 + "\n")
                return jsonify({
                    'success': True,
                    'message': f'Successfully synced "{game_title}" with IGDB'
                })
            else:
                print(f"❌ Failed to update database")
                print("=" * 80 + "\n")
                return jsonify({
                    'success': False,
                    'message': 'Failed to update database with IGDB data'
                }), 500

        else:
            return jsonify({
                'success': False,
                'message': f'Invalid source: {source}. Use "rawg" or "igdb"'
            }), 400

    except Exception as e:
        print(f"\n❌ Error syncing game: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/sync-igdb', methods=['POST'])
def sync_with_igdb():
    """
    Sync all unsynced games with IGDB API.
    Similar to RAWG sync but for IGDB.
    """
    if task_status['igdb']['running']:
        return jsonify({
            'success': False,
            'message': 'IGDB sync already running'
        }), 409

    def update_status(message: str):
        """Callback to update sync status."""
        task_status['igdb']['logs'].append(message)

    def run_sync():
        """Run the IGDB sync in background."""
        task_status['igdb']['running'] = True
        task_status['igdb']['logs'] = []

        try:
            from src.sync.igdb_sync import sync_all_games_with_igdb
            result = sync_all_games_with_igdb(callback=update_status)
            task_status['igdb']['result'] = result
        except Exception as e:
            task_status['igdb']['logs'].append(f"ERROR: {str(e)}")
            import traceback
            task_status['igdb']['logs'].append(traceback.format_exc())
        finally:
            task_status['igdb']['running'] = False

    # Start sync in background thread
    import threading
    sync_thread = threading.Thread(target=run_sync)
    sync_thread.daemon = True
    sync_thread.start()

    return jsonify({
        'success': True,
        'message': 'IGDB sync started'
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Epic Games Library Dashboard")
    print("=" * 60)
    print("\nStarting server at http://localhost:5000")
    print("\nIMPORTANT: Before syncing with RAWG, please:")
    print("1. Get a free API key at: https://rawg.io/apidocs")
    print("2. Edit rawg_sync.py and replace 'YOUR_RAWG_API_KEY_HERE' with your key")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
