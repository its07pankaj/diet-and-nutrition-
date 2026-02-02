/**
 * DietNotify Notification Manager
 * Handles push notification setup, registration, and management
 * Uses Firebase Cloud Messaging for web push notifications
 */

class NotificationManager {
    constructor() {
        this.messaging = null;
        this.currentToken = null;
        this.isSupported = false;
        this.isEnabled = false;

        // Check browser support
        this.checkSupport();
        this.injectStyles();
    }

    /**
     * Inject premium styles for modals and toasts
     */
    injectStyles() {
        if (document.getElementById('notification-premium-styles')) return;

        const style = document.createElement('style');
        style.id = 'notification-premium-styles';
        style.textContent = `
            /* Premium Notification Modal */
            .notification-modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.6);
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                z-index: 99999;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                animation: modalFadeIn 0.3s ease forwards;
            }
            
            @keyframes modalFadeIn {
                to { opacity: 1; }
            }
            
            .notification-modal {
                background: linear-gradient(145deg, rgba(255,255,255,0.95), rgba(240,240,240,0.9));
                border-radius: 28px;
                padding: 40px;
                max-width: 420px;
                width: 90%;
                box-shadow: 
                    0 25px 80px rgba(0,0,0,0.3),
                    0 0 0 1px rgba(255,255,255,0.5) inset,
                    0 0 100px rgba(22, 163, 74, 0.1);
                text-align: center;
                transform: scale(0.8) translateY(30px);
                animation: modalSlideIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
                position: relative;
                overflow: hidden;
            }
            
            .notification-modal::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 6px;
                background: linear-gradient(90deg, #16a34a, #22d3ee, #16a34a);
                background-size: 200% 100%;
                animation: shimmer 2s infinite linear;
            }
            
            @keyframes shimmer {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }
            
            @keyframes modalSlideIn {
                to { transform: scale(1) translateY(0); }
            }
            
            .notification-modal-icon {
                width: 90px;
                height: 90px;
                background: linear-gradient(135deg, #16a34a, #22d3ee);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 25px;
                box-shadow: 0 15px 40px rgba(22, 163, 74, 0.3);
                animation: bellRing 1s ease-in-out infinite;
                animation-delay: 0.5s;
            }
            
            @keyframes bellRing {
                0%, 100% { transform: rotate(0deg); }
                10% { transform: rotate(15deg); }
                20% { transform: rotate(-15deg); }
                30% { transform: rotate(10deg); }
                40% { transform: rotate(-10deg); }
                50% { transform: rotate(5deg); }
                60% { transform: rotate(0deg); }
            }
            
            .notification-modal-icon i {
                font-size: 40px;
                color: white;
            }
            
            .notification-modal h2 {
                font-size: 1.8rem;
                font-weight: 800;
                color: #1a1a1a;
                margin-bottom: 12px;
                letter-spacing: -0.5px;
            }
            
            .notification-modal p {
                font-size: 1.05rem;
                color: #555;
                line-height: 1.6;
                margin-bottom: 30px;
            }
            
            .notification-modal-features {
                display: flex;
                flex-direction: column;
                gap: 12px;
                margin-bottom: 30px;
                text-align: left;
                padding: 20px;
                background: rgba(22, 163, 74, 0.05);
                border-radius: 16px;
                border: 1px solid rgba(22, 163, 74, 0.1);
            }
            
            .notification-modal-feature {
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 0.95rem;
                color: #333;
            }
            
            .notification-modal-feature i {
                color: #16a34a;
                font-size: 1.1rem;
                width: 24px;
            }
            
            .notification-modal-buttons {
                display: flex;
                gap: 12px;
            }
            
            .notification-modal-btn {
                flex: 1;
                padding: 16px 24px;
                border-radius: 16px;
                font-size: 1rem;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s ease;
                border: none;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }
            
            .notification-modal-btn.primary {
                background: linear-gradient(135deg, #16a34a, #22c55e);
                color: white;
                box-shadow: 0 8px 25px rgba(22, 163, 74, 0.35);
            }
            
            .notification-modal-btn.primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 35px rgba(22, 163, 74, 0.45);
            }
            
            .notification-modal-btn.secondary {
                background: rgba(0,0,0,0.05);
                color: #666;
            }
            
            .notification-modal-btn.secondary:hover {
                background: rgba(0,0,0,0.1);
            }
            
            .notification-modal-btn.loading {
                pointer-events: none;
                opacity: 0.7;
            }
            
            .notification-modal-btn .spinner {
                width: 18px;
                height: 18px;
                border: 2px solid rgba(255,255,255,0.3);
                border-top-color: white;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            /* Toast Notifications */
            .notification-toast {
                position: fixed;
                bottom: 30px;
                right: 30px;
                background: linear-gradient(135deg, rgba(20,20,20,0.95), rgba(40,40,40,0.9));
                color: white;
                padding: 18px 28px;
                border-radius: 16px;
                box-shadow: 0 15px 50px rgba(0,0,0,0.4);
                z-index: 100000;
                animation: toastSlideIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), toastFadeOut 0.4s ease 3s forwards;
                max-width: 380px;
                border: 1px solid rgba(255,255,255,0.1);
            }
            
            .toast-content {
                display: flex;
                flex-direction: column;
                gap: 6px;
            }
            
            .toast-content strong {
                font-size: 1.1rem;
                font-weight: 700;
            }
            
            .toast-content span {
                font-size: 0.95rem;
                opacity: 0.85;
            }
            
            @keyframes toastSlideIn {
                from { transform: translateX(120%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            @keyframes toastFadeOut {
                to { opacity: 0; transform: translateX(120%); }
            }
            
            /* Success state */
            .notification-modal.success .notification-modal-icon {
                background: linear-gradient(135deg, #22c55e, #16a34a);
                animation: none;
            }
            
            .notification-modal.success h2 {
                color: #16a34a;
            }
            
            /* Mobile responsive */
            @media (max-width: 480px) {
                .notification-modal {
                    padding: 30px 25px;
                    border-radius: 24px;
                }
                
                .notification-modal h2 {
                    font-size: 1.5rem;
                }
                
                .notification-modal-buttons {
                    flex-direction: column;
                }
                
                .notification-toast {
                    left: 15px;
                    right: 15px;
                    bottom: 15px;
                }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Show premium permission modal
     */
    showPermissionModal() {
        return new Promise((resolve) => {
            // Create overlay
            const overlay = document.createElement('div');
            overlay.className = 'notification-modal-overlay';
            overlay.innerHTML = `
                <div class="notification-modal">
                    <div class="notification-modal-icon">
                        <i class="fas fa-bell"></i>
                    </div>
                    <h2>🍽️ Never Miss a Meal!</h2>
                    <p>Get timely reminders for your scheduled meals and stay on track with your nutrition goals.</p>
                    
                    <div class="notification-modal-features">
                        <div class="notification-modal-feature">
                            <i class="fas fa-clock"></i>
                            <span>Smart reminders 5 minutes before each meal</span>
                        </div>
                        <div class="notification-modal-feature">
                            <i class="fas fa-utensils"></i>
                            <span>See what's on your plate at a glance</span>
                        </div>
                        <div class="notification-modal-feature">
                            <i class="fas fa-toggle-on"></i>
                            <span>Easy to disable anytime from settings</span>
                        </div>
                    </div>
                    
                    <div class="notification-modal-buttons">
                        <button class="notification-modal-btn secondary" id="notifDeny">
                            Maybe Later
                        </button>
                        <button class="notification-modal-btn primary" id="notifAllow">
                            <i class="fas fa-bell"></i>
                            Enable Reminders
                        </button>
                    </div>
                </div>
            `;

            document.body.appendChild(overlay);

            // Button handlers
            const allowBtn = overlay.querySelector('#notifAllow');
            const denyBtn = overlay.querySelector('#notifDeny');
            const modal = overlay.querySelector('.notification-modal');

            allowBtn.addEventListener('click', async () => {
                // Show loading state
                allowBtn.innerHTML = '<div class="spinner"></div> Enabling...';
                allowBtn.classList.add('loading');
                denyBtn.style.display = 'none';

                resolve(true);
            });

            denyBtn.addEventListener('click', () => {
                overlay.style.animation = 'modalFadeIn 0.3s ease reverse forwards';
                setTimeout(() => overlay.remove(), 300);
                resolve(false);
            });

            // Store overlay reference for later
            this.activeModal = overlay;
        });
    }

    /**
     * Update modal to success state
     */
    showModalSuccess(scheduledMeals = 0) {
        if (!this.activeModal) return;

        const modal = this.activeModal.querySelector('.notification-modal');
        const icon = modal.querySelector('.notification-modal-icon');
        const title = modal.querySelector('h2');
        const content = modal.querySelector('p');
        const features = modal.querySelector('.notification-modal-features');
        const buttons = modal.querySelector('.notification-modal-buttons');

        modal.classList.add('success');
        icon.innerHTML = '<i class="fas fa-check"></i>';
        title.textContent = '✅ You\'re All Set!';
        content.textContent = scheduledMeals > 0
            ? `${scheduledMeals} meal reminders scheduled. You'll receive notifications before each meal.`
            : 'Notifications enabled! When you have an active diet plan, you\'ll receive meal reminders.';
        features.style.display = 'none';
        buttons.innerHTML = `
            <button class="notification-modal-btn primary" style="flex: 1;" onclick="this.closest('.notification-modal-overlay').remove()">
                <i class="fas fa-thumbs-up"></i>
                Got It!
            </button>
        `;
    }

    /**
     * Close the modal
     */
    closeModal() {
        if (this.activeModal) {
            this.activeModal.style.animation = 'modalFadeIn 0.3s ease reverse forwards';
            setTimeout(() => {
                this.activeModal.remove();
                this.activeModal = null;
            }, 300);
        }
    }

    /**
     * Check if browser supports push notifications
     */
    checkSupport() {
        this.isSupported = 'Notification' in window &&
            'serviceWorker' in navigator &&
            'PushManager' in window;

        if (!this.isSupported) {
            console.log('[Notifications] Browser does not support push notifications');
        }
        return this.isSupported;
    }

    /**
     * Initialize Firebase Messaging
     */
    async init() {
        console.log('[Notifications] Initializing manager...');
        if (!this.isSupported) {
            return false;
        }

        try {
            const response = await fetch('/api/notifications/firebase-config');
            const data = await response.json();

            if (!data.config || data.config.apiKey === 'YOUR_API_KEY') {
                console.log('[Notifications] Firebase not configured yet');
                return false;
            }

            if (typeof firebase !== 'undefined') {
                if (!firebase.apps.length) {
                    firebase.initializeApp(data.config);
                }

                this.messaging = firebase.messaging();

                // Add cache busting to force update
                const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js?v=' + Date.now());
                console.log('[Notifications] Service worker registered');
                this.swRegistration = registration;

                this.messaging.onMessage((payload) => {
                    console.log('[Notifications] Foreground message received:', payload);

                    // Professional Handling: Use Service Worker registration to show notification
                    // This ensures consistent behavior with background notifications
                    const title = payload.notification.title || 'DietNotify Reminder';
                    const body = payload.notification.body || 'Time to eat!';
                    const timestamp = new Date().getTime();

                    // 1. ALWAYS show an in-app Toast (Guarantees visibility if OS blocks notifications)
                    this.showToast(`🔔 ${title.replace('🍽️ ', '')}`, body);

                    const options = {
                        body: body,
                        icon: '/static/img/logo.svg',
                        badge: '/static/img/logo.svg',
                        // AGGRESSIVE VIBRATION: Long-Short-Long
                        vibrate: [500, 200, 500],
                        requireInteraction: true,
                        dir: 'auto',
                        lang: 'en-US',
                        // Unique tag prevents overwriting unless we want to
                        tag: 'diet-notification-' + timestamp,
                        // High priority for mobile
                        timestamp: timestamp,
                        actions: [
                            { action: 'view', title: 'View Plan' },
                            { action: 'close', title: 'Close' }
                        ],
                        data: payload.data
                    };

                    // 2. Try standard Service Worker API (Native Notification)
                    if (this.swRegistration && this.swRegistration.showNotification) {
                        this.swRegistration.showNotification(title, options)
                            .then(() => console.log('[Notifications] Displayed via SW'))
                            .catch(err => {
                                console.error('[Notifications] SW display failed:', err);
                                // Fallback to window Notification API
                                new Notification(title, options);
                            });
                    } else {
                        // Fallback checking registration
                        navigator.serviceWorker.getRegistration().then(reg => {
                            if (reg) {
                                reg.showNotification(title, options);
                            } else {
                                new Notification(title, options);
                            }
                        });
                    }

                    // Also play a sound if desired (optional but requested "professional" feel usually implies sound)
                    // const audio = new Audio('/static/sounds/notification.mp3');
                    // audio.play().catch(e => console.log('Audio play failed', e));
                });

                return true;
            } else {
                console.log('[Notifications] Firebase SDK not loaded');
                return false;
            }
        } catch (error) {
            console.error('[Notifications] Init error:', error);
            return false;
        }
    }

    /**
     * Request notification permission
     */
    async requestPermission() {
        if (!this.isSupported) {
            this.showToast('❌ Not Supported', 'Push notifications are not supported in your browser');
            return false;
        }

        try {
            // Check if already granted
            if (Notification.permission === 'granted') {
                console.log('[Notifications] Permission already granted');
                return true;
            }

            // Check if blocked (can't request again)
            if (Notification.permission === 'denied') {
                console.log('[Notifications] Permission blocked by user');
                this.closeModal();
                this.showToast('🔕 Blocked', 'Notifications are blocked. Enable in browser settings.');
                return false;
            }

            // Request permission (only if 'default')
            const permission = await Notification.requestPermission();
            console.log('[Notifications] Permission result:', permission);

            if (permission === 'granted') {
                console.log('[Notifications] Permission granted');
                return true;
            } else {
                console.log('[Notifications] Permission denied or dismissed');
                this.closeModal();
                return false;
            }
        } catch (error) {
            console.error('[Notifications] Permission error:', error);
            return false;
        }
    }

    /**
     * Get FCM device token
     */
    async getToken() {
        console.log('[Notifications] getToken called, messaging:', !!this.messaging);

        if (!this.messaging) {
            console.log('[Notifications] No messaging, calling init()...');
            await this.init();
        }

        if (!this.messaging) {
            console.log('[Notifications] Still no messaging after init');
            return null;
        }

        try {
            console.log('[Notifications] Fetching firebase config...');
            const configResponse = await fetch('/api/notifications/firebase-config');
            const configData = await configResponse.json();
            console.log('[Notifications] Config received, vapidKey exists:', !!configData.vapidKey);

            if (!configData.vapidKey || configData.vapidKey === 'YOUR_VAPID_PUBLIC_KEY') {
                console.log('[Notifications] VAPID key not configured');
                return null;
            }

            // Ensure service worker is ready and active
            let registration = this.swRegistration || await navigator.serviceWorker.getRegistration('/');

            if (!registration) {
                console.log('[Notifications] No SW registration found, attempting to register...');
                registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');
            }

            // Wait for service worker to be active
            if (registration.installing || registration.waiting) {
                console.log('[Notifications] Service worker is installing/waiting, waiting for activation...');
                await new Promise((resolve) => {
                    const sw = registration.installing || registration.waiting;
                    sw.addEventListener('statechange', (e) => {
                        if (e.target.state === 'activated') {
                            console.log('[Notifications] Service worker activated!');
                            resolve();
                        }
                    });
                });
            }

            console.log('[Notifications] Service worker state:', registration.active ? registration.active.state : 'null');

            console.log('[Notifications] Requesting FCM token...');
            const token = await this.messaging.getToken({
                vapidKey: configData.vapidKey,
                serviceWorkerRegistration: registration
            });

            if (token) {
                console.log('[Notifications] Token obtained:', token.substring(0, 20) + '...');
                this.currentToken = token;
                return token;
            } else {
                console.log('[Notifications] No token returned from getToken()');
                return null;
            }
        } catch (error) {
            console.error('[Notifications] Token error:', error);
            const errorMsg = error.message || 'Check console';
            const errorCode = error.code || 'no-code';
            console.error('[Notifications] Error details:', errorMsg, errorCode);
            this.showToast(`❌ Token Error (${errorCode})`, errorMsg);
            return null;
        }
    }

    /**
     * Register token with backend
     */
    async registerToken(token = null) {
        const tokenToRegister = token || this.currentToken;

        if (!tokenToRegister) {
            console.log('[Notifications] No token to register');
            return { success: false };
        }

        try {
            const response = await fetch('/api/notifications/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    token: tokenToRegister,
                    device_info: {
                        userAgent: navigator.userAgent,
                        platform: navigator.platform,
                        timestamp: new Date().toISOString()
                    }
                })
            });

            const data = await response.json();

            if (data.success) {
                console.log('[Notifications] Token registered successfully');
                this.isEnabled = true;
                return data;
            } else {
                console.error('[Notifications] Registration failed:', data.error);
                return { success: false };
            }
        } catch (error) {
            console.error('[Notifications] Registration error:', error);
            return { success: false };
        }
    }

    /**
     * Hard Reset: Delete token and unregister SW to force fresh connection
     */
    async hardReset() {
        console.log('[Notifications] Performing HARD RESET...');
        try {
            // 1. Delete token (This is the critical missing step)
            if (this.messaging) {
                try {
                    await this.messaging.deleteToken();
                    console.log('[Notifications] Token deleted.');
                } catch (e) {
                    console.warn('[Notifications] Token delete failed (could be already goone):', e);
                }
            }

            // 2. Clear stored token
            this.currentToken = null;

            // 3. Unregister SW
            if (this.swRegistration) {
                await this.swRegistration.unregister();
                console.log('[Notifications] SW unregistered.');
            } else {
                const reg = await navigator.serviceWorker.getRegistration();
                if (reg) await reg.unregister();
            }

            // 4. Force Re-Init
            await this.init();

            // 5. Get NEW Token
            const newToken = await this.getToken();

            // 6. Register NEW Token
            if (newToken) {
                await this.registerToken(newToken);
                return true;
            }
            return false;

        } catch (e) {
            console.error('[Notifications] Hard reset failed:', e);
            throw e;
        }
    }

    /**
     * Unregister token (disable notifications)
     */
    async unregisterToken() {
        if (!this.currentToken) {
            return true;
        }

        try {
            const response = await fetch('/api/notifications/unregister', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: this.currentToken })
            });

            const data = await response.json();

            if (data.success) {
                this.isEnabled = false;
                this.currentToken = null;
                this.showToast('🔕 Disabled', 'Meal reminders turned off');
                return true;
            }
            return false;
        } catch (error) {
            console.error('[Notifications] Unregister error:', error);
            return false;
        }
    }

    /**
     * Update notification preferences
     */
    async updatePreferences(prefs) {
        try {
            const response = await fetch('/api/notifications/preferences', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(prefs)
            });

            const data = await response.json();
            if (!response.ok) {
                console.error('[Notifications] Preferences update failed:', data.error);
                return { success: false, error: data.error };
            }
            return data;
        } catch (error) {
            console.error('[Notifications] Preferences update error:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Get current preferences
     */
    async getPreferences() {
        try {
            const response = await fetch('/api/notifications/preferences');
            const data = await response.json();
            if (!response.ok) {
                console.error('[Notifications] Get preferences failed:', data.error);
                return null;
            }
            return data;
        } catch (error) {
            console.error('[Notifications] Get preferences error:', error);
            return null;
        }
    }

    /**
     * Get notification status
     */
    async getStatus() {
        try {
            const response = await fetch('/api/notifications/status');
            const data = await response.json();
            if (!response.ok) return { success: false, error: data.error || 'Status check failed' };
            return data;
        } catch (error) {
            console.error('[Notifications] Status error:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Send test notification
     */
    async sendTest() {
        try {
            // 1. Immediate Local Check
            // 1. Immediate Local Check (Professional Verification)
            if (Notification.permission === 'granted') {
                const now = new Date().toLocaleTimeString();

                // Use SW if possible for local test too
                if (this.swRegistration) {
                    this.swRegistration.showNotification(`🔔 Verified: Mobile Ready`, {
                        body: `Your device is ready to receive alerts. (Local Test: ${now})`,
                        icon: '/static/img/logo.svg',
                        vibrate: [100, 50, 100],
                        tag: 'local-verify-' + Date.now()
                    });
                } else {
                    new Notification(`🔔 Verified: Mobile Ready`, {
                        body: `Your device is ready to receive alerts. (Local Test: ${now})`,
                        icon: '/static/img/logo.svg'
                    });
                }
            } else {
                this.showToast('⚠ Permission Issue', 'Browser has not granted notification access.');
                return false;
            }

            // Ensure we have the current token for THIS device
            if (!this.currentToken) {
                await this.getToken();
            }

            const response = await fetch('/api/notifications/test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: this.currentToken }) // Send valid token or null
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('✅ Signal Sent', 'Server processed the request. Watch for "Verification: Server".');
                return true;
            } else {
                this.showToast('❌ Server Error', data.error || 'Could not send test');
                return false;
            }
        } catch (error) {
            console.error('[Notifications] Test error:', error);
            return false;
        }
    }

    /**
     * Enable notifications with premium modal (full flow)
     */
    async enable() {
        // Show beautiful modal first
        const userWants = await this.showPermissionModal();

        if (!userWants) {
            return false;
        }

        // Helper to show debug on modal
        const showDebug = (msg) => {
            console.log('[Notifications]', msg);
            const modal = this.activeModal?.querySelector('.notification-modal');
            if (modal) {
                const btn = modal.querySelector('.notification-modal-btn.primary');
                if (btn) btn.innerHTML = `<div class="spinner"></div> ${msg}`;
            }
        };

        // Wrap entire process in timeout to prevent infinite stuck
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => reject(new Error('timeout')), 15000);
        });

        const enableProcess = async () => {
            try {
                // 1. Initialize Firebase
                showDebug('Step 1: Init Firebase...');
                const initOk = await this.init();
                if (!initOk) {
                    this.closeModal();
                    this.showToast('⚠️ Setup Needed', 'Firebase not configured. Check admin settings.');
                    return false;
                }

                // 2. Request permission (browser prompt)
                showDebug('Step 2: Requesting permission...');
                const permOk = await this.requestPermission();
                if (!permOk) {
                    showDebug('Permission denied or dismissed');
                    return false;
                }

                // 3. Get token
                showDebug('Step 3: Getting token...');
                const token = await this.getToken();
                if (!token) {
                    this.closeModal();
                    this.showToast('❌ Error', 'Could not get notification token');
                    return false;
                }

                // 4. Register with backend
                showDebug('Step 4: Registering...');
                const regResult = await this.registerToken(token);

                // 5. Update preferences if successful
                if (regResult.success) {
                    await this.updatePreferences({ enabled: true });

                    // Show success state in modal
                    this.showModalSuccess(regResult.scheduled_meals || 0);
                    return true;
                }

                this.closeModal();
                this.showToast('❌ Error', 'Could not register for notifications');
                return false;
            } catch (err) {
                showDebug('Error: ' + err.message);
                throw err;
            }
        };

        try {
            return await Promise.race([enableProcess(), timeoutPromise]);
        } catch (error) {
            console.error('[Notifications] Enable failed:', error);
            this.closeModal();
            if (error.message === 'timeout') {
                this.showToast('⏱️ Timeout', 'Notification setup took too long. Check browser console for errors.');
            } else {
                this.showToast('❌ Error', error.message || 'Failed to enable notifications');
            }
            return false;
        }
    }

    /**
     * Disable notifications
     */
    async disable() {
        await this.updatePreferences({ enabled: false });
        await this.unregisterToken();
        this.isEnabled = false;
    }

    /**
     * Show a toast notification on the page
     */
    showToast(title, message) {
        const toast = document.createElement('div');
        toast.className = 'notification-toast';
        toast.innerHTML = `
            <div class="toast-content">
                <strong>${title}</strong>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(toast);

        setTimeout(() => toast.remove(), 3500);
    }
}

// Global instance
window.notificationManager = new NotificationManager();
