from github import Github
import os
import re
from dotenv import load_dotenv
import requests
import base64
import pandas as pd


def extract_repositories_from_content(content):
    """
    Extrai os detalhes dos repositórios do conteúdo do arquivo .tfvars.
    Retorna um dicionário com os nomes dos repositórios e suas propriedades.
    """
    # Expressão regular para encontrar blocos de repositórios
    repo_pattern = re.compile(r'\s*=\s*{\s*name\s*=\s*"([^"]+)"\s*description\s*=\s*"([^"]+)"')
    repos = repo_pattern.findall(content)
    
    # Estrutura para armazenar informações dos repositórios
    repositories_info = {name: {"description": description} for name, description in repos}
    return repositories_info

def get_squad_repos(repo_name, path):
    # Carrega o token de acesso do ambiente
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    g = Github(ACCESS_TOKEN)

    repo = g.get_repo(repo_name)
    contents = repo.get_contents(path)

    squad_repos = {}

    for content_file in contents:
        if content_file.name.endswith('.tfvars'):
            squad_name = content_file.name.rsplit('.', 1)[0]
            content_data = content_file.decoded_content.decode('utf-8')
            repositories_info = extract_repositories_from_content(content_data)
            squad_repos[squad_name] = repositories_info

    return squad_repos

def parse_tfvars_content(content):
    """
    Extrai informações dos repositórios do conteúdo de um arquivo tfvars.
    """
    # Esta é uma forma simplificada e pode precisar de ajustes dependendo da complexidade do seu arquivo tfvars
    pattern = re.compile(r'name\s*=\s*"([^"]+)"')
    matches = pattern.findall(content)
    
    return matches

def get_squads_and_repos(repo_name, path):
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    g = Github(ACCESS_TOKEN)

    repo = g.get_repo(repo_name)
    contents = repo.get_contents(path)

    data = []
    print(contents)
    for content_file in contents: # type: ignore
        if content_file.name.endswith('.tfvars'):
            squad_name = content_file.name.rsplit('.', 1)[0]
            file_content = repo.get_contents(content_file.path)
            decoded_content = base64.b64decode(file_content.content).decode('utf-8')
            repo_names = parse_tfvars_content(decoded_content)
            
            for repo_name in repo_names:
                data.append({
                    'Squad Name': squad_name,
                    'Repository Name': repo_name
                })

    return pd.DataFrame(data)


# Exemplo de uso
repo_name = 'yaperos/devops'
path = 'terraform/tfvars/squads'
squad_repos = get_squad_repos(repo_name, path)
data = []
for squad, repos in squad_repos.items():
    print(f"Squad: {squad}")
    for repo_name, repo_info in repos.items():
        print(f"  - {repo_name}: {repo_info['description']}")
        data.append({
                    'Squad Name': squad,
                    'Repository Name': repo_name,
                    'Description': repo_info['description']

                })

repos = pd.DataFrame(data)
repos_old = pd.read_excel('/Users/alexfrisoneyape/Development/EM-projects/output/repos.xlsx').copy()
repos.to_excel('/Users/alexfrisoneyape/Development/EM-projects/output/repos.xlsx')
repos_new = pd.read_excel('/Users/alexfrisoneyape/Development/EM-projects/output/repos.xlsx').copy()

# Identificando novos, removidos e alterados
novos = repos_new[~repos_new['Repository Name'].isin(repos_old['Repository Name'])]
removidos = repos_old[~repos_old['Repository Name'].isin(repos_new['Repository Name'])]

# Preparando dados para comparação de alterações
comuns_old = repos_old[repos_old['Repository Name'].isin(repos_new['Repository Name'])]
comuns_new = repos_new[repos_new['Repository Name'].isin(repos_old['Repository Name'])]

# Ordenando para facilitar a comparação
comuns_old = comuns_old.sort_values(by='Repository Name').reset_index(drop=True)
comuns_new = comuns_new.sort_values(by='Repository Name').reset_index(drop=True)

# Checando alterações, considerando todos os campos
alterados = comuns_old != comuns_new
indices_alterados = alterados.any(axis=1)

# Selecionando as colunas relevantes para mostrar nos resultados
novos_repos = novos[['Squad Name', 'Repository Name']]
removidos_repos = removidos[['Squad Name', 'Repository Name']]
comuns_alterados = comuns_old[indices_alterados]

# Exibindo os resultados
if not novos_repos.empty:
    print("################################")
    print("Novos Repositórios Adicionados:")
    print("################################")
    print(novos_repos)
else:
    print("Não foram encontrados repositórios novos")

if not removidos_repos.empty:    
    print("################################")
    print("\nRepositórios Removidos:")
    print("################################")
    print(removidos_repos)
else:
    print("Não foram encontrados repositórios removidos")

if not comuns_alterados.empty:
    print("################################")
    print("\nAlterações em Repositórios Existentes:")
    print("################################")
    print(comuns_alterados)
else:
    print("Não foram encontrados repositórios alterados")