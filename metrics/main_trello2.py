import requests
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv('.env')

API_KEY = os.getenv('API_KEY_TRELLO')
TOKEN = os.getenv('TOKEN_TRELLO')

# ID da organização que você deseja listar os membros
organization_id = '6422139a562ad598532c0956'

# URL base da API do Trello
base_url = 'https://api.trello.com/1'

# Endpoint para listar todos os membros de uma organização
endpoint = f'{base_url}/organizations/{organization_id}/members'

# Endpoint para listar todos os membros de uma organização
members_endpoint = f'{base_url}/organizations/{organization_id}/members'


# Parâmetros da solicitação
params = {
    'key': API_KEY,
    'token': TOKEN
}

# Fazendo a solicitação GET para obter os membros da organização
response = requests.get(members_endpoint, params=params)

if response.status_code == 200:
    members = response.json()
    
    for member in members:
        # Obtendo o ID do membro
        member_id = member['id']
        
        # Endpoint para obter detalhes de um membro específico
        member_detail_endpoint = f'{base_url}/members/{member_id}'
        
        # Fazendo a solicitação GET para obter detalhes do membro
        member_response = requests.get(member_detail_endpoint, params=params)
        
        if member_response.status_code == 200:
            member_detail = member_response.json()
            
            # Imprimir detalhes do membro
            print("Nome:", member_detail['fullName'])
            print("Email:", member_detail['email'])  # Se disponível
            print("Username:", member_detail['username'])
            print("ID:", member_detail['id'])
            print("URL do avatar:", member_detail['avatarUrl'])
            print("--------------------")
        else:
            print("Erro ao obter detalhes do membro.")
            print(member_response.text)
else:
    print("Erro ao obter membros da organização.")
    print(response.text)