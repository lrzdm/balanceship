import streamlit as st
import random
import time
from streamlit.components.v1 import html

st.set_page_config(layout="wide")

# Sample data for the ticker
sample_data = [
    ("AAPL", "+1.2%"),
    ("TSLA", "-2.5%"),
    ("MSFT", "+0.8%"),
    ("GOOGL", "+1.0%"),
    ("AMZN", "-0.3%"),
    ("NVDA", "+2.3%"),
    ("META", "-1.4%")
]

# Randomize colors
def get_random_color():
    return random.choice(["#00ff00", "#ff0000", "#00ffff", "#ffa500", "#ff69b4", "#ffffff"])

# HTML for the page
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
    position: absolute;
    top: 0;
    width: 100%;
    display: flex;
    justify-content: space-around;
    align-items: center;
    background: rgba(0, 0, 0, 0.8);
    padding: 1rem;
    z-index: 10;
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
    position: absolute;
    top: 60px;
    width: 100%;
    background-color: black;
    overflow: hidden;
    height: 40px;
    border-top: 2px solid #333;
    border-bottom: 2px solid #333;
    z-index: 9;
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

for name, value in sample_data:
    html_code += f'<span class="ticker-item" style="color:{get_random_color()};">{name}: {value}</span>'

html_code += """
  </div>
</div>
"""

html(html_code, height=300)

# Optional content or intro text
st.markdown("""
<div style='position:relative; top:160px; color:white; text-align:center;'>
    <h1>Welcome to Financial Insights Hub</h1>
    <p>Real-time analysis, smart data. Make better financial decisions.</p>
</div>
""", unsafe_allow_html=True)

# Cool additional section: Trending KPIs
st.markdown("""
<div style='position:relative; top:200px; text-align:center; padding:2rem;'>
    <h2 style='color:#00f7ff;'>🚀 Trending Financial Metrics</h2>
    <p style='color:white;'>Keep an eye on what's moving the markets. Explore key KPIs updated live from our database.</p>
    <div style='display:flex; justify-content:center; gap:2rem; flex-wrap:wrap;'>
        <div style='background-color:#111; padding:1.5rem; border-radius:12px; color:#0f0; min-width:200px;'>
            <h3>Debt/Equity</h3>
            <p>0.56</p>
        </div>
        <div style='background-color:#111; padding:1.5rem; border-radius:12px; color:#f00; min-width:200px;'>
            <h3>ROE</h3>
            <p>18.9%</p>
        </div>
        <div style='background-color:#111; padding:1.5rem; border-radius:12px; color:#0ff; min-width:200px;'>
            <h3>Net Margin</h3>
            <p>12.3%</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# AI-generated insight box
st.markdown("""
<div style='position:relative; top:240px; text-align:center; padding:2rem; background-color:#0a0a0a; color:white;'>
    <h2 style='color:#00f7ff;'>🤖 Snapshot AI Insights</h2>
    <p style='font-size:18px;'>"Nel Q1 il margine operativo medio è cresciuto del <span style='color:#00ff00;'>+12%</span> tra le mid-cap europee, trainato da energia e tech."</p>
</div>
""", unsafe_allow_html=True)

# Dynamic geographic visualization (placeholder image)
st.markdown("""
<div style='position:relative; top:260px; text-align:center; padding:2rem;'>
    <h2 style='color:#00f7ff;'>🌍 Global Data Coverage</h2>
    <img src='https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/World_map_-_low_resolution_gray_political.png/1200px-World_map_-_low_resolution_gray_political.png' width='60%' style='border-radius:15px; box-shadow: 0 0 10px rgba(0,0,0,0.7);'>
    <p style='color:white; margin-top:1rem;'>We track financial KPIs across global markets, industries, and economies.</p>
</div>
""", unsafe_allow_html=True)
