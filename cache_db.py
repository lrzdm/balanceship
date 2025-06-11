import os
import json
from sqlalchemy import create_engine, Column, String, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Path e modalità di connessione
DATABASE_URL = "sqlite:///data/financial_cache.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

class FinancialCache(Base):
    __tablename__ = 'cache'
    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    years = Column(String)  # es: "2021_2022_2023"
    data_json = Column(Text)

# CREA LE TABELLE SOLO IN LOCALE
if os.environ.get("STREAMLIT_CLOUD") != "1":
    Base.metadata.create_all(engine)

def save_to_db(symbol, years, data):
    if os.environ.get("STREAMLIT_CLOUD") == "1":
        return  # Disabilita salvataggio su cloud per evitare errori
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
    try:
        entry = session.query(FinancialCache).filter_by(symbol=symbol, years=key).first()
        if entry:
            return json.loads(entry.data_json)
    except Exception as e:
        import streamlit as st
        st.error("Errore nella lettura del database. Potrebbe essere corrotto.")
        st.exception(e)
    finally:
        session.close()
    return None
