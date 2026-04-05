/* ============================================
   Mental Health AI - Frontend Application
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    // ====================
    // DOM Elements
    // ====================
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const emotionBadge = document.getElementById('current-emotion');
    const suggestionsList = document.getElementById('suggestions-list');
    const trendAnalysis = document.getElementById('trends');
    const sendButton = document.getElementById('send-button');
    const clearChatBtn = document.getElementById('clear-chat-btn');
    const settingsBtn = document.getElementById('settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const closeModalBtn = document.getElementById('close-modal');
    const messageCount = document.getElementById('message-count');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    // ====================
    // Configuration
    // ====================
    const API_BASE = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000'
  : 'https://backend.onrender.com';
    const USER_ID = "user_" + Math.random().toString(36).substr(2, 9);
    
    let messageCounter = 0;
    let emotions = [];
    
    // ====================
    // Initialization
    // ====================
    console.log(`🚀 MindGuardian initialized with User ID: ${USER_ID}`);
    loadInitialData();
    setupEventListeners();
    
    // ====================
    // Event Listeners
    // ====================
    function setupEventListeners() {
        chatForm.addEventListener('submit', handleChatSubmit);
        clearChatBtn.addEventListener('click', handleClearChat);
        settingsBtn.addEventListener('click', handleSettingsOpen);
        closeModalBtn.addEventListener('click', handleSettingsClose);
        settingsModal.addEventListener('click', (e) => {
            if (e.target === settingsModal) handleSettingsClose();
        });
    }
    
    // ====================
    // Chat Handler
    // ====================
    async function handleChatSubmit(e) {
        e.preventDefault();
        
        const text = userInput.value.trim();
        if (!text) return;
        
        // Disable input while processing
        userInput.disabled = true;
        sendButton.disabled = true;
        
        // Add user message to UI
        appendMessage(text, 'user');
        userInput.value = '';
        messageCounter++;
        updateStats();
        
        // Show typing indicator
        const typingId = showTypingIndicator();
        
        try {
            // Send to backend
            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    message: text,
                    user_id: USER_ID 
                })
            });
            
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Remove typing indicator
            removeTypingIndicator(typingId);
            
            // Add AI response
            appendMessage(data.response, 'ai', data.emotion);
            
            // Track emotion
            if (data.emotion) {
                emotions.push(data.emotion);
            }
            
            // Update dashboard
            updateDashboard(data);
            
        } catch (error) {
            console.error('❌ API Error:', error);
            removeTypingIndicator(typingId);
            appendMessage(
                "I'm having trouble connecting to the server. Please check if the backend is running and try again.",
                'ai',
                'error'
            );
        } finally {
            // Re-enable input
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus();
        }
    }
    
    // ====================
    // Message Functions
    // ====================
    function appendMessage(text, sender, metadata = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message`;
        
        if (metadata === 'error' || (typeof metadata === 'string' && metadata.toLowerCase() === 'critical')) {
            msgDiv.classList.add('crisis-message');
        }
        
        const iconClass = sender === 'user' ? 'fa-user' : 'fa-robot';
        const timestamp = new Date().toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        msgDiv.innerHTML = `
            <div class="avatar">
                <i class="fa-solid ${iconClass}"></i>
            </div>
            <div class="message-wrapper">
                <div class="message-content">
                    <p>${escapeHTML(text)}</p>
                </div>
                <span class="message-time">${timestamp}</span>
            </div>
        `;
        
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }
    
    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai-message';
        typingDiv.id = id;
        
        typingDiv.innerHTML = `
            <div class="avatar">
                <i class="fa-solid fa-robot"></i>
            </div>
            <div class="message-wrapper">
                <div class="typing-indicator">
                    <div class="dots">
                        <div class="dot"></div>
                        <div class="dot"></div>
                        <div class="dot"></div>
                    </div>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
        return id;
    }
    
    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }
    
    function scrollToBottom() {
        const container = document.querySelector('.chat-container');
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 0);
    }
    
    // ====================
    // Dashboard Update
    // ====================
    function updateDashboard(data) {
        // Update emotion badge
        if (data.emotion) {
            updateEmotionBadge(data.emotion);
        }
        
        // Update suggestions
        if (data.suggestion) {
            addSuggestion(data.suggestion);
        }
        
        // Update mood chart
        loadMoodStats();
    }
    
    function updateEmotionBadge(emotion) {
        let icon = 'fa-face-meh';
        const emotionLower = emotion.toLowerCase();
        
        if (emotionLower.includes('joy') || emotionLower.includes('happy')) {
            icon = 'fa-face-smile';
        } else if (emotionLower.includes('sad')) {
            icon = 'fa-face-frown';
        } else if (emotionLower.includes('ang')) {
            icon = 'fa-face-angry';
        } else if (emotionLower.includes('fear') || emotionLower.includes('anxi')) {
            icon = 'fa-face-flushed';
        } else if (emotionLower.includes('critical') || emotionLower.includes('emergency')) {
            icon = 'fa-triangle-exclamation';
            emotionBadge.classList.add('crisis');
            emotionBadge.innerHTML = `
                <i class="fa-solid ${icon}"></i>
                <span>EMERGENCY - REACH OUT</span>
            `;
            return;
        }
        
        emotionBadge.classList.remove('crisis');
        emotionBadge.innerHTML = `
            <i class="fa-solid ${icon}"></i>
            <span>${escapeHTML(emotion)}</span>
        `;
    }
    
    function addSuggestion(suggestion) {
        const div = document.createElement('div');
        div.className = 'suggestion-item';
        div.innerHTML = `
            <i class="fa-solid fa-lightbulb"></i>
            <span>${escapeHTML(suggestion)}</span>
        `;
        
        suggestionsList.innerHTML = '';
        suggestionsList.appendChild(div);
        
        // Fade in animation
        div.style.animation = 'fadeInUp 0.3s ease';
    }
    
    // ====================
    // Statistics
    // ====================
    function updateStats() {
        messageCount.textContent = messageCounter;
    }
    
    function loadInitialData() {
        // Initialize with default values
        updateStats();
        
        // Try to load trend analysis
        loadTrendAnalysis();
        
        // Hide loading overlay after a short delay
        setTimeout(() => {
            loadingOverlay.style.display = 'none';
        }, 1500);
    }
    
    let moodChart = null;
    
    async function loadMoodStats() {
        try {
            const response = await fetch(`${API_BASE}/mood-stats`);
            const stats = await response.json();
            
            if (stats.total === 0) {
                document.getElementById('trends-placeholder').style.display = 'block';
                if (moodChart) moodChart.destroy();
                document.getElementById('mood-chart').style.display = 'none';
                return;
            }
            
            // Hide placeholder and show chart
            document.getElementById('trends-placeholder').style.display = 'none';
            document.getElementById('mood-chart').style.display = 'block';
            
            // Display mood trend
            const trendText = document.getElementById('mood-trend-text');
            const trendEmoji = {
                'improving': '📈 Your mood is improving!',
                'challenging': '📉 Things seem challenging. You\'re not alone.',
                'stressed': '😰 You seem stressed. Take a moment to breathe.',
                'stable': '😌 Your mood is stable and balanced.'
            };
            
            trendText.textContent = trendEmoji[stats.mood_trend] || trendEmoji['stable'];
            
            // Prepare chart data
            const emotionLabels = Object.keys(stats.emotions);
            const emotionData = Object.values(stats.emotions);
            const emotionColors = {
                'happy': '#FFD700',
                'sad': '#4169E1',
                'angry': '#FF6347',
                'anxious': '#FFA500',
                'fear': '#8B008B',
                'neutral': '#A9A9A9'
            };
            
            const colors = emotionLabels.map(e => emotionColors[e] || '#999');
            
            // Create or update chart
            const ctx = document.getElementById('mood-chart').getContext('2d');
            
            if (moodChart) {
                moodChart.destroy();
            }
            
            moodChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: emotionLabels.map(e => capitalize(e)),
                    datasets: [{
                        data: emotionData,
                        backgroundColor: colors,
                        borderColor: '#1a1a1a',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#999',
                                font: { size: 11 },
                                padding: 8
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const value = context.parsed;
                                    const percentage = ((value / stats.total) * 100).toFixed(1);
                                    return `${context.label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
            
        } catch (e) {
            console.log("Could not load mood stats:", e);
        }
    }
    
    function capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
    
    async function loadTrendAnalysis() {
        try {
            // Load initial mood stats
            await loadMoodStats();
        } catch (e) {
            console.log("Could not load trend analysis:", e);
        }
    }
    
    // ====================
    // Clear Chat
    // ====================
    function handleClearChat() {
        if (confirm('Are you sure you want to clear this conversation?')) {
            chatMessages.innerHTML = '';
            messageCounter = 0;
            emotions = [];
            updateStats();
            
            // Add welcome message
            setTimeout(() => {
                appendMessage(
                    "👋 Chat cleared! Let's start fresh. How are you feeling today?",
                    'ai'
                );
            }, 300);
        }
    }
    
    // ====================
    // Settings Modal
    // ====================
    function handleSettingsOpen() {
        settingsModal.classList.remove('hidden');
    }
    
    function handleSettingsClose() {
        settingsModal.classList.add('hidden');
    }
    
    // ====================
    // Utility Functions
    // ====================
    function escapeHTML(str) {
        if (typeof str !== 'string') return '';
        
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        
        return str.replace(/[&<>"']/g, char => map[char]);
    }
    
    function showLoading(show = true) {
        if (show) {
            loadingOverlay.classList.add('active');
        } else {
            loadingOverlay.classList.remove('active');
        }
    }
    
    // ====================
    // Keyboard Shortcuts
    // ====================
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K to focus input
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            userInput.focus();
        }
        
        // Escape to close modal
        if (e.key === 'Escape') {
            handleSettingsClose();
        }
    });
    
    // ====================
    // Export for debugging
    // ====================
    window.MindGuardian = {
        USER_ID,
        messageCounter,
        emotions,
        API_BASE
    };
    
    console.log('✅ MindGuardian Frontend Ready');
});

