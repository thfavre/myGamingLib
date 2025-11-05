/**
 * API Service
 * All API calls to the Flask backend
 */

const API = {
    /**
     * Fetch all games from the library
     */
    async getGames() {
        try {
            const response = await fetch('/api/games');
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching games:', error);
            throw error;
        }
    },

    /**
     * Fetch library statistics
     */
    async getStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching stats:', error);
            throw error;
        }
    },

    /**
     * Open Chrome browser for Epic Games scraping
     */
    async openChrome() {
        try {
            const response = await fetch('/api/open-chrome', { method: 'POST' });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error opening Chrome:', error);
            throw error;
        }
    },

    /**
     * Start parsing Epic Games after user logs in
     */
    async startParsing() {
        try {
            const response = await fetch('/api/start-parsing', { method: 'POST' });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error starting parsing:', error);
            throw error;
        }
    },

    /**
     * Start RAWG metadata sync
     */
    async startRawgSync(forceResync = false) {
        try {
            const response = await fetch('/api/sync', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ force_resync: forceResync })
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error starting RAWG sync:', error);
            throw error;
        }
    },

    /**
     * Start IGDB metadata sync
     */
    async startIgdbSync() {
        try {
            const response = await fetch('/api/sync-igdb', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error starting IGDB sync:', error);
            throw error;
        }
    },

    /**
     * Get task status (scraping, syncing, igdb)
     */
    async getTaskStatus(taskType) {
        try {
            const response = await fetch(`/api/status/${taskType}`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error(`Error getting ${taskType} status:`, error);
            throw error;
        }
    },

    /**
     * Search RAWG for games
     */
    async searchGames(query) {
        try {
            const response = await fetch('/api/search-game', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error searching games:', error);
            throw error;
        }
    },

    /**
     * Add a game manually to the library
     */
    async addManualGame(rawgId, gameName) {
        try {
            const response = await fetch('/api/add-manual-game', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rawg_id: rawgId,
                    game_name: gameName
                })
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error adding manual game:', error);
            throw error;
        }
    },

    /**
     * Sync a single game with RAWG or IGDB
     */
    async syncSingleGame(gameId, source = 'rawg') {
        try {
            const response = await fetch(`/api/sync-single-game/${gameId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ source })
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error(`Error syncing single game with ${source}:`, error);
            throw error;
        }
    }
};

// Make API available globally
window.API = API;
