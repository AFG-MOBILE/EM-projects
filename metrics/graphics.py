from matplotlib import pyplot as plt
import pandas as pd
import nave


def plot_bugs_over_time(criados, resolvidos, meses, tipo):
    # Transformando os valores de bugs resolvidos em negativos para a visualização
    resolvidos_negativos = [-abs(x) for x in resolvidos]
    # Criando um DataFrame para os dados
    df_bugs = pd.DataFrame({
        'Mês': meses,
        f'{tipo} Creados': criados,
        f'{tipo} Resolvidos': resolvidos_negativos
    })

    # Criando o gráfico
    fig, ax = plt.subplots(figsize=(14, 8))  
     
    # Barras para bugs criados
    bars_criados = ax.bar(meses, criados, color='#a86ebb', label=f'{tipo} Creados')

    # Barras para bugs resolvidos
    bars_resolvidos = ax.bar(meses, resolvidos_negativos, color='#5dd5b1', label=f'{tipo} Resolvidos')

    # Adicionando as anotações em cada barra
    for bars in [bars_criados, bars_resolvidos]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate('{}'.format(abs(height)),
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3 if height > 0 else -12),  # 3 pontos de deslocamento vertical para cima para bugs criados, para baixo para resolvidos
                        textcoords="offset points",
                        ha='center', va='bottom' if height > 0 else 'top')

    cinza = '#7f7f7f'
    plt.rcParams['text.color'] = cinza
    plt.rcParams['axes.edgecolor'] = cinza   # Cor padrão para contornos dos eixos
    plt.rcParams['xtick.color'] = cinza    # Cor padrão para ticks do eixo x
    plt.rcParams['ytick.color'] = cinza
    plt.xlabel('Mes', color=cinza)
    plt.ylabel('Number of Cards', color=cinza)
    plt.title(f'{tipo} Creados e Resolvidos en Mês',color=cinza)
    ax.legend(loc='lower left', bbox_to_anchor=(1,1))
    
    # Ajustando os limites para dar mais espaço interno
    ax.set_ylim(min(-max(resolvidos)*1.2, ax.get_ylim()[0]), max(criados)*1.2)
    plt.savefig(f'{tipo}_grafico.png')
    plt.tight_layout()
    plt.show()

def plot_created_vs_finished(df, df_finished, start_date, end_date):
    df = nave.format_dates(df)
    df_finished = nave.format_dates(df_finished)
    
    # Convert the provided dates to datetime format using the specified format
    start_date = pd.to_datetime(start_date, format='%d/%m/%Y', errors='coerce')
    end_date = pd.to_datetime(end_date, format='%d/%m/%Y', errors='coerce')

    # Define the date range for the created vs finished chart
    full_date_range = pd.date_range(start_date, end_date)

    # Check if the date range is valid
    if len(full_date_range) == 0:
        print("Warning: Invalid date range. Please ensure the start date is before the end date.")
        return

    # Calculate the number of cards created and finished for each day
    created_count = []
    finished_count = []
    
    for date in full_date_range:
        date = pd.to_datetime(date,format='%Y-%m-%d').strftime('%Y-%m-%d')    
        created_on_date = len(df[df['Start date'] == date])
        finished_on_date = len(df_finished[df_finished['End date'] == date])
        print(f'{date} - created_on_date: {created_on_date} - finished_on_date: {finished_on_date}')
        created_count.append(created_on_date)
        finished_count.append(finished_on_date)

    # Calculate the average number of cards created and finished
    avg_created = sum(created_count) / len(full_date_range)
    avg_finished = sum(finished_count) / len(full_date_range)

    # Plot the Created vs Finished chart with averages
    plt.figure(figsize=(14, 7))
    cinza = '#7f7f7f'
    plt.rcParams['text.color'] = cinza
    plt.rcParams['axes.edgecolor'] = cinza   # Cor padrão para contornos dos eixos
    plt.rcParams['xtick.color'] = cinza    # Cor padrão para ticks do eixo x
    plt.rcParams['ytick.color'] = cinza
    plt.plot(full_date_range, created_count, label='Cards Created', marker='o', color='#a86ebb', linestyle='-')
    plt.plot(full_date_range, finished_count, label='Cards Finished', marker='x', color='#5dd5b1', linestyle='-')
    plt.axhline(y=avg_created, color='#a86ebb', linestyle='--', label='Average Cards Created')
    plt.axhline(y=avg_finished, color='#5dd5b1', linestyle='--', label='Average Cards Finished')
    plt.fill_between(full_date_range, created_count, color='#a86ebb', alpha=0.3)
    plt.fill_between(full_date_range, finished_count, color='#66ceb7', alpha=0.3)
    plt.title('Cards Created vs Cards Finished Over Time with Averages')
    plt.xlabel('Date', color=cinza)
    plt.ylabel('Number of Cards', color=cinza)
    plt.legend(loc='upper right')
    plt.xticks(rotation=45)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()

def plot_bugs_restantes_por_mes(dataframe):
    # Convertendo colunas de data para formato de data do pandas
    dataframe['End date'] = pd.to_datetime(dataframe['End date'], format='%d %b %Y')
    dataframe['Start date'] = pd.to_datetime(dataframe['Start date'], format='%d %b %Y')

    # Criando colunas de mês para 'End date' e 'Start date'
    dataframe['End month'] = dataframe['End date'].dt.to_period('M')
    dataframe['Start month'] = dataframe['Start date'].dt.to_period('M')

    # Contando os bugs finalizados por mês
    bugs_finalizados_por_mes = dataframe['End month'].value_counts().sort_index()

    # Contando os bugs restantes por mês
    bugs_restantes_por_mes = bugs_finalizados_por_mes.copy()
    bugs_restantes_por_mes = bugs_restantes_por_mes.cumsum().shift(fill_value=0)
    bugs_restantes_por_mes = bugs_restantes_por_mes.diff().fillna(bugs_finalizados_por_mes)

    # Tornando os valores de bugs restantes negativos para plotagem
    bugs_restantes_por_mes = -bugs_restantes_por_mes

    # Plotando o gráfico de barras
    plt.figure(figsize=(10, 6))

    # Plotando os bugs restantes em cada mês no eixo vertical negativo
    plt.bar(bugs_restantes_por_mes.index.astype(str), bugs_restantes_por_mes, label='Bugs Restantes')

    # Plotando os bugs finalizados em cada mês
    plt.bar(bugs_finalizados_por_mes.index.astype(str), bugs_finalizados_por_mes, label='Bugs Finalizados')

    plt.xlabel('Mês')
    plt.ylabel('Número de Bugs')
    plt.title('Bugs Restantes e Finalizados por Mês')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Exibindo o gráfico
    plt.show()

def plot_cycle_time_by_week(df):
    # Converter 'week_start' para categoria para preservar a ordem na visualização do gráfico
    df['week_start'] = pd.Categorical(df['week_start'], categories=df['week_start'].unique(), ordered=True)

    # Criar o gráfico
    plt.figure(figsize=(7, 5))

    # Definindo a cor cinza claro para o fundo do gráfico, eixos e grid
    # plt.rcParams['axes.facecolor'] = 'lightgrey'
    plt.rcParams['axes.edgecolor'] = '#b2afaf'
    plt.rcParams['xtick.color'] = '#b2afaf'  # Cor do texto do eixo x
    plt.rcParams['ytick.color'] = '#b2afaf'  # Cor do texto do eixo y
    plt.rcParams['grid.color'] = '#b2afaf'

    # Iterar sobre os owners
    for owner, data in df.groupby('owner'):
        if owner == 'chapter':
            plt.plot(data['week_start'], data['cycle_time'], marker='o', label=owner, linestyle='-.', color='#b2afaf')
        elif owner == 'team':
            color_beige = (0.9608, 0.8706, 0.702)
            plt.plot(data['week_start'], data['cycle_time'], marker='o', label=owner, linestyle='--', color=color_beige)
        else:
            plt.plot(data['week_start'], data['cycle_time'], marker='o', label=owner, color='#a86ebb')
        # plt.plot(data['week_start'], data['cycle_time'], marker='o', label=owner)

    # plt.title('Cycle Time por Semana e Owner')
    # plt.xlabel('Semana')
    # plt.ylabel('Cycle Time')
    # plt.legend()
    # plt.grid(True)
    plt.grid(axis='y')
    plt.show()