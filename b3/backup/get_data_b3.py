import pandas as pd
from sqlalchemy import create_engine

# Configurações para o banco de dados (SQLite)
db_uri = 'sqlite:///arca.db'  # Substitua pelo URI do seu banco de dados

# Nome da tabela onde você deseja inserir os dados
table_name = 'movimentacao'

# Conecta ao banco de dados
engine = create_engine(db_uri)

# Consulta o banco de dados e recupera os dados da tabela
query = f"SELECT * FROM {table_name}"
df = pd.read_sql(query, engine)

# print("Dados do arquivo CSV foram gravados no banco de dados.")
print(df)
