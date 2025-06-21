import streamlit as st
import random
import time
from streamlit.components.v1 import html
import datetime
from cache_db import load_from_db
from data_utils import read_exchanges, read_companies
import base64
import os

st.set_page_config(layout="wide")

# ---- AUTOREFRESH EVERY 60 SECONDS ----
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

REFRESH_INTERVAL = 60
if time.time() - st.session_state.last_refresh > REFRESH_INTERVAL:
    st.session_state.last_refresh = time.time()
    st.experimental_rerun()

# ---- KPI & AI PHRASE CONFIG ----
kpi_fields = [
    ("total_revenue", "revenue", "reported a revenue of {val}B USD"),
    ("ebit", "EBIT", "had an EBIT of {val}B USD"),
    ("ebitda", "EBITDA", "posted an EBITDA of {val}B USD"),
    ("free_cash_flow", "Free Cash Flow", "generated Free Cash Flow of {val}B USD"),
    ("net_income", "net profit", "achieved a net profit of {val}B USD"),
    ("basic_eps", "EPS", "had an EPS of {val}"),
    ("cost_of_revenue", "COGS", "reported COGS of {val}B USD"),
    ("total_debt", "total debt", "closed the year with total debt of {val}B"),
    ("total_assets", "total assets", "held total assets worth {val}B"),
    ("operating_income", "operating income", "reached operating income of {val}B"),
    ("gross_profit", "gross profit", "achieved gross profit of {val}B"),
    ("pretax_income", "pre-tax income", "earned pre-tax income of {val}B")
]

# ---- LOAD ALL TICKERS FROM DB ----
def get_all_tickers():
    exchanges = read_exchanges("exchanges.txt")
    tickers = []
    for ex in exchanges.values():
        companies = read_companies(ex)
        for c in companies:
            if 'ticker' in c:
                tickers.append(c['ticker'])
    return list(set(tickers))

# ---- RANDOM SNAPSHOT INSIGHT ----
def load_random_snapshot():
    tickers = get_all_tickers()
    ticker = random.choice(tickers)
    year = random.choice(["2021", "2022", "2023"])
    data = load_from_db(ticker, [year])
    if not data or not data[0]:
        return "Data not available."
    d = data[0]
    random.shuffle(kpi_fields)
    for key, label, phrase in kpi_fields:
        val = d.get(key)
        if val and isinstance(val, (int, float)) and val != 0:
            val_fmt = f"{val:.2f}"
            return f"In {year}, {ticker} {phrase.format(val=val_fmt)}."
    return "Data incomplete for insight."

if "snapshot_timestamp" not in st.session_state:
    st.session_state.snapshot_timestamp = time.time()
    st.session_state.snapshot_phrase = load_random_snapshot()

if time.time() - st.session_state.snapshot_timestamp > 120:
    st.session_state.snapshot_phrase = load_random_snapshot()
    st.session_state.snapshot_timestamp = time.time()

# ---- LOAD TICKER DATA FOR BAR ----
def load_ticker_bar_data():
    tickers = get_all_tickers()
    sampled = random.sample(tickers, min(25, len(tickers)))  # genera 25
    years = ["2021", "2022", "2023"]
    result = []
    for t in sampled:
        y = random.choice(years)
        data = load_from_db(t, [y])
        if data and isinstance(data[0], dict):
            d = data[0]
            key, label, _ = random.choice(kpi_fields)
            val = d.get(key)
            if val:
                try:
                    val_fmt = f"{float(val):.2f}"
                    result.append((t, y, f"{label.title()}: {val_fmt}B"))
                except:
                    continue
    return result

bar_items = load_ticker_bar_data()

def get_random_color():
    return random.choice(["#00ff00", "#ff0000", "#00ffff", "#ffa500", "#ff69b4", "#ffffff"])

# ---- LOAD LOGOS ----
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo1 = get_base64_image("images/logo1.png")
logo2 = get_base64_image("images/logo2.png")

html_code = f"""
<style>
  body, .block-container {{
    padding-left: 0 !important;
    padding-right: 0 !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
  }}

  .video-background {{
    position: fixed;
    right: 0;
    bottom: 0;
    min-width: 100%;
    min-height: 100%;
    z-index: -1;
    object-fit: cover;
  }}
  .navbar {{
   position: fixed;
   top: 0;
   width: 100%;
   display: flex;
   align-items: center;
   background: rgba(0, 0, 0, 0.8);
   padding: 0.5rem 1rem;
   z-index: 999;
   gap: 2rem;           /* aggiunto gap tra logo e link */
  }}
 .navbar-left {{
   display: flex;
   align-items: center;
   gap: 15px;
   flex-shrink: 0;      /* impedisce che il logo si riduca */
 }}
  .navbar-right {{
    display: flex;
    align-items: center;
    gap: 1.5rem;         /* spazio tra i link */
    margin-left: 1rem;   /* riduci il margine sinistro per avvicinare i link */
  }}
  .navbar-left img {{
    height: 50px;
  }}
  .navbar a {{
    color: white;
    text-decoration: none;
    font-weight: bold;
    margin-left: 2rem;
    transition: color 0.3s;
  }}
  .navbar a:hover {{
    color: #00f7ff;
  }}
  .ticker-bar {{
    position: fixed;
    top: 70px;
    width: 100%;
    background-color: black;
    overflow: hidden;
    height: 40px;
    border-top: 2px solid #333;
    border-bottom: 2px solid #333;
    z-index: 998;
    display: flex;
    align-items: center;
  }}
  .ticker-content {{
    display: inline-block;
    white-space: nowrap;
    animation: ticker 60s linear infinite;
  }}
  @keyframes ticker {{
    from {{ transform: translateX(0%); }}
    to {{ transform: translateX(-50%); }}
  }}
  .ticker-item {{
    display: inline-block;
    margin: 0 2rem;
    font-size: 1rem;
    font-family: monospace;
    line-height: 40px;
  }}
</style>

<video autoplay muted loop class="video-background">
  <source src="your-company-video.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

<div class="navbar">
  <div class="navbar-left">
    <img src="data:image/png;base64,{logo1}" />
    <img src="data:image/png;base64,{logo2}" />
  </div>
  <div class="navbar-right">
    <a href="#">Home</a>
    <a href="#">Financials</a>
    <a href="#">Insights</a>
    <a href="#">About Us</a>
    <a href="#">Contact</a>
  </div>
</div>

<div class="ticker-bar">
  <div class="ticker-content" id="ticker-content">
"""

for t, y, val in bar_items:
    html_code += f'<span class="ticker-item" style="color:{get_random_color()};">{t} ({y}): {val}</span>'

# Duplico il contenuto per continuità senza pause
for t, y, val in bar_items:
    html_code += f'<span class="ticker-item" style="color:{get_random_color()};">{t} ({y}): {val}</span>'

html_code += """
  </div>
</div>
"""


html(html_code, height=300)

# ---- HEADLINE ----
st.markdown("""
<div style='position:relative; top:160px; color:black; text-align:center;'>
    <h1>Welcome to Financial Insights Hub</h1>
    <p>Real-time analysis, smart data. Make better financial decisions.</p>
</div>
""", unsafe_allow_html=True)

# ---- SNAPSHOT INSIGHT ----
st.markdown(f"""
<div style='position:relative; top:200px; text-align:center; padding:2rem; background-color:#0a0a0a; color:white;'>
    <h2 style='color:#00f7ff;'>🤖 Snapshot AI Insights</h2>
    <p style='font-size:18px;'>{st.session_state.snapshot_phrase}</p>
</div>
""", unsafe_allow_html=True)

# ---- GLOBAL COVERAGE ----
# mostra mappa locale
st.image("images/World-Map.png", use_column_width=True)

# overlay pallini con html + css
locations = {
    "Rome": (50, 80),    # posizioni x,y in pixel o percentuali sulla mappa (da regolare)
    "New York": (150, 100),
    "Tokyo": (300, 120),
}

dots_html = "<div style='position:relative; margin-top:-300px; width:100%; height:0;'>"
for city, (x, y) in locations.items():
    dots_html += f"""
    <div title="{city}" style='
        position: absolute;
        top: {y}px;
        left: {x}px;
        width: 12px;
        height: 12px;
        background: red;
        border-radius: 50%;
        border: 2px solid white;
        cursor: pointer;
        z-index: 10;
    '></div>
    """
dots_html += "</div>"

st.markdown(dots_html, unsafe_allow_html=True)

