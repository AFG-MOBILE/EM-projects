import metric_log
import pandas as pd
import services
import subprocess

MONTH = 9
YEAR = 2023

def checkDeckMetrics():
    periodo, metrics, metrics_raw = services.getAllMetrics(MONTH,YEAR)
    print(metrics)
    metrics.to_excel('/Users/alexfrisoneyape/Development/EM-projects/metrics/metrics.xlsx')
    subprocess.run(['open', '-a', 'Microsoft Excel', '/Users/alexfrisoneyape/Development/EM-projects/metrics/metrics.xlsx' ])
    
if __name__ == "__main__":
    metric_log.config_metric_log()
    
    team_ids = ['43331478','89131764','211090647','303557783','393516834','497712838','1011864046','1124213248','1490690188','1809319925','1831290743']
    chapter_ids = ['43331478','89131764','211090647','303557783','393516834','497712838','1011864046','1124213248','1490690188','1809319925','1831290743']
    contributor = {'name':'Ricardo', 'id': ['1180048021']}
    df_metrics = services.createInfographicContributor(MONTH, YEAR, contributor, team_ids, chapter_ids)     
    # services.createSlideForShowcase('/Users/alexfrisoneyape/Development/EM-projects/metrics/metricas.xlsx','Noviembre')
    