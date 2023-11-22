import requests

def buscar_produtos_bestbuy(nome_produto, preco_maximo):
    api_key = ""
    # Substitua 'nome_produto' e 'preco_maximo' pelos seus valores desejados
    # A chave da API (api_key) deve ser fornecida pela Best Buy após a aprovação do seu acesso
    url = f"https://api.bestbuy.com/v1/products((search={nome_produto}&salePrice<=preco_maximo&condition=pre-owned))?format=json&apiKey={api_key}"
    
    response = requests.get(url)
    if response.ok:
        return response.json()  # Ou processe a resposta como necessário
    else:
        return f"Erro na solicitação: {response.status_code}"
