import streamlit as st
import os
from PIL import Image
import base64

# Configurazione della pagina
st.set_page_config(page_title="Who We Are", layout="wide")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- LOGHI IN ALTO ---
logo1_path = os.path.join("images", "logo1.png")
logo2_path = os.path.join("images", "logo2.png")

logo_html = ""
if os.path.exists(logo1_path):
    logo1_base64 = get_base64_of_bin_file(logo1_path)
    logo_html += f'<img src="data:image/png;base64,{logo1_base64}" class="logo logo-large">'

if os.path.exists(logo2_path):
    logo2_base64 = get_base64_of_bin_file(logo2_path)
    logo_html += f'<img src="data:image/png;base64,{logo2_base64}" class="logo logo-small">'

logo_html = f"<div class='logo-container'>{logo_html}</div>"

st.markdown(f"""
<style>
    .logo-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 30px;
        margin: 20px auto;
        flex-wrap: wrap;
    }}
    .logo {{
        display: block;
    }}
    .logo-large {{
        height: 100px;
    }}
    .logo-small {{
        height: 60px;
    }}
    .startup-box {{
        background-color: #f0f2f6;
        border-radius: 12px;
        padding: 25px;
        margin: 30px auto;
    }}
    .description-block {{
        padding: 40px 20px;
        text-align: justify;
        font-size: 18px;
    }}
    .profile-card {{
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }}
    .contact-section {{
        margin-top: 50px;
        padding: 30px;
        background-color: #f9f9f9;
        border-radius: 12px;
        text-align: center;
    }}
    .social-icons a {{
        margin: 0 10px;
        font-size: 24px;
        text-decoration: none;
    }}
    @media screen and (max-width: 768px) {{
        .description-block {{
            font-size: 16px;
        }}
        .profile-card h4 {{
            font-size: 18px;
        }}
        .profile-card p {{
            font-size: 14px;
        }}
    }}
</style>
{logo_html}
""", unsafe_allow_html=True)

# --- INFORMAZIONI STARTUP ---
st.markdown("""
<div class='startup-box'>
    <h2 style='text-align: center;'>🚀Our Startup</h2>
    <ul style='list-style: none; padding-left: 0; font-size: 16px;'>
        <li><strong>Founded:</strong> 2025</li>
        <li><strong>Sector:</strong> Finance & Data Analytics</li>
        <li><strong>Headquarters:</strong> Rome, Italy</li>
        <li><strong>Mission:</strong> Empower businesses with intelligent financial tools</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# --- DESCRIZIONE AZIENDA ---
st.markdown("""
<div class='description-block'>
    <h2 style='text-align: center;'>🏢 About Us</h2>
    <p>At Balanceship, we’re on a mission to bring clarity and simplicity to financial data.\
    Navigating financial information should be like sailing a well-balanced ship—steady, reliable, and easy to steer.\
    In a world full of complex numbers and overwhelming reports, Balance-ship provides a calm, clear view. We help users compare and benchmark\
    company financials in a straightforward, visually intuitive way. Our platform is designed to give you trustworthy insights-fast.\
    Whether you're exploring markets, tracking competitors, or making strategic decisions, Balanceship offers a streamlined way to compare\
    financials across companies-with accuracy, transparency, and ease. We’re here to be the go-to source for smart, simple financial comparison.
<div style='margin-top: 20px; font-weight: bold; text-align: center;'>
    We are Balanceship. Built for clarity. Backed by data. Designed for everyone.
</div>
""", unsafe_allow_html=True)

# --- PROFILI ---
st.markdown("<h2 style='text-align: center;'>👥 Our Team</h2>", unsafe_allow_html=True)

profiles = [
    {
        'name': 'Lorenzo De Meo',
        'description': 'Professional with an engineering background and an MBA, specializing in financial reporting, internal audit, and risk management.\
Experienced in financial analysis, accounting, and managing financial risks to support strategic decision-making. Proficient in leveraging Power BI and \
Python for data-driven insights.',
        'image_path': 'images/Lorenzo De Meo_01.jpg'
    },
    {
        'name': 'William Herbert Gazzo',
        'description': 'Professional with a solid business background and a professional training from SDA Bocconi. \
Specializing in project management, business planning, and the management of financing and budgets. He boasts extensive experience in consulting firms \
and multinational companies, where he has held managerial roles.',
        'image_path': 'images/William H Gazzo_01.jpg'
    },
    {
        'name': 'Gabriele Schininà',
        'description': 'Professional with a solid economic and financial background and training from SDA Bocconi. Specializing in financial modelling, \
strategic planning, and budget management. He boasts extensive experience in listed and non-listed multinational companies, where he has held roles in \
business controlling.',
        'image_path': 'images/Gabriele Schinina_01.jpg'
    },
    {
        'name': 'Giovanni Serusi',
        'description': 'Professional with a solid scientific background, specializing in clinical and cognitive neuroscience and with economic training\
from SDA Bocconi. Specializing in competitive intelligence and scouting new investment opportunities with a focus on the life-science sector.',
        'image_path': 'images/Giovanni Serusi_01.jpg'
    }
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

# Percorsi delle icone
instagram_icon_path = os.path.join("images", "IG.png")
linkedin_icon_path = os.path.join("images", "LIN.png")

# Converti le immagini in base64
instagram_icon_base64 = get_base64_of_bin_file(instagram_icon_path)
linkedin_icon_base64 = get_base64_of_bin_file(linkedin_icon_path)

# --- CONTATTI ---
# HTML per visualizzare le icone con link
##st.markdown(f"""
##<div style='display: flex; justify-content: center; gap: 20px;'>
##    <a href='https://www.instagram.com/tuo_profilo' target='_blank'>
##        <img src='data:image/png;base64,{instagram_icon_base64}' width='40' height='40'>
##    </a>
##    <a href='https://www.linkedin.com/in/tuo_profilo' target='_blank'>
##        <img src='data:image/png;base64,{linkedin_icon_base64}' width='40' height='40'>
##    </a>
##</div>
##""", unsafe_allow_html=True)

st.markdown(f"""
<div class='contact-section'>
    <h3>📬 Contact Us</h3>
    <p>If you want to collaborate or learn more about our project, feel free to <a href='mailto:your-email@example.com'>send us an email</a>.</p>
    <div style='display: flex; justify-content: center; gap: 20px;'>
        <a href='https://www.instagram.com/tuo_profilo' target='_blank'>
            <img src='data:image/png;base64,{instagram_icon_base64}' width='40' height='40'>
        </a>
        <a href='https://www.linkedin.com/in/tuo_profilo' target='_blank'>
            <img src='data:image/png;base64,{linkedin_icon_base64}' width='40' height='40'>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
logo_path = os.path.join("images", "logo4.png")
logo_base64 = get_base64_of_bin_file(logo_path) if os.path.exists(logo_path) else ""

st.sidebar.markdown(f"""
    <div style='text-align: center;'>
        <img src="data:image/png;base64,{logo_base64}" style='height: 70px;'><br>
        <span style='font-size: 14px;'>Your Name</span><br>
        <a href="https://github.com/tuo-username" target="_blank">🌐 LinkedIn</a>
    </div>
""", unsafe_allow_html=True)
