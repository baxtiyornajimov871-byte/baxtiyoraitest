/**
 * BaxtiyorAiTest - Chat Core JavaScript
 * Modern chat functionality, conversation history, and AI streaming effects.
 */

let currentConversationId = null;
let conversations = [];
let isProcessing = false;
let typingIndicatorElement = null;

function initChat() {
    const input = document.getElementById('message-input');
    const search = document.getElementById('chat-search');
    const form = document.getElementById('chat-form');
    const newChatButton = document.getElementById('new-chat-btn');
    const newChatButtonTop = document.getElementById('new-chat-btn-top');

    if (input) {
        input.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 180) + 'px';
        });

        input.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        });
    }

    if (search) {
        search.addEventListener('input', function () {
            const query = this.value.toLowerCase();
            renderConversationList(query);
        });
    }

    if (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            sendMessage();
        });
    }

    if (newChatButton) {
        newChatButton.addEventListener('click', createNewChat);
    }

    if (newChatButtonTop) {
        newChatButtonTop.addEventListener('click', createNewChat);
    }

    loadConversations();
}

async function loadConversations() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/chat/', {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        conversations = Array.isArray(data.conversations) ? data.conversations : [];
        renderConversationList();

        if (conversations.length) {
            const active = conversations.find((conv) => conv.id === currentConversationId) || conversations[0];
            selectConversation(active.id);
        } else {
            showEmptyState();
        }
    } catch (error) {
        console.error('Unable to load conversations', error);
        showEmptyState();
    }
}

function renderConversationList(filter = '') {
    const list = document.getElementById('conversations-list');
    list.innerHTML = '';

    const filtered = conversations.filter((conversation) => {
        const title = (conversation.title || 'Yangi suhbat').toLowerCase();
        return title.includes(filter.toLowerCase());
    });

    if (!filtered.length) {
        list.innerHTML = `<div class="rounded-3xl border border-dashed border-white/10 bg-white/5 p-6 text-center text-sm text-gray-400">Hech qanday suhbat topilmadi.</div>`;
        return;
    }

    filtered.forEach((conversation) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = `conversation-item ${conversation.id === currentConversationId ? 'active' : ''}`;
        button.innerHTML = `
            <div class="conversation-title">${escapeHtml(conversation.title || 'Yangi suhbat')}</div>
            <div class="conversation-snippet">${escapeHtml(conversation.last_message || 'Suhbatni boshlash uchun yozing...')}</div>
        `;
        button.addEventListener('click', () => selectConversation(conversation.id));
        list.appendChild(button);
    });
}

async function selectConversation(conversationId) {
    if (isProcessing || !conversationId) {
        return;
    }

    currentConversationId = conversationId;
    renderConversationList();
    await loadConversation(conversationId);
    closeSidebar();
}

async function loadConversation(conversationId) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/chat/${conversationId}`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok && data.conversation) {
            const conversation = data.conversation;
            document.getElementById('chat-title').textContent = conversation.title || 'Yangi suhbat';
            document.getElementById('chat-subtitle').textContent = `${conversation.model || 'llama3-70b-8192'} • ${conversation.provider || 'Groq'}`;
            renderMessages(Array.isArray(data.messages) ? data.messages : []);
        } else {
            showEmptyState();
        }
    } catch (error) {
        console.error('Unable to load conversation', error);
        showEmptyState();
    }
}

function renderMessages(messages) {
    const container = document.getElementById('messages');
    container.innerHTML = '';
    hideEmptyState();

    if (!messages.length) {
        showEmptyState();
        return;
    }

    messages.forEach((message) => {
        addMessageToUI(message.role, message.content, message);
    });

    scrollToBottom();
}

async function sendMessage() {
    if (isProcessing) {
        return;
    }

    const input = document.getElementById('message-input');
    const prompt = input.value.trim();

    if (!prompt) {
        return;
    }

    if (!currentConversationId) {
        const created = await createNewChat();
        if (!created) {
            return;
        }
    }

    addMessageToUI('user', prompt);
    input.value = '';
    input.style.height = 'auto';
    scrollToBottom();

    showTypingIndicator();
    isProcessing = true;

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`/api/chat/${currentConversationId}/message`, {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: prompt,
                model: 'llama3-70b-8192',
                temperature: 0.7
            })
        });

        const data = await response.json();

        removeTypingIndicator();

        if (response.ok && data.ai_message) {
            simulateStreamingResponse(data.ai_message.content, data.ai_message);
        } else {
            const message = data.error || 'Server bilan aloqa o‘rnatilmadi. Iltimos qayta urinib ko‘ring.';
            addMessageToUI('assistant', message, null, true);
        }
    } catch (error) {
        console.error('Send message error:', error);
        removeTypingIndicator();
        addMessageToUI('assistant', 'Server bilan aloqa o‘rnatilmadi. Iltimos qayta urinib ko‘ring.', null, true);
    } finally {
        isProcessing = false;
        scrollToBottom();
    }
}

function simulateStreamingResponse(content, messageData = null) {
    const messagesContainer = document.getElementById('messages');
    hideEmptyState();

    const wrapper = document.createElement('div');
    wrapper.className = 'flex justify-start message-wrapper';

    const avatar = document.createElement('div');
    avatar.className = 'w-10 h-10 rounded-3xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-sm font-semibold text-white';
    avatar.textContent = 'AI';

    const bubble = document.createElement('div');
    bubble.className = 'message assistant max-w-[80%]';

    const markdown = document.createElement('div');
    markdown.className = 'markdown';
    markdown.textContent = '';
    bubble.appendChild(markdown);

    if (messageData) {
        const meta = document.createElement('div');
        meta.className = 'message-meta';
        meta.innerHTML = `
            <span>${escapeHtml(messageData.model || 'AI')}</span>
            <button type="button" class="copy-btn" onclick="copyMessage(this)"><i class="fas fa-copy"></i></button>
        `;
        bubble.appendChild(meta);
    }

    wrapper.appendChild(avatar);
    wrapper.appendChild(bubble);
    messagesContainer.appendChild(wrapper);
    scrollToBottom();

    let index = 0;
    const interval = setInterval(() => {
        if (index >= content.length) {
            clearInterval(interval);
            markdown.innerHTML = marked ? marked.parse(content) : escapeHtml(content);
            scrollToBottom();
            return;
        }

        index += 2;
        markdown.textContent = content.slice(0, index);
        scrollToBottom();
    }, 20);
}

function addMessageToUI(role, content, messageData = null, isError = false) {
    const messagesContainer = document.getElementById('messages');
    const emptyState = document.getElementById('empty-state');

    if (emptyState) {
        emptyState.style.display = 'none';
    }

    const wrapper = document.createElement('div');
    wrapper.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'} message-wrapper`;

    const bubble = document.createElement('div');
    bubble.className = `message ${role === 'user' ? 'user max-w-[75%]' : 'assistant max-w-[80%]'}`;

    const markdown = document.createElement('div');
    markdown.className = 'markdown';

    if (role === 'user') {
        markdown.textContent = content;
    } else {
        markdown.innerHTML = marked ? marked.parse(content) : escapeHtml(content);
    }

    bubble.appendChild(markdown);

    if (messageData || isError) {
        const meta = document.createElement('div');
        meta.className = 'message-meta';
        meta.innerHTML = `
            <span>${escapeHtml(messageData?.model || (isError ? 'Xato' : 'AI'))}</span>
            <button type="button" class="copy-btn" onclick="copyMessage(this)"><i class="fas fa-copy"></i></button>
        `;
        bubble.appendChild(meta);
    }

    wrapper.appendChild(bubble);
    messagesContainer.appendChild(wrapper);
}

function showTypingIndicator() {
    if (typingIndicatorElement) {
        return;
    }

    const messagesContainer = document.getElementById('messages');
    const wrapper = document.createElement('div');
    wrapper.id = 'typing-indicator';
    wrapper.className = 'flex justify-start message-wrapper';

    const bubble = document.createElement('div');
    bubble.className = 'typing-indicator';
    bubble.innerHTML = `
        <span>AI javob yozmoqda</span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
    `;

    wrapper.appendChild(bubble);
    messagesContainer.appendChild(wrapper);
    typingIndicatorElement = wrapper;
    scrollToBottom();
}

function removeTypingIndicator() {
    if (!typingIndicatorElement) {
        return;
    }

    typingIndicatorElement.remove();
    typingIndicatorElement = null;
}

async function createNewChat() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/chat/new', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok && data.conversation) {
            conversations.unshift(data.conversation);
            currentConversationId = data.conversation.id;
            renderConversationList();
            selectConversation(currentConversationId);
            return true;
        }

        return false;
    } catch (error) {
        console.error('Unable to create chat', error);
        return false;
    }
}

function copyMessage(button) {
    const messageText = button.closest('.message').querySelector('.markdown').innerText;
    navigator.clipboard.writeText(messageText).then(() => {
        const original = button.innerHTML;
        button.innerHTML = '✅';
        setTimeout(() => {
            button.innerHTML = original;
        }, 1400);
    });
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar?.classList.toggle('open');
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (window.innerWidth < 1024 && sidebar?.classList.contains('open')) {
        sidebar.classList.remove('open');
    }
}

function showEmptyState() {
    const emptyState = document.getElementById('empty-state');
    if (emptyState) {
        emptyState.style.display = 'flex';
    }
}

function hideEmptyState() {
    const emptyState = document.getElementById('empty-state');
    if (emptyState) {
        emptyState.style.display = 'none';
    }
}

function escapeHtml(text) {
    if (typeof text !== 'string') {
        return '';
    }

    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

window.initChat = initChat;
window.sendMessage = sendMessage;
window.createNewChat = createNewChat;
window.copyMessage = copyMessage;
window.toggleSidebar = toggleSidebar;
