import pandas as pd
from fuzzywuzzy import fuzz

def normalizar_nome(nome):
    """
    Normaliza o nome removendo espaços em branco extras e convertendo para minúsculas.
    """
    return nome.lower().strip()

def nome_mais_curto_se_similares(nome1, nome2, limiar=80):
    """
    Compara dois nomes e retorna o mais curto se forem considerados similares.
    """
    if fuzz.token_sort_ratio(normalizar_nome(nome1), normalizar_nome(nome2)) >= limiar:
        return nome1 if len(nome1) < len(nome2) else nome2
    return nome1

def unificar_nomes_na_mesma_coluna(df, coluna, limiar=80):
    """
    Para cada nome na coluna especificada, compara com todos os outros e mantém
    o nome de menor tamanho se forem considerados similares.
    """
    nomes_unicos = df[coluna].unique()
    nomes_finais = {}

    for nome in nomes_unicos:
        nome_atual = nome
        for outro_nome in nomes_unicos:
            nome_atual = nome_mais_curto_se_similares(nome_atual, outro_nome, limiar)
        nomes_finais[nome] = nome_atual

    # Atualiza o DataFrame com os nomes unificados
    df[coluna] = df[coluna].map(nomes_finais)
    return df

# Exemplo de uso
dados = {
    'nomes': 
    [
    "Adolfo Luna",
    "Alexsandro Alves",
    "Alexsandro Silva",
    "Aline Haxkar",
    "Brenda Liberato",
    "Danilo Efrain Ramirez Jara - GLOBANT",
    "Eysson Saucedo Garcia",
    "Fernando Ivan Perez",
    "Frank Rafael",
    "Grecia Maguina Moreno",
    "José Villablanca",
    "Juan Antonio",
    "Juan Antonio Cahuana",
    "Juliana Torres",
    "Juliana Torres G.",
    "Manuel Antonio Guerra Suarez",
    "Manuel Guerra",
    "marcelogomes",
    "Miguel Cruz",
    "Miguel Sanchez Rojas",
    "Oscar Granada",
    "Ricardo Saldanha",
    "Richard Jans Inga Aliaga",
    "Samuel Salirrosas",
    "Samuel Salirrosas Rumay",
    "Sanny",
    "Sophie",
    "Thomas Sanchez",
    "Viviana Quilape"
]
}
# df = pd.DataFrame(dados)

# # Aplicar unificação na mesma coluna
# df_atualizado = unificar_nomes_na_mesma_coluna(df, 'nomes')

# print(df_atualizado)
