import subprocess
import sys
from pathlib import Path
import time
import logging

# Configuração
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "pipeline_run.log"

logging.basicConfig(
    filename=LOG_FILE, level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

def print_banner():
    print(f"""{Colors.GREEN}
    ================================================
       OMNICHANNEL ETL PIPELINE (Data Engineering)
    ================================================{Colors.RESET}
    """)

def run_step(step_name: str, script_path: Path) -> bool:
    print(f"\n{Colors.YELLOW}[▶] Executando: {step_name}...{Colors.RESET}")
    logging.info(f"Start: {step_name}")
    
    try:
        # Usa subprocess com captura de log segura
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        for line in process.stdout:
            sys.stdout.write(f"  | {line}")
            
        process.wait()
        
        if process.returncode == 0:
            print(f"{Colors.GREEN}[✔] {step_name} Concluído.{Colors.RESET}")
            logging.info(f"Success: {step_name}")
            return True
        else:
            print(f"{Colors.RED}[✖] Falha no processo: {step_name}{Colors.RESET}")
            logging.error(f"Failed: {step_name} with code {process.returncode}")
            return False
            
    except KeyboardInterrupt:
        process.terminate()
        print(f"\n{Colors.RED}Processo abortado pelo usuário!{Colors.RESET}")
        sys.exit(1)

def main():
    print_banner()
    
    steps = [
        ("Extração BD Loja Física", BASE_DIR / "src" / "extractors" / "extract_store_db.py"),
        ("Extração API E-commerce", BASE_DIR / "src" / "extractors" / "extract_web_api.py"),
        ("Carga no Google Sheets (Dashboard)", BASE_DIR / "src" / "loaders" / "load_gsheets.py"),
    ]
    
    for name, path in steps:
        success = run_step(name, path)
        if not success:
            print(f"\n{Colors.RED}Pipeline interrompido devido a erro crítico.{Colors.RESET}")
            sys.exit(1)
            
    print(f"\n{Colors.GREEN}================ PIPELINE FINALIZADO COM SUCESSO ================={Colors.RESET}")

if __name__ == "__main__":
    main()