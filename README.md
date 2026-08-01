# Omnichannel ETL Data Pipeline

Este projeto é um **Data Pipeline** completo desenvolvido em Python para consolidação de dados omnichannel. Ele extrai métricas de vendas e inventário de fontes de dados heterogêneas (Bancos de Dados Relacionais e APIs REST) e consolida um dashboard executivo no Google Sheets.

## 🚀 Arquitetura e Tecnologias

- **Source 1 (Lojas Físicas):** Simulação de um banco de dados Relacional PostgreSQL extraído via `SQLAlchemy`.
- **Source 2 (E-commerce):** Consumo de API REST, simulando plataformas de marketplace, utilizando a biblioteca `requests`.
- **Processamento:** Limpeza, transformação e unificação de dados tabulares utilizando `Pandas`. Armazenamento intermediário em formato `Parquet` (Data Lake approach).
- **Destino:** Escrita automatizada em um relatório do `Google Sheets` via Service Accounts e API do GCloud.
- **Orquestração e Resiliência:** Módulo orquestrador central usando `subprocess`. Uso intenso do **Retry Pattern** (via biblioteca `tenacity`) para contornar instabilidades de rede e timeouts de banco.

## ⚙️ Funcionalidades de Engenharia Destacadas

- **Tratamento Robusto de Erros:** Resiliência contra quedas de API utilizando *Exponential Backoff*.
- **Decoupled Architecture:** Módulos isolados (`extractors`, `loaders`), permitindo plugar novas fontes de dados sem quebrar a pipeline.
- **Graceful Shutdown:** Manipulação de sinais via terminal (captura de `Ctrl+C` para matar sub-processos orfãos e proteger a integridade dos dados).
- **Parquet Storage:** Uso do padrão da indústria de dados colunares para salvar snapshots temporários do ETL, garantindo que a fase de 'Load' seja idempotente.

## 🛠️ Instalação e Execução

Pré-requisitos: Python 3.10+ instalado em sua máquina.

**1. Clone o repositório:**
```bash
git clone [https://github.com/seu-usuario/omnichannel-etl-pipeline.git](https://github.com/seu-usuario/omnichannel-etl-pipeline.git)

cd omnichannel-etl-pipeline

```

2. Crie o ambiente virtual:

```python
python -m venv venv
```

3. Ative o ambiente virtual:

No Linux/macOS:

```python
source venv/bin/activate
```

No Windows:

```python
venv\Scripts\activate
```

4. Instale as dependências:

```python
pip install -r requirements.txt
```