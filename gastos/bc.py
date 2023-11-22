import requests
import commons

def get_dolar_cotacao(str):
    data = commons.ajusta_data_para_sexta(str)
    
    # Define a URL de consulta
    url = f'https://api.bcb.gov.br/dados/serie/bcdata.sgs.10813/dados?formato=json'
    
    # Faz a requisição à API
    response = requests.get(url)
    response.raise_for_status()  # Lança uma exceção se a resposta for um erro
    
    # Obtém os dados da resposta
    data_response = response.json()
    # print(data_response)
    for dic in data_response:
        if dic['data'] == data:
            return round(float(dic['valor']),2)

    return False
