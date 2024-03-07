import metric_log
import trello
import pandas as pd
import subprocess

if __name__ == "__main__":
    metric_log.config_metric_log()
    # execucao_diaria()
    from_date = '2023-08-01'  # Formato aaaa-mm-dd
    to_date = '2024-02-29'    # Formato aaaa-mm-dd
    filename = 'detailed_interactions_cards_done_list_'
    teams = [
                {
                "name": "Marketplace",
                "list_id": "632b5ec4ee1230008bd34d7f",
                "board_id": "632b5ec4ee1230008bd34d6d",
                }
                ,
                {
                "name": "Promos",
                "list_id": "620cbb3308424a3f218f092a",
                "board_id": "620c10ba5cfd7d4ce889d72a",
                }
                ,
                {
                "name": "Gas",
                "list_id": "64f1ea80397bb170a09d94d6",
                "board_id": "64f1e97949e709e5e6b71a5c",
                }
                ,
                {
                "name": "Ticketing",
                "list_id": "655e08356fcd465b2586172f",
                "board_id": "65553c0e788023b27f5a8753",
                }
                ,
                {
                "name": "Gaming & Giftcards",
                "list_id": "642b603196ce37ad17d7fbf6",
                "board_id": "642b54df3e995f8aaa97429b",
                }
            ]
    df_general = []
    for team in teams:
        print(f"Getting {team['name']} data……")
        df = trello.generateMetricsTrello(team['name'],team['board_id'],team['list_id'], f"{filename}{team['name']}.xlsx",from_date, to_date)
        df_general.append(df)
    
    # Concatena todos os DataFrames na lista para criar um DataFrame total
    df_total = pd.concat(df_general, ignore_index=True)
    filename_final = '/Users/alexfrisoneyape/Development/EM-projects/metrics/Interactions_Cards_Done.xlsx'
    df_total.to_excel(filename_final)
    subprocess.run(['open', '-a', 'Microsoft Excel', filename_final ])