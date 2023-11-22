import pandas as pd
from pandasql import sqldf
import os
from sqlalchemy import create_engine, MetaData
import sqlite3


def create_data_frame(direto):
    # Inicialize uma lista para armazenar os DataFrames lidos
    frames = []
    # Listar todos os arquivos CSV no diretório
    arquivos_csv = [arquivo for arquivo in os.listdir(direto) if arquivo.endswith('.csv')]
    # Loop para ler e concatenar os arquivos
    for arquivo_csv in arquivos_csv:
        caminho_completo = os.path.join(direto, arquivo_csv)
        df_temp = pd.read_csv(caminho_completo, sep=';', header=0)
        frames.append(df_temp)
    return frames

def format_data_frame(data_frame, data_columns, currency_collumns):
    for column in data_columns:
        data_frame[column] = pd.to_datetime(data_frame[column], format='%d/%m/%Y')

    # Remova os caracteres não numéricos da coluna 
    for column in currency_collumns:
        data_frame[column] = data_frame[column].str.replace(' - ','0')
        data_frame[column] = data_frame[column].str.replace('R$','')
        data_frame[column] = data_frame[column].str.replace(' ','')
        data_frame[column] = data_frame[column].str.replace('.','')
        data_frame[column] = data_frame[column].str.replace(',','.')
        #Converta a coluna 'Valor' para tipo float
        data_frame[column] = data_frame[column].astype(float)

def populate_db(data_frame, table):
    # Inserir os dados do DataFrame no banco de dados
    print(f'***********')
    print(f'*********** Inserindo Dados em {table}')
    print(f'***********')
    data_frame.to_sql(table, con=engine, if_exists='append', index=False)
    

def drop_db():
    # Conecta ao banco de dados
    engine = create_engine(db_uri)
    metadata = MetaData()

    # Use o método drop_all para excluir todas as tabelas no banco de dados
    metadata.reflect(bind=engine)
    metadata.drop_all(bind=engine)

def create_table_and_create_key():
    # Conecte-se ao banco de dados SQLite
    conn = sqlite3.connect('arca.db')

    # Crie um cursor para executar comandos SQL
    cursor = conn.cursor()

    # Crie a tabela com uma chave composta de 'ID' e 'Nome'
    cursor.execute(f'''
        CREATE TABLE movimentacao (
            'Entrada/Saída' TEXT,
            'Data' DATE,
            'Movimentação' TEXT,
            'Produto' TEXT,
            'Quantidade' INTEGER,
            'Preço unitário' REAL,
            'Valor da Operação'  REAL,
            PRIMARY KEY ('Produto', 'Data')
        )
    ''')

    # Crie a tabela com uma chave composta de 'ID' e 'Nome'
    cursor.execute('''
        CREATE TABLE proventos (
            'Produto', 
            'Pagamento', 
            'Tipo de Evento', 
            'Instituição', 
            'Quantidade', 
            'Preço unitário', 
            'Valor líquido',
            PRIMARY KEY ('Produto','Pagamento')
        )
    ''')

    # Salve as alterações e feche a conexão com o banco de dados
    conn.commit()
    conn.close()



if __name__ == "__main__":
    # Configurações para o banco de dados (SQLite)
    db_uri = 'sqlite:///arca.db'  # Substitua pelo URI do seu banco de dados
    
    # Diretório que contém os arquivos CSV
    tables = ['movimentacao', 'proventos']
    
    # Conectar ao banco de dados
    engine = create_engine(db_uri)
    
    data_frames = [pd.DataFrame(),pd.DataFrame()]
    # drop_db()

    data_frames[0] = pd.concat(create_data_frame(f'/Users/alexfrisoneyape/Development/EM/b3/{tables[0]}/'), ignore_index=True)    
    data_frames[1] = pd.concat(create_data_frame(f'/Users/alexfrisoneyape/Development/EM/b3/{tables[1]}/'), ignore_index=True)    
    
    format_data_frame(data_frames[0], ['Data'], ['Preço unitário', 'Valor da Operação'])
    format_data_frame(data_frames[1], ['Pagamento'], ['Preço unitário', 'Valor líquido'])
    
    print(data_frames[0])
    print(data_frames[1])

    # create_table_and_create_key()
    # populate_db(data_frames[0],tables[0])
    # populate_db(data_frames[1],tables[1])
    movimentacoes = data_frames[0]
    query = f"SELECT * FROM movimentacoes"
    df_movimentacoes = sqldf(query,globals())
    print(df_movimentacoes)


