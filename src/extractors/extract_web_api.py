import pandas as pd
import requests
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

API_URL = os.getenv("ECOMMERCE_API_URL", "https://api.mock-ecommerce.com/v1/sales")
API_TOKEN = os.getenv("ECOMMERCE_API_TOKEN", "dummy_token")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def fetch_ecommerce_data(target_month: str) -> pd.DataFrame:
    """Consome a API REST do E-commerce com tolerância a falhas."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Acessando API E-commerce...")
    
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    params = {"period": target_month, "format": "json"}
    
    # Simulação de chamada HTTP segura (Substitui a integração frágil SOAP/WSDL)
    response = requests.get(API_URL, headers=headers, params=params, timeout=30)
    response.raise_for_status() # Lança erro se status não for 200, ativando o retry
    
    data = response.json().get("data", [])
    return pd.DataFrame(data)

def run_extraction(target_month: str):
    print("--- Iniciando Extração API E-commerce ---")
    
    try:
        df = fetch_ecommerce_data(target_month)
    except Exception as e:
        print(f"✖ Falha Crítica ao acessar API após retentativas: {e}")
        return # Permite graceful fallback em vez de quebrar a pipeline toda

    if df.empty:
        print("Aviso: Nenhum dado retornado da API.")
        return

    # Padronização para combinar com os dados da loja física
    df_clean = df[['region_id', 'category', 'qty', 'revenue']].copy()
    df_clean.rename(columns={'region_id': 'store_id', 'category': 'product_category', 
                             'qty': 'total_quantity', 'revenue': 'total_revenue'}, inplace=True)
    df_clean['source'] = 'ECOMMERCE'

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = PROCESSED_DATA_DIR / f"web_sales_{target_month}_{timestamp}.parquet"
    
    df_clean.to_parquet(file_path, index=False)
    print(f"✔ Dados salvos com sucesso em: {file_path.name}")

if __name__ == "__main__":
    current_month = datetime.now().strftime("%Y-%m")
    run_extraction(current_month)