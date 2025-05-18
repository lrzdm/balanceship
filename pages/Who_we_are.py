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
</style>
{logo_html}
""", unsafe_allow_html=True)

# Contenuto della pagina
def run():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    st.title("👥 Who We Are")

    profiles = [
        {
            'name': 'Lorenzo De Meo',
            'description': 'Professional with an engineering background and an MBA, specializing in financial reporting, internal audit, and risk management. Experienced in financial analysis, accounting, and managing financial risks to support strategic decision-making. Proficient in leveraging Power BI and Python for data-driven insights. Proven ability to communicate complex financial information to senior leadership and build strong relationships with stakeholders.',
            'image_path': 'images/Lorenzo De Meo_01.jpg'
        },
        {
            'name': 'William Herbert Gazzo',
            'description': 'Professional with a solid business background and a professional training from SDA Bocconi. Specializing in project management, business planning, and the management of financing and budgets. He boasts extensive experience in consulting firms and multinational companies, where he has held managerial roles. Expert in managing projects across various sectors, from Automotive to FMCG, from Energy to Pharma, with a particular focus on the latter. Skilled in the use of PowerPoint and project management software, he has a proven ability to communicate complex information to C-level executives, both internally and externally. Always ready to face new challenges and contribute to achieving shared goals.',
            'image_path': 'images/person2.jpg'
        },
        {
            'name': 'Gabriele Schininà',
            'description': 'Professional with a solid economic and financial background and training from SDA Bocconi. Specializing in financial modelling, strategic planning, and budget management. He boasts extensive experience in listed and non-listed multinational companies, where he has held roles in business controlling. Expert in financial analysis, accounting, and managing budgets and forecasts, providing crucial support for strategic decision-making. Proficient in using Power BI and Excel to gain data-driven insights, he has a proven ability to communicate complex financial information to company leadership. Excels in building and maintaining strong relationships with internal and external stakeholders, thus contributing to a collaborative and results-oriented work environment.',
            'image_path': 'images/person3.jpg'
        },
        {
            'name': 'Giovanni Serusi',
            'description': 'Professional with a solid scientific background, specializing in clinical and cognitive neuroscience and with economic training from SDA Bocconi. Specializing in competitive intelligence and scouting new investment opportunities with a focus on the life-science sector. Excels in building and maintaining strong relationships with internal and external stakeholders, contributing to the development of a robust and collaborative network.',
            'image_path': 'images/Giovanni Serusi_01.jpg'
        }
    ]

    for profile in profiles:
        col1, col2 = st.columns([1, 3])
        with col1:
            if os.path.exists(profile['image_path']):
                img = Image.open(profile['image_path'])
                st.image(img, use_container_width=True)
        with col2:
            st.markdown(f"### {profile['name']}")
            st.markdown(f"<p class='description'>{profile['description']}</p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Titolo in alto nella sidebar
    st.sidebar.title("       ")
    st.sidebar.markdown("---")
    st.sidebar.markdown("###")

# --- Sidebar: Logo + Nome + Link in basso ---
# HTML e CSS per posizionare in basso
# Funzione per convertire l'immagine in base64
def get_base64_of_bin_file2(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Path del logo (assicurati che il file esista)
logo_path = os.path.join("images", "logo4.png")
logo_html = ""
if os.path.exists(logo_path):
    logo_base64 = get_base64_of_bin_file2(logo_path)
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="logo">'
    
st.sidebar.markdown(
    f"""
    <style>
        /* Elimina bordi e ombre nei contenitori della sidebar */
        section[data-testid="stSidebar"] div {{
            border: none !important;
            box-shadow: none !important;
        }}

        /* Specificamente rimuove eventuali linee sopra il footer */
        .sidebar-footer {{
            border-top: none !important;
            box-shadow: none !important;
            margin-top: 0px !important;
            padding-top: 0px !important;
        }}

        .sidebar-footer div {{
            border: none !important;
            box-shadow: none !important;
        }}

        .sidebar-footer a {{
            border: none !important;
            box-shadow: none !important;
            text-decoration: none;
            font-size: 12px;
            display: block;
            margin-top: 12px;
        }}

        .sidebar-footer img {{
            height: 70px;
            margin-right: 8px;
            vertical-align: middle;
        }}

        .sidebar-footer span {{
            font-size: 13px;
            vertical-align: middle;
        }}

    </style>

    <div class="sidebar-footer">
        <div>
            <img src="data:image/png;base64,{logo_base64}">
            <span>Your Name</span>
        </div>
        <a href="https://github.com/tuo-username" target="_blank">🌐 LinkedIn</a>
    </div>
    """,
    unsafe_allow_html=True
)

# Esegui la funzione run per ogni pagina
if __name__ == "__main__":
    run()
