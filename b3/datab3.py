import pandas as pd
from pandasql import sqldf
import os
from sqlalchemy import create_engine, MetaData


def __create_data_frame(direto):
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

def __format_data_frame(data_frame, data_columns, currency_collumns):
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


def getMovimentacoes():
    data_frame = pd.concat(__create_data_frame(f'/Users/alexfrisoneyape/Development/EM/b3/movimentacao/'), ignore_index=True)    
    __format_data_frame(data_frame, ['Data'], ['Preço unitário', 'Valor da Operação'])
    return data_frame
    
def getProventos():
    data_frame = pd.concat(__create_data_frame(f'/Users/alexfrisoneyape/Development/EM/b3/proventos/'), ignore_index=True)    
    __format_data_frame(data_frame, ['Pagamento'], ['Preço unitário', 'Valor líquido'])
    return data_frame

def saveCSV(data,path):
    df = pd.DataFrame(data)
    # Salve o DataFrame em um arquivo CSV
    df.to_csv(path, index=False)  # index=False para não incluir o índice no arquivo

