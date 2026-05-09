/**
 * BaxtiyorAiTest - Chat Core JavaScript
 * Real-time chat functionality, message handling, and AI interaction
 */

let currentConversationId = null;
let isProcessing = false;

// Initialize Chat
function initChat() {
    console.log('💬 Chat system initialized');
    
    const input = document.getElementById('message-input');
    if (input) {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Auto resize textarea
        input.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 180) + 'px';
        });
    }
    
    // Load last conversation or create new
    const path = window.location.pathname;
    if (path.includes('/chat/')) {
        const id = path.split('/').pop();
        if (id && !isNaN(id)) {
            loadConversation(parseInt(id));
        }
    } else {
        // Default: show empty state
        showEmptyState();
    }
}

// Send Message
async function sendMessage() {
    if (isProcessing) return;
    
    const input = document.getElementById('message-input');
    const content = input.value.trim();
    
    if (!content) return;
    if (!currentConversationId) {
        await createNewChat();
    }
    
    isProcessing = true;
    
    // Add user message to UI
    addMessageToUI('user', content);
    input.value = '';
    input.style.height = 'auto';
    
    // Scroll to bottom
    scrollToBottom();
    
    try {
        const token = localStorage.getItem('access_token');
        
        const response = await fetch(`/api/chat/${currentConversationId}/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                content: content,
                model: "llama3-70b-8192",
                temperature: 0.7
            })
        });
        
        const data = await response.json();
        
        if (data.ai_message) {
            addMessageToUI('assistant', data.ai_message.content, data.ai_message);
        } else if (data.error) {
            addMessageToUI('assistant', `Xatolik: ${data.error}`, null, true);
        }
        
    } catch (error) {
        console.error('Send message error:', error);
        addMessageToUI('assistant', 'Server bilan aloqa o‘rnatilmadi. Iltimos qayta urinib ko‘ring.', null, true);
    } finally {
        isProcessing = false;
        scrollToBottom();
    }
}

// Add Message to UI
function addMessageToUI(role, content, messageData = null, isError = false) {
    const messagesContainer = document.getElementById('messages');
    const emptyState = document.getElementById('empty-state');
    
    if (emptyState) emptyState.style.display = 'none';
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'} message-wrapper`;
    
    let html = '';
    
    if (role === 'user') {
        html = `
            <div class="message user max-w-[75%]">
                <div class="markdown">${content}</div>
            </div>
        `;
    } else {
        html = `
            <div class="flex gap-4 max-w-[80%]">
                <div class="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex-shrink-0 flex items-center justify-center text-white text-sm font-bold">AI</div>
                <div class="message assistant flex-1">
                    <div class="markdown">${marked ? marked.parse(content) : content}</div>
                    ${messageData ? `
                    <div class="flex justify-between items-center mt-4 text-[10px] text-gray-500">
                        <span>${messageData.model || 'AI'}</span>
                        <button onclick="copyMessage(this)" class="copy-btn text-purple-400 hover:text-purple-300">
                            <i class="fas fa-copy"></i>
                        </button>
                    </div>` : ''}
                </div>
            </div>
        `;
    }
    
    messageDiv.innerHTML = html;
    messagesContainer.appendChild(messageDiv);
}

// Scroll to bottom
function scrollToBottom() {
    const messages = document.getElementById('messages');
    if (messages) {
        messages.scrollTop = messages.scrollHeight;
    }
}

// Show empty state
function showEmptyState() {
    const empty = document.getElementById('empty-state');
    if (empty) empty.style.display = 'flex';
}

// Create New Chat
async function createNewChat() {
    try {
        const token = localStorage.getItem('access_token');
        const res = await fetch('/api/chat/new', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await res.json();
        if (data.conversation) {
            currentConversationId = data.conversation.id;
            document.getElementById('chat-title').textContent = data.conversation.title;
        }
    } catch (e) {
        console.error(e);
    }
}

// Load Conversation
async function loadConversation(id) {
    currentConversationId = id;
    // Load messages logic (to be expanded)
    console.log(`Loading conversation ${id}`);
}

// Copy message
function copyMessage(btn) {
    const messageText = btn.closest('.message').querySelector('.markdown').innerText;
    navigator.clipboard.writeText(messageText).then(() => {
        const original = btn.innerHTML;
        btn.innerHTML = '✅';
        setTimeout(() => btn.innerHTML = original, 1500);
    });
}

// Make functions global
window.sendMessage = sendMessage;
window.createNewChat = createNewChat;
window.initChat = initChat;
window.copyMessage = copyMessage;