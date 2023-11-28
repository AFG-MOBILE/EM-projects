from jinja2 import Template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



def preencher_template_informe_semanal(template_file, destaques):
    with open(template_file, 'r') as file:
        template_html = file.read()

    # Dados para preencher o template
    informe_semanal = {
        'destaques': destaques
    }

    # Compilar o template
    template = Template(template_html)

    # Preencher o template com os dados
    conteudo_email = template.render(informe_semanal)

    return conteudo_email


def renderizar_html_para_png(arquivo_html, arquivo_png):
    # Configuração do WebDriver (neste exemplo, usando o Chrome)
    service = Service('/usr/local/bin/chromedriver')  # Insira o caminho para o ChromeDriver
    driver = webdriver.Chrome(service=service)

    # Carregar o arquivo HTML local no navegador
    driver.get(f'file:///{arquivo_html}')

    # Capturar a imagem da página HTML
    screenshot = driver.save_screenshot(arquivo_png)

    # Fechar o navegador
    driver.quit()

    if screenshot:
        print(f'A página HTML foi renderizada como {arquivo_png} com sucesso.')
    else:
        print('Erro ao renderizar a página HTML como imagem.')


