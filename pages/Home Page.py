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
    #st.experimental_rerun()

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

if time.time() - st.session_state.snapshot_timestamp > 30:
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
  .stApp, .main, .block-container {{
    background-color: rgba(0, 0, 0, 0) !important;
    background: transparent !important;
  }}
  .navbar {{
    position: fixed;
    top: 0;
    width: 100%;
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 1);
    padding: 0.5rem 1rem;
    z-index: 999;
    gap: 2rem;
    color: black;
  }}
  .navbar-left {{
    display: flex;
    align-items: center;
    gap: 15px;
    flex-shrink: 0;
  }}
  .navbar-right {{
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-left: 7rem;
  }}
  .navbar-left img {{
    height: 50px;
  }}
  .navbar a {{
    color: #0173C4;           /* blu pagina */
    text-decoration: none;
    font-weight: bold;
    margin-left: 2rem;
    padding: 0.3rem 0.6rem;   /* spazio interno per il box */
    border-radius: 5px;       /* angoli arrotondati */
    transition: background-color 0.3s, color 0.3s;
    display: inline-block;    /* per applicare padding e background */
  }}
  .navbar a:hover {{
    background-color: #0173C4;  /* sfondo blu */
    color: white;               /* testo bianco */
    cursor: pointer;
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
  .video-background {{
    position: fixed;
    top: 110px;
    right: 0;
    bottom: 0;
    min-width: 100%;
    height: calc(100% - 110px);
    z-index: -1;
    object-fit: cover;
    opacity: 0.8;
    background-color: black;
  }}
</style>

<video autoplay loop class="video-background">
  <source src="https://www.dropbox.com/scl/fi/zpyh82bkpbhoi2dkf78f4/test_video.mp4?rlkey=td6g1wyi08kt6ko59fmsdzqa7&st=ly84c83k&raw=1" type="video/mp4">
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


html(html_code, height=800)

# ---- HEADLINE ----
st.markdown("""
<div style='position:relative; top:100px; color:#0173C4; text-align:center;'>
    <h1 style="text-shadow: 1px 1px 2px black;">Welcome to BalanceShip Financial Hub</h1>
    <p>Real-time analysis, smart data. Make better financial decisions.</p>
</div>
""", unsafe_allow_html=True)

#------BOX MAPPA E INSIGHTS----------
import streamlit as st
from PIL import Image

# Prendo la frase dal session_state
snapshot_phrase = st.session_state.get("snapshot_phrase", "Your AI-driven financial insight here...")

# Carico e ridimensiono l'immagine
map_base64 = get_base64_image("images/Map_Chart.png")
new_width = 300 

# Layout con box affiancati
st.markdown(f"""
<style>
  .container-flex {{
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin-top: 120px;
    flex-wrap: wrap;
  }}
  .box-insight {{
    flex: 1 1 350px;
    background-color: #0a0a0a;
    color: white;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(1, 115, 196, 0.4);
    min-width: 300px;
  }}
  .box-insight h2 {{
    color: #0173C4;
    margin-bottom: 1rem;
  }}
  .box-insight p {{
    font-size: 1.2rem;
    line-height: 1.4;
  }}
  .box-map {{
    flex: 1 1 350px;
    background-color: white;
    padding: 1rem;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(1, 115, 196, 0.3);
    display: flex;
    justify-content: center;
    align-items: center;
    min-width: 300px;
    transition: transform 0.3s ease;
  }}
  .box-map:hover {{
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(1, 115, 196, 0.6);
  }}
  .box-map h3 {{
    color: #0173C4;
    text-align: center;
    margin-bottom: 1rem;
  }}
  img.map-image {{
    border-radius: 12px;
    max-width: 100%;
    height: auto;
  }}
</style>

<div class="container-flex">
  <div class="box-insight">
    <h2>🤖 Snapshot Insights</h2>
    <p>{snapshot_phrase}</p>
  </div>
  <div class="box-map">
    <div>
      <h3>🌍 Stock Exchanges on our databases</h3>
      <img src="data:image/png;base64,{map_base64}" alt="Map Chart" class="map-image" style="width:{new_width}px;" />
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

