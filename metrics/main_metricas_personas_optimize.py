from types import NoneType
import requests
from dotenv import load_dotenv
import os
import pandas as pd
import subprocess
from datetime import datetime,timedelta
import commons_yape
from github import Github
import re
from base64 import b64decode
import difflib
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from fuzzywuzzy import process, fuzz

# from metrics.trello import TOKEN

load_dotenv('.env')

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

API_KEY = "522a4cd86f769c2cd1c8b97c151e0210"
GITHUB_TOKEN = ACCESS_TOKEN
ORGANIZATION = 'yaperos'  # Substitua 'organization_name' pela sua organização
START_DATE,END_DATE = '2024-01-01', '2024-05-31'
# FILENAME = "/Users/alexfrisoneyape/Development/EM-projects/output/metrics_personas.xlsx"
FILENAME = "/Users/alexfrisoneyape/Development/EM-projects/output/personas.xlsx"
FILENAME_TEMP = "/Users/alexfrisoneyape/Development/EM-projects/output/personas_temp.xlsx"
FILENAME_OLD = "/Users/alexfrisoneyape/Development/EM-projects/output/personas-jan_a_maio.xlsx"
FILENAME_BASE_CONTRIBUTORS = "/Users/alexfrisoneyape/Development/EM-projects/output/Base de colaboradores.xlsx"
# TEAMS = ['marketplace', 'insurance'] 

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
    #   "roll_up": "custom",
      "roll_up": "1mo",
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
        {"after": f'{START_DATE}', "before": f'{END_DATE}'}
      ]
    }
    
    # Fazer a requisição e retornar a resposta
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def split_period_by_month(start_date, end_date):
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    periods = []
    
    current = start
    while current <= end:
        month_end = (current + pd.offsets.MonthEnd(0))
        if month_end > end:
            month_end = end
        
        periods.append({
            "after": current.strftime('%Y-%m-%d'),
            "before": month_end.strftime('%Y-%m-%d')
        })
        
        current = month_end + timedelta(days=1)
    
    return periods

def getMetricsContributorsByLinearB():
    # URL da API
    url = "https://public-api.linearb.io/api/v2/measurements"
    
    # Cabeçalhos necessários para a requisição
    headers = {
        "x-api-key": API_KEY
    }
    time_ranges = split_period_by_month(START_DATE, END_DATE)
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
      "time_ranges": time_ranges
    }
    
    # Fazer a requisição e retornar a resposta
    response = requests.post(url, json=payload, headers=headers).json()
    
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
    
    headers = {"x-api-key": API_KEY}
    teams_url = "https://public-api.linearb.io/api/v1/teams?nonmerged_members_only=false"
    
    response = requests.get(teams_url, headers=headers)
    contributors_dict = {}
    
    teams_contributors_formatted_data = []
    if response.status_code == 200:
        teams_data = response.json()
        for item in teams_data.get("items", []):
            print(f"team:{item['name']}")
            for contributor in item.get("contributors", []):
                print(contributor)
                
                contributors_dict[contributor["id"]] = contributor["name"]
                formatted_record = {
                    "Team":item['name'],
                    "Contributor Name":contributor["name"]
                }
                teams_contributors_formatted_data.append(formatted_record)
    
    metrics_formatted_data = []

    # Iterar sobre cada registro na resposta das métricas
    for record in formatted_data:
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
            
            metrics_formatted_data.append(formatted_record)

    return metrics_formatted_data, teams_contributors_formatted_data

def get_team_members(organization):
    
    def fetch_teams():
        teams_url = f'https://api.github.com/orgs/{organization}/teams'
        response = requests.get(teams_url, headers=headers)
        if response.status_code == 200:
            teams = response.json()
            return [team['slug'] for team in teams],{team['slug']: team['name'] for team in teams}
        else:
            print(f"Failed to fetch teams for organization {organization}: {response.status_code}")
            return [],{}

    def fetch_team_members(team):
        team_members_url = f'https://api.github.com/orgs/{organization}/teams/{team}/members'
        response = requests.get(team_members_url, headers=headers)
        if response.status_code == 200:
            members = response.json()
            return [member['login'] for member in members]
        else:
            print(f"Failed to fetch members for team {team}: {response.status_code}")
            return []

    all_teams, all_teams_dict = fetch_teams()
    all_members = []
    team_members_dict = []

    for team_slug, team_name in all_teams_dict.items():
        members = fetch_team_members(team_slug)
        all_members.extend(members)
        team_members_dict.extend([{"Username": member, "Team": team_name} for member in members])

    return all_members, team_members_dict

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

def find_best_match(name, name_list, threshold=85):
    # Remover valores NaN da lista de nomes
    if (name is None or name is NoneType):
        return None, 0
    name_list = [str(n) for n in name_list if isinstance(n, str)]
    if isinstance(name, float):  # Verificar se o nome é um float e convertê-lo para string
        name = str(name)
    best_match, best_score = process.extractOne(name, name_list, scorer=fuzz.token_sort_ratio)
    return best_match if best_score >= threshold else None, best_score

def list_contributor_activities(username, start_date, end_date):
    

    def fetch_prs(query):
        url = f'https://api.github.com/search/issues?q={query}'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('items', [])
        else:
            print(f"Failed to fetch PRs: {response.status_code} - {response.reason}")
            return []

    def fetch_pr_details(url):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch PR details: {response.status_code} - {response.reason}")
            return None

    def fetch_pr_reviews(url):
        reviews_url = f'{url}/reviews'
        response = requests.get(reviews_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch PR reviews: {response.status_code} - {response.reason}")
            return []
        
    def format_date(date_str):
        if date_str:
            data_objeto = datetime.strptime(date_str[:-1], "%Y-%m-%dT%H:%M:%S")
            return data_objeto.strftime("%Y-%m-%d")
        else:
            return ""

    def is_within_date_range(date_str, start_date, end_date):
        date_obj = datetime.strptime(date_str[:-1], "%Y-%m-%dT%H:%M:%S")
        return start_date <= date_obj <= end_date

    activities = {}
    
    # PRs created by the user
    created_query = f'author:{username} type:pr created:{start_date}..{end_date}'
    created_prs = fetch_prs(created_query)
    
    # PRs merged by the user
    merged_query = f'author:{username} is:pr merged:{start_date}..{end_date}'
    merged_prs = fetch_prs(merged_query)
    
    # PRs reviewed by the user
    reviewed_query = f'reviewed-by:{username} type:pr'
    reviewed_prs = fetch_prs(reviewed_query)

    def add_to_activities(pr, pr_details, activity_type, activity_date):
        repo_name = pr['repository_url'].split('/')[-1]
        url = pr['pull_request']['url']
        url = url.replace("https://api.github.com/repos","https://github.com").replace("pulls","pull")

        pr_additions = pr_details.get('additions', 0)
        pr_deletions = pr_details.get('deletions', 0)
        pr_labels = [label['name'] for label in pr_details.get('labels', [])]

        pr_creation_date = ""
        pr_merged_at = ""
        pr_reviewed_at = ""
        pr_closed_at = ""
        if pr_details.get('closed_at') is not None:
            pr_closed_at = format_date(pr_details['closed_at'])

        if activity_type == "PR Reviewed":
            pr_reviewed_at = activity_date
        elif activity_type == "PR Merged":
            pr_merged_at = activity_date
        elif activity_type == "PR Created":
            pr_creation_date = activity_date
        
        if repo_name not in activities:
            activities[repo_name] = []

        
        activities[repo_name].append({
            'Repo': repo_name,
            'Author': pr_details['user']['login'],
            'PR Title': pr['title'],
            'Additions': pr_additions,
            'Deletions': pr_deletions,
            'Labels': pr_labels,
            'Activity Date': activity_date,
            'Creation Date': pr_creation_date,
            'Merged Date': pr_merged_at,
            'Reviewed Date': pr_reviewed_at,
            'Close Date': pr_closed_at,
            'URL': url,
            'Activity Type': activity_type
        })

    active_contributors = set()

    # Process created PRs
    for pr in tqdm(created_prs, desc="Processing created PRs"):
        pr_details = fetch_pr_details(pr['pull_request']['url'])
        if pr_details:
            activity_date = format_date(pr['created_at'])
            add_to_activities(pr, pr_details, 'PR Created', activity_date)
            active_contributors.add(pr_details['user']['login'])
    
    # Process merged PRs
    for pr in tqdm(merged_prs, desc="Processing merged PRs"):
        pr_details = fetch_pr_details(pr['pull_request']['url'])
        if pr_details:
            activity_date = format_date(pr_details.get('merged_at'))
            add_to_activities(pr, pr_details, 'PR Merged', activity_date)
            active_contributors.add(pr_details['user']['login'])
    
    # Process reviewed PRs
    for pr in tqdm(reviewed_prs, desc="Processing reviewed PRs"):
        pr_details = fetch_pr_details(pr['pull_request']['url'])
        if pr_details:
            reviews = fetch_pr_reviews(pr['pull_request']['url'])
            for review in reviews:
                if review.get('user') and review.get('submitted_at') and review['user'].get('login') == username and is_within_date_range(review.get('submitted_at'), datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d")):
                    activity_date = format_date(review.get('submitted_at'))
                    add_to_activities(pr, pr_details, 'PR Reviewed', activity_date)
                    active_contributors.add(review['user']['login'])
                    break


    return activities

def get_personas_metrics():
    # 1. Obtendo os membros do time e o dicionario de times com os seus membros
    team_members, team_members_data  = get_team_members(ORGANIZATION)
    
    # 2. Obtendo as metricas do linearB
    data_metrics_linearb, data_teams_contributors = getMetricsContributorsByLinearB()

    data = []
    data_members = []
    # 4. Verificando cada membro do time
    count = 0
    for member in team_members:
        count = count + 1
        # 5. Obtendo dados o nome completo do usuario no github
        response = requests.get(f'https://api.github.com/users/{member}', headers=headers)
        user_info = response.json()
        fullname = user_info.get('name', 'Not available')
        
        created_at = None
        if user_info.get('created_at'):
            created_at = datetime.strptime(user_info.get('created_at')[:-1], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
        
        updated_at = None
        if user_info.get('updated_at'):
            updated_at = datetime.strptime(user_info.get('updated_at')[:-1], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
        
        data_members.append({
            "Username":member,
            "Fullname":fullname,
            "Created":created_at,
            "Last Access":updated_at
        })

        print(f"Activities for {member}:")
        hasActivities = False
        activities = list_contributor_activities(member, START_DATE,END_DATE)
        for repo, prs in activities.items():
            # print(f'Repository: {repo}')
            for pr in prs:
                hasActivities = True
                data.append({
                            'Activity Date': pr['Activity Date'],
                            "Creation Date":pr['Creation Date'],
                            "Username":member,
                            "Fullname":fullname,
                            "Repo": repo,
                            "PR Title":pr['PR Title'],
                            "Labels":pr['Labels'],
                            "Additions":pr['Additions'],
                            "Deletions":pr['Deletions'],
                            "Merged Date":pr['Merged Date'],
                            "URL":pr['URL'],
                            "Author Pull request":pr['Author'],
                            'Reviewed Date': pr['Reviewed Date'],
                            'Close Date': pr['Close Date'],
                            'Activity Type': pr['Activity Type']
            })
                
        if (hasActivities == False):
            data.append({
                            'Activity Date': END_DATE,
                            "Creation Date":None,
                            "Username":member,
                            "Fullname":fullname,
                            "Repo": None,
                            "PR Title":None,
                            "Labels":None,
                            "Additions":None,
                            "Deletions":None,
                            "Merged Date":None,
                            "URL":None,
                            "Author Pull request":None,
                            'Reviewed Date': None,
                            'Close Date': None,
                            'Activity Type': 'No Activity'
            })
        

    metrics_personas = pd.DataFrame(data)
    metrics_personas.rename(columns={'Fullname': 'Contributor Name'}, inplace=True)
    metrics_members_personas = pd.DataFrame(data_members)
    metrics_team_members_personas = pd.DataFrame(team_members_data)
    metrics_members_personas.rename(columns={'Fullname': 'Contributor Name'}, inplace=True)
    metrics_linearb_personas = pd.DataFrame(data_metrics_linearb)
    
    # Converter as datas para um formato consistente (ano-mês)
    metrics_personas['Date'] = pd.to_datetime(metrics_personas['Activity Date']).dt.to_period('M')
    metrics_linearb_personas['Date'] = pd.to_datetime(metrics_linearb_personas['Date']).dt.to_period('M')

    # Unificar os dados com base em 'Creation Date' e 'Contributor Name'
    merged_data = pd.merge(metrics_personas, metrics_linearb_personas, how='left', on=['Date', 'Contributor Name'])

    # Obtendo os dados dos contributors obtido pelo Ruben
    df_details_contributors = pd.read_excel(FILENAME_BASE_CONTRIBUTORS, sheet_name='Hoja2')

    # Adicionar colunas de correspondência e similaridade no dataframe de colaboradores
    metrics_members_personas['Correspondência'] = None
    metrics_members_personas['Similaridade'] = 0

    # Lista de nomes completos na planilha
    names_planilha = df_details_contributors['NOMBRE COMPLETO'].tolist()

    # Encontrar correspondências
    for index, row in metrics_members_personas.iterrows():
        best_match, similarity = find_best_match(row['Contributor Name'], names_planilha)
        metrics_members_personas.at[index, 'Contributor Name Match'] = best_match
        metrics_members_personas.at[index, 'Similaridade'] = similarity

    # Merge dos dados
    df_merge = pd.merge(metrics_members_personas, df_details_contributors, left_on='Contributor Name Match', right_on='NOMBRE COMPLETO', how='left')
    
    merged_data.to_excel(FILENAME, sheet_name="General", index=False)
    with pd.ExcelWriter(FILENAME, engine='openpyxl', mode='a') as writer:
        metrics_linearb_personas.to_excel(writer, sheet_name="LinearB Metrics", index=False)
        metrics_team_members_personas.to_excel(writer, sheet_name="Teams Contributors", index=False)
        df_merge.to_excel(writer, sheet_name='Contributors', index=False)
    subprocess.run(['open', '-a', 'Microsoft Excel', FILENAME])

start_time = time.time()
get_personas_metrics()
end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time:.2f} seconds")