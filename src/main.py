"""
Miguel Filipe Rodrigues Almeida de Matos Fazenda
Nº 110877
Mestrado em Engenharia Informática
"""

import sys
from Start import Start
from Tokenizer import Tokenizer
from Indexer import Indexer
from Merger import Merger
from Searcher import Searcher

if __name__ == "__main__":

    # parse comand line arguments
    if "-h" in sys.argv or len(sys.argv) == 1:
        print("Weigthed reverse indexer")
        print("\nOPTIONS:")
        print("[-m] modo de execução -> 0 pra indexar | 1 para pesquisar")
        print("[-w] método de pesagem -> 0 para VSM | 1 para BM25")
        print("[-f] nome do ficheiro alvo de indexação")
        print("[-q] tamanho dos chunks -> quantidade de reviews que cada chunk vai possuir")
        print("[-t] opções do tokenizer -> carrega configurações do tokenizer.conf (para modo 0 e 1)")
        print("[-b] boost nas queries -> melhora(talvez...) os resultados das queries")
        exit()

    ficheiro = "amazon_reviews_us_Digital_Video_Games_v1_00.tsv"
    chunk_size = 10000
    tokenizer_config = None

    # remove nome do ficheiro dos argumentos
    del sys.argv[0]

    # remove argumento das opções do tokenizer
    if "-t" in sys.argv:  
        for x in range(len(sys.argv)):
            if sys.argv[x] == "-t":
                del sys.argv[x]
                tokenizer_config = "tokenizer.conf"
                break

    # verifica se o boost das queries é pretendido
    boost = False
    if "-b" in sys.argv:
        boost = True

    # argumentos pares são keys e ímpares values
    args = dict(zip(sys.argv[::2], sys.argv[1::2]))  

    # -----------------Processamento das opções-----------------
    if "-f" in args:  # nome do ficheiro pra indexar
        ficheiro = args["-f"]

    if "-q" in args:  # tamanho do chunk
        chunk_size = args["-q"]

    modes = [0, 1]
    if "-w" in args:
        if int(args["-w"]) not in modes:  # método de pesagem(VSM ou BM25)
            print(args["-w"])
            print("Método de pesagem não reconhecido.")
            print("A sair...")
            exit()
    else:
        print("Método de pesagem não especificado.")
        print("A sair...")
        exit()

    if "-m" in args:
        if int(args['-m']) == 0:  # dá prioridade ao modo index
            print("Starting indexer...")
            Start(Tokenizer(tokenizer_config),
                Indexer(),
                Merger(),
                ficheiro,
                chunk_size,
                  int(args["-w"])).start()
            exit()

        if int(args["-m"]) == 1:  # modo search
            print("Starting searcher...")
            results = Searcher(Tokenizer(tokenizer_config)).search(int(args["-w"]), boost)
            exit()
    else:
        print("Modo de execução não identificado.")
        print("A sair...")
        exit()
