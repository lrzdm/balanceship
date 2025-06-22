import streamlit as st
import random
import time
from streamlit.components.v1 import html
import streamlit.components.v1 as components
import datetime
from cache_db import load_from_db
from data_utils import read_exchanges, read_companies
import base64
import os
from PIL import Image
from pages import Database, KPI_Dashboard, Who_we_are, Graph  # importa le tue pagine .py

st.set_page_config(layout="wide")

query_params = st.query_params
selected_page = query_params.get("page", ["Home"])[0]

# Routing logico in base al parametro
if selected_page == "Home":
    st.title("Home")
    st.write("Benvenuto nella homepage.")
elif selected_page == "Financials":
    Financials.app()
elif selected_page == "Insights":
    Insights.app()
elif selected_page == "About":
    About.app()
elif selected_page == "Contact":
    Contact.app()
else:
    st.error("Pagina non trovata.")


# Base64 helper
def get_base64(path):
    with open(path, 'rb') as f: return base64.b64encode(f.read()).decode()
        
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
    
@st.cache_data
def cached_all_tickers():
    return get_all_tickers()

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
                    b_metrics = ["total_revenue", "ebit", "ebitda", "free_cash_flow", "net_income", "cost_of_revenue", "total_debt", "total_assets", "operating_income", "gross_profit", "pretax_income"]
                    if key in b_metrics:
                        val_str = f"{val_fmt}B"
                    else:
                        val_str = val_fmt
                    
                    result.append((t, y, f"{label.title()}: {val_str}"))
                    #result.append((t, y, f"{label.title()}: {val_fmt}B"))
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

bg_home = "#0173C4" if selected_page == "Home" else "transparent"
color_home = "white" if selected_page == "Home" else "#0173C4"
bg_db = "#0173C4" if selected_page == "Database" else "transparent"
color_db = "white" if selected_page == "Database" else "#0173C4"
bg_ds = "#0173C4" if selected_page == "Dashboard" else "transparent"
color_ds = "white" if selected_page == "Dashboard" else "#0173C4"
bg_gr = "#0173C4" if selected_page == "Graphs" else "transparent"
color_gr = "white" if selected_page == "Graphs" else "#0173C4"
bg_our = "#0173C4" if selected_page == "Our Team" else "transparent"
color_our = "white" if selected_page == "Our Team" else "#0173C4"


# Inizio stringa HTML/CSS
html_code = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');

  html, body, .main {{
    font-family: 'Open Sans', sans-serif !important;
    font-size: 16px !important;
    color: black;
  }}
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
    margin-bottom: 50px;
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
    color: #0173C4;
    text-decoration: none;
    font-weight: bold;
    margin-left: 2rem;
    padding: 0.3rem 0.6rem;
    border-radius: 5px;
    transition: background-color 0.3s, color 0.3s;
    display: inline-block;
  }}
  .navbar a:hover {{
    background-color: #0173C4;
    color: white;
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
  @media (max-width: 768px) {{
    .navbar-right { flex-wrap: wrap; margin-left: 0; }
    .profile-grid { flex-direction: column; align-items: center; }
    .ticker-item { font-size: 0.8rem; margin: 0 1rem; }
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
    <a href="/?page=Home" style="background-color: {bg_home}; color: {color_home};">Home</a>
    <a href="/?page=Database" style="background-color: {bg_db}; color: {color_db};">Database</a>
    <a href="/?page=Dashboard" style="background-color: {bg_ds}; color: {color_ds};">Dashboard</a>
    <a href="/?page=Graphs" style="background-color: {bg_gr}; color: {color_gr};">Graphs</a>
    <a href="/?page=Our Team" style="background-color: {bg_our}; color: {color_our};">Our Team</a>
  </div>
</div>

<div class="ticker-bar">
  <div class="ticker-content" id="ticker-content">
"""

# Riduce lo spazio sopra (puoi regolare)
st.markdown("<style>.main {{padding-top: 0rem !important;}}</style>", unsafe_allow_html=True)

# Aggiunge spazio sotto la barra
st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)


# Aggiunta dinamica dei ticker (due volte per scorrimento fluido)
for t, y, val in bar_items * 2:  # duplica direttamente
    html_code += f'<span class="ticker-item" style="color:{get_random_color()};">{t} ({y}): {val}</span>'

# Chiusura blocco
html_code += """
  </div>
</div>
"""

# Rendering
html(html_code, height=800)


# ---- HEADLINE ----
st.markdown("""
<div style='margin-top: 100px; margin-bottom: 100px; color:#0173C4; text-align:center;'>
    <h1>Welcome to BalanceShip!</h1>
    <p>Smart data. Make better financial decisions.</p>
</div>
""", unsafe_allow_html=True)


#----BOX COUNTER AND MAP--------

n_companies = len(get_all_tickers())
n_years = 3
n_records = n_companies * n_years * 34

n_companies_fmt = format(n_companies, ",")
n_years_fmt = format(n_years, ",")
n_records_fmt = format(n_records, ",")

new_width = 300
map_base64 = get_base64_image("images/Map_Chart.png")


# CSS per le card animate in stile profili
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

.profile-grid {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 2rem;
    margin-top: 3rem;
}

.profile-card {
    width: 220px;
    height: 250px;
    perspective: 1000px;
}

.profile-inner {
    width: 100%;
    height: 100%;
    transition: transform 0.8s;
    transform-style: preserve-3d;
    position: relative;
    cursor: pointer;
}

.profile-card:hover .profile-inner {
    transform: rotateY(180deg);
}

.profile-front, .profile-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(1, 115, 196, 0.2);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    font-family: 'Open Sans', sans-serif;
}
.profile-front {
    background-color: #0173C4;
    color: white;
    padding: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.profile-front i {
    font-size: 2.8rem;
    margin-bottom: 0.5rem;
}

.profile-front h4 {
    font-size: 1.2rem;
    margin: 0;
    margin-top: 0.5rem 0 0 0;
}

.profile-back {
    background-color: #01c4a7;
    color: white;
    transform: rotateY(180deg);
    font-size: 2.2rem;
    font-weight: bold;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h3 style='text-align:center; color:#0173C4;'>📊 Our Data in Numbers</h3>", unsafe_allow_html=True)

# HTML delle card (tutte concatenate correttamente)
# HTML delle card con variabili dinamiche
cards = f"""
<div class='profile-grid'>
  <div class='profile-card'>
    <div class='profile-inner'>
      <div class='profile-front'>
        <i class='fas fa-building'></i>
        <h4>Companies</h4>
      </div>
      <div class='profile-back'>
        {n_companies_fmt}
      </div>
    </div>
  </div>
  <div class='profile-card'>
    <div class='profile-inner'>
      <div class='profile-front'>
        <i class='fas fa-database'></i>
        <h4>Records</h4>
      </div>
      <div class='profile-back'>
        {n_records_fmt}
      </div>
    </div>
  </div>
  <div class='profile-card'>
    <div class='profile-inner'>
      <div class='profile-front'>
        <i class='fas fa-calendar-alt'></i>
        <h4>Years</h4>
      </div>
      <div class='profile-back'>
        {n_years_fmt}
      </div>
    </div>
  </div>
</div>
"""

# Mostra le card
st.markdown(cards, unsafe_allow_html=True)
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

# Map section
st.markdown(f"""
<div class='map-box'>
  <h3 style='text-align:center; color:#0173C4;'>🌍 Stock Exchanges on our Databases</h3>
  <img src="data:image/png;base64,{map_base64}" class="map-img"/>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# --- Sidebar ---
insta, lin = get_base64("images/IG.png"), get_base64("images/LIN.png")
sidebar_logo = get_base64("images/logo4.png") if os.path.exists("images/logo4.png") else ""
st.sidebar.markdown(f"""
<div style='text-align:center;margin-top:20px'>
  <img src="data:image/png;base64,{sidebar_logo}" width='120'><br>
  <small>Navigate the financial sea with clarity ⚓</small><br>
  <a href='#'><img src='data:image/png;base64,{insta}' width='30' style='margin:5px'></a>
  <a href='#'><img src='data:image/png;base64,{lin}' width='30' style='margin:5px'></a>
</div>
""", unsafe_allow_html=True)

st.write("ciaooo!!!")
st.markdown("""
<hr style="margin-top:50px;"/>
<div style='text-align: center; font-size: 0.9rem; color: grey;'>
    &copy; 2025 BalanceShip. All rights reserved.
</div>
""", unsafe_allow_html=True)

