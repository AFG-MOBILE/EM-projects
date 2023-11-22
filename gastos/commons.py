import os
import pandas as pd
import datetime

def create_data_from_filenames(directory_path: str) -> pd.DataFrame:
    # Lista todos os arquivos no diretório especificado
    all_files = os.listdir(directory_path)
    
    # Filtra apenas arquivos com extensão .pdf
    pdf_files = [file for file in all_files if file.endswith('.pdf')]
    
    # Extrai informações dos nomes dos arquivos
    data = []
    keys = ['data', 'descricao', 'valor_em_real', 'cotacao_cartao', 'valor_em_dolar']
    for file in pdf_files:
        # Remove a extensão .pdf e divide usando o caractere '|'
        info = file[:-4].split('|')
        data_dict = dict(zip(keys, info))
        data.append(data_dict)
    return data
    
def ajusta_data_para_sexta(data_str: str) -> str:
    # Converte a string no formato 'dd/mm/yyyy' para um objeto datetime.date
    data = datetime.datetime.strptime(data_str, '%d/%m/%Y').date()
    
    # Verifica se a data é um sábado (5) ou domingo (6)
    if data.weekday() == 5:  # sábado
        data -= datetime.timedelta(days=1)
    elif data.weekday() == 6:  # domingo
        data -= datetime.timedelta(days=2)
    
    # Retorna a data ajustada no formato 'dd/mm/yyyy'
    return data.strftime('%d/%m/%Y')