import streamlit as st
import pandas as pd
import plotly.express as px
from data_utils import read_exchanges, read_companies, get_financial_data, remove_duplicates, compute_kpis, get_all_financial_data
from cache_db import save_kpis_to_db, FinancialCache, KPICache
from cache_db import load_kpis_for_symbol_year, load_all_kpis
from cache_db import load_from_db, convert_numpy
import os
import json
import base64
import io
import plotly.express as px
import numpy as np
from sqlalchemy import create_engine, Column, String, Text, Integer
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
from cache_db import Session
from cache_db import create_tables
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Graph.py")


st.set_page_config(page_title="Graphs", layout="wide")

COLUMN_LABELS = {
"symbol": "Ticker",
"sector": "Sector",
"industry": "Industry",
"description": "Company Name",
"stock_exchange": "Exchange",
"year": "Year",
"total_revenue": "Total Revenue",
"operating_revenue": "Operating Revenue",
"cost_of_revenue": "Cost of Revenue",
"gross_profit": "Gross Profit",
"operating_expense": "Operating Expense",
"sg_and_a": "SG&A",
"r_and_d": "R&D",
"operating_income": "Operating Income",
"net_non_operating_interest_income_expense": "Non-Operating Interest Income/Expense",
"interest_expense_non_operating": "Interest Expense (Non-Op)",
"pretax_income": "Pre-tax Income",
"tax_provision": "Tax Provision",
"net_income_common_stockholders": "Net Income to Stockholders",
"net_income": "Net Income",
"net_income_continuous_operations": "Net Income (Cont. Ops)",
"basic_eps": "Basic EPS",
"diluted_eps": "Diluted EPS",
"basic_average_shares": "Avg. Shares (Basic)",
"diluted_average_shares": "Avg. Shares (Diluted)",
"total_expenses": "Total Expenses",
"normalized_income": "Normalized Income",
"interest_expense": "Interest Expense",
"net_interest_income": "Net Interest Income",
"ebit": "EBIT",
"ebitda": "EBITDA",
"reconciled_depreciation": "Reconciled Depreciation",
"normalized_ebitda": "Normalized EBITDA",
"total_assets": "Total Assets",
"stockholders_equity": "Stockholders' Equity",
"changes_in_cash": "Changes in Cash",
"working_capital": "Working Capital",
"invested_capital": "Invested Capital",
"total_debt": "Total Debt"
}

# Funzione per convertire immagini in base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Header con logo
def render_logos():
    logo_html = ""
    for logo_path, css_class in [("images/logo1.png", "logo-large"), ("images/logo2.png", "logo-small")]:
        if os.path.exists(logo_path):
            base64_logo = get_base64_of_bin_file(logo_path)
            logo_html += f'<img src="data:image/png;base64,{base64_logo}" class="logo {css_class}">' 
    st.markdown(f"""
    <style>
        .logo-container {{ display: flex; justify-content: center; gap: 30px; margin: 20px auto; }}
        .logo {{ display: block; }}
        .logo-large {{ height: 100px; }}
        .logo-small {{ height: 60px; }}
    </style>
    <div class='logo-container'>{logo_html}</div>
    """, unsafe_allow_html=True)


# KPI Table e Grafici
@st.cache_data(show_spinner=False)
def load_financials(symbol, year, description=None):
    df_kpis = load_kpis_for_symbol_year(symbol, year, description=description)
    if not df_kpis.empty:
        # Se esistono dati nel DB per questa combinazione, ritorna quelli senza chiamare API
        return df_kpis, None
    else:
        # Altrimenti chiama API, calcola KPI e salva solo nuovi record senza update
        df_financials = get_financial_data(symbol, year)
        df_kpis = compute_kpis(df_financials)
        save_kpis_to_db(df_kpis)
        return df_kpis, df_financials

def load_all_kpis_with_auto_update():
    try:
        existing = {}

        # Prima lettura dei KPI esistenti
        with Session() as session:
            entries = session.query(KPICache).all()

            for e in entries:
                try:
                    if isinstance(e.kpi_json, str):
                        val = json.loads(e.kpi_json)
                    elif isinstance(e.kpi_json, dict):
                        val = e.kpi_json
                    else:
                        val = None
                        logger.warning(f"Formato inatteso in kpi_json per {e.symbol} {e.year}: {type(e.kpi_json)}")
                except Exception as exc:
                    val = None
                    logger.error(f"Errore parsing JSON in kpi_json per {e.symbol} {e.year}: {exc}")

                existing[(e.symbol, e.year, e.description or None)] = val

        # Lettura dei financial cache
        with Session() as session:
            financial_entries = session.query(FinancialCache).all()

        for entry in financial_entries:
            key = (entry.symbol, entry.year, None)
            try:
                if isinstance(entry.data_json, str):
                    data = json.loads(entry.data_json)
                elif isinstance(entry.data_json, dict):
                    data = entry.data_json
                else:
                    raise ValueError(f"Formato sconosciuto in entry.data_json: {type(entry.data_json)}")

                df_financial = pd.DataFrame([data])
                df_kpis = compute_kpis(df_financial)
                df_kpis["description"] = None

                kpi_dict = df_kpis.drop(columns=["symbol", "year", "description"], errors="ignore").iloc[0].to_dict()
                kpi_dict = convert_numpy(kpi_dict)

                existing_val = existing.get(key)
                if not isinstance(existing_val, dict):
                    existing_val = None

                if key not in existing or existing_val != kpi_dict:
                    save_kpis_to_db(df_kpis)

            except Exception as e:
                logger.error(f"Errore nel calcolo/salvataggio KPI per {entry.symbol} {entry.year}: {e}")

        return load_all_kpis()

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Errore FATALE in load_all_kpis_with_auto_update:\n{tb}")
        st.error(f"Errore fatale durante il caricamento KPI: {e}\n{tb}")
        return pd.DataFrame()

def load_all_kpis_read_only():
    try:
        with Session() as session:
            entries = session.query(KPICache).all()
            kpi_data = []
            for e in entries:
                try:
                    if isinstance(e.kpi_json, str):
                        val = json.loads(e.kpi_json)
                    elif isinstance(e.kpi_json, dict):
                        val = e.kpi_json
                    else:
                        logger.warning(f"Formato inatteso in kpi_json per {e.symbol} {e.year}: {type(e.kpi_json)}")
                        continue

                    val['symbol'] = e.symbol
                    val['year'] = e.year
                    val['description'] = e.description
                    kpi_data.append(val)

                except Exception as exc:
                    logger.error(f"Errore parsing JSON per {e.symbol} {e.year}: {exc}")

        df_kpis = pd.DataFrame(kpi_data)
        return df_kpis

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Errore nel caricamento dei KPI dal database:\n{tb}")
        st.error(f"Errore durante il caricamento KPI: {e}")
        return pd.DataFrame()

USE_READ_ONLY = True

if USE_READ_ONLY:
    df_all_kpis = load_all_kpis_read_only()
else:
    df_all_kpis = load_all_kpis_with_auto_update()


# 2. Leggi exchanges (una sola volta)
exchanges = read_exchanges("exchanges.txt")

def render_kpis(df_all_kpis, exchanges_dict):
    st.header("📊 KPI Dashboard")

    # 1. Caricamento KPI e aggiornamento automatico se mancanti
    with st.spinner("Caricamento KPI in corso..."):
        if USE_READ_ONLY:
            df_all_kpis = load_all_kpis_read_only()
        else:
            df_all_kpis = load_all_kpis_with_auto_update()

    if df_all_kpis.empty:
        st.warning("Nessun KPI disponibile. Carica prima i dati finanziari.")
        return

    # 2. Aggiungi filtro Exchange: lista exchange da dizionario esterno (passato a questa funzione)
    exchange_names = list(exchanges_dict.keys())
    selected_exchange = st.selectbox("Seleziona Exchange", ["All"] + exchange_names, index=0)

    # 3. Filtra df_all_kpis per exchange (se non "All")
    if selected_exchange != "All":
        # Ottieni simboli appartenenti all'exchange selezionato
        companies_exchange = read_companies(exchanges_dict[selected_exchange])
        symbols_for_exchange = {c["ticker"] for c in companies_exchange}
        df_all_kpis = df_all_kpis[df_all_kpis["symbol"].isin(symbols_for_exchange)]

    if df_all_kpis.empty:
        st.warning(f"Nessun KPI disponibile per l'exchange selezionato: {selected_exchange}")
        st.stop()

    # 4. Preparazione dizionario descrizioni → simboli
    descriptions_dict = df_all_kpis.groupby("description")["symbol"].apply(lambda x: list(sorted(set(x)))).to_dict()
    descriptions_available = sorted(k for k in descriptions_dict if k is not None)
    years_available = sorted(df_all_kpis["year"].astype(str).unique())

    # 5. Default filters
    default_desc = ['Apple Inc.'] if 'Apple Inc.' in descriptions_available else (descriptions_available[:1] if descriptions_available else [])
    default_years = ['2023'] if "2023" in years_available else ([years_available[-1]] if years_available else [])

    # 6. Gestione session state
    if 'selected_desc' in st.session_state:
        st.session_state['selected_desc'] = [x for x in st.session_state['selected_desc'] if x in descriptions_available]
    else:
        st.session_state['selected_desc'] = default_desc

    if 'selected_years' in st.session_state:
        st.session_state['selected_years'] = [y for y in st.session_state['selected_years'] if y in years_available]
    else:
        st.session_state['selected_years'] = default_years

    # 7. Filtri UI
    col1, col2 = st.columns(2)
    selected_desc = col1.multiselect(
        "Seleziona aziende",
        descriptions_available,
        default=st.session_state['selected_desc'],
        key="desc_filter"
    )
    selected_years = col2.multiselect(
        "Seleziona anni",
        years_available,
        default=st.session_state['selected_years'],
        key="year_filter"
    )

    # 8. Limiti e controlli
    if len(selected_desc) > 3:
        st.warning("Puoi selezionare al massimo 3 aziende.")
        st.stop()
    if len(selected_years) > 3:
        st.warning("Puoi selezionare al massimo 3 anni.")
        st.stop()

    st.session_state['selected_desc'] = selected_desc
    st.session_state['selected_years'] = selected_years

    if not selected_desc or not selected_years:
        st.warning("Seleziona almeno un'azienda e un anno.")
        st.stop()

    # 9. Estrazione simboli selezionati
    selected_symbols = []
    for d in selected_desc:
        selected_symbols.extend(descriptions_dict.get(d, []))

    if not selected_symbols:
        st.warning("Nessun simbolo trovato per le aziende selezionate.")
        st.stop()

    # 10. Filtro finale sui dati
    df_filtered = df_all_kpis[
        (df_all_kpis['symbol'].isin(selected_symbols)) &
        (df_all_kpis['year'].astype(str).isin(selected_years)) &
        (df_all_kpis['description'].isin(selected_desc))
    ]

    if df_filtered.empty:
        st.warning("Nessun dato trovato per i filtri selezionati.")
        st.stop()

    # 9. Preparazione tabella pivot
    id_vars = ['symbol', 'description', 'year']
    value_vars = [col for col in df_filtered.columns if col not in id_vars and df_filtered[col].dtype != 'object']
    df_melt = df_filtered.melt(id_vars=id_vars, value_vars=value_vars, var_name='KPI', value_name='Value')
    df_melt['desc_year'] = df_melt['description'] + ' ' + df_melt['year'].astype(str)
    df_pivot = df_melt.pivot(index='KPI', columns='desc_year', values='Value')

    df_pivot = df_pivot.apply(pd.to_numeric, errors='coerce')
    df_clean = df_pivot.fillna(np.nan)

    # 10. Visualizzazione
    st.subheader("📋 Elenco KPI")
    num_cols = df_clean.select_dtypes(include=['number']).columns
    styled = df_clean.style.format({col: "{:.2%}" for col in num_cols})
    st.dataframe(styled, height=600)

    # Layout bottoni Reset e Download
    col_reset, col_download = st.columns([1, 1])
    with col_reset:
        if st.button("Reset Filters"):
            st.session_state['selected_desc'] = default_desc
            st.session_state['selected_years'] = default_years
            st.experimental_rerun()

    with col_download:
        buffer = io.BytesIO()
        df_filtered_clean = df_filtered.copy().replace({np.nan: ""})
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_filtered_clean.to_excel(writer, index=False, sheet_name='KPI')
        st.download_button(
            label="Scarica Excel",
            data=buffer.getvalue(),
            file_name="kpi_filtered.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )




    # 🔵 Bubble Chart
    st.subheader("🔵 Bubble Chart")
    bubble_cols = [col for col in df_filtered.columns if col not in ['symbol', 'description', 'year', 'exchange']]
    if len(bubble_cols) >= 3:
        col1, col2, col3 = st.columns(3)
        with col1:
            x_axis = st.selectbox("X Axis", bubble_cols)
        with col2:
            y_axis = st.selectbox("Y Axis", bubble_cols, index=1)
        with col3:
            size_axis = st.selectbox("Bubble Size", bubble_cols, index=2)

        df_plot = df_filtered.dropna(subset=[x_axis, y_axis, size_axis]).copy()

        # Assicurati che i valori size siano >= 0 (o > 0)
        df_plot[size_axis] = df_plot[size_axis].clip(lower=0)

        # opzionale: se vuoi evitare bolle di dimensione zero (invisibili), puoi fare così:
        min_size = 0.1
        df_plot[size_axis] = df_plot[size_axis].apply(lambda x: max(x, min_size))

        df_plot['label'] = df_plot['description'] + ' ' + df_plot['year'].astype(str)

        fig = px.scatter(
            df_plot,
            x=x_axis,
            y=y_axis,
            size=size_axis,
            color='description',
            hover_name='label',
            title="KPI Bubble Chart"
        )
        st.plotly_chart(fig, use_container_width=True)



        ## Uncomment for charts
        # st.subheader("KPI Charts")
        # for kpi in df_pivot.index:
        #     st.markdown(f"### {kpi}")
        #     chart_data = df_pivot.loc[kpi].reset_index()
        #     chart_data.columns = ['Company-Year', 'Value']
        #     fig = px.line(chart_data, x='Company-Year', y='Value', markers=True, title=f'{kpi} over time')
        #     fig.update_layout(xaxis_tickangle=-45, height=400)
        #     st.plotly_chart(fig, use_container_width=True)


# Grafici Generali
@st.cache_data(show_spinner=False)
def load_data_for_selection(selected_symbols, selected_years):
    from data_utils import load_from_db
    data = []

    for symbol in selected_symbols:
        records = load_from_db(symbol, selected_years)
        for r in records:
            if isinstance(r, dict) and r:
                r['symbol'] = symbol
                data.append(r)
            else:
                print(f"⚠️ Record vuoto o non valido per {symbol}")
    return data



def render_general_graphs():
    st.header("📈 Interactive Graphs")

    # --- Selettori aziende (una volta sola) ---
    exchanges = read_exchanges("exchanges.txt")
    companies_all = []
    for path in exchanges.values():
        companies_all += read_companies(path)

    descriptions_dict = {c['description']: c['ticker'] for c in companies_all if 'description' in c and 'ticker' in c}
    descriptions_available = sorted(descriptions_dict.keys())
    default_desc = ['Apple Inc.'] if 'Apple Inc.' in descriptions_available else descriptions_available[:1]

    selected_desc = st.multiselect("Select Companies", descriptions_available, default=default_desc)
    if not selected_desc:
        st.warning("Please select at least one company.")
        return

    selected_symbols = [descriptions_dict[d] for d in selected_desc]
    selected_years = ['2021', '2022', '2023']
    df = pd.DataFrame(load_data_for_selection(selected_symbols, selected_years))

    if df.empty:
        st.warning("No data found for the selected companies.")
        return

    # 🔧 Fix tipi
    df['year'] = df['year'].astype(str)

    columns_to_plot = [
        "total_revenue", "net_income", "ebitda", "gross_profit",
        "stockholders_equity", "total_assets", "basic_eps", "diluted_eps"
    ]


     # --- GRAFICO 1 ---
    st.subheader("📉 Graph 1: Metric over Time per Company")
    col1, _ = st.columns(2)
    with col1:
        metric = st.selectbox("Select Metric", options=columns_to_plot,
                              format_func=lambda x: COLUMN_LABELS.get(x, x), index=0, key="metric1")

    df1 = df[df['description'].isin(selected_desc)].copy()
    df1[metric] = pd.to_numeric(df1[metric], errors='coerce')
    df1['year'] = df1['year'].astype(str)
    fig1 = px.line(df1, x='year', y=metric, color='description', markers=True,
                   labels={"year": "Year", metric: COLUMN_LABELS.get(metric, metric), "description": "Company"},
                   title=COLUMN_LABELS.get(metric, metric) + " Over Time")
    fig1.update_layout(xaxis=dict(tickmode="array", tickvals=sorted(df1['year'].unique())))
    st.plotly_chart(fig1, use_container_width=True)


    # --- GRAFICO 2 ---
    st.subheader("📐 Graph 2: Custom Ratio Over Time")
    col2, col3 = st.columns(2)

    # Metti Apple come default nella selectbox, se è presente in columns_to_plot
    default_numerator = "ebitda"  # o la chiave esatta corrispondente nel tuo df
    default_denominator = "total_revenue"  # idem
    default_company = "Apple Inc."

    with col2:
        numerator = st.selectbox(
            "Numerator",
            columns_to_plot,
            index=columns_to_plot.index(default_numerator) if default_numerator in columns_to_plot else 0,
            format_func=lambda x: COLUMN_LABELS.get(x, x),
            key="num"
        )
    with col3:
        denominator = st.selectbox(
            "Denominator",
            columns_to_plot,
            index=columns_to_plot.index(default_denominator) if default_denominator in columns_to_plot else 0,
            format_func=lambda x: COLUMN_LABELS.get(x, x),
            key="den"
        )

    # Usa Apple di default come descrizione selezionata
    #selected_desc = [default_company]

    if numerator != denominator:
        df_ratio = df[df['description'].isin(selected_desc)].copy()
        df_ratio[numerator] = pd.to_numeric(df_ratio[numerator], errors='coerce')
        df_ratio[denominator] = pd.to_numeric(df_ratio[denominator], errors='coerce')
        df_ratio['ratio'] = df_ratio[numerator] / df_ratio[denominator]
        df_ratio['year'] = df_ratio['year'].astype(str)

        fig3 = px.line(
            df_ratio,
            x='year',
            y='ratio',
            color='description',
            markers=True,
            labels={"year": "Year", "ratio": "Ratio", "description": "Company"},
            title=f"{COLUMN_LABELS.get(numerator, numerator)} / {COLUMN_LABELS.get(denominator, denominator)} Over Time"
        )
        fig3.update_layout(xaxis=dict(tickmode="array", tickvals=sorted(df_ratio['year'].unique())))
        st.plotly_chart(fig3, use_container_width=True) 

    # --- GRAFICO 3 ---
    st.subheader("📊 Graph 3: Metric Average per Sector")
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_sector = st.selectbox("Metric", options=columns_to_plot,
                                     format_func=lambda x: COLUMN_LABELS.get(x, x), index=0, key="sector")
    with col2:
        exchange_names = list(exchanges.keys())
        selected_exchange = st.selectbox("Stock Exchange", exchange_names)
    with col3:
        selected_year = st.selectbox("Year", selected_years, index=2)

    df_sector = df[(df['stock_exchange'] == selected_exchange) & (df['year'] == str(selected_year))].copy()

    # Pulizia dati
    df_sector["sector"] = df_sector["sector"].replace("null", np.nan)
    df_sector[metric_sector] = pd.to_numeric(df_sector[metric_sector], errors='coerce')

    # Rimozione righe con valori mancanti
    df_sector = df_sector.dropna(subset=["sector", metric_sector])

    # Calcolo media per settore
    sector_avg = df_sector.groupby("sector")[metric_sector].mean().reset_index()


    fig2 = px.bar(sector_avg, x="sector", y=metric_sector,
                  title=f"Average {COLUMN_LABELS.get(metric_sector, metric_sector)} per Sector in {selected_year} ({selected_exchange})",
                  labels={metric_sector: COLUMN_LABELS.get(metric_sector, metric_sector), "sector": "Sector"})
    st.plotly_chart(fig2, use_container_width=True)



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
        <span style='font-size: 14px;'>Navigate financial sea with clarity!</span><br>
        <a href='https://www.instagram.com/tuo_profilo' target='_blank' style="display: inline-block; margin-top: 20px;">
            <img src='data:image/png;base64,{instagram_icon_base64}' width='40' height='40'>
        <a href='https://www.linkedin.com/in/tuo_profilo' target='_blank' style="display: inline-block; margin-top: 20px;">
            <img src='data:image/png;base64,{linkedin_icon_base64}' width='40' height='40'>
    </div>

""", unsafe_allow_html=True)

def run():
    render_logos()
    render_kpis(df_all_kpis, exchanges)
    #render_kpis(df_all_kpis)
    st.markdown("---")
    render_general_graphs()
    #render_sidebar_footer()

if __name__ == "__main__":
    run()
