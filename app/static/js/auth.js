/**
 * BaxtiyorAiTest - Authentication JavaScript
 * Login, Register, and Auth Flow Management
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Login Form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value.trim();
            
            if (!email || !password) {
                showToast('Email va parolni kiriting', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    localStorage.setItem('access_token', data.access_token);
                    showToast('Muvaffaqiyatli kirdingiz! 🎉', 'success');
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 800);
                } else {
                    showToast(data.error || 'Login yoki parol xato', 'error');
                }
            } catch (error) {
                console.error(error);
                showToast('Server bilan aloqa o‘rnatilmadi', 'error');
            }
        });
    }

    // Register Form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value.trim();
            const display_name = document.getElementById('display_name').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value.trim();
            const password_confirm = document.getElementById('password_confirm').value.trim();
            
            if (password !== password_confirm) {
                showToast('Parollar mos kelmadi', 'error');
                return;
            }
            
            if (password.length < 8) {
                showToast('Parol kamida 8 ta belgidan iborat bo‘lishi kerak', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username,
                        email,
                        password,
                        display_name: display_name || username
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showToast('Hisob muvaffaqiyatli yaratildi! Endi kirishingiz mumkin.', 'success');
                    setTimeout(() => {
                        window.location.href = '/api/auth/login';
                    }, 1500);
                } else {
                    showToast(data.error || 'Ro‘yxatdan o‘tishda xatolik', 'error');
                }
            } catch (error) {
                console.error(error);
                showToast('Server bilan aloqa o‘rnatilmadi', 'error');
            }
        });
    }
    
    console.log('%c🔐 Auth system loaded successfully', 'color: #a855f7; font-weight: bold;');
});

// Global showToast function (agar main.js da bo'lmasa)
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.style.position = 'fixed';
    toast.style.bottom = '24px';
    toast.style.right = '24px';
    toast.style.padding = '16px 24px';
    toast.style.borderRadius = '16px';
    toast.style.color = 'white';
    toast.style.zIndex = '9999';
    toast.style.boxShadow = '0 10px 15px -3px rgb(0 0 0 / 0.3)';
    toast.style.display = 'flex';
    toast.style.alignItems = 'center';
    toast.style.gap = '12px';
    toast.style.minWidth = '280px';
    
    if (type === 'success') {
        toast.style.backgroundColor = '#10b981';
    } else if (type === 'error') {
        toast.style.backgroundColor = '#ef4444';
    } else {
        toast.style.backgroundColor = '#3b82f6';
    }
    
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
    }, 3500);
}

// Make showToast globally available
window.showToast = showToast;