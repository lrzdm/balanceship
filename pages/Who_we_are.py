import streamlit as st
import os
from PIL import Image
import base64

# Configurazione pagina
st.set_page_config(page_title="Who We Are", layout="wide")

# Funzione per codifica base64 immagini
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

# --- CSS Personalizzato ---
st.markdown("""
<style>
    body {
        background-color: #f8f9fb;
        color: #1f1f1f;
        font-family: 'Segoe UI', sans-serif;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 30px;
        margin: 30px auto 10px auto;
        flex-wrap: wrap;
    }
    .logo-large {
        height: 90px;
    }
    .logo-small {
        height: 60px;
    }
    .startup-box {
        background: linear-gradient(to right, #e0ecf8, #ffffff);
        border-left: 6px solid #2575fc;
        border-radius: 10px;
        padding: 30px;
        margin: 30px auto;
    }
    .description-block {
        padding: 40px 25px;
        font-size: 18px;
        background-color: #ffffff;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.07);
        line-height: 1.6;
    }
    .profile-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        margin-bottom: 25px;
    }
    .contact-section {
        margin-top: 60px;
        padding: 40px 20px;
        background-color: #f0f4f8;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 3px 10px rgba(0,0,0,0.04);
    }
    .contact-section h3 {
        margin-bottom: 20px;
    }
    .social-icons a {
        margin: 0 12px;
        font-size: 24px;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGHI IN ALTO ---
logo_html = ""
for logo_path, cls in [("images/logo1.png", "logo-large"), ("images/logo2.png", "logo-small")]:
    if os.path.exists(logo_path):
        logo_b64 = get_base64_of_bin_file(logo_path)
        logo_html += f'<img src="data:image/png;base64,{logo_b64}" class="{cls}">' 

st.markdown(f"<div class='logo-container'>{logo_html}</div>", unsafe_allow_html=True)

# --- INFO STARTUP ---
st.markdown("""
<div class='startup-box'>
    <h2 style='text-align: center;'>🚀 Our Startup</h2>
    <ul style='list-style: none; padding-left: 0; font-size: 16px;'>
        <li><strong>Founded:</strong> 2025</li>
        <li><strong>Sector:</strong> Finance & Data Analytics</li>
        <li><strong>Headquarters:</strong> Rome, Italy</li>
        <li><strong>Mission:</strong> Empower businesses with intelligent financial tools</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# --- DESCRIZIONE ---
st.markdown("""
<div class='description-block'>
    <h2 style='text-align: center;'>🏢 About Us</h2>
    <p>At <strong>Balanceship</strong>, we bring clarity and simplicity to financial data.
    Navigating complex information should feel like steering a well-balanced ship.
    Our platform offers a calm, clear view on company financials—trustworthy, benchmarked, and intuitive.
    Whether you're analyzing markets, evaluating competitors, or making strategic calls, Balanceship provides tools to unlock insight with confidence.</p>
    <div style='margin-top: 30px; font-weight: bold; text-align: center; color: #2575fc;'>
        Navigate the financial sea with clarity ⚓
    </div>
</div>
""", unsafe_allow_html=True)

# --- TEAM ---
st.markdown("<h2 style='text-align: center;'>👥 Our Team</h2>", unsafe_allow_html=True)

profiles = [
    { 'name': 'Lorenzo De Meo', 'description': 'Engineer + MBA. Expertise in financial reporting, audit & risk management. Skilled in Power BI and Python for data analytics.', 'image_path': 'images/Lorenzo De Meo_01.jpg' },
    { 'name': 'William Herbert Gazzo', 'description': 'Business strategist with SDA Bocconi training. Specializes in project management, business planning and financial control.', 'image_path': 'images/William H Gazzo_01.jpg' },
    { 'name': 'Gabriele Schininà', 'description': 'Finance expert from SDA Bocconi. Strong background in financial modeling, strategic planning and multinational business controlling.', 'image_path': 'images/Gabriele Schinina_01.jpg' },
    { 'name': 'Giovanni Serusi', 'description': 'Neuroscientist and economist from SDA Bocconi. Focused on competitive intelligence and investment opportunities in life sciences.', 'image_path': 'images/Giovanni Serusi_01.jpg' }
]

for profile in profiles:
    with st.container():
        cols = st.columns([1, 3])
        with cols[0]:
            if os.path.exists(profile['image_path']):
                img = Image.open(profile['image_path'])
                st.image(img, use_container_width=True)
        with cols[1]:
            st.markdown(f"<div class='profile-card'><h4>{profile['name']}</h4><p>{profile['description']}</p></div>", unsafe_allow_html=True)

# --- CONTATTI ---
instagram_icon = get_base64_of_bin_file("images/IG.png")
linkedin_icon = get_base64_of_bin_file("images/LIN.png")

st.markdown(f"""
<div class='contact-section'>
    <h3>📬 Contact Us</h3>
    <p>Interested in collaborating? <a href='mailto:your-email@example.com'>Send us an email</a> or follow us:</p>
    <div style='display: flex; justify-content: center; gap: 20px;'>
        <a href='https://www.instagram.com/tuo_profilo' target='_blank'>
            <img src='data:image/png;base64,{instagram_icon}' width='40' height='40'>
        </a>
        <a href='https://www.linkedin.com/in/tuo_profilo' target='_blank'>
            <img src='data:image/png;base64,{linkedin_icon}' width='40' height='40'>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
sidebar_logo_path = "images/logo4.png"
sidebar_logo = get_base64_of_bin_file(sidebar_logo_path) if os.path.exists(sidebar_logo_path) else ""

st.sidebar.markdown(f"""
<div style='text-align: center;'>
    <img src="data:image/png;base64,{sidebar_logo}" style="height: 70px; margin-top: 20px;"><br>
    <span style='font-size: 14px;'>Navigate financial sea with clarity!</span><br>
    <a href='https://www.instagram.com/tuo_profilo' target='_blank'>
        <img src='data:image/png;base64,{instagram_icon}' width='35' height='35' style='margin: 10px;'>
    </a>
    <a href='https://www.linkedin.com/in/tuo_profilo' target='_blank'>
        <img src='data:image/png;base64,{linkedin_icon}' width='35' height='35' style='margin: 10px;'>
    </a>
</div>
""", unsafe_allow_html=True)
