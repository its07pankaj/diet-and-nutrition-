/**
 * Diety Assistant Manager
 * Handles the floating chat interface and communication with Gemma 3 4B.
 */
class DietyAssistant {
    constructor() {
        this.isOpen = false;
        this.chatMessages = document.getElementById('dietyMessages');
        this.chatInput = document.getElementById('dietyInput');
        this.container = document.getElementById('dietyContainer');
        this.toggleBtn = document.getElementById('dietyToggle');

        // Dragging state
        this.isDragging = false;
        this.dragStartX = 0;
        this.dragStartY = 0;
        this.initialRight = 25;
        this.initialBottom = 25;

        this.init();
    }

    init() {
        console.log('[Diety] Initializing Assistant...');

        // Ensure container is at the very root (prepend to body for maximum visual priority)
        if (this.container && this.container.parentElement !== document.body) {
            document.body.prepend(this.container);
        }

        // Force fixed follow even in complex layouts
        this.container.style.position = 'fixed';
        this.container.style.zIndex = '2147483647';
        this.container.style.transform = 'translateZ(0)'; // Hardware context

        // Click to toggle
        this.toggleBtn.addEventListener('click', (e) => {
            if (this.isDragging) return; // Don't toggle if we just finished dragging
            this.toggle();
        });

        const closeBtn = document.getElementById('dietyClose');
        if (closeBtn) {
            closeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggle();
            });
        }

        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // DRAG LOGIC
        this.setupDragging();

        // Initial welcome message or History Load
        this.loadHistory();
    }

    loadHistory() {
        try {
            const history = JSON.parse(localStorage.getItem('diety_chat_history') || '[]');
            if (history.length > 0) {
                console.log(`[Diety] Loaded ${history.length} messages from history`);
                history.forEach(msg => this.addMessage(msg.text, msg.sender, false)); // false = don't save again
            } else {
                this.addMessage("Hi! I'm Diety. How can I help you with your health goals today?", 'ai', true);
            }
        } catch (e) {
            console.error('[Diety] Error loading history:', e);
            this.addMessage("Hi! I'm Diety. How can I help you with your health goals today?", 'ai', true);
        }
    }

    saveHistory(text, sender) {
        try {
            const history = JSON.parse(localStorage.getItem('diety_chat_history') || '[]');
            history.push({ text, sender, timestamp: Date.now() });

            // Keep last 50 messages
            if (history.length > 50) {
                history.shift();
            }

            localStorage.setItem('diety_chat_history', JSON.stringify(history));
        } catch (e) {
            console.error('[Diety] Error saving history:', e);
        }
    }

    setupDragging() {
        const handleStart = (e) => {
            const clientX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
            const clientY = e.type === 'touchstart' ? e.touches[0].clientY : e.clientY;

            this.isDragging = false; // Reset on every start
            this.dragStartX = clientX;
            this.dragStartY = clientY;

            // Get current computed style
            const style = window.getComputedStyle(this.container);
            this.initialRight = parseInt(style.right);
            this.initialBottom = parseInt(style.bottom);

            document.addEventListener('mousemove', handleMove);
            document.addEventListener('mouseup', handleEnd);
            document.addEventListener('touchmove', handleMove, { passive: false });
            document.addEventListener('touchend', handleEnd);
        };

        const handleMove = (e) => {
            // Disable dragging if chat is open on mobile (full screen mode)
            if (this.isOpen && window.innerWidth <= 768) return;

            const clientX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
            const clientY = e.type === 'touchmove' ? e.touches[0].clientY : e.clientY;

            const dx = clientX - this.dragStartX;
            const dy = clientY - this.dragStartY;

            if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
                this.isDragging = true;
                e.preventDefault(); // Prevent scrolling while dragging
            }

            if (this.isDragging) {
                const newRight = this.initialRight - dx;
                const newBottom = this.initialBottom - dy;

                // Boundaries (keep it within screen-ish)
                this.container.style.right = `${Math.max(0, Math.min(window.innerWidth - 60, newRight))}px`;
                this.container.style.bottom = `${Math.max(0, Math.min(window.innerHeight - 60, newBottom))}px`;
            }
        };

        const handleEnd = () => {
            document.removeEventListener('mousemove', handleMove);
            document.removeEventListener('mouseup', handleEnd);
            document.removeEventListener('touchmove', handleMove);
            document.removeEventListener('touchend', handleEnd);

            // Re-enable interactions after a brief delay if we were dragging
            if (this.isDragging) {
                setTimeout(() => { this.isDragging = false; }, 10);
            }
        };

        this.toggleBtn.addEventListener('mousedown', handleStart);
        this.toggleBtn.addEventListener('touchstart', handleStart);
    }

    toggle() {
        this.isOpen = !this.isOpen;
        this.container.classList.toggle('active', this.isOpen);

        const badge = document.getElementById('dietyBadge');
        const container = this.container;
        const chatWindow = document.getElementById('dietyChatWindow');
        const header = document.querySelector('.diety-header');
        const messages = document.getElementById('dietyMessages');
        const inputArea = document.querySelector('.diety-input');

        if (this.isOpen) {
            if (badge) badge.style.display = 'none';
            document.body.style.overflow = 'hidden';
            document.body.style.position = 'fixed';
            document.body.style.width = '100%';
            document.body.style.height = '100%';

            // Mobile keyboard handling - position elements individually
            if (window.visualViewport && window.innerWidth <= 768) {
                const handler = () => {
                    if (!this.isOpen) return;
                    const vv = window.visualViewport;

                    // Make container cover EXACTLY the visible viewport - no extra space
                    container.style.position = 'fixed';
                    container.style.top = '0';
                    container.style.left = '0';
                    container.style.width = '100%';
                    container.style.height = `${vv.height}px`; // Use vv.height, not 100vh
                    container.style.zIndex = '2147483647';
                    container.style.overflow = 'hidden'; // No scroll on container

                    // Chat window fills container - THIS IS THE BACKGROUND LAYER
                    chatWindow.style.position = 'fixed';
                    chatWindow.style.top = '0';
                    chatWindow.style.left = '0';
                    chatWindow.style.width = '100%';
                    chatWindow.style.height = `${vv.height}px`;
                    chatWindow.style.display = 'flex';
                    chatWindow.style.flexDirection = 'column';
                    // UNIFIED STATIONARY BACKGROUND
                    chatWindow.style.backgroundColor = 'rgba(236, 254, 255, 0.98)';
                    chatWindow.style.backgroundImage = 'url("/static/img/diety_bg.png")';
                    chatWindow.style.backgroundSize = 'cover';
                    chatWindow.style.backgroundPosition = 'center';
                    chatWindow.style.backgroundRepeat = 'no-repeat';
                    chatWindow.style.backgroundAttachment = 'fixed';

                    // Header at top - FIXED to screen
                    if (header) {
                        header.style.position = 'fixed';
                        header.style.top = '0';
                        header.style.left = '0';
                        header.style.width = '100%';
                        header.style.zIndex = '1000';
                        header.style.flexShrink = '0';
                    }

                    // Input at bottom of visual viewport - ABOVE keyboard
                    if (inputArea) {
                        inputArea.style.position = 'fixed';
                        inputArea.style.bottom = `${window.innerHeight - vv.height}px`;
                        inputArea.style.left = '0';
                        inputArea.style.width = '100%';
                        inputArea.style.zIndex = '999';
                        inputArea.style.flexShrink = '0';
                    }

                    // Messages between header and input - TRANSPARENT TOP LAYER
                    if (messages && header && inputArea) {
                        const headerHeight = header.offsetHeight || 60;
                        const inputHeight = inputArea.offsetHeight || 70;
                        messages.style.position = 'fixed';
                        messages.style.top = `${headerHeight}px`;
                        messages.style.left = '0';
                        messages.style.width = '100%';
                        messages.style.height = `${vv.height - headerHeight - inputHeight}px`;
                        messages.style.overflowY = 'auto';
                        messages.style.zIndex = '100';

                        // TRANSPARENT - shows chatWindow background through
                        messages.style.background = 'transparent';

                        // Auto-scroll to bottom
                        // Auto-scroll to bottom
                        this.scrollToBottom();
                    }
                };

                this._vvHandler = handler;
                window.visualViewport.addEventListener('resize', handler);
                window.visualViewport.addEventListener('scroll', handler);

                // Run after a small delay to let elements render
                setTimeout(handler, 50);
                setTimeout(() => this.chatInput.focus(), 100);
            }
        } else {
            document.body.style.overflow = '';
            document.body.style.position = '';
            document.body.style.width = '';
            document.body.style.height = '';

            // Reset ALL styles
            container.style.cssText = '';
            chatWindow.style.cssText = '';
            if (header) header.style.cssText = '';
            if (messages) messages.style.cssText = '';
            if (inputArea) inputArea.style.cssText = '';

            if (this._vvHandler) {
                window.visualViewport.removeEventListener('resize', this._vvHandler);
                window.visualViewport.removeEventListener('scroll', this._vvHandler);
                this._vvHandler = null;
            }
        }
    }

    async sendMessage() {
        const text = this.chatInput.value.trim();
        if (!text) return;

        this.chatInput.value = '';
        this.addMessage(text, 'user');

        // Show typing indicator
        const typingId = this.addTypingIndicator();

        try {
            const resp = await fetch('/api/assistant_chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            const data = await resp.json();
            this.removeTypingIndicator(typingId);

            if (data.status === 'success') {
                this.addMessage(data.reply, 'ai');
            } else {
                this.addMessage("Sorry, my metabolic sensors are recalibrating. Try again?", 'ai');
            }
        } catch (err) {
            this.removeTypingIndicator(typingId);
            console.error('[Diety] Error:', err);
            this.addMessage("I'm momentarily offline. Please check your connection.", 'ai');
        }
    }

    addMessage(text, sender, save = true) {
        const msg = document.createElement('div');
        msg.className = `diety-message ${sender}-message`;
        msg.innerText = text;
        this.chatMessages.appendChild(msg);
        this.scrollToBottom();

        if (save) {
            this.saveHistory(text, sender);
        }
    }

    scrollToBottom() {
        // Use requestAnimationFrame to ensure DOM is updated
        requestAnimationFrame(() => {
            this.chatMessages.scrollTo({
                top: this.chatMessages.scrollHeight,
                behavior: 'smooth'
            });
            // Fallback for instant positioning
            setTimeout(() => {
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }, 100);
        });
    }

    addTypingIndicator() {
        const id = 'typing-' + Date.now();
        const indicator = document.createElement('div');
        indicator.id = id;
        indicator.className = 'diety-message ai-message typing';
        indicator.innerHTML = '<span>.</span><span>.</span><span>.</span>';
        this.chatMessages.appendChild(indicator);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        return id;
    }

    removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) {
            el.remove();
            this.scrollToBottom();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.dietyAssistant = new DietyAssistant();
});
