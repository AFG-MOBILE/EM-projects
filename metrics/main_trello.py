import metric_log
import trello
import pandas as pd
import subprocess
from base64 import b64decode
from github import Github
import os
import re
from fuzzywuzzy import process
from rapidfuzz import process, fuzz

# Função para encontrar o melhor match com base na similaridade
def match_names(name, list_names):
    highest = process.extractOne(name, list_names, score_cutoff=80)
    return highest[0] if highest else None

def find_best_match(target_name, list_names, score_cutoff=80):
    matches = process.extract(target_name, list_names, scorer=fuzz.WRatio, score_cutoff=score_cutoff)

    # Se não encontrar nenhum match, retorna None
    if not matches:
        return None

    # Filtra matches com a mesma pontuação mais alta
    top_score = matches[0][1]
    top_matches = [match for match in matches if match[1] == top_score]

    # Se houver mais de um top match, aplica critérios de desempate
    if len(top_matches) > 1:
        # Procurando pelo primeiro nome no target_name para desempate
        first_name = target_name.split()[0]
        refined_matches = [(name, score) for name, score, _ in top_matches if first_name.lower() in name.lower()]
        
        # Se refinamento encontrar correspondentes, seleciona aquele com o primeiro nome mais à esquerda (presumindo maior relevância)
        if refined_matches:
            return sorted(refined_matches, key=lambda x: x[0].lower().index(first_name.lower()))[0][0]
        else:
            # Se nenhum match refinado, retorna o match original com a pontuação mais alta
            return top_matches[0][0]
    else:
        # Retorna o match mais alto se não houver empate
        return top_matches[0][0]


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


if __name__ == "__main__":
    metric_log.config_metric_log()
    from_date = '2023-08-01'  # Formato aaaa-mm-dd
    to_date = '2024-02-29'    # Formato aaaa-mm-dd
    filename = 'detailed_interactions_cards_done_list_'
    teams = [
                {
                "name": "Marketplace",
                "list_id": "632b5ec4ee1230008bd34d7f",
                "board_id": "632b5ec4ee1230008bd34d6d",
                }
                ,
                {
                "name": "Promos",
                "list_id": "620cbb3308424a3f218f092a",
                "board_id": "620c10ba5cfd7d4ce889d72a",
                }
                ,
                {
                "name": "Gas",
                "list_id": "64f1ea80397bb170a09d94d6",
                "board_id": "64f1e97949e709e5e6b71a5c",
                }
                ,
                {
                "name": "Ticketing",
                "list_id": "655e08356fcd465b2586172f",
                "board_id": "65553c0e788023b27f5a8753",
                }
                ,
                {
                "name": "Gaming & Giftcards",
                "list_id": "642b603196ce37ad17d7fbf6",
                "board_id": "642b54df3e995f8aaa97429b",
                }
            ]
    df_general = []
    for team in teams:
        print(f"Getting {team['name']} data……")
        df = trello.generateMetricsTrello(team['name'],team['board_id'],team['list_id'], f"{filename}{team['name']}.xlsx",from_date, to_date)
        df_general.append(df)
    
    # Concatena todos os DataFrames na lista para criar um DataFrame total
    df_total = pd.concat(df_general, ignore_index=True)

    contributors_metrics = df_total

    data = extrair_dados_usuarios()
    contributors_roles = pd.DataFrame(data)

    # Preparar uma lista com nomes únicos para a comparação
    unique_names_metrics = contributors_metrics['Member Name'].unique()
    unique_names_roles = contributors_roles['Contributor Name'].unique()

    # Criando um dicionário de correspondências
    matches = {name: find_best_match(name, unique_names_roles) for name in unique_names_metrics}

    # Mapeando os nomes no DataFrame contributors_metrics para os correspondentes mais similares
    contributors_metrics['Matched Name'] = contributors_metrics['Member Name'].map(matches)

    # Unindo as informações dos dois DataFrames
    result_df = pd.merge(contributors_metrics, contributors_roles, left_on='Matched Name', right_on='Contributor Name', how='left')
    result_df = result_df[['Card ID',	'Card Name',	'Card Url',	'Matched Name',	'Action Date','Card Done','Board Name',	'Username',	'Email',	'Role',	'Squad',	'Division']]
    result_df = result_df.rename(columns={'Matched Name': 'Member Name'})
    filename_final = '/Users/alexfrisoneyape/Development/EM-projects/metrics/Interactions_Cards_Done.xlsx'
    result_df.to_excel(filename_final)
    subprocess.run(['open', '-a', 'Microsoft Excel', filename_final ])