/**
 * BaxtiyorAiTest - Bot Management JavaScript
 * Custom Bot creation, marketplace, and creator features
 */

console.log('%c🤖 Bot system initialized', 'color: #c026d3; font-weight: bold;');

// Create New Bot
async function createBot() {
    const name = document.getElementById('bot-name').value.trim();
    const description = document.getElementById('bot-description').value.trim();
    const systemPrompt = document.getElementById('system-prompt').value.trim();
    const greeting = document.getElementById('greeting-message').value.trim();
    const temperature = parseFloat(document.getElementById('temperature').value);
    const category = document.getElementById('bot-category').value;
    const visibility = document.getElementById('visibility').value;

    if (!name || !description || !systemPrompt) {
        showToast('Iltimos, majburiy maydonlarni to‘ldiring', 'error');
        return;
    }

    try {
        const token = localStorage.getItem('access_token');
        
        const response = await fetch('/api/bots/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                name: name,
                description: description,
                system_prompt: systemPrompt,
                greeting_message: greeting || "Salom! Men sizga qanday yordam bera olaman?",
                temperature: temperature,
                category: category,
                visibility: visibility
            })
        });

        const data = await response.json();

        if (response.ok) {
            showToast(`Bot "${name}" muvaffaqiyatli yaratildi! 🎉`, 'success');
            setTimeout(() => {
                window.location.href = '/api/bots/my-bots';
            }, 1200);
        } else {
            showToast(data.error || 'Bot yaratishda xatolik yuz berdi', 'error');
        }
    } catch (error) {
        console.error(error);
        showToast('Server bilan aloqa o‘rnatilmadi', 'error');
    }
}

// Preview Bot (Demo)
function previewBot() {
    const name = document.getElementById('bot-name').value.trim() || "Demo Bot";
    showToast(`${name} botining oldindan ko‘rinishi (demo)`, 'info');
}

// Load Creator Dashboard
async function loadCreatorDashboard() {
    try {
        const token = localStorage.getItem('access_token');
        const res = await fetch('/api/creator/dashboard', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
            const data = await res.json();
            
            document.getElementById('total-bots').textContent = data.stats.total_bots;
            document.getElementById('total-usage').textContent = data.stats.total_usage;
            document.getElementById('total-likes').textContent = data.stats.total_likes;
            
            renderMyBots(data.bots);
        }
    } catch (e) {
        console.error(e);
    }
}

// Render User's Bots
function renderMyBots(bots) {
    const container = document.getElementById('my-bots-grid');
    if (!container) return;
    
    container.innerHTML = bots.map(bot => `
        <div class="bg-gray-900 border border-white/10 rounded-3xl p-6 hover:border-purple-500/30 transition-all group">
            <div class="flex items-center gap-4 mb-4">
                <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center text-2xl">
                    🤖
                </div>
                <div class="flex-1">
                    <h4 class="font-semibold">${bot.name}</h4>
                    <p class="text-xs text-gray-500">${bot.category || 'Umumiy'}</p>
                </div>
            </div>
            <p class="text-sm text-gray-400 line-clamp-2 mb-6">${bot.description}</p>
            <div class="flex justify-between text-xs">
                <span class="text-emerald-400">${bot.usage_count} foydalanish</span>
                <span class="text-purple-400">${bot.likes_count} like</span>
            </div>
        </div>
    `).join('');
}

// Load Marketplace
async function loadMarketplace() {
    try {
        const res = await fetch('/api/public/bots');
        const data = await res.json();
        
        renderBots(data.bots, 'all-bots-grid');
    } catch (e) {
        console.error(e);
    }
}

function renderBots(bots, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = bots.map(bot => `
        <div onclick="viewBot('${bot.slug}')" 
             class="bg-gray-900 border border-white/10 rounded-3xl overflow-hidden hover:border-purple-500/50 transition-all cursor-pointer group">
            <div class="h-40 bg-gradient-to-br from-purple-900 to-pink-900 flex items-center justify-center text-6xl">
                🤖
            </div>
            <div class="p-6">
                <h4 class="font-semibold text-lg mb-1 group-hover:text-purple-400 transition-colors">${bot.name}</h4>
                <p class="text-sm text-gray-400 line-clamp-2 mb-4">${bot.description}</p>
                <div class="flex items-center justify-between text-xs">
                    <span class="text-gray-500">@${bot.owner?.username}</span>
                    <span class="text-emerald-400">${bot.usage_count} ishlatildi</span>
                </div>
            </div>
        </div>
    `).join('');
}

function viewBot(slug) {
    window.location.href = `/api/public/bots/${slug}`;
}

// Search Bots
function searchBots() {
    // Real search will be implemented with debounce
    console.log('Searching bots...');
}

// Filter Bots
function filterBots() {
    console.log('Filtering bots...');
}

// Make functions available globally
window.createBot = createBot;
window.previewBot = previewBot;
window.loadCreatorDashboard = loadCreatorDashboard;
window.loadMarketplace = loadMarketplace;
window.viewBot = viewBot;
window.searchBots = searchBots;
window.filterBots = filterBots;