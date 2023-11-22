import metric_log
import pandas as pd
import services
from dotenv import load_dotenv
import os

MONTH = 10
YEAR = 2023

def checkDeckMetrics():
    periodo, metrics, metrics_raw = services.getAllMetrics(MONTH,YEAR)
    print(metrics)
    metrics.to_excel('/Users/alexfrisoneyape/Development/EM/metricas/metrics.xlsx')
    
if __name__ == "__main__":
    metric_log.config_metric_log()
    # services.getBugsGraph('01/08/2023','01/11/2023', 'owner_marketplace')
    # Carregar variáveis de ambiente a partir do arquivo .env
    load_dotenv('.env')

    # Lendo as chaves de API e tokens do arquivo .env
    api_key = os.getenv('DD_API_KEY')
    print(api_key)