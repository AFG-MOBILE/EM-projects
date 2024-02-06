import os
import subprocess
import pandas as pd
import requests
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import time  # Importe o módulo time


# Carrega variáveis de ambiente
load_dotenv('.env')

API_KEY_TRELLO = os.getenv('API_KEY_TRELLO')
TOKEN_TRELLO = os.getenv('TOKEN_TRELLO')

# Substitua pelos seus valores reais
API_KEY = API_KEY_TRELLO
TOKEN = TOKEN_TRELLO

# LIST_ID = "632b5ec4ee1230008bd34d7f"  #marketplace 
# LIST_ID = "620cbb3308424a3f218f092a" #promos
LIST_ID = "61ae4a1ca02160403e4daeda" #devops
FROM_DATE = '2024-01-01'  # Formato aaaa-mm-dd
TO_DATE = '2024-01-31'    # Formato aaaa-mm-dd
# board_id = '632b5ec4ee1230008bd34d6d' #marketplace
# board_id = '620c10ba5cfd7d4ce889d72a' #promos
board_id = '61ae4a1ca02160403e4daece' #dev ops solicitudes
filename = 'detailed_interactions_cards_done_list_devops.xlsx'

def get_actions_for_card(card_id, api_key, token):
    """Busca ações de adição de membros para um card específico."""
    url = f"https://api.trello.com/1/cards/{card_id}/actions"
    params = {
        'key': api_key,
        'token': token,
        'filter': 'addMemberToCard',
        'before': TO_DATE,
        'since': FROM_DATE
    }
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else []

member_info_cache = {}  # Cache para informações de membros

def get_member_info(member_id, api_key, token):
    """Obtém informações do membro pelo ID, utilizando cache."""
    if member_id not in member_info_cache:
        url = f"https://api.trello.com/1/members/{member_id}"
        params = {'key': api_key, 'token': token}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            member = response.json()
            member_info_cache[member_id] = {
                'name': member.get('fullName'),
                'username': member.get('username')
            }
    return member_info_cache.get(member_id, {'name': 'Unknown', 'username': 'Unknown'})


def process_card(card, api_key, token):
    """Processa um card para extrair informações dos membros adicionados, incluindo o nome do card."""
    card_id = card['id']
    card_name = card['name']
    actions = get_actions_for_card(card_id, api_key, token)
    card_member_info = []
    for action in actions:
        if 'member' in action['data']:
            member_id = action['data']['member']['id']
            member_info = get_member_info(member_id, api_key, token)
            action_date = datetime.strptime(action['date'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
            card_member_info.append({
                'Card ID': card_id,
                'Card Name': card_name,  # Adicionado nome do card
                'Member Name': member_info['name'],
                'Action Date': action_date
            })
    return card_member_info

def get_all_members(api_key, token, board_id):
    """Obtém todos os membros do board."""
    url = f"https://api.trello.com/1/boards/{board_id}/members?key={api_key}&token={token}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []

def get_members_not_found(cards, all_members):
    """Identifica membros que não estão presentes nos cards."""
    card_members = set(member['Member Name'] for card in cards for member in card)
    all_members_names = set(member['fullName'] for member in all_members)
    not_found_members = all_members_names - card_members
    return [{'Member Name': member, 'Status': 'Not Found'} for member in not_found_members]

# Início da contagem do tempo
start_time = time.time()

# Obtem cards da lista
url = f"https://api.trello.com/1/lists/{LIST_ID}/cards?key={API_KEY}&token={TOKEN}"
response = requests.get(url)
cards = response.json() if response.status_code == 200 else []

# Coleta informações dos membros para cada card
detailed_info = []
for card in cards:
     detailed_info.extend(process_card(card, API_KEY, TOKEN))

# detailed_info = [
#     {'Card ID': '1', 'Card Name': 'Card A', 'Member Name': 'Alice', 'Action Date': '2024-01-05'},
#     {'Card ID': '1', 'Card Name': 'Card A', 'Member Name': 'Bob', 'Action Date': '2024-01-10'},
#     {'Card ID': '2', 'Card Name': 'Card B', 'Member Name': 'Charlie', 'Action Date': '2024-01-15'},
#     {'Card ID': '2', 'Card Name': 'Card B', 'Member Name': 'Alice', 'Action Date': '2024-01-20'},
#     # Adicione mais entradas conforme necessário
# ]
df = pd.DataFrame(detailed_info)
print(f"detailed_info: {df}")
# Obtem todos os membros do board
all_members = get_all_members(API_KEY, TOKEN, board_id)
# Convertendo a lista de membros do quadro em um DataFrame
members_df = pd.DataFrame(all_members)
print(f"members_df: {members_df}")

# Coleta informações sobre membros não encontrados nos cards
# not_found_members_info = get_members_not_found(detailed_info, members_df)
not_found_df = members_df[~members_df['fullName'].isin(df['Member Name'])]

# Exportando para Excel com as abas especificadas
with pd.ExcelWriter(filename, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='General Data', index=False)
    pivot_members_cards = df.pivot_table(index='Member Name', values='Card ID', aggfunc='count')
    pivot_members_cards.rename(columns={'Card ID': 'Total Cards'}).to_excel(writer, sheet_name='Members x Cards')
    df['Count'] = 1
    pivot_cards_members = df.pivot_table(index='Card Name', columns='Member Name', values='Count', aggfunc='count', fill_value=0)
    pivot_cards_members.to_excel(writer, sheet_name='Cards x Members')
    not_found_df.to_excel(writer, sheet_name='Not Members', index=False)


subprocess.run(['open', '-a', 'Microsoft Excel', filename ])
print(f"Dados exportados com sucesso para '{filename}'.")
# Fim da execução do código
end_time = time.time()
# Calcula o tempo decorrido em segundos
elapsed_time = end_time - start_time
# Converte o tempo decorrido para minutos e segundos
minutes = int(elapsed_time // 60)
seconds = int(elapsed_time % 60)
print(f"Tempo total de execução: {minutes} minutos e {seconds} segundos.")