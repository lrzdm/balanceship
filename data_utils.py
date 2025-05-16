from flask import Flask, render_template, request, jsonify
import yfinance as yf
import csv
import os
import pickle
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import datetime

CACHE_DIR = 'cache'

def read_exchanges(filename):
    exchanges = {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 2:
                exchanges[row[0].strip()] = row[1].strip()
    return exchanges

def read_companies(filename):
    companies = []
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            companies.append(row)
    return companies

def format_to_billions(value):
    try:
        value_in_billions = value / 1_000_000_000
        return f"{value_in_billions:,.3f}"
    except Exception:
        return "N/A"
    
def load_from_cache(symbol, years):
    cache_file = os.path.join(CACHE_DIR, f'{symbol}_{"_".join(years)}.pkl')
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    return None

def save_to_cache(symbol, years, data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f'{symbol}_{"_".join(years)}.pkl')
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)
        
def get_financial_data(symbol, years, force_refresh=False, description=None, stock_exchange=None):
    if not force_refresh:
        cached_data = load_from_cache(symbol, years)
        if cached_data is not None:
            return cached_data

    try:
        stock = yf.Ticker(symbol)
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow
        info = stock.info

        if financials.empty and balance_sheet.empty and cashflow.empty:
            print(f"No financial data found for symbol: {symbol}")
            return []
        
        data_list = []
        columns_years = financials.columns.year
        year_indices = [i for i, y in enumerate(columns_years) if str(y) in years]

        for year_index in year_indices:
            year_column = financials.columns[year_index]
            year = str(columns_years[year_index])

            #current_assets = balance_sheet.loc['Current Assets', year_column] if 'Current Assets' in balance_sheet.index else 0
            #current_liabilities = balance_sheet.loc['Current Liabilities', year_column] if 'Current Liabilities' in balance_sheet.index else 0
   

            data = {
                'symbol': symbol,
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'description': description,
                'stock_exchange': stock_exchange,
                'year': year,
                'total_revenue': format_to_billions(financials.loc['Total Revenue', year_column] if 'Total Revenue' in financials.index else 0),
                'operating_revenue': format_to_billions(financials.loc['Operating Revenue', year_column] if 'Operating Revenue' in financials.index else 0),
                'cost_of_revenue': format_to_billions(financials.loc['Cost Of Revenue', year_column] if 'Cost Of Revenue' in financials.index else 0),
                'gross_profit': format_to_billions(financials.loc['Gross Profit', year_column] if 'Gross Profit' in financials.index else 0),
                'operating_expense': format_to_billions(financials.loc['Operating Expense', year_column] if 'Operating Expense' in financials.index else 0),
                'sg_and_a': format_to_billions(financials.loc['Selling General And Administration', year_column] if 'Selling General And Administration' in financials.index else 0),
                'r_and_d': format_to_billions(financials.loc['Research And Development', year_column] if 'Research And Development' in financials.index else 0),
                'operating_income': format_to_billions(financials.loc['Operating Income', year_column] if 'Operating Income' in financials.index else 0),
                'net_non_operating_interest_income_expense': format_to_billions(financials.loc['Net Non Operating Interest Income Expense', year_column] if 'Net Non Operating Interest Income Expense' in financials.index else 0),
                'interest_expense_non_operating': format_to_billions(financials.loc['Interest Expense Non Operating', year_column] if 'Interest Expense Non Operating' in financials.index else 0),
                'pretax_income': format_to_billions(financials.loc['Pretax Income', year_column] if 'Pretax Income' in financials.index else 0),
                'tax_provision': format_to_billions(financials.loc['Tax Provision', year_column] if 'Tax Provision' in financials.index else 0),
                'net_income_common_stockholders': format_to_billions(financials.loc['Net Income Common Stockholders', year_column] if 'Net Income Common Stockholders' in financials.index else 0),
                'net_income': format_to_billions(financials.loc['Net Income', year_column] if 'Net Income' in financials.index else 0),
                'net_income_continuous_operations': format_to_billions(financials.loc['Net Income Continuous Operations', year_column] if 'Net Income Continuous Operations' in financials.index else 0),
                'basic_eps': financials.loc['Basic EPS', year_column] if 'Basic EPS' in financials.index else 0,
                'diluted_eps': financials.loc['Diluted EPS', year_column] if 'Diluted EPS' in financials.index else 0,
                'basic_average_shares': format_to_billions(financials.loc['Basic Average Shares', year_column] if 'Basic Average Shares' in financials.index else 0),
                'diluted_average_shares': format_to_billions(financials.loc['Diluted Average Shares', year_column] if 'Diluted Average Shares' in financials.index else 0),
                'total_expenses': format_to_billions(financials.loc['Total Expenses', year_column] if 'Total Expenses' in financials.index else 0),
                'normalized_income': format_to_billions(financials.loc['Normalized Income', year_column] if 'Normalized Income' in financials.index else 0),
                'interest_expense': format_to_billions(financials.loc['Interest Expense', year_column] if 'Interest Expense' in financials.index else 0),
                'net_interest_income': format_to_billions(financials.loc['Net Interest Income', year_column] if 'Net Interest Income' in financials.index else 0),
                'ebit': format_to_billions(financials.loc['EBIT', year_column] if 'EBIT' in financials.index else 0),
                'ebitda': format_to_billions(financials.loc['EBITDA', year_column] if 'EBITDA' in financials.index else 0),
                'reconciled_depreciation': format_to_billions(financials.loc['Reconciled Depreciation', year_column] if 'Reconciled Depreciation' in financials.index else 0),
                'normalized_ebitda': format_to_billions(financials.loc['Normalized EBITDA', year_column] if 'Normalized EBITDA' in financials.index else 0),
                'total_assets': format_to_billions(balance_sheet.loc['Total Assets', year_column] if 'Total Assets' in balance_sheet.index else 0),
                'stockholders_equity': format_to_billions(balance_sheet.loc["Stockholders Equity", year_column] if "Stockholders Equity" in balance_sheet.index else 0),
                'changes_in_cash': format_to_billions(cashflow.loc['Changes In Cash', year_column] if 'Changes In Cash' in cashflow.index else 0),
                'working_capital': format_to_billions(balance_sheet.loc["Working Capital", year_column] if "Working Capital" in balance_sheet.index else 0),
                'invested_capital': format_to_billions(balance_sheet.loc["Invested Capital", year_column] if "Invested Capital" in balance_sheet.index else 0),
                'total_debt': format_to_billions(balance_sheet.loc["Total Debt", year_column] if "Total Debt" in balance_sheet.index else 0)
            }

            data_list.append(data)

        save_to_cache(symbol, years, data_list)
        return data_list
    except Exception as e:
        print(f"Error retrieving financial data for {symbol}: {e}")
        return []

def remove_duplicates(data):
    seen = set()
    unique_data = []
    for item in data:
        item_tuple = tuple(item.items())
        if item_tuple not in seen:
            seen.add(item_tuple)
            unique_data.append(item)
    return unique_data

def get_all_financial_data(force_refresh=False):
    #print(f"[{datetime.datetime.now()}] >>> get_all_financial_data() chiamata dallo scheduler...")
    exchanges = read_exchanges('exchanges.txt')
    financial_data = []

    for exchange in exchanges.values():
        companies = read_companies(exchange)
        for company in companies:
            symbol = company['ticker']
            description = company['description']
            stock_exchange = exchange
            # Passiamo 'description' come parametro a get_financial_data
            data_list = get_financial_data(symbol, ['2021', '2022', '2023'], description=description, stock_exchange=stock_exchange)
            for data in data_list:
                data['description'] = description
                data['stock_exchange'] = stock_exchange
                financial_data.append(data)
                
    financial_data = remove_duplicates(financial_data)
    financial_data.sort(key=lambda x: (x['symbol'], x['year']))

    return financial_data


