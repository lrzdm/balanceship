from sqlalchemy import create_engine

url = "postgresql+psycopg2://postgres:ukI1XkSjJ9KZXw8p@db.ushtfkgezrisfwddarye.supabase.co:5432/postgres"
engine = create_engine(url)

try:
    with engine.connect() as conn:
        print("✅ Connessione riuscita")
except Exception as e:
    print("❌ Errore:", e)


