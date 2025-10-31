from flask import Flask, render_template, jsonify, request
from threading import Thread
import traceback
from database import get_all_games, get_game_count
from scraper_simple import open_chrome_browser, start_parsing_now, close_chrome_browser
from rawg_sync import sync_with_rawg

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
