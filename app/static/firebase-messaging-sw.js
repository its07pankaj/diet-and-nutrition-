/**
 * Firebase Service Worker for DietNotify
 * Handles background push notifications
 */

// Import Firebase scripts (v10.13.2 - must match main page)
importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging-compat.js');

// Firebase config - from your Firebase Console
const firebaseConfig = {
    apiKey: "AIzaSyDnA_X6q3k9Jn3loCvV8fvsLJNTMxlHClE",
    authDomain: "dietnotify.firebaseapp.com",
    projectId: "dietnotify",
    storageBucket: "dietnotify.firebasestorage.app",
    messagingSenderId: "174828371624",
    appId: "1:174828371624:web:d80c76b8630b40f2208c9d"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
    console.log('[SW] Background message received:', payload);

    const notificationTitle = payload.notification?.title || '🍽️ DietNotify';
    const notificationOptions = {
        body: payload.notification?.body || 'Time for your scheduled meal!',
        icon: '/static/img/logo.svg',
        badge: '/static/img/logo.svg',
        vibrate: [200, 100, 200],
        tag: 'meal-reminder',
        requireInteraction: true,
        actions: [
            { action: 'view', title: 'View Diet Plan' },
            { action: 'dismiss', title: 'Dismiss' }
        ],
        data: payload.data || {}
    };

    return self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
    console.log('[SW] Notification clicked:', event);

    event.notification.close();

    if (event.action === 'view' || !event.action) {
        // Open diet dashboard
        event.waitUntil(
            clients.matchAll({ type: 'window', includeUncontrolled: true })
                .then((clientList) => {
                    // Check if app is already open
                    for (const client of clientList) {
                        if (client.url.includes('/diet') && 'focus' in client) {
                            return client.focus();
                        }
                    }
                    // Open new window
                    if (clients.openWindow) {
                        return clients.openWindow('/diet/dashboard');
                    }
                })
        );
    }
});

// Log when service worker is installed
self.addEventListener('install', (event) => {
    console.log('[SW] Service worker installed');
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    console.log('[SW] Service worker activated');
    event.waitUntil(clients.claim());
});
