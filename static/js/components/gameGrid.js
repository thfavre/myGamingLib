/**
 * Game Grid Component
 * Logic for displaying game cards in the main grid
 */

const GameGrid = {
    /**
     * Create HTML for a single game card
     */
    createGameCard(game) {
        const hasSyncData = game.rawg__synced || game.rawg_synced;
        const imageUrl = game.rawg__background_image || '';
        const rating = game.rawg__rating ? Formatters.formatRating(game.rawg__rating) : null;
        const releaseYear = game.rawg__released ? Formatters.getYear(game.rawg__released) : null;

        const genres = this._formatGenres(game);

        return `
            <div class="game-card ${!hasSyncData ? 'no-sync' : ''}" onclick="GameGrid.showGameDetail(${game.id})">
                ${imageUrl ?
                    `<img src="${imageUrl}" alt="${Formatters.escapeHtml(game.title)}" class="game-card-image">` :
                    '<div class="game-card-image"></div>'
                }
                <div class="game-card-content">
                    <h3 class="game-card-title">${Formatters.escapeHtml(game.title)}</h3>
                    <div class="game-card-meta">
                        ${rating ? `<span class="meta-badge badge-rating">★ ${rating}</span>` : ''}
                        ${releaseYear ? `<span class="meta-badge badge-date">${releaseYear}</span>` : ''}
                    </div>
                    <div class="game-card-genres">
                        ${genres}
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Format genres for card display (show first 3)
     */
    _formatGenres(game) {
        const genres = game.rawg__genres;
        if (!genres || !Array.isArray(genres) || genres.length === 0) return '';

        return genres.slice(0, 3).map(g => {
            const genreName = typeof g === 'object' ? g.name : g;
            return `<span class="genre-tag">${Formatters.escapeHtml(genreName)}</span>`;
        }).join('');
    },

    /**
     * Show game detail modal
     */
    showGameDetail(gameId) {
        const gameStore = Alpine.store('games');
        const game = gameStore.allGames.find(g => g.id === gameId);

        if (!game) {
            console.error('Game not found:', gameId);
            return;
        }

        // Log game info to console for debugging
        console.log('Showing game detail for:', game.title);

        // Update current game in store
        gameStore.setCurrentGame(game);

        // Show modal
        const modal = document.getElementById('gameModal');
        const detailDiv = document.getElementById('gameDetail');

        detailDiv.innerHTML = GameDetail.buildDetailHTML(game);
        modal.style.display = 'flex';
    },

    /**
     * Close game detail modal
     */
    closeGameModal() {
        const modal = document.getElementById('gameModal');
        modal.style.display = 'none';

        // Clear current game
        const gameStore = Alpine.store('games');
        gameStore.setCurrentGame(null);
    },

    /**
     * Render all games in the grid
     */
    renderGames(games) {
        const grid = document.getElementById('gamesGrid');

        if (!games || games.length === 0) {
            grid.innerHTML = '<div class="loading">No games found. Click "Parse Epic Games" to get started!</div>';
            return;
        }

        grid.innerHTML = games.map(game => this.createGameCard(game)).join('');
    }
};

// Make GameGrid available globally
window.GameGrid = GameGrid;

// Close modal when clicking outside
window.addEventListener('click', (event) => {
    const gameModal = document.getElementById('gameModal');
    const addGameModal = document.getElementById('addGameModal');

    if (event.target === gameModal) {
        GameGrid.closeGameModal();
    }
    if (event.target === addGameModal) {
        GameSearch.closeModal();
    }
});
