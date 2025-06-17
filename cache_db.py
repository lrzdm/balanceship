import os
import json
import logging
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Column, String, Text, Integer
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cache_db")

# Base ORM
Base = declarative_base()

# Engine di DB
if os.environ.get("STREAMLIT_CLOUD") == "1":
    DATABASE_URL = os.environ.get("DATABASE_URL")
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    os.makedirs("data", exist_ok=True)
    DATABASE_URL = "sqlite:///data/financials_db.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

Session = scoped_session(sessionmaker(bind=engine))

# Modelli tabella
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

def create_tables():
    if os.environ.get("STREAMLIT_CLOUD") != "1":
        Base.metadata.create_all(engine)
        logger.info("✅ Tabelle create o già esistenti.")

# Convertitore robusto per tipi numpy e date
def convert_numpy(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(i) for i in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, (np.datetime64, pd.Timestamp)):
        return str(obj)
    elif pd.isna(obj):
        return None
    return obj

def save_to_db(symbol, years, data_list):
    session = Session()
    try:
        for i, year in enumerate(years):
            year_int = int(year)
            if i >= len(data_list) or not isinstance(data_list[i], dict) or not data_list[i]:
                logger.debug(f"Salvataggio SKIPPED per {symbol} anno {year}: no data.")
                continue

            data_for_year = data_list[i]
            data_for_year = convert_numpy(data_for_year)
            json_data = json.dumps(data_for_year, ensure_ascii=False)

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
            if entry and entry.data_json:
                try:
                    if isinstance(entry.data_json, str):
                        result_data.append(json.loads(entry.data_json))
                    elif isinstance(entry.data_json, dict):
                        # Già dict, probabilmente salvato male in passato
                        result_data.append(entry.data_json)
                    else:
                        logger.warning(f"Formato inaspettato per {symbol} {year}: {type(entry.data_json)}")
                        result_data.append(None)
                except Exception as e:
                    logger.error(f"JSON decode error per {symbol} {year}: {e}")
                    result_data.append(None)
            else:
                result_data.append(None)
        return result_data
    except Exception as e:
        logger.error(f"Errore caricamento FinancialCache: {e}")
        return [None] * len(years)
    finally:
        session.close()
        
def save_kpis_to_db(kpi_df):
    session = Session()
    try:
        for _, row in kpi_df.iterrows():
            symbol = row['symbol']
            year = int(row['year'])
            desc = row.get('description', None)
            data = row.drop(['symbol','year','description'], errors='ignore').to_dict()
            data = convert_numpy(data)
            json_data = json.dumps(data, ensure_ascii=False)

            entry = session.query(KPICache).filter_by(symbol=symbol, year=year, description=desc).first()
            if entry:
                if entry.kpi_json != json_data:
                    entry.kpi_json = json_data
                    logger.info(f"Aggiornato KPICache per {symbol} anno {year}")
            else:
                entry = KPICache(symbol=symbol, year=year, description=desc, kpi_json=json_data)
                session.add(entry)
                logger.info(f"Inserito KPICache per {symbol} anno {year}")
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
        records = []
        for entry in session.query(KPICache).all():
            try:
                data = json.loads(entry.kpi_json)
                data.update({'symbol': entry.symbol, 'year': entry.year, 'description': entry.description})
                records.append(data)
            except Exception as e:
                logger.error(f"Errore JSON decode KPICache {entry.symbol} {entry.year}: {e}")
        return pd.DataFrame(records)
    except Exception as e:
        logger.error(f"Errore caricamento KPICache: {e}")
        return pd.DataFrame()
    finally:
        session.close()
