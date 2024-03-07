import services
import subprocess

if __name__ == "__main__":
    # gerando os dados para cadastro no carne leao
    services.getCardExtract('01/09/2023','27/02/2024', 2000)
    subprocess.run(['open', '-a', 'Microsoft Excel', '/Users/alexfrisoneyape/Desktop/Gastos/template/recibos/gastos_escritorio.xlsx'])
    
    # coleta dos dados dos recibos para reembolso
    # services.exportSpreadsheet('/Users/alexfrisoneyape/Desktop/Gastos/Janeiro/gastos','/Users/alexfrisoneyape/Desktop/Gastos/Janeiro/gastos.xlsx')