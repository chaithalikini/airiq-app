# 🌬️ AirIQ — Real-Time Air Quality Insight Web App

A full-stack Data Science internship project built with **Flask**, **OpenWeatherMap API**, **SQLite**, and **Bootstrap 5**.

---

## 📁 Project Structure

```
air_quality_app/
├── app.py                  ← Main Flask application
├── users.db                ← SQLite database (auto-created on first run)
├── requirements.txt        ← Python dependencies
├── README.md
├── templates/
│   ├── base.html           ← Master layout (navbar, footer, flash messages)
│   ├── index.html          ← Home page with city search form
│   ├── result.html         ← AQI results with charts
│   ├── login.html          ← User login page
│   ├── register.html       ← User registration page
│   ├── methodology.html    ← Technical explanation
│   └── about.html          ← About the project
└── static/
    ├── css/style.css       ← All custom styles
    └── js/main.js          ← UI enhancements
```

---

## ⚡ Quick Start

### 1. Get a Free API Key
Sign up at [openweathermap.org](https://openweathermap.org/api) and copy your API key.

### 2. Add Your API Key
Open `app.py` and replace:
```python
OPENWEATHER_API_KEY = "YOUR_API_KEY_HERE"
```
with your actual key.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
python app.py
```

Visit **http://127.0.0.1:5000** in your browser.

---

## 🔑 Features

| Feature | Details |
|---|---|
| **Authentication** | Register / Login / Logout using Flask sessions |
| **Password Security** | Hashed with Werkzeug PBKDF2 |
| **AQI Display** | Index 1–5 with colour-coded badges |
| **Pollutants** | PM2.5, PM10, CO, NO₂, O₃, SO₂ |
| **Health Tips** | Contextual advice based on AQI level |
| **Responsive UI** | Works on mobile, tablet, and desktop |
| **Animated Charts** | Progress bars animate on load |

---

## 🌈 AQI Scale

| Index | Category  | Colour  |
|-------|-----------|---------|
| 1     | Good      | 🟢 Green |
| 2     | Fair      | 🟡 Yellow |
| 3     | Moderate  | 🟠 Orange |
| 4     | Poor      | 🔴 Red |
| 5     | Very Poor | 🟣 Purple |

---

## 🛠️ Technology Stack

- **Backend** — Python 3, Flask, Werkzeug
- **Database** — SQLite (via Python's built-in `sqlite3`)
- **API** — OpenWeatherMap (Geocoding + Air Pollution endpoints)
- **Frontend** — Bootstrap 5, Bootstrap Icons, Google Fonts (Syne + DM Sans)
- **Templating** — Jinja2

---

## 📝 Notes for Submission

- The `users.db` file is auto-created when you run `app.py` for the first time.
- Make sure to activate a virtual environment before installing dependencies.
- The free OpenWeatherMap tier is sufficient for this project.