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

st.set_page_config(layout="wide")


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

# Inizio stringa HTML/CSS
html_code = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');

  html, body, .main {{
    font-family: 'Open Sans', sans-serif !important;
    font-size: 18px !important;
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
    <h1>Welcome to BalanceShip Financial Hub</h1>
    <p>Real-time analysis, smart data. Make better financial decisions.</p>
</div>
""", unsafe_allow_html=True)


#----BOX COUNTER AND MAP--------

n_companies = len(get_all_tickers())
n_years = 3
n_records = n_companies * n_years * 34

new_width = 600
map_base64 = get_base64_image("images/Map_Chart.png")



# CSS per le card flip
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600&display=swap');

html, body, .main {
    font-family: 'Open Sans', sans-serif !important;
    background-color: #f8f9fa !important;
    padding: 0;
    margin: 0;
}

.container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: stretch;
    gap: 2rem;
    margin: 60px auto 40px auto;
    max-width: 1400px;
    padding: 0 2rem;
}

.box {
    flex: 1 1 400px;
    background-color: #f2f2f2;
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(1, 115, 196, 0.2);
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.box h2 {
    color: #0173C4;
    text-align: center;
    margin-bottom: 2rem;
}

.flip-card-container {
    display: flex;
    justify-content: space-around;
    gap: 2rem;
    flex-wrap: nowrap;
}

.flip-card {
    background-color: transparent;
    width: 140px;
    height: 160px;
    perspective: 1000px;
    cursor: pointer;
}

.flip-card-inner {
    position: relative;
    width: 100%;
    height: 100%;
    text-align: center;
    transition: transform 0.7s;
    transform-style: preserve-3d;
    border-radius: 15px;
    box-shadow: 0 8px 25px rgba(1, 115, 196, 0.2);
}

.flip-card.flipped .flip-card-inner {
    transform: rotateY(180deg);
}

.flip-card-front, .flip-card-back {
    position: absolute;
    width: 100%;
    height: 100%;
    -webkit-backface-visibility: hidden;
    backface-visibility: hidden;
    border-radius: 15px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 1rem;
    font-family: 'Orbitron', monospace;
}

.flip-card-front {
    background-color: #0173C4;
    color: white;
    font-size: 3rem;
    user-select: none;
}

.flip-card-front i {
    font-size: 3.5rem;
    margin-bottom: 0.5rem;
}

.flip-card-back {
    background-color: #01c4a7;
    color: white;
    transform: rotateY(180deg);
    font-size: 2.8rem;
    user-select: none;
}

.counter-label {
    margin-top: 10px;
    font-size: 1.1rem;
    font-weight: 600;
    color: #01395e;
    user-select: none;
}
</style>

<!-- Usa icone fontawesome CDN -->
<link
  href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
  rel="stylesheet"
/>
""", unsafe_allow_html=True)

# Container principale
st.markdown("<div class='container'>", unsafe_allow_html=True)

# Box contenente card
st.markdown("<div class='box'><h2>📊 Our Data in Numbers</h2>", unsafe_allow_html=True)

st.markdown("""
<div class="flip-card-container">
  <div class="flip-card" id="card1">
    <div class="flip-card-inner">
      <div class="flip-card-front">
        <i class="fas fa-building"></i>
        <div class="counter-label">Companies</div>
      </div>
      <div class="flip-card-back">{companies}</div>
    </div>
  </div>

  <div class="flip-card" id="card2">
    <div class="flip-card-inner">
      <div class="flip-card-front">
        <i class="fas fa-database"></i>
        <div class="counter-label">Records</div>
      </div>
      <div class="flip-card-back">{records}</div>
    </div>
  </div>

  <div class="flip-card" id="card3">
    <div class="flip-card-inner">
      <div class="flip-card-front">
        <i class="fas fa-calendar-alt"></i>
        <div class="counter-label">Years</div>
      </div>
      <div class="flip-card-back">{years}</div>
    </div>
  </div>
</div>
""".format(companies=f"{n_companies:,}", records=f"{n_records:,}", years=n_years), unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Box con mappa
st.markdown(f"""
<div class='box map-box'>
    <h3>🌍 Stock Exchanges on our Databases</h3>
    <img src="data:image/png;base64,{map_base64}" class="map-img" />
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# JS per flip al click
st.markdown("""
<script>
const cards = document.querySelectorAll('.flip-card');
cards.forEach(card => {
  card.addEventListener('click', () => {
    card.classList.toggle('flipped');
  });
});
</script>
""", unsafe_allow_html=True)
