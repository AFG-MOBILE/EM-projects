import metric_log
import pandas as pd
import services
import subprocess

MONTH = 12
YEAR = 2023

def checkDeckMetrics():
    periodo, metrics, metrics_raw = services.getAllMetrics(MONTH,YEAR)
    print(metrics)
    metrics.to_excel('/Users/alexfrisoneyape/Development/EM-projects/metrics/metrics.xlsx')
    subprocess.run(['open', '-a', 'Microsoft Excel', '/Users/alexfrisoneyape/Development/EM-projects/metrics/metrics.xlsx' ])
    
if __name__ == "__main__":
    metric_log.config_metric_log()
    
    # df_metrics = services.checkMetricsByMonth([11,12], YEAR) 
    # services.createSlideForShowcase('/Users/alexfrisoneyape/Development/EM-projects/metrics/metricas.xlsx','Diciembre')
    services.getInfoReleasesYear()
    