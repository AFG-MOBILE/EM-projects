import services
import subprocess

if __name__ == "__main__":
    # gerando os dados para cadastro no carne leao
    services.getCardExtract('01/01/2024','25/03/2024', 3000)
    subprocess.run(['open', '-a', 'Microsoft Excel', '/Users/alexfrisoneyape/Desktop/Gastos/template/recibos/gastos_escritorio.xlsx'])
    
    # coleta dos dados dos recibos para reembolso
    # services.exportSpreadsheet('/Users/alexfrisoneyape/Desktop/Gastos/Janeiro/gastos','/Users/alexfrisoneyape/Desktop/Gastos/Janeiro/gastos.xlsx')