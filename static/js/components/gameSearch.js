/**
 * Game Search Component
 * Logic for searching and manually adding games to the library
 */

const GameSearch = {
    /**
     * Open the add game modal
     */
    openModal() {
        const modal = document.getElementById('addGameModal');
        modal.style.display = 'flex';

        // Reset the form
        document.getElementById('searchResults').innerHTML = '';
        document.getElementById('gameSearchInput').value = '';
        document.getElementById('searchStatus').style.display = 'none';
    },

    /**
     * Close the add game modal
     */
    closeModal() {
        const modal = document.getElementById('addGameModal');
        modal.style.display = 'none';
    },

    /**
     * Search RAWG for games
     */
    async searchGames() {
        const query = document.getElementById('gameSearchInput').value.trim();

        if (!query) {
            alert('Please enter a game name to search');
            return;
        }

        const searchBtn = document.getElementById('searchGameBtn');
        const searchStatus = document.getElementById('searchStatus');
        const searchResults = document.getElementById('searchResults');

        // Show loading state
        searchBtn.disabled = true;
        searchBtn.innerHTML = '<span class="btn-icon">⏳</span> Searching...';
        searchStatus.style.display = 'block';
        searchStatus.textContent = 'Searching RAWG database...';
        searchStatus.style.color = '#ccc';
        searchResults.innerHTML = '';

        try {
            const data = await API.searchGames(query);

            if (data.success && data.results.length > 0) {
                searchStatus.style.display = 'none';
                this.displaySearchResults(data.results);
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
    },

    /**
     * Display search results
     */
    displaySearchResults(results) {
        const searchResults = document.getElementById('searchResults');

        const resultsHTML = results.map(game => {
            const genres = game.genres && game.genres.length > 0 ?
                `<div class="search-result-genres">${game.genres.join(', ')}</div>` : '';

            const platforms = game.platforms && game.platforms.length > 0 ?
                `<div style="font-size: 0.8em; color: #999; margin-top: 5px;">Platforms: ${game.platforms.slice(0, 4).join(', ')}${game.platforms.length > 4 ? '...' : ''}</div>` : '';

            const imageHTML = game.background_image ?
                `<img src="${game.background_image}" alt="${Formatters.escapeHtml(game.name)}" class="search-result-image">` :
                '<div class="search-result-image" style="background: rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center;">No Image</div>';

            return `
                <div class="search-result-card">
                    ${imageHTML}
                    <div class="search-result-info">
                        <div class="search-result-title">${Formatters.escapeHtml(game.name)}</div>
                        <div class="search-result-meta">
                            ${game.released ? `<span>📅 ${game.released}</span>` : ''}
                            ${game.rating ? `<span>⭐ ${game.rating}/5</span>` : ''}
                            ${game.metacritic ? `<span>🎮 ${game.metacritic}/100</span>` : ''}
                        </div>
                        ${genres}
                        ${platforms}
                        <div class="search-result-actions">
                            <button class="btn-small btn-add" onclick="GameSearch.addGameToLibrary(${game.id}, '${game.name.replace(/'/g, "\\'")}', event)">
                                ➕ Add to Library
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        searchResults.innerHTML = resultsHTML;
    },

    /**
     * Add a game to the library
     */
    async addGameToLibrary(rawgId, gameName, event) {
        const btn = event.target;
        btn.disabled = true;
        btn.innerHTML = '⏳ Adding...';

        try {
            const data = await API.addManualGame(rawgId, gameName);

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
                const gameStore = Alpine.store('games');
                await gameStore.loadGames();

                // Close modal after a delay
                setTimeout(() => {
                    this.closeModal();
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
    },

    /**
     * Initialize event listeners
     */
    init() {
        // Add game button
        document.getElementById('addManualBtn')?.addEventListener('click', () => {
            this.openModal();
        });

        // Search button
        document.getElementById('searchGameBtn')?.addEventListener('click', () => {
            this.searchGames();
        });

        // Enter key to search
        document.getElementById('gameSearchInput')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchGames();
            }
        });
    }
};

// Make GameSearch available globally
window.GameSearch = GameSearch;
