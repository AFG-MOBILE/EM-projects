import metric_log
import services
import subprocess

MONTH = 9
YEAR = 2023

def checkDeckMetrics():
    periodo, metrics, metrics_raw = services.getAllMetrics(MONTH,YEAR)
    print(metrics)
    metrics.to_excel('/Users/alexfrisoneyape/Development/EM-projects/metrics/metrics.xlsx')
    metrics_raw.to_excel(f'/Users/alexfrisoneyape/Development/EM-projects/metrics/metrics_raw_{MONTH}_{YEAR}.xlsx')
    file = f'/Users/alexfrisoneyape/Development/EM-projects/metrics/metrics_raw_{MONTH}_{YEAR}.xlsx'
    subprocess.run(['open', '-a', 'Microsoft Excel', file ])
    
if __name__ == "__main__":
    metric_log.config_metric_log()
    # checkDeckMetrics()
    df_metrics = services.checkMetricsByMonth([12,1], [2023, 2024]) 
    services.createSlideForShowcase('/Users/alexfrisoneyape/Development/EM-projects/metrics/metricas.xlsx','Enero')
    
#     minutes = [45,
# 1253,
# 27,
# 82,
# 94,
# 215,
# 81,
# 119,
# 21893,
# 10312,
# 3336,
# 11246]
#     for minute in minutes:
#         print(commons_yape.formatTime(minute))
    