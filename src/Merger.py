import math
import sys
from MyCounter import MyCounter


class Merger:
    def __init__(self):
        self.dirCnM = "chunks/"
        self.dirGroups = "groups/"

    # commun methods to help
    # apanha o próximo termo a escrever
    def get_next_term(self, lines, splitted_lines):
        terms = []
        for line in lines:
            strip = line.rstrip("\n")
            seps = strip.split("\t")
            splitted_lines.append(seps)
            terms.append(seps[0])
            
        return (sorted(terms))[0]

    # remove lines vazias e files que já chegaram ao final
    def remove_unused(self, del_ind_files, files, lines):
        for x in sorted(del_ind_files, reverse=True):
            del lines[x]
            files[x].close()
            del files[x]

    # escreve grupo de linhas a escrever
    def write_group(self, lines_to_write, merge_files):
        sep1 = lines_to_write[0].split("\t")  # guarda primeira palavra da primeira linha
        sep2 = lines_to_write[len(lines_to_write) - 1].split("\t")  # guarda primeira palavra da última linha
        merge_files.append(sep1[0] + "_" + sep2[0] + ".tsv")

        # abre sempre o ´último ficheiro pra escrever
        with open(self.dirGroups + merge_files[len(merge_files) - 1], "w", encoding="utf-8") as file:
            for line in lines_to_write:
                file.write(line + "\n")

    # vsm methods
    # merge das linhas a escrever numa única, vsm version
    # versão tp2
    def create_vsm_weigthed_final_line(self, lines_to_merge, next_term, post_counter):
        string = ""
        document_frequency = 0

        with open(self.dirGroups + "index_list.txt", "r", encoding="utf-8") as file:
            doc_quantity = int(file.readline().rstrip("\n"))

        for x in range(len(lines_to_merge)):
            document_frequency += len(lines_to_merge[x]) / 2  # quantidade de documentos onde está presente o termo

        for line in lines_to_merge:
            for ind, word in enumerate(line):
                if ind % 2 == 1:  # percorre apenas ids
                    string += "\t"
                    string += word
                    string += "\t"
                    term_frequency = int(line[ind + 1])
                    # weigth = tf * idf
                    string += str(round((1 * math.log10(term_frequency) * 1), 4))
                    post_counter.increment()

        # termo idf doc_id1 weigth1 doc_id2 weigth2...
        return next_term + "\t" + str(math.log10(doc_quantity/document_frequency)) + string

    # todo versão tp3
    def new_create_vsm_weighted_final_line(self, lines_to_merge, next_term, post_counter):
        string = ""
        document_frequency = 0

        with open(self.dirGroups + "index_list.txt", "r", encoding="utf-8") as file:
            doc_quantity = int(file.readline().rstrip("\n"))

        for x in range(len(lines_to_merge)):
            document_frequency += len(lines_to_merge[x]) / 2        # quantidade de documentos onde está presente o termo

        for line in lines_to_merge:
            for ind, word in enumerate(line):
                if ind % 2 == 1:                                    # percorre apenas ids
                    string += f"\t{word}\t"                         # adiciona índice da review
                    term_frequency = len(line[ind + 1].split("_"))  # len(posições do termo) = frequencia do termo na review
                    string += f"{round((1 * math.log10(term_frequency) * 1), 4)}"  # adiciona peso (tf * idf)
                    string += f"\t{line[ind + 1]}"                  # adiciona posições do termo na review
                    post_counter.increment()

        # termo idf doc_id1 weight1 pos1_pos2_pos3 doc_id2 weight2 pos1_pos2_pos3...
        return next_term + f"\t{math.log10(doc_quantity/document_frequency)}{string}"

    # função que faz merge dos chunks todos, pesando os termos no processo
    def vsm_merge(self, lista_chunks):
        files = [open(self.dirCnM + filename, "r", encoding="utf-8") for filename in lista_chunks]  # abre todos os ficheiros
        lines = [file.readline() for file in files]  # lê 1 linha de cada ficheiro
        lines_to_write = []  # estrutura para guardar linhas a escrever futuramente
        merge_files = []  # estrutura que guarda o nome dos ficheiros que possuem já a informação junta(não repetida) e pesada
        post_counter = MyCounter()

        while len(lines) > 0 and sys.getsizeof(lines_to_write) != 0:
            # guarda primeiro termo a ler
            splitted_lines = []  # guarda linhas fracionadas
            next_term = self.get_next_term(lines, splitted_lines)

            # escolhe linhas fracionadas a escrever com base no prox termo
            lines_to_merge = []
            del_ind_files = []
            for ind, line in enumerate(splitted_lines):
                if splitted_lines[ind][0] == next_term:  # compara termos
                    lines_to_merge.append(line)  # guarda linha a escrever
                    new = files[ind].readline()  # lê já a próxima linha
                    if new == "":  # nova linha == EOF
                        del_ind_files.append(ind)  # guarda índice para apagar futuramente

                    else:
                        lines[ind] = new.rstrip("\n")

            # remove linhas e fecha ficheiros
            self.remove_unused(del_ind_files, files, lines)

            # cria linha final
            # versão tp2
            # line_to_write = self.create_vsm_weigthed_final_line(lines_to_merge, next_term, post_counter)
            # todo versão tp3
            line_to_write = self.new_create_vsm_weighted_final_line(lines_to_merge, next_term, post_counter)

            # guarda linhas a escrever
            lines_to_write.append(line_to_write)

            # escreve linhas a cada 1000000 posts
            if post_counter.count > 1000000 or len(
                    lines) == 0:  # se chegou a treshold de posts ou ficou sem linhas pra ler
                self.write_group(lines_to_write, merge_files)

                lines_to_write.clear()  # limpa linhas
                post_counter.reset()  # reseta contador

        return merge_files

    # bm25 methods
    # merge das linhas a escrever, bm25 version
    # versão tp2
    def create_bm25_weigthed_final_line(self, lines_to_merge, next_term, post_counter):
        string = ""
        document_frequency = 0
        b = 0.75
        k1 = 1.2

        with open(self.dirGroups + "index_list.txt", "r", encoding="utf-8") as file:
            doc_quantity = int(file.readline().rstrip("\n"))

        for x in range(len(lines_to_merge)):
            document_frequency += len(lines_to_merge[x]) / 2  # quantidade de documentos onde o termo está presente

        for line in lines_to_merge:
            document_frequencies = [int(x) for ind, x in enumerate(line) if ind > 0 and ind % 2 == 1]
            document_length = sum(document_frequencies)
            average_document_length = document_length / len(document_frequencies)
            B = (1 - b) * (document_length / average_document_length)
            for ind, word in enumerate(line):
                if ind % 2 == 1:  # percorre apenas ids
                    string += "\t"
                    string += word
                    string += "\t"
                    term_frequency = int(line[ind + 1])
                    # weigth(term frequency normalization)
                    normalized_term_frequency = term_frequency / B
                    weigth = (math.log10(doc_quantity / document_frequency)) * (((k1 + 1) * normalized_term_frequency) / (k1 + normalized_term_frequency))
                    string += str(round(weigth, 4))
                    post_counter.increment()

        # termo idf doc_id1 weigth1 doc_id2 weigth2...
        return next_term + "\t" + str(math.log10(doc_quantity / document_frequency)) + string

    # todo versão tp3
    def new_create_bm25_weighted_final_line(self, lines_to_merge, next_term, post_counter):
        string = ""
        document_frequency = 0
        b = 0.75
        k1 = 1.2

        with open(self.dirGroups + "index_list.txt", "r", encoding="utf-8") as file:
            doc_quantity = int(file.readline().rstrip("\n"))

        for x in range(len(lines_to_merge)):
            document_frequency += len(lines_to_merge[x]) / 2

        for line in lines_to_merge:
            document_frequencies = [len(x.split("_")) for ind, x in enumerate(line) if ind > 0 and ind % 2 == 1]
            document_lenght = sum(document_frequencies)
            average_document_lenght = document_lenght / len(document_frequencies)
            B = (1 - b) * (document_lenght / average_document_lenght)
            for ind, word in enumerate(line):
                if ind % 2 == 1:  # percorre apenas ids
                    string += f"\t{word}\t"
                    term_frequency = len(line[ind + 1].split("_"))  # len(posições do termo) = frequência do termo na review
                    # weight(term frequency normalization)
                    normalized_term_frequency = term_frequency / B
                    weight = (math.log10(doc_quantity / document_frequency)) * (((k1 + 1) * normalized_term_frequency) / (k1 + normalized_term_frequency))
                    string += str(round(weight, 4))  # adiciona peso à string
                    string += f"\t{line[ind + 1]}"  # adiciona posições à string
                    post_counter.increment()

        # termo idf doc_id1 weight1 pos1_pos2_pos3 doc_id2 weight2 pos1_pos2_pos3...
        return next_term + "\t" + str(math.log10(doc_quantity / document_frequency)) + string

    # função que faz merge dos chunks todos, pesando os termos no processo de acordo com
    def bm25_merge(self, lista_chunks):
        files = [open(self.dirCnM + filename, "r", encoding="utf-8") for filename in lista_chunks]
        lines = [file.readline() for file in files]
        lines_to_write = []
        merge_files = []
        post_counter = MyCounter()

        while len(lines) > 0 and sys.getsizeof(lines_to_write) != 0:
            # guarda primeiro termo a ler
            splitted_lines = []  # guarda linhas fracionadas
            next_term = self.get_next_term(lines, splitted_lines)

            # escolhe linhas fracionadas a escrever com base no prox termo
            lines_to_merge = []
            del_ind_files = []
            for ind, line in enumerate(splitted_lines):
                if splitted_lines[ind][0] == next_term:  # compara termos
                    lines_to_merge.append(line)  # guarda linha a escrever
                    new = files[ind].readline()  # lê já a próxima linha
                    if new == "":  # EOF
                        del_ind_files.append(ind)  # guarda índice para apagar futuramente

                    else:
                        lines[ind] = new.rstrip("\n")

            # remove linhas e fecha ficheiros
            self.remove_unused(del_ind_files, files, lines)

            # cria linha final
            # versão tp2
            # line_to_write = self.create_bm25_weigthed_final_line(lines_to_merge, next_term, post_counter)
            # todo versão tp3
            line_to_write = self.new_create_bm25_weighted_final_line(lines_to_merge, next_term, post_counter)

            # guarda linhas a escrever
            lines_to_write.append(line_to_write)

            # escreve linhas a cada 1000000 posts
            if post_counter.count > 1000000 or len(
                    lines) == 0:  # se chegou a treshold de posts ou ficou sem linhas pra ler
                self.write_group(lines_to_write, merge_files)

                lines_to_write.clear()  # limpa linhas
                post_counter.reset()  # reseta contador
        return merge_files
