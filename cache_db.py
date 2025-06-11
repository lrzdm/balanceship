import os
import json
import requests
from sqlalchemy import create_engine, Column, String, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def download_database_if_missing():
    db_path = "data/financial_cache.db"
    if not os.path.exists(db_path):
        print("Scaricamento del database da GitHub...")
        url = "https://github.com/lrzdm/balanceship/releases/download/1.1/financial_cache.db"
        response = requests.get(url)
        with open(db_path, "wb") as f:
            f.write(response.content)
        print("✅ Database scaricato.")

# Scarica il database se non presente
download_database_if_missing()

# Crea la cartella se non esiste
os.makedirs("data", exist_ok=True)
engine = create_engine('sqlite:///data/financial_cache.db')

Base = declarative_base()
Session = sessionmaker(bind=engine)

class FinancialCache(Base):
    __tablename__ = 'cache'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    years = Column(String)  # es: "2021_2022_2023"
    data_json = Column(Text)

Base.metadata.create_all(engine)

def save_to_db(symbol, years, data):
    session = Session()
    key = "_".join(years)
    entry = session.query(FinancialCache).filter_by(symbol=symbol, years=key).first()
    if entry:
        entry.data_json = json.dumps(data)
    else:
        entry = FinancialCache(symbol=symbol, years=key, data_json=json.dumps(data))
        session.add(entry)
    session.commit()
    session.close()

def load_from_db(symbol, years):
    session = Session()
    key = "_".join(years)
    entry = session.query(FinancialCache).filter_by(symbol=symbol, years=key).first()
    session.close()
    if entry:
        return json.loads(entry.data_json)
    return None
