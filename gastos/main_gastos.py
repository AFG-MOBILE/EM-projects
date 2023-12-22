import services
import subprocess

if __name__ == "__main__":
    services.getCardExtract('01/09/2023','21/12/2023', 2000)
    subprocess.run(['open', '-a', 'Microsoft Excel', '/Users/alexfrisoneyape/Desktop/Gastos/test/recibos/gastos_escritorio.xlsx'])