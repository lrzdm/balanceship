### FILE CORRETTO: graphs_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from data_utils import read_exchanges, read_companies, get_financial_data, compute_kpis
from cache_db import load_kpis_for_symbol_year, save_kpis_to_db, KPICache, Session
import json
import io
import os
import base64
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Graph.py")

st.set_page_config(page_title="Graphs", layout="wide")

# === FUNZIONI MIGLIORATE ===

@st.cache_data(show_spinner=False)
def load_kpis_filtered_by_exchange(symbols_filter=None):
    try:
        with Session() as session:
            query = session.query(KPICache)
            if symbols_filter:
                query = query.filter(KPICache.symbol.in_(symbols_filter))

            entries = query.all()
            kpi_data = []
            for e in entries:
                try:
                    val = json.loads(e.kpi_json) if isinstance(e.kpi_json, str) else e.kpi_json
                    if isinstance(val, dict):
                        val['symbol'] = e.symbol
                        val['year'] = e.year
                        val['description'] = e.description
                        kpi_data.append(val)
                except Exception as exc:
                    logger.warning(f"Errore parsing JSON per {e.symbol} {e.year}: {exc}")
        return pd.DataFrame(kpi_data)
    except Exception as e:
        st.error(f"Errore durante il caricamento KPI: {e}")
        return pd.DataFrame()

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
    return data

# === RENDER KPIs ===
def render_kpis(exchanges_dict):
    st.header("📊 KPI Dashboard")
    exchange_names = list(exchanges_dict.keys())
    selected_exchange = st.selectbox("Seleziona Exchange", ["All"] + exchange_names, index=0)

    if selected_exchange != "All":
        companies_exchange = read_companies(exchanges_dict[selected_exchange])
        symbols_for_exchange = {c["ticker"] for c in companies_exchange if "ticker" in c}
        df_all_kpis = load_kpis_filtered_by_exchange(symbols_for_exchange)
    else:
        df_all_kpis = load_kpis_filtered_by_exchange()

    if df_all_kpis.empty:
        st.warning("Nessun dato disponibile.")
        return

    descriptions_dict = df_all_kpis.groupby("description")["symbol"].apply(list).to_dict()
    descriptions_available = sorted(k for k in descriptions_dict if k is not None)
    years_available = sorted(df_all_kpis["year"].astype(str).unique())

    selected_desc = st.multiselect("Seleziona aziende", descriptions_available, default=descriptions_available[:1])
    selected_years = st.multiselect("Seleziona anni", years_available, default=years_available[-1:])

    if not selected_desc or not selected_years:
        st.warning("Seleziona almeno un'azienda e un anno.")
        return

    selected_symbols = [s for d in selected_desc for s in descriptions_dict.get(d, [])]
    df_filtered = df_all_kpis[
        (df_all_kpis['symbol'].isin(selected_symbols)) &
        (df_all_kpis['year'].astype(str).isin(selected_years)) &
        (df_all_kpis['description'].isin(selected_desc))
    ]

    if df_filtered.empty:
        st.warning("Nessun dato trovato.")
        return

    st.dataframe(df_filtered)

# === GRAFICI ===
def render_general_graphs():
    st.header("📈 Interactive Graphs")
    exchanges = read_exchanges("exchanges.txt")
    companies_all = []
    for path in exchanges.values():
        companies_all += read_companies(path)

    descriptions_dict = {c['description']: c['ticker'] for c in companies_all if 'description' in c and 'ticker' in c}
    descriptions_available = sorted(descriptions_dict.keys())
    selected_desc = st.multiselect("Select Companies", descriptions_available, default=descriptions_available[:1])

    if not selected_desc:
        st.warning("Please select at least one company.")
        return

    selected_symbols = [descriptions_dict[d] for d in selected_desc]
    selected_years = ['2021', '2022', '2023']
    df = pd.DataFrame(load_data_for_selection(selected_symbols, selected_years))

    if df.empty:
        st.warning("No data found.")
        return

    df['year'] = df['year'].astype(str)
    metric_sector = st.selectbox("Metric", ["ebitda", "total_revenue", "net_income"], index=0)
    selected_exchange = st.selectbox("Exchange", list(exchanges.keys()))
    selected_year = st.selectbox("Year", selected_years, index=2)

    # Ricarica dati da tutte le aziende di quell'exchange
    companies_exchange = read_companies(exchanges[selected_exchange])
    symbols_exchange = [c['ticker'] for c in companies_exchange]
    df_sector = pd.DataFrame(load_data_for_selection(symbols_exchange, [selected_year]))
    df_sector['year'] = df_sector['year'].astype(str)
    df_sector['sector'] = df_sector['sector'].replace("null", np.nan)
    df_sector[metric_sector] = pd.to_numeric(df_sector[metric_sector], errors='coerce')
    df_sector = df_sector.dropna(subset=["sector", metric_sector])
    sector_avg = df_sector.groupby("sector")[metric_sector].mean().reset_index()

    fig = px.bar(sector_avg, x="sector", y=metric_sector, title=f"Average {metric_sector} in {selected_year} ({selected_exchange})")
    st.plotly_chart(fig, use_container_width=True)

# === MAIN ===
def run():
    exchanges = read_exchanges("exchanges.txt")
    render_kpis(exchanges)
    st.markdown("---")
    render_general_graphs()

if __name__ == "__main__":
    run()
