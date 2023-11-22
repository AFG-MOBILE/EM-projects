import base64
import requests
from github import Github
import timer_metrics
import linearb
import functools
import cache_yape
from dotenv import load_dotenv
import os

load_dotenv('.env')

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

@timer_metrics.timer_decorator
def listar_releases_de_staging(data_inicial, data_final):
    releases_stg_prd = []
    
    # Nome da organização
    org_name = 'yaperos'

    org = Github(ACCESS_TOKEN).get_organization(org_name)

    for repo in org.get_repos():
        releases = repo.get_releases()
        # Filtre as releases com base na data de criação
        releases_apos_data = [release for release in releases if
                              release.created_at >= data_inicial and release.created_at <= data_final]
        for release in releases_apos_data:

            tag_name = release.tag_name
            # Obtenha a tag específica
            tag = repo.get_git_ref(f'tags/{tag_name}')

            stage = "release"
            # Verifica se a tag está em staging
            if "-rc" in tag_name:
                stage = "staging"

            timestamp = release.created_at
            owner = get_owner_from_codeowners(repo.full_name)

            release = {}
            release['repo_name'] = repo.html_url
            release['stage'] = stage
            release['commit_sha'] = tag.object.sha
            release['timestamp'] = timestamp.isoformat()
            release['owner'] = owner
            releases_stg_prd.append(release)
            
    return releases_stg_prd

# Função para obter o proprietário (owner) de um repositório
# @functools.lru_cache(maxsize=None)
def get_owner_from_codeowners(repo_full_name):
    return linearb.get_owner_from_codeowners(repo_full_name)

@timer_metrics.timer_decorator
def get_repositories_into_services():
    unique_repositories = set()
    # URL da API
    url = 'https://public-api.linearb.io/api/v1/services/'
    # Chave de API
    api_key = os.getenv('API_KEY')
    # Cabeçalhos
    headers = {
        'accept': 'application/json',
        'x-api-key': api_key
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

@cache_yape.daily_cache_clear
@functools.lru_cache(maxsize=None)
def get_all_repositories_github():
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ORG_NAME = 'yaperos'
    # Inicialize a instância da API do GitHub
    g = Github(ACCESS_TOKEN)
    # Obtenha a organização
    org = g.get_organization(ORG_NAME)
    # Lista de repositórios da organização
    return [repo for repo in org.get_repos() if repo.private and not repo.archived]

def check_repositories_in_github(all_repositories):
    # Verifica se os itens de all_repositories estão em unique_repositories
    # print("*** Verificando o owner no Github:")
    for repo in all_repositories:
        repo_name = repo.name
        owner = get_owner_from_codeowners(repo_name)
        # print(f"O repositorio '{repo_name}' possui como owner: {owner}")

def check_repositories_without_owners_in_github(all_repositories):
    repositories_without_owners = set()
    for repo in all_repositories:
        isTest = "test" in repo.name
        if not isTest:
            hasOwner = check_codeowners_file(repo.name)
            if not hasOwner:
                repositories_without_owners.add(repo.name)
    return repositories_without_owners

@cache_yape.daily_cache_clear
@functools.lru_cache(maxsize=None)
def check_codeowners_file(repo_full_name):
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ORG_NAME = 'yaperos'
    BASE_URL = 'https://api.github.com'
    headers = {
        'Authorization': f'token {ACCESS_TOKEN}',
    }
    owners_url = f'{BASE_URL}/repos/{ORG_NAME}/{repo_full_name}/contents/.github/CODEOWNERS'
    response = requests.get(owners_url, headers=headers)

    if response.status_code == 200:
        content = response.json().get('content', '')
        decoded_content = base64.b64decode(content).decode('utf-8')
        # Divida o conteúdo por linhas e obtenha o primeiro item como owner
        lines = decoded_content.strip().split('\n')
        if lines:
            return True
    return False