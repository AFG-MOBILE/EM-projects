import json
from datetime import datetime
import requests
import github_yape
import timer_metrics
import concurrent.futures
import functools
import cache_yape
from dotenv import load_dotenv
import os

load_dotenv('.env')

# Substitua com suas chaves de API do Datadog
DD_API_KEY = os.getenv('DD_API_KEY')
DD_APP_KEY = os.getenv('DD_APP_KEY')

# URL da API do Datadog
url = 'https://api.datadoghq.com/api/v2/ci/pipelines/events/search'

# Cabeçalhos
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "DD-API-KEY": DD_API_KEY,
    "DD-APPLICATION-KEY": DD_APP_KEY
}

@cache_yape.daily_cache_clear
@functools.lru_cache(maxsize=None)
def getReleasesQA(data_inicial, data_final):
    releases = []
    
    query = 'ci_level:job (@ci.job.name:"deploy / deploy" @ci.pipeline.name:"QA Flow" OR @ci.job.name:deploy @ci.pipeline.name:"QA Flow")'

    # Dados JSON
    data = {
        "filter": {
            # "from": "now-1y",
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
    print(f"datadog: {data}")
    # Faça a solicitação POST usando a biblioteca requests
    response = requests.post(url, data=json.dumps(data), headers=headers)
    # Verifique a resposta
    if response.status_code == 200:
        data = response.json()
        # Loop através dos eventos
        for event in data.get('data', []):
            release = parse_event(event)
            if release:
                releases.append(release)
    else:
        print(f"Falha na solicitação - Código de status: {response.status_code}")
        print(response.text)
    return releases

@cache_yape.daily_cache_clear
@functools.lru_cache(maxsize=None)
def getReleasesStaging(data_inicial, data_final):
    releases = []
    query = 'ci_level:job (@ci.pipeline.name:"Release Flow" @ci.job.name:"deploy_stg / deploy" OR @ci.pipeline.name:"Release Flow" @ci.job.name:deploy)'

    # Dados JSON
    data = {
        "filter": {
            # "from": "now-1y",
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
    print(f"datadog: {data}")
    # Faça a solicitação POST usando a biblioteca requests
    response = requests.post(url, data=json.dumps(data), headers=headers)
    # Verifique a resposta
    if response.status_code == 200:
        data = response.json()
        # Loop através dos eventos
        for event in data.get('data', []):
            release = parse_event(event)
            if release:
                releases.append(release)
    else:
        print(f"Falha na solicitação - Código de status: {response.status_code}")
        print(response.text)
    return releases

@cache_yape.daily_cache_clear
@functools.lru_cache(maxsize=None)
def getReleasesProduction(data_inicial, data_final):
    releases = []
    query = 'ci_level:job (@ci.pipeline.name:"Release Flow" @ci.job.name:"deploy_prd / deploy" OR @ci.pipeline.name:"Release Flow" @ci.job.name:deployPRD)'
    
    # Dados JSON
    data = {
        "filter": {
            # "from": "now-1y",
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
    print(f"datadog: {data}")
    # Faça a solicitação POST usando a biblioteca requests
    response = requests.post(url, data=json.dumps(data), headers=headers)
    # Verifique a resposta
    if response.status_code == 200:
        data = response.json()
        # Loop através dos eventos
        for event in data.get('data', []):
            release = parse_event(event)
            if release:
                releases.append(release)
    else:
        print(f"Falha na solicitação - Código de status: {response.status_code}")
        print(response.text)
    return releases

@cache_yape.daily_cache_clear
@timer_metrics.timer_decorator
@functools.lru_cache(maxsize=None)
def getAllReleases(data_inicial, data_final):
    releases = []
    
    # URL da API do Datadog
    url = 'https://api.datadoghq.com/api/v2/ci/pipelines/events/search'

    # query = 'ci_level:job (@ci.pipeline.name:"Release Flow" @ci.job.name:"deploy_prd / deploy" OR @ci.pipeline.name:"Release Flow" @ci.job.name:deployPRD OR @ci.pipeline.name:"Release Flow" @ci.job.name:"deploy_stg / deploy" OR @ci.pipeline.name:"Release Flow" @ci.job.name:deploy OR @ci.job.name:"deploy / deploy" @ci.pipeline.name:"QA Flow" OR @ci.job.name:deploy @ci.pipeline.name:"QA Flow")'
    query = '(@ci.pipeline.name:"Release Flow" @ci.job.name:"deploy_prd / deploy" OR @ci.pipeline.name:"Release Flow" @ci.job.name:deployPRD OR @ci.pipeline.name:"Release Flow" @ci.job.name:"deploy_stg / deploy" OR @ci.pipeline.name:"Release Flow" @ci.job.name:deploy OR @ci.job.name:"deploy / deploy" @ci.pipeline.name:"QA Flow" OR @ci.job.name:deploy @ci.pipeline.name:"QA Flow")'
    # Cabeçalhos
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "DD-API-KEY": DD_API_KEY,
        "DD-APPLICATION-KEY": DD_APP_KEY
    }
    # Dados JSON
    data = {
        "filter": {
            # "from": "now-1y",
            "from": data_inicial,
            "query": query,
            "to": data_final
        },
        "options": {
            "timezone": "GMT"
        },
        "page": {
            "limit": 50000
        }
    }
    
    # Faça a solicitação POST usando a biblioteca requests
    response = requests.post(url, data=json.dumps(data), headers=headers)
    # Verifique a resposta
    if response.status_code == 200:
        data = response.json()
        # Usando um ThreadPoolExecutor para executar a função parse_file em vários arquivos simultaneamente
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(parse_event, data.get('data', [])))

        for result in results:
            releases.append(result)

    else:
        print(f"Falha na solicitação - Código de status: {response.status_code}")
        print(response.text)
    return releases

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
    owner = github_yape.get_owner_from_codeowners(short_repo_name)
    if owner == 'Depreciado/Sem Owner':
        return False
    
    release = {}
    release['repo_name'] = repo_name
    release['stage'] = stage
    release['commit_sha'] = commit_sha
    release['timestamp'] = timestamp_datetime.isoformat()
    release['owner'] = owner
    release['status'] = status
    return release

