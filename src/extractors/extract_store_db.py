import pandas as pd
import sqlalchemy
from sqlalchemy import text
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

# Configuração de caminhos usando Pathlib (Moderno)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_URL = os.getenv("STORE_DB_URL", "sqlite:///simulated_store.db") # Usando SQLite como fallback seguro

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_sales_data(target_month: str) -> pd.DataFrame:
    """Extrai dados de vendas físicas do banco relacional com Retry Pattern."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Conectando ao banco da Loja Física...")
    
    engine = sqlalchemy.create_engine(DB_URL)
    
    # Query genérica de simulação de vendas (Substitui o SQL específico da empresa)
    query = text("""
        SELECT 
            store_id,
            product_category,
            SUM(quantity_sold) as total_quantity,
            SUM(net_revenue) as total_revenue,
            MAX(last_update) as last_sync
        FROM physical_sales
        WHERE strftime('%Y-%m', sale_date) = :period
        GROUP BY store_id, product_category
    """)
    
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"period": target_month})
            return df
    except Exception as e:
        print(f"[ALERTA] Falha na conexão ou query. Tentando novamente... Erro: {e}")
        raise # O raise trigga o retry do tenacity

def run_extraction(target_month: str):
    print("--- Iniciando Extração DB Lojas Físicas ---")
    df = fetch_sales_data(target_month)
    
    if df.empty:
        print("Aviso: Nenhum dado retornado do Banco. Processo abortado.")
        return
        
    # Tratamento de dados (Transform)
    df['total_revenue'] = df['total_revenue'].astype(float).round(2)
    df['source'] = 'PHYSICAL_STORE'
    
    # Salvar em Parquet (Melhor prática que Pickle)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = PROCESSED_DATA_DIR / f"store_sales_{target_month}_{timestamp}.parquet"
    
    df.to_parquet(file_path, index=False)
    print(f"✔ Dados salvos com sucesso em: {file_path.name}")

if __name__ == "__main__":
    current_month = datetime.now().strftime("%Y-%m")
    run_extraction(current_month)