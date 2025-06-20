import streamlit as st
import os, base64
from PIL import Image

st.set_page_config(page_title="Who We Are", layout="wide")

# Base64 helper
def get_base64(path):
    with open(path, 'rb') as f: return base64.b64encode(f.read()).decode()

# --- CSS ---
st.markdown("""
<style>
body { background-color: #eceff1; color: #263238; }
.logo-container { display: flex; justify-content: center; gap: 30px; margin: 30px auto; flex-wrap: wrap; }
.logo-large { height: 90px; }
.logo-small { height: 60px; }
.startup-box { background: #f5f5f5; border-left: 6px solid #0288d1; border-radius: 10px; padding: 30px; margin: 30px; }
.description-block { background: #fff; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); padding: 40px; margin: 20px; }
.profile-grid { display: flex; justify-content: center; gap: 30px; margin: 30px; }
.profile-card { background: #fff; width: 260px; height: 360px; border-radius: 12px; perspective: 1000px; }
.profile-inner { position: relative; width: 100%; height: 100%; text-align: center; transition: transform 0.8s; transform-style: preserve-3d; }
.profile-card:hover .profile-inner { transform: rotateY(180deg); }
.profile-front, .profile-back { position: absolute; width: 100%; height: 100%; backface-visibility: hidden; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; }
.profile-front { background: #0288d1; color: #fff; }
.profile-back { background: #fff; color: #263238; transform: rotateY(180deg); }
.profile-front img { border-radius: 50%; width: 120px; height: 120px; object-fit: cover; margin-bottom: 20px; }
.timeline-block { background-color: #fff; border-radius: 12px; padding: 40px; margin: 40px auto; max-width: 800px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.timeline-block h2 { text-align: center; margin-bottom: 40px; }
.timeline-item { display: flex; align-items: flex-start; margin-bottom: 30px; }
.timeline-year { background: #0288d1; color: #fff; padding: 10px 20px; border-radius: 20px; margin-right: 20px; font-weight: bold; min-width: 80px; text-align: center; }
.video-container { display: flex; justify-content: center; margin: 30px; }
</style>
""", unsafe_allow_html=True)

# --- Logo Top ---
logo_html = ""
for path, cls in [("images/logo1.png","logo-large"),("images/logo2.png","logo-small")]:
    if os.path.exists(path):
        logo_html += f'<img src="data:image/png;base64,{get_base64(path)}" class="{cls}">'
st.markdown(f"<div class='logo-container'>{logo_html}</div>", unsafe_allow_html=True)

# --- Startup Info ---
st.markdown("""
<div class='startup-box'>
  <h2>🚀 Our Startup</h2>
  <ul style='list-style:none; padding-left:0'>
    <li><strong>Founded:</strong> 2025</li>
    <li><strong>Sector:</strong> Finance & Data Analytics</li>
    <li><strong>HQ:</strong> Rome, Italy</li>
    <li><strong>Mission:</strong> Empower businesses with intelligent financial tools</li>
  </ul>
</div>
""", unsafe_allow_html=True)

# --- Embedded Video ---
st.markdown("""
<div class='video-container'>
  <iframe width="800" height="450" src="https://www.youtube.com/embed/YOUR_VIDEO_ID"
    title="Balanceship Presentation" frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen></iframe>
</div>
""", unsafe_allow_html=True)

# --- Company Description ---
st.markdown("""
<div class='description-block'>
    <h2 style='text-align: center;'>🏢 About Us</h2>
    <p><strong>Balanceship</strong> means clarity and control over financial data. Just like steering a well-balanced ship, our tools help you navigate company financials with ease and confidence.</p>
    <p>We believe financial analysis should be intuitive, actionable, and beautiful. That’s why we design tools that speak the language of business professionals—clear dashboards, strong KPIs, and powerful benchmarking.</p>
    <div style='margin-top: 30px; font-weight: bold; text-align: center; color: #2575fc;'>
        Navigate the financial sea with clarity ⚓
    </div>
</div>
""", unsafe_allow_html=True)

# --- Team Profiles ---
st.markdown("<h2 style='text-align:center; margin-top:40px;'>👥 Our Team</h2>", unsafe_allow_html=True)
profiles = [
  ("Lorenzo De Meo","Engineer + MBA…","images/Lorenzo De Meo_01.jpg"),
  ("William H Gazzo","Business strategist…","images/William H Gazzo_01.jpg"),
  ("Gabriele Schininà","Finance expert…","images/Gabriele Schinina_01.jpg"),
  ("Giovanni Serusi","Neuroscientist + economist…","images/Giovanni Serusi_01.jpg"),
]
cards = ""
for name, desc, img in profiles:
    if not os.path.exists(img): continue
    cards += f"""
    <div class='profile-card'>
      <div class='profile-inner'>
        <div class='profile-front'>
          <img src="data:image/jpeg;base64,{get_base64(img)}">
          <h4>{name}</h4>
        </div>
        <div class='profile-back'>
          <h4>{name}</h4>
          <p style='font-size:14px;'>{desc}</p>
        </div>
      </div>
    </div>"""
st.markdown(f"<div class='profile-grid'>{cards}</div>", unsafe_allow_html=True)

# --- TIMELINE ---
st.markdown("<h2 style='text-align: center;'>📈 Our Journey</h2>", unsafe_allow_html=True)
st.markdown("""
<div class='timeline'>
    <div class='timeline-box left'>
        <div class='timeline-content'>
            <h4>2025 – Foundation</h4>
            <p>Balanceship is born in Rome with the goal of making financial insights accessible.</p>
        </div>
    </div>
    <div class='timeline-box right'>
        <div class='timeline-content'>
            <h4>2026 – MVP Launch</h4>
            <p>Released the first version of our data platform for financial ratio visualization.</p>
        </div>
    </div>
    <div class='timeline-box left'>
        <div class='timeline-content'>
            <h4>2027 – Strategic Clients</h4>
            <p>Onboarded early enterprise clients and improved benchmarking features.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Contacts ---
insta, lin = get_base64("images/IG.png"), get_base64("images/LIN.png")
st.markdown(f"""
<div style='background:#f5f5f5;padding:40px;border-radius:12px; text-align:center; box-shadow:0 3px 10px rgba(0,0,0,0.05); margin:30px'>
  <h3>📬 Contact Us</h3>
  <p>Interested in collaborating? <a href='mailto:your-email@example.com'>Send us an email</a></p>
  <a href='#'><img src='data:image/png;base64,{insta}' width='40' style='margin:10px'></a>
  <a href='#'><img src='data:image/png;base64,{lin}' width='40' style='margin:10px'></a>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
sidebar_logo = get_base64("images/logo4.png") if os.path.exists("images/logo4.png") else ""
st.sidebar.markdown(f"""
<div style='text-align:center;margin-top:20px'>
  <img src="data:image/png;base64,{sidebar_logo}" width='120'><br>
  <small>Navigate the financial sea with clarity ⚓</small><br>
  <a href='#'><img src='data:image/png;base64,{insta}' width='30' style='margin:5px'></a>
  <a href='#'><img src='data:image/png;base64,{lin}' width='30' style='margin:5px'></a>
</div>
""", unsafe_allow_html=True)
