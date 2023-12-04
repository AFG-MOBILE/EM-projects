from datetime import datetime, timedelta
from collections import Counter
import math



def get_start_end_dates(year, month):
    # Data de início é o primeiro dia do mês
    start_date = datetime(year, month, 1)
    
    # Se o mês for dezembro (12), o próximo mês é janeiro (1) do próximo ano
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        # Data de fim é o dia anterior ao primeiro dia do próximo mês
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    # Formatando as datas no formato desejado
    formatted_start = start_date.strftime('%d/%m/%y')
    formatted_end = end_date.strftime('%d/%m/%y')
    final_date = datetime.strptime(formatted_end, '%d/%m/%y')
    if final_date > datetime.now():
        formatted_end = datetime.now().strftime('%d/%m/%y')
    return formatted_start, formatted_end
    

def get_start_end_dates_format(year, month, format):
    # Data de início é o primeiro dia do mês
    start_date = datetime(year, month, 1)
    
    # Se o mês for dezembro (12), o próximo mês é janeiro (1) do próximo ano
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        # Data de fim é o dia anterior ao primeiro dia do próximo mês
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    # Formatando as datas no formato desejado
    formatted_start = start_date.strftime(format)
    formatted_end = end_date.strftime(format)
    final_date = datetime.strptime(formatted_end, '%Y-%m-%d')
    if final_date > datetime.now():
        formatted_end = datetime.now().strftime('%Y-%m-%d')
    return formatted_start, formatted_end

def isValidMonth(month, year):
    start_date = datetime(year, month, 1)
    if start_date > datetime.now():
        return False
    return True

def formatTime(minutos):
    if not isinstance(minutos, int) and not isinstance(minutos, float)  or minutos == 0 or math.isnan(minutos):
        return '0m'

    minutos = int(minutos)
    # Calculando a quantidade de dias, horas e minutos
    dias = minutos // (24 * 60)
    minutos_restantes = minutos % (24 * 60)
    horas = minutos_restantes // 60
    minutos_finais = minutos_restantes % 60

    # Criando a string de retorno
    if dias > 1:
        str_dias = f"{dias}d"
    elif dias == 1:
        str_dias = "1d"
    else:
        str_dias = ""

    if horas > 1:
        str_horas = f"{horas}h"
    elif horas == 1:
        str_horas = "1h"
    else:
        str_horas = ""

    if dias == 0:
        if minutos_finais > 1:
            str_minutos = f"{minutos_finais}m"
        elif minutos_finais == 1:
            str_minutos = "1m"
        else:
            str_minutos = ""
    else:
        str_minutos = ""

    # Combinando as partes em uma única string
    result = " ".join(filter(None, [str_dias, str_horas, str_minutos]))
    return result

def getBenchmark(metricType, minute):
    # print(f'metric: {metricType} - {minute}')
    metricTypeDict = {
                    "cycleTime":{"elite":73,"strong":155,"fair":304},
                    "codingTime":{"elite":19,"strong":44,"fair":99},
                    "pickupTime":{"elite":7,"strong":13,"fair":24},
                    "reviewTime":{"elite":5,"strong":14,"fair":29},
                    "deployTime":{"elite":6,"strong":50,"fair":137},
                    "refactor":{"elite":9,"strong":15,"fair":21},
                    "rework":{"elite":2,"strong":5,"fair":7}
                }
    if metricType == 'refactor' or metricType == 'rework':
        # Definindo os limites
        elite_limite = metricTypeDict[metricType]['elite']
        strong_limite = metricTypeDict[metricType]['strong']
        fair_limite = metricTypeDict[metricType]['fair']
    else:
        # Definindo os limites em minutos
        elite_limite = metricTypeDict[metricType]['elite'] * 60 #7h
        strong_limite = metricTypeDict[metricType]['strong'] * 60 #13h
        fair_limite = metricTypeDict[metricType]['fair'] * 60 #24h

    if (not isinstance(minute, float) and not isinstance(minute, int)) or minute == 0 :
        return '\U000026AA'

    # Verificando as condições e retornando o rótulo correspondente
    if minute <= elite_limite:
        return '\U0001F7E2'
    elif minute > elite_limite and minute <= strong_limite:
        return '\U0001F535'
    elif minute > strong_limite and minute <= fair_limite:
        return '\U0001F7E1'
    else:
        return '\U0001F534'

def getBenchmarkWorkBreakDown(metricType, minute):
    
    metricTypeDict = {
                    "refactor":{"elite":9,"strong":15,"fair":21},
                    "rework":{"elite":2,"strong":5,"fair":7}
                }

    # Definindo os limites em minutos
    elite_limite = metricTypeDict[metricType]['elite']
    strong_limite = metricTypeDict[metricType]['strong']
    fair_limite = metricTypeDict[metricType]['fair'] 

    if (not isinstance(minute, float) and not isinstance(minute, int)) or minute == 0 :
        return '\U000026AA'

    # Verificando as condições e retornando o rótulo correspondente
    if minute <= elite_limite:
        return '\U0001F7E2'
    elif minute > elite_limite and minute <= strong_limite:
        return '\U0001F535'
    elif minute > strong_limite and minute <= fair_limite:
        return '\U0001F7E1'
    else:
        return '\U0001F534'    

def convert_date_format(str):
    print(str)
    date_obj = datetime.strptime(str, '%d/%m/%Y')
    return date_obj.strftime('%Y-%m-%d')

def yape_colors():
    return ['#b2afaf','#a86ebb','#5dd5b1','#66ceb7', '#f34a5a', '#69217a', '#cd384f','#7f7f7f','#ffc000']

def compare_metrics(result):
    simbolos = ['⬆', '⬇', '⁃']

    if (result == 'isBetter'):
        return simbolos[0]
    elif (result == 'isWorse'):
        return simbolos[1]
    return simbolos[2]
