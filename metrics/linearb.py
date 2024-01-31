import requests
import metric_log
import github_yape
import functools
import cache_yape
import commons_yape
from dotenv import load_dotenv
import os

@cache_yape.daily_cache_clear
@functools.lru_cache(maxsize=None)
def execute_linearb_post(repo, stage, tag_name, timestamp, owner):
    
    API_URL = 'https://public-api.linearb.io/api/v1/deployments'
    API_KEY = os.getenv('API_KEY')
    services = []
    services.append(owner)
    data = {
        "repo_url": repo,
        "ref_name": tag_name,
        "timestamp": timestamp,
        "stage": stage,
        "services": services
    }

    headers = {
        'accept': 'application/json',
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.post(API_URL, json=data, headers=headers)
    if response.status_code != 200:
        metric_log.log_critical(f"Falha na solicitação - Código de status: {response.status_code} - request data:{data} - response:{response.text}")
        print(f"Falha na solicitação - Código de status: {response.status_code} - request data:{data} - response:{response.text}")
        return False
    return True

@cache_yape.daily_cache_clear
@functools.lru_cache(maxsize=None)
def get_repositories_into_services():
    unique_repositories = set()

    url = 'https://public-api.linearb.io/api/v1/services/'
    
    # Chave de API
    API_KEY = os.getenv('API_KEY')
    # Cabeçalhos
    headers = {
        'accept': 'application/json',
        'x-api-key': API_KEY
    }

    # Faça a solicitação GET
    response = requests.get(url, headers=headers)
    # Verifique a resposta
    if response.status_code == 200:
        data = response.json()
        items = data['items']
        for item in items:
            paths = item['paths']

            for path in paths:
                path_name = path['name']
                unique_repositories.add(path_name)
    else:
        print(f"Falha na solicitação - Código de status: {response.status_code}")
        print(response.text)
    return unique_repositories

def get_repositories_with_ids():
    respositories = {}

    url = 'https://public-api.linearb.io/api/v1/services/'
    
    # Chave de API
    API_KEY = os.getenv('API_KEY')
    # Cabeçalhos
    headers = {
        'accept': 'application/json',
        'x-api-key': API_KEY
    }

    # Faça a solicitação GET
    response = requests.get(url, headers=headers)
    # Verifique a resposta
    if response.status_code == 200:
        data = response.json()
        items = data['items']
        for item in items:
            paths = item['paths']

            for path in paths:
                print(path)
                path_name = path['name']
                path_id = path['id']
                respositories[path_id] = path_name
    else:
        print(f"Falha na solicitação - Código de status: {response.status_code}")
        print(response.text)
    return respositories

def check_repositories_in_linearb(all_repositories):
    repositories_without_services = []
    # Verifica se os itens de all_repositories estão em unique_repositories
    for repo in all_repositories:
        repo_name = repo.name
        if repo_name not in get_repositories_into_services():
            owner = github_yape.get_owner_from_codeowners(repo_name)
            repositories_without_services.append(f"{repo_name}")
    return repositories_without_services

# def getRepositoriesWithOwners():
@cache_yape.daily_cache_clear
@functools.lru_cache(maxsize=None)
def getRepositoriesWithOwners():
    reposWithOwners = {}

    url = 'https://public-api.linearb.io/api/v1/services/'
    
    # Chave de API
    API_KEY = os.getenv('API_KEY')
    # Cabeçalhos
    headers = {
        'accept': 'application/json',
        'x-api-key': API_KEY
    }

    # Faça a solicitação GET
    response = requests.get(url, headers=headers)
    # Verifique a resposta
    if response.status_code == 200:
        data = response.json()
        # print(data)
        items = data['items']
        for item in items:
            paths = item['paths']

            for path in paths:
                path_name = path['name']
                reposWithOwners[path_name] = item['name']
                # unique_repositories.add(path_name)
    else:
        print(f"Falha na solicitação - Código de status: {response.status_code}")
        print(response.text)
        return False
    return reposWithOwners  

def get_owner_from_codeowners(repo):
    repos = getRepositoriesWithOwners()
    repo = repo.replace('yaperos/','')
    if repo in repos:
        return repos[repo]
    return 'Depreciado/Sem Owner'

# def getRepositoriesWithOwners():
@cache_yape.daily_cache_clear
@functools.lru_cache(maxsize=None)
def get_services():
    unique_services = {}

    url = 'https://public-api.linearb.io/api/v1/services/'
    
    # Chave de API
    API_KEY = os.getenv('API_KEY')

    # Cabeçalhos
    headers = {
        'accept': 'application/json',
        'x-api-key': API_KEY
    }

    # Faça a solicitação GET
    response = requests.get(url, headers=headers)
    # Verifique a resposta
    if response.status_code == 200:
        data = response.json()
        items = data['items']
        for item in items:
            item_id = item["id"]
            item_name = item["name"]
            unique_services[item_name] = item_id
        
    else:
        print(f"Falha na solicitação - Código de status: {response.status_code}")
        print(response.text)
    return unique_services

# def getRepositoriesWithOwners():
@cache_yape.daily_cache_clear
@functools.lru_cache(maxsize=None)
def get_teams():
    unique_teams = {}

    url = 'https://public-api.linearb.io/api/v1/teams/'
    
    # Chave de API
    API_KEY = os.getenv('API_KEY')

    # Cabeçalhos
    headers = {
        'accept': 'application/json',
        'x-api-key': API_KEY
    }

    # Faça a solicitação GET
    response = requests.get(url, headers=headers)
    # Verifique a resposta
    if response.status_code == 200:
        data = response.json()
        items = data['items']
        for item in items:
            item_id = item["id"]
            item_name = item["name"]
            unique_teams[item_name] = item_id
        
    else:
        print(f"Falha na solicitação - Código de status: {response.status_code}")
        print(response.text)
    return unique_teams

def get_repositories_in_services():
    unique_services = {}

    url = 'https://public-api.linearb.io/api/v1/services/'
    
    # Chave de API
    API_KEY = os.getenv('API_KEY')

    # Cabeçalhos
    headers = {
        'accept': 'application/json',
        'x-api-key': API_KEY
    }

    # Faça a solicitação GET
    response = requests.get(url, headers=headers)
    # Verifique a resposta
    if response.status_code == 200:
        data = response.json()
        items = data['items']
        for item in items:
            item_id = item["id"]
            item_name = item["name"]
            paths = item['paths']
            unique_repositories_ids = []
            for path in paths:
                path_id = path['id']
                unique_repositories_ids.append(path_id)
            unique_services[item_name] = unique_repositories_ids
    else:
        print(f"Falha na solicitação - Código de status: {response.status_code}")
        print(response.text)
    return unique_services

@cache_yape.daily_cache_clear
@functools.lru_cache(maxsize=None)
def get_measurements(servicesIds, owner, month, year):
    inicio_linearb, fim_linearb = commons_yape.get_start_end_dates_format(year,month,'%Y-%m-%d')
    
    API_URL = 'https://public-api.linearb.io/api/v2/measurements'
    API_KEY = os.getenv('API_KEY')
    
    requestedMetrics = [ 
                          {
                           "name":"branch.computed.cycle_time",
                           "agg": "avg"
                          },
                          {
                            "name":"branch.time_to_pr",
                            "agg": "avg"
                          },
                          {
                            "name":"branch.time_to_review",
                            "agg": "avg"
                          },
                          {
                             "name":"branch.review_time",
                             "agg": "avg"
                          },
                          {
                             "name":"branch.time_to_prod",
                             "agg": "avg"
                          },
                          {
                             "name":"commit.activity.new_work.count"
                          },
                          {
                             "name":"commit.activity.refactor.count"
                          },
                          {
                             "name":"commit.activity.rework.count"
                          },
                          {
                             "name":"branch.state.computed.done"
                          }
                        ]
    time_ranges = [
        {"after": f"{inicio_linearb}",
        "before": f"{fim_linearb}"}
    ]
    data = {
        "service_ids": servicesIds,
        "requested_metrics":requestedMetrics,
        "time_ranges":time_ranges
    }
    headers = {
        'accept': 'application/json',
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.post(API_URL, json=data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        metrics = {}
        metrics['owner'] = owner
        
        for data_metric in data[0]['metrics']: 
            cycle_time = 0
            if 'branch.computed.cycle_time:avg' not in data_metric:
                cycle_time = 0
            else:
                cycle_time = data_metric['branch.computed.cycle_time:avg']
            cycle_time_minutes = cycle_time
            cycle_time = commons_yape.formatTime(cycle_time)
            
            coding_time = 0
            if 'branch.time_to_pr:avg' not in data_metric:
                coding_time = 0
            else:
                coding_time = data_metric['branch.time_to_pr:avg']
            coding_time_minutes = coding_time
            coding_time = commons_yape.formatTime(coding_time)

            pickup_time = 0 
            if 'branch.time_to_review:avg' not in data_metric:
                pickup_time = 0
            else:
                pickup_time = data_metric['branch.time_to_review:avg']
            pickup_time_minutes = pickup_time
            pickup_time = commons_yape.formatTime(pickup_time)

            review_time = 0
            if 'branch.review_time:avg' not in data_metric:
                review_time = 0
            else:
                review_time = data_metric['branch.review_time:avg']
            review_time_minutes = review_time
            review_time = commons_yape.formatTime(review_time)

            deploy_time = 0
            if 'branch.time_to_prod:avg' not in data_metric:
                deploy_time = 0
            else:
                deploy_time = data_metric['branch.time_to_prod:avg']
            deploy_time_minutes = deploy_time
            deploy_time = commons_yape.formatTime(deploy_time)

            new_code = 0
            # print(f"commit.activity.new_work.count: {data_metric['commit.activity.new_work.count']}")
            if 'commit.activity.new_work.count' not in data_metric or data_metric['commit.activity.new_work.count'] == 0 or data_metric['commit.activity.new_work.count'] is None:
                new_code = 0
            else:
                new_code = (data_metric['commit.activity.new_work.count']*100)/data_metric['commit.total_changes']
                new_code = round(new_code,2)

            refactor = 0
            if 'commit.activity.refactor.count' not in data_metric or data_metric['commit.activity.refactor.count'] == 0 or data_metric['commit.activity.refactor.count'] is None:
                refactor = 0
            else:
                refactor = (data_metric['commit.activity.refactor.count']*100)/data_metric['commit.total_changes']
                refactor = round(refactor,2)

            rework = 0
            if 'commit.activity.rework.count' not in data_metric or data_metric['commit.activity.rework.count'] == 0 or data_metric['commit.activity.rework.count'] is None:
                rework = 0
            else:
                # metrics['rework'] = data_metric['commit.activity.rework.count']
                rework = (data_metric['commit.activity.rework.count']*100)/data_metric['commit.total_changes']
                rework = round(rework,2)

            metrics['cycle time'] = f"{commons_yape.getBenchmark('cycleTime',cycle_time_minutes)} {commons_yape.formatTime(cycle_time_minutes)}"
            metrics['cycle time (minutes)'] = cycle_time_minutes
            metrics['coding_raw'] = coding_time_minutes
            metrics['pickup_raw'] = pickup_time_minutes
            metrics['review_raw'] = review_time_minutes
            metrics['deploy_raw'] = deploy_time_minutes
            metrics['coding'] = f"{commons_yape.getBenchmark('codingTime',coding_time_minutes)} {commons_yape.formatTime(coding_time_minutes)}"
            metrics['pickup'] = f"{commons_yape.getBenchmark('pickupTime',pickup_time_minutes)} {commons_yape.formatTime(pickup_time_minutes)}"
            metrics['review'] = f"{commons_yape.getBenchmark('reviewTime',review_time_minutes)} {commons_yape.formatTime(review_time_minutes)}"
            metrics['deploy'] = f"{commons_yape.getBenchmark('deployTime',deploy_time_minutes)} {commons_yape.formatTime(deploy_time_minutes)}"
            # metrics['coding pickup review deploy'] = f"{status_coding} {status_pickup} {status_review} {status_deploy}"
            # metrics['pickup'] = commons_yape.getCodeTimeBenchmark(pickup_time_minutes)
            # metrics['review'] = commons_yape.getCodeTimeBenchmark(review_time_minutes)
            # metrics['deploy'] = commons_yape.getCodeTimeBenchmark(deploy_time_minutes)
            metrics['new_code_raw'] = new_code
            metrics['refactor_raw'] = refactor
            metrics['rework_raw'] = rework
            metrics['refactor'] = f"{commons_yape.getBenchmark('refactor',refactor)} {refactor}%"
            metrics['rework'] = f"{commons_yape.getBenchmark('rework',rework)} {rework}%"
            metrics['work breakdown(newcode-refactor-rework)'] = f"{new_code}% - {refactor}% - {rework}%"

            # if 'branch.state.computed.done' not in data_metric:
            #     metrics['branchs_done'] = 0
            # else:
            #     metrics['branchs_done'] = data_metric['branch.state.computed.done']
        return metrics
    else:
        metric_log.log_critical(f"Falha na solicitação - Código de status: {response.status_code} - request data:{data} - response:{response.text}")
        print(f"Falha na solicitação - Código de status: {response.status_code} - request data:{data} - response:{response.text}")
        return {}

@cache_yape.daily_cache_clear
@functools.lru_cache(maxsize=None)
def get_measurementsByTeam(teamIds, owner, month, year):
    inicio_linearb, fim_linearb = commons_yape.get_start_end_dates_format(year,month,'%Y-%m-%d')
    
    API_URL = 'https://public-api.linearb.io/api/v2/measurements'
    API_KEY = os.getenv('API_KEY')
    
    requestedMetrics = [ 
                          {
                           "name":"branch.computed.cycle_time",
                           "agg": "avg"
                          },
                          {
                            "name":"branch.time_to_pr",
                            "agg": "avg"
                          },
                          {
                            "name":"branch.time_to_review",
                            "agg": "avg"
                          },
                          {
                             "name":"branch.review_time",
                             "agg": "avg"
                          },
                          {
                             "name":"branch.time_to_prod",
                             "agg": "avg"
                          },
                          {
                             "name":"commit.activity.new_work.count"
                          },
                          {
                             "name":"commit.activity.refactor.count"
                          },
                          {
                             "name":"commit.activity.rework.count"
                          },
                          {
                             "name":"branch.state.computed.done"
                          }
                        ]
    time_ranges = [
        {"after": f"{inicio_linearb}",
        "before": f"{fim_linearb}"}
    ]
    data = {
        "team_ids": teamIds,
        "requested_metrics":requestedMetrics,
        "time_ranges":time_ranges
    }
    headers = {
        'accept': 'application/json',
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.post(API_URL, json=data, headers=headers)
    if response.status_code == 200:
        data = response.json()
        metrics = {}
        metrics['owner'] = owner
        
        for data_metric in data[0]['metrics']: 
            cycle_time = 0
            if 'branch.computed.cycle_time:avg' not in data_metric:
                cycle_time = 0
            else:
                cycle_time = data_metric['branch.computed.cycle_time:avg']
            cycle_time_minutes = cycle_time
            cycle_time = commons_yape.formatTime(cycle_time)
            
            coding_time = 0
            if 'branch.time_to_pr:avg' not in data_metric:
                coding_time = 0
            else:
                coding_time = data_metric['branch.time_to_pr:avg']
            coding_time_minutes = coding_time
            coding_time = commons_yape.formatTime(coding_time)

            pickup_time = 0 
            if 'branch.time_to_review:avg' not in data_metric:
                pickup_time = 0
            else:
                pickup_time = data_metric['branch.time_to_review:avg']
            pickup_time_minutes = pickup_time
            pickup_time = commons_yape.formatTime(pickup_time)

            review_time = 0
            if 'branch.review_time:avg' not in data_metric:
                review_time = 0
            else:
                review_time = data_metric['branch.review_time:avg']
            review_time_minutes = review_time
            review_time = commons_yape.formatTime(review_time)

            deploy_time = 0
            if 'branch.time_to_prod:avg' not in data_metric:
                deploy_time = 0
            else:
                deploy_time = data_metric['branch.time_to_prod:avg']
            deploy_time_minutes = deploy_time
            deploy_time = commons_yape.formatTime(deploy_time)

            new_code = 0
            if 'commit.activity.new_work.count' not in data_metric or data_metric['commit.activity.new_work.count'] == 0:
                new_code = 0
            else:
                new_code = (data_metric['commit.activity.new_work.count']*100)/data_metric['commit.total_changes']
                new_code = round(new_code,2)

            refactor = 0
            if 'commit.activity.refactor.count' not in data_metric or data_metric['commit.activity.refactor.count'] == 0:
                refactor = 0
            else:
                refactor = (data_metric['commit.activity.refactor.count']*100)/data_metric['commit.total_changes']
                refactor = round(refactor,2)

            rework = 0
            if 'commit.activity.rework.count' not in data_metric or data_metric['commit.activity.rework.count'] == 0:
                rework = 0
            else:
                # metrics['rework'] = data_metric['commit.activity.rework.count']
                rework = (data_metric['commit.activity.rework.count']*100)/data_metric['commit.total_changes']
                rework = round(rework,2)

            metrics['cycle time'] = f"{commons_yape.getBenchmark('cycleTime',cycle_time_minutes)} {commons_yape.formatTime(cycle_time_minutes)}"
            metrics['cycle time (minutes)'] = cycle_time_minutes
            
            metrics['coding'] = f"{commons_yape.getBenchmark('codingTime',coding_time_minutes)} {commons_yape.formatTime(coding_time_minutes)}"
            metrics['pickup'] = f"{commons_yape.getBenchmark('pickupTime',pickup_time_minutes)} {commons_yape.formatTime(pickup_time_minutes)}"
            metrics['review'] = f"{commons_yape.getBenchmark('reviewTime',review_time_minutes)} {commons_yape.formatTime(review_time_minutes)}"
            metrics['deploy'] = f"{commons_yape.getBenchmark('deployTime',deploy_time_minutes)} {commons_yape.formatTime(deploy_time_minutes)}"
            # metrics['coding pickup review deploy'] = f"{status_coding} {status_pickup} {status_review} {status_deploy}"
            # metrics['pickup'] = commons_yape.getCodeTimeBenchmark(pickup_time_minutes)
            # metrics['review'] = commons_yape.getCodeTimeBenchmark(review_time_minutes)
            # metrics['deploy'] = commons_yape.getCodeTimeBenchmark(deploy_time_minutes)
            
            metrics['work breakdown(newcode-refactor-rework)'] = f"{new_code}% - {refactor}% - {rework}%"

            # if 'branch.state.computed.done' not in data_metric:
            #     metrics['branchs_done'] = 0
            # else:
            #     metrics['branchs_done'] = data_metric['branch.state.computed.done']
        return metrics
    else:
        metric_log.log_critical(f"Falha na solicitação - Código de status: {response.status_code} - request data:{data} - response:{response.text}")
        print(f"Falha na solicitação - Código de status: {response.status_code} - request data:{data} - response:{response.text}")
        return {}    
