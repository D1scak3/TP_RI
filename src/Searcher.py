import math
import os
import time
from operator import itemgetter
from Tokenizer import Tokenizer
from collections import Counter
from collections import OrderedDict


"""
Procura nos ficheiros indexados a query pretendida.
Por enquanto ainda só devolve a quantidade de reviews onde o termo está presente.
"""


class Searcher:

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.dirQueries = "queries/"
        self.dirGroups = "groups/"
        self.dirCorpus = "corpus/"

    def dir_create(self):
        try:
            parent = os.getcwd()  # diretoria atual
            path = os.path.join(parent, self.dirQueries)  # nova diretoria
            os.mkdir(path)  # cria nova diretoria
            print("Diretoria " + self.dirQueries + " criada para guardar queries.")
        except:
            print("Diretoria para guardar queries já existe.")

    """----------------------commun methods to help----------------------"""
    # versão tp2
    def process_query(self, query):
        tokenized_query = []
        self.tokenizer.tokenize(query, tokenized_query)
        # res = tokenized_query[0]
        # for x in range(len(tokenized_query)):
        #     if x > 0:  # ignora termo
        #         res += "\t"
        #         res += tokenized_query[x]

        return tokenized_query

    # todo versão tp3
    def new_process_query(self, query):
        tokenized_query = []
        self.tokenizer.new_tokenize(query, tokenized_query)
        return tokenized_query

    # versão tp2
    def get_files(self, termos):
        path = os.getcwd()  # diretoria atual
        path = os.path.join(path, self.dirGroups)  # diretoria pra pesquisar grupos
        group_list = [x for x in os.listdir(path) if os.path.isfile(path + x) and x.endswith(".tsv")]  # lista de grupos
        files = {}

        for nome in group_list:
            files[nome] = []
            strip = nome.rstrip(".tsv")
            split = strip.split("_")
            for termo in termos:
                if split[0] <= termo <= split[1]:
                    files[nome].append(termo)

        return files

    # todo versão tp3
    def new_get_files(self, termos):
        path = os.getcwd()  # diretoria atual
        path = os.path.join(path, self.dirGroups)  # diretoria pra pesquisar grupos
        group_list = [x for x in os.listdir(path) if os.path.isfile(path + x) and x.endswith(".tsv")]  # lista de grupos
        files = {}

        for nome in group_list:
            files[nome] = []
            strip = nome.rstrip(".tsv")
            split = strip.split("_")
            for termo in termos:
                if split[0] <= termo[0] <= split[1]:
                    files[nome].append(termo)

        return files

    """----------------------vsm methods----------------------"""
    def vsm_save_results(self, cosine_scores):
        review_ids = {}
        with open(self.dirGroups + "index_list.txt", "r", encoding="utf-8") as file:
            for ind, line in enumerate(file):
                if ind > 0:
                    strip = line.rstrip("\n")
                    split = strip.split(" ")
                    review_ids[int(split[0])] = split[1]

        with open(self.dirQueries + "vsm_query_results.txt", "w", encoding="utf-8") as file:
            for query in cosine_scores:  # percorre queries
                new_list = []
                file.write(f"Query\t{query}")  # escreve query
                for result in cosine_scores[query]:  # percorre resultados de pesquisa da query
                    val = review_ids[int(result[0])]  # vai buscar id_real através do id_transformado
                    new_list.append(val)
                    file.write(f"\t{val}")
                cosine_scores[query] = new_list
                file.write("\n")

    # versão tp2
    def calc_vsm_vals(self, tokenized_query_terms, selected_groups):
        results = []
        query_term_frequency = Counter(tokenized_query_terms)  # dicionário que conta os termos
        for group in selected_groups:  # percorre grupos
            for term in tokenized_query_terms:  # percorre termos
                if term in selected_groups[group]:  # verifica se termo está no grupo
                    with open(self.dirGroups + group, "r", encoding="utf-8") as file:  # abre grupo
                        for line in file:
                            strip = line.rstrip("\n")
                            split = strip.split("\t")
                            if split[0] == term:  # verifica se é a linha correta do grupo escolhido
                                for ind, x in enumerate(split):
                                    if ind > 1 and ind % 2 == 0:
                                        query_term_weigth = (1 + math.log10(query_term_frequency[term])) * float(split[1])
                                        res = float(split[ind + 1]) * query_term_weigth  # tf*idf * tf*idf
                                        results.append((x, round(res, 4)))  # id do documento, resultado

        return results

    # todo versão tp3
    def new_calc_vsm_vals(self, tokenized_query_terms, selected_groups):

        # obtem term_frequency na query
        query_term_frequency = OrderedDict()  # dicionário que mantém a ordem de inserção das keys
        for word in tokenized_query_terms:
            if word in query_term_frequency:
                query_term_frequency[word] += 1
            else:
                query_term_frequency[word] = 1

        # guarda linhas para calcular pesos
        lines = []
        for group in selected_groups:
            if len(selected_groups[group]) > 0:
                with open(self.dirGroups + group, "r", encoding="utf-8") as file:
                    for line in file:
                        strip = line.rstrip("\n")
                        split = strip.split("\t")
                        for x in selected_groups[group]:
                            if split[0] == x:
                                lines.append(line)

        # calcula resultados
        results = []
        for line in lines:
            strip = line.rstrip("\n")
            split = strip.split("\t")
            termo = split[0]
            idf = split[1]

            for ind, x in enumerate(split):
                if ind > 1 and ind % 3 == 2:
                    query_term_weigth = (1 + math.log10(query_term_frequency[termo])) * float(idf)
                    res = float(split[ind + 1]) * query_term_weigth
                    results.append((x, res))

        return results

    # todo versão tp3
    def new_boosted_calc_vsm_vals(self, tokenized_query_terms, selected_groups):

        # obtem term_frequency na query
        query_term_frequency = OrderedDict()  # dicionário que mantém a ordem de inserção das keys
        for tup in tokenized_query_terms:
            term = tup[0]
            positions = tup[1]  # não é utilizado...
            if term in query_term_frequency:
                query_term_frequency[term] += 1
            else:
                query_term_frequency[term] = 1

        # recolhe linhas para calcular pesos
        lines = []
        for group in selected_groups:
            if len(selected_groups[group]) > 0:
                with open(self.dirGroups + group, "r", encoding="utf-8") as file:
                    for line in file:
                        strip = line.rstrip("\n")
                        split = strip.split("\t")
                        for x in selected_groups[group]:
                            if split[0] == x[0]:
                                lines.append(line)

        # processa linhas para facilitar cálculo dos resultdos
        reviews = {}  # {review_id, []} -> lista de tuplos (term, idf, weight, pos1_pos2_pos3)
        for line in lines:
            strip = line.rstrip("\n")
            split = strip.split("\t")
            termo = split[0]
            idf = split[1]

            for ind, x in enumerate(split):
                # termo idf doc_id weight pos1_pos2_pos3 doc_id weight pos1_pos2_pos3
                # 0     1   2      0      1              2      0      1 (restos da divisão do índice por 3)
                # doc_id's são sempre resto = 2
                if ind > 1 and ind % 3 == 2:  # review_id já está presente
                    if split[ind] in reviews:
                        reviews[split[ind]].append((termo, idf, split[ind + 1], split[ind + 2]))  # (termo, idf, peso, posições)
                    else:  # review_id ainda não está presetne
                        reviews[split[ind]] = []
                        reviews[split[ind]].append((termo, idf, split[ind + 1], split[ind + 2]))  # (termo, idf, peso, posições)

        # calcula resultados finais
        results = []  # (review_id, final_weight)
        for review in reviews:  # percorre reviews
            positions = []
            if len(reviews[review]) > 1:  # tem vários termos na review
                # percorre tuplos da review para obter posições
                for tup in reviews[review]:
                    positions += [int(x) for x in tup[3].split("_") if int(x) >= 0]

                span = max(positions) - min(positions)
                term_amount = len(positions)
                boost = 1 + (term_amount / span)

                # percorre tuplos outra vez pra calcular pesos
                for tup in reviews[review]:  # percorre reviews
                    termo = tup[0]  # termo
                    idf = tup[1]  # idf do termo
                    term_weight = float(tup[2])  # peso do termo na review
                    query_term_weight = (1 + math.log10(query_term_frequency[termo])) * float(idf)  # peso do termo na query
                    weight = term_weight * query_term_weight  # peso final
                    results.append((review, weight * boost))  # peso com boost

            elif len(reviews[review]) == 1:  # tem apenas 1 termo na review
                for tup in reviews[review]:
                    termo = tup[0]
                    idf = tup[1]
                    term_weight = float(tup[2])
                    query_term_weight = (1 + math.log10(query_term_frequency[termo])) * float(idf)
                    weight = term_weight * query_term_weight
                    results.append((review, weight))

            else:  # não tem termos na review
                continue

        return results

    def vsm_search(self, boost):
        cosine_scores = {}

        with open(self.dirCorpus + "queries.txt", "r", encoding="utf-8") as queries:
            for query in queries:
                query = query.rstrip("\n")
                if boost:
                    # todo versão tp3 somente
                    tokenized_query_terms = self.new_process_query(query)
                    selected_groups = self.new_get_files(tokenized_query_terms)
                    cosine_scores[query] = sorted(self.new_boosted_calc_vsm_vals(tokenized_query_terms, selected_groups), reverse=True, key=lambda x: x[1])[0:100]
                else:
                    # versão tp2
                    tokenized_query_terms = self.process_query(query)
                    selected_groups = self.get_files(tokenized_query_terms)
                    # cosine_scores[query] = sorted(self.calc_vsm_vals(tokenized_query_terms, selected_groups), reverse=True, key=lambda x: x[1])[0:100]
                    # todo versão tp3
                    cosine_scores[query] = sorted(self.new_calc_vsm_vals(tokenized_query_terms, selected_groups), reverse=True, key=lambda x: x[1])[0:100]

        self.vsm_save_results(cosine_scores)

        return cosine_scores

    """----------------------bm25 methods----------------------"""
    def bm25_save_results(self, bm25_scores):
        review_ids = {}
        with open(self.dirGroups + "index_list.txt", "r", encoding="utf-8") as file:
            for ind, line in enumerate(file):
                if ind > 0:
                    strip = line.rstrip("\n")
                    split = strip.split(" ")
                    review_ids[int(split[0])] = split[1]

        with open(self.dirQueries + "bm25_query_results.txt", "w", encoding="utf-8") as file:
            for query in bm25_scores:
                new_list = []
                file.write(f"Query\t{query}")
                for tuplo in bm25_scores[query]:
                    val = review_ids[int(tuplo[0])]
                    new_list.append(val)
                    file.write(f"\t{val}")
                bm25_scores[query] = new_list
                file.write("\n")

    # versão tp2
    def calc_bm25_vals(self, selected_groups):
        results = {}  # (doc_id, weigth_sum)

        for group in selected_groups:  # percorre grupos
            if len(selected_groups[group]) > 0:  # se grupo tiver termos pra procurar
                with open(self.dirGroups + group, "r", encoding="utf-8") as file:
                    for line in file:
                        strip = line.rstrip("\n")
                        split = strip.split("\t")
                        if split[0] in selected_groups[group]:  # se termo está nos termos do grupo a procurar
                            for ind, x in enumerate(split):
                                if ind > 1 and ind % 2 == 0:
                                    if split[ind] in results:  # se doc_id presente nos resultados
                                        results[split[ind]] += round(float(split[ind + 1]), 4)  # soma valor
                                    else:  # se doc_id não está presente
                                        results[split[ind]] = round(float(split[ind + 1]), 4)  # adiciona valor

        return results

    # todo versão tp3
    def new_calc_bm25_vals(self, selected_groups):
        # recolhe linhas pra calcular pesos
        lines = []
        for group in selected_groups:
            if len(selected_groups[group]) > 0:
                with open(self.dirGroups + group, "r", encoding="utf-8") as file:
                    for line in file:
                        strip = line.rstrip("\n")
                        split = strip.split("\t")
                        for x in selected_groups[group]:
                            if split[0] == x:
                                lines.append(line)

        # processa linhas para facilitar cálculo dos resultados
        reviews = {}
        for line in lines:
            strip = line.rstrip("\n")
            split = strip.split("\t")

            for ind, x in enumerate(split):
                if ind > 1 and ind % 3 == 2:
                    if split[ind] in reviews:
                        reviews[split[ind]].append((split[ind + 1], split[ind + 2]))  # (peso, posições)
                    else:  # review_id ainda não está presetne
                        reviews[split[ind]] = []
                        reviews[split[ind]].append((split[ind + 1], split[ind + 2]))  # (peso, posições)

        # calcula resultados finais
        results = {}
        for review in reviews:
            weight = 0
            for tup in reviews[review]:
                weight += float(tup[0])

            results[review] = weight

        return results

    # todo versão tp3
    def new_boosted_calc_bm25_vals(self, selected_groups):
        # recolhe linhas para calcular pesos
        lines = []  # linhas com termo idf review_id weight pos1_pos2_pos3 review_id weight pos1_pos2_pos3...
        for group in selected_groups:
            if len(selected_groups[group]) > 0:
                with open(self.dirGroups + group, "r", encoding="utf-8") as file:
                    for line in file:
                        strip = line.rstrip("\n")
                        split = strip.split("\t")
                        for x in selected_groups[group]:
                            if split[0] == x[0]:
                                lines.append(line)

        # processa linhas para facilitar cálculo dos resultados
        reviews = {}  # {review_id, []} -> lista de tuplos (weight, pos1_pos2_pos3)
        for line in lines:
            strip = line.rstrip("\n")
            split = strip.split("\t")

            for ind, x in enumerate(split):
                # termo idf doc_id weight pos1_pos2_pos3 doc_id weight pos1_pos2_pos3
                # 0     1   2      0      1              2      0      1 (restos da divisão do índice por 3)
                # doc_id's são sempre resto = 2
                if ind > 1 and ind % 3 == 2:  # review_id já está presente
                    if split[ind] in reviews:
                        reviews[split[ind]].append((split[ind + 1], split[ind + 2]))  # (peso, posições)
                    else:  # review_id ainda não está presetne
                        reviews[split[ind]] = []
                        reviews[split[ind]].append((split[ind + 1], split[ind + 2]))  # (peso, posições)

        # calcula resultados finais
        results = {}  # {review_id, peso_final}
        for review in reviews:  # percorre reviews
            positions = []
            # len(reviews[review]) corresponde à quantidade de termos unicos da query presentes na review
            if len(reviews[review]) > 1:
                weight = 0  # peso final da review
                for tup in reviews[review]:  # percorre tuplos da review
                    weight += float(tup[0])  # soma dos pesos do bm25
                    positions += [int(x) for x in tup[1].split("_") if int(x) >= 0]

                # boost depende de:
                # - quantidade de termos que estão na query (mais termos, maior interesse)
                span = max(positions) - min(positions)
                # - distância entre o primeiro e o último termo
                # (quanto menor, maior relevância lexical terão na review e mais semelhante será à query)
                term_amount = len(positions)
                boost = 1 + (term_amount / span)
                results[review] = weight * boost

            elif len(reviews[review]) == 1:  # apenas tem 1 tuplo(equivalente a 1 termo, logo não tem direito a boost)
                tuplos = reviews[review]  # lista de tuplos
                tuplo = tuplos[0]  # único elemento da lista
                weight = float(tuplo[0])  # (weight, pos1_pos2_pos3)
                results[review] = weight

            else:  # sem elementos na lista
                continue

        return results

    def bm25_search(self, boost):
        bm25_scores = {}

        with open(self.dirCorpus + "queries.txt", "r", encoding="utf-8") as queries:
            for query in queries:
                query = query.rstrip("\n")
                if boost:
                    # todo versão tp3
                    tokenized_query_terms = self.new_process_query(query)
                    selected_groups = self.new_get_files(tokenized_query_terms)
                    bm25_scores[query] = sorted(self.new_boosted_calc_bm25_vals(selected_groups).items(), reverse=True, key=lambda x: x[0])[0:100]
                else:
                    # versão tp2
                    tokenized_query_terms = self.process_query(query)
                    selected_groups = self.get_files(tokenized_query_terms)
                    # bm25_scores[query] = sorted(self.calc_bm25_vals(selected_groups).items(), reverse=True, key=lambda x: x[1])[0:99]
                    # todo versão tp 3
                    bm25_scores[query] = sorted(self.new_calc_bm25_vals(selected_groups).items(), reverse=True, key=lambda x: x[1])[0:99]

        self.bm25_save_results(bm25_scores)

        return bm25_scores

    """----------------------Métodos que calculam métricas----------------------"""
    # obtem os 50 resultados reais
    def get_real_results(self):
        real_results = {}
        counter = 0
        with open(self.dirCorpus + "queries.relevance.txt", "r", encoding="utf-8") as file:
            query = None
            for line in file:
                if line.startswith("Q"):
                    strip = line.rstrip("\n")
                    split = strip.split(":")
                    query = split[1]
                    real_results[query] = []
                    counter = 0

                else:  # guarda apenas k valores
                    strip = line.rstrip("\n")
                    split = strip.split("\t")
                    if len(split) < 2:  # ignora linhas vazias
                        continue
                    real_results[query].append((split[0], int(split[1])))  # (review_id, relevance)
                    counter += 1

        return real_results

    # calcula precison, recall e f_measure
    def calc_prf(self, real_k_results, obtained_k_results):

        true_positives = 0
        false_positives = 0
        false_negatives = 0
        moment_precisions = []

        real_k_results_ids = []  # facilita identificar true positives
        for x in real_k_results:
            real_k_results_ids.append(x[0])  # guarda apenas os ids

        # percore resultados obtidos
        for review in obtained_k_results:
            if review in real_k_results_ids:
                true_positives += 1
                moment = true_positives / (true_positives + false_positives)
                moment_precisions.append(moment)
            else:
                false_positives += 1
                moment = true_positives / (true_positives + false_positives)
                moment_precisions.append(moment)

        # percorre resultados reais
        for tup in real_k_results:
            review = tup[0]
            relevance = tup[1]  # não utilizado aqui...
            if review not in obtained_k_results:
                false_negatives += 1

        # calcula valores
        if true_positives + false_positives == 0:
            precision = 0
        else:
            precision = true_positives / (true_positives + false_positives)

        recall = true_positives / (true_positives + false_negatives)

        if precision + recall == 0:
            f_measure = 0
        else:
            f_measure = (2 * precision * recall) / (precision + recall)

        return precision, recall, f_measure, sum(moment_precisions) / len(moment_precisions)

    def calc_ndcg(self, real_k_results, obtained_k_results):
        real_dcg = []
        obtained_dcg = []

        # calcula dcg real
        for ind, tup in enumerate(real_k_results):
            review_id = tup[0]  # não é utilizado...
            relevance = tup[1]
            if ind > 0:
                gain = relevance + (relevance / math.log2(ind + 1))
                real_dcg.append(gain)
            else:
                real_dcg.append(relevance)

        # calcula dcg obtido
        for ind, review in enumerate(obtained_k_results):
            relevance = 0
            for tup in real_k_results:
                if tup[0] == review:
                    relevance = tup[1]

            if len(obtained_dcg) == 0:  # primeiro elemento
                obtained_dcg.append(relevance)
            else:
                gain = relevance + (relevance / math.log2(ind + 1))
                obtained_dcg.append(gain)

        # calcula ndcg vals
        ndcg = []
        for x in range(len(real_dcg)):
            val = obtained_dcg[x] / real_dcg[x]
            ndcg.append(val)

        return ndcg

    # calculate metrics
    def calc_metrics(self, obtained_results):

        # carrega todos os resultados
        real_results = self.get_real_results()

        for query in obtained_results:
            query_latencies = []
            query_throughput_start = time.time()
            print(f"\n---------------------------------------Query: {query}---------------------------------------")

            for k in (10, 20, 50):
                # obtem k resultados reais e obtidos de uma certa query
                # real_k_results = OrderedDict()
                # for review, relevance in real_results[query][0:k]:
                #     real_k_results[review] = relevance
                real_k_results = real_results[query][:k]

                # obtained_k_results = OrderedDict()
                # i = 0
                # for review in obtained_results[query][:k]:
                #     obtained_k_results[review] = None
                obtained_k_results = obtained_results[query][:k]

                # calcula precision, recall e f-measure
                prf = self.calc_prf(real_k_results, obtained_k_results)

                # calcula normalized discounted cumulative gain
                ndcg = self.calc_ndcg(real_k_results, obtained_k_results)

                # avg_query_throughput = self.calc_aqt()
                # median_query_latency = self.calc_mql()

                query_throughput_end = time.time()
                query_latencies.append(query_throughput_end - query_throughput_start)

                # print dos resultados
                print(f"K: {k}")
                print(f"\tPrecision: {prf[0]}\tAverage precision: {prf[3]}\tRecall: {prf[1]}")
                print(f"\tF-measure: {prf[2]}\tNormalized Discounted Cumulative Gain: {ndcg}")
                print(f"\tAverage query throughput: {(query_throughput_end - query_throughput_start) / k}")

            print(f"Median query latency: {sum(query_latencies) / len(query_latencies)}")

    """Método principal"""
    # search method
    def search(self, weight_method, boost):
        scores = None

        self.dir_create()

        if weight_method == 0:
            scores = self.vsm_search(boost)
        else:
            scores = self.bm25_search(boost)

        self.calc_metrics(scores)

        return scores
