from io import StringIO
from matplotlib import pyplot as plt
import requests
import pandas as pd
import commons_yape
import functools
import cache_yape
from typing import List
import graphics
from dotenv import load_dotenv
import os


# Estou adicionado em anexo um arquivo csv que sao dados exportado de um board do trello de uma equipe da minha empresa. Gostaria de analisar um periodo espefico por exemplo, 01/09/2023 até 30/09/2023. Gostaria dos seguintes filtros:
#  • Passado uma etiqueta verifica todos os cards que contém as palavras da etiquetada informada
#  • Queria que verificasse todos os cards criados com essa etiqueta até o inicio do período e que contenham algum tempo em uma das colunas que contenha o nome "Ready for"
#  • Queria que verificasse todos os cards criados durante o periodo até o seu ultimo dia e que contenham algum tempo em uma das colunas que contenha o nome "Ready for"
#  • Queria que verificasse todos os cards finalizado até o ultimo dia o ultimo dia do período
#  • Queria que todo o codigo criado fosse criada de uma forma bem modular, pode ser um arquivo so porem com funcoes bem coesas 
#  • Por fim gerasse algumas visões desses dados

def format_dates(df):
    mask = df['Start date'].apply(check_format)
    df.loc[mask, 'Start date'] = pd.to_datetime(df.loc[mask, 'Start date'], format="%d %b %Y").dt.strftime('%Y-%m-%d')
    df['Start date'] = pd.to_datetime(df['Start date'], errors='coerce')

    mask = df['End date'].apply(check_format)
    df.loc[mask, 'End date'] = pd.to_datetime(df.loc[mask, 'End date'], format="%d %b %Y").dt.strftime('%Y-%m-%d')
    df['End date'] = pd.to_datetime(df['End date'], errors='coerce')

    # Convert the 'Start date' and 'End date' columns to datetime format, if they aren't already
    if df['Start date'].dtype != 'datetime64[ns]':
        df['Start date'] = pd.to_datetime(df['Start date'], format='%d %b %Y', errors='coerce')
    if df['End date'].dtype != 'datetime64[ns]':
        df['End date'] = pd.to_datetime(df['End date'], format='%d %b %Y', errors='coerce')
    return df

 
def __format_dates(df):
    mask = df['Start date'].apply(check_format)
    df.loc[mask, 'Start date'] = pd.to_datetime(df.loc[mask, 'Start date'], format="%d %b %Y").dt.strftime('%Y-%m-%d')
    df['Start date'] = pd.to_datetime(df['Start date'], errors='coerce')

    mask = df['End date'].apply(check_format)
    df.loc[mask, 'End date'] = pd.to_datetime(df.loc[mask, 'End date'], format="%d %b %Y").dt.strftime('%Y-%m-%d')
    df['End date'] = pd.to_datetime(df['End date'], errors='coerce')

    # Convert the 'Start date' and 'End date' columns to datetime format, if they aren't already
    if df['Start date'].dtype != 'datetime64[ns]':
        df['Start date'] = pd.to_datetime(df['Start date'], format='%d %b %Y', errors='coerce')
    if df['End date'].dtype != 'datetime64[ns]':
        df['End date'] = pd.to_datetime(df['End date'], format='%d %b %Y', errors='coerce')
    return df



def __filter_tasks_by_label(data: pd.DataFrame, label: str) -> pd.DataFrame:
    return data[data['Task labels'].str.contains(label, na=False, case=False)].copy()

def __filter_tasks_with_sprint(data: pd.DataFrame) -> pd.DataFrame:
    return data[data['Sprint'].str.contains('24', na=False, case=False)].copy()
    # return data[data['Task labels'].str.contains(label, na=False, case=False)].copy()

def __cards_before_period_with_time(df, start_date):
    # Convert the 'Start date' column to datetime format
    mask = df['Start date'].apply(check_format)
    df.loc[mask, 'Start date'] = pd.to_datetime(df.loc[mask, 'Start date'], format="%d %b %Y").dt.strftime('%Y-%m-%d')
    df['Start date'] = pd.to_datetime(df['Start date'], errors='coerce')
    # Filter rows with a start date before the specified start date
    df_before_start_date = df[df['Start date'] < start_date]
    df_before_start_date['Start date'] = pd.to_datetime(start_date, format="%d/%m/%Y").strftime('%Y-%m-%d')
    df_with_time = df_before_start_date.copy()
    # # Filter rows that have non-null values in columns with the name "Ready for"
    # ready_for_columns = [col for col in df.columns if "Ready for" in col]
    # df_with_time = df_before_start_date.dropna(subset=ready_for_columns, how='all')
    
    
    return df_with_time

def __cards_during_period_with_time(df, start_date, end_date):
    # Convert the 'Start date' column to datetime format
    mask = df['Start date'].apply(check_format)
    df.loc[mask, 'Start date'] = pd.to_datetime(df.loc[mask, 'Start date'], format="%d %b %Y").dt.strftime('%Y-%m-%d')
    df['Start date'] = pd.to_datetime(df['Start date'], errors='coerce')
    start = pd.to_datetime(start_date,format='%d/%m/%Y').strftime('%Y-%m-%d')
    final = pd.to_datetime(end_date,format='%d/%m/%Y').strftime('%Y-%m-%d')

    # Filter rows with a start date within the specified period
    df_during_period = df[(df['Start date'] <= final)]
    # Filter rows that have non-null values in columns with the name "Ready for"
    # ready_for_columns = [col for col in df.columns if "Ready for" in col]
    # df_with_time = df_during_period.dropna(subset=ready_for_columns, how='all')
    
    # return df_with_time
    return df_during_period

def __cards_finished_by_end_date(df, end_date):
    # Convert the 'End date' column to datetime format
    # mask = df['Start date'].apply(check_format)
    # df.loc[mask, 'Start date'] = pd.to_datetime(df.loc[mask, 'Start date'], format="%d %b %Y").dt.strftime('%Y-%m-%d')
    # df['Start date'] = pd.to_datetime(df['Start date'], errors='coerce')
    # start = pd.to_datetime(start_date,format='%d/%m/%Y').strftime('%Y-%m-%d')
    mask = df['End date'].apply(check_format)
    df.loc[mask, 'End date'] = pd.to_datetime(df.loc[mask, 'End date'], format="%d %b %Y").dt.strftime('%Y-%m-%d')
    df['End date'] = pd.to_datetime(df['End date'], errors='coerce')
    final = pd.to_datetime(end_date,format='%d/%m/%Y').strftime('%Y-%m-%d')
    # Filter rows with an end date on or before the specified end date
    # df_finished_by_end_date = df[(df['Start date'] >= final)
    #     (df['Status'].str.contains('Done', case=False, na=False)) & 
    #     (df[df['End date'] <= final])
    # ]
    df_finished_by_end_date = df[df['Status'].str.contains('Done', na=False)].copy()
    df_finished_by_end_date = df[df['End date'] <= final]
    return df_finished_by_end_date

@cache_yape.daily_cache_clear
@functools.lru_cache(maxsize=None)
def __download_csv(url, save_path):
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors

    with open(save_path, 'wb') as file:
        file.write(response.content)

@cache_yape.daily_cache_clear
@functools.lru_cache(maxsize=None)
def __loadDashboardByMonthYear(dashboard, month, year):
    dashboards = __getDashboards()
    dashboard_id = dashboards[dashboard]
    # URL da API
    url = f'https://trello.getnave.com/api/dashboards/{dashboard_id}/export'
    AUTHORIZATION = os.getenv('AUTHORIZATION')
    # Cabeçalho de autorização
    headers = {
        'Authorization': AUTHORIZATION
    }
    
    inicio, fim = commons_yape.get_start_end_dates_format(year,month,'%Y-%m-%d')
    
    # Corpo da solicitação (body)
    payload = {
        'from': inicio,
        'to': fim,
        'type': 'csv'
    }
    # Realiza a solicitação POST
    response = requests.post(url, headers=headers, json=payload)

    # Verifica a resposta
    if response.status_code == 200:
        # A solicitação foi bem-sucedida
        data = response.json()
        return data['url']
    else:   
        print(response)
        exit(0)

def __loadDashboard(dashboard, data_inicio, data_fim):
    dashboards = __getDashboards()
    dashboard_id = dashboards[dashboard]
    # URL da API
    url = f'https://trello.getnave.com/api/dashboards/{dashboard_id}/export'

    AUTHORIZATION = os.getenv('AUTHORIZATION')
    # Cabeçalho de autorização
    headers = {
        'Authorization': AUTHORIZATION
    }
    
    # inicio, fim = commons_yape.get_start_end_dates_format(year,month,'%Y-%m-%d')
    inicio = commons_yape.convert_date_format(data_inicio)
    fim = commons_yape.convert_date_format(data_fim)
    
    # Corpo da solicitação (body)
    payload = {
        'from': inicio,
        'to': fim,
        'type': 'csv'
    }
    # Realiza a solicitação POST
    response = requests.post(url, headers=headers, json=payload)

    # Verifica a resposta
    if response.status_code == 200:
        # A solicitação foi bem-sucedida
        data = response.json()
        return data['url']
    else:   
        print(response)
        exit(0)
    
def __getDashboards():
    # TODO: add os ids de cada dashboard do nave conta yape
    dashboards = {
            'owner_marketplace':'6556179749a6901b4b68605c', 
            'owner_promos':'655d1fe149a6901b4b5286e4',
            'owner_gas':'65561a084faca135b9a13be1',
            'owner_tipodecambio':'655e60780fe84fad40dac901',
            'owner_crm':'6560e39c17729a6b12e5b268',
            'owner_insurance':'655e60e60fe84fad40dacb82',
            'owner_krossboarder-remesas':'655e600549a6901b4b8dca4a',
            'owner_devops':'6569d70ea2ddf02373ec59b6' 
            }
    return dashboards

# Função para verificar se a data segue o formato "%d %b %Y"
def check_format(date_str):
    try:
        pd.to_datetime(date_str, format="%d %b %Y")
        return True
    except:
        return False

@cache_yape.daily_cache_clear
@functools.lru_cache(maxsize=None)
def getCardsByLabel(month, year, labels):
    if not commons_yape.isValidMonth(month, year):
        print('Mês informado é inválido')
        exit(0)

    data = pd.DataFrame()
    for dashboard in list(__getDashboards().keys()):
        url_dashboard = __loadDashboardByMonthYear(dashboard, month, year)   
        __download_csv(url_dashboard, f'{dashboard}-{year}-{month}.csv')
        # Load the CSV file into a DataFrame
        data_dashboard = pd.read_csv(f'{dashboard}-{year}-{month}.csv')
        data_dashboard['Owner'] = dashboard
        data = pd.concat([data, data_dashboard], ignore_index=True)
    
    # Identificando as linhas que têm datas no formato "%d %b %Y"
    mask = data['Start date'].apply(check_format)
    mask = data['End date'].apply(check_format)

    # Convertendo essas datas para o formato "%Y-%m-%d"
    data.loc[mask, 'Start date'] = pd.to_datetime(data.loc[mask, 'Start date'], format="%d %b %Y").dt.strftime('%Y-%m-%d')
    data.loc[mask, 'End date'] = pd.to_datetime(data.loc[mask, 'End date'], format="%d %b %Y").dt.strftime('%Y-%m-%d')

    # Convert 'Start date' and 'End date' to datetime format
    data['Start date'] = pd.to_datetime(data['Start date'], errors='coerce')
    data['End date'] = pd.to_datetime(data['End date'], errors='coerce')
    df = data.copy()
    # filtro_palavras = data['Task labels'].apply(lambda x: any(label in x for label in labels))
    cards_created_in_month = df[(df['Start date'].dt.month <= month) & 
                         (df['Start date'].dt.year <= year) &
                         (~df['Status'].str.contains('Done', case=False, na=False))]
    filtro_labels = cards_created_in_month['Task labels'].apply(lambda x: any(label.lower() in str(x).lower() for label in labels))
    # Aplicando o filtro ao DataFrame
    cards_created_in_month_with_filter = cards_created_in_month[filtro_labels]
    filtro_labels = data['Task labels'].apply(lambda x: any(label.lower() in str(x).lower() for label in labels))
    cards_until_month = data[filtro_labels]
    
    completed_cards = cards_until_month[
        (cards_until_month['Status'].str.contains('Done', case=False, na=False)) & 
        (cards_until_month['End date'].dt.month == month) & 
        (cards_until_month['End date'].dt.year == year)
    ]

    cards_done = completed_cards[['Owner','Task name', 'Task URL', 'Start date', 'End date', 'Status', 'Task labels']]
    cards_created_in_month_with_filter = cards_created_in_month_with_filter[['Owner','Task name', 'Task URL', 'Start date', 'End date', 'Status', 'Task labels']]
    inicio, fim = commons_yape.get_start_end_dates_format(year,month,'%Y-%m-%d')
    return f'periodo: {inicio} - {fim}',len(cards_created_in_month_with_filter), len(cards_done), cards_done, cards_created_in_month_with_filter

def getDashBoardData(owner, data_inicio, data_fim):
    # url_dashboard = __loadDashboard(owner, data_inicio, data_fim)   
    # __download_csv(url_dashboard, f'{owner}-dashboard_temp.csv')
    # Load the CSV file into a DataFrame
    # return pd.read_csv(f'{owner}-dashboard_temp.csv')
    return pd.read_csv('/Users/alexfrisoneyape/Development/EM/owner_marketplace-2023-10.csv')

def getSpotGraph(data_inicio, data_fim, label, data_dashboard):
    #  Filter label
    data_dashboard_filter = __filter_tasks_by_label(data_dashboard.copy(), label)
    # data_dashboard_filter = __filter_tasks_with_sprint(data_dashboard_filter.copy())
    # # cards planejados ou cards que sobraram do ultimo sprint
    # cards_before = __cards_before_period_with_time(data_dashboard_filter.copy(), data_inicio)
    # #  os cards criados durante o período especificado que estao em colunas com o nome "Ready for".
    cards_during = __cards_during_period_with_time(data_dashboard_filter.copy(), data_inicio, data_fim)
    # #  os cards que foram finalizados até a data final do período especificado.
    cards_finished = __cards_finished_by_end_date(data_dashboard_filter.copy(), data_fim)
    # cards_created_all_criteria = pd.concat([cards_before, cards_during], ignore_index=True) 
    cards_during['date'] = cards_during['Start date']
    cards_during['month'] = cards_during['date'].dt.to_period('M')
    tasks_during_per_month = cards_during.groupby('month')['Task name'].count().reset_index()
    tasks_during_per_month = tasks_during_per_month.rename(columns={'index': 'month'})
    tasks_during_per_month.rename(columns={'Task name': 'Tasks Created'}, inplace=True)

    cards_finished['date'] = cards_finished['End date']
    cards_finished['month'] = cards_finished['date'].dt.to_period('M')
    tasks_finished_per_month = cards_finished.groupby('month')['Task name'].count().reset_index()
    cards_finished = cards_finished.rename(columns={'index': 'month'})
    tasks_finished_per_month.rename(columns={'Task name': 'Tasks Finished'}, inplace=True)
    
    merged_grouped_diff = pd.merge(tasks_during_per_month, tasks_finished_per_month, on="month", how='outer')
    merged_grouped_diff.fillna(0, inplace=True)
    merged_grouped_diff['Tasks Finished'] = merged_grouped_diff['Tasks Finished'].astype('Int64')
    merged_grouped_diff['Tasks Created'] = merged_grouped_diff['Tasks Created'].astype('Int64')
    merged_grouped_diff['month'] = merged_grouped_diff['month'].dt.strftime('%b')
    print(merged_grouped_diff)
    print(f" cards criados durante: {len(cards_during)}")
    print(f" cards finalizados: {len(cards_finished)}")
    graphics.plot_bugs_over_time(merged_grouped_diff['Tasks Created'],merged_grouped_diff['Tasks Finished'],merged_grouped_diff['month'])
    # plot_created_vs_finished(cards_created_all_criteria, cards_finished,data_inicio, data_fim)

def getBugsCreatedVsFinished(data_inicio, data_fim, data_dashboard):
    data_dashboard_filter = __filter_tasks_by_label(data_dashboard.copy(), 'Bug')
    cards_during = __cards_during_period_with_time(data_dashboard_filter.copy(), data_inicio, data_fim)
    cards_finished = __cards_finished_by_end_date(data_dashboard_filter.copy(), data_fim)
    cards_during['date'] = cards_during['Start date']
    cards_during['month'] = cards_during['date'].dt.to_period('M')
    tasks_during_per_month = cards_during.groupby('month')['Task name'].count().reset_index()
    tasks_during_per_month = tasks_during_per_month.rename(columns={'index': 'month'})
    tasks_during_per_month.rename(columns={'Task name': 'Tasks Created'}, inplace=True)

    cards_finished['date'] = cards_finished['End date']
    cards_finished['month'] = cards_finished['date'].dt.to_period('M')
    tasks_finished_per_month = cards_finished.groupby('month')['Task name'].count().reset_index()
    cards_finished = cards_finished.rename(columns={'index': 'month'})
    tasks_finished_per_month.rename(columns={'Task name': 'Tasks Finished'}, inplace=True)
    
    merged_grouped_diff = pd.merge(tasks_during_per_month, tasks_finished_per_month, on="month", how='outer')
    merged_grouped_diff.fillna(0, inplace=True)
    merged_grouped_diff['Tasks Finished'] = merged_grouped_diff['Tasks Finished'].astype('Int64')
    merged_grouped_diff['Tasks Created'] = merged_grouped_diff['Tasks Created'].astype('Int64')
    merged_grouped_diff['month'] = merged_grouped_diff['month'].dt.strftime('%b')
    print(merged_grouped_diff)
    print(f" cards criados durante: {len(cards_during)}")
    print(f" cards finalizados: {len(cards_finished)}")
    graphics.plot_bugs_over_time(merged_grouped_diff['Tasks Created'],merged_grouped_diff['Tasks Finished'],merged_grouped_diff['month'],'Bugs')

def getDTCreatedVsFinished(data_inicio, data_fim, data_dashboard):
    data_dashboard_filter = __filter_tasks_by_label(data_dashboard.copy(), 'Debt')
    cards_during = __cards_during_period_with_time(data_dashboard_filter.copy(), data_inicio, data_fim)
    cards_finished = __cards_finished_by_end_date(data_dashboard_filter.copy(), data_fim)
    cards_during['date'] = cards_during['Start date']
    cards_during['month'] = cards_during['date'].dt.to_period('M')
    tasks_during_per_month = cards_during.groupby('month')['Task name'].count().reset_index()
    tasks_during_per_month = tasks_during_per_month.rename(columns={'index': 'month'})
    tasks_during_per_month.rename(columns={'Task name': 'Tasks Created'}, inplace=True)

    cards_finished['date'] = cards_finished['End date']
    cards_finished['month'] = cards_finished['date'].dt.to_period('M')
    tasks_finished_per_month = cards_finished.groupby('month')['Task name'].count().reset_index()
    cards_finished = cards_finished.rename(columns={'index': 'month'})
    tasks_finished_per_month.rename(columns={'Task name': 'Tasks Finished'}, inplace=True)
    
    merged_grouped_diff = pd.merge(tasks_during_per_month, tasks_finished_per_month, on="month", how='outer')
    merged_grouped_diff.fillna(0, inplace=True)
    merged_grouped_diff['Tasks Finished'] = merged_grouped_diff['Tasks Finished'].astype('Int64')
    merged_grouped_diff['Tasks Created'] = merged_grouped_diff['Tasks Created'].astype('Int64')
    merged_grouped_diff['month'] = merged_grouped_diff['month'].dt.strftime('%b')
    print(merged_grouped_diff)
    print(f" cards criados durante: {len(cards_during)}")
    print(f" cards finalizados: {len(cards_finished)}")
    graphics.plot_bugs_over_time(merged_grouped_diff['Tasks Created'],merged_grouped_diff['Tasks Finished']*-1,merged_grouped_diff['month'],'Deudas Tecnicas')