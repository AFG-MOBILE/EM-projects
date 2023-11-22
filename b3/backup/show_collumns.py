import sqlite3

# Conecte-se ao banco de dados SQLite
conn = sqlite3.connect('arca.db')

# Crie um cursor
cursor = conn.cursor()

# Substitua 'MinhaTabela' pelo nome da tabela desejada
tabela = 'movimentacao'

# Consulta para obter informações sobre a tabela
cursor.execute(f"PRAGMA table_info({tabela})")

# Recupere os resultados
colunas = [row[1] for row in cursor.fetchall()]

# Feche a conexão
conn.close()

print('Nomes das colunas:', colunas)
