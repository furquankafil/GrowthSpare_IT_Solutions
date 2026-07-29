/**
 * GrowthSpare IT Solutions - Theme Synchronization Engine
 * Executes instantly inside header blocks to prevent visual FOUC (Flash of Unstyled Content).
 * Maps, enforces, and locks Dark/Light mode selections inside local browser storage.
 */

(function () {
    const cachedTheme = localStorage.getItem('theme');

    // Site defaults to Light Mode. Dark Mode is applied ONLY when the user has
    // explicitly chosen it before (persisted in localStorage by the toggle
    // buttons in navbar.html / dashboard/base_dashboard.html). OS-level
    // "prefers-color-scheme" is intentionally NOT consulted, per spec:
    // Dark Mode should only ever activate via an explicit user click.
    if (cachedTheme === 'dark') {
        document.documentElement.classList.add('dark');
        document.documentElement.classList.remove('light');
    } else {
        document.documentElement.classList.remove('dark');
        document.documentElement.classList.add('light');
    }
})();

// NOTE: Click-to-toggle handlers for #navbar-theme-toggle, #mobile-theme-toggle,
// and #dashboard-theme-toggle are implemented directly in navbar.html and
// dashboard/base_dashboard.html (they already correctly add/remove both classes
// and persist the choice). This file's sole job is the pre-paint FOUC guard above.