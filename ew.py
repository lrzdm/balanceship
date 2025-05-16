import streamlit as st
import pandas as pd
from data_utils import read_exchanges, read_companies, get_financial_data, remove_duplicates
import base64
import os
import io
from xlsxwriter import Workbook
from PIL import Image
from pages import Graph, Who_we_are

st.set_page_config(page_title="Financials", layout="wide")


# Mappa delle pagine
PAGES = {
    "Page 1": Graph,
    "Page 2": Who_we_are,
}

# Menu di navigazione nella sidebar
st.sidebar.title("Navigazione")
selection = st.sidebar.radio("Vai a", list(PAGES.keys()))

# Funzione per convertire l'immagine in base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Path del logo (assicurati che il file esista)
logo_path = os.path.join("images", "logo.png")
logo_html = ""
if os.path.exists(logo_path):
    logo_base64 = get_base64_of_bin_file(logo_path)
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="logo">'

st.markdown(f"""
<style>
    .main-container {{
        padding-left: 1cm;
        padding-right: 1cm;
    }}
    .logo {{
        height: 60px;
        margin: 15px auto;
        display: block;
    }}
</style>
<div class='main-container'>
    {logo_html}
""", unsafe_allow_html=True)


st.markdown("<div class='main-container'>", unsafe_allow_html=True)

st.title("📊 Financial Data")

# Selezione anni, borse, settore, industria
exchanges = read_exchanges('exchanges.txt')
exchange_names = list(exchanges.keys())
years_available = ['2021', '2022', '2023']
sectors_available = ['Communication Services', 'Consumer Cyclical', 'Consumer Defensive', 'Energy', 'Finance Services', 'Healthcare', 'Industrials', 'Real Estate', 'Technology', 'Utilities']

financial_data = []
selected_years = ['2023']
selected_exchanges = ['NASDAQ']
selected_sectors = []
selected_industries = []

col1, col2, col3, col4 = st.columns(4)
with col1:
    selected_years = st.multiselect("Select Years", years_available, default=selected_years)
with col2:
    selected_exchanges = st.multiselect("Select Stock Exchanges", exchange_names, default=selected_exchanges)
with col3:
    selected_sectors = st.multiselect("Select Sector", sectors_available)


if st.button("Reset Filters"):
    selected_years = ['2023']
    selected_exchanges = ['NASDAQ']
    selected_sectors = []
    selected_industries = []

currency = "USD"
exchange_currency_mapping = {
    'NASDAQ': 'USD',
    'S&P 500': 'USD',
    'FTSE MIB': 'EUR',
    'FTSE 100': 'GBP',
    'Nikkei 225': 'JPY',
}

if selected_exchanges:
    currency = exchange_currency_mapping.get(selected_exchanges[0], 'local currency')

currency_messages = {
    'USD': 'Numbers reported are in billions of Dollars ($).',
    'EUR': 'Numbers reported are in billions of Euros (€).',
    'GBP': 'Numbers reported are in billions of Pounds (£).',
    'JPY': 'Numbers reported are in billions of Yens (¥).'
}

st.markdown(f"<div class='currency-info'>{currency_messages.get(currency, 'Numbers reported are in billions of the local currency.')}</div>", unsafe_allow_html=True)

for exchange in selected_exchanges:
    companies = read_companies(exchanges[exchange])
    for company in companies:
        symbol = company['ticker']
        description = company['description']
        stock_exchange = exchange
        data_list = get_financial_data(symbol, selected_years)
        for data in data_list:
            data['description'] = description
            data['stock_exchange'] = stock_exchange
            financial_data.append(data)

financial_data = remove_duplicates(financial_data)
if selected_sectors:
    industries_available = list(set(d['industry'] for d in financial_data if 'industry' in d and d['sector'] in selected_sectors))
else:
    industries_available = list(set(d['industry'] for d in financial_data if 'industry' in d))

# Mostra il multiselect per l'industria con le opzioni basate sulle industrie disponibili
with col4:
    selected_industries = st.multiselect("Select Industry", industries_available, default=selected_industries)


if selected_sectors:
    financial_data = [d for d in financial_data if d.get('sector') in selected_sectors]
if selected_industries:
    financial_data = [d for d in financial_data if d.get('industry') in selected_industries]

financial_data.sort(key=lambda x: (x['symbol'], x['year']))


if financial_data:
    df = pd.DataFrame(financial_data)
    column_order = [
    'symbol', 'sector', 'industry', 'description', 'stock_exchange', 'year',
    'total_revenue', 'operating_revenue', 'cost_of_revenue', 'gross_profit',
    'operating_expense', 'sg_and_a', 'r_and_d', 'operating_income',
    'net_non_operating_interest_income_expense', 'interest_expense_non_operating',
    'pretax_income', 'tax_provision', 'net_income_common_stockholders',
    'net_income', 'net_income_continuous_operations', 'basic_eps', 'diluted_eps',
    'basic_average_shares', 'diluted_average_shares', 'total_expenses',
    'normalized_income', 'interest_expense', 'net_interest_income',
    'ebit', 'ebitda', 'reconciled_depreciation', 'normalized_ebitda',
    'total_assets', 'stockholders_equity', 'changes_in_cash',
    'working_capital', 'invested_capital', 'total_debt'
    ]

    df = df[column_order]  # applica l'ordine delle colonne
    st.success(f"{len(df)} records loaded.")
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

    df.rename(columns=COLUMN_LABELS, inplace=True)

    # Crea un buffer per il file Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Financials')
    excel_data = output.getvalue()

    st.download_button(
        label="Download Excel",
        data=excel_data,
        file_name="financial_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.dataframe(df, use_container_width=True)

else:
    st.warning("No financial data available for the selected years and exchanges.")


# Titolo in alto nella sidebar
st.sidebar.title("       ")
st.sidebar.markdown("---")
st.sidebar.markdown("###")

# --- Sidebar: Logo + Nome + Link in basso ---
# HTML e CSS per posizionare in basso
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
            height: 30px;
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

# Carica e esegui la pagina selezionata
page = PAGES[selection]
page.run()

st.markdown("</div>", unsafe_allow_html=True)
