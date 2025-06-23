import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_utils import read_exchanges, read_companies, get_financial_data, remove_duplicates, compute_kpis
from data_utils import get_or_fetch_data 
import os
import base64

st.set_page_config(page_title="KPI Dashboard", layout="wide")
st.title("📊 KPI Dashboard")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- SIDEBAR ---
logo_path = os.path.join("images", "logo4.png")
logo_base64 = get_base64_of_bin_file(logo_path) if os.path.exists(logo_path) else ""

# Percorsi delle icone
instagram_icon_path = os.path.join("images", "IG.png")
linkedin_icon_path = os.path.join("images", "LIN.png")

# Converti le immagini in base64
instagram_icon_base64 = get_base64_of_bin_file(instagram_icon_path)
linkedin_icon_base64 = get_base64_of_bin_file(linkedin_icon_path)

st.sidebar.markdown(f"""
    <div style='text-align: center;'>
        <img src="data:image/png;base64,{logo_base64}" style="height: 70px; display: inline-block; margin-top: 20px;"><br>
        <span style='font-size: 14px;'>Navigate financial sea with clarity ⚓</span><br>
        <a href='https://www.instagram.com/tuo_profilo' target='_blank' style="display: inline-block; margin-top: 20px;">
            <img src='data:image/png;base64,{instagram_icon_base64}' width='40' height='40'>
        <a href='https://www.linkedin.com/in/tuo_profilo' target='_blank' style="display: inline-block; margin-top: 20px;">
            <img src='data:image/png;base64,{linkedin_icon_base64}' width='40' height='40'>
    </div>

""", unsafe_allow_html=True)

color_palette = [
    "#6495ED",  # Cornflower Blue
    "#3CB371",  # Medium Sea Green
    "#FF6347",  # Tomato
    "#DAA520",  # Goldenrod
    "#4169E1",  # Royal Blue
    "#BA55D3",  # Medium Orchid
    "#FF8C00",  # Dark Orange
    "#40E0D0",  # Turquoise
    "#708090",  # Slate Gray
    "#B22222"   # Firebrick
]


# Lettura borse e aziende
exchanges = read_exchanges("exchanges.txt")
exchange_names = list(exchanges.keys())
years_available = ['2021', '2022', '2023']
sectors_available = ['Communication Services', 'Consumer Cyclical', 'Consumer Defensive', 'Energy', 'Finance Services', 'Healthcare', 'Industrials', 'Real Estate', 'Technology', 'Utilities']

# --- Layout filtri in riga ---
col1, col2, col3, col4 = st.columns([1.2, 1.5, 2.2, 2])
with col1:
    selected_year = st.selectbox("Year", years_available, index=2)
with col2:
    selected_exchange = st.selectbox("Exchange", exchange_names, index=0)
with col3:
    companies = read_companies(exchanges[selected_exchange])
    symbol_to_name = {c["ticker"]: c["description"] for c in companies}
    name_to_symbol = {v: k for k, v in symbol_to_name.items()}
    company_names = list(symbol_to_name.values())
    selected_company_names = st.multiselect("Companies (up to 10)", options=company_names, max_selections=10)
    selected_symbols = [name_to_symbol[name] for name in selected_company_names]
with col4:
    selected_sector = st.selectbox("Sector", options=["All"] + sectors_available)

# --- Caricamento dati aziende selezionate ---
financial_data = []
for symbol in selected_symbols:
    desc = symbol_to_name.get(symbol, "")
    data = get_or_fetch_data(symbol, [selected_year], desc, selected_exchange)
    financial_data.extend(data)

# --- Se settore selezionato, carico anche tutti i dati del settore ---
sector_data = []
if selected_sector != "All":
    for company in read_companies(exchanges[selected_exchange]):
        if company["ticker"] not in selected_symbols:
            desc = company.get("description", "")
            data = get_or_fetch_data(company["ticker"], [selected_year], desc, selected_exchange)
            sector_data.extend(d for d in data if d.get("sector") == selected_sector)


# --- Se non c'è nulla, stop ---
if not financial_data:
    st.warning("No data available for the selected companies.")
    st.stop()

# --- Unisco dati selezionati e settore (per calcolo media) ---
combined_data = financial_data + sector_data

# --- Calcolo KPI ---
df_kpi_all = compute_kpis(combined_data)
df_kpi_all = df_kpi_all[df_kpi_all["year"] == int(selected_year)]

# --- EPS e settore dal raw data ---
df_raw = pd.DataFrame(combined_data)
if "ticker" in df_raw.columns and "symbol" not in df_raw.columns:
    df_raw.rename(columns={"ticker": "symbol"}, inplace=True)
df_kpi_all = pd.merge(df_kpi_all, df_raw[["symbol", "basic_eps", "sector"]], on="symbol", how="left")


# Rinomina chiara
df_kpi_all.rename(columns={
    "EBITDA Margin": "EBITDA Margin",
    "Debt/Equity": "Debt to Equity",
    "FCF Margin": "FCF Margin",
    "basic_eps": "EPS"
}, inplace=True)

# Aggiungi descrizione azienda
df_kpi_all["company_name"] = df_kpi_all["symbol"].map(symbol_to_name)

# Split: dati visibili vs per media di settore
df_visible = df_kpi_all[df_kpi_all["symbol"].isin(selected_symbols)]

def legend_chart():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="lines",
        line=dict(color="red", dash="dash"),
        name="Companies Avg"
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="lines",
        line=dict(color="blue", dash="dot"),
        name="Sector Avg"
    ))
    fig.update_layout(
        height=50,
        margin=dict(t=0, b=0, l=0, r=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="center",
            x=0.5
        )
    )
    return fig

# Mostro legenda sotto filtri, sopra grafici
st.plotly_chart(legend_chart(), use_container_width=True)


# Funzione grafico (GO con legenda e formattazione)
def kpi_chart(df_visible, df_full, metric, title):
    import plotly.graph_objects as go

    fig = go.Figure()

    company_names = df_visible["company_name"].tolist()
    company_colors = {name: color_palette[i % len(color_palette)] for i, name in enumerate(company_names)}

    # BAR per le aziende selezionate
    fig.add_trace(go.Bar(
        x=company_names,
        y=df_visible[metric].round(3),
        marker_color=[company_colors[name] for name in company_names],
        text=df_visible[metric].round(3),
        textposition="auto",
        showlegend=False
    ))

    # Calcola medie
    global_avg = df_visible[metric].mean()
    sector_avg = None
    if selected_sector != "All":
        sector_df = df_full[df_full["sector"] == selected_sector]
        if not sector_df.empty:
            sector_avg = sector_df[metric].mean()

    # --- LINEA: Market Avg ---
    if not pd.isna(global_avg):
        global_avg = round(global_avg, 3)
        fig.add_shape(
            type="line",
            xref="paper", yref="y",
            x0=0, x1=1, y0=global_avg, y1=global_avg,
            line=dict(color="red", dash="dash")
        )
        # Dummy trace per legenda + label
        fig.add_trace(go.Scatter(
            x=[company_names[-1]],
            y=[global_avg],
            mode="text",
            text=[f"{global_avg}"],
            textposition="top right",
            textfont=dict(color="red"),
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            line=dict(color="red", dash="dash"),
            showlegend=False,
            name="Companies Avg"
        ))

    # --- LINEA: Sector Avg ---
    if sector_avg is not None and not pd.isna(sector_avg):
        sector_avg = round(sector_avg, 3)
        fig.add_shape(
            type="line",
            xref="paper", yref="y",
            x0=0, x1=1, y0=sector_avg, y1=sector_avg,
            line=dict(color="blue", dash="dot")
        )
        fig.add_trace(go.Scatter(
            x=[company_names[-1]],
            y=[sector_avg],
            mode="text",
            text=[f"{sector_avg}"],
            textposition="bottom right",
            textfont=dict(color="blue"),
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode="lines",
            line=dict(color="blue", dash="dot"),
            showlegend=False,
            name="Sector Avg"
        ))

    # Layout generale
    fig.update_layout(
        title=title,
        yaxis_title=metric,
        barmode="group",
        height=280,
        margin=dict(t=28, b=28, l=20, r=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )

    return fig


# I grafici ora senza legenda interna (già fatto nel kpi_chart)
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(kpi_chart(df_visible, df_kpi_all, "EBITDA Margin", "EBITDA Margin"), use_container_width=True)
with col2:
    st.plotly_chart(kpi_chart(df_visible, df_kpi_all, "Debt to Equity", "Debt/Equity"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(kpi_chart(df_visible, df_kpi_all, "FCF Margin", "Free Cash Flow Margin"), use_container_width=True)
with col4:
    st.plotly_chart(kpi_chart(df_visible, df_kpi_all, "EPS", "Earnings Per Share (EPS)"), use_container_width=True)
