import metric_log
import pandas as pd
import services

MONTH = 10
YEAR = 2023

def checkDeckMetrics():
    periodo, metrics, metrics_raw = services.getAllMetrics(MONTH,YEAR)
    print(metrics)
    metrics.to_excel('/Users/alexfrisoneyape/Development/EM/metricas/metrics.xlsx')
    
if __name__ == "__main__":
    metric_log.config_metric_log()
    
    services.checkMetricsByMonth() 