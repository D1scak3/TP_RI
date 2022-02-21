import os
import sys
import time
import gzip
from pathlib import Path

from MyCounter import MyCounter


class Start:
    def __init__(self, tokenizer, indexer, merger, ficheiro, chunk_size, weight_method):
        # diretorias
        self.dirCnM = "chunks/"
        self.dirGroups = "groups/"
        self.dirCorpus = "corpus/"
        
        # tokenizer, indexer, merger
        self.tokenizer = tokenizer
        self.indexer = indexer
        self.merger = merger

        # caraterísticas do algoritmo
        self.ficheiro = ficheiro
        self.chunk_size = chunk_size
        self.weight_method = weight_method

        # estruturas de dados
        self.tokenized_words = []
        self.indexed_info = {}
        self.sorted_info = []
        self.lista_chunks = []
        self.lista_ids = []

        # contadores
        self.chunk_count = MyCounter()
        self.merge_count = MyCounter()
        self.line_count = MyCounter()
        self.term_count = MyCounter()

    # função que cria as diretorias
    def dir_create(self):
        try:
            parent = os.getcwd()  # diretoria atual
            path = os.path.join(parent, self.dirCnM)  # nova diretoria
            os.mkdir(path)  # cria nova diretoria
            print("Diretoria " + self.dirCnM + " criada para guardar chunks e merges.")
        except:
            print("Diretoria para guardar chunks e merges já existe.")

        try:
            parent = os.getcwd()  # diretoria atual
            path = os.path.join(parent, self.dirGroups)  # nova diretoria
            os.mkdir(path)  # cria nova diretoria
            print("Diretoria " + self.dirGroups + " criada para separar info indexada.")
        except:
            print("Diretoria para guardar grupos já existe.")

    # writes chunk to memory, versão tp2
    """escreve chunks para memória"""
    def write_chunk(self, sorted_info, nome_chunk):
        with open(self.dirCnM + nome_chunk, "w", encoding="utf-8") as ficheiro:
            print("A escrever " + nome_chunk + " para disco...")

            linha = ""
            for termo in sorted_info:  # percorre dicionario(termo, sub_dic)
                linha += f"{termo[0]}"
                sub_dic = termo[1]  # sub dicionario
                for y in sub_dic:  # percorre sub_dicionario
                    linha += "\t"
                    linha += str(y)
                    linha += "\t"
                    linha += str(sub_dic[y])
                linha += "\n"
                ficheiro.write(linha)
                linha = ""

    # write chunk to memory, versão tp3
    """escreve chunks para memória, incluindo a posição dos termos nas reviews"""
    def new_write_chunk(self, sorted_info, nome_chunk):
        with open(self.dirCnM + nome_chunk, "w", encoding="utf-8") as ficheiro:
            print("A escrever " + nome_chunk + " para disco...")

            linha = ""
            for tup in sorted_info:  # percorre tuplos (termo, sub_dic)
                termo = tup[0]
                sub_dic = tup[1]
                linha += f"{termo}"
                for doc_id in sub_dic:  # percorre sub_dic {document_id, position_list}
                    position_list = sub_dic[doc_id]
                    linha += f"\t{doc_id}"
                    for ind, position in enumerate(position_list):  # percorre posições dos termos da position_list
                        if ind == 0:  # se primeiro elemento
                            linha += f"\t{position}"
                        else:  # se for outro elemento qualquer
                            linha += f"_{position}"
                linha += "\n"
                ficheiro.write(linha)
                linha = ""

    # guarda quantidade de índices(documentos) lista de indexs(atribui a cada índice das reviews um id específico)
    def save_index_list(self):
        with open(self.dirGroups + "index_list.txt", "w", encoding="utf-8") as file:
            file.write(f"{len(self.lista_ids)}\n")
            for ind, id in enumerate(self.lista_ids):
                file.write(f"{ind + 1} {id}\n")

    # compacta o ficheiro pretendido
    def compact(self, merge_files):
        for file in merge_files:
            with open(self.dirGroups + file, "r", encoding="utf-8") as uncompressed_file:
                with gzip.open(self.dirGroups + file + ".gz", "wt", encoding="utf-8") as compressed_file:
                    for line in uncompressed_file:
                        self.term_count.increment()
                        compressed_file.write(line)

    # inicia algoritmo
    def start(self):
        # cria diretoria
        self.dir_create()

        print("A indexar ficheiro...")

        start_time = time.time()

        with open(self.dirCorpus + self.ficheiro, "r", encoding="utf-8") as file:
            file.readline()  # lê linha com nomes das colunas

            while True:
                line = file.readline()

                if line:
                    split = line.split("\t")
                    string = split[5] + " " + split[12] + " " + split[13]  # concatena title, headline e body

                    # adiciona id da review à lista de ids
                    self.lista_ids.append(split[2])

                    # tokeniza a string
                    # versão tp2
                    # self.tokenizer.tokenize(string, self.tokenized_words)
                    # todo versão 3
                    self.tokenizer.new_tokenize(string, self.tokenized_words)

                    # indexa as tokenized_words
                    # usa len(self.lista_ids) em vez do id original, corresponde sempre ao último id adicionado ao self.lista_ids
                    # versão tp2
                    # self.indexer.index(self.tokenized_words, len(self.lista_ids), self.indexed_info)
                    # todo versão 3
                    self.indexer.new_index(self.tokenized_words, len(self.lista_ids), self.indexed_info)
                    self.tokenized_words.clear()

                    # incrementa contador de linhas
                    self.line_count.increment()

                    if self.line_count.count % self.chunk_size == 0:  # se chegou ao limite do chunk
                        # transforma dicionário {termo, sub_dic} em lista ordenada por termo [term, sub_dic]
                        self.sorted_info = sorted(self.indexed_info.items(), key=lambda x: x[0])
                        self.indexed_info.clear()

                        self.chunk_count.increment()
                        self.lista_chunks.append("chunk" + str(self.chunk_count.count) + ".tsv")
                        # versão tp2
                        # self.write_chunk(self.sorted_info, self.lista_chunks[len(self.lista_chunks) - 1])
                        # todo versão 3
                        self.new_write_chunk(self.sorted_info, self.lista_chunks[len(self.lista_chunks) - 1])
                        self.sorted_info.clear()

                else:  # EOF
                    if self.indexed_info:  # ainda tem pra escrever
                        self.sorted_info = sorted(self.indexed_info.items(), key=lambda x: x[0])
                        self.indexed_info.clear()

                        self.chunk_count.increment()
                        self.lista_chunks.append("chunk" + str(self.chunk_count.count) + ".tsv")
                        # versão tp2
                        # self.write_chunk(self.sorted_info, self.lista_chunks[len(self.lista_chunks) - 1])
                        # todo versão tp3
                        self.new_write_chunk(self.sorted_info, self.lista_chunks[len(self.lista_chunks) - 1])
                        self.sorted_info.clear()
                        break
                        
                    else:  # se por alguma razão não tiver nada pra escrever
                        break

        end_time = time.time()

        # guarda lista de ids
        self.save_index_list()

        # merge dos ficheiros
        print("A fazer merge dos ficheiros...")
        merge_start = time.time()
        if self.weight_method == 0:
            merge_files = self.merger.vsm_merge(self.lista_chunks)
        else:
            merge_files = self.merger.bm25_merge(self.lista_chunks)
        merge_end = time.time()

        # compacta ficheiros
        print("A compactar os ficheiros...")
        compact_start = time.time()
        self.compact(merge_files)
        compact_end = time.time()

        # tamanho das indexações
        pre_index_size = sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, dirnames, filenames in os.walk("./" + self.dirCnM) for filename in filenames)
        pos_index_size = sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, dirnames, filenames in os.walk("./" + self.dirGroups) for filename in filenames if filename.endswith(".tsv"))
        compact_index_size = sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, dirnames, filenames in os.walk("./" + self.dirGroups) for filename in filenames if filename.endswith(".tsv.gz"))

        print("\n---------------------Resultados finais---------------------")
        print("Nome ficheiro(corpus): " + self.ficheiro)
        print("Tempos:")
        print(f"    indexação reversa: {end_time - start_time} segundos")
        print(f"    merge dos ficheiros: {merge_end - merge_start} segundos")
        print(f"    comprimir indexação final: {compact_end - compact_start} segundos")
        print(f"    tamanho da indexação pre-merge: {round(pre_index_size / 1048576, 4)} mbs")
        print(f"    tamanho da indexação pos-merge: {round(pos_index_size / 1048576, 4)} mbs")
        print(f"    tamanho da indexação compactada: {round(compact_index_size / 1048576, 4)} mbs")
        print(f"    quantidade de chunks antes do merge: {self.chunk_count.count}")
        print(f"    quantidade de termos diferentes: {self.term_count.count}")

