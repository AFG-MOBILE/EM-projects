import datab3

if __name__ == "__main__":
    movimentacoes = datab3.getMovimentacoes()
    proventos = datab3.getProventos()
    datab3.saveCSV(movimentacoes, '/Users/alexfrisoneyape/Development/EM/b3/movimentacoes_consolidado.csv')
    datab3.saveCSV(proventos, '/Users/alexfrisoneyape/Development/EM/b3/proventos_consolidado.csv')
    print(proventos)