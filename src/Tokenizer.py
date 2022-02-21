import re
from nltk.stem import PorterStemmer


class Tokenizer:
    """
    Visa tokenizar cada palavra numa dada string.
    Para além de tokenizar, também processa cada token conforme as caraterísticas pretendidas.
    """

    def __init__(self, conf=None):
        if conf:  # configuração do tokenizer
            self.stopword_filter = []
            self.porter_stemmer = None
            self.load_conf(conf)

        else:  # configuração default
            self.min_len = 3
            self.stopword_filter = []
            self.porter_stemmer = None

    def load_conf(self, conf):
        with open(conf, "r", encoding="utf-8") as file:
            for line in file:
                strip = line.rstrip("\n")
                split = strip.split(" ")

                if split[0] == "#":  # ignora linha comentada
                    continue

                if split[0] == "min_len":
                    self.min_len = int(split[1])

                if split[0] == "porter_stemmer" and split[1] == "True":
                    self.porter_stemmer = PorterStemmer()

                if split[0] == "stopword_list":
                    for ind, x in enumerate(split):
                        if ind > 0:
                            self.stopword_filter.append(x)

    # versão tp2
    """Separa as palavras e seleciona-as com base nos requerimentos."""
    def tokenize(self, string, tokenized_words):
        # split da string
        words = re.split("[^A-Za-z0-9]+", string)

        # tamanho máximo por causa de uma string com uns 30 "Z"
        words = [x for x in words if self.min_len <= len(x) < 15 and x not in self.stopword_filter]  # opção 1

        if self.porter_stemmer:
            for x in range(len(words)):
                words[x] = self.porter_stemmer.stem(words[x])

        tokenized_words += words

    # versão tp3
    """Separa as palavras e seleciona-as com base nos requerimentos. Guarda também a posição da palavra."""
    def new_tokenize(self, string, tokenized_words):
        # split da string
        words = re.split("[^A-Za-z0-9]+", string)

        # seleciona apenas as que verificam os requerimentos (também adiciona a posição/índice da palavra na review)
        words = [(x, ind) for ind, x in enumerate(words) if
                 self.min_len <= len(x) < 15 and x not in self.stopword_filter]

        if self.porter_stemmer:
            for x in range(len(words)):
                tup = words[x]
                # cria novo tuplo e substitui o anterior
                words[x] = (self.porter_stemmer.stem(tup[0]), tup[1])

        tokenized_words += words
