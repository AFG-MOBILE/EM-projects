import metric_log
import trello
def execucao_diaria():
    # list_id = "632b5ec4ee1230008bd34d7f"  #marketplace 
    list_id = "620cbb3308424a3f218f092a" #promos
    # list_id = "61ae4a1ca02160403e4daeda" #devops
    from_date = '2023-12-01'  # Formato aaaa-mm-dd
    to_date = '2024-01-31'    # Formato aaaa-mm-dd
    # board_id = '632b5ec4ee1230008bd34d6d' #marketplace
    board_id = '620c10ba5cfd7d4ce889d72a' #promos
    # board_id = '61ae4a1ca02160403e4daece' #dev ops solicitudes
    filename = 'detailed_interactions_cards_done_list_promos.xlsx'

    trello.generateMetricsTrello(board_id,list_id, filename,from_date, to_date)


if __name__ == "__main__":
    metric_log.config_metric_log()
    execucao_diaria()