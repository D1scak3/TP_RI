class Indexer:
    def __init__(self):
        pass

    # versão tp2
    """Verifica se a palavra já existe
    indexed_info={termo, subd_dic}
    subd_dic={doc_id, count}"""
    def index(self, tokenized_words, identifier, indexed_info):
        for word in tokenized_words:
            if word not in indexed_info:
                indexed_info[word] = {}
                indexed_info[word][identifier] = 1
            
            else:
                if identifier not in indexed_info[word]:
                    indexed_info[word][identifier] = 1
                
                else:
                    indexed_info[word][identifier] += 1

    # versão tp3
    """Verifica se a palavra já existe
    indexed_info={termo, sub_dic}
    sub_dic={doc_id, lista }
    lista = [pos1, pos2, pos3]
    a lista possui posições ordenadas, pk os termos vêm por ordem"""
    def new_index(self, tokenized_words, identifier, indexed_info):
        for tup in tokenized_words:  # tup = (termo, posição)
            if tup[0] not in indexed_info:
                indexed_info[tup[0]] = {}
                indexed_info[tup[0]][identifier] = []
                indexed_info[tup[0]][identifier].append(tup[1])

            else:
                if identifier not in indexed_info[tup[0]]:
                    indexed_info[tup[0]][identifier] = []
                    indexed_info[tup[0]][identifier].append(tup[1])

                else:
                    indexed_info[tup[0]][identifier].append(tup[1])
