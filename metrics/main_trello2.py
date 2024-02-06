import os
import subprocess
import requests
import pandas as pd
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv('.env')

ORG_ID = '6422139a562ad598532c0956'
API_KEY_TRELLO = os.getenv('API_KEY_TRELLO')
TOKEN_TRELLO = os.getenv('TOKEN_TRELLO')
filename = 'org_members_activities.xlsx'



def get_org_members(org_id, key, token):
    url = f"https://api.trello.com/1/organizations/{org_id}/members"
    params = {'key': key, 'token': token}
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else []

def get_member_actions(member_id, key, token):
    url = f"https://api.trello.com/1/members/{member_id}/actions"
    params = {'key': key, 'token': token, 'limit': 1}  # Ajuste o limite conforme necessário
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else []

# Listando membros da organização
members = get_org_members(ORG_ID, API_KEY_TRELLO, TOKEN_TRELLO)

# Preparando os dados para o DataFrame
data = []
for member in members:
    actions = get_member_actions(member['id'], API_KEY_TRELLO, TOKEN_TRELLO)
    for action in actions:
        board_name = action['data']['board']['name'] if 'board' in action['data'] else 'N/A'
        card_name = action['data']['card']['name'] if 'card' in action['data'] else 'N/A'
        
        data.append({
            'Member Name': member['fullName'],
            'Member Username': member['username'],
            'Action Date': action['date'],
            'Action Type': action['type'],
            'Board Name': board_name,
            'Card Name': card_name
        })

# Convertendo para DataFrame
df = pd.DataFrame(data)

print(df)

# Para exportar para Excel
df.to_excel(filename, index=False)
subprocess.run(['open', '-a', 'Microsoft Excel', filename ])