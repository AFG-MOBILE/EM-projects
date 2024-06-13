import requests
from dotenv import load_dotenv
import os
import pandas as pd
import subprocess
from datetime import datetime
import commons_yape
from base64 import b64decode
import json
from datetime import datetime,timedelta

load_dotenv('.env')

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

API_KEY = "522a4cd86f769c2cd1c8b97c151e0210"
GITHUB_TOKEN = ACCESS_TOKEN
ORGANIZATION = 'yaperos'  # Substitua 'organization_name' pela sua organização
START_DATE,END_DATE = '2024-04-01', '2024-04-30'
# FILENAME = "/Users/alexfrisoneyape/Development/EM-projects/output/metrics_personas.xlsx"
FILENAME = "/Users/alexfrisoneyape/Development/EM-projects/output/equipos.xlsx"

DD_API_KEY = os.getenv('DD_API_KEY')
DD_APP_KEY = os.getenv('DD_APP_KEY')

headers_datadog = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "DD-API-KEY": DD_API_KEY,
    "DD-APPLICATION-KEY": DD_APP_KEY
}

headers_githhub = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

def fetch_teams():
    teams_url = f'https://api.github.com/orgs/{ORGANIZATION}/teams'
    response = requests.get(teams_url, headers=headers_githhub)
    if response.status_code == 200:
        teams = response.json()
        return {team['slug']: team['name'] for team in teams}
    else:
        print(f"Failed to fetch teams for organization {ORGANIZATION}: {response.status_code}")
        return {}

def fetch_team_repos(team_slug):
    repos_url = f'https://api.github.com/orgs/{ORGANIZATION}/teams/{team_slug}/repos'
    response = requests.get(repos_url, headers=headers_githhub)
    if response.status_code == 200:
        repos = response.json()
        return [repo['name'] for repo in repos]
    else:
        print(f"Failed to fetch repositories for team {team_slug} in organization {ORGANIZATION}: {response.status_code}")
        return []

def getDeploy(data_inicial, data_final, stage):

    def parse_event(event):
        short_repo_name = event.get('attributes', {}).get('attributes', {}).get('git', {}).get('repository',
                                                                                                    {}).get('name', {})
        repo_name = event.get('attributes', {}).get('attributes', {}).get('git', {}).get('repository_url', {})
        commit_sha = event.get('attributes', {}).get('attributes', {}).get('git', {}).get('commit', {}).get('sha',
                                                                                                                    'N/A')
        timestamp = event.get('attributes', {}).get('attributes', {}).get('start', 'N/A')
        status = event.get('attributes', {}).get('attributes', {}).get('github', {}).get('conclusion', 'N/A')
        pipeline = event.get('attributes', {}).get('attributes', {}).get('ci', {}).get('pipeline', {}).get('name', '')
        job_name = event.get('attributes', {}).get('attributes', {}).get('ci', {}).get('job', {}).get('name', '')
                # Converter o timestamp para um objeto datetime
        timestamp_datetime = datetime.fromtimestamp(
                    timestamp / 1000000000.0)  # Dividido por 1 bilhão para converter nanossegundos para segundos
        stage = "qa"
        if pipeline == 'Release Flow':
            if job_name == 'deploy_prd / deploy' or job_name == 'deployPRD':
                stage = "release"
            elif job_name == 'deploy_stg / deploy' or job_name == 'deploy':
                stage = "staging"
        
        release = {}
        release['Repo'] = short_repo_name.replace("yaperos/","")
        release['Stage'] = stage
        release['Commit_sha'] = commit_sha
        release['Timestamp'] = timestamp_datetime.isoformat()
        release['Status'] = status
        return release

    url = 'https://api.datadoghq.com/api/v2/ci/pipelines/events/search'
    deploys = []
    
    # QA
    query = '(@ci.job.name:"deploy / deploy" @ci.pipeline.name:"QA Flow" OR @ci.job.name:deploy @ci.pipeline.name:"QA Flow")'
    # old
    # query = 'ci_level:job (@ci.job.name:"deploy / deploy" @ci.pipeline.name:"QA Flow" OR @ci.job.name:deploy @ci.pipeline.name:"QA Flow")'
    if stage == 'staging':
        # Staging
        query = '(@ci.pipeline.name:"Release Flow" @ci.job.name:"deploy_stg / deploy" OR @ci.pipeline.name:"Release Flow" @ci.job.name:deploy)'
        # query old
        # query = 'ci_level:job (@ci.pipeline.name:"Release Flow" @ci.job.name:"deploy_stg / deploy" OR @ci.pipeline.name:"Release Flow" @ci.job.name:deploy)'
    elif stage == 'release':
        # Production
        query = '(@ci.pipeline.name:"Release Flow" @ci.job.name:"deploy_prd / deploy" OR @ci.pipeline.name:"Release Flow" @ci.job.name:deployPRD)'
        # old
        # query = 'ci_level:job (@ci.pipeline.name:"Release Flow" @ci.job.name:"deploy_prd / deploy" OR @ci.pipeline.name:"Release Flow" @ci.job.name:deployPRD)'

    # Dados JSON
    data = {
        "filter": {
            "from": data_inicial,
            "query": query,
            "to": data_final
        },
        "options": {
            "timezone": "GMT"
        },
        "page": {
            "limit": 5000
        }
    }
    # Faça a solicitação POST usando a biblioteca requests
    response = requests.post(url, data=json.dumps(data), headers=headers_datadog)
    # Verifique a resposta
    if response.status_code == 200:
        data = response.json()
        # Loop através dos eventos
        for event in data.get('data', []):
            deploy = parse_event(event)
            if deploy:
                deploys.append(deploy)
    else:
        print(f"Falha na solicitação - Código de status: {response.status_code}")
        print(response.text)
    return deploys

def fetch_releases():
    # Data de início para listar releases
    data_inicial = datetime.strptime(f'{START_DATE} 00:00:00', '%Y-%m-%d %H:%M:%S') #datetime.now()
    data_final = datetime.strptime(f'{END_DATE} 23:59:59', '%Y-%m-%d %H:%M:%S') #datetime.now()
    data_inicial_query_datadog = round(data_inicial.timestamp()) * 1000
    data_final_query_datadog = round(data_final.timestamp()) * 1000
    
    releaseQA = getDeploy(data_inicial_query_datadog,data_final_query_datadog,"qa")
    releaseStaging = getDeploy(data_inicial_query_datadog,data_final_query_datadog,"staging")
    releaseProduction = getDeploy(data_inicial_query_datadog,data_final_query_datadog,"production")
    release = releaseQA + releaseStaging + releaseProduction

    df_release = pd.DataFrame(release)
    # Filtrando os deploys com status "success"
    # df_release_successful = df_release[df_release['status'] == 'success']
    
    # return df_release_successful
    return df_release

def fetch_teams_with_repos():
    teams = fetch_teams()
    team_repos = []
    team_repos_dict = {}
    for slug, name in teams.items():
        repos = fetch_team_repos(slug)
        team_repos_dict[name] = repos
        for repo in repos:
            team_repos.append({
                "Team":name,
                "Repo":repo
            })
    df_metrics_teams = pd.DataFrame(team_repos)
    return df_metrics_teams

def fetch_linearB():

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

    # URL da API
    url = "https://public-api.linearb.io/api/v2/measurements"
    
    # Cabeçalhos necessários para a requisição
    headers = {
        "x-api-key": API_KEY
    }
    time_ranges = split_period_by_month(START_DATE, END_DATE)
    # Parâmetros do corpo da requisição
    payload = {
      "group_by": "team",
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
    print(response)
    exit()
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


def getMetricsTeams():
    # 1. Obtendo os times no github com os seus repositorios
    df_teams_with_repos = fetch_teams_with_repos()

    # 2. Obtendo deploys
    df_metrics_teams = fetch_releases()

    # 3. Obbtendo cycle time y workbreakddown
    df_metrics_linearb = fetch_linearB()

    df_teams_with_repos.to_excel(FILENAME, sheet_name="Teams Repos", index=False)
    with pd.ExcelWriter(FILENAME, engine='openpyxl', mode='a') as writer:
        df_metrics_teams.to_excel(writer, sheet_name="Deploys por Repos", index=False)
        df_metrics_linearb.to_excel(writer, sheet_name="LinearB Metrics", index=False)
    subprocess.run(['open', '-a', 'Microsoft Excel', FILENAME])

# getMetricsTeams()

# • Repos por Releases
# • Repos por Team
# • Linearb por Team

fetch_linearB()