/**
 * BaxtiyorAiTest - Main JavaScript
 * Core functionality, utilities, and global helpers
 */

console.log('%c🚀 BaxtiyorAiTest v1.0.0 initialized', 'color: #a855f7; font-weight: bold;');

// Global Variables
let currentUser = null;
let currentConversationId = null;

// Utility Functions
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-6 right-6 px-6 py-4 rounded-2xl text-sm font-medium shadow-2xl z-50 flex items-center gap-3 
                       ${type === 'success' ? 'bg-emerald-600' : type === 'error' ? 'bg-red-600' : 'bg-gray-700'}`;
    toast.innerHTML = `
        ${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'} 
        <span>${message}</span>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.transition = 'all 0.4s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

// Toggle Sidebar (Mobile)
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('hidden');
    }
}

// Logout
async function logout() {
    if (confirm('Tizimdan chiqmoqchimisiz?')) {
        try {
            const response = await fetch('/api/auth/logout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (response.ok) {
                localStorage.removeItem('access_token');
                window.location.href = '/api/auth/login';
            }
        } catch (e) {
            localStorage.removeItem('access_token');
            window.location.href = '/api/auth/login';
        }
    }
}

// Check Auth Status
async function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        if (!window.location.pathname.includes('/auth')) {
            window.location.href = '/api/auth/login';
        }
        return false;
    }
    
    try {
        const res = await fetch('/api/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
            currentUser = await res.json();
            updateUserUI();
            return true;
        } else {
            localStorage.removeItem('access_token');
            window.location.href = '/api/auth/login';
            return false;
        }
    } catch (e) {
        console.error('Auth check failed', e);
        return false;
    }
}

function updateUserUI() {
    if (!currentUser) return;
    
    // Update navbar avatar and name
    const navUsername = document.getElementById('nav-username');
    const navAvatar = document.getElementById('nav-avatar');
    
    if (navUsername) navUsername.textContent = currentUser.display_name || currentUser.username;
    if (navAvatar) navAvatar.textContent = (currentUser.display_name || currentUser.username)[0].toUpperCase();
}

// Global Search
function globalSearch() {
    const query = document.getElementById('global-search')?.value.trim();
    if (query && query.length > 2) {
        showToast(`Qidirilmoqda: "${query}"...`, 'info');
        // Future: Implement global search across chats and bots
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM fully loaded');
    
    // Check authentication on protected pages
    if (!window.location.pathname.includes('/auth') && 
        !window.location.pathname.includes('/public')) {
        checkAuth();
    }
    
    // Tailwind script already loaded via CDN
    console.log('%cBaxtiyorAiTest UI initialized successfully', 'color: #22c55e; font-size: 13px;');
});

// Make functions globally available
window.showToast = showToast;
window.toggleSidebar = toggleSidebar;
window.logout = logout;
window.globalSearch = globalSearch;