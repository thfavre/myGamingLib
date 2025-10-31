// State
let allGames = [];
let filteredGames = [];
let currentGenres = new Set();

// Polling intervals
let scrapingPollInterval = null;
let syncingPollInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadGames();
    loadStats();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('parseEpicBtn').addEventListener('click', parseEpicGames);
    document.getElementById('continueParsingBtn').addEventListener('click', continueParsing);
    document.getElementById('syncBtn').addEventListener('click', startSyncing);
    document.getElementById('refreshBtn').addEventListener('click', () => {
        loadGames();
        loadStats();
    });
    document.getElementById('searchInput').addEventListener('input', filterGames);
    document.getElementById('genreFilter').addEventListener('change', filterGames);
    document.getElementById('playerFilter').addEventListener('change', filterGames);
    document.getElementById('sortBy').addEventListener('change', filterGames);
}

// Load games from API
async function loadGames() {
    try {
        const response = await fetch('/api/games');
        const data = await response.json();

        if (data.success) {
            allGames = data.games;
            extractGenres();
            filterGames();
        } else {
            console.error('Error loading games:', data.error);
            displayError('Failed to load games');
        }
    } catch (error) {
        console.error('Error loading games:', error);
        displayError('Failed to load games');
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        if (data.success) {
            document.getElementById('totalGames').textContent = data.total_games;
            document.getElementById('syncedGames').textContent = data.synced_games;
            document.getElementById('localMpGames').textContent = data.local_multiplayer_games;
            document.getElementById('onlineMpGames').textContent = data.online_multiplayer_games;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Extract unique genres for filter
function extractGenres() {
    currentGenres.clear();
    allGames.forEach(game => {
        if (game.genres) {
            game.genres.forEach(genre => currentGenres.add(genre));
        }
    });

    const genreFilter = document.getElementById('genreFilter');
    genreFilter.innerHTML = '<option value="">All Genres</option>';
    Array.from(currentGenres).sort().forEach(genre => {
        const option = document.createElement('option');
        option.value = genre;
        option.textContent = genre;
        genreFilter.appendChild(option);
    });
}

// Filter and sort games
function filterGames() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const genreFilter = document.getElementById('genreFilter').value;
    const playerFilter = document.getElementById('playerFilter').value;
    const sortBy = document.getElementById('sortBy').value;

    filteredGames = allGames.filter(game => {
        // Search filter
        if (searchTerm && !game.title.toLowerCase().includes(searchTerm)) {
            return false;
        }

        // Genre filter
        if (genreFilter && (!game.genres || !game.genres.includes(genreFilter))) {
            return false;
        }

        // Player filter
        if (playerFilter === 'local') {
            if (!game.local_players_max || game.local_players_max <= 1) {
                return false;
            }
        } else if (playerFilter === 'online') {
            if (!game.online_players_max || game.online_players_max <= 1) {
                return false;
            }
        } else if (playerFilter === 'singleplayer') {
            if ((game.local_players_max && game.local_players_max > 1) ||
                (game.online_players_max && game.online_players_max > 1)) {
                return false;
            }
        }

        return true;
    });

    // Sort
    filteredGames.sort((a, b) => {
        if (sortBy === 'title') {
            return a.title.localeCompare(b.title);
        } else if (sortBy === 'rating') {
            return (b.rating || 0) - (a.rating || 0);
        } else if (sortBy === 'release_date') {
            return (b.release_date || '').localeCompare(a.release_date || '');
        }
        return 0;
    });

    displayGames();
}

// Display games in grid
function displayGames() {
    const grid = document.getElementById('gamesGrid');

    if (filteredGames.length === 0) {
        grid.innerHTML = '<div class="loading">No games found. Click "Parse Epic Games" to get started!</div>';
        return;
    }

    grid.innerHTML = filteredGames.map(game => createGameCard(game)).join('');
}

// Create game card HTML
function createGameCard(game) {
    const hasSyncData = game.synced_with_rawg;
    const imageUrl = game.background_image || game.cover_image || '';
    const rating = game.rating ? game.rating.toFixed(1) : null;
    const releaseYear = game.release_date ? new Date(game.release_date).getFullYear() : null;

    const localPlayers = game.local_players_max > 1 ?
        `<span class="meta-badge badge-local">Local ${game.local_players_min}-${game.local_players_max}P</span>` : '';

    const onlinePlayers = game.online_players_max > 1 ?
        `<span class="meta-badge badge-online">Online ${game.online_players_min}-${game.online_players_max}P</span>` : '';

    const genres = game.genres && game.genres.length > 0 ?
        game.genres.slice(0, 3).map(g => `<span class="genre-tag">${g}</span>`).join('') : '';

    return `
        <div class="game-card ${!hasSyncData ? 'no-sync' : ''}" onclick="showGameDetail(${game.id})">
            ${imageUrl ? `<img src="${imageUrl}" alt="${game.title}" class="game-card-image">` :
                '<div class="game-card-image"></div>'}
            <div class="game-card-content">
                <h3 class="game-card-title">${game.title}</h3>
                <div class="game-card-meta">
                    ${rating ? `<span class="meta-badge badge-rating">★ ${rating}</span>` : ''}
                    ${releaseYear ? `<span class="meta-badge badge-date">${releaseYear}</span>` : ''}
                    ${localPlayers}
                    ${onlinePlayers}
                </div>
                <div class="game-card-genres">
                    ${genres}
                </div>
            </div>
        </div>
    `;
}

// Show game detail modal
function showGameDetail(gameId) {
    const game = allGames.find(g => g.id === gameId);
    if (!game) return;

    const modal = document.getElementById('gameModal');
    const detailDiv = document.getElementById('gameDetail');

    const imageUrl = game.background_image || game.cover_image || '';
    const rating = game.rating ? game.rating.toFixed(1) : 'N/A';
    const metacritic = game.metacritic_score || 'N/A';
    const releaseDate = game.release_date || 'Unknown';
    const platforms = game.platforms ? game.platforms.join(', ') : 'N/A';
    const genres = game.genres ? game.genres.join(', ') : 'N/A';
    const description = game.description || 'No description available.';

    const localPlayersText = game.local_players_max ?
        `${game.local_players_min || 1}-${game.local_players_max} Players` : 'N/A';
    const onlinePlayersText = game.online_players_max ?
        `${game.online_players_min || 1}-${game.online_players_max} Players` : 'N/A';

    const screenshots = game.screenshots && game.screenshots.length > 0 ?
        `<div class="game-detail-section">
            <h3>Screenshots</h3>
            <div class="screenshots-grid">
                ${game.screenshots.map(url => `<img src="${url}" alt="Screenshot" class="screenshot">`).join('')}
            </div>
        </div>` : '';

    detailDiv.innerHTML = `
        <div class="game-detail-header">
            <h2 class="game-detail-title">${game.title}</h2>
            <div class="game-detail-meta">
                <span class="meta-badge badge-rating">★ ${rating}</span>
                <span class="meta-badge badge-rating">Metacritic: ${metacritic}</span>
                <span class="meta-badge badge-date">${releaseDate}</span>
            </div>
        </div>

        ${imageUrl ? `<img src="${imageUrl}" alt="${game.title}" class="game-detail-image">` : ''}

        <div class="game-detail-section">
            <h3>Player Information (Critical Feature)</h3>
            <div class="player-info">
                <div class="player-info-box">
                    <h4>Local Multiplayer</h4>
                    <div class="player-count">${localPlayersText}</div>
                </div>
                <div class="player-info-box">
                    <h4>Online Multiplayer</h4>
                    <div class="player-count">${onlinePlayersText}</div>
                </div>
            </div>
        </div>

        <div class="game-detail-section">
            <h3>Description</h3>
            <p>${description}</p>
        </div>

        <div class="game-detail-section">
            <h3>Details</h3>
            <p><strong>Genres:</strong> ${genres}</p>
            <p><strong>Platforms:</strong> ${platforms}</p>
            ${game.esrb_rating ? `<p><strong>ESRB Rating:</strong> ${game.esrb_rating}</p>` : ''}
        </div>

        ${screenshots}
    `;

    modal.style.display = 'flex';
}

function closeModal() {
    document.getElementById('gameModal').style.display = 'none';
}

function closePanel(panelId) {
    document.getElementById(panelId).style.display = 'none';
}

// Parse Epic Games - opens Chrome and shows Continue button
async function parseEpicGames() {
    const btn = document.getElementById('parseEpicBtn');
    btn.disabled = true;
    btn.textContent = 'Opening Chrome...';

    try {
        const response = await fetch('/api/open-chrome', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            showPanel('scrapingPanel');
            startPolling('scraping');

            // Show the Continue button in the status panel
            setTimeout(() => {
                document.getElementById('continueButtonContainer').style.display = 'block';
            }, 2000); // Wait 2 seconds for Chrome to open

            btn.textContent = 'Chrome Opened ✓';
        } else {
            alert(data.message);
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">🎮</span> Parse Epic Games';
        }
    } catch (error) {
        console.error('Error opening Chrome:', error);
        alert('Failed to open Chrome');
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">🎮</span> Parse Epic Games';
    }
}

// Continue button clicked - start parsing
async function continueParsing() {
    const btn = document.getElementById('continueParsingBtn');
    btn.disabled = true;
    btn.textContent = 'Starting...';

    // Hide the continue button container
    document.getElementById('continueButtonContainer').style.display = 'none';

    try {
        const response = await fetch('/api/start-parsing', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            startPolling('scraping');
        } else {
            alert(data.message);
            // Show the continue button again
            document.getElementById('continueButtonContainer').style.display = 'block';
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">▶️</span> Continue';
        }
    } catch (error) {
        console.error('Error starting parsing:', error);
        alert('Failed to start parsing');
        // Show the continue button again
        document.getElementById('continueButtonContainer').style.display = 'block';
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">▶️</span> Continue';
    }
}

async function startSyncing() {
    const btn = document.getElementById('syncBtn');
    btn.disabled = true;
    btn.textContent = 'Syncing...';

    try {
        const response = await fetch('/api/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ force_resync: false })
        });
        const data = await response.json();

        if (data.success) {
            showPanel('syncingPanel');
            startPolling('syncing');
        } else {
            alert(data.message);
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">🔄</span> Sync with RAWG';
        }
    } catch (error) {
        console.error('Error starting sync:', error);
        alert('Failed to start sync');
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">🔄</span> Sync with RAWG';
    }
}

function showPanel(panelId) {
    document.getElementById(panelId).style.display = 'block';
}

function startPolling(taskType) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/api/status/${taskType}`);
            const data = await response.json();

            if (data.success) {
                updateLogs(taskType, data.logs);

                if (!data.running) {
                    clearInterval(interval);
                    taskComplete(taskType, data.result);
                }
            }
        } catch (error) {
            console.error(`Error polling ${taskType}:`, error);
        }
    }, 1000);

    if (taskType === 'scraping') {
        scrapingPollInterval = interval;
    } else {
        syncingPollInterval = interval;
    }
}

function updateLogs(taskType, logs) {
    const logsDiv = document.getElementById(`${taskType}Logs`);
    logsDiv.innerHTML = logs.map(log => `<p>${log}</p>`).join('');
    logsDiv.scrollTop = logsDiv.scrollHeight;
}

function taskComplete(taskType, result) {
    if (taskType === 'scraping') {
        // Reset the main button
        const btn = document.getElementById('parseEpicBtn');
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">🎮</span> Parse Epic Games';

        // Hide continue button
        document.getElementById('continueButtonContainer').style.display = 'none';

        // Reset continue button
        const continueBtn = document.getElementById('continueParsingBtn');
        continueBtn.disabled = false;
        continueBtn.innerHTML = '<span class="btn-icon">▶️</span> Continue';
    } else {
        const btn = document.getElementById('syncBtn');
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">🔄</span> Sync with RAWG';
    }

    if (result && result.success) {
        loadGames();
        loadStats();
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('gameModal');
    if (event.target === modal) {
        closeModal();
    }
}
