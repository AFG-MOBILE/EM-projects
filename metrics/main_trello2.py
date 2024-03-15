from rapidfuzz import process, fuzz
import pandas as pd
import subprocess


# Função para encontrar a melhor correspondência de nomes
# def find_best_match(name, list_names, score_cutoff=80):
#     highest = process.extractOne(name, list_names, scorer=fuzz.WRatio, score_cutoff=score_cutoff)
#     return highest[0] if highest else None
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
    


# Carregando os arquivos em DataFrames
interactions_cards_done = pd.read_excel("/Users/alexfrisoneyape/Development/EM-projects/output/Interactions_Cards_Done.xlsx", engine='openpyxl')
contributors_metrics_roles = pd.read_excel("/Users/alexfrisoneyape/Development/EM-projects/output/contributors_roles.xlsx", engine='openpyxl')

# list_names = contributors_metrics_roles['Contributor Name'].unique()
unique_names_metrics = interactions_cards_done['Member Name'].unique()
unique_names_roles = contributors_metrics_roles['Contributor Name'].unique()


# Criando um dicionário de correspondências
matches = {name: find_best_match(name, unique_names_roles) for name in unique_names_metrics}

# Mapeando os nomes no DataFrame contributors_metrics para os correspondentes mais similares
interactions_cards_done['Matched Name'] = interactions_cards_done['Member Name'].map(matches)

# Unindo as informações dos dois DataFrames
result_df = pd.merge(interactions_cards_done, contributors_metrics_roles, left_on='Matched Name', right_on='Contributor Name', how='left')

filename_final = '/Users/alexfrisoneyape/Development/EM-projects/output/Merge_Interactions_Cards_Done.xlsx'
result_df.to_excel(filename_final)
subprocess.run(['open', '-a', 'Microsoft Excel', filename_final ])