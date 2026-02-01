/**
 * navbar.js
 * Handles dynamic navbar state (Login vs Profile) and active link highlighting.
 */

document.addEventListener('DOMContentLoaded', async () => {
    // Accessibility: Detect tabbing for focus outlines
    window.addEventListener('keydown', e => {
        if (e.key === 'Tab') {
            document.body.classList.add('user-is-tabbing');
        }
    });
    window.addEventListener('mousedown', () => {
        document.body.classList.remove('user-is-tabbing');
    });

    // Image Fade-In Observer
    const imgObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.classList.add('img-loaded');
                observer.unobserve(img);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('img').forEach(img => {
        img.classList.add('img-loading');
        imgObserver.observe(img);
    });

    // 1. Highlight Active Link
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (currentPath === href || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
            link.classList.add('active-link'); // Support both class naming conventions
        } else {
            link.classList.remove('active');
            link.classList.remove('active-link');
        }
    });

    // 2. Handle Auth State
    const authItem = document.getElementById('nav-auth-item');
    if (!authItem) return; // Exit if navbar doesn't have the auth item container

    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();

        if (data.authenticated) {
            // User is logged in
            const name = data.profile?.name ? data.profile.name.split(' ')[0] : (data.user_id || 'User');

            authItem.innerHTML = `
                <div style="display: flex; align-items: center; gap: 12px;">
                    <a href="/profile_setup.html" class="user-badge" style="display: flex; align-items: center; gap: 8px; text-decoration: none; color: var(--brand-diet); border: 1px solid var(--border-color, #e4e4e7); padding: 6px 16px; border-radius: 20px; background: rgba(22, 163, 74, 0.05); font-weight: 600;">
                        <i class="fas fa-user-circle"></i>
                        <span>${name}</span>
                    </a>
                    <a href="#" onclick="logout(); return false;" class="logout-btn" style="text-decoration: none; color: var(--accent, #dc2626); font-weight: 600; font-size: 0.9rem; padding: 6px 12px; border-radius: 20px; transition: all 0.3s ease; display: flex; align-items: center; gap: 6px; background: rgba(220, 38, 38, 0.05);">
                        <i class="fas fa-sign-out-alt"></i>
                        <span>Logout</span>
                    </a>
                </div>
            `;
        } else {
            // User is not logged in (Default state is usually Login button, so simpler to leave it or reset it)
            authItem.innerHTML = `
                <a href="/login" class="btn btn-primary" style="padding: 10px 24px; border-radius: 50px; background: var(--brand-diet); color: #fff; font-weight: 600; text-decoration: none; transition: all 0.3s ease; box-shadow: 0 4px 10px rgba(22, 163, 74, 0.2);">
                    🔐 Login
                </a>
            `;
        }
    } catch (error) {
        console.error('Navbar auth check error:', error);
    }
});

// 3. Add Scroll Effect for "Sexy" Floating Navbar
window.addEventListener('scroll', () => {
    const nav = document.querySelector('.navbar');
    if (nav) {
        if (window.scrollY > 20) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    }
});

// 4. Mobile Toggle Logic
document.addEventListener('DOMContentLoaded', () => {
    const navToggle = document.getElementById('navToggle');
    const navLinksList = document.getElementById('navLinks');

    if (navToggle && navLinksList) {
        navToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            navLinksList.classList.toggle('active');
            navToggle.classList.toggle('active');
        });

        // Close on link click
        navLinksList.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinksList.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });

        // Close on click outside
        document.addEventListener('click', (e) => {
            if (!navLinksList.contains(e.target) && !navToggle.contains(e.target)) {
                navLinksList.classList.remove('active');
                navToggle.classList.remove('active');
            }
        });
    }
});

/**
 * Global Logout Function
 */
/**
 * Global Logout Function with Premium Modal
 */
async function logout() {
    // 1. Create Modal HTML if doesn't exist
    let modal = document.getElementById('logoutModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'logoutModal';
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-card">
                <div class="modal-icon">
                    <i class="fas fa-sign-out-alt"></i>
                </div>
                <h3 class="modal-title">Terminate Session?</h3>
                <p class="modal-text">Are you sure you want to log out from DietNotify? Any unsaved changes on this page will be lost.</p>
                <div class="modal-footer">
                    <button class="modal-btn btn-cancel" id="logoutCancel">Keep Me In</button>
                    <button class="modal-btn btn-confirm" id="logoutConfirm">Yes, Logout</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);

        // Add event listeners
        document.getElementById('logoutCancel').addEventListener('click', () => {
            modal.classList.remove('active');
            setTimeout(() => { modal.style.display = 'none'; }, 300);
        });

        document.getElementById('logoutConfirm').addEventListener('click', executeLogout);

        // Close on click outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
                setTimeout(() => { modal.style.display = 'none'; }, 300);
            }
        });
    }

    // 2. Show Modal
    modal.style.display = 'flex';
    setTimeout(() => { modal.classList.add('active'); }, 10);
}

/**
 * Execute the actual logout API call
 */
async function executeLogout() {
    const confirmBtn = document.getElementById('logoutConfirm');
    const originalText = confirmBtn.innerText;
    confirmBtn.innerText = 'Logging out...';
    confirmBtn.disabled = true;

    try {
        const response = await fetch('/api/auth/logout', { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            localStorage.removeItem('fullDietData');
            window.location.href = '/login';
        }
    } catch (e) {
        console.error('Logout failed:', e);
        window.location.href = '/login';
    }
}
