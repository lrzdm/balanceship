import streamlit as st
import pandas as pd
import plotly.express as px
from data_utils import read_exchanges, read_companies, get_financial_data, remove_duplicates
import os
import base64

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

def run():
    st.title("📈 Interactive Graphs")

    exchanges = read_exchanges("exchanges.txt")
    exchange_names = list(exchanges.keys())
    years = ['2021', '2022', '2023']
    columns_to_plot = [
        "total_revenue", "net_income", "ebitda", "gross_profit",
        "stockholders_equity", "total_assets", "basic_eps", "diluted_eps"
    ]

    @st.cache_data(show_spinner=False)
    def load_data():
        data = []
        for exchange in exchanges:
            companies = read_companies(exchanges[exchange])
            for company in companies:
                symbol = company['ticker']
                description = company['description']
                data_list = get_financial_data(symbol, years)
                for entry in data_list:
                    entry['description'] = description
                    entry['stock_exchange'] = exchange
                    data.append(entry)
        return remove_duplicates(data)

    raw_data = load_data()
    df = pd.DataFrame(raw_data)

    st.subheader("📊 Graph 1: Metric over Time per Company")
    col1, col2 = st.columns(2)
    with col1:
        selected_metric = st.selectbox("Select Metric", options=columns_to_plot, format_func=lambda x: COLUMN_LABELS.get(x, x), index=columns_to_plot.index("total_revenue"))
    with col2:
        default_companies = ["Netflix"] if "Netflix" in df['description'].values else []
        selected_companies = st.multiselect("Select Companies", sorted(df['description'].unique().tolist()), default=["Netflix"] if "Netflix" in df['description'].values else [])

    if selected_companies:
        plot_df = df[df['description'].isin(selected_companies)]
        plot_df[selected_metric] = pd.to_numeric(plot_df[selected_metric], errors='coerce')
        plot_df['year'] = plot_df['year'].astype(str)
        fig = px.line(
            plot_df,
            x="year",
            y=selected_metric,
            color="description",
            line_shape="linear",
            markers=True,
            labels={"year": "Year", selected_metric: COLUMN_LABELS.get(selected_metric, selected_metric), "description": "Company"},
            category_orders={"year": ["2021", "2022", "2023"]},
            title=COLUMN_LABELS.get(selected_metric, selected_metric) + " Over Time"
        )
        # Rimuovi i markers esplicitamente
        #fig.update_traces(mode='lines')  # Imposta la dimensione del marker a 0
        fig.update_layout(
            xaxis=dict(
                tickmode="array",
                tickvals=["2021", "2022", "2023"],
                ticktext=["2021", "2022", "2023"]
            )
        )    
        st.plotly_chart(fig, use_container_width=True)
        #st.download_button("Download Graph 1 as PNG", fig.to_image(format="png"), file_name="graph1.png")
    st.markdown("<div style='margin-bottom: 3cm;'></div>", unsafe_allow_html=True)

    st.subheader("📊 Graph 2: Metric Average per Sector")
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_sector = st.selectbox("Metric", options=columns_to_plot, format_func=lambda x: COLUMN_LABELS.get(x, x), index=columns_to_plot.index("total_revenue"), key="sector")
    with col2:
        selected_exchange = st.selectbox("Stock Exchange", exchange_names)
    with col3:
        selected_year = st.selectbox("Year", years, index=years.index("2023"))

    sector_df = df[(df['stock_exchange'] == selected_exchange) & (df['year'] == selected_year)]
    sector_df[metric_sector] = pd.to_numeric(sector_df[metric_sector], errors='coerce')
    sector_mean = sector_df.groupby("sector")[metric_sector].mean().reset_index()

    fig2 = px.bar(
        sector_mean,
        x="sector",
        y=metric_sector,
        title=f"Average {metric_sector.replace('_', ' ').title()} per Sector in {selected_year} ({selected_exchange})",
        labels={metric_sector: metric_sector.replace('_', ' ').title(), "sector": "Sector"}
    )
    st.plotly_chart(fig2, use_container_width=True)
    #st.download_button("Download Graph 2 as PNG", fig2.to_image(format="png"), file_name="graph2.png")
    st.markdown("<div style='margin-bottom: 3cm;'></div>", unsafe_allow_html=True)

    st.subheader("📊 Graph 3: Ratio Over Time")
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_ratio_companies = st.multiselect("Select Companies", sorted(df['description'].unique()), default=["Netflix"] if "Netflix" in df['description'].values else [], key="ratio")
    with col2:
        numerator = st.selectbox("Numerator", options=columns_to_plot, format_func=lambda x: COLUMN_LABELS.get(x, x), index=columns_to_plot.index("total_revenue"), key="num")
    with col3:
        denominator = st.selectbox("Denominator", options=columns_to_plot, format_func=lambda x: COLUMN_LABELS.get(x, x), index=columns_to_plot.index("stockholders_equity") if "stockholders_equity" in columns_to_plot else 1, key="den")

    if selected_ratio_companies and numerator != denominator:
        ratio_df = df[df['description'].isin(selected_ratio_companies)].copy()
        ratio_df[numerator] = pd.to_numeric(ratio_df[numerator], errors='coerce')
        ratio_df[denominator] = pd.to_numeric(ratio_df[denominator], errors='coerce')
        ratio_df['ratio'] = ratio_df[numerator] / ratio_df[denominator]
        ratio_df['year'] = ratio_df['year'].astype(str)
        fig3 = px.line(
            ratio_df,
            x="year",
            y="ratio",
            color="description",
            line_shape="linear",
            markers=True,
            labels={"year": "Year", "ratio": "Ratio", "description": "Company"},
            category_orders={"year": ["2021", "2022", "2023"]},
            title=f"{COLUMN_LABELS.get(numerator, numerator)} / {COLUMN_LABELS.get(denominator, denominator)} Over Time"
        )

    # Rimuovi i markers esplicitamente
        #fig3.update_traces(mode='lines')  # Imposta la dimensione del marker a 0

        fig3.update_layout(
            xaxis=dict(
                tickmode="array",
                tickvals=["2021", "2022", "2023"],
                ticktext=["2021", "2022", "2023"]
            )
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        #st.download_button("Download Graph 3 as PNG", fig3.to_image(format="png"), file_name="graph3.png")
    st.markdown("<div style='margin-bottom: 3cm;'></div>", unsafe_allow_html=True)

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

# Esegui la funzione run
if __name__ == "__main__":
    run()

st.markdown("</div>", unsafe_allow_html=True)

