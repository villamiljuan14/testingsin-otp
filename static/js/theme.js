/**
 * Enviart Theme Management System
 * Modularized for cross-page consistency and zero-inline policy.
 */

(function() {
    // 1. Immediate Theme Application (FOUC Prevention)
    const initTheme = () => {
        const savedTheme = localStorage.getItem('color-theme');
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme === 'dark' || (!savedTheme && systemDark)) {
            document.documentElement.classList.add('dark');
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            document.documentElement.setAttribute('data-theme', 'light');
        }
    };

    initTheme();

    // 2. Global Event Listeners
    document.addEventListener('DOMContentLoaded', () => {
        const themeToggleBtn = document.getElementById('theme-toggle');
        const darkIcon = document.getElementById('theme-toggle-dark-icon') || document.getElementById('moon-icon');
        const lightIcon = document.getElementById('theme-toggle-light-icon') || document.getElementById('sun-icon');

        const updateIcons = (isDark) => {
            if (isDark) {
                if (lightIcon) lightIcon.classList.remove('hidden');
                if (darkIcon) darkIcon.classList.add('hidden');
            } else {
                if (darkIcon) darkIcon.classList.remove('hidden');
                if (lightIcon) lightIcon.classList.add('hidden');
            }
        };

        // Sync initial icon state
        updateIcons(document.documentElement.classList.contains('dark'));

        if (themeToggleBtn) {
            themeToggleBtn.addEventListener('click', () => {
                const isDark = document.documentElement.classList.toggle('dark');
                const newTheme = isDark ? 'dark' : 'light';
                
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('color-theme', newTheme);
                updateIcons(isDark);

                // Optional: Trigger custom event for other components (like charts)
                document.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }));
            });
        }
    });

    // Handle system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!localStorage.getItem('color-theme')) {
            const newTheme = e.matches ? 'dark' : 'light';
            document.documentElement.classList.toggle('dark', e.matches);
            document.documentElement.setAttribute('data-theme', newTheme);
        }
    });
})();
