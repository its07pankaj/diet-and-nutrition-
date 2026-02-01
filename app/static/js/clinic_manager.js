/**
 * Clinic Manager - AI Discovery Edition
 * Replaces POI search with Gemini-powered expert discovery.
 * Removes all simulated data and sci-fi visuals.
 */
class ClinicManager {
    constructor() {
        this.mapboxToken = 'pk.eyJ1IjoicGFua2FqMDciLCJhIjoiY21reHJ2aWJ5MDIyajNjc2R4NmZ0Nm9qdyJ9.jByCUQcUGdwtGzgUbcMa-w';
        this.map = null;
        this.markers = [];
        this.userMarker = null;
        this.userLocation = null;
        this.currentStyle = 'light';
        this.isScanning = false;

        mapboxgl.accessToken = this.mapboxToken;
    }

    initMap() {
        if (this.map) return;

        console.log('[ClinicManager] Initializing Map (Clean Mode)...');

        this.map = new mapboxgl.Map({
            container: 'map',
            style: 'mapbox://styles/mapbox/light-v11',
            center: [77.2090, 28.6139],
            zoom: 12,
            pitch: 0, // Flat professional view
            antialias: true
        });

        this.map.on('load', () => {
            console.log('[ClinicManager] Map loaded.');
            this.locateUser();
        });
    }

    setStyle(mode) {
        if (!this.map || this.currentStyle === mode) return;
        const styleUrl = mode === 'satellite' ? 'mapbox://styles/mapbox/satellite-streets-v12' : 'mapbox://styles/mapbox/light-v11';
        this.map.setStyle(styleUrl);
        this.currentStyle = mode;
        document.getElementById('modeStandard').classList.toggle('active', mode === 'light');
        document.getElementById('modeSatellite').classList.toggle('active', mode === 'satellite');
    }

    async manualSearch() {
        const input = document.getElementById('mapSearchInput');
        const query = input.value.trim();
        if (!query) return;

        console.log('[ClinicManager] Manual AI Search:', query);
        this.setScanning(true, 'ANALYZING AREA...');

        try {
            // Get location context first
            let locUrl = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(query)}.json?access_token=${this.mapboxToken}&limit=1`;
            const locResp = await fetch(locUrl);
            const locData = await locResp.json();

            if (locData.features && locData.features.length > 0) {
                const target = locData.features[0];
                this.userLocation = target.center;
                const locName = target.place_name;

                this.map.flyTo({ center: this.userLocation, zoom: 13 });
                this.updateUserMarker();
                this.fetchAIExperts(query, locName);
            }
        } catch (err) {
            console.error('Manual search error:', err);
            this.setScanning(false);
        }
    }

    async locateUser() {
        if (!navigator.geolocation) return;

        this.setScanning(true, 'DETECTING LOCATION...');

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                this.userLocation = [position.coords.longitude, position.coords.latitude];
                this.updateUserMarker();
                this.map.flyTo({ center: this.userLocation, zoom: 14 });

                // Get name for context
                const revUrl = `https://api.mapbox.com/geocoding/v5/mapbox.places/${this.userLocation[0]},${this.userLocation[1]}.json?access_token=${this.mapboxToken}&limit=1`;
                const revResp = await fetch(revUrl);
                const revData = await revResp.json();
                const locName = revData.features[0]?.place_name || 'My Location';

                this.fetchAIExperts('nutritionists and health clinics', locName);
            },
            (err) => {
                console.error('Geo error:', err);
                this.setScanning(false);
            }
        );
    }

    updateUserMarker() {
        if (this.userMarker) this.userMarker.remove();
        const el = document.createElement('div');
        el.className = 'user-marker-pulse'; // Keep the pulse, it's functional
        this.userMarker = new mapboxgl.Marker(el)
            .setLngLat(this.userLocation)
            .addTo(this.map);
    }

    async fetchAIExperts(query, locationName) {
        console.log(`[ClinicManager] Requesting AI Discovery for: ${query} NEAR ${locationName}`);
        this.setScanning(true, 'FINDING NEAREST EXPERTS...');
        this.clearMarkers();

        try {
            const resp = await fetch('/api/expert_search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    lat: this.userLocation[1],
                    lng: this.userLocation[0],
                    query: query,
                    location_name: locationName
                })
            });

            if (!resp.ok) throw new Error(`HTTP Error: ${resp.status}`);

            const data = await resp.json();
            console.log('[ClinicManager] AI Data received:', data);

            if (data.status === 'success' && data.experts && data.experts.length > 0) {
                this.processAIResults(data.experts);
            } else {
                console.warn('[ClinicManager] No experts found or error:', data);
                this.setScanning(false, 'NO LOCAL EXPERTS FOUND');
                setTimeout(() => this.setScanning(false), 3000);
            }
        } catch (err) {
            console.error('[ClinicManager] AI Discovery failed:', err);
            this.setScanning(false, 'NETWORK ERROR');
            setTimeout(() => this.setScanning(false), 3000);
        }
    }

    async processAIResults(experts) {
        const expertListEl = document.getElementById('expertList');
        const expertDetailsGrid = document.getElementById('expertDetailsGrid');
        expertListEl.innerHTML = '';
        expertDetailsGrid.innerHTML = '';

        for (const exp of experts) {
            // We need to geocode the address to place it on the map
            const geoUrl = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(exp.address)}.json?access_token=${this.mapboxToken}&limit=1`;
            try {
                const gResp = await fetch(geoUrl);
                const gData = await gResp.json();

                if (gData.features && gData.features.length > 0) {
                    const coords = gData.features[0].center;
                    this.addExpertToUI(exp, coords);
                }
            } catch (e) {
                console.warn('Geocoding failed for:', exp.name);
            }
        }

        this.setScanning(false);
    }

    addExpertToUI(expert, coords) {
        const marker = new mapboxgl.Marker({ color: '#eab308' })
            .setLngLat(coords)
            .setPopup(new mapboxgl.Popup({ offset: 25 }).setHTML(`
                <div style="font-family: 'Outfit', sans-serif;">
                    <strong style="color: #0891b2; display: block; margin-bottom: 5px;">${expert.name}</strong>
                    <span style="font-size: 0.8rem; color: #666;">${expert.address}</span>
                </div>
            `))
            .addTo(this.map);

        this.markers.push(marker);

        const listEl = document.getElementById('expertList');
        const item = document.createElement('div');
        item.className = 'expert-item-small';
        item.innerHTML = `<span class="name">${expert.name}</span><span class="type">${expert.type}</span>`;
        item.onclick = () => {
            this.map.flyTo({ center: coords, zoom: 15 });
            marker.togglePopup();
        };
        listEl.appendChild(item);

        const gridEl = document.getElementById('expertDetailsGrid');
        gridEl.innerHTML += `
            <div class="meal-card" style="min-height: auto; padding: 25px; border-left: 5px solid var(--accent-primary);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
                    <div class="meal-name" style="margin-bottom: 0;">${expert.name}</div>
                    <span style="background: rgba(8, 145, 178, 0.1); color: var(--accent-primary); padding: 4px 12px; border-radius: 100px; font-size: 0.7rem; font-weight: 800;">${expert.type.toUpperCase()}</span>
                </div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 10px;">
                    <i class="fas fa-map-marker-alt" style="margin-right: 8px; color: var(--accent-primary);"></i> ${expert.address}
                </div>
                <div style="font-size: 0.85rem; color: var(--text-muted); font-style: italic; margin-bottom: 15px;">
                    ${expert.relevance}
                </div>
                <button onclick="window.clinicManager.focusExpert([${coords[0]}, ${coords[1]}])" class="btn btn-secondary" style="width: 100%; border-radius: 12px;">SHOW ON MAP</button>
            </div>
        `;
    }

    focusExpert(coords) {
        showSection('experts');
        this.map.flyTo({ center: coords, zoom: 16 });
    }

    clearMarkers() {
        this.markers.forEach(m => m.remove());
        this.markers = [];
    }

    setScanning(active, label = '') {
        this.isScanning = active;
        const radar = document.getElementById('mapRadar');
        const radarLabel = document.getElementById('radarLabel');

        if (radar) {
            // We use the radar container for the loading overlay now, but stripped of visuals
            radar.style.opacity = active ? '1' : '0';
            radar.style.pointerEvents = active ? 'all' : 'none';
            // Hide the actual radar-circle and sweep via CSS or just set display:none
        }
        if (radarLabel && label) radarLabel.innerText = label;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.clinicManager = new ClinicManager();
    const originalShowSection = window.showSection;
    window.showSection = (sectionId, el) => {
        originalShowSection(sectionId, el);
        if (sectionId === 'experts') {
            setTimeout(() => {
                window.clinicManager.initMap();
            }, 500);
        }
    };
});
