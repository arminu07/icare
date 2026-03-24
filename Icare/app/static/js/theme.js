// Theme Management System
// Handles light/dark mode toggling with localStorage persistence

function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme);
}

function applyTheme(theme) {
    const body = document.body;
    
    if (theme === 'light') {
        body.classList.remove('dark-mode');
        body.classList.add('light-mode');
        localStorage.setItem('theme', 'light');
        updateThemeButton('sun', 'Light');
    } else {
        body.classList.remove('light-mode');
        body.classList.add('dark-mode');
        localStorage.setItem('theme', 'dark');
        updateThemeButton('moon', 'Dark');
    }
    
    // Set cookie for server-side theme awareness
    document.cookie = `theme=${theme}; max-age=${365 * 24 * 60 * 60}; path=/`;
}

function toggleTheme() {
    const body = document.body;
    const isLight = body.classList.contains('light-mode');
    const newTheme = isLight ? 'dark' : 'light';
    applyTheme(newTheme);
}

function updateThemeButton(icon, text) {
    const buttons = document.querySelectorAll('.theme-toggle-btn');
    buttons.forEach(btn => {
        const iconElement = btn.querySelector('i');
        const textSpan = btn.querySelector('span');
        
        if (iconElement) {
            iconElement.className = `fas fa-${icon}`;
        }
        
        if (textSpan) {
            textSpan.textContent = text;
        }
    });
}

// Load theme on page load
document.addEventListener('DOMContentLoaded', loadTheme);
