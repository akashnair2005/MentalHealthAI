document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const emotionBadge = document.getElementById('current-emotion');
    const suggestionsList = document.getElementById('suggestions-list');
    const trendAnalysis = document.getElementById('trend-analysis');

    const API_BASE = '/api';
    const TEST_USER_ID = "local_dev_user";

    // Load initial mood history
    fetchHistory();

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text) return;

        // 1. Add user message to UI
        appendMessage(text, 'user');
        userInput.value = '';
        
        // 2. Add typing indicator
        const typingId = showTypingIndicator();

        try {
            // 3. Send request to backend
            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text, user_id: TEST_USER_ID })
            });

            const data = await response.json();
            
            // 4. Remove typing indicator
            removeTypingIndicator(typingId);

            // 5. Add AI response to UI
            appendMessage(data.response, 'ai', data.is_crisis);

            // 6. Update UI elements (Emotion & Suggestions)
            updateDashboard(data);

            // Refresh history
            fetchHistory();

        } catch (error) {
            console.error('API Error:', error);
            removeTypingIndicator(typingId);
            appendMessage("I'm having trouble connecting to the server. Please try again later.", 'ai');
        }
    });

    function appendMessage(text, sender, isCrisis = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message new-message`;
        if (isCrisis) msgDiv.classList.add('crisis-message');

        const iconClass = sender === 'user' ? 'fa-user' : 'fa-robot';
        
        msgDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid ${iconClass}"></i></div>
            <div class="message-content">
                <p>${escapeHTML(text)}</p>
            </div>
        `;
        
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.className = `message ai-message new-message`;
        typingDiv.id = id;
        
        typingDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="typing-indicator">
                <div class="dots">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
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

    function updateDashboard(data) {
        // Update Emotion Badge
        if (data.is_crisis) {
            emotionBadge.className = 'emotion-badge crisis';
            emotionBadge.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> <span>EMERGENCY</span>`;
        } else {
            emotionBadge.className = 'emotion-badge';
            let icon = 'fa-face-meh';
            const eLower = data.emotion.toLowerCase();
            if (eLower.includes('joy') || eLower.includes('happy')) icon = 'fa-face-smile';
            else if (eLower.includes('sad')) icon = 'fa-face-frown';
            else if (eLower.includes('ang')) icon = 'fa-face-angry';
            else if (eLower.includes('anxi') || eLower.includes('fear')) icon = 'fa-face-flushed';
            
            emotionBadge.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${escapeHTML(data.emotion)}</span>`;
        }

        // Update Suggestions
        if (data.suggestions && data.suggestions.length > 0) {
            suggestionsList.innerHTML = '';
            data.suggestions.forEach(sug => {
                const div = document.createElement('div');
                div.className = 'suggestion-item';
                div.textContent = sug;
                suggestionsList.appendChild(div);
            });
        }
    }

    async function fetchHistory() {
        try {
            const res = await fetch(`${API_BASE}/mood_history?user_id=${TEST_USER_ID}`);
            if(!res.ok) return;
            const data = await res.json();
            
            if (data.trend_analysis) {
                trendAnalysis.innerHTML = `<p>${escapeHTML(data.trend_analysis)}</p>`;
            }
        } catch (e) {
            console.log("Could not fetch history:", e);
        }
    }

    function scrollToBottom() {
        const container = document.querySelector('.chat-container');
        container.scrollTop = container.scrollHeight;
    }

    function escapeHTML(str) {
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }
});
