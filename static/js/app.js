/**
 * Main Alpine.js Application
 * Initializes Alpine.js and sets up the global game store
 */

// Wait for Alpine.js to be loaded
document.addEventListener('alpine:init', () => {
    console.log('Alpine.js initialized');

    // Global game store - manages all game-related state
    Alpine.store('games', {
        // State
        allGames: [],
        filteredGames: [],
        currentGame: null,
        stats: {
            total: 0,
            syncedRawg: 0,
            syncedIgdb: 0,
            localMp: 0,
            onlineMp: 0
        },
        genres: [],

        // Loading states
        isLoading: true,

        // Filters
        searchQuery: '',
        selectedGenre: '',
        selectedPlayerFilter: '',
        selectedLocalPlayers: '',
        selectedOnlinePlayers: '',
        selectedPlayerCount: '',
        sortBy: 'title',

        // Initialize the store
        async init() {
            await this.loadGames();
        },

        // Load all games from API
        async loadGames() {
            this.isLoading = true;
            try {
                const response = await fetch('/api/games');
                const data = await response.json();
                this.allGames = data.games || [];
                this.updateStats();
                this.extractGenres();
                this.applyFilters();

                // Trigger render after loading
                if (window.renderGames) {
                    window.renderGames();
                }
            } catch (error) {
                console.error('Failed to load games:', error);
            } finally {
                this.isLoading = false;
            }
        },

        // Update statistics
        updateStats() {
            const games = this.allGames;
            this.stats.total = games.length;
            this.stats.syncedRawg = games.filter(g => g.rawg__synced === 1 || g.rawg__synced === true).length;
            this.stats.syncedIgdb = games.filter(g => g.igdb__synced === 1 || g.igdb__synced === true).length;
            this.stats.localMp = games.filter(g => g.rawg__tags?.includes('Local Multiplayer') ||
                                                     g.rawg__tags?.includes('Local Co-Op')).length;
            this.stats.onlineMp = games.filter(g => g.rawg__tags?.includes('Online Co-Op') ||
                                                      g.rawg__tags?.includes('Multiplayer')).length;
        },

        // Extract unique genres from all games
        extractGenres() {
            const genreSet = new Set();
            this.allGames.forEach(game => {
                const genres = game.rawg__genres || [];
                genres.forEach(genre => {
                    const genreName = typeof genre === 'object' ? genre.name : genre;
                    if (genreName) genreSet.add(genreName);
                });
            });
            this.genres = Array.from(genreSet).sort();
        },

        // Apply all filters and sorting
        applyFilters() {
            let filtered = [...this.allGames];

            // Apply search filter
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase();
                filtered = filtered.filter(game =>
                    game.title?.toLowerCase().includes(query)
                );
            }

            // Apply genre filter
            if (this.selectedGenre) {
                filtered = filtered.filter(game => {
                    const genres = game.rawg__genres || [];
                    const genreNames = genres.map(g => typeof g === 'object' ? g.name : g);
                    return genreNames.includes(this.selectedGenre);
                });
            }

            // Apply player filter
            if (this.selectedPlayerFilter) {
                filtered = filtered.filter(game => {
                    const tags = game.rawg__tags || [];
                    if (this.selectedPlayerFilter === 'local') {
                        return tags.includes('Local Multiplayer') || tags.includes('Local Co-Op');
                    } else if (this.selectedPlayerFilter === 'online') {
                        return tags.includes('Online Co-Op') || tags.includes('Multiplayer');
                    } else if (this.selectedPlayerFilter === 'singleplayer') {
                        return tags.includes('Singleplayer');
                    }
                    return true;
                });
            }

            // Apply combined player count filter
            if (this.selectedPlayerCount) {
                if (this.selectedPlayerCount === '1') {
                    // Single player only
                    filtered = filtered.filter(game => {
                        const localMax = game.rawg__local_players_max;
                        const onlineMax = game.rawg__online_players_max;
                        return (!localMax || localMax === 1) && (!onlineMax || onlineMax === 1);
                    });
                } else if (this.selectedPlayerCount.startsWith('local_')) {
                    // Local multiplayer filter
                    const minPlayers = parseInt(this.selectedPlayerCount.split('_')[1]);
                    filtered = filtered.filter(game => {
                        const localMax = game.rawg__local_players_max;
                        return localMax && localMax >= minPlayers;
                    });
                } else if (this.selectedPlayerCount.startsWith('online_')) {
                    // Online multiplayer filter
                    const minPlayers = parseInt(this.selectedPlayerCount.split('_')[1]);
                    filtered = filtered.filter(game => {
                        const onlineMax = game.rawg__online_players_max;
                        return onlineMax && onlineMax >= minPlayers;
                    });
                }
            }

            // Apply local players filter
            if (this.selectedLocalPlayers) {
                const minPlayers = parseInt(this.selectedLocalPlayers);
                filtered = filtered.filter(game => {
                    const localMax = game.rawg__local_players_max;
                    if (minPlayers === 1) {
                        return !localMax || localMax === 1;
                    } else {
                        return localMax && localMax >= minPlayers;
                    }
                });
            }

            // Apply online players filter
            if (this.selectedOnlinePlayers) {
                const minPlayers = parseInt(this.selectedOnlinePlayers);
                filtered = filtered.filter(game => {
                    const onlineMax = game.rawg__online_players_max;
                    if (minPlayers === 1) {
                        return !onlineMax || onlineMax === 1;
                    } else {
                        return onlineMax && onlineMax >= minPlayers;
                    }
                });
            }

            // Apply sorting
            filtered.sort((a, b) => {
                if (this.sortBy === 'title') {
                    return (a.title || '').localeCompare(b.title || '');
                } else if (this.sortBy === 'rating') {
                    const ratingA = Formatters.calculateCombinedScore(a) || 0;
                    const ratingB = Formatters.calculateCombinedScore(b) || 0;
                    return ratingB - ratingA;
                } else if (this.sortBy === 'release_date') {
                    return (b.rawg__released || '').localeCompare(a.rawg__released || '');
                } else if (this.sortBy === 'local_players') {
                    return (b.rawg__local_players_max || 0) - (a.rawg__local_players_max || 0);
                } else if (this.sortBy === 'online_players') {
                    return (b.rawg__online_players_max || 0) - (a.rawg__online_players_max || 0);
                }
                return 0;
            });

            this.filteredGames = filtered;
        },

        // Set current game for detail view
        setCurrentGame(game) {
            this.currentGame = game;
        },

        // Refresh games list
        async refresh() {
            await this.loadGames();
        }
    });

    // Task status store - manages background task status
    Alpine.store('tasks', {
        scraping: {
            active: false,
            logs: [],
            waitingForContinue: false
        },
        syncingRawg: {
            active: false,
            logs: []
        },
        syncingIgdb: {
            active: false,
            logs: []
        },

        // Poll for task status
        pollTaskStatus() {
            setInterval(async () => {
                try {
                    const response = await fetch('/api/task_status');
                    const data = await response.json();

                    // Update scraping status
                    if (data.scraping) {
                        this.scraping.active = data.scraping.active;
                        this.scraping.logs = data.scraping.logs || [];
                        this.scraping.waitingForContinue = data.scraping.waiting_for_continue || false;
                    }

                    // Update RAWG sync status
                    if (data.syncing) {
                        this.syncingRawg.active = data.syncing.active;
                        this.syncingRawg.logs = data.syncing.logs || [];
                    }

                    // Update IGDB sync status
                    if (data.igdb) {
                        this.syncingIgdb.active = data.igdb.active;
                        this.syncingIgdb.logs = data.igdb.logs || [];
                    }
                } catch (error) {
                    console.error('Failed to poll task status:', error);
                }
            }, 2000); // Poll every 2 seconds
        },

        // Close task panel
        closePanel(panelName) {
            if (panelName === 'scraping') {
                this.scraping.active = false;
            } else if (panelName === 'syncingRawg') {
                this.syncingRawg.active = false;
            } else if (panelName === 'syncingIgdb') {
                this.syncingIgdb.active = false;
            }
        }
    });
});

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for Alpine.js to initialize
    // Alpine loads with 'defer', so we need to wait for it
    setTimeout(() => {
        initializeApp();
    }, 100);
});

/**
 * Initialize the application
 */
function initializeApp() {
    // Check if Alpine is available
    if (typeof Alpine === 'undefined') {
        console.error('Alpine.js not loaded yet, retrying...');
        setTimeout(initializeApp, 100);
        return;
    }

    // Initialize game store
    const gameStore = Alpine.store('games');
    if (gameStore) {
        gameStore.init();
    }

    // Start polling for task status
    const taskStore = Alpine.store('tasks');
    if (taskStore) {
        taskStore.pollTaskStatus();
    }

    // Initialize components
    TaskStatus.init();
    GameSearch.init();

    // Setup filter event listeners
    setupFilterListeners();

    // Initial render will be triggered by loadGames() in the store
}

/**
 * Setup filter event listeners
 */
function setupFilterListeners() {
    const gameStore = Alpine.store('games');

    // Search input
    document.getElementById('searchInput')?.addEventListener('input', (e) => {
        gameStore.searchQuery = e.target.value;
        gameStore.applyFilters();
        renderGames();
    });

    // Genre filter
    document.getElementById('genreFilter')?.addEventListener('change', (e) => {
        gameStore.selectedGenre = e.target.value;
        gameStore.applyFilters();
        renderGames();
    });

    // Player filter
    document.getElementById('playerFilter')?.addEventListener('change', (e) => {
        gameStore.selectedPlayerFilter = e.target.value;
        gameStore.applyFilters();
        renderGames();
    });

    // Combined Player Count filter
    document.getElementById('playerCountFilter')?.addEventListener('change', (e) => {
        gameStore.selectedPlayerCount = e.target.value;
        gameStore.applyFilters();
        renderGames();
    });

    // Local players filter
    document.getElementById('localPlayersFilter')?.addEventListener('change', (e) => {
        gameStore.selectedLocalPlayers = e.target.value;
        gameStore.applyFilters();
        renderGames();
    });

    // Online players filter
    document.getElementById('onlinePlayersFilter')?.addEventListener('change', (e) => {
        gameStore.selectedOnlinePlayers = e.target.value;
        gameStore.applyFilters();
        renderGames();
    });

    // Sort by
    document.getElementById('sortBy')?.addEventListener('change', (e) => {
        gameStore.sortBy = e.target.value;
        gameStore.applyFilters();
        renderGames();
    });

    // Clear button
    document.getElementById('clearFiltersBtn')?.addEventListener('click', () => {
        clearAllFilters();
    });
}

/**
 * Clear all filters
 */
function clearAllFilters() {
    const gameStore = Alpine.store('games');

    // Reset filter values
    document.getElementById('searchInput').value = '';
    document.getElementById('genreFilter').value = '';
    document.getElementById('playerFilter').value = '';
    document.getElementById('playerCountFilter').value = '';
    document.getElementById('sortBy').value = 'title';

    // Reset store values
    gameStore.searchQuery = '';
    gameStore.selectedGenre = '';
    gameStore.selectedPlayerFilter = '';
    gameStore.selectedPlayerCount = '';
    gameStore.sortBy = 'title';

    // Reapply filters and render
    gameStore.applyFilters();
    renderGames();
}

/**
 * Apply advanced player count filters
 */
function applyAdvancedPlayerFilters() {
    const minLocal = parseInt(document.getElementById('minLocalPlayers').value) || null;
    const maxLocal = parseInt(document.getElementById('maxLocalPlayers').value) || null;
    const minOnline = parseInt(document.getElementById('minOnlinePlayers').value) || null;
    const maxOnline = parseInt(document.getElementById('maxOnlinePlayers').value) || null;

    // Build query parameters
    const params = new URLSearchParams();
    if (minLocal) params.set('min_local_players', minLocal);
    if (maxLocal) params.set('max_local_players', maxLocal);
    if (minOnline) params.set('min_online_players', minOnline);
    if (maxOnline) params.set('max_online_players', maxOnline);

    // Load filtered games from API
    loadGamesWithFilters(params);
}

/**
 * Clear advanced player count filters
 */
function clearAdvancedPlayerFilters() {
    document.getElementById('minLocalPlayers').value = '';
    document.getElementById('maxLocalPlayers').value = '';
    document.getElementById('minOnlinePlayers').value = '';
    document.getElementById('maxOnlinePlayers').value = '';

    // Reload all games without filters
    Alpine.store('games').loadGames();
}

/**
 * Load games with specific filters from API
 */
async function loadGamesWithFilters(params) {
    const gameStore = Alpine.store('games');
    gameStore.isLoading = true;

    try {
        const url = '/api/games' + (params.toString() ? '?' + params.toString() : '');
        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            gameStore.allGames = data.games || [];
            gameStore.updateStats();
            gameStore.extractGenres();
            gameStore.applyFilters();
            renderGames();
        } else {
            console.error('Failed to load filtered games:', data.error);
        }
    } catch (error) {
        console.error('Failed to load filtered games:', error);
    } finally {
        gameStore.isLoading = false;
    }
}

/**
 * Render games to the grid
 */
function renderGames() {
    const gameStore = Alpine.store('games');
    GameGrid.renderGames(gameStore.filteredGames);

    // Update genre filter options
    updateGenreFilter();

    // Update stats display
    updateStatsDisplay();
}

/**
 * Update stats display
 */
function updateStatsDisplay() {
    const gameStore = Alpine.store('games');
    const stats = gameStore.stats;

    const totalGamesEl = document.getElementById('totalGames');
    const syncedGamesRawgEl = document.getElementById('syncedGamesRawg');
    const syncedGamesIgdbEl = document.getElementById('syncedGamesIgdb');
    const localMpGamesEl = document.getElementById('localMpGames');
    const onlineMpGamesEl = document.getElementById('onlineMpGames');

    if (totalGamesEl) totalGamesEl.textContent = stats.total;
    if (syncedGamesRawgEl) syncedGamesRawgEl.textContent = stats.syncedRawg;
    if (syncedGamesIgdbEl) syncedGamesIgdbEl.textContent = stats.syncedIgdb;
    if (localMpGamesEl) localMpGamesEl.textContent = stats.localMp;
    if (onlineMpGamesEl) onlineMpGamesEl.textContent = stats.onlineMp;
}

// Make renderGames available globally for the store to call
window.renderGames = renderGames;

/**
 * Update genre filter dropdown
 */
function updateGenreFilter() {
    const gameStore = Alpine.store('games');
    const genreFilter = document.getElementById('genreFilter');

    if (!genreFilter) return;

    const currentValue = genreFilter.value;
    genreFilter.innerHTML = '<option value="">All Genres</option>';

    gameStore.genres.forEach(genre => {
        const option = document.createElement('option');
        option.value = genre;
        option.textContent = genre;
        if (genre === currentValue) {
            option.selected = true;
        }
        genreFilter.appendChild(option);
    });
}
