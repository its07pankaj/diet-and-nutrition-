# 🥗 DietNotify

<div align="center">

![DietNotify](logo/logo%202.png)

**AI-Powered Nutrition & Lifestyle Discipline Platform**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![Gemini AI](https://img.shields.io/badge/Gemini-2.5--Flash-orange.svg)](https://ai.google.dev/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-purple.svg)](https://supabase.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Science-based nutrition tracking and AI-powered meal planning for disciplined lifestyles*

[🚀 Getting Started](#-getting-started) •
[✨ Features](#-features) •
[🏗️ Architecture](#️-architecture) •
[📊 API Reference](#-api-reference) •
[🤝 Contributing](#-contributing)

</div>

---

## 📖 Introduction

**DietNotify** is a technology-driven web platform designed to help individuals improve their lifestyle through nutrition awareness, habit discipline, and routine consistency. The platform uses **Machine Learning (ML)** and **Artificial Intelligence (AI)**, including **Large Language Models (LLMs)**, to analyze user-provided data and generate scientific, non-medical insights.

### 🎯 Core Philosophy

> *"Most health problems originate from poor lifestyle discipline, not lack of information."*

DietNotify focuses on **behavior, consistency, and awareness**, rather than medical diagnosis or disease treatment. It empowers users to build disciplined, consistent, and healthier lifestyles using science and ethical AI.

---

## ✨ Features

### 🔍 Intelligent Food Search
- **1,700+ Vegetarian Foods** - Comprehensive database with Indian and global cuisines
- **50+ Nutrients Tracked** - Complete macro and micronutrient breakdowns
- **Smart Search Engine** - ML-enhanced prioritization of nutrient-dense foods
- **Real-time Autocomplete** - Instant results as you type

### 📊 Daily Meal Calculator
- **Multi-food Aggregation** - Combine multiple ingredients for complete meal analysis
- **Automatic Calculations** - Precise nutritional totals with mathematical accuracy
- **Visual Breakdowns** - Charts and graphs for easy understanding

### 🤖 AI Diet Planning (Powered by Gemini 2.5 Flash)
- **Personalized Diet Plans** - Based on your bio-profile and goals
- **Scientific Meal Timing** - Aligned with circadian rhythm and metabolism
- **Weekly/Monthly Plans** - Flexible duration options
- **Performance Projections** - Track expected health improvements over time
- **Comprehensive Analysis** - Health radar, metabolic logic flow, and expert recommendations

### 👤 User Profile System
- **5-Step Profile Setup** - Complete lifestyle assessment
- **Goal-based Personalization** - Fat loss, muscle gain, maintenance, or general health
- **Activity Level Tracking** - Sedentary to very active lifestyles
- **Dietary Preferences** - Vegetarian, vegan, and cuisine preferences
- **Health Condition Awareness** - Non-medical lifestyle adjustments

### 🔐 Authentication & Security
- **Secure User Registration** - Password hashing with SHA-256
- **Session Management** - 7-day persistent sessions
- **Supabase Cloud Database** - Enterprise-grade data storage
- **CORS Protection** - Cross-Origin Resource Sharing enabled

### 🌿 100% Vegetarian Focus
- **Strict Filtering** - Automatic removal of non-vegetarian items
- **Indian Foods Database** - Traditional vegetarian dishes included
- **Veg-first Philosophy** - Clean, plant-based nutrition

---

## 🏗️ Architecture

### Project Structure

```
v3/
├── 📁 app/                          # Main Flask Application
│   ├── __init__.py                  # App factory & initialization
│   ├── routes.py                    # Main page routes & API endpoints
│   ├── auth_routes.py               # Authentication & profile APIs
│   ├── diet_routes.py               # AI diet planning routes
│   │
│   ├── 📁 core/                     # Core Business Logic
│   │   ├── data_loader.py           # CSV data loading & search
│   │   ├── database.py              # Supabase database operations
│   │   └── nutrition_engine.py      # Scientific calculations
│   │
│   ├── 📁 services/                 # External Services
│   │   └── ai_diet_service.py       # Gemini AI integration
│   │
│   ├── 📁 static/                   # Frontend Assets
│   │   ├── css/style.css            # Main stylesheet (40KB+)
│   │   ├── js/                      # JavaScript modules
│   │   │   ├── navbar.js            # Navigation logic
│   │   │   ├── nutrition_engine.js  # Food search UI
│   │   │   ├── profile_engine.js    # Profile setup UI
│   │   │   └── strict_auth.js       # Auth protection
│   │   ├── img/                     # Images & graphics
│   │   └── data/                    # Static data files
│   │
│   └── 📁 templates/                # Jinja2 HTML Templates
│       ├── index.html               # Landing page
│       ├── nutrition.html           # Food search & calculator
│       ├── login.html               # Login/Signup page
│       ├── profile_setup.html       # 5-step profile wizard
│       ├── diet_create.html         # AI plan generator
│       ├── diet_dashboard.html      # Plan visualization
│       └── auth_callback.html       # Auth redirect handler
│
├── 📁 data/                         # Data Storage
│   ├── 📁 nutrition_db/             # Nutrition Databases
│   │   ├── FINAL FOOD DATASET/      # 16 CSV group files
│   │   ├── DeitNotify/              # Combined food data
│   │   ├── indian_foods.csv         # Indian cuisine data
│   │   └── Project details/         # Documentation
│   └── 📁 users/                    # User data (local backup)
│
├── 📁 scripts/                      # Utility Scripts
│   ├── convert_data.py              # Data processing
│   └── test_ai.py                   # AI service testing
│
├── 📁 logo/                         # Brand Assets
│   ├── logo.png
│   └── logo 2.png
│
├── run.py                           # Application entry point
├── post.md                          # Social media content
└── README.md                        # This file
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Flask 3.0 | Web framework & API server |
| **AI/ML** | Google Gemini 2.5 Flash | Diet plan generation |
| **Database** | Supabase (PostgreSQL) | Cloud data storage |
| **Data Processing** | Pandas | CSV handling & search |
| **Frontend** | Vanilla HTML/CSS/JS | Modern, responsive UI |
| **Styling** | Glassmorphism Design | Premium Gen-Z aesthetic |
| **Fonts** | Google Fonts (Outfit) | Modern typography |

### MVC Pattern

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     ROUTES      │────▶│    SERVICES     │────▶│   TEMPLATES     │
│   (Controller)  │     │    (Model)      │     │    (View)       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │
        │                       ▼
        │               ┌─────────────────┐
        │               │   CORE LOGIC    │
        │               │ • data_loader   │
        │               │ • database      │
        │               │ • nutrition_eng │
        │               └─────────────────┘
        │                       │
        ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   EXTERNAL AI   │     │    DATABASE     │
│   (Gemini API)  │     │   (Supabase)    │
└─────────────────┘     └─────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Internet connection (for AI and database)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/dietnotify.git
   cd dietnotify/v3
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask flask-cors pandas google-genai requests
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the platform**
   ```
   🌐 http://localhost:5000
   ```

### Environment Variables (Optional)

```bash
# For production deployment
export SECRET_KEY="your-secure-secret-key"
export SUPABASE_URL="your-supabase-url"
export SUPABASE_ANON_KEY="your-supabase-key"
```

---

## 📊 API Reference

### Authentication APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/signup` | POST | Create new user account |
| `/api/auth/login` | POST | Authenticate user |
| `/api/auth/logout` | POST | End user session |
| `/api/auth/status` | GET | Get authentication status |
| `/api/auth/profile/step` | POST | Save profile setup step |
| `/api/auth/profile/progress` | GET | Get profile completion |

### Nutrition APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search?q={query}` | GET | Search food database |
| `/api/food/{name}` | GET | Get detailed food info |
| `/api/calculate` | POST | Calculate meal totals |
| `/api/status` | GET | API health check |

### Diet Planning APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/diet/generate_all` | POST | Generate AI diet plan |
| `/api/diet/save_plan` | POST | Save generated plan |
| `/api/diet/active_plan` | GET | Get active plan |
| `/api/diet/my_plans` | GET | List all user plans |
| `/api/diet/plan/{id}` | GET | Get specific plan |
| `/api/diet/set_active/{id}` | POST | Set plan as active |
| `/api/diet/user_profile` | GET | Get user profile |

### Example: Search Foods

```javascript
// Search for foods containing "rice"
fetch('/api/search?q=rice')
  .then(res => res.json())
  .then(foods => console.log(foods));
```

### Example: Generate Diet Plan

```javascript
fetch('/api/diet/generate_all', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ duration: 'weekly' })
})
.then(res => res.json())
.then(plan => console.log(plan));
```

---

## 📁 Data Sources

### Nutrition Databases

| Database | Records | Description |
|----------|---------|-------------|
| Combined Food Data | 1,400+ | Primary nutrition dataset |
| FOOD-DATA-GROUP | 16 files | Categorized food groups |
| Indian Foods | 200+ | Traditional Indian cuisine |

### Data Fields

```
Food Name, Caloric Value, Fat, Saturated Fats, Cholesterol, Sodium,
Carbohydrates, Fiber, Sugars, Protein, Calcium, Iron, Magnesium,
Phosphorus, Potassium, Zinc, Vitamin A, Vitamin C, Vitamin D,
Vitamin E, Vitamin K, Vitamin B1-B12, and more...
```

---

## 🎨 UI/UX Design

### Design System

- **Primary Color**: `#00D26A` (Green - Diet/Health)
- **Secondary Color**: `#FFD93D` (Yellow - Energy)
- **Background**: Dark theme with gradients
- **Effects**: Glassmorphism, smooth animations
- **Typography**: Outfit font family (Google Fonts)

### Responsive Design

- **Desktop**: Full dashboard experience
- **Tablet**: Optimized layouts
- **Mobile**: Carousel swiping, touch-friendly

---

## ⚠️ Important Disclaimers

### What DietNotify IS:
- ✅ Lifestyle and nutrition awareness platform
- ✅ Habit discipline and consistency tracker
- ✅ AI-powered meal planning assistant
- ✅ Educational nutrition tool

### What DietNotify is NOT:
- ❌ Medical diagnosis system
- ❌ Disease treatment platform
- ❌ Clinical nutrition therapy
- ❌ Replacement for healthcare professionals

> **Disclaimer**: DietNotify is a lifestyle and nutrition awareness platform. It does not provide medical advice, diagnosis, or treatment. Users with health concerns must consult certified healthcare professionals.

---

## 🔒 Privacy & Data Policy

- **Data Storage**: Supabase cloud (encrypted)
- **Data Sharing**: Never sold or shared with third parties
- **Data Rights**: Users can export or delete their data
- **Analytics**: Anonymized for platform improvement
- **AI Usage**: Outputs are informational, not medical

---

## 🛠️ Development

### Project Scripts

```bash
# Run development server
python run.py

# Test AI service
python scripts/test_ai.py

# Convert data formats
python scripts/convert_data.py
```

### Code Quality

- **Pattern**: MVC (Model-View-Controller)
- **API Style**: RESTful JSON
- **Auth**: Session-based with decorators
- **Error Handling**: Try-catch with logging

---

## 📈 Future Roadmap

- [ ] Mobile App (React Native / Expo)
- [ ] Weekly Progress Reports via Email
- [ ] Water Intake Tracking
- [ ] Habit Streaks & Gamification
- [ ] AI Chatbot for Lifestyle Guidance
- [ ] Export Reports as PDF
- [ ] Multi-language Support

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

Built with ❤️ by the DietNotify Team

---

<div align="center">

**🌿 Precision Nutrition for the Elite 🌿**

*© 2026 DietNotify. All rights reserved.*

</div>
