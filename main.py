import os
import time
import pandas as pd
import requests
import unidecode
from google.cloud import bigquery
from sqlalchemy import create_engine


#3if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
   #3 os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\issag\OneDrive\Área de Trabalho\pokemon-projeto\novo-pokemon\credentials\chave_teste_dev.json"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/credentials/chave_teste_dev.json"


# CONFIGURAÇÕES DO BANCO via variáveis de ambiente
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASS = os.getenv('POSTGRES_PASSWORD', 'Ams83')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB', 'Ranking_pokemon')

DB_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(DB_URL)

# Variável do caminho da chave Google para autenticação BigQuery
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
else:
    raise EnvironmentError("Variável GOOGLE_APPLICATION_CREDENTIALS não definida no ambiente.")

# 1. Extrai dados do BigQuery para tabela local PostgreSQL
def extract_bigquery():
    client = bigquery.Client()
    query = """
        SELECT nome, numero, ranking
        FROM `bravo-atlas.teste_dev_bravo.ranking_pokemon`
        ORDER BY ranking DESC
        LIMIT 1000
    """
    df = client.query(query).to_dataframe()
    df.to_sql("ranking_bigquery", engine, if_exists="replace", index=False)
    print("[1/4] Dados do BigQuery salvos no PostgreSQL.")

# 2. Busca dados da PokeAPI com base no nome
def get_pokeapi_data(nome):
    nome_formatado = nome.lower().replace(" ", "-").replace(".", "").replace("'", "")\
                    .replace("\u2640", "f").replace("\u2642", "m")
    nome_formatado = unidecode.unidecode(nome_formatado)
    url = f"https://pokeapi.co/api/v2/pokemon/{nome_formatado}"
    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{nome_formatado}"

    try:
        r_pokemon = requests.get(url)
        r_species = requests.get(species_url)

        if r_pokemon.status_code != 200 or r_species.status_code != 200:
            return {'numero': None, 'tipos': None, 'habilidades': None, 'geracao': None}

        pj = r_pokemon.json()
        sj = r_species.json()

        return {
            'numero': pj['id'],
            'tipos': ', '.join(t['type']['name'] for t in pj['types']),
            'habilidades': ', '.join(h['ability']['name'] for h in pj['abilities']),
            'geracao': sj['generation']['name']
        }
    except:
        return {'numero': None, 'tipos': None, 'habilidades': None, 'geracao': None}

# 3. Extrai dados da API e salva localmente no banco
def fetch_pokeapi():
    df_ranking = pd.read_sql("SELECT * FROM ranking_bigquery", engine)
    dados = []
    for idx, row in df_ranking.iterrows():
        nome = row['nome']
        d = get_pokeapi_data(nome)
        d['nome'] = nome
        d['ranking'] = row['ranking']
        dados.append(d)
        time.sleep(0.5)
    df_api = pd.DataFrame(dados)
    df_api.to_sql("dados_pokeapi", engine, if_exists="replace", index=False)
    print("[2/4] Dados da API salvos no PostgreSQL.")

# 4. Merge dos dados do BigQuery + PokeAPI e salva final
def padronizar_nome(nome):
    if pd.isnull(nome):
        return ""
    nome = nome.lower().strip()
    nome = unidecode.unidecode(nome)
    nome = nome.replace(" ", "-").replace(".", "")
    return nome

def merge_and_store():
    df_bq = pd.read_sql("SELECT * FROM ranking_bigquery", engine)
    df_api = pd.read_sql("SELECT * FROM dados_pokeapi", engine)

    df_bq['nome_padronizado'] = df_bq['nome'].apply(padronizar_nome)
    df_api['nome_padronizado'] = df_api['nome'].apply(padronizar_nome)

    df_merged = pd.merge(df_bq, df_api, on="nome_padronizado", how="inner")
    df_merged.drop(columns=["nome_padronizado"], inplace=True)
    df_merged.rename(columns={'nome_x': 'nome', 'ranking_x': 'ranking'}, inplace=True)

    df_merged.to_sql("ranking_unificado", engine, if_exists="replace", index=False)
    print("[3/4] Dados unificados salvos no PostgreSQL.")

# 5. Verifica os dados finais
def verify_results():
    df = pd.read_sql("SELECT * FROM ranking_unificado", engine)
    print("[4/4] Verificando resultado final:")
    print(df[['nome', 'ranking']].head(10))

# Função principal
def main():
    extract_bigquery()
    fetch_pokeapi()
    merge_and_store()
    verify_results()
    print("\nPipeline completo com sucesso!")

if __name__ == "__main__":
    main()
