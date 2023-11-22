import logging
from datetime import datetime

def config_metric_log():
    filename = f"/Users/alexfrisoneyape/Development/EM-projects/logs/{datetime.today().strftime('%Y-%m-%d')} - metrics.log"
    logging.basicConfig(filename=filename, level=logging.CRITICAL,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
def log_critical(msg):
    logging.critical(msg)