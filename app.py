from flask import Flask, render_template, jsonify, request
from threading import Thread
import traceback
from database import get_all_games, get_game_count, add_game, update_game_metadata
from scraper_simple import open_chrome_browser, start_parsing_now, close_chrome_browser
from rawg_sync import sync_with_rawg, RAWGSyncer

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
    """Get all games from the database."""
    try:
        games = get_all_games()
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

        synced_games = sum(1 for g in games if g.get('synced_with_rawg'))

        # Count games with local multiplayer
        local_mp_games = sum(1 for g in games
                           if g.get('local_players_max') and g.get('local_players_max') > 1)

        # Count games with online multiplayer
        online_mp_games = sum(1 for g in games
                            if g.get('online_players_max') and g.get('online_players_max') > 1)

        return jsonify({
            'success': True,
            'total_games': total_games,
            'synced_games': synced_games,
            'unsynced_games': total_games - synced_games,
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
    Get status of a background task (scraping or syncing).

    Args:
        task_type: 'scraping' or 'syncing'
    """
    if task_type not in ['scraping', 'syncing']:
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
    if task_type not in ['scraping', 'syncing']:
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
                'background_image': game.get('background_image'),
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

        # Extract metadata
        metadata = syncer.extract_metadata(
            game_details,
            screenshots_data=screenshots,
            achievements_data=achievements,
            trailers_data=trailers,
            stores_data=stores
        )

        # Update database with metadata
        update_game_metadata(game_db_id, metadata)

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
        print(f"  Original Name:   {game.get('name_original', 'N/A')}")
        print(f"  RAWG ID:         {game.get('rawg_id', 'N/A')}")
        print(f"  RAWG Slug:       {game.get('rawg_slug', 'N/A')}")
        print(f"  Epic ID:         {game.get('epic_id', 'N/A')}")

        # Alternative Names
        if game.get('alternative_names'):
            alt_names = game.get('alternative_names')
            if isinstance(alt_names, list) and len(alt_names) > 0:
                print(f"  Alt Names:       {', '.join(alt_names)}")

        # Dates
        print("\n📅 DATES")
        print("-" * 80)
        print(f"  Release Date:    {game.get('release_date', 'N/A')}")
        print(f"  TBA:             {'Yes' if game.get('tba') else 'No'}")
        print(f"  Added to DB:     {game.get('created_at', 'N/A')}")
        print(f"  Last Updated:    {game.get('updated_at', 'N/A')}")
        print(f"  RAWG Updated:    {game.get('updated_at_rawg', 'N/A')}")

        # Ratings
        print("\n⭐ RATINGS & REVIEWS")
        print("-" * 80)
        print(f"  RAWG Rating:     {game.get('rating', 'N/A')}/5")
        print(f"  Rating Top:      {game.get('rating_top', 'N/A')}")
        print(f"  Ratings Count:   {game.get('ratings_count', 'N/A')}")
        print(f"  Reviews Count:   {game.get('reviews_count', 'N/A')}")
        print(f"  Metacritic:      {game.get('metacritic_score', 'N/A')}/100")
        print(f"  Metacritic URL:  {game.get('metacritic_url', 'N/A')}")
        print(f"  ESRB Rating:     {game.get('esrb_rating', 'N/A')}")

        # Player Counts (CRITICAL FEATURE)
        print("\n👥 PLAYER COUNTS (LOCAL & ONLINE)")
        print("-" * 80)
        local_min = game.get('local_players_min', 'N/A')
        local_max = game.get('local_players_max', 'N/A')
        online_min = game.get('online_players_min', 'N/A')
        online_max = game.get('online_players_max', 'N/A')

        print(f"  Local Players:   {local_min} - {local_max}")
        print(f"  Online Players:  {online_min} - {online_max}")

        # Statistics
        print("\n📊 STATISTICS")
        print("-" * 80)
        print(f"  Playtime:        {game.get('playtime', 'N/A')} hours")
        print(f"  Added Count:     {game.get('added_count', 'N/A')} users")
        print(f"  Suggestions:     {game.get('suggestions_count', 'N/A')}")

        # Content Counts
        print("\n📸 CONTENT COUNTS")
        print("-" * 80)
        print(f"  Screenshots:     {game.get('screenshots_count', 'N/A')}")
        print(f"  Achievements:    {game.get('achievements_count', 'N/A')}")
        print(f"  Movies/Trailers: {game.get('movies_count', 'N/A')}")
        print(f"  Creators:        {game.get('creators_count', 'N/A')}")

        # Genres
        if game.get('genres'):
            genres = game.get('genres')
            if isinstance(genres, list):
                print("\n🎯 GENRES")
                print("-" * 80)
                print(f"  {', '.join(genres)}")

        # Platforms
        if game.get('platforms'):
            platforms = game.get('platforms')
            if isinstance(platforms, list):
                print("\n💻 PLATFORMS")
                print("-" * 80)
                print(f"  {', '.join(platforms)}")

        if game.get('parent_platforms'):
            parent_plat = game.get('parent_platforms')
            if isinstance(parent_plat, list):
                print(f"  Parent: {', '.join(parent_plat)}")

        # Tags
        if game.get('tags'):
            tags = game.get('tags')
            if isinstance(tags, list) and len(tags) > 0:
                print("\n🏷️  TAGS")
                print("-" * 80)
                print(f"  {', '.join(tags[:20])}")  # First 20 tags
                if len(tags) > 20:
                    print(f"  ... and {len(tags) - 20} more")

        # Developers
        if game.get('developers'):
            devs = game.get('developers')
            if isinstance(devs, list) and len(devs) > 0:
                print("\n👨‍💻 DEVELOPERS")
                print("-" * 80)
                for dev in devs:
                    print(f"  - {dev.get('name', 'Unknown')} (ID: {dev.get('id', 'N/A')})")

        # Publishers
        if game.get('publishers'):
            pubs = game.get('publishers')
            if isinstance(pubs, list) and len(pubs) > 0:
                print("\n🏢 PUBLISHERS")
                print("-" * 80)
                for pub in pubs:
                    print(f"  - {pub.get('name', 'Unknown')} (ID: {pub.get('id', 'N/A')})")

        # Screenshots
        if game.get('screenshots'):
            screens = game.get('screenshots')
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
        if game.get('achievements'):
            achs = game.get('achievements')
            if isinstance(achs, list) and len(achs) > 0:
                print("\n🏆 ACHIEVEMENTS")
                print("-" * 80)
                print(f"  Total: {len(achs)}")
                for i, ach in enumerate(achs[:5], 1):  # Show first 5
                    print(f"  {i}. {ach.get('name', 'Unknown')} - {ach.get('percent', 'N/A')}%")
                if len(achs) > 5:
                    print(f"  ... and {len(achs) - 5} more")

        # Trailers
        if game.get('trailers'):
            trails = game.get('trailers')
            if isinstance(trails, list) and len(trails) > 0:
                print("\n🎬 TRAILERS")
                print("-" * 80)
                for i, trailer in enumerate(trails, 1):
                    print(f"  {i}. {trailer.get('name', 'Unknown')}")
                    print(f"     Preview: {trailer.get('preview', 'N/A')}")

        # Stores
        if game.get('stores'):
            stores = game.get('stores')
            if isinstance(stores, list) and len(stores) > 0:
                print("\n🛒 WHERE TO BUY")
                print("-" * 80)
                for store in stores:
                    print(f"  - {store.get('store_name', 'Unknown')}")
                    print(f"    URL: {store.get('url', 'N/A')}")

        # Links
        print("\n🔗 LINKS")
        print("-" * 80)
        print(f"  Website:         {game.get('website', 'N/A')}")
        print(f"  Background Img:  {game.get('background_image', 'N/A')}")
        print(f"  Cover Image:     {game.get('cover_image', 'N/A')}")

        # Reddit
        if game.get('reddit_url'):
            print("\n💬 REDDIT COMMUNITY")
            print("-" * 80)
            print(f"  Subreddit:       {game.get('reddit_name', 'N/A')}")
            print(f"  URL:             {game.get('reddit_url', 'N/A')}")
            print(f"  Post Count:      {game.get('reddit_count', 'N/A')}")
            if game.get('reddit_description'):
                print(f"  Description:     {game.get('reddit_description', 'N/A')[:100]}...")

        # Description
        if game.get('description'):
            print("\n📖 DESCRIPTION")
            print("-" * 80)
            desc = game.get('description', '')
            # Print first 500 chars
            if len(desc) > 500:
                print(f"  {desc[:500]}...")
                print(f"  ... ({len(desc)} total characters)")
            else:
                print(f"  {desc}")

        # Sync Status
        print("\n✅ SYNC STATUS")
        print("-" * 80)
        print(f"  Synced with RAWG: {'Yes' if game.get('synced_with_rawg') else 'No'}")

        print("\n" + "=" * 80)
        print(f"✓ Complete information for: {game.get('title')}")
        print("=" * 80 + "\n")

        return jsonify({'success': True, 'message': 'Game info printed to terminal'})

    except Exception as e:
        print(f"\n❌ Error printing game info: {str(e)}\n")
        return jsonify({'success': False, 'error': str(e)}), 500

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
