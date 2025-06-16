import os
import json
import logging
import pandas as pd
from sqlalchemy import create_engine, Column, String, Text, Integer
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
import streamlit as st
import os

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cache_db")

# Base ORM
Base = declarative_base()

# Scegli il database in base all'ambiente
if os.environ.get("STREAMLIT_CLOUD") == "1":
    DATABASE_URL = os.environ.get("DATABASE_URL")
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    os.makedirs("data", exist_ok=True)
    DATABASE_URL = "sqlite:///data/financials_db.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
print("✅ Database in uso:", DATABASE_URL)
Session = scoped_session(sessionmaker(bind=engine))

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

# Crea le tabelle solo in locale
def create_tables():
    if os.environ.get("STREAMLIT_CLOUD") != "1":
        Base.metadata.create_all(engine)
        logger.info("✅ Tabelle SQLite create o già esistenti.")

def save_to_db(symbol, years, data):
    session = Session()
    try:
        for i, year in enumerate(years):
            year_int = int(year)
            data_for_year = data[i] if i < len(data) else {}
            json_data = json.dumps(data_for_year)

            # Cerca record esistente
            entry = session.query(FinancialCache).filter_by(symbol=symbol, year=year_int).first()

            if entry:
                if entry.data_json != json_data:
                    entry.data_json = json_data
                    logger.info(f"Aggiornato FinancialCache per {symbol} anno {year_int}")
            else:
                entry = FinancialCache(symbol=symbol, year=year_int, data_json=json_data)
                session.add(entry)
                logger.info(f"Inserito FinancialCache per {symbol} anno {year_int}")

        session.commit()
    except Exception as e:
        logger.error(f"Errore salvataggio FinancialCache: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def load_from_db(symbol, years):
    session = Session()
    result_data = []
    try:
        for year in years:
            year_int = int(year)
            entry = session.query(FinancialCache).filter_by(symbol=symbol, year=year_int).first()
            if entry:
                result_data.append(json.loads(entry.data_json))
            else:
                result_data.append(None)
        return result_data
    except Exception as e:
        logger.error(f"Errore caricamento FinancialCache: {e}")
        return [None]*len(years)
    finally:
        session.close()

def save_kpis_to_db(kpi_df):
    session = Session()
    try:
        for _, row in kpi_df.iterrows():
            symbol = row['symbol']
            year = int(row['year'])
            description = row.get('description', None)

            columns_to_drop = ['symbol', 'year', 'description']
            data = row.drop([col for col in columns_to_drop if col in row]).to_dict()
            json_data = json.dumps(data)

            # Cerca record esistente per symbol, year e description (se presente)
            query = session.query(KPICache).filter(
                KPICache.symbol == symbol,
                KPICache.year == year,
                KPICache.description == description
            )
            entry = query.first()

            if entry:
                if entry.kpi_json != json_data:
                    entry.kpi_json = json_data
                    logger.info(f"Aggiornato KPICache per {symbol} anno {year} desc {description}")
            else:
                entry = KPICache(
                    symbol=symbol,
                    year=year,
                    kpi_json=json_data,
                    description=description
                )
                session.add(entry)
                logger.info(f"Inserito KPICache per {symbol} anno {year} desc {description}")

        session.commit()
    except Exception as e:
        logger.error(f"Errore salvataggio KPICache: {e}")
        session.rollback()
        raise
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
    except Exception as e:
        logger.error(f"Errore caricamento KPICache: {e}")
        return pd.DataFrame()
    finally:
        session.close()
