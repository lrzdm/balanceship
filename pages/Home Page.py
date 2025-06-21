import streamlit as st
import random
import time
from streamlit.components.v1 import html
import datetime
from cache_db import load_from_db
from data_utils import read_exchanges, read_companies
import datetime

st.set_page_config(layout="wide")

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

REFRESH_INTERVAL = 60  # secondi
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
    sampled = random.sample(tickers, min(7, len(tickers)))
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

html_code = f"""
<style>
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
    justify-content: space-around;
    align-items: center;
    background: rgba(0, 0, 0, 0.8);
    padding: 1rem;
    z-index: 999;
  }}
  .navbar a {{
    color: white;
    text-decoration: none;
    font-weight: bold;
    transition: color 0.3s;
  }}
  .navbar a:hover {{
    color: #00f7ff;
  }}
  .ticker-bar {{
    position: fixed;
    top: 60px;
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
    animation: ticker 30s linear infinite;
  }}
  @keyframes ticker {{
    from {{ transform: translateX(100%); }}
    to {{ transform: translateX(-100%); }}
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
  <a href="#">Home</a>
  <a href="#">Financials</a>
  <a href="#">Insights</a>
  <a href="#">About Us</a>
  <a href="#">Contact</a>
</div>

<div class="ticker-bar">
  <div class="ticker-content">
"""

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
st.markdown("""
<div style='position:relative; top:240px; text-align:center; padding:2rem;'>
    <h2 style='color:#00f7ff;'>🌍 Global Data Coverage</h2>
    <img src='https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/World_map_-_low_resolution_gray_political.png/1200px-World_map_-_low_resolution_gray_political.png' width='60%' style='border-radius:15px; box-shadow: 0 0 10px rgba(0,0,0,0.7); background:white;'>
    <p style='color:white; margin-top:1rem;'>We track financial KPIs across global markets, industries, and economies.</p>
</div>
""", unsafe_allow_html=True)
