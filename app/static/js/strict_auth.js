/**
 * strict_auth.js
 * Enforces strict authentication on protected pages.
 * Redirects to /login if user is not authenticated.
 */

(async function checkAuth() {
    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();

        if (!data.authenticated) {
            console.warn('User not authenticated. Redirecting to login...');

            // Store current URL to redirect back after login (optional future enhancement)
            sessionStorage.setItem('redirect_url', window.location.href);

            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        // Fallback: If verification fails, staying on page might be safer 
        // OR redirecting if strict security is needed. 
        // For now, let's redirect on error to be safe.
        window.location.href = '/login';
    }
})();
