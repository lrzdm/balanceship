import os
import json
import requests
import pandas as pd
from sqlalchemy import create_engine, Column, String, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# Scarica il database se non presente
def download_database_if_missing():
    db_path = "data/financials_db.db"
    if not os.path.exists(db_path):
        print("Scaricamento del database da GitHub...")
        url = "https://github.com/lrzdm/balanceship/releases/download/1.2/financials_db.db"
        response = requests.get(url)
        os.makedirs("data", exist_ok=True)
        with open(db_path, "wb") as f:
            f.write(response.content)
        print("✅ Database scaricato.")

download_database_if_missing()

engine = create_engine('sqlite:///data/financials_db.db')
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

# Tabelle
class FinancialCache(Base):
    __tablename__ = 'cache'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    year = Column(Integer, index=True)
    data_json = Column(Text)

class KPICache(Base):
    __tablename__ = 'kpi_cache'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    description = Column(String, index=True, nullable=True)
    year = Column(Integer, index=True)
    kpi_json = Column(Text)

if os.environ.get("STREAMLIT_CLOUD") != "1":
    Base.metadata.create_all(engine)

# Funzioni di sola lettura
def load_from_db(symbol, years):
    session = Session()
    result_data = []
    try:
        for year in years:
            entry = session.query(FinancialCache).filter_by(symbol=symbol, year=int(year)).first()
            result_data.append(json.loads(entry.data_json) if entry else None)
        return result_data
    finally:
        session.close()

def load_kpis_from_db():
    session = Session()
    try:
        entries = session.query(KPICache).all()
        records = []
        for entry in entries:
            kpi_data = json.loads(entry.kpi_json)
            kpi_data.update({
                'symbol': entry.symbol,
                'year': entry.year,
                'description': entry.description
            })
            records.append(kpi_data)
        return pd.DataFrame(records)
    finally:
        session.close()
