/**
 * Game Detail Component
 * Logic for displaying detailed game information in modals
 */

const GameDetail = {
    /**
     * Build comprehensive game detail HTML (for modal)
     * This generates the full game detail view with all metadata
     */
    buildDetailHTML(game) {
        if (!game) return '';

        const hasRAWGData = game.rawg__synced === 1 || game.rawg_synced;
        const hasIGDBData = game.igdb__synced === 1 || game.igdb_synced;

        // If no metadata at all, show sync buttons
        if (!hasRAWGData && !hasIGDBData) {
            return this._buildNoMetadataView(game);
        }

        // Build comprehensive view with both RAWG and IGDB data
        return this._buildComprehensiveView(game, hasRAWGData, hasIGDBData);
    },

    /**
     * Build view when no metadata is available
     */
    _buildNoMetadataView(game) {
        return `
            <div class="game-detail-header">
                <h2>${Formatters.escapeHtml(game.title)}</h2>
            </div>
            <div class="game-detail-content">
                <div class="no-metadata-message">
                    <h3>No metadata available for this game</h3>
                    <p>Sync with RAWG or IGDB to get detailed information about this game.</p>
                    <div class="sync-buttons">
                        <button class="btn btn-primary" onclick="GameDetail.syncGame(${game.id}, 'rawg')">
                            <span class="btn-icon">🔄</span> Sync with RAWG
                        </button>
                        <button class="btn btn-secondary" onclick="GameDetail.syncGame(${game.id}, 'igdb')">
                            <span class="btn-icon">🎮</span> Sync with IGDB
                        </button>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Build comprehensive view with all data from RAWG and IGDB
     */
    _buildComprehensiveView(game, hasRAWGData, hasIGDBData) {
        // Prepare all data
        const imageUrl = game.rawg__background_image || game.igdb__cover || '';
        const title = game.title;

        // Ratings - show both if different
        const rawgRating = game.rawg__rating ? Formatters.formatRating(game.rawg__rating) : null;
        const igdbRating = game.igdb__rating ? Formatters.formatIgdbRating(game.igdb__rating) : null;
        const metacritic = game.rawg__metacritic || null;

        // Release date
        const releaseDate = game.rawg__released || game.igdb__first_release_date || 'Unknown';

        // Description - prefer RAWG as it's usually more detailed
        const description = game.rawg__description || game.igdb__summary || 'No description available.';
        const storyline = game.igdb__storyline || null;

        // Build the comprehensive HTML
        return `
            <div class="game-detail-header">
                <h2 class="game-detail-title">${Formatters.escapeHtml(title)}</h2>
                <div class="game-detail-meta">
                    ${rawgRating ? `<span class="meta-badge badge-rating" title="RAWG Rating">⭐ ${rawgRating}/5</span>` : ''}
                    ${igdbRating && igdbRating !== rawgRating ? `<span class="meta-badge badge-rating" title="IGDB Rating" style="background: rgba(250, 112, 154, 0.3)">🎮 ${igdbRating}/5</span>` : ''}
                    ${metacritic ? `<span class="meta-badge badge-rating" title="Metacritic Score">📊 ${metacritic}/100</span>` : ''}
                    <span class="meta-badge badge-date">📅 ${releaseDate}</span>
                    ${hasRAWGData ? `<span class="meta-badge" style="background: rgba(102, 126, 234, 0.3); color: #667eea;" title="Synced with RAWG">✓ RAWG</span>` : ''}
                    ${hasIGDBData ? `<span class="meta-badge" style="background: rgba(250, 112, 154, 0.3); color: #fa709a;" title="Synced with IGDB">✓ IGDB</span>` : ''}
                </div>

                ${!hasIGDBData && hasRAWGData ? `
                <div style="margin: 15px 0; padding: 12px; background: rgba(250, 112, 154, 0.1); border-radius: 8px; border: 2px solid rgba(250, 112, 154, 0.3); text-align: center;">
                    <button onclick="GameDetail.syncGame(${game.id}, 'igdb')" class="btn btn-small" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white;">
                        <span style="margin-right: 8px;">🎮</span> Sync with IGDB for more data
                    </button>
                </div>
                ` : ''}

                ${!hasRAWGData && hasIGDBData ? `
                <div style="margin: 15px 0; padding: 12px; background: rgba(102, 126, 234, 0.1); border-radius: 8px; border: 2px solid rgba(102, 126, 234, 0.3); text-align: center;">
                    <button onclick="GameDetail.syncGame(${game.id}, 'rawg')" class="btn btn-small" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                        <span style="margin-right: 8px;">🔄</span> Sync with RAWG for more data
                    </button>
                </div>
                ` : ''}
            </div>

            ${imageUrl ? `<img src="${imageUrl}" alt="${Formatters.escapeHtml(title)}" class="game-detail-image">` : ''}

            <div class="game-detail-grid">
                <div class="game-detail-main">
                    ${this._buildDescriptionSection(description, storyline)}
                    ${this._buildScreenshots(game)}
                    ${this._buildTrailers(game)}
                    ${this._buildAchievements(game)}
                </div>

                <div class="game-detail-sidebar">
                    ${this._buildRatingsSection(game, rawgRating, igdbRating, metacritic)}
                    ${this._buildGameInfoSection(game, hasRAWGData, hasIGDBData)}
                    ${this._buildDevelopersPublishers(game, hasRAWGData, hasIGDBData)}
                    ${this._buildPlatformsSection(game, hasRAWGData, hasIGDBData)}
                    ${this._buildStoreLinks(game)}
                    ${this._buildTags(game)}
                </div>
            </div>
        `;
    },

    /**
     * Build description section
     */
    _buildDescriptionSection(description, storyline) {
        return `
            <div class="game-detail-section">
                <h3>📖 Description</h3>
                <div class="game-description">${Formatters.nl2br(Formatters.escapeHtml(description))}</div>
                ${storyline ? `
                    <div style="margin-top: 20px; padding: 15px; background: rgba(250, 112, 154, 0.1); border-left: 4px solid #fa709a; border-radius: 4px;">
                        <h4 style="color: #fa709a; margin-bottom: 10px;">📚 Storyline (IGDB)</h4>
                        <p style="color: #ccc; line-height: 1.6;">${Formatters.nl2br(Formatters.escapeHtml(storyline))}</p>
                    </div>
                ` : ''}
            </div>
        `;
    },

    /**
     * Build comprehensive ratings section
     */
    _buildRatingsSection(game, rawgRating, igdbRating, metacritic) {
        const hasRatings = rawgRating || igdbRating || metacritic || game.rawg__ratings_count || game.igdb__rating_count;
        if (!hasRatings) return '';

        return `
            <div class="game-detail-section">
                <h3>⭐ Ratings & Reviews</h3>
                <div class="game-stats">
                    ${rawgRating ? `<div class="stat-item"><span class="stat-label">RAWG Rating:</span> <span class="stat-value" style="color: #667eea;">${rawgRating}/5.0</span></div>` : ''}
                    ${igdbRating ? `<div class="stat-item"><span class="stat-label">IGDB Rating:</span> <span class="stat-value" style="color: #fa709a;">${igdbRating}/5.0</span></div>` : ''}
                    ${game.igdb__total_rating ? `<div class="stat-item"><span class="stat-label">IGDB Aggregated:</span> <span class="stat-value" style="color: #fa709a;">${Formatters.formatIgdbRating(game.igdb__total_rating)}/5.0</span></div>` : ''}
                    ${metacritic ? `<div class="stat-item"><span class="stat-label">Metacritic:</span> <span class="stat-value" style="color: #ffd700;">${metacritic}/100</span></div>` : ''}
                    ${game.rawg__ratings_count ? `<div class="stat-item"><span class="stat-label">RAWG Reviews:</span> <span class="stat-value">${Formatters.formatNumber(game.rawg__ratings_count)}</span></div>` : ''}
                    ${game.igdb__rating_count ? `<div class="stat-item"><span class="stat-label">IGDB Reviews:</span> <span class="stat-value">${Formatters.formatNumber(game.igdb__rating_count)}</span></div>` : ''}
                    ${game.rawg__reviews_count ? `<div class="stat-item"><span class="stat-label">User Reviews:</span> <span class="stat-value">${Formatters.formatNumber(game.rawg__reviews_count)}</span></div>` : ''}
                </div>
            </div>
        `;
    },

    /**
     * Build game info section with all metadata
     */
    _buildGameInfoSection(game, hasRAWGData, hasIGDBData) {
        const rawgGenres = hasRAWGData ? Formatters.extractGenreNames(game.rawg__genres).join(', ') : null;
        const igdbGenres = hasIGDBData && game.igdb__genres ? (Array.isArray(game.igdb__genres) ? game.igdb__genres.join(', ') : game.igdb__genres) : null;
        const genres = rawgGenres || igdbGenres || 'N/A';

        return `
            <div class="game-detail-section">
                <h3>📊 Game Statistics</h3>
                <div class="game-stats">
                    ${game.rawg__added_count ? `<div class="stat-item"><span class="stat-label">Players (RAWG):</span> <span class="stat-value">${Formatters.formatNumber(game.rawg__added_count)}</span></div>` : ''}
                    ${game.igdb__follows ? `<div class="stat-item"><span class="stat-label">Followers (IGDB):</span> <span class="stat-value">${Formatters.formatNumber(game.igdb__follows)}</span></div>` : ''}
                    ${game.rawg__playtime ? `<div class="stat-item"><span class="stat-label">Avg Playtime:</span> <span class="stat-value">${game.rawg__playtime}h</span></div>` : ''}
                    ${game.rawg__achievements_count ? `<div class="stat-item"><span class="stat-label">Achievements:</span> <span class="stat-value">${game.rawg__achievements_count}</span></div>` : ''}
                    ${game.rawg__suggestions_count ? `<div class="stat-item"><span class="stat-label">Suggestions:</span> <span class="stat-value">${Formatters.formatNumber(game.rawg__suggestions_count)}</span></div>` : ''}
                </div>
            </div>

            <div class="game-detail-section">
                <h3>ℹ️ Game Information</h3>
                <div class="game-details-list">
                    <div class="detail-item">
                        <span class="detail-label">Genres:</span>
                        <span class="detail-value">${genres}</span>
                    </div>
                    ${game.igdb__game_modes ? `
                    <div class="detail-item">
                        <span class="detail-label">Game Modes:</span>
                        <span class="detail-value">${Array.isArray(game.igdb__game_modes) ? game.igdb__game_modes.join(', ') : game.igdb__game_modes}</span>
                    </div>` : ''}
                    ${game.igdb__player_perspectives ? `
                    <div class="detail-item">
                        <span class="detail-label">Perspectives:</span>
                        <span class="detail-value">${Array.isArray(game.igdb__player_perspectives) ? game.igdb__player_perspectives.join(', ') : game.igdb__player_perspectives}</span>
                    </div>` : ''}
                    ${game.igdb__themes ? `
                    <div class="detail-item">
                        <span class="detail-label">Themes:</span>
                        <span class="detail-value">${Array.isArray(game.igdb__themes) ? game.igdb__themes.join(', ') : game.igdb__themes}</span>
                    </div>` : ''}
                    ${game.rawg__esrb_rating || game.igdb__age_ratings ? `
                    <div class="detail-item">
                        <span class="detail-label">Age Rating:</span>
                        <span class="detail-value">${game.rawg__esrb_rating || (Array.isArray(game.igdb__age_ratings) ? game.igdb__age_ratings.join(', ') : game.igdb__age_ratings)}</span>
                    </div>` : ''}
                    ${game.rawg__website || game.igdb__url ? `
                    <div class="detail-item">
                        <span class="detail-label">Website:</span>
                        <a href="${game.rawg__website || game.igdb__url}" target="_blank" class="detail-link">Visit Official Site 🔗</a>
                    </div>` : ''}
                    ${game.rawg__reddit_url ? `
                    <div class="detail-item">
                        <span class="detail-label">Reddit:</span>
                        <a href="${game.rawg__reddit_url}" target="_blank" class="detail-link">r/${game.rawg__reddit_name || 'community'} 💬</a>
                    </div>` : ''}
                </div>
            </div>
        `;
    },

    /**
     * Build developers and publishers section
     */
    _buildDevelopersPublishers(game, hasRAWGData, hasIGDBData) {
        const rawgDevs = hasRAWGData && game.rawg__developers ? game.rawg__developers.map(dev => dev.name || 'Unknown').join(', ') : null;
        const igdbDevs = hasIGDBData && game.igdb__developers ? (Array.isArray(game.igdb__developers) ? game.igdb__developers.join(', ') : game.igdb__developers) : null;

        const rawgPubs = hasRAWGData && game.rawg__publishers ? game.rawg__publishers.map(pub => pub.name || 'Unknown').join(', ') : null;
        const igdbPubs = hasIGDBData && game.igdb__publishers ? (Array.isArray(game.igdb__publishers) ? game.igdb__publishers.join(', ') : game.igdb__publishers) : null;

        const developers = rawgDevs || igdbDevs || 'Unknown';
        const publishers = rawgPubs || igdbPubs || 'Unknown';

        return `
            <div class="game-detail-section">
                <h3>👨‍💻 Development</h3>
                <div class="game-details-list">
                    <div class="detail-item">
                        <span class="detail-label">Developer:</span>
                        <span class="detail-value">${developers}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Publisher:</span>
                        <span class="detail-value">${publishers}</span>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Build platforms section
     */
    _buildPlatformsSection(game, hasRAWGData, hasIGDBData) {
        const rawgPlatforms = hasRAWGData ? Formatters.extractPlatformNames(game.rawg__platforms).join(', ') : null;
        const igdbPlatforms = hasIGDBData && game.igdb__platforms ? (Array.isArray(game.igdb__platforms) ? game.igdb__platforms.join(', ') : game.igdb__platforms) : null;

        const platforms = rawgPlatforms || igdbPlatforms;
        if (!platforms) return '';

        return `
            <div class="game-detail-section">
                <h3>💻 Platforms</h3>
                <div class="detail-item">
                    <span class="detail-value">${platforms}</span>
                </div>
            </div>
        `;
    },

    /**
     * Build IGDB-only view (legacy - kept for compatibility)
     */
    _buildIGDBView(game) {
        const cover = game.igdb__cover || '';
        const summary = game.igdb__summary || 'No description available.';
        const rating = game.igdb__rating ? Formatters.formatIgdbRating(game.igdb__rating) : 'N/A';

        const genres = this._formatIGDBArray(game.igdb__genres);
        const developers = this._formatIGDBArray(game.igdb__developers);
        const publishers = this._formatIGDBArray(game.igdb__publishers);

        return `
            <div class="game-detail-header" ${cover ? `style="background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)), url('${cover}')"` : ''}>
                <h2>${Formatters.escapeHtml(game.igdb__name || game.title)}</h2>
            </div>
            <div class="game-detail-content">
                <div class="game-detail-section">
                    <h3>About</h3>
                    <p>${Formatters.nl2br(Formatters.escapeHtml(summary))}</p>
                    ${game.igdb__storyline ? `<p style="margin-top: 1rem;"><strong>Storyline:</strong> ${Formatters.nl2br(Formatters.escapeHtml(game.igdb__storyline))}</p>` : ''}
                </div>

                <div class="game-detail-section">
                    <h3>Rating</h3>
                    <p>IGDB Rating: ${rating} / 5.0</p>
                    ${game.igdb__total_rating ? `<p>Aggregated Rating: ${Formatters.formatIgdbRating(game.igdb__total_rating)} / 5.0</p>` : ''}
                </div>

                ${genres ? `<div class="game-detail-section"><h3>Genres</h3><p>${genres}</p></div>` : ''}
                ${developers ? `<div class="game-detail-section"><h3>Developers</h3><p>${developers}</p></div>` : ''}
                ${publishers ? `<div class="game-detail-section"><h3>Publishers</h3><p>${publishers}</p></div>` : ''}

                <div class="game-detail-section">
                    <p style="text-align: center; margin-top: 2rem;">
                        <button class="btn btn-primary" onclick="GameDetail.syncGame(${game.id}, 'rawg')">
                            <span class="btn-icon">🔄</span> Also Sync with RAWG
                        </button>
                    </p>
                </div>
            </div>
        `;
    },

    /**
     * Build RAWG view (main view)
     */
    _buildRAWGView(game, hasIGDBData) {
        const imageUrl = game.rawg__background_image || '';
        const rating = Formatters.formatRating(game.rawg__rating);
        const metacritic = game.rawg__metacritic || 'N/A';
        const releaseDate = game.rawg__released || 'Unknown';

        const platforms = Formatters.extractPlatformNames(game.rawg__platforms).join(', ') || 'N/A';
        const genres = Formatters.extractGenreNames(game.rawg__genres).join(', ') || 'N/A';
        const description = Formatters.nl2br(game.rawg__description || 'No description available.');

        const screenshots = this._buildScreenshots(game);
        const achievements = this._buildAchievements(game);
        const trailers = this._buildTrailers(game);
        const storeLinks = this._buildStoreLinks(game);
        const tags = this._buildTags(game);

        const developers = game.rawg__developers?.map(dev => dev.name || 'Unknown').join(', ') || 'Unknown';
        const publishers = game.rawg__publishers?.map(pub => pub.name || 'Unknown').join(', ') || 'Unknown';

        return `
            <div class="game-detail-header">
                <h2 class="game-detail-title">${Formatters.escapeHtml(game.title)}</h2>
                <div class="game-detail-meta">
                    <span class="meta-badge badge-rating">⭐ ${rating}/5</span>
                    ${metacritic !== 'N/A' ? `<span class="meta-badge badge-rating">🎮 ${metacritic}/100</span>` : ''}
                    <span class="meta-badge badge-date">📅 ${releaseDate}</span>
                </div>

                ${!hasIGDBData ? `
                <div id="igdbSyncSection-${game.id}" style="margin: 20px 0; padding: 15px; background: rgba(76, 175, 80, 0.1); border-radius: 8px; border: 2px solid #4caf50;">
                    <h3 style="margin-top: 0; color: #4caf50;">🎮 Sync with IGDB</h3>
                    <p style="margin: 10px 0; font-size: 0.9em; color: #ccc;">Fetch detailed game information from the IGDB database</p>
                    <button id="igdbSyncBtn-${game.id}" onclick="GameDetail.syncGame(${game.id}, 'igdb')" class="btn btn-success" style="width: 100%;">
                        <span class="btn-icon">🔄</span> Sync with IGDB
                    </button>
                </div>
                ` : ''}
            </div>

            ${imageUrl ? `<img src="${imageUrl}" alt="${Formatters.escapeHtml(game.title)}" class="game-detail-image">` : ''}

            <div class="game-detail-grid">
                <div class="game-detail-main">
                    <div class="game-detail-section">
                        <h3>📖 Description</h3>
                        <div class="game-description">${description}</div>
                    </div>

                    ${screenshots}
                    ${achievements}
                    ${trailers}
                </div>

                <div class="game-detail-sidebar">
                    <div class="game-detail-section">
                        <h3>📊 Game Stats</h3>
                        <div class="game-stats">
                            ${game.ratings_count ? `<div class="stat-item"><span class="stat-label">Reviews:</span> <span class="stat-value">${Formatters.formatNumber(game.ratings_count)}</span></div>` : ''}
                            ${game.added_count ? `<div class="stat-item"><span class="stat-label">Players:</span> <span class="stat-value">${Formatters.formatNumber(game.added_count)}</span></div>` : ''}
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
    },

    /**
     * Build screenshots section
     */
    _buildScreenshots(game) {
        if (!game.rawg__screenshots || game.rawg__screenshots.length === 0) return '';

        const screenshots = game.rawg__screenshots.map(screenshot => {
            const imageUrl = typeof screenshot === 'object' ? screenshot.image : screenshot;
            return `<img src="${imageUrl}" alt="Screenshot" class="screenshot" onclick="window.open('${imageUrl}', '_blank')">`;
        }).join('');

        return `
            <div class="game-detail-section">
                <h3>📷 Screenshots (${game.rawg__screenshots.length})</h3>
                <div class="screenshots-grid">
                    ${screenshots}
                </div>
            </div>
        `;
    },

    /**
     * Build achievements section
     */
    _buildAchievements(game) {
        if (!game.rawg__achievements || game.rawg__achievements.length === 0) return '';

        const achievementsHTML = game.rawg__achievements.slice(0, 5).map(ach => `
            <div class="achievement-card">
                <div class="achievement-name">${Formatters.escapeHtml(ach.name || 'Unknown')}</div>
                <div class="achievement-percent">${ach.percent || 'N/A'}%</div>
                ${ach.description ? `<div class="achievement-desc">${Formatters.escapeHtml(ach.description)}</div>` : ''}
            </div>
        `).join('');

        const expandButton = game.rawg__achievements.length > 5 ? `
            <div class="achievement-more">
                <button class="expand-btn" onclick="GameDetail.expandAchievements(${game.id})">
                    +${game.rawg__achievements.length - 5} more achievements
                </button>
            </div>
        ` : '';

        return `
            <div class="game-detail-section">
                <h3>🏆 Achievements (${game.rawg__achievements.length})</h3>
                <div class="achievements-grid" id="achievements-${game.id}">
                    ${achievementsHTML}
                    ${expandButton}
                </div>
            </div>
        `;
    },

    /**
     * Build trailers section
     */
    _buildTrailers(game) {
        if (!game.rawg__trailers || game.rawg__trailers.length === 0) return '';

        const trailersHTML = game.rawg__trailers.map(trailer => `
            <div class="trailer-card">
                ${trailer.preview ? `<img src="${trailer.preview}" alt="${Formatters.escapeHtml(trailer.name)}" class="trailer-preview">` : ''}
                <div class="trailer-name">${Formatters.escapeHtml(trailer.name || 'Video')}</div>
            </div>
        `).join('');

        return `
            <div class="game-detail-section">
                <h3>🎬 Trailers & Videos (${game.rawg__trailers.length})</h3>
                <div class="trailers-grid">
                    ${trailersHTML}
                </div>
            </div>
        `;
    },

    /**
     * Build store links section
     */
    _buildStoreLinks(game) {
        if (!game.rawg__stores || game.rawg__stores.length === 0) return '';

        const linksHTML = game.rawg__stores.map(store => `
            <a href="${store.url}" target="_blank" class="store-link">
                <span class="store-name">${Formatters.escapeHtml(store.store_name || 'Game Store')}</span>
                <span class="store-icon">🔗</span>
            </a>
        `).join('');

        return `
            <div class="game-detail-section">
                <h3>🛒 Where to Buy</h3>
                <div class="store-links">
                    ${linksHTML}
                </div>
            </div>
        `;
    },

    /**
     * Build tags section
     */
    _buildTags(game) {
        if (!game.rawg__tags || game.rawg__tags.length === 0) return '';

        const tagsHTML = game.rawg__tags.slice(0, 15).map(tag => {
            const tagName = typeof tag === 'object' ? tag.name : tag;
            return `<span class="tag-pill">${Formatters.escapeHtml(tagName)}</span>`;
        }).join('');

        const expandButton = game.rawg__tags.length > 15 ? `
            <button class="tag-more expand-btn" onclick="GameDetail.expandTags(${game.id})">
                +${game.rawg__tags.length - 15} more
            </button>
        ` : '';

        return `
            <div class="game-detail-section">
                <h3>🏷️ Tags</h3>
                <div class="tags-container" id="tags-${game.id}">
                    ${tagsHTML}
                    ${expandButton}
                </div>
            </div>
        `;
    },

    /**
     * Format IGDB array fields
     */
    _formatIGDBArray(field) {
        if (!field || !Array.isArray(field) || field.length === 0) return '';
        return field.join(', ');
    },

    /**
     * Sync a game with RAWG or IGDB
     */
    async syncGame(gameId, source) {
        const gameStore = Alpine.store('games');
        const modal = document.getElementById('gameModal');
        const detailDiv = document.getElementById('gameDetail');

        // Show loading
        detailDiv.innerHTML = `
            <div class="game-detail-content">
                <div class="no-metadata-message">
                    <h3>Syncing with ${source.toUpperCase()}...</h3>
                    <p>Fetching game metadata. This may take a few seconds.</p>
                    <div style="margin-top: 2rem;">
                        <div class="loading-spinner"></div>
                    </div>
                </div>
            </div>
        `;

        try {
            const data = await API.syncSingleGame(gameId, source);

            if (data.success) {
                // Refresh games
                await gameStore.loadGames();

                // Close and reopen modal with updated data
                modal.style.display = 'none';

                setTimeout(() => {
                    const updatedGame = gameStore.allGames.find(g => g.id === gameId);
                    if (updatedGame) {
                        gameStore.setCurrentGame(updatedGame);
                        detailDiv.innerHTML = this.buildDetailHTML(updatedGame);
                        modal.style.display = 'flex';
                    }
                }, 300);
            } else {
                detailDiv.innerHTML = `
                    <div class="game-detail-content">
                        <div class="no-metadata-message">
                            <h3>Sync Failed</h3>
                            <p>${data.message || 'Failed to sync. Please try again.'}</p>
                            <button class="btn btn-primary" onclick="document.getElementById('gameModal').style.display='none'">
                                Close
                            </button>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            console.error(`Error syncing with ${source}:`, error);
            detailDiv.innerHTML = `
                <div class="game-detail-content">
                    <div class="no-metadata-message">
                        <h3>Error</h3>
                        <p>An error occurred while syncing. Please try again.</p>
                        <button class="btn btn-primary" onclick="document.getElementById('gameModal').style.display='none'">
                            Close
                        </button>
                    </div>
                </div>
            `;
        }
    },

    /**
     * Expand achievements to show all
     */
    expandAchievements(gameId) {
        const gameStore = Alpine.store('games');
        const game = gameStore.allGames.find(g => g.id === gameId);
        if (!game || !game.rawg__achievements) return;

        const container = document.getElementById(`achievements-${gameId}`);
        const achievementsHTML = game.rawg__achievements.map(ach => `
            <div class="achievement-card">
                <div class="achievement-name">${Formatters.escapeHtml(ach.name || 'Unknown')}</div>
                <div class="achievement-percent">${ach.percent || 'N/A'}%</div>
                ${ach.description ? `<div class="achievement-desc">${Formatters.escapeHtml(ach.description)}</div>` : ''}
            </div>
        `).join('');

        container.innerHTML = achievementsHTML + `
            <div class="achievement-more">
                <button class="expand-btn collapse-btn" onclick="GameDetail.collapseAchievements(${gameId})">
                    Show less
                </button>
            </div>
        `;
    },

    /**
     * Collapse achievements to show only first 5
     */
    collapseAchievements(gameId) {
        const gameStore = Alpine.store('games');
        const game = gameStore.allGames.find(g => g.id === gameId);
        if (!game || !game.rawg__achievements) return;

        const container = document.getElementById(`achievements-${gameId}`);
        const achievementsHTML = game.rawg__achievements.slice(0, 5).map(ach => `
            <div class="achievement-card">
                <div class="achievement-name">${Formatters.escapeHtml(ach.name || 'Unknown')}</div>
                <div class="achievement-percent">${ach.percent || 'N/A'}%</div>
                ${ach.description ? `<div class="achievement-desc">${Formatters.escapeHtml(ach.description)}</div>` : ''}
            </div>
        `).join('');

        container.innerHTML = achievementsHTML + `
            <div class="achievement-more">
                <button class="expand-btn" onclick="GameDetail.expandAchievements(${gameId})">
                    +${game.rawg__achievements.length - 5} more achievements
                </button>
            </div>
        `;
    },

    /**
     * Expand tags to show all
     */
    expandTags(gameId) {
        const gameStore = Alpine.store('games');
        const game = gameStore.allGames.find(g => g.id === gameId);
        if (!game || !game.rawg__tags) return;

        const container = document.getElementById(`tags-${gameId}`);
        const tagsHTML = game.rawg__tags.map(tag => {
            const tagName = typeof tag === 'object' ? tag.name : tag;
            return `<span class="tag-pill">${Formatters.escapeHtml(tagName)}</span>`;
        }).join('');

        container.innerHTML = tagsHTML + `
            <button class="tag-more expand-btn collapse-btn" onclick="GameDetail.collapseTags(${gameId})">
                Show less
            </button>
        `;
    },

    /**
     * Collapse tags to show only first 15
     */
    collapseTags(gameId) {
        const gameStore = Alpine.store('games');
        const game = gameStore.allGames.find(g => g.id === gameId);
        if (!game || !game.rawg__tags) return;

        const container = document.getElementById(`tags-${gameId}`);
        const tagsHTML = game.rawg__tags.slice(0, 15).map(tag => {
            const tagName = typeof tag === 'object' ? tag.name : tag;
            return `<span class="tag-pill">${Formatters.escapeHtml(tagName)}</span>`;
        }).join('');

        container.innerHTML = tagsHTML + `
            <button class="tag-more expand-btn" onclick="GameDetail.expandTags(${gameId})">
                +${game.rawg__tags.length - 15} more
            </button>
        `;
    }
};

// Make GameDetail available globally
window.GameDetail = GameDetail;
