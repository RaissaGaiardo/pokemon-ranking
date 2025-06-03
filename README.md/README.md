
# Pokémon Pipeline - Prof. Carvalho's Project

Este projeto automatiza a coleta e integração diária de dados dos Pokémon mais populares, unificando dados do BigQuery e da PokeAPI, e armazenando-os em um banco PostgreSQL containerizado.

## Tecnologias 
Python 3.10
Docker / Docker Compose
Google BigQuery
PostgreSQL
PokeAPI

## Como rodar o projeto

### 1. Clone o repositório
git clone https://github.com/RaissaGaiardo/pokemon-ranking
cd pokemon-projeto

## 2. Adicione sua chave do BigQuery
Coloque seu arquivo chave_teste_dev.json na pasta credentials/.

### 3. Inicie os containers
Construa e suba os containers com docker-compose:
docker-compose up -d --build

## Execute o pipeline
Para rodar o pipeline manualmente dentro do container:
docker exec -it pokemon_pipeline python /app/main.py

## 4. Acesse o banco
Conecte-se ao PostgreSQL via PgAdmin:
Host: localhost
Porta: 5432
Usuário: postgres
Senha: Ams83
Banco: Ranking_pokemon

As seguintes tabelas serão criadas:
ranking_bigquery
dados_pokeapi
ranking_unificado

## Agendamento diário
O cron dentro do container executa o pipeline automaticamente diariamente.