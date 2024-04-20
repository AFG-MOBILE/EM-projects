import requests
from dotenv import load_dotenv
import os
import pandas as pd
import subprocess
from datetime import datetime
import commons_yape
from github import Github
import re
from base64 import b64decode
import difflib

load_dotenv('.env')

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

API_KEY = "522a4cd86f769c2cd1c8b97c151e0210"
GITHUB_TOKEN = ACCESS_TOKEN
ORGANIZATION = 'yaperos'  # Substitua 'organization_name' pela sua organização
START_DATE,END_DATE = '2024-03-01', '2024-03-31'
FILENAME = "/Users/alexfrisoneyape/Development/EM-projects/output/metrics_personas.xlsx"

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

def match_names(nome, lista_nomes):
    matches = []
    
    # Itera sobre todos os nomes na lista
    for candidate_name in lista_nomes:
        # Calcula a similaridade entre os nomes
        similarity_ratio = difflib.SequenceMatcher(None, nome, candidate_name).ratio()
        
        # Verifica se a similaridade é maior ou igual a 0.6 e se existem pelo menos 2 palavras muito semelhantes
        if similarity_ratio >= 0.6 and sum(1 for word in nome.split() if word in candidate_name.split()) >= 1:
            matches.append((candidate_name, similarity_ratio))
    
    # Retorna o nome com o maior nível de semelhança
    if matches:
        return max(matches, key=lambda x: x[1])
    else:
        return None, None

def find_similar_names(contributors_metrics, contributors_roles):
    similar_names = []
    similarity_levels = []

    for index, row in contributors_metrics.iterrows():
        nome = row['Contributor Name']
        lista_nomes = contributors_roles['Contributor Name'].tolist()

        melhor_nome, nivel_similaridade = match_names(nome, lista_nomes)
        if melhor_nome is not None:
            print(f"O nome mais semelhante a '{nome}' é '{melhor_nome}' com nível de similaridade de {nivel_similaridade:.2f}.")
            similar_names.append(melhor_nome)
            similarity_levels.append(nivel_similaridade)
        else:
            print(f"Nenhum nome semelhante encontrado para '{nome}'. Removendo a linha do DataFrame.")
            contributors_metrics.drop(index, inplace=True)
        
    contributors_metrics['Best Match Name'] = similar_names
    contributors_metrics['Similarity Level'] = similarity_levels


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
                "Date": record.get("date", "N/A"),  # Ajusta o formato da data para mm/yyyy
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

def parse_and_format_response(response):
    # Estrutura para armazenar os dados formatados
    formatted_data = []
    
    # Iterar sobre os períodos na resposta
    for period in response:
        # Iterar sobre as métricas para cada contribuidor
        for metric in period["metrics"]:

            data_objeto = datetime.strptime(period["after"], "%Y-%m-%d")
            data_formatada = data_objeto.strftime("%Y-%m")
            # Preparar o registro com a data formatada
            metric_data = {"date": data_formatada}
            
            # Extrair métricas relevantes
            relevant_metrics = ["contributor_id","branch.computed.cycle_time:avg", "commit.activity.new_work.count", "commit.total_changes", "commit.activity.refactor.count", "commit.activity.rework.count", "pr.reviews", "pr.new", "pr.merged", "branch.state.computed.done","commit.activity_days"]
            for key in relevant_metrics:
                if key in metric:
                    metric_data[key] = metric[key]
            
            # Adicionar o registro formatado à lista
            formatted_data.append(metric_data)
    
    return formatted_data


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
        {"after": "2024-03-01", "before": "2024-03-31"}
      ]
    }
    
    # Fazer a requisição e retornar a resposta
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def getMetricsContributorsByLinearB(fetch_linearb_data, parse_and_format_response, get_contributor_names, format_with_name_contributor):
    response = fetch_linearb_data()  # Descomente esta linha para fazer a requisição real
    formatted_data = parse_and_format_response(response)  # Use a resposta real aqui

    contributor_names = get_contributor_names()

    contributor_data = format_with_name_contributor(formatted_data, contributor_names)
    return contributor_data

def getInfoUser(username):
    response = requests.get(f'https://api.github.com/users/{username}', headers=headers)
    user_info = response.json()
    fullname = user_info.get('name', 'Not available')
    print(f"User Full Name: {fullname}")
    return fullname

def get_teams():
    response = requests.get(f'https://api.github.com/orgs/{ORGANIZATION}/teams', headers=headers)
    teams = response.json()
    print(teams)
    for team in teams:
        print(f"Team Name: {team['name']}, Team ID: {team['id']}")

def get_team_members(organization):
    team_members_url = f'https://api.github.com/orgs/{organization}/teams/marketplace/members'
    response = requests.get(team_members_url, headers=headers)
    members = response.json()
    members_login = [member['login'] for member in members]
    print(f"marketplace: {members}")
    team_members_url = f'https://api.github.com/orgs/{organization}/teams/insurance/members'
    response = requests.get(team_members_url, headers=headers)
    members = response.json()
    for member in members:
        members_login.append(member['login'])

    print(f"marketplace & insurance: {members}")
    return members_login

def get_user_reviews(username,start_date,end_date):
    query = f'is:pr reviewed-by:{username} created:{start_date}..{end_date}'
    url = f'https://api.github.com/search/issues?q={query}'

    response = requests.get(url, headers=headers)
    repos_prs = response.json().get('items', [])

    activities = {}
    
    for pr in repos_prs:
        repo_name = pr['repository_url'].split('/')[-1]
        pr_details_response = requests.get(pr['pull_request']['url'], headers=headers)
        pr_details = pr_details_response.json()
        
        data_objeto = datetime.strptime(pr_details['created_at'][:-1], "%Y-%m-%dT%H:%M:%S")
        pr_creation_date = data_objeto.strftime("%Y-%m-%d")
        if (pr_details['merged_at']):
            data_objeto = datetime.strptime(pr_details['merged_at'][:-1], "%Y-%m-%dT%H:%M:%S")
            pr_merged_at = data_objeto.strftime("%Y-%m-%d")
        else:
            pr_merged_at = ""

        if (pr_details['closed_at']):
            data_objeto = datetime.strptime(pr_details['closed_at'][:-1], "%Y-%m-%dT%H:%M:%S")
            pr_closed_at = data_objeto.strftime("%Y-%m-%d")
        else:
            pr_closed_at = ""  
        
        author = pr_details['user']['login']
        
        if repo_name not in activities:
            activities[repo_name] = []
        activities[repo_name].append({
            'Repo':repo_name,
            'Author':author,
            'PR Title': pr['title'],
            'Creation Date':pr_creation_date,
            'Merged Date': pr_merged_at,
            'Close Date': pr_closed_at,
            'URL':pr['pull_request']['url']
        })
    
    return activities

def list_contributor_activities(username, start_date, end_date):
    query = f'author:{username} type:pr created:{start_date}..{end_date}'
    repos_response = requests.get(f'https://api.github.com/search/issues?q={query}', headers=headers)
    repos_prs = repos_response.json().get('items', [])

    activities = {}
    
    for pr in repos_prs:
        repo_name = pr['repository_url'].split('/')[-1]
        pr_details_response = requests.get(pr['pull_request']['url'], headers=headers)
        pr_details = pr_details_response.json()
        
        pr_size = pr_details['additions'] + pr_details['deletions']
        pr_additions = pr_details['additions']  # Quantidade de linhas adicionadas
        pr_deletions = pr_details['deletions']  # Quantidade de linhas removidas

        data_objeto = datetime.strptime(pr_details['created_at'][:-1], "%Y-%m-%dT%H:%M:%S")
        pr_creation_date = data_objeto.strftime("%Y-%m-%d")
        if (pr_details['merged_at']):
            data_objeto = datetime.strptime(pr_details['merged_at'][:-1], "%Y-%m-%dT%H:%M:%S")
            pr_merged_at = data_objeto.strftime("%Y-%m-%d")
        else:
            pr_merged_at = ""

        if (pr_details['closed_at']):
            data_objeto = datetime.strptime(pr_details['closed_at'][:-1], "%Y-%m-%dT%H:%M:%S")
            pr_closed_at = data_objeto.strftime("%Y-%m-%d")
        else:
            pr_closed_at = ""  
        
        if repo_name not in activities:
            activities[repo_name] = []
        activities[repo_name].append({
            'Repo':repo_name,
            'Author':pr_details['user']['login'],
            'PR Title': pr['title'],
            'Additions': pr_additions,
            'Deletions': pr_deletions,
            'Creation Date':pr_creation_date,
            'Merged Date': pr_merged_at,
            'Close Date': pr_closed_at,
            'URL':pr['pull_request']['url']
        })
    
    return activities

# get_teams()
# exit()
def get_personas_metrics(ORGANIZATION, START_DATE, END_DATE, FILENAME, find_similar_names, extrair_dados_usuarios, format_with_name_contributor, get_contributor_names, parse_and_format_response, fetch_linearb_data, getMetricsContributorsByLinearB, getInfoUser, get_team_members, get_user_reviews, list_contributor_activities):
    team_members = get_team_members(ORGANIZATION)
    
    data_metrics_linearb = getMetricsContributorsByLinearB(fetch_linearb_data, parse_and_format_response, get_contributor_names, format_with_name_contributor)
    data_roles = extrair_dados_usuarios()

    data = []
    data_reviews = []
    data_members = []
    for member in team_members:
        fullname = getInfoUser(member)

        data_members.append({
        "Username":member,
        "Fullname":fullname
    })
        print(f"Activities for {member}:")
        activities = list_contributor_activities(member, START_DATE,END_DATE)
        for repo, prs in activities.items():
            print(f'Repository: {repo}')
            for pr in prs:
                data.append({
                            "Creation Date":pr['Creation Date'],
                            "Username":member,
                            "Fullname":fullname,
                            "Repo": repo,
                            "PR Title":pr['PR Title'],
                            "Additions":pr['Additions'],
                            "Deletions":pr['Deletions'],
                            "Merged Date":pr['Merged Date'],
                            "URL":pr['URL'],
                            "Type": "PR Created",
                            "Author Pull request":pr['Author']
            })
        print(f"Reviews by {member}:")
        reviews = get_user_reviews(member, START_DATE,END_DATE)
        for repo, prs in reviews.items():
            print(f'Repository: {repo}')
            for pr in prs:
                data.append({
                            "Creation Date":pr['Creation Date'],
                            "Username":member,
                            "Fullname":fullname,
                            "Repo": pr['Repo'],
                            "PR Title":pr['PR Title'],
                            "Additions":"",
                            "Deletions":"",
                            "Merged Date":"",
                            "URL":pr['URL'],
                            "Type": "PR Reviewed",
                            "Author Pull request":pr['Author'],

            })
        print("\n")  # Adiciona uma linha vazia entre cada membro para melhor leitura



    metrics_personas = pd.DataFrame(data)
    metrics_personas.rename(columns={'Fullname': 'Contributor Name'}, inplace=True)
    metrics_reviews_personas = pd.DataFrame(data_reviews)
    metrics_reviews_personas.rename(columns={'Fullname': 'Contributor Name'}, inplace=True)
    metrics_members_personas = pd.DataFrame(data_members)
    metrics_members_personas.rename(columns={'Fullname': 'Contributor Name'}, inplace=True)
    metrics_linearb_personas = pd.DataFrame(data_metrics_linearb)
    metrics_contributors_roles = pd.DataFrame(data_roles)

    find_similar_names(metrics_personas,metrics_contributors_roles)
    find_similar_names(metrics_reviews_personas,metrics_contributors_roles)
    find_similar_names(metrics_members_personas,metrics_contributors_roles)
    find_similar_names(metrics_linearb_personas,metrics_contributors_roles)

    metrics_merged_contributors_roles = pd.merge(metrics_members_personas, metrics_contributors_roles, left_on='Best Match Name', right_on='Contributor Name', how='left')

    metrics_personas.to_excel(FILENAME, sheet_name="Contributors PR's", index=False)
    with pd.ExcelWriter(FILENAME, engine='openpyxl', mode='a') as writer:
        metrics_linearb_personas.to_excel(writer, sheet_name="Contributors LinearB", index=False)
        # metrics_reviews_personas.to_excel(writer, sheet_name="Contributors Reviews", index=False)
        metrics_merged_contributors_roles.to_excel(writer, sheet_name="Contributors", index=False)
        # metrics_contributors_roles.to_excel(writer, sheet_name="Contributors Roles", index=False)
    subprocess.run(['open', '-a', 'Microsoft Excel', FILENAME])

get_personas_metrics(ORGANIZATION, START_DATE, END_DATE, FILENAME, find_similar_names, extrair_dados_usuarios, format_with_name_contributor, get_contributor_names, parse_and_format_response, fetch_linearb_data, getMetricsContributorsByLinearB, getInfoUser, get_team_members, get_user_reviews, list_contributor_activities)
