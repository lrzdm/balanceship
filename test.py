from sqlalchemy import create_engine
import streamlit as st

url = "postgresql+psycopg2://postgres:ukI1XkSjJ9KZXw8p@db.ushtfkgezrisfwddarye.supabase.co:5432/postgres"
engine = create_engine(url)

try:
    with engine.connect() as conn:
        st.write("✅ Connessione riuscita")
except Exception as e:
    st.write("❌ Errore:", e)


