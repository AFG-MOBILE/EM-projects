
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_ebay_titles_prices(url, user_agent):
    headers = {
        'User-Agent': user_agent
    }

    try:
        response = requests.get(url, headers=headers)

        # Verifique se a solicitação foi bem-sucedida
        if response.ok:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Encontre todos os itens da lista baseados na tag e classe
            items = soup.find_all('li', class_='s-item')
            
            results = []
            for item in items:
                # Inicializando o dicionário para armazenar dados do item
                item_data = {}

                # Encontrar o título do item
                title_tag = item.find('div', class_='s-item__title')
                if title_tag:
                    item_data['title'] = title_tag.get_text(strip=True)

                # Encontrar o preço do item
                price_tag = item.find('span', class_='s-item__price')
                if price_tag:
                    item_data['price'] = price_tag.get_text(strip=True)
                
                # Adiciona o dicionário do item à lista de resultados se tiver título e preço
                if 'title' in item_data and 'price' in item_data:
                    results.append(item_data)
            df = pd.DataFrame(results)
            return df
        else:
            response.raise_for_status()
    
    except requests.RequestException as e:
        print(f'Erro na requisição: {e}')
        return []