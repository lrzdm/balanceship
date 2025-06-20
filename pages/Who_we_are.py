import streamlit as st
import os
from PIL import Image
import base64

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Who We Are", layout="wide")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

# --- CSS PERSONALIZZATO ---
st.markdown("""
<style>
    body {
        background-color: #f3f4f6;
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
    .logo-large { height: 90px; }
    .logo-small { height: 60px; }

    .startup-box {
        background: linear-gradient(to right, #dee9f7, #ffffff);
        border-left: 6px solid #2575fc;
        border-radius: 10px;
        padding: 30px;
        margin: 30px auto;
        max-width: 900px;
    }

    .description-block {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 40px 30px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.05);
        max-width: 1000px;
        margin: auto;
        line-height: 1.6;
        font-size: 18px;
    }

    .profile-card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        transition: 0.3s;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }

    .profile-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }

    .contact-section {
        margin-top: 60px;
        padding: 50px 20px;
        background-color: #e5eaf2;
        border-radius: 15px;
        text-align: center;
    }

    .timeline {
        position: relative;
        max-width: 900px;
        margin: 40px auto;
    }

    .timeline::after {
        content: '';
        position: absolute;
        width: 4px;
        background-color: #2575fc;
        top: 0;
        bottom: 0;
        left: 50%;
        margin-left: -2px;
    }

    .timeline-box {
        padding: 20px 30px;
        background-color: white;
        position: relative;
        border-radius: 8px;
        width: 45%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.07);
    }

    .left { left: 0; }
    .right { left: 55%; }

    .timeline-box::before {
        content: "";
        position: absolute;
        top: 20px;
        width: 20px;
        height: 20px;
        background-color: #2575fc;
        border-radius: 50%;
        z-index: 1;
    }

    .left::before { right: -10px; }
    .right::before { left: -10px; }

    .timeline-content {
        font-size: 16px;
        line-height: 1.5;
    }

</style>
""", unsafe_allow_html=True)

# --- LOGHI ---
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
    <p><strong>Balanceship</strong> means clarity and control over financial data. Just like steering a well-balanced ship, our tools help you navigate company financials with ease and confidence.</p>
    <p>We believe financial analysis should be intuitive, actionable, and beautiful. That’s why we design tools that speak the language of business professionals—clear dashboards, strong KPIs, and powerful benchmarking.</p>
    <div style='margin-top: 30px; font-weight: bold; text-align: center; color: #2575fc;'>
        Navigate the financial sea with clarity ⚓
    </div>
</div>
""", unsafe_allow_html=True)

# --- VIDEO EMBED ---
st.markdown("<h2 style='text-align: center; margin-top: 50px;'>🎥 Watch Our Vision</h2>", unsafe_allow_html=True)
st.video("https://www.youtube.com/watch?v=PVWfopGXY1g")  # Sostituisci con il tuo link YouTube

# --- TEAM ---
st.markdown("<h2 style='text-align: center; margin-top: 60px;'>👥 Our Team</h2>", unsafe_allow_html=True)

profiles = [
    { 'name': 'Lorenzo De Meo', 'description': 'Engineer + MBA. Expertise in financial reporting, audit & risk management. Skilled in Power BI and Python for data analytics.', 'image_path': 'images/Lorenzo De Meo_01.jpg', 'linkedin': 'https://linkedin.com/in/lorenzodemeo' },
    { 'name': 'William H. Gazzo', 'description': 'Business strategist with SDA Bocconi training. Project management, business planning and financial control.', 'image_path': 'images/William H Gazzo_01.jpg', 'linkedin': 'https://linkedin.com/in/williamgazzo' },
    { 'name': 'Gabriele Schininà', 'description': 'Finance expert from SDA Bocconi. Strong in financial modeling, strategic planning and multinational controlling.', 'image_path': 'images/Gabriele Schinina_01.jpg', 'linkedin': 'https://linkedin.com/in/gabrieleschinina' },
    { 'name': 'Giovanni Serusi', 'description': 'Neuroscientist and economist from SDA Bocconi. Competitive intelligence & investments in life sciences.', 'image_path': 'images/Giovanni Serusi_01.jpg', 'linkedin': 'https://linkedin.com/in/giovanniserusi' }
]

for profile in profiles:
    with st.container():
        cols = st.columns([1, 3])
        with cols[0]:
            if os.path.exists(profile['image_path']):
                st.image(Image.open(profile['image_path']), use_container_width=True)
        with cols[1]:
            st.markdown(f"""
            <div class='profile-card'>
                <h4>{profile['name']}</h4>
                <p>{profile['description']}</p>
                <a href="{profile['linkedin']}" target="_blank" style='color: #2575fc; font-weight: bold;'>🔗 LinkedIn</a>
            </div>
            """, unsafe_allow_html=True)

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

# --- CONTATTI ---
instagram_icon = get_base64_of_bin_file("images/IG.png")
linkedin_icon = get_base64_of_bin_file("images/LIN.png")

st.markdown(f"""
<div class='contact-section'>
    <h3>📬 Contact Us</h3>
    <p>Want to collaborate? <a href='mailto:your-email@example.com'>Send us an email</a> or follow us:</p>
    <div style='margin-top: 20px;'>
        <a href='https://www.instagram.com/tuo_profilo' target='_blank'>
            <img src='data:image/png;base64,{instagram_icon}' width='40' height='40'>
        </a>
        <a href='https://www.linkedin.com/in/tuo_profilo' target='_blank'>
            <img src='data:image/png;base64,{linkedin_icon}' width='40' height='40' style='margin-left: 20px;'>
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
