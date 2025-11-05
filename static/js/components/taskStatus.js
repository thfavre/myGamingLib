/**
 * Task Status Component
 * Logic for managing background tasks (scraping, syncing)
 */

const TaskStatus = {
    /**
     * Parse Epic Games - Step 1: Open Chrome
     */
    async parseEpicGames() {
        const btn = document.getElementById('parseEpicBtn');
        btn.disabled = true;
        btn.textContent = 'Opening Chrome...';

        try {
            const data = await API.openChrome();

            if (data.success) {
                this.showPanel('scrapingPanel');

                // Show the Continue button after Chrome opens
                setTimeout(() => {
                    document.getElementById('continueButtonContainer').style.display = 'block';
                }, 2000);

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
    },

    /**
     * Parse Epic Games - Step 2: Continue after login
     */
    async continueParsing() {
        const btn = document.getElementById('continueParsingBtn');
        btn.disabled = true;
        btn.textContent = 'Starting...';

        // Hide the continue button container
        document.getElementById('continueButtonContainer').style.display = 'none';

        try {
            const data = await API.startParsing();

            if (data.success) {
                this.startPolling('scraping');
            } else {
                alert(data.message);
                document.getElementById('continueButtonContainer').style.display = 'block';
                btn.disabled = false;
                btn.innerHTML = '<span class="btn-icon">▶️</span> Continue';
            }
        } catch (error) {
            console.error('Error starting parsing:', error);
            alert('Failed to start parsing');
            document.getElementById('continueButtonContainer').style.display = 'block';
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">▶️</span> Continue';
        }
    },

    /**
     * Start RAWG sync
     */
    async startRawgSync() {
        const btn = document.getElementById('syncBtn');
        btn.disabled = true;
        btn.textContent = 'Syncing...';

        try {
            const data = await API.startRawgSync();

            if (data.success) {
                this.showPanel('syncingPanel');
                this.startPolling('syncing');
            } else {
                alert(data.message);
                btn.disabled = false;
                btn.innerHTML = '<span class="btn-icon">🔄</span> Sync with RAWG';
            }
        } catch (error) {
            console.error('Error starting RAWG sync:', error);
            alert('Failed to start sync');
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">🔄</span> Sync with RAWG';
        }
    },

    /**
     * Start IGDB sync
     */
    async startIgdbSync() {
        const btn = document.getElementById('syncIgdbBtn');
        btn.disabled = true;
        btn.textContent = 'Syncing...';

        try {
            const data = await API.startIgdbSync();

            if (data.success) {
                this.showPanel('igdbPanel');
                this.startPolling('igdb');
            } else {
                alert(data.message);
                btn.disabled = false;
                btn.innerHTML = '<span class="btn-icon">🎮</span> Sync with IGDB';
            }
        } catch (error) {
            console.error('Error starting IGDB sync:', error);
            alert('Failed to start IGDB sync');
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">🎮</span> Sync with IGDB';
        }
    },

    /**
     * Show a status panel
     */
    showPanel(panelId) {
        const panel = document.getElementById(panelId);
        if (panel) {
            panel.style.display = 'block';
        }
    },

    /**
     * Close a status panel
     */
    closePanel(panelId) {
        const panel = document.getElementById(panelId);
        if (panel) {
            panel.style.display = 'none';
        }
    },

    /**
     * Start polling for task status
     */
    startPolling(taskType) {
        const interval = setInterval(async () => {
            try {
                const data = await API.getTaskStatus(taskType);

                if (data.success) {
                    this.updateLogs(taskType, data.logs);

                    if (!data.running) {
                        clearInterval(interval);
                        await this.taskComplete(taskType, data.result);
                    }
                }
            } catch (error) {
                console.error(`Error polling ${taskType}:`, error);
            }
        }, 1000);
    },

    /**
     * Update logs in the status panel
     */
    updateLogs(taskType, logs) {
        const logsDiv = document.getElementById(`${taskType}Logs`);
        if (!logsDiv) return;

        logsDiv.innerHTML = logs.map(log => `<p>${Formatters.escapeHtml(log)}</p>`).join('');
        logsDiv.scrollTop = logsDiv.scrollHeight;
    },

    /**
     * Handle task completion
     */
    async taskComplete(taskType, result) {
        if (taskType === 'scraping') {
            const btn = document.getElementById('parseEpicBtn');
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">🎮</span> Parse Epic Games';

            document.getElementById('continueButtonContainer').style.display = 'none';

            const continueBtn = document.getElementById('continueParsingBtn');
            continueBtn.disabled = false;
            continueBtn.innerHTML = '<span class="btn-icon">▶️</span> Continue';
        } else if (taskType === 'syncing') {
            const btn = document.getElementById('syncBtn');
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">🔄</span> Sync with RAWG';
        } else if (taskType === 'igdb') {
            const btn = document.getElementById('syncIgdbBtn');
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">🎮</span> Sync with IGDB';
        }

        // Refresh games and stats if task was successful
        if (result && result.success) {
            const gameStore = Alpine.store('games');
            await gameStore.loadGames();
        }
    },

    /**
     * Refresh library
     */
    async refreshLibrary() {
        const gameStore = Alpine.store('games');
        await gameStore.loadGames();
    },

    /**
     * Initialize event listeners
     */
    init() {
        // Parse Epic Games button
        document.getElementById('parseEpicBtn')?.addEventListener('click', () => {
            this.parseEpicGames();
        });

        // Continue parsing button
        document.getElementById('continueParsingBtn')?.addEventListener('click', () => {
            this.continueParsing();
        });

        // Sync with RAWG button
        document.getElementById('syncBtn')?.addEventListener('click', () => {
            this.startRawgSync();
        });

        // Sync with IGDB button
        document.getElementById('syncIgdbBtn')?.addEventListener('click', () => {
            this.startIgdbSync();
        });

        // Refresh button
        document.getElementById('refreshBtn')?.addEventListener('click', () => {
            this.refreshLibrary();
        });
    }
};

// Make TaskStatus available globally
window.TaskStatus = TaskStatus;

// Make closePanel available globally for onclick handlers in HTML
window.closePanel = (panelId) => TaskStatus.closePanel(panelId);
window.closeModal = () => GameGrid.closeGameModal();
