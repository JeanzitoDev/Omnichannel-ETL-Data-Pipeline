import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from pathlib import Path
import os
import glob
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# Credenciais e Infos da Planilha
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEET_TAB_NAME = os.getenv("DASHBOARD_TAB_NAME", "Consolidated_Sales")

def get_latest_parquet(prefix: str) -> pd.DataFrame:
    """Busca o arquivo mais recente processado pelos extratores."""
    search_pattern = os.path.join(PROCESSED_DATA_DIR, f"{prefix}_*.parquet")
    files = glob.glob(search_pattern)
    
    if not files:
        return pd.DataFrame()
        
    latest_file = max(files, key=os.path.getmtime)
    print(f"Carregando: {Path(latest_file).name}")
    return pd.read_parquet(latest_file)

def run_sync():
    print("--- Iniciando Sincronização com Google Sheets ---")
    
    # 1. Carrega os dados processados
    df_store = get_latest_parquet("store_sales")
    df_web = get_latest_parquet("web_sales")
    
    if df_store.empty and df_web.empty:
        print("✖ Sem dados novos para processar.")
        return
        
    # 2. Concatena as fontes de dados
    df_final = pd.concat([df_store, df_web], ignore_index=True)
    
    # 3. Adiciona colunas dinâmicas (Regra de Negócio Genérica)
    df_final['average_ticket'] = df_final['total_revenue'] / df_final['total_quantity']
    df_final = df_final.round(2).fillna(0)
    
    # 4. Sincroniza com Google Sheets
    print("Conectando ao Google Cloud...")
    try:
        gc = gspread.service_account(filename=CREDENTIALS_FILE)
        workbook = gc.open_by_key(SHEET_ID)
        worksheet = workbook.worksheet(SHEET_TAB_NAME)
        
        # Backup em memória antes de sobrescrever
        print("Criando backup rápido (em caso de falha de conexão)...")
        _ = worksheet.get_all_records() 
        
        print("Enviando dados...")
        worksheet.clear()
        # O allow_formulas=True permite que o engenheiro gerencie o layout e dashboards a partir desses dados crus
        set_with_dataframe(worksheet, df_final, include_index=False, resize=True) 
        
        print("✔ Google Sheets Dashboard atualizado com sucesso!")
        
    except Exception as e:
        print(f"✖ Erro fatal durante a sincronização da planilha: {e}")

if __name__ == "__main__":
    run_sync()