import os
import subprocess
import pandas as pd
import requests
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from tqdm import tqdm  # Importar tqdm para acompanhar o progresso
import threading

# Carrega variáveis de ambiente
load_dotenv('.env')

API_KEY = os.getenv('API_KEY_TRELLO')
TOKEN = os.getenv('TOKEN_TRELLO')


# # LIST_ID = "632b5ec4ee1230008bd34d7f"  #marketplace 
# # LIST_ID = "620cbb3308424a3f218f092a" #promos
# LIST_ID = "61ae4a1ca02160403e4daeda" #devops
# FROM_DATE = '2024-01-01'  # Formato aaaa-mm-dd
# TO_DATE = '2024-01-31'    # Formato aaaa-mm-dd
# # board_id = '632b5ec4ee1230008bd34d6d' #marketplace
# # board_id = '620c10ba5cfd7d4ce889d72a' #promos
# board_id = '61ae4a1ca02160403e4daece' #dev ops solicitudes
# filename = 'detailed_interactions_cards_done_list_devops.xlsx'

# Cache para informações de membros
member_info_cache = {}  
lock = threading.Lock()

def get_actions_for_card(card_id, api_key, token, from_date, to_date):
    """Busca ações de adição de membros para um card específico."""
    url = f"https://api.trello.com/1/cards/{card_id}/actions"
    params = {
        'key': api_key,
        'token': token,
        'filter': 'addMemberToCard'
        # 'before': to_date,
        # 'since': from_date
    }
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else []

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

def process_card(card, api_key, token, from_date, to_date):
    """Processa um card para extrair informações dos membros adicionados, incluindo o nome do card."""
    card_id = card['id']
    card_name = card['name']
    card_url = card['shortUrl']
    actions = get_actions_for_card(card_id, api_key, token, from_date, to_date)
    # print(f"Total de actions: {len(actions)}")
    card_member_info = []
    for action in actions:
        if 'member' in action['data']:
            member_id = action['data']['member']['id']
            member_info = get_member_info(member_id, api_key, token)
            action_date = datetime.strptime(action['date'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
            card_member_info.append({
                'Card ID': card_id,
                'Card Name': card_name,
                'Card Url': card_url,  
                'Member Name': member_info['name'],
                'Action Date': action_date
            })
    return card_member_info

def get_all_members(api_key, token, board_id):
    """Obtém todos os membros do board."""
    url = f"https://api.trello.com/1/boards/{board_id}/members?key={api_key}&token={token}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []

def get_card_in_done(list_id):
    # Obtem cards da lista
    url = f"https://api.trello.com/1/lists/{list_id}/cards?key={API_KEY}&token={TOKEN}"
    response = requests.get(url)
    cards = response.json() if response.status_code == 200 else []
    return cards

def filter_cards_by_column(cards, column_id, api_key, token, from_date_str, to_date_str):
    # Convertendo as strings de data para objetos datetime
    from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d')

    filtered_cards = []

    for card in tqdm(cards, desc='Filtering cards'):
        card_movements = get_card_movements(card['id'], api_key, token)
        if card_movements:
            for movement in card_movements:
                if 'data' in movement and 'listAfter' in movement['data'] and movement['data']['listAfter']['id'] == column_id:
                    movement_date = datetime.strptime(movement['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    if from_date <= movement_date <= to_date:
                        card['movement_date'] = movement_date
                        filtered_cards.append(card)
                        break  # Uma vez que encontramos o movimento válido, podemos parar de verificar os outros movimentos
    return filtered_cards

# def filter_cards_by_column(cards, column_id, api_key, token, from_date_str, to_date_str):
#     # Convertendo as strings de data para objetos datetime
#     from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
#     to_date = datetime.strptime(to_date_str, '%Y-%m-%d')

#     filtered_cards = []

#     def process_card_with_lock(card):
#         card_movements = get_card_movements(card['id'], api_key, token)
#         if card_movements:
#             for movement in card_movements:
#                 if 'data' in movement and 'listAfter' in movement['data'] and movement['data']['listAfter']['id'] == column_id:
#                     movement_date = datetime.strptime(movement['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
#                     if from_date <= movement_date <= to_date:
#                         card['movement_date'] = movement_date
#                         with lock:
#                             filtered_cards.append(card)
#                         break

#     with ThreadPoolExecutor(max_workers=100) as executor:
#         list(tqdm(executor.map(process_card_with_lock, cards), total=len(cards), desc='Filtering cards'))

#     return filtered_cards

def get_card_movements(card_id, api_key, token):
    """Obtém o histórico de movimentações de um cartão."""
    url = f"https://api.trello.com/1/cards/{card_id}/actions"
    params = {
        'key': api_key,
        'token': token,
        'filter': 'updateCard:idList'
    }
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else []

def memberInfoByCard(cards, from_date, to_date):
    # Coleta informações dos membros para cada card
    detailed_info = []
    for card in tqdm(cards, desc='Processing cards'):
        try:
            card_info = process_card(card, API_KEY, TOKEN, from_date, to_date)
            detailed_info.extend(card_info)
        except Exception as exc:
            print(f'Error processing card {card}: {exc}')

    # Convertendo a lista de detalhes de cartões em um DataFrame
    df = pd.DataFrame(detailed_info)
    return df

def exportDataToExcel(filename, df, not_found_df, df_all_cards):
    # Exportando para Excel com as abas especificadas
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='General Data', index=False)
        pivot_members_cards = df.pivot_table(index='Member Name', values='Card ID', aggfunc='count')
        pivot_members_cards.rename(columns={'Card ID': 'Total Cards'}).to_excel(writer, sheet_name='Members x Cards')
        df['Count'] = 1
        pivot_cards_members = df.pivot_table(index='Card Name', columns='Member Name', values='Count', aggfunc='count', fill_value=0)
        pivot_cards_members.to_excel(writer, sheet_name='Cards x Members')
        not_found_df.to_excel(writer, sheet_name='Not Members', index=False)
        df_all_cards.to_excel(writer, sheet_name='All Cards in Done', index=False)

    subprocess.run(['open', '-a', 'Microsoft Excel', filename])


def generateMetricsTrello(board_id, list_id, filename, from_date, to_date):
    # Obtem todos os membros do board
    all_members = get_all_members(API_KEY, TOKEN, board_id)
    # Convertendo a lista de membros do quadro em um DataFrame
    members_df = pd.DataFrame(all_members)
    # print(members_df)

    cards = get_card_in_done(list_id)
    # df_all_cards = pd.DataFrame(cards)

    # Filtrar os cartões pela movimentação para a coluna desejada (cards, column_name, from_date_str, to_date_str):
    filtered_cards = filter_cards_by_column(cards, list_id, API_KEY, TOKEN,from_date, to_date)
    df_filtered_cards = pd.DataFrame(filtered_cards)
    print(f"total de cards filtrados: {df_filtered_cards.shape[0]}")
    
    df = memberInfoByCard(filtered_cards, from_date, to_date)
    print(f"total de info de membro do board em um card: {df.shape[0]}")
    # print(df)
    # Coleta informações sobre membros não encontrados nos cards
    not_found_df = members_df[~members_df['fullName'].isin(df['Member Name'])]

    exportDataToExcel(filename,df,not_found_df, df_filtered_cards)
