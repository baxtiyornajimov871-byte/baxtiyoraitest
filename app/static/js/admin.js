/**
 * BaxtiyorAiTest - Admin Dashboard JavaScript
 * Advanced admin panel functionality
 */

console.log('%c🛡️ Admin panel initialized', 'color: #eab308; font-weight: bold;');

// Load Admin Dashboard
async function loadAdminDashboard() {
    try {
        const token = localStorage.getItem('access_token');
        
        const response = await fetch('/api/admin/dashboard', {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Admin access required');
        }

        const data = await response.json();
        
        // Fill statistics
        document.getElementById('total-users').textContent = data.system_stats.total_users.toLocaleString();
        document.getElementById('total-chats').textContent = data.system_stats.total_conversations.toLocaleString();
        document.getElementById('total-messages').textContent = data.system_stats.total_messages.toLocaleString();
        document.getElementById('total-bots').textContent = data.system_stats.total_bots.toLocaleString();

        // Render Provider Stats
        renderProviderStats(data.provider_stats);
        
        // Render Recent Activity
        renderRecentActivity(data.recent_activities);
        
        // Render Top Bots
        renderTopBots(data.top_bots);

    } catch (error) {
        console.error('Admin dashboard load failed:', error);
        showToast('Admin panelga kirish huquqi yo‘q yoki server xatosi', 'error');
    }
}

// Render Provider Statistics
function renderProviderStats(stats) {
    const container = document.getElementById('provider-stats');
    if (!container) return;

    let html = '';
    stats.forEach(stat => {
        const percent = Math.min(Math.round((stat.tokens || 100) / 1000), 100);
        html += `
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-4">
                    <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center text-white font-bold">
                        ${stat.provider === 'groq' ? '⚡' : '🤗'}
                    </div>
                    <div>
                        <p class="font-medium">${stat.provider.toUpperCase()}</p>
                        <p class="text-xs text-gray-500">${stat.messages} ta xabar</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="font-mono text-sm">${stat.tokens.toLocaleString()} token</p>
                    <div class="w-32 h-2 bg-gray-700 rounded-full mt-2 overflow-hidden">
                        <div class="h-full bg-gradient-to-r from-blue-400 to-cyan-400" style="width: ${percent}%"></div>
                    </div>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

// Render Recent Activity
function renderRecentActivity(activities) {
    const container = document.getElementById('recent-activity');
    if (!container) return;

    let html = '';
    activities.forEach(activity => {
        html += `
            <div class="flex gap-4 items-start border-b border-white/5 pb-4 last:border-none last:pb-0">
                <div class="text-2xl mt-0.5">
                    ${activity.event_type === 'chat_message' ? '💬' : 
                      activity.event_type === 'bot_created' ? '🤖' : '👤'}
                </div>
                <div class="flex-1">
                    <p class="text-sm">${activity.description}</p>
                    <p class="text-[10px] text-gray-500 mt-1">
                        ${new Date(activity.created_at).toLocaleTimeString('uz-UZ')}
                    </p>
                </div>
            </div>
        `;
    });
    container.innerHTML = html || '<p class="text-gray-500 text-center py-8">Hozircha faollik yo‘q</p>';
}

// Render Top Bots
function renderTopBots(bots) {
    const container = document.getElementById('top-bots');
    if (!container) return;

    container.innerHTML = bots.map(bot => `
        <div class="bg-gray-800/50 rounded-2xl p-5 hover:bg-gray-700/50 transition-all cursor-pointer">
            <div class="text-3xl mb-3">🤖</div>
            <h4 class="font-semibold text-sm mb-1 line-clamp-1">${bot.name}</h4>
            <p class="text-xs text-gray-400 line-clamp-2 mb-4">${bot.description}</p>
            <div class="flex justify-between items-center text-[10px]">
                <span class="text-emerald-400">${bot.usage_count} ishlatish</span>
                <span class="text-purple-400">${bot.likes_count} ❤️</span>
            </div>
        </div>
    `).join('');
}

// Refresh Dashboard
function refreshDashboard() {
    showToast('Ma\'lumotlar yangilanmoqda...', 'info');
    loadAdminDashboard();
}

// Make functions global
window.loadAdminDashboard = loadAdminDashboard;
window.refreshDashboard = refreshDashboard;