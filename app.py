"""
Air Quality Insight Web Application
====================================
Main Flask application file.
Handles routing, authentication, and API calls to OpenWeatherMap.

Author: Data Science Internship Project
"""

import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

from dotenv import load_dotenv
load_dotenv()
# ─────────────────────────────────────────────
# App Configuration
# ─────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "airquality_secret_key_2024"  # Change this in production!

# !! Replace with your actual OpenWeatherMap API key !!
# Get a free key at: https://openweathermap.org/api

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")

DATABASE = "users.db"


# ─────────────────────────────────────────────
# Database Setup
# ─────────────────────────────────────────────
def get_db():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn


def init_db():
    """Create the users table if it doesn't exist."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    UNIQUE NOT NULL,
                email    TEXT    UNIQUE NOT NULL,
                password TEXT    NOT NULL
            )
        """)
        conn.commit()


# ─────────────────────────────────────────────
# Login Required Decorator
# ─────────────────────────────────────────────
def login_required(f):
    """Decorator: redirects to login if user is not authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ─────────────────────────────────────────────
# API Helper Functions
# ─────────────────────────────────────────────
def get_coordinates(city_name):
    """
    Convert a city name to latitude and longitude
    using OpenWeatherMap Geocoding API.
    Returns (lat, lon, country) or raises ValueError.
    """
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {"q": city_name, "limit": 1, "appid": OPENWEATHER_API_KEY}

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data:
        raise ValueError(f"City '{city_name}' not found. Please check the spelling.")

    return data[0]["lat"], data[0]["lon"], data[0].get("country", "")


def get_air_quality(lat, lon):
    """
    Fetch air pollution data for given coordinates
    using OpenWeatherMap Air Pollution API.
    Returns a dict with AQI and pollutant values.
    """
    url = "http://api.openweathermap.org/data/2.5/air_pollution"
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY}

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    components = data["list"][0]["components"]
    aqi_index  = data["list"][0]["main"]["aqi"]  # 1–5 scale from OpenWeather

    return {
        "aqi":   aqi_index,
        "pm2_5": round(components.get("pm2_5", 0), 2),
        "pm10":  round(components.get("pm10",  0), 2),
        "co":    round(components.get("co",    0), 2),
        "no2":   round(components.get("no2",   0), 2),
        "o3":    round(components.get("o3",    0), 2),
        "so2":   round(components.get("so2",   0), 2),
    }


def interpret_aqi(aqi_index):
    """
    Map OpenWeather AQI index (1–5) to
    a human-readable label, color, and description.
    """
    mapping = {
        1: ("Good",       "good",      "#2ecc71",
            "Air quality is satisfactory and poses little or no risk."),
        2: ("Fair",       "fair",      "#f1c40f",
            "Air quality is acceptable. Some pollutants may affect sensitive groups."),
        3: ("Moderate",   "moderate",  "#e67e22",
            "Members of sensitive groups may experience health effects."),
        4: ("Poor",       "poor",      "#e74c3c",
            "Everyone may begin to experience health effects."),
        5: ("Very Poor",  "very_poor", "#8e44ad",
            "Health warnings. Everyone may experience serious health effects."),
    }
    return mapping.get(aqi_index, ("Unknown", "unknown", "#95a5a6", "Data unavailable."))


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.route("/")
def home():
    """Home page with the city search form (login required)."""
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")


@app.route("/result", methods=["POST"])
@login_required
def result():
    """
    Process city form submission.
    Fetches geocoding + air quality data and renders result page.
    """
    city = request.form.get("city", "").strip()

    if not city:
        flash("Please enter a city name.", "danger")
        return redirect(url_for("home"))

    try:
        lat, lon, country = get_coordinates(city)
        aq_data           = get_air_quality(lat, lon)
        label, css_class, color, description = interpret_aqi(aq_data["aqi"])

        return render_template(
            "result.html",
            city        = city.title(),
            country     = country,
            lat         = lat,
            lon         = lon,
            aqi_label   = label,
            aqi_class   = css_class,
            aqi_color   = color,
            aqi_desc    = description,
            **aq_data,
        )

    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("home"))

    except requests.exceptions.ConnectionError:
        flash("Network error. Please check your internet connection.", "danger")
        return redirect(url_for("home"))

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            flash("Invalid API key. Please update your OpenWeatherMap API key in app.py.", "danger")
        else:
            flash(f"API error: {e}", "danger")
        return redirect(url_for("home"))

    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "danger")
        return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration page."""
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email",    "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm",  "")

        # Basic validation
        if not all([username, email, password, confirm]):
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        hashed = generate_password_hash(password)

        try:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                    (username, email, hashed),
                )
                conn.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Username or email already exists.", "danger")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login page."""
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"]  = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Clear session and redirect to login."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/methodology")
def methodology():
    return render_template("methodology.html")


# ─────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────
if __name__ == "__main__":
    init_db()          # Create DB tables on first run
    app.run(debug=True)