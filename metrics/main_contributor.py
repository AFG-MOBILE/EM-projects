from fileinput import filename
import requests
from datetime import datetime
import pandas as pd
import subprocess
import commons_yape
from fuzzywuzzy import process
from github import Github
import os
from base64 import b64decode
import re

API_KEY = "522a4cd86f769c2cd1c8b97c151e0210"

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

def fetch_linearb_data():
    # URL da API
    url = "https://public-api.linearb.io/api/v2/measurements"
    
    # Cabeçalhos necessários para a requisição
    headers = {
        "x-api-key": API_KEY
    }
    
    # Parâmetros do corpo da requisição
    payload = {
      "group_by": "contributor",
      "roll_up": "custom",
      "requested_metrics": [
        {"name": "branch.computed.cycle_time", "agg": "avg"},
        {"name": "commit.activity.new_work.count"},
        {"name": "commit.activity.refactor.count"},
        {"name": "commit.activity.rework.count"},
        {"name": "pr.reviews"},
        {"name": "pr.new"},
        {"name": "pr.merged"},
        {"name": "branch.state.computed.done"},
        {"name": "commit.activity_days"}
      ],
      "time_ranges": [
        {"after": "2023-08-01", "before": "2023-08-31"},
        {"after": "2023-09-01", "before": "2023-09-30"},
        {"after": "2023-10-01", "before": "2023-10-31"},
        {"after": "2023-11-01", "before": "2023-11-30"},
        {"after": "2023-12-01", "before": "2023-12-31"},
        {"after": "2024-01-01", "before": "2024-01-31"},
        {"after": "2024-02-01", "before": "2024-02-29"},
        {"after": "2024-03-01", "before": "2024-03-11"}
      ]
    }
    
    # Fazer a requisição e retornar a resposta
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def parse_and_format_response(response):
    # Estrutura para armazenar os dados formatados
    formatted_data = []
    
    # Iterar sobre os períodos na resposta
    for period in response:
        # Formatar a data
        date_format = datetime.strptime(period["after"], "%Y-%m-%d").strftime("%m/%Y")
        
        # Iterar sobre as métricas para cada contribuidor
        for metric in period["metrics"]:
            # Preparar o registro com a data formatada
            metric_data = {"date": date_format}
            
            # Extrair métricas relevantes
            relevant_metrics = ["contributor_id","branch.computed.cycle_time:avg", "commit.activity.new_work.count", "commit.total_changes", "commit.activity.refactor.count", "commit.activity.rework.count", "pr.reviews", "pr.new", "pr.merged", "branch.state.computed.done","commit.activity_days"]
            for key in relevant_metrics:
                if key in metric:
                    metric_data[key] = metric[key]
            
            # Adicionar o registro formatado à lista
            formatted_data.append(metric_data)
    
    return formatted_data

def get_contributor_names():
    headers = {"x-api-key": API_KEY}
    teams_url = "https://public-api.linearb.io/api/v1/teams?nonmerged_members_only=false"
    
    response = requests.get(teams_url, headers=headers)
    contributors_dict = {}
    
    if response.status_code == 200:
        teams_data = response.json()
        for item in teams_data.get("items", []):
            for contributor in item.get("contributors", []):
                contributors_dict[contributor["id"]] = contributor["name"]
    
    return contributors_dict

def format_with_name_contributor(metrics_response, contributors_dict):
    formatted_data = []

    # Iterar sobre cada registro na resposta das métricas
    for record in metrics_response:
        contributor_id = record.get("contributor_id")
        if contributors_dict.get(contributor_id):
            contributor_name = contributors_dict.get(contributor_id, "Unknown Contributor")  # Pega o nome ou "Unknown" se não encontrar
            formatted_record = {
                "Contributor Id": contributor_id,
                "Contributor Name": contributor_name,
                "Date": record.get("date", "N/A")[:7],  # Ajusta o formato da data para mm/yyyy
                "Cycle time": record.get("branch.computed.cycle_time:avg"),
                "Cycle time (Formatted)": commons_yape.formatTime(record.get("branch.computed.cycle_time:avg",0)),
                "Total Changes": record.get("commit.total_changes"),
                "New Work": record.get("commit.activity.new_work.count"),
                "New Work (%)": record.get("commit.activity.new_work.count")*100/record.get("commit.total_changes") if record.get("commit.activity.new_work.count") is not None and record.get("commit.activity.new_work.count") != 0  else 0,
                "Refactor": record.get("commit.activity.refactor.count"),
                "Refactor (%)": record.get("commit.activity.refactor.count")*100/record.get("commit.total_changes") if record.get("commit.activity.refactor.count") is not None and record.get("commit.activity.refactor.count") != 0  else 0,
                "Rework": record.get("commit.activity.rework.count"),
                "Rework (%)": record.get("commit.activity.rework.count")*100/record.get("commit.total_changes") if record.get("commit.activity.rework.count") is not None and record.get("commit.activity.rework.count") != 0  else 0,
                "PR Reviews": record.get("pr.reviews"),
                "PR New": record.get("pr.new"),
                "PR Merged": record.get("pr.merged"),
                "Branches Done": record.get("branch.state.computed.done"),
                "Activity Days": record.get("commit.activity_days")
            }
            
            formatted_data.append(formatted_record)

    return formatted_data

def getMetricsContributorsByLinearB(fetch_linearb_data, parse_and_format_response, get_contributor_names, format_with_name_contributor):
    response = fetch_linearb_data()  # Descomente esta linha para fazer a requisição real
    formatted_data = parse_and_format_response(response)  # Use a resposta real aqui

    contributor_names = get_contributor_names()

    contributor_data = format_with_name_contributor(formatted_data, contributor_names)
    df_contributor = pd.DataFrame(contributor_data)

    filename = "/Users/alexfrisoneyape/Development/EM-projects/output/contributors_metrics.xlsx"
    df_contributor.to_excel(filename)

    # Filtro para contribuidores inativos
    mask = (
        (df_contributor['Total Changes'].isnull() | (df_contributor['Total Changes'] == 0)) &
        (df_contributor['PR Reviews'].isnull() | (df_contributor['PR Reviews'] == 0)) &
        (df_contributor['PR New'].isnull() | (df_contributor['PR New'] == 0)) &
        (df_contributor['PR Merged'].isnull() | (df_contributor['PR Merged'] == 0)) &
        (df_contributor['Branches Done'].isnull() | (df_contributor['Branches Done'] == 0))
    )

    df_inactive_contributors = df_contributor[mask].copy()

    # Verifique se há contribuidores inativos para adicionar
    if not df_inactive_contributors.empty:
    # Crie uma nova aba na planilha para contribuidores inativos
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
            df_inactive_contributors.to_excel(writer, sheet_name='Inactive Contributors', index=False)
    else:
        print("Não há contribuidores inativos para adicionar.")

    subprocess.run(['open', '-a', 'Microsoft Excel', filename])
    return df_contributor

# Função para encontrar o melhor match com base na similaridade
def match_names(name, list_names):
    highest = process.extractOne(name, list_names)
    return highest[0] if highest else None

contributors_metrics = getMetricsContributorsByLinearB(fetch_linearb_data, parse_and_format_response, get_contributor_names, format_with_name_contributor)
data = extrair_dados_usuarios()
contributors_roles = pd.DataFrame(data)

# Preparar uma lista com nomes únicos para a comparação
unique_names_metrics = contributors_metrics['Contributor Name'].unique()
unique_names_roles = contributors_roles['Contributor Name'].unique()

# Criando um dicionário de correspondências
matches = {name: match_names(name, unique_names_roles) for name in unique_names_metrics}

# Mapeando os nomes no DataFrame contributors_metrics para os correspondentes mais similares
contributors_metrics['Matched Name'] = contributors_metrics['Contributor Name'].map(matches)

# Unindo as informações dos dois DataFrames
result_df = pd.merge(contributors_metrics, contributors_roles, left_on='Matched Name', right_on='Contributor Name', how='left')
result_df = result_df[['Contributor Id', 'Matched Name', 'Date','Cycle time','Cycle time (Formatted)','Total Changes', 'New Work','New Work (%)', 'Refactor', 'Refactor (%)','Rework', 'Rework (%)', 'PR Reviews', 'PR New', 'PR Merged', 'Branches Done', 'Activity Days','Username', 'Email', 'Role', 'Squad', 'Division']]
# Renomeando a coluna 'Nome' para 'Primeiro Nome'
result_df = result_df.rename(columns={'Matched Name': 'Contributor Name'})
result_df.to_excel("/Users/alexfrisoneyape/Development/EM-projects/output/contributors_metrics_roles.xlsx")
subprocess.run(['open', '-a', 'Microsoft Excel', "/Users/alexfrisoneyape/Development/EM-projects/output/contributors_metrics_roles.xlsx"])
# filename = "/Users/alexfrisoneyape/Development/EM-projects/output/contributors_roles.xlsx"
# contributors_roles.to_excel(filename)
# subprocess.run(['open', '-a', 'Microsoft Excel', filename])

# # Aplicando a função para unificar nomes no DataFrame contributors_metrics
# unique_names = contributors_roles['Contributor Name'].unique()
# contributors_metrics['Unified Contributor Name'] = contributors_metrics['Contributor Name'].apply(find_best_match, choices=unique_names)

# # Unindo os DataFrames
# merged_df = pd.merge(contributors_metrics, contributors_roles, left_on='Unified Contributor Name', right_on='Contributor Name', how='left')
# merged_df.to_excel("/Users/alexfrisoneyape/Development/EM-projects/output/contributors_metrics_roles.xlsx")
# subprocess.run(['open', '-a', 'Microsoft Excel', "/Users/alexfrisoneyape/Development/EM-projects/output/contributors_metrics_roles.xlsx"])


