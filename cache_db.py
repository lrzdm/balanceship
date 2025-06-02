from sqlalchemy import create_engine, Column, String, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()
engine = create_engine('sqlite:///financial_cache.db')
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
