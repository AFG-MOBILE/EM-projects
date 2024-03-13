from github import Github
import re
from base64 import b64decode
from dotenv import load_dotenv
import os
import pandas as pd
import subprocess
from fuzzywuzzy import process



# Função para extrair dados dos usuários a partir do conteúdo do arquivo
def extrair_dados_usuarios():
    # Autenticação na API do GitHub
    token = os.getenv('ACCESS_TOKEN')
    g = Github(token)

    # Acessando o repositório e o arquivo
    # nome_do_usuario = "nome_do_usuario"
    nome_do_repositorio = "yaperos/devops"
    caminho_arquivo = "terraform/tfvars/squads/okta.tfvars"

    repo = g.get_repo(f"{nome_do_repositorio}")
    contents = repo.get_contents(caminho_arquivo)
    # Decodificando o conteúdo do arquivo
    file_content = b64decode(contents.content).decode('utf-8')
    user_definitions = re.findall(r'(\w+)\s*=\s*{([^}]+)}', file_content)
    users_data = {}

    for user_key, user_data in user_definitions:
        user_attributes = re.findall(r'(\w+)\s*=\s*"([^"]+)"|\s*(\w+)\s*=\s*\[([^\]]+)\]', user_data)
        user_info = {}
        for attr in user_attributes:
            key = attr[0] if attr[0] else attr[2]
            value = attr[1] if attr[1] else attr[3]
            if key in ['groups', 'squad', 'tooling_teams']:
                user_info[key] = [item.strip().strip('"') for item in value.split(',')]
            else:
                user_info[key] = value
        users_data[user_key] = user_info
    
    data = []
    for user_key, user_info in users_data.items():
        print(f"Usuário: {user_key}")
        print(f"Info: {user_info}")
        if not 'first_name' in user_info:
            continue
        fullname = f"{user_info['first_name']} {user_info['last_name']}"
        data.append({
                        'Contributor Name': fullname,
                        'Username':user_key,
                        'Email':user_info['email'],
                        'Role': user_info['title'] if 'title' in user_info else '',
                        'Squad': user_info['squad'] if 'squad' in user_info else '',
                        'Division': user_info['division'] if 'division' in user_info else ''
                    })
        for info_key, info_value in user_info.items():
            print(f"  {info_key}: {info_value}")
            
        print("-" * 40)

    return data

data = extrair_dados_usuarios()
users = pd.DataFrame(data)
filename = "/Users/alexfrisoneyape/Development/EM-projects/output/contributors_roles.xlsx"
users.to_excel(filename)
subprocess.run(['open', '-a', 'Microsoft Excel', filename])
