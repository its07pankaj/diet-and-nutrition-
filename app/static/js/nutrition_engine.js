/**
 * DietNotify Nutrition Engine
 * Strict Separation: Food Search vs Daily Meal Data
 * NOW CONNECTED TO PYTHON FLASK BACKEND
 */

let mealLog = [];
let currentMode = null; // 'search' or 'meal'
// Works when served from server.py OR opened as file
const API_BASE = window.location.protocol === 'file:'
    ? "http://127.0.0.1:5000/api"
    : "/api";

// DOM Elements - Selection
const selectionScreen = document.getElementById('selectionScreen');
const searchSection = document.getElementById('searchSection');
const mealSection = document.getElementById('mealSection');

// DOM Elements - Search Mode
const mainSearchInput = document.getElementById('mainSearchInput');
const searchResults = document.getElementById('searchResults');
const singleItemView = document.getElementById('singleItemView');
const detailName = document.getElementById('detailName');
const majorNutrientsGrid = document.getElementById('majorNutrientsGrid');
const detailMicros = document.getElementById('detailMicros');

// DOM Elements - Meal Mode
const mealSearchInput = document.getElementById('mealSearchInput');
const mealSearchResults = document.getElementById('mealSearchResults');
const mealList = document.getElementById('mealList');
const mealSummaryGrid = document.getElementById('mealSummaryGrid');
const clearLogBtn = document.getElementById('clearLogBtn');

// Load Data - NO LONGER NEEDED (Backend handles it)
document.addEventListener('DOMContentLoaded', () => {
    // Check if API is alive (optional)
    fetch(`${API_BASE}/`)
        .then(res => console.log("Backend Connected"))
        .catch(err => console.error("Backend Offline! Run app.py"));

    setupEventListeners();
});

// --- UI SWITCHING ---

window.switchMode = function (mode) {
    currentMode = mode;
    selectionScreen.style.display = 'none';

    if (mode === 'search') {
        searchSection.style.display = 'block';
        mealSection.style.display = 'none';
        mainSearchInput.focus();
    } else {
        searchSection.style.display = 'none';
        mealSection.style.display = 'block';
        mealSearchInput.focus();
        renderMealLog(); // Refresh view
    }
}

window.showSelection = function () {
    selectionScreen.style.display = 'flex';
    searchSection.style.display = 'none';
    mealSection.style.display = 'none';

    // Reset inputs
    mainSearchInput.value = '';
    mealSearchInput.value = '';
    searchResults.style.display = 'none';
    singleItemView.style.display = 'none';
    mealSearchResults.style.display = 'none';
}

function setupEventListeners() {
    // Mode 1: Search Input (Debounced ideally, but direct for now)
    let timeout = null;
    mainSearchInput.addEventListener('input', (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            handleSearch(e.target.value, searchResults, 'view');
        }, 300); // 300ms debounce
    });

    // Mode 2: Meal Search Input
    mealSearchInput.addEventListener('input', (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            handleSearch(e.target.value, mealSearchResults, 'add');
        }, 300);
    });

    // Clear Log
    clearLogBtn.addEventListener('click', () => {
        mealLog = [];
        renderMealLog();
    });

    // Validating Click Outside to close dropdowns
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-bar')) {
            searchResults.style.display = 'none';
            mealSearchResults.style.display = 'none';
        }
    });
}

// --- SEARCH LOGIC (VIA API) ---

async function handleSearch(query, container, type) {
    query = query.toLowerCase().trim();
    if (query.length < 2) {
        container.style.display = 'none';
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
        const matches = await res.json();
        renderResults(matches, container, type);
    } catch (e) {
        console.error("Search failed", e);
    }
}

function renderResults(items, container, type) {
    container.innerHTML = '';

    if (items.length === 0) {
        container.style.display = 'none';
        return;
    }

    items.forEach(item => {
        const div = document.createElement('div');
        div.className = 'result-item';
        // Backend key matching
        div.innerHTML = `
            <span class="food-name">${item.food}</span>
            <span class="macros">${Math.round(item['Caloric Value'] || 0)} cal</span>
        `;

        div.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent closing immediately
            if (type === 'view') {
                displaySingleItemDetail(item);
                mainSearchInput.value = item.food;
                container.style.display = 'none';
            } else {
                addToMeal(item);
                mealSearchInput.value = '';
                container.style.display = 'none';
            }
        });

        container.appendChild(div);
    });

    container.style.display = 'block';
}

// --- MODE 1: SINGLE ITEM DISPLAY (Enhanced Visual Design) ---

// Nutrient metadata with categories, units, and daily values
const NUTRIENT_META = {
    // Vitamins
    'Vitamin A': { cat: 'Vitamins', unit: 'mcg', dv: 900, icon: '🔶' },
    'Vitamin B1': { cat: 'Vitamins', unit: 'mg', dv: 1.2, icon: '💊' },
    'Vitamin B2': { cat: 'Vitamins', unit: 'mg', dv: 1.3, icon: '💊' },
    'Vitamin B3': { cat: 'Vitamins', unit: 'mg', dv: 16, icon: '💊' },
    'Vitamin B5': { cat: 'Vitamins', unit: 'mg', dv: 5, icon: '💊' },
    'Vitamin B6': { cat: 'Vitamins', unit: 'mg', dv: 1.7, icon: '💊' },
    'Vitamin B11': { cat: 'Vitamins', unit: 'mcg', dv: 400, icon: '💊' },
    'Vitamin B12': { cat: 'Vitamins', unit: 'mcg', dv: 2.4, icon: '🔴' },
    'Vitamin C': { cat: 'Vitamins', unit: 'mg', dv: 90, icon: '🍊' },
    'Vitamin D': { cat: 'Vitamins', unit: 'mcg', dv: 20, icon: '☀️' },
    'Vitamin E': { cat: 'Vitamins', unit: 'mg', dv: 15, icon: '🌿' },
    'Vitamin K': { cat: 'Vitamins', unit: 'mcg', dv: 120, icon: '🥬' },
    // Minerals
    'Calcium': { cat: 'Minerals', unit: 'mg', dv: 1300, icon: '🦴' },
    'Iron': { cat: 'Minerals', unit: 'mg', dv: 18, icon: '🩸' },
    'Magnesium': { cat: 'Minerals', unit: 'mg', dv: 420, icon: '⚡' },
    'Phosphorus': { cat: 'Minerals', unit: 'mg', dv: 1250, icon: '💎' },
    'Potassium': { cat: 'Minerals', unit: 'mg', dv: 4700, icon: '🍌' },
    'Sodium': { cat: 'Minerals', unit: 'mg', dv: 2300, icon: '🧂' },
    'Zinc': { cat: 'Minerals', unit: 'mg', dv: 11, icon: '🔩' },
    'Selenium': { cat: 'Minerals', unit: 'mcg', dv: 55, icon: '💫' },
    'Copper': { cat: 'Minerals', unit: 'mg', dv: 0.9, icon: '🔧' },
    'Manganese': { cat: 'Minerals', unit: 'mg', dv: 2.3, icon: '⚙️' },
    // Fats
    'Saturated Fats': { cat: 'Fats', unit: 'g', dv: 20, icon: '🧈' },
    'Monounsaturated Fats': { cat: 'Fats', unit: 'g', dv: null, icon: '🫒' },
    'Polyunsaturated Fats': { cat: 'Fats', unit: 'g', dv: null, icon: '🐟' },
    'Trans Fats': { cat: 'Fats', unit: 'g', dv: 0, icon: '⚠️' },
    'Cholesterol': { cat: 'Fats', unit: 'mg', dv: 300, icon: '💔' },
    // Other
    'Fiber': { cat: 'Other', unit: 'g', dv: 28, icon: '🌾' },
    'Water': { cat: 'Other', unit: 'g', dv: null, icon: '💧' },
    'rank': { cat: 'skip', unit: '', dv: null, icon: '' },
    'Nutrition Density': { cat: 'skip', unit: '', dv: null, icon: '' },
};

function displaySingleItemDetail(item) {
    // Update header
    detailName.innerHTML = `<span class="gradient-text">${item.food}</span>`;

    // 1. Major Nutrients - Enhanced Cards
    const majors = [
        { key: 'Caloric Value', icon: '🔥', unit: 'kcal', color: '#f97316' },
        { key: 'Protein', icon: '💪', unit: 'g', color: '#22c55e' },
        { key: 'Carbohydrates', icon: '🍞', unit: 'g', color: '#eab308' },
        { key: 'Fat', icon: '🧈', unit: 'g', color: '#ef4444' },
        { key: 'Fiber', icon: '🌾', unit: 'g', color: '#84cc16' },
        { key: 'Sugars', icon: '🍬', unit: 'g', color: '#ec4899' },
    ];

    majorNutrientsGrid.innerHTML = '';

    majors.forEach(m => {
        const val = parseFloat(item[m.key]) || 0;
        const div = document.createElement('div');
        div.className = 'macro-card';
        div.innerHTML = `
            <div class="macro-icon" style="background: ${m.color}20; color: ${m.color};">${m.icon}</div>
            <div class="macro-info">
                <span class="macro-label">${m.key}</span>
                <span class="macro-value" style="color: ${m.color};">${val.toFixed(1)}<small>${m.unit}</small></span>
            </div>
        `;
        majorNutrientsGrid.appendChild(div);
    });

    // 2. Detailed Profile - Categorized with Progress Bars
    detailMicros.innerHTML = '';

    const others = { ...item };
    const junk = ['food', 'is_veg', 'Unnamed: 0', 'Unnamed: 0.1', 'id', 'index', 'level_0',
        'Caloric Value', 'Protein', 'Fat', 'Carbohydrates', 'Sugars', 'Fiber'];
    junk.forEach(k => delete others[k]);

    // Group by category
    const categories = { 'Vitamins': [], 'Minerals': [], 'Fats': [], 'Other': [] };

    Object.entries(others).forEach(([key, value]) => {
        const val = parseFloat(value);
        if (isNaN(val) || val <= 0) return;

        const meta = NUTRIENT_META[key] || { cat: 'Other', unit: '', dv: null, icon: '📊' };
        if (meta.cat === 'skip') return;

        categories[meta.cat].push({
            name: key,
            value: val,
            unit: meta.unit,
            dv: meta.dv,
            icon: meta.icon,
            percent: meta.dv ? Math.min((val / meta.dv) * 100, 100) : null
        });
    });

    // Render each category
    Object.entries(categories).forEach(([catName, nutrients]) => {
        if (nutrients.length === 0) return;

        // Sort by value descending
        nutrients.sort((a, b) => b.value - a.value);

        const catDiv = document.createElement('div');
        catDiv.className = 'nutrient-category';
        catDiv.innerHTML = `<h5 class="category-title">${getCategoryIcon(catName)} ${catName}</h5>`;

        const grid = document.createElement('div');
        grid.className = 'nutrient-grid';

        nutrients.forEach(n => {
            const nutrientEl = document.createElement('div');
            nutrientEl.className = 'nutrient-item';
            nutrientEl.innerHTML = `
                <div class="nutrient-header">
                    <span class="nutrient-name">${n.icon} ${n.name}</span>
                    <span class="nutrient-value">${n.value.toFixed(2)} <small>${n.unit}</small></span>
                </div>
                ${n.percent !== null ? `
                    <div class="nutrient-bar-bg">
                        <div class="nutrient-bar" style="width: ${n.percent}%; background: ${getBarColor(n.percent)};"></div>
                    </div>
                    <span class="nutrient-dv">${n.percent.toFixed(0)}% DV</span>
                ` : ''}
            `;
            grid.appendChild(nutrientEl);
        });

        catDiv.appendChild(grid);
        detailMicros.appendChild(catDiv);
    });

    singleItemView.style.display = 'block';
}

function getCategoryIcon(cat) {
    const icons = { 'Vitamins': '💊', 'Minerals': '💎', 'Fats': '🧈', 'Other': '📊' };
    return icons[cat] || '📦';
}

function getBarColor(percent) {
    if (percent >= 80) return '#22c55e';
    if (percent >= 50) return '#eab308';
    if (percent >= 25) return '#f97316';
    return '#64748b';
}

// --- MODE 2: MEAL LOGIC (Real Data Aggregation) ---

function addToMeal(item) {
    mealLog.push({ ...item, _id: Date.now() });
    renderMealLog();
}

function removeFromMeal(id) {
    mealLog = mealLog.filter(x => x._id !== id);
    renderMealLog();
}

function renderMealLog() {
    mealList.innerHTML = '';
    if (mealLog.length === 0) {
        mealList.innerHTML = '<p style="color:gray; text-align:center;">Plate is empty.</p>';
        mealSummaryGrid.innerHTML = '<p style="color:gray;">Add items to see totals.</p>';
        return;
    }

    // Render List
    mealLog.forEach(item => {
        const div = document.createElement('div');
        div.className = 'added-item';
        div.innerHTML = `
            <span>${item.food}</span>
            <span style="color:#888; font-size:0.9rem;">${Math.round(item['Caloric Value'])} kcal</span>
            <button onclick="removeFromMeal(${item._id})" style="color: #ff6b6b; background:none; border:none; cursor:pointer;">✕</button>
        `;
        mealList.appendChild(div);
    });

    // Calculate Totals (All Numeric Columns)
    calculateMealTotals();
}

function calculateMealTotals() {
    const totals = {};
    const ignore = ['food', 'is_veg', 'Unnamed: 0', 'id', '_id', 'index', 'Unnamed: 0.1', 'level_0'];

    // 1. Sum up all values
    mealLog.forEach(item => {
        Object.keys(item).forEach(k => {
            if (ignore.includes(k)) return;
            const val = parseFloat(item[k]);
            if (!isNaN(val)) {
                totals[k] = (totals[k] || 0) + val;
            }
        });
    });

    mealSummaryGrid.innerHTML = '';

    // 2. Render Major Nutrients Aggregated
    const majors = [
        { key: 'Caloric Value', icon: '🔥', unit: 'kcal', color: '#f97316' },
        { key: 'Protein', icon: '💪', unit: 'g', color: '#22c55e' },
        { key: 'Carbohydrates', icon: '🍞', unit: 'g', color: '#eab308' },
        { key: 'Fat', icon: '🧈', unit: 'g', color: '#ef4444' },
        { key: 'Fiber', icon: '🌾', unit: 'g', color: '#84cc16' },
        { key: 'Sugars', icon: '🍬', unit: 'g', color: '#ec4899' },
    ];

    const majorsContainer = document.createElement('div');
    majorsContainer.style.marginBottom = '24px';

    // Header for Majors
    majorsContainer.innerHTML = `<h4 style="color:white; margin-bottom:12px; font-size:1.1rem;">🔥 Total Macros</h4>`;

    // Grid for Majors
    const majorsGrid = document.createElement('div');
    majorsGrid.className = 'macros-grid';
    majorsContainer.appendChild(majorsGrid);

    majors.forEach(m => {
        const val = totals[m.key] || 0;
        const div = document.createElement('div');
        div.className = 'macro-card';
        div.innerHTML = `
            <div class="macro-icon" style="background: ${m.color}20; color: ${m.color};">${m.icon}</div>
            <div class="macro-info">
                <span class="macro-label">${m.key}</span>
                <span class="macro-value" style="color: ${m.color};">${val.toFixed(0)}<small>${m.unit}</small></span>
            </div>
        `;
        majorsGrid.appendChild(div);
    });

    mealSummaryGrid.appendChild(majorsContainer);

    // 3. Render Detailed Aggregated Profile
    const detailsContainer = document.createElement('div');
    detailsContainer.innerHTML = `<h4 style="color:var(--text-secondary); margin-bottom:16px; margin-top:30px; font-size:1.1rem;">📊 Detailed Total Profile</h4>`;

    // Group by category used in NUTRIENT_META
    const categories = { 'Vitamins': [], 'Minerals': [], 'Fats': [], 'Other': [] };

    Object.entries(totals).forEach(([key, value]) => {
        if (value <= 0) return;
        // Skip majors in detailed view
        if (majors.some(m => m.key === key)) return;

        const meta = NUTRIENT_META[key] || { cat: 'Other', unit: '', dv: null, icon: '📊' };
        if (meta.cat === 'skip') return;

        categories[meta.cat].push({
            name: key,
            value: value,
            unit: meta.unit,
            dv: meta.dv,
            icon: meta.icon,
            percent: meta.dv ? Math.min((value / meta.dv) * 100, 100) : null
        });
    });

    // Render Categories
    Object.entries(categories).forEach(([catName, nutrients]) => {
        if (nutrients.length === 0) return;

        // Sort by percent DV if available, else value
        nutrients.sort((a, b) => (b.percent || 0) - (a.percent || 0));

        const catDiv = document.createElement('div');
        catDiv.className = 'nutrient-category';
        catDiv.innerHTML = `<h5 class="category-title">${getCategoryIcon(catName)} ${catName}</h5>`;

        const grid = document.createElement('div');
        grid.className = 'nutrient-grid';

        nutrients.forEach(n => {
            const nutrientEl = document.createElement('div');
            nutrientEl.className = 'nutrient-item';
            nutrientEl.innerHTML = `
                <div class="nutrient-header">
                    <span class="nutrient-name">${n.icon} ${n.name}</span>
                    <span class="nutrient-value">${n.value.toFixed(1)} <small>${n.unit}</small></span>
                </div>
                ${n.percent !== null ? `
                    <div class="nutrient-bar-bg">
                        <div class="nutrient-bar" style="width: ${n.percent}%; background: ${getBarColor(n.percent)};"></div>
                    </div>
                    <span class="nutrient-dv">${n.percent.toFixed(0)}% Daily Value</span>
                ` : ''}
            `;
            grid.appendChild(nutrientEl);
        });

        catDiv.appendChild(grid);
        detailsContainer.appendChild(catDiv);
    });

    mealSummaryGrid.appendChild(detailsContainer);
}

