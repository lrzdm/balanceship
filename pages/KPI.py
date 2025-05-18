import streamlit as st
import os
from PIL import Image
import base64
from data_utils import compute_kpis, get_financial_data, get_all_financial_data
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="KPI", layout="wide")

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
    def run_kpis():
        st.title("📊 Financial KPI Table")

        @st.cache_data(show_spinner=False)
        def load_financials_from_cache():
            return get_all_financial_data()

        financial_data = load_financials_from_cache()
        df_fin = pd.DataFrame(financial_data)

        # Calcolo KPI
        df_kpis = compute_kpis(financial_data)

        # Aggiungi description se manca
        if 'description' not in df_kpis.columns:
            df_kpis = df_kpis.merge(df_fin[['symbol', 'description']].drop_duplicates(), on='symbol', how='left')

        # Filtri
        descriptions_dict = df_kpis.drop_duplicates(subset='symbol').set_index('description')['symbol'].to_dict()
        descriptions_available = sorted(descriptions_dict.keys())

        col1, col2 = st.columns(2)
        with col1:
            selected_descriptions = st.multiselect(
                "Select Companies",
                descriptions_available,
                default=[descriptions_available[0]] if descriptions_available else []
            )
        with col2:
            years_available = sorted(df_kpis['year'].astype(str).unique())
            selected_years = st.multiselect("Select Years", years_available, default=years_available)

        selected_symbols = [descriptions_dict[desc] for desc in selected_descriptions]

        if selected_symbols and selected_years:
            df_filtered = df_kpis[
                (df_kpis['symbol'].isin(selected_symbols)) &
                (df_kpis['year'].astype(str).isin(selected_years))
            ]

            # Mettiamo i KPI come colonna per pivot: assumo che compute_kpis crei colonne KPI, quindi faccio melt
            # Se invece i KPI sono colonne, melt per farle righe:
            id_vars = ['symbol', 'description', 'year']
            value_vars = [col for col in df_filtered.columns if col not in id_vars]

            df_melt = df_filtered.melt(id_vars=id_vars, value_vars=value_vars, var_name='KPI', value_name='Value')

            # Ora pivot: index=KPI, columns=description + year combinati
            df_melt['desc_year'] = df_melt['description'] + ' ' + df_melt['year'].astype(str)

            df_pivot = df_melt.pivot(index='KPI', columns='desc_year', values='Value')
            
            st.subheader("📋 KPIs List")
            #st.dataframe(df_pivot.style.format("{:.2%}"))
            st.dataframe(df_pivot.style.format("{:.2%}"), height=600)

            # Grafici
            st.subheader("📈 KPI Charts")
            for kpi in df_pivot.index:
                st.markdown(f"### {kpi}")
                kpi_data = df_pivot.loc[kpi].reset_index()
                kpi_data.columns = ['Company-Year', 'Value']
                fig = px.line(
                    kpi_data,
                    x='Company-Year',
                    y='Value',
                    markers=True,
                    title=f'{kpi} over time',
                    labels={'Company-Year': 'Company-Year', 'Value': kpi},
                )
                fig.update_layout(xaxis_tickangle=-45, height=400)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Please select at least one company and one year to view KPIs.")

    run_kpis()



    
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
