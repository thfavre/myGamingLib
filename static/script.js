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

    // Print game info to terminal
    printGameInfoToTerminal(gameId);

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

    // Screenshots section
    const screenshots = game.screenshots && game.screenshots.length > 0 ?
        `<div class="game-detail-section">
            <h3>📷 Screenshots (${game.screenshots.length})</h3>
            <div class="screenshots-grid">
                ${game.screenshots.map(screenshot => {
                    const imageUrl = typeof screenshot === 'object' ? screenshot.image : screenshot;
                    return `<img src="${imageUrl}" alt="Screenshot" class="screenshot" onclick="window.open('${imageUrl}', '_blank')">`;
                }).join('')}
            </div>
        </div>` : '';

    // Achievements section
    const achievements = game.achievements && game.achievements.length > 0 ?
        `<div class="game-detail-section">
            <h3>🏆 Achievements (${game.achievements.length})</h3>
            <div class="achievements-grid" id="achievements-${game.id}">
                ${game.achievements.slice(0, 5).map(ach => `
                    <div class="achievement-card">
                        <div class="achievement-name">${ach.name || 'Unknown'}</div>
                        <div class="achievement-percent">${ach.percent || 'N/A'}%</div>
                        ${ach.description ? `<div class="achievement-desc">${ach.description}</div>` : ''}
                    </div>
                `).join('')}
                ${game.achievements.length > 5 ? `
                    <div class="achievement-more">
                        <button class="expand-btn" onclick="expandAchievements(${game.id})">
                            +${game.achievements.length - 5} more achievements
                        </button>
                    </div>
                ` : ''}
            </div>
        </div>` : '';

    // Store links section
    const storeLinks = game.stores && game.stores.length > 0 ?
        `<div class="game-detail-section">
            <h3>🛒 Where to Buy</h3>
            <div class="store-links">
                ${game.stores.map(store => `
                    <a href="${store.url}" target="_blank" class="store-link">
                        <span class="store-name">${store.store_name || 'Game Store'}</span>
                        <span class="store-icon">🔗</span>
                    </a>
                `).join('')}
            </div>
        </div>` : '';

    // Tags section
    const tags = game.tags && game.tags.length > 0 ?
        `<div class="game-detail-section">
            <h3>🏷️ Tags</h3>
            <div class="tags-container" id="tags-${game.id}">
                ${game.tags.slice(0, 15).map(tag => `<span class="tag-pill">${tag}</span>`).join('')}
                ${game.tags.length > 15 ? `
                    <button class="tag-more expand-btn" onclick="expandTags(${game.id})">
                        +${game.tags.length - 15} more
                    </button>
                ` : ''}
            </div>
        </div>` : '';

    // Developers & Publishers
    const developers = game.developers && game.developers.length > 0 ?
        game.developers.map(dev => dev.name || 'Unknown').join(', ') : 'Unknown';
    
    const publishers = game.publishers && game.publishers.length > 0 ?
        game.publishers.map(pub => pub.name || 'Unknown').join(', ') : 'Unknown';

    // Trailers section
    const trailers = game.trailers && game.trailers.length > 0 ?
        `<div class="game-detail-section">
            <h3>🎬 Trailers & Videos (${game.trailers.length})</h3>
            <div class="trailers-grid">
                ${game.trailers.map(trailer => `
                    <div class="trailer-card">
                        ${trailer.preview ? `<img src="${trailer.preview}" alt="${trailer.name}" class="trailer-preview">` : ''}
                        <div class="trailer-name">${trailer.name || 'Video'}</div>
                    </div>
                `).join('')}
            </div>
        </div>` : '';

    detailDiv.innerHTML = `
        <div class="game-detail-header">
            <h2 class="game-detail-title">${game.title}</h2>
            <div class="game-detail-meta">
                <span class="meta-badge badge-rating">⭐ ${rating}/5</span>
                ${metacritic !== 'N/A' ? `<span class="meta-badge badge-rating">🎮 ${metacritic}/100</span>` : ''}
                <span class="meta-badge badge-date">📅 ${releaseDate}</span>
            </div>

            <!-- IGDB Sync Section -->
            <div style="margin: 20px 0; padding: 15px; background: rgba(76, 175, 80, 0.1); border-radius: 8px; border: 2px solid #4caf50;">
                <h3 style="margin-top: 0; color: #4caf50;">🎮 Sync with IGDB</h3>
                <p style="margin: 10px 0; font-size: 0.9em; color: #ccc;">Fetch detailed game information from the IGDB database</p>
                <button onclick="syncWithIGDB(${game.id}, '${game.title.replace(/'/g, "\\'")}', event)" class="btn" style="background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%); padding: 12px 24px; width: 100%;">
                    <span class="btn-icon">🔄</span> Sync with IGDB
                </button>
                <div id="igdbResponse-${game.id}" style="margin-top: 15px; display: none;">
                    <!-- IGDB response will be displayed here -->
                </div>
            </div>

        ${imageUrl ? `<img src="${imageUrl}" alt="${game.title}" class="game-detail-image">` : ''}

        <div class="game-detail-grid">
            <div class="game-detail-main">
                <div class="game-detail-section">
                    <h3>📖 Description</h3>
                    <div class="game-description">${description.replace(/\n/g, '<br>')}</div>
                </div>

                ${screenshots}
                ${achievements}
                ${trailers}
            </div>

            <div class="game-detail-sidebar">
                <div class="game-detail-section">
                    <h3>👥 Player Information</h3>
                    <div class="player-info-compact">
                        <div class="player-info-item">
                            <span class="player-label">Local:</span>
                            <span class="player-value">${localPlayersText}</span>
                        </div>
                        <div class="player-info-item">
                            <span class="player-label">Online:</span>
                            <span class="player-value">${onlinePlayersText}</span>
                        </div>
                    </div>
                </div>

                <div class="game-detail-section">
                    <h3>📊 Game Stats</h3>
                    <div class="game-stats">
                        ${game.ratings_count ? `<div class="stat-item"><span class="stat-label">Reviews:</span> <span class="stat-value">${game.ratings_count}</span></div>` : ''}
                        ${game.added_count ? `<div class="stat-item"><span class="stat-label">Players:</span> <span class="stat-value">${game.added_count}</span></div>` : ''}
                        ${game.playtime ? `<div class="stat-item"><span class="stat-label">Avg Playtime:</span> <span class="stat-value">${game.playtime}h</span></div>` : ''}
                        ${game.achievements_count ? `<div class="stat-item"><span class="stat-label">Achievements:</span> <span class="stat-value">${game.achievements_count}</span></div>` : ''}
                    </div>
                </div>

                <div class="game-detail-section">
                    <h3>ℹ️ Game Details</h3>
                    <div class="game-details-list">
                        <div class="detail-item">
                            <span class="detail-label">Genres:</span>
                            <span class="detail-value">${genres}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Platforms:</span>
                            <span class="detail-value">${platforms}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Developer:</span>
                            <span class="detail-value">${developers}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Publisher:</span>
                            <span class="detail-value">${publishers}</span>
                        </div>
                        ${game.esrb_rating ? `
                        <div class="detail-item">
                            <span class="detail-label">ESRB:</span>
                            <span class="detail-value">${game.esrb_rating}</span>
                        </div>` : ''}
                        ${game.website ? `
                        <div class="detail-item">
                            <span class="detail-label">Website:</span>
                            <a href="${game.website}" target="_blank" class="detail-link">Visit 🔗</a>
                        </div>` : ''}
                    </div>
                </div>

                ${storeLinks}
                ${tags}
            </div>
        </div>
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
    const addGameModal = document.getElementById('addGameModal');

    if (event.target === modal) {
        closeModal();
    }
    if (event.target === addGameModal) {
        closeAddGameModal();
    }
}

// ==================== MANUAL GAME ADDITION ====================

function openAddGameModal() {
    const modal = document.getElementById('addGameModal');
    modal.style.display = 'flex';
    document.getElementById('searchResults').innerHTML = '';
    document.getElementById('gameSearchInput').value = '';
    document.getElementById('searchStatus').style.display = 'none';
}

function closeAddGameModal() {
    const modal = document.getElementById('addGameModal');
    modal.style.display = 'none';
}

async function searchRAWG() {
    const query = document.getElementById('gameSearchInput').value.trim();

    if (!query) {
        alert('Please enter a game name to search');
        return;
    }

    const searchBtn = document.getElementById('searchGameBtn');
    const searchStatus = document.getElementById('searchStatus');
    const searchResults = document.getElementById('searchResults');

    // Disable button and show loading
    searchBtn.disabled = true;
    searchBtn.innerHTML = '<span class="btn-icon">⏳</span> Searching...';
    searchStatus.style.display = 'block';
    searchStatus.textContent = 'Searching RAWG database...';
    searchResults.innerHTML = '';

    try {
        const response = await fetch('/api/search-game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        if (data.success && data.results.length > 0) {
            searchStatus.style.display = 'none';
            displaySearchResults(data.results);
        } else {
            searchStatus.textContent = 'No games found. Try a different search term.';
            searchStatus.style.color = '#f5576c';
        }
    } catch (error) {
        console.error('Search error:', error);
        searchStatus.textContent = 'Error searching. Please try again.';
        searchStatus.style.color = '#f5576c';
    } finally {
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<span class="btn-icon">🔍</span> Search RAWG';
    }
}

function displaySearchResults(results) {
    const searchResults = document.getElementById('searchResults');
    searchResults.innerHTML = results.map(game => `
        <div class="search-result-card">
            ${game.background_image ?
                `<img src="${game.background_image}" alt="${game.name}" class="search-result-image">` :
                '<div class="search-result-image" style="background: rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center;">No Image</div>'
            }
            <div class="search-result-info">
                <div class="search-result-title">${game.name}</div>
                <div class="search-result-meta">
                    ${game.released ? `<span>📅 ${game.released}</span>` : ''}
                    ${game.rating ? `<span>⭐ ${game.rating}/5</span>` : ''}
                    ${game.metacritic ? `<span>🎮 ${game.metacritic}/100</span>` : ''}
                </div>
                ${game.genres && game.genres.length > 0 ?
                    `<div class="search-result-genres">${game.genres.join(', ')}</div>` :
                    ''
                }
                ${game.platforms && game.platforms.length > 0 ?
                    `<div style="font-size: 0.8em; color: #999; margin-top: 5px;">Platforms: ${game.platforms.slice(0, 4).join(', ')}${game.platforms.length > 4 ? '...' : ''}</div>` :
                    ''
                }
                <div class="search-result-actions">
                    <button class="btn-small btn-add" onclick="addGameToLibrary(${game.id}, '${game.name.replace(/'/g, "\\'")}')">
                        ➕ Add to Library
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

async function addGameToLibrary(rawgId, gameName) {
    const btn = event.target;
    btn.disabled = true;
    btn.innerHTML = '⏳ Adding...';

    try {
        const response = await fetch('/api/add-manual-game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                rawg_id: rawgId,
                game_name: gameName
            })
        });

        const data = await response.json();

        if (data.success) {
            btn.innerHTML = '✅ Added!';
            btn.style.background = 'linear-gradient(135deg, #4caf50 0%, #8bc34a 100%)';

            // Show success message
            alert(`${gameName} has been added to your library with full metadata!\n\n` +
                  `✅ ${data.metadata.screenshots_count} screenshots\n` +
                  `✅ ${data.metadata.achievements_count} achievements\n` +
                  `✅ ${data.metadata.trailers_count} trailers\n` +
                  `✅ ${data.metadata.stores_count} store links`);

            // Refresh library
            loadGames();
            loadStats();

            // Close modal after a delay
            setTimeout(() => {
                closeAddGameModal();
            }, 1500);
        } else {
            if (data.already_exists) {
                alert(`${gameName} is already in your library!`);
                btn.innerHTML = '✓ Already Added';
                btn.disabled = true;
            } else {
                alert(`Error: ${data.error}`);
                btn.disabled = false;
                btn.innerHTML = '➕ Add to Library';
            }
        }
    } catch (error) {
        console.error('Add game error:', error);
        alert('Error adding game. Please try again.');
        btn.disabled = false;
        btn.innerHTML = '➕ Add to Library';
    }
}

// Event listeners
document.getElementById('addManualBtn').addEventListener('click', openAddGameModal);
document.getElementById('searchGameBtn').addEventListener('click', searchRAWG);

// Allow Enter key to search
document.getElementById('gameSearchInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchRAWG();
    }
});

// ==================== PRINT GAME INFO TO TERMINAL ====================

async function printGameInfoToTerminal(gameId) {
    try {
        const game = allGames.find(g => g.id === gameId);
        if (!game) {
            console.error(`❌ Game with ID ${gameId} not found`);
            return;
        }

        // Print to browser console with beautiful formatting
        console.log("\n" + "=".repeat(80));
        console.log(`🎮 GAME DETAILS: ${game.title || 'Unknown'}`);
        console.log("=".repeat(80));

        // Basic Information
        console.log("\n📋 BASIC INFORMATION");
        console.log("-".repeat(80));
        console.log(`  ID:              ${game.id}`);
        console.log(`  Title:           ${game.title}`);
        console.log(`  Original Name:   ${game.name_original || 'N/A'}`);
        console.log(`  RAWG ID:         ${game.rawg_id || 'N/A'}`);
        console.log(`  RAWG Slug:       ${game.rawg_slug || 'N/A'}`);
        console.log(`  Epic ID:         ${game.epic_id || 'N/A'}`);

        // Alternative Names
        if (game.alternative_names && Array.isArray(game.alternative_names) && game.alternative_names.length > 0) {
            console.log(`  Alt Names:       ${game.alternative_names.join(', ')}`);
        }

        // Dates
        console.log("\n📅 DATES");
        console.log("-".repeat(80));
        console.log(`  Release Date:    ${game.release_date || 'N/A'}`);
        console.log(`  TBA:             ${game.tba ? 'Yes' : 'No'}`);
        console.log(`  Added to DB:     ${game.created_at || 'N/A'}`);
        console.log(`  Last Updated:    ${game.updated_at || 'N/A'}`);
        console.log(`  RAWG Updated:    ${game.updated_at_rawg || 'N/A'}`);

        // Ratings
        console.log("\n⭐ RATINGS & REVIEWS");
        console.log("-".repeat(80));
        console.log(`  RAWG Rating:     ${game.rating || 'N/A'}/5`);
        console.log(`  Rating Top:      ${game.rating_top || 'N/A'}`);
        console.log(`  Ratings Count:   ${game.ratings_count || 'N/A'}`);
        console.log(`  Reviews Count:   ${game.reviews_count || 'N/A'}`);
        console.log(`  Metacritic:      ${game.metacritic_score || 'N/A'}/100`);
        console.log(`  Metacritic URL:  ${game.metacritic_url || 'N/A'}`);
        console.log(`  ESRB Rating:     ${game.esrb_rating || 'N/A'}`);

        // Player Counts (CRITICAL FEATURE)
        console.log("\n👥 PLAYER COUNTS (LOCAL & ONLINE)");
        console.log("-".repeat(80));
        const localMin = game.local_players_min || 'N/A';
        const localMax = game.local_players_max || 'N/A';
        const onlineMin = game.online_players_min || 'N/A';
        const onlineMax = game.online_players_max || 'N/A';

        console.log(`  Local Players:   ${localMin} - ${localMax}`);
        console.log(`  Online Players:  ${onlineMin} - ${onlineMax}`);

        // Statistics
        console.log("\n📊 STATISTICS");
        console.log("-".repeat(80));
        console.log(`  Playtime:        ${game.playtime || 'N/A'} hours`);
        console.log(`  Added Count:     ${game.added_count || 'N/A'} users`);
        console.log(`  Suggestions:     ${game.suggestions_count || 'N/A'}`);

        // Content Counts
        console.log("\n📸 CONTENT COUNTS");
        console.log("-".repeat(80));
        console.log(`  Screenshots:     ${game.screenshots_count || 'N/A'}`);
        console.log(`  Achievements:    ${game.achievements_count || 'N/A'}`);
        console.log(`  Movies/Trailers: ${game.movies_count || 'N/A'}`);
        console.log(`  Creators:        ${game.creators_count || 'N/A'}`);

        // Genres
        if (game.genres && Array.isArray(game.genres)) {
            console.log("\n🎯 GENRES");
            console.log("-".repeat(80));
            console.log(`  ${game.genres.join(', ')}`);
        }

        // Platforms
        if (game.platforms && Array.isArray(game.platforms)) {
            console.log("\n💻 PLATFORMS");
            console.log("-".repeat(80));
            console.log(`  ${game.platforms.join(', ')}`);
        }

        if (game.parent_platforms && Array.isArray(game.parent_platforms)) {
            console.log(`  Parent: ${game.parent_platforms.join(', ')}`);
        }

        // Tags
        if (game.tags && Array.isArray(game.tags) && game.tags.length > 0) {
            console.log("\n🏷️  TAGS");
            console.log("-".repeat(80));
            console.log(`  ${game.tags.slice(0, 20).join(', ')}`);  // First 20 tags
            if (game.tags.length > 20) {
                console.log(`  ... and ${game.tags.length - 20} more`);
            }
        }

        // Developers
        if (game.developers && Array.isArray(game.developers) && game.developers.length > 0) {
            console.log("\n👨‍💻 DEVELOPERS");
            console.log("-".repeat(80));
            game.developers.forEach(dev => {
                console.log(`  - ${dev.name || 'Unknown'} (ID: ${dev.id || 'N/A'})`);
            });
        }

        // Publishers
        if (game.publishers && Array.isArray(game.publishers) && game.publishers.length > 0) {
            console.log("\n🏢 PUBLISHERS");
            console.log("-".repeat(80));
            game.publishers.forEach(pub => {
                console.log(`  - ${pub.name || 'Unknown'} (ID: ${pub.id || 'N/A'})`);
            });
        }

        // Screenshots
        if (game.screenshots && Array.isArray(game.screenshots) && game.screenshots.length > 0) {
            console.log("\n📷 SCREENSHOTS");
            console.log("-".repeat(80));
            console.log(`  Total: ${game.screenshots.length}`);
            game.screenshots.slice(0, 5).forEach((screen, i) => {  // Show first 5
                if (typeof screen === 'object' && screen.image) {
                    console.log(`  ${i + 1}. ${screen.image}`);
                } else {
                    console.log(`  ${i + 1}. ${screen}`);
                }
            });
            if (game.screenshots.length > 5) {
                console.log(`  ... and ${game.screenshots.length - 5} more`);
            }
        }

        // Achievements
        if (game.achievements && Array.isArray(game.achievements) && game.achievements.length > 0) {
            console.log("\n🏆 ACHIEVEMENTS");
            console.log("-".repeat(80));
            console.log(`  Total: ${game.achievements.length}`);
            game.achievements.slice(0, 5).forEach((ach, i) => {  // Show first 5
                console.log(`  ${i + 1}. ${ach.name || 'Unknown'} - ${ach.percent || 'N/A'}%`);
            });
            if (game.achievements.length > 5) {
                console.log(`  ... and ${game.achievements.length - 5} more`);
            }
        }

        // Trailers
        if (game.trailers && Array.isArray(game.trailers) && game.trailers.length > 0) {
            console.log("\n🎬 TRAILERS");
            console.log("-".repeat(80));
            game.trailers.forEach((trailer, i) => {
                console.log(`  ${i + 1}. ${trailer.name || 'Unknown'}`);
                console.log(`     Preview: ${trailer.preview || 'N/A'}`);
            });
        }

        // Stores
        if (game.stores && Array.isArray(game.stores) && game.stores.length > 0) {
            console.log("\n🛒 WHERE TO BUY");
            console.log("-".repeat(80));
            game.stores.forEach(store => {
                console.log(`  - ${store.store_name || 'Unknown'}`);
                console.log(`    URL: ${store.url || 'N/A'}`);
            });
        }

        // Links
        console.log("\n🔗 LINKS");
        console.log("-".repeat(80));
        console.log(`  Website:         ${game.website || 'N/A'}`);
        console.log(`  Background Img:  ${game.background_image || 'N/A'}`);
        console.log(`  Cover Image:     ${game.cover_image || 'N/A'}`);

        // Reddit
        if (game.reddit_url) {
            console.log("\n💬 REDDIT COMMUNITY");
            console.log("-".repeat(80));
            console.log(`  Subreddit:       ${game.reddit_name || 'N/A'}`);
            console.log(`  URL:             ${game.reddit_url || 'N/A'}`);
            console.log(`  Post Count:      ${game.reddit_count || 'N/A'}`);
            if (game.reddit_description) {
                console.log(`  Description:     ${game.reddit_description.substring(0, 100)}...`);
            }
        }

        // Description
        if (game.description) {
            console.log("\n📖 DESCRIPTION");
            console.log("-".repeat(80));
            const desc = game.description;
            // Print first 500 chars
            if (desc.length > 500) {
                console.log(`  ${desc.substring(0, 500)}...`);
                console.log(`  ... (${desc.length} total characters)`);
            } else {
                console.log(`  ${desc}`);
            }
        }

        // Sync Status
        console.log("\n✅ SYNC STATUS");
        console.log("-".repeat(80));
        console.log(`  Synced with RAWG: ${game.synced_with_rawg ? 'Yes' : 'No'}`);

        console.log("\n" + "=".repeat(80));
        console.log(`✓ Complete information for: ${game.title}`);
        console.log("=".repeat(80) + "\n");

        console.log(`Game info for "${game.title}" printed above. Check the browser console for details.`);

    } catch (error) {
        console.error('Error printing game info:', error);
    }
}

// ==================== IGDB SYNC FUNCTIONALITY ====================

async function syncWithIGDB(gameId, gameTitle, event) {
    // Prevent button from being clicked multiple times
    if (event) {
        event.target.disabled = true;
    }

    const responseDiv = document.getElementById(`igdbResponse-${gameId}`);
    responseDiv.style.display = 'block';
    responseDiv.innerHTML = '<p style="text-align: center; color: #4caf50;">⏳ Searching IGDB for "' + gameTitle + '"...</p>';

    try {
        const response = await fetch('/api/sync-igdb', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_title: gameTitle
            })
        });

        const data = await response.json();

        if (data.success) {
            // Format the response data nicely
            const gameData = data.data;

            let html = `
                <div style="background: #1a1a1a; padding: 20px; border-radius: 8px; border: 1px solid #4caf50;">
                    <h3 style="color: #4caf50; margin-top: 0;">✓ IGDB Data Retrieved Successfully!</h3>
                    <p style="color: #8bc34a; margin: 5px 0;">
                        <strong>Matched Game:</strong> ${data.game_name} (IGDB ID: ${data.igdb_id})
                    </p>

                    <div style="max-height: 500px; overflow-y: auto; font-family: monospace; font-size: 0.85em;">
            `;

            // Display all fields from the game data
            for (const [key, value] of Object.entries(gameData)) {
                let displayValue;

                if (value === null || value === undefined) {
                    displayValue = '<em style="color: #666;">N/A</em>';
                } else if (Array.isArray(value)) {
                    displayValue = `<span style="color: #8bc34a;">[Array: ${value.length} items]</span>`;
                    if (value.length > 0 && value.length <= 10) {
                        displayValue += `<br><span style="margin-left: 20px; color: #ccc;">${JSON.stringify(value, null, 2)}</span>`;
                    }
                } else if (typeof value === 'object') {
                    displayValue = `<span style="color: #8bc34a;">[Object]</span><br><span style="margin-left: 20px; color: #ccc;">${JSON.stringify(value, null, 2)}</span>`;
                } else if (typeof value === 'boolean') {
                    displayValue = `<span style="color: ${value ? '#4caf50' : '#f44336'};">${value}</span>`;
                } else if (typeof value === 'number') {
                    displayValue = `<span style="color: #ffc107;">${value}</span>`;
                } else {
                    displayValue = `<span style="color: #fff;">${value}</span>`;
                }

                html += `
                    <div style="margin-bottom: 10px; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 4px;">
                        <strong style="color: #4caf50;">${key}:</strong> ${displayValue}
                    </div>
                `;
            }

            html += `
                    </div>

                    <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #333;">
                        <p style="font-size: 0.9em; color: #999; margin: 0;">
                            📋 Complete game data from IGDB API displayed above.
                        </p>
                        <button onclick="closeIGDBResponse(${gameId})" class="btn" style="margin-top: 10px; background: #666;">
                            Close
                        </button>
                    </div>
                </div>
            `;

            responseDiv.innerHTML = html;
        } else {
            responseDiv.innerHTML = `
                <div style="background: rgba(244, 67, 54, 0.1); padding: 15px; border-radius: 8px; border: 1px solid #f44336;">
                    <h4 style="color: #f44336; margin-top: 0;">❌ Error</h4>
                    <p style="color: #ccc;">${data.error || 'Failed to sync with IGDB'}</p>
                    <p style="font-size: 0.85em; color: #999;">Make sure you have configured your IGDB credentials in the .env file.</p>
                    <button onclick="closeIGDBResponse(${gameId})" class="btn" style="margin-top: 10px; background: #666;">
                        Close
                    </button>
                </div>
            `;
        }
    } catch (error) {
        console.error('IGDB sync error:', error);
        responseDiv.innerHTML = `
            <div style="background: rgba(244, 67, 54, 0.1); padding: 15px; border-radius: 8px; border: 1px solid #f44336;">
                <h4 style="color: #f44336; margin-top: 0;">❌ Error</h4>
                <p style="color: #ccc;">Network error: ${error.message}</p>
                <button onclick="closeIGDBResponse(${gameId})" class="btn" style="margin-top: 10px; background: #666;">
                    Close
                </button>
            </div>
        `;
    } finally {
        // Re-enable the button
        if (event && event.target) {
            event.target.disabled = false;
        }
    }
}

function closeIGDBResponse(gameId) {
    const responseDiv = document.getElementById(`igdbResponse-${gameId}`);
    responseDiv.style.display = 'none';
    responseDiv.innerHTML = '';
}

// ==================== EXPAND FUNCTIONALITY ====================

function expandAchievements(gameId) {
    const game = allGames.find(g => g.id === gameId);
    if (!game || !game.achievements) return;

    const container = document.getElementById(`achievements-${gameId}`);
    
    // Replace the grid with all achievements
    container.innerHTML = game.achievements.map(ach => `
        <div class="achievement-card">
            <div class="achievement-name">${ach.name || 'Unknown'}</div>
            <div class="achievement-percent">${ach.percent || 'N/A'}%</div>
            ${ach.description ? `<div class="achievement-desc">${ach.description}</div>` : ''}
        </div>
    `).join('') + `
        <div class="achievement-more">
            <button class="expand-btn collapse-btn" onclick="collapseAchievements(${gameId})">
                Show less
            </button>
        </div>
    `;
}

function collapseAchievements(gameId) {
    const game = allGames.find(g => g.id === gameId);
    if (!game || !game.achievements) return;

    const container = document.getElementById(`achievements-${gameId}`);
    
    // Show only first 5 achievements again
    container.innerHTML = game.achievements.slice(0, 5).map(ach => `
        <div class="achievement-card">
            <div class="achievement-name">${ach.name || 'Unknown'}</div>
            <div class="achievement-percent">${ach.percent || 'N/A'}%</div>
            ${ach.description ? `<div class="achievement-desc">${ach.description}</div>` : ''}
        </div>
    `).join('') + `
        <div class="achievement-more">
            <button class="expand-btn" onclick="expandAchievements(${gameId})">
                +${game.achievements.length - 5} more achievements
            </button>
        </div>
    `;
}

function expandTags(gameId) {
    const game = allGames.find(g => g.id === gameId);
    if (!game || !game.tags) return;

    const container = document.getElementById(`tags-${gameId}`);
    
    // Show all tags
    container.innerHTML = game.tags.map(tag => `<span class="tag-pill">${tag}</span>`).join('') + `
        <button class="tag-more expand-btn collapse-btn" onclick="collapseTags(${gameId})">
            Show less
        </button>
    `;
}

function collapseTags(gameId) {
    const game = allGames.find(g => g.id === gameId);
    if (!game || !game.tags) return;

    const container = document.getElementById(`tags-${gameId}`);
    
    // Show only first 15 tags again
    container.innerHTML = game.tags.slice(0, 15).map(tag => `<span class="tag-pill">${tag}</span>`).join('') + `
        <button class="tag-more expand-btn" onclick="expandTags(${gameId})">
            +${game.tags.length - 15} more
        </button>
    `;
}
