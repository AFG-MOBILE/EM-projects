import metric_log
import services

MONTH = 10
YEAR = 2023

def execucao_diaria():
    result = services.checkNewServicesWithoutOwners()
    print(result)

if __name__ == "__main__":
    metric_log.config_metric_log()
    execucao_diaria()