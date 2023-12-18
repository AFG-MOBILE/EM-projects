import metric_log
import pandas as pd
import services
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font

MONTH = 10
YEAR = 2023


if __name__ == "__main__":
    metric_log.config_metric_log()
    periodo, df = services.getInfoDevOps(MONTH, YEAR)
    print(df)