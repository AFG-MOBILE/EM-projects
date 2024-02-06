from dotenv import load_dotenv
import os
import pandas as pd
import requests

load_dotenv('.env')

# Substitua com suas chaves de API do Datadog
API_KEY_TRELLO = os.getenv('API_KEY_TRELLO')
TOKEN_TRELLO = os.getenv('TOKEN_TRELLO')
ORG_ID = '6422139a562ad598532c0956'

# Cabeçalho para aceitar JSON
headers = {
    'Accept': 'application/json'
}

def get_members():
    # URL para a solicitação da API
    url = f'https://api.trello.com/1/organizations/{ORG_ID}/members?key={API_KEY_TRELLO}&token={TOKEN_TRELLO}'

    # Fazendo a solicitação GET
    response = requests.get(url, headers=headers)

    # Verificando se a solicitação foi bem-sucedida
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return f'Erro na solicitação: {response.status_code}'

def get_cards_member(member_id):
    url = f'https://api.trello.com/1/members/{member_id}/cards?key={API_KEY_TRELLO}&token={TOKEN_TRELLO}'

    # Fazendo a solicitação GET
    response = requests.get(url, headers=headers)

    # Verificando se a solicitação foi bem-sucedida
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return f'Erro na solicitação: {response.status_code}'
    
def get_actions_on_card(card_id):
    url = f'https://api.trello.com/1/cards/{card_id}/actions?key={API_KEY_TRELLO}&token={TOKEN_TRELLO}'

    # Fazendo a solicitação GET
    response = requests.get(url, headers=headers)

    # Verificando se a solicitação foi bem-sucedida
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return f'Erro na solicitação: {response.status_code}'
    
def get_lists_on_board(board_id):
    
    url = f'https://api.trello.com/1/boards/{board_id}/lists?key={API_KEY_TRELLO}&token={TOKEN_TRELLO}'

    # Fazendo a solicitação GET
    response = requests.get(url, headers=headers)

    # Verificando se a solicitação foi bem-sucedida
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return f'Erro na solicitação: {response.status_code}'
    
def get_cards_in_Collumn_Done(list_id):
    url = f'https://api.trello.com/1/lists/{list_id}/cards?key={API_KEY_TRELLO}&token={TOKEN_TRELLO}'

    # Fazendo a solicitação GET
    response = requests.get(url, headers=headers)

    # Verificando se a solicitação foi bem-sucedida
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data)
    else:
        return f'Erro na solicitação: {response.status_code}'