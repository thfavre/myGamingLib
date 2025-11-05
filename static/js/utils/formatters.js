/**
 * Formatter Utilities
 * Helper functions for formatting data for display
 */

const Formatters = {
    /**
     * Format release date
     */
    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } catch (error) {
            return dateString;
        }
    },

    /**
     * Get year from date string
     */
    getYear(dateString) {
        if (!dateString) return null;
        try {
            return new Date(dateString).getFullYear();
        } catch (error) {
            return null;
        }
    },

    /**
     * Format rating (ensure 1 decimal place)
     */
    formatRating(rating) {
        if (rating === null || rating === undefined) return 'N/A';
        return parseFloat(rating).toFixed(1);
    },

    /**
     * Format IGDB rating (0-100) to 0-5 scale
     */
    formatIgdbRating(rating) {
        if (!rating) return 'N/A';
        return (rating / 20).toFixed(1);
    },

    /**
     * Format playtime in hours
     */
    formatPlaytime(hours) {
        if (!hours) return 'N/A';
        if (hours < 1) return '< 1 hour';
        if (hours === 1) return '1 hour';
        return `${hours} hours`;
    },

    /**
     * Format large numbers with commas
     */
    formatNumber(num) {
        if (!num) return 'N/A';
        return num.toLocaleString('en-US');
    },

    /**
     * Get player count display string
     */
    formatPlayerCount(min, max) {
        if (!max || max <= 1) return null;
        if (!min) min = 1;
        return `${min}-${max}P`;
    },

    /**
     * Extract genre names from genre array
     */
    extractGenreNames(genres) {
        if (!genres || !Array.isArray(genres)) return [];
        return genres.map(g => typeof g === 'object' ? g.name : g).filter(Boolean);
    },

    /**
     * Extract platform names from platform array
     */
    extractPlatformNames(platforms) {
        if (!platforms || !Array.isArray(platforms)) return [];
        return platforms.map(p => typeof p === 'object' ? p.platform : p).filter(Boolean);
    },

    /**
     * Extract tag names from tag array
     */
    extractTagNames(tags) {
        if (!tags || !Array.isArray(tags)) return [];
        return tags.map(t => typeof t === 'object' ? t.name : t).filter(Boolean);
    },

    /**
     * Truncate text to specified length
     */
    truncate(text, maxLength = 100) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    },

    /**
     * Convert newlines to HTML breaks
     */
    nl2br(text) {
        if (!text) return '';
        return text.replace(/\n/g, '<br>');
    },

    /**
     * Escape HTML for safe display
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Make Formatters available globally
window.Formatters = Formatters;
