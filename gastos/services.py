import functools
import bc
import commons
import pandas as pd
import subprocess
from pynubank import Nubank
import json
from datetime import datetime
import numpy as np
import cache_gastos
from dotenv import load_dotenv
import os

load_dotenv('.env')

base_values = {
        "Papel A4": 20, "Tinta de impressora": 50, "Mouse": 30, "Teclado": 40, "Cadeira": 150,
        "Mesa": 300, "Software de gestão": 500, "Café": 10, "Água mineral": 12, "Lâmpada": 8,
        "Filtro de linha": 25, "Estabilizador": 70, "Monitor": 400, "Notebook": 2000,
        "Roteador": 120, "Switch": 150, "Cabo HDMI": 15, "Cabo USB": 10, "Caneta": 1,
        "Marcador de texto": 3, "Pasta": 5, "Clip": 1, "Grampeador": 10, "Grampos": 2,
        "Apagador": 4, "Quadro branco": 80, "Projetor": 800, "Telefone": 150,
        "Headset": 100, "Webcam": 250, "Licença de software": 600, "Extensão elétrica": 20,
        "Carregador": 40, "Bateria": 90, "Pendrive": 30, "HD externo": 250, "SSD": 300,
        "Placa de vídeo": 1200, "Placa-mãe": 500, "Processador": 800,"Suporte para monitor": 50, "Fonte de alimentação": 200, "Cooler": 70, "Capa para notebook": 30, 
        "Fone de ouvido": 80, "Microfone": 90, "Mochila": 120, "Case para pendrive": 10, "Película para tela": 15,
        "Protetor de teclado": 10, "Mousepad": 20, "Suporte para notebook": 60, "Limpeza de equipamentos": 100,
        "Instalação de software": 150, "Atualização de hardware": 500, "Licença de antivírus": 80, "Subscrição de cloud": 20,
        "Treinamento técnico": 300, "Consultoria IT": 1000, "Upgrade de memória RAM": 300, "Placa de rede": 150,
        "Antena wifi": 50, "Cabo de rede": 15, "Patch panel": 200, "Rack para servidores": 1500,"Scanner": 450, "Impressora": 800, "Cadeira ergonômica": 400, "Mesa ajustável": 700,
        "Suporte para celular/tablet": 35, "Carregador wireless": 60, "Webcam HD": 350,
        "Refil de tinta para impressora": 100, "Cartucho de toner": 250, "Papel fotográfico": 30,
        "Envelopes": 15, "Etiquetas": 20, "Sistema operacional": 800, "Pacote Office": 500,
        "Software de design gráfico": 2000, "Firewall": 300, "Software de backup": 150,
        "Serviço de manutenção": 250, "Garantia estendida": 150, "Aluguel de equipamento": 100,
        "Serviço de limpeza": 80, "Conexão VPN": 50, "Calculadora": 25, "Organizador de mesa": 40, "Relógio de parede": 30, "Calendário": 10,
        "Bloco de anotações": 15, "Post-it": 10, "Porta-canetas": 12, "Servidor": 3000, "Unidade de fita de backup": 1500,
        "Hub USB": 45, "Repetidor de sinal": 90, "Máquina de café": 400, "Geladeira de escritório": 600,
        "Ar condicionado portátil": 700, "Estante para livros": 250, "Armário com chave": 300, "Sofá": 500,
        "Planta de escritório": 50, "Biombo": 100, "Software de CRM": 1000, "Software de ERP": 1500, 
        "Plataforma de e-commerce": 1200, "Sistema de videoconferência": 500, "Ferramenta de automação de marketing": 800,
        "Serviço de segurança": 200, "Monitoramento 24h": 100, "Reciclagem de equipamentos": 50,
        "Treinamento de segurança": 300, "Auditoria externa": 1000, "Relógio de ponto": 400, "Camera de segurança": 300,
        "Gravador de voz": 80, "Disco rígido NAS": 800, "Rack para rede": 250, "Furador de papel": 20,
        "Encadernadora": 150, "Laminadora": 200, "Scanner de mão": 120, "Sistema de PA": 500,
        "Caixa de som para conferência": 220, "Modem": 100, "Receptor Wi-Fi": 80, "Rolo de etiquetas": 20,
        "Sistema de alarme": 400, "Estação de carregamento": 60, "Kit de ferramentas de TI": 150,
        "Selo de segurança": 5, "Tela de projeção": 150, "Conversor digital": 50, "Mesa digitalizadora": 300,
        "Kit primeiros socorros": 40, "Extintor": 80, "Kit limpeza de PC": 30, "Pincel atômico": 5, "Régua": 4, "Compasso": 15, "Tesoura": 6, "Lápis": 1, "Borracha": 2, "Cola": 8,
        "Microondas": 300, "Chaleira elétrica": 80, "Ventilador": 100, "Purificador de ar": 150, "Desumidificador": 200,
        "Sistema de som": 500, "Interfone": 120, "Cadeira de visitante": 200, "Mesa de reunião": 800,
        "Armário para arquivo": 400, "Gaveteiro": 250, "Sofá-cama": 700, "Puff": 150, "Poltrona reclinável": 450,
        "Software de contabilidade": 1200, "Ferramenta de gestão de projetos": 700, "Plataforma de e-learning": 900,
        "Software de edição de vídeo": 1500, "Sistema de gestão de RH": 1100, "Catering para reuniões": 200,
        "Serviço de jardinagem": 300, "Manutenção de elevador": 500, "Serviço de correio": 50,
        "Impressão em grande formato": 70, "Relógio biométrico": 600, "Máquina de xerox": 1000, "Agenda": 20,
        "Cortina para janela": 150, "Papel reciclado": 25, "Adesivo decorativo": 50, "Porta retrato": 20,
        "Sistema de videovigilância": 1500, "Iluminação LED": 100, "Luminária de mesa": 60, "Relógio digital": 50,
        "Balde de gelo": 40, "Carimbo": 15, "Etiqueta adesiva": 10, "Papel colorido": 30, "Envelope timbrado": 40,
        "Carrinho de arquivo": 180, "Tela anti-reflexo": 60, "Suporte para pés": 45, "Pasta sanfonada": 35,
        "Máquina de selar": 150, "Fita adesiva": 5, "Porta-recados": np.random.uniform(20, 30), "Organizador de cabos": np.random.uniform(20, 30),
        "Lixeira": np.random.uniform(20, 30), "Descanso para os pés": np.random.uniform(20, 30),
        "Capa para cadeira": np.random.uniform(20, 30), "Suporte para documentos": np.random.uniform(20, 30),
        "Kit de limpeza para tela": np.random.uniform(20, 30), "Porta-revistas": np.random.uniform(20, 30),
        "Suporte para guarda-chuva": np.random.uniform(20, 30), "Almofada para cadeira": np.random.uniform(20, 30),
        "Gancho para bolsa": np.random.uniform(20, 30), "Tapete antiestático": np.random.uniform(20, 30),
        "Luminária USB": np.random.uniform(20, 30), "Suporte para copos": np.random.uniform(20, 30),
        "Plugin para navegador": np.random.uniform(20, 30), "Extensão para software de edição": np.random.uniform(20, 30),
        "Tema para apresentações": np.random.uniform(20, 30), "Fontes premium": np.random.uniform(20, 30),
        "Ícones para design": np.random.uniform(20, 30), "Caneca personalizada": np.random.uniform(20, 30),
        "Porta-caneca aquecido": np.random.uniform(20, 30), "Protetor auricular": np.random.uniform(20, 30),
        "Máscara de dormir": np.random.uniform(20, 30), "Garrafa térmica": np.random.uniform(20, 30),
        "Adesivo anti-luz azul": np.random.uniform(20, 30), "Adesivo para webcam": np.random.uniform(20, 30),
        "Suporte para celular": np.random.uniform(20, 30), "Capa para tablet": np.random.uniform(20, 30),
        "Cordão para crachá": np.random.uniform(20, 30), "Protetor de tomada": np.random.uniform(20, 30),
        "Bloqueador de janela": np.random.uniform(20, 30), "Porta-lápis estilizado": np.random.uniform(20, 30),
        "Adaptador Bluetooth": np.random.uniform(20, 30), "Suporte para headset": np.random.uniform(20, 30),
        "Mini ventilador USB": np.random.uniform(20, 30), "Bloco de rascunho": np.random.uniform(20, 30),
        "Separador de páginas": np.random.uniform(20, 30), "Mousepad ergonômico": np.random.uniform(20, 30),
        "Pasta organizadora": np.random.uniform(20, 30), "Fita decorativa": np.random.uniform(20, 30),
        "Lápis de cor": np.random.uniform(20, 30), "Pincel para quadro": np.random.uniform(20, 30),
        "Caneta de gel": np.random.uniform(20, 30), "Caderno universitário": np.random.uniform(20, 30),
        "Mini caixa de som": np.random.uniform(20, 30), "Apoio para punho": np.random.uniform(20, 30),
        "Capa para mouse": np.random.uniform(20, 30), "Marcador permanente": np.random.uniform(20, 30),
        "Carregador portátil": np.random.uniform(20, 30), "Organizador de fios": np.random.uniform(20, 30),
        "Clips coloridos": np.random.uniform(10, 20), "Adesivos decorativos": np.random.uniform(10, 20),
        "Porta-clipes": np.random.uniform(10, 20), "Canetas coloridas": np.random.uniform(10, 20),
        "Apontador": np.random.uniform(10, 20), "Estojo": np.random.uniform(10, 20), "Porta-papel": np.random.uniform(10, 20),
        "Almofada decorativa": np.random.uniform(10, 20), "Tapete pequeno": np.random.uniform(10, 20),
        "Descanso de pulso": np.random.uniform(10, 20), "Gancho autoadesivo": np.random.uniform(10, 20),
        "Separador de gavetas": np.random.uniform(10, 20), "Organizador de gavetas": np.random.uniform(10, 20),
        "Suporte para livros": np.random.uniform(10, 20), "Tema para sistema operacional": np.random.uniform(10, 20),
        "Fontes básicas": np.random.uniform(10, 20), "Pacote de ícones simples": np.random.uniform(10, 20),
        "Plugin básico para software de design": np.random.uniform(10, 20),
        "Extensão para software de produtividade": np.random.uniform(10, 20), "Caneca temática": np.random.uniform(10, 20),
        "Porta-lápis temático": np.random.uniform(10, 20), "Adesivo para notebook": np.random.uniform(10, 20),
        "Capa protetora para teclado": np.random.uniform(10, 20), "Mousepad temático": np.random.uniform(10, 20),
        "Suporte simples para tablet": np.random.uniform(10, 20), "Capa protetora para mouse": np.random.uniform(10, 20),
        "Bloco autoadesivo": np.random.uniform(10, 20), "Cordão para crachá estilizado": np.random.uniform(10, 20),
        "Marcador de página": np.random.uniform(10, 20), "Pasta catálogo": np.random.uniform(10, 20),
        "Quadro de avisos pequeno": np.random.uniform(10, 20), "Suporte para celular ajustável": np.random.uniform(10, 20),
        "Espelho de mesa": np.random.uniform(10, 20), "Carregador USB simples": np.random.uniform(10, 20),
        "Adaptador de tomada": np.random.uniform(10, 20), "Fita dupla face": np.random.uniform(10, 20),
        "Película protetora para celular": np.random.uniform(10, 20), "Etiquetas coloridas": np.random.uniform(10, 20),
        "Pasta plástica": np.random.uniform(10, 20), "Copo retrátil": np.random.uniform(10, 20),
        "Adaptador para fone de ouvido": np.random.uniform(10, 20), "Suporte para sacola": np.random.uniform(10, 20),
        "Lápis estilizado": np.random.uniform(10, 20), "Borracha temática": np.random.uniform(10, 20),
        "Tapa olhos para descanso": np.random.uniform(10, 20), "Squeeze para água": np.random.uniform(10, 20),
        "Protetor para câmera de notebook": np.random.uniform(10, 20), "Porta-copos estilizado": np.random.uniform(10, 20),
        "Suporte para headset ajustável": np.random.uniform(10, 20), "Fone de ouvido simples": np.random.uniform(10, 20),
        "Clips simples": np.random.uniform(0, 10), "Post-it": np.random.uniform(0, 10),
        "Elásticos": np.random.uniform(0, 10), "Lápis simples": np.random.uniform(0, 10),
        "Borracha branca": np.random.uniform(0, 10), "Régua pequena": np.random.uniform(0, 10), 
        "Apontador simples": np.random.uniform(0, 10), "Bloco de anotações": np.random.uniform(0, 10),
        "Caneta esferográfica": np.random.uniform(0, 10), "Marcador simples": np.random.uniform(0, 10),
        "Pasta transparente": np.random.uniform(0, 10), "Envelope pequeno": np.random.uniform(0, 10),
        "Etiquetas adesivas": np.random.uniform(0, 10), "Pasta elástica": np.random.uniform(0, 10),
        "Chaveiro temático": np.random.uniform(0, 10), "Adesivo pequeno": np.random.uniform(0, 10),
        "Porta-caneta simples": np.random.uniform(0, 10), "Porta-clips simples": np.random.uniform(0, 10),
        "Suporte para papel": np.random.uniform(0, 10), "Marcador de livro": np.random.uniform(0, 10),
        "Protetor de cabo": np.random.uniform(0, 10), "Adaptador de tomada simples": np.random.uniform(0, 10),
        "Cordão simples": np.random.uniform(0, 10), "Porta-lápis pequeno": np.random.uniform(0, 10),
        "Copo plástico": np.random.uniform(0, 10), "Caneta marca texto": np.random.uniform(0, 10),
        "Bloco autoadesivo pequeno": np.random.uniform(0, 10), "Papel reciclado": np.random.uniform(0, 10),
        "Envelopes coloridos": np.random.uniform(0, 10), "Papel fotográfico": np.random.uniform(0, 10),
        "Adesivo redondo": np.random.uniform(0, 10), "Caneta gel": np.random.uniform(0, 10),
        "Bloco de rascunho pequeno": np.random.uniform(0, 10), "Clips colorido": np.random.uniform(0, 10),
        "Etiqueta para nome": np.random.uniform(0, 10), "Adesivo para identificação": np.random.uniform(0, 10),
        "Caneta retrátil": np.random.uniform(0, 10), "Lápis de cor básico": np.random.uniform(0, 10),
        "Capa para bloco de notas": np.random.uniform(0, 10), "Envelope para CD": np.random.uniform(0, 10),
        "Adesivo decorativo pequeno": np.random.uniform(0, 10), "Bloco de notas temático": np.random.uniform(0, 10),
        "Caneta ponta fina": np.random.uniform(0, 10), "Clip magnético": np.random.uniform(0, 10),
        "Marcador de página colorido": np.random.uniform(0, 10), "Envelope decorado": np.random.uniform(0, 10),
        "Computador de mesa": np.random.uniform(800, 1200),
        "Impressora multifuncional": np.random.uniform(500, 800),
        "Telefone IP": np.random.uniform(500, 700),
        "Cadeira ergonômica": np.random.uniform(500, 1000),
        "Projetor": np.random.uniform(700, 1000),
        "Impressora 3D": np.random.uniform(3000, 5000),
        "Servidor de rede": np.random.uniform(4000, 7000),
        "Sistema de videoconferência": np.random.uniform(3000, 6000),
        "Estação de trabalho de alto desempenho": np.random.uniform(8000, 12000)
    }

def _calTax(items):

    IRPF = 0.2750
    IOF_CARD = 0.0638
    IOF_BANK = 0.0110
    SPREAD_BANK = 0.06

    
    total_impostos = 0
    dados_para_planilha_de_reembolso = []
    last_data = ''
    for item in items:
        item_para_reembolso = {}
        # obter a cotacao do dolar da data oficial, caso a data seja em um fds será calculada a data de sexta
        data = item['data'].replace('-','/')
        cotacao_oficial = bc.get_dolar_cotacao(data)
        valor_em_dolar = round(float(item['valor_em_real'])/cotacao_oficial,2)
        valor_em_dolar_com_IRPF = round(valor_em_dolar * (1+IRPF),2)
        valor_em_dolar_com_IOF_CARD = round(valor_em_dolar_com_IRPF * (1+IOF_CARD),2)
        valor_em_dolar_com_IOF_BANK = round(valor_em_dolar_com_IOF_CARD * (1+IOF_BANK),2)
        valor_em_dolar_com_spread = round(valor_em_dolar_com_IOF_BANK * (1+SPREAD_BANK),2)
        valor_declarado = valor_em_dolar_com_spread
        total_imposto = valor_declarado - float(item['valor_em_dolar'])
        total_imposto = round(total_imposto,2)
        item_para_reembolso['data'] = data
        item_para_reembolso['descricao'] = item['descricao']
        item_para_reembolso['numero de dias'] = 1
        item_para_reembolso['importe unitario'] = f'{valor_em_dolar}'.replace('.',',')
        item_para_reembolso['total usd'] = f'{valor_em_dolar}'.replace('.',',')
        # item_para_reembolso['total_imposto'] = total_imposto
        dados_para_planilha_de_reembolso.append(item_para_reembolso)
        total_impostos += total_imposto
        last_data = data
    item_espaco = {}
    item_gasto_sem_comprovantes = {}
    item_espaco['data'] = ''
    item_espaco['descricao'] = ''
    item_espaco['numero de dias'] = ''
    item_espaco['importe unitario'] = ''
    item_espaco['total usd'] = ''
    dados_para_planilha_de_reembolso.append(item_espaco)
    item_gasto_sem_comprovantes['data'] = data
    item_gasto_sem_comprovantes['descricao'] = 'Impuesto Brazil para o recebimento de valor de rendicion de gastos'
    item_gasto_sem_comprovantes['numero de dias'] = 1
    item_gasto_sem_comprovantes['importe unitario'] = ''
    item_gasto_sem_comprovantes['total usd'] = f'{total_impostos}'.replace('.',',')
    dados_para_planilha_de_reembolso.append(item_gasto_sem_comprovantes)
    return dados_para_planilha_de_reembolso, f'{round(total_impostos,2)}'.replace('.',',')

def exportSpreadsheet(str,path_excel_file):
    items = commons.create_data_from_filenames(str)
    print(items)
    data, total_tax = _calTax(items)
    df = pd.DataFrame(data)
    print(df)
    # Exportando o DataFrame para Excel
    df.to_excel(path_excel_file, index=False)
    # Abrir o arquivo
    subprocess.run(["open", path_excel_file])

@cache_gastos.daily_cache_clear
@functools.lru_cache(maxsize=None)
def __getRealDataInNubank():
    nu = Nubank()
    NB_LOGIN = os.getenv('NB_LOGIN')
    NB_PASSWORD = os.getenv('NB_PASSWORD')
    nu.authenticate_with_cert(NB_LOGIN, NB_PASSWORD, '/Users/alexfrisoneyape/Development/EM-projects/nubank/nubank/cert.p12')
    card_data = nu.get_card_statements()
    with open('card_data.json', 'w') as file:
        json.dump(card_data, file, indent=4)
    return card_data

def getCardExtract(data_inicio,data_fim, threshold):
    card_data = __getRealDataInNubank()
    # with open('/Users/alexfrisoneyape/Development/EM/card_data.json', 'r') as file:
    #     card_data = json.load(file)
    data = __get_top_transactions_by_period(data_inicio,data_fim,card_data)
    df = pd.DataFrame(data)
    df['amount'] = df['amount'] / 100
    df = df[~df['description'].str.contains('escrit', case=False, na=False)]
    df['valor carne-leao'] = df['amount'] * 0.275
    df['valor carne-leao'] = round(df['valor carne-leao'],2)
    df['cumulative_sum'] = round(df['valor carne-leao'].cumsum(),2)
    selected_transactions = df[df['cumulative_sum'] <= threshold]
    # Aplicar a função à coluna "amount" para gerar a coluna "item_escritorio"
    selected_transactions['item_escritorio'] = selected_transactions['amount'].apply(lambda x: find_closest_office_item(x * 100))
    # Ordenar as transações filtradas pelo valor em ordem decrescente
    selected_transactions = selected_transactions.sort_values(by='time', ascending=False)
    selected_transactions["time"] = pd.to_datetime(selected_transactions["time"], format='ISO8601').dt.strftime('%d/%m/%Y')
    df_to_excel = selected_transactions[["time","item_escritorio", "amount","description"]]
    df_to_excel.to_excel('/Users/alexfrisoneyape/Development/EM-projects/gastos/output/gastos_escritorio.xlsx', index=False)


def __get_top_transactions_by_period(start_date: str, end_date: str, card_data):
    # Converter as datas fornecidas para objetos datetime
    start_datetime = datetime.strptime(start_date, '%d/%m/%Y')
    end_datetime = datetime.strptime(end_date, '%d/%m/%Y')

    # Filtrar transações dentro do período especificado
    filtered_transactions = [
        transaction for transaction in card_data
        if start_datetime <= datetime.fromisoformat(transaction['time'].split('T')[0]) <= end_datetime
    ]

    # Ordenar as transações filtradas pelo valor em ordem decrescente
    top_transactions = sorted(filtered_transactions, key=lambda x: x['amount'], reverse=True)

    # Extrair as informações relevantes para as transações mais caras
    top_transactions_info = [
        {
            "description": transaction["description"],
            "amount": transaction["amount"],
            "time": transaction["time"],
            "category": transaction["title"]
        }
        for transaction in top_transactions
    ]
    
    return top_transactions_info

class ItemsQueue:
    def __init__(self):
        self.queue = []
    
    def add(self, item):
        """Add a new item to the queue."""
        self.queue.append(item)
        # Ensure the queue doesn't exceed 50 items
        while len(self.queue) > 50:
            self.queue.pop(0)
    
    def get_last_itens(self):
        return self.queue

# Adaptação da função para diversificar os itens retornados
previous_item = None
queue = ItemsQueue()

def find_closest_office_item(amount_in_cents):
    # Valores aproximados para os itens base (em reais)
    
    global previous_item, queue
    # Converter a quantia de centavos para reais
    amount = amount_in_cents / 100
    
    # Encontrar o item de escritório mais próximo
    sorted_items = sorted(base_values.items(), key=lambda x: x[1], reverse=True)
    
    # Filter out items that exceed the given amount or are in the last_five_items list
    filtered_items = [item for item in sorted_items if item[1] <= amount and item[0] not in queue.get_last_itens()]
    if filtered_items:
        queue.add(filtered_items[0][0])
        return f"{filtered_items[0][0]} para escritorio"
    
    return 'Não foi encontrado um item de escritorio não repetido'

