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
    
    arquivo_template = '/Users/alexfrisoneyape/Development/EM-projects/metrics/template_informe_mensal.html'
    # Exemplo de uso da função
    destaques_semana = [
        'Conquista de um novo cliente importante.',
        'Lançamento bem-sucedido do novo produto X.',
        'Progresso significativo no projeto Y.',
        # Adicione outros destaques conforme necessário
    ]
    services.generateNewsletter(arquivo_template,destaques_semana)