#Recuperação de Informação

##Assignment 3 - Boosting and Metric Evaluation .
Este trabalho foi feito no âmbito da unidade curricular de **Recuperação de Informação**.

O algoritmo, conforme os parâmetros introduzidos, indexa o ficheiro indicado.
Possui 2 modos de execução, **_reverse indexing_** e **_weighted search_**.

O **_reverse indexing_** passa pelas seguintes fases de execução:
- indexação reversa de chunks do fichiero alvo;
- junção dos chunks(resultado final são vários "grupos" que possuem os termos indexados sem repetição e já pesados);
- compacta os grupos;

O **_weighted search_** passa pelas seguintes fases de execução:
- tokenização da query;
- seleção dos ficheiros onde estão os termos da query processados;
- pesa reviews, aplica boost caso especificado, e guarda resultado;
- seleciona os top 100 resultados da query e escreve-os num ficheiro .txt;
- calcula métricas para os top 10, 20 e 50 resultados obtidos de cada query;


###Classes
####- **Tokenizer**
Classe que recebe uma string(review) e a divide em vários _tokens_.
Cada _token_ é depois processado de acordo com várias regras estipuladas tais como:
    
- tamanho mínimo
- _stopword list_
- _snowball stemmer_

As palavras utilizadas na **_stopword list_** são as primeiras 30 de acordo com o primeiro link na referência.

####- **_Indexer_**
Classe que recebe os tokens(review processada) e os indexa de acordo com o método **_reverse indexing_**.

Toda a informação é armazenada numa estrutura do tipo **_dictionary_**, onde a **_key_** é o token processado
e o **_value_** é um "**_sub-dictionary_**". 

No "**_sub-dictionary_**" a **_key_** é o **identifier** da review
e o **_value_** a frequência do termo na _review_.

####- **_Merger_**
Classe responsável por fazer o "_merge_" de todos os _chunks_.

####- **_Counter_**
Classe que serve como contador, foi criada para o caso de ser necessário contar iterações
dentro de funções que já retornam valores.

####- **_Searcher_**
Classe que procura a informação pretendida. Para cada query procura os top 100 resultados e guarda-os
num ficheiro .txt.


###Instruções
Na diretoria do projeto, os corpus necessitam de estar numa pasta **".corpus"** e **descomprimidos**.

O ficheiro "queries.relevance.txt" também necessita de estar na diretoria **.corpus**.

Para alterar as configurações to tokenizer alterar o ficheiro tokenizer.conf. Linhas que começam por um
"#" são ignoradas.

Para correr o programa em modo "pesquisar", é necessário primeiro "indexar" o ficheiro pretendido.

O algoritmo possui várias flags para especificar o comportamento do mesmo, sendo elas:
- [-m] modo de execução -> 0 para indexar | 1 para pesquisar
- [-w] método de pesagem -> 0 para VSM | 1 para BM25
- [-f] nome do ficheiro alvo de indexação
- [-q] tamanho dos chunks -> quantidade de reviews que cada chunk vai possuir
- [-t] opções do tokenizer -> carrega configurações do tokenizer.conf (para modo 0 e 1)
- [-b] opção para aplicar boost ao fazer search das queries

###Resultados do Searcher
Os resultados são apresentados no ecrã após a realização das queries e cálculo das métricas.

###Resultados do Indexer
####- amazon_reviews_us_Digital_Video_Games_v1_0(71Mb)
##### vsm
|        Caraterísticas         | Run nº 1 | Run nº 2 | Run nº 3 | Run nº 4 |
|:-----------------------------:|:--------:|:--------:|:--------:|:--------:|
|        tamanho mínimo         |    3     |    0     |    0     |    3     |
|         stopword list         |    x     |    v     |    x     |    v     |
|        Porter Stemmer         |    x     |    x     |    v     |    v     |
|        Tempo indexação        |  10.5s   |  13.3s   |  124.7s  |  98.6s   |
|          Tempo merge          |  12.8s   |  13.2s   |  11.4s   |  8.85s   |
|       Tempo compressão        |  15.3s   |  15.8s   |  16.9s   |  12.9s   |
|       Quantidade termos       |  96334   |  97891   |  51761   |  51140   |
|       Quantidade chunks       |    15    |    15    |    15    |    15    |
|      Threshold de linhas      |  10000   |  10000   |  10000   |  10000   |
| Tamanho indexação(pre-merge)  | 51.76Mb  | 54.05Mb  | 57.13Mb  | 42.70Mb  |
| Tamanho indexação(pos-merge)  | 133.97Mb | 133.97Mb | 74.39Mb  | 129.16Mb |
| Tamanho indexação(compactada) | 37.98Mb  | 37.98Mb  | 20.55Mb  | 36.03Mb  |

##### bm25
|        Caraterísticas         | Run nº 1 | Run nº 2 | Run nº 3 | Run nº 4 |
|:-----------------------------:|:--------:|:--------:|:--------:|:--------:|
|        tamanho mínimo         |    3     |    0     |    0     |    3     |
|         stopword list         |    x     |    v     |    x     |    v     |
|        Porter Stemmer         |    x     |    x     |    v     |    v     |
|        Tempo indexação        |   9.6s   |  12.1s   |  113.5s  |  100.4s  |
|          Tempo merge          |  14.3s   |  15.3s   |  14.4s   |  12.3s   |
|       Tempo compressão        |  11.1s   |  11.3s   |  13.8s   |  10.4s   |
|       Quantidade termos       |  96334   |  97891   |  51761   |  51140   |
|       Quantidade chunks       |    15    |    15    |    15    |    15    |
|      Threshold de linhas      |  10000   |  10000   |  10000   |  10000   |
| Tamanho indexação(pre-merge)  | 51.76Mb  | 54.05Mb  | 57.13Mb  | 42.70Mb  |
| Tamanho indexação(pos-merge)  | 79.92Mb  | 163.53Mb | 253.12Mb | 319.90Mb |
| Tamanho indexação(compactada) | 20.69Mb  | 42.30Mb  | 64.33Mb  | 81.21Mb  |

####- amazon_reviews_us_Digital_Music_Purchase_v1_00.tsv(600Mb)
##### vsm
|        Caraterísticas         | Run nº 1 | Run nº 2  | Run nº 3  | Run nº 4  |
|:-----------------------------:|:--------:|:---------:|:---------:|:---------:|
|        tamanho mínimo         |    3     |     0     |     0     |     3     |
|         stopword list         |    x     |     v     |     x     |     v     |
|        Porter Stemmer         |    x     |     x     |     v     |     v     |
|        Tempo indexação        |  85.8s   |  110.1s   |  924.6s   |  761.4s   |
|          Tempo merge          |  162.3s  |  169.5s   |  157.8s   |  116.5s   |
|       Tempo compressão        |  135.7s  |  139.3s   |  156.4s   |  110.7s   |
|       Quantidade termos       |  482369  |  482922   |  293641   |  293049   |
|       Quantidade chunks       |   169    |    169    |    169    |    169    |
|      Threshold de linhas      |  10000   |   10000   |   10000   |   10000   |
| Tamanho indexação(pre-merge)  | 507.62Mb | 534.13Mb  | 578.98Mb  | 420.43Mb  |
| Tamanho indexação(pos-merge)  | 600.78Mb | 1232.93Mb | 2019.30Mb | 2516.36Mb |
| Tamanho indexação(compactada) | 164.67Mb | 337.48Mb  | 519.59Mb  | 653.58Mb  |

##### bm25
|        Caraterísticas         | Run nº 1 | Run nº 2  | Run nº 3  | Run nº 4  |
|:-----------------------------:|:--------:|:---------:|:---------:|:---------:|
|        tamanho mínimo         |    3     |     0     |     0     |     3     |
|         stopword list         |    x     |     v     |     x     |     v     |
|        Porter Stemmer         |    x     |     x     |     v     |     v     |
|        Tempo indexação        |  92.3s   |  140.3s   |  950.2s   |  760.0s   |
|          Tempo merge          |  150.2s  |  208.3s   |  219.1s   |  158.8s   |
|       Tempo compressão        |  132.0s  |  108.1s   |  130.1s   |   91.1s   |
|       Quantidade termos       |  482369  |  484922   |  293641   |  293049   |
|       Quantidade chunks       |   169    |    169    |    169    |    169    |
|      Threshold de linhas      |  10000   |   10000   |   10000   |   10000   |
| Tamanho indexação(pre-merge)  | 507.62Mb | 534.13Mb  | 578.98Mb  | 420.43Mb  |
| Tamanho indexação(pos-merge)  | 870.30Mb | 1086.92Mb | 2657.41Mb | 2761.75Mb |
| Tamanho indexação(compactada) | 238.30Mb | 264.98Mb  | 660.68Mb  | 667.65Mb  |

####- amazon_reviews_us_Digital_Music_Purchase_v1_00.tsv(3.58Gb)
##### vsm
|        Caraterísticas         | Run nº 1  |
|:-----------------------------:|:---------:|
|        tamanho mínimo         |     3     |
|         stopword list         |     x     |
|        Porter Stemmer         |     x     |
|        Tempo indexação        |  795.1s   |
|          Tempo merge          |  2163.9s  |
|       Tempo compressão        |  1041.4s  |
|       Quantidade termos       |  1545450  |
|       Quantidade chunks       |    476    |
|      Threshold de linhas      |   10000   |
| Tamanho indexação(pre-merge)  | 3177.18Mb |
| Tamanho indexação(pos-merge)  | 4778.15Mb |
| Tamanho indexação(compactada) | 1249.72Mb |

##### bm25
|        Caraterísticas         | Run nº 1  |
|:-----------------------------:|:---------:|
|        tamanho mínimo         |     3     |
|         stopword list         |     x     |
|        Porter Stemmer         |     x     |
|        Tempo indexação        |  815.1s   |
|          Tempo merge          |  1614.5s  |
|       Tempo compressão        |  865.3s   |
|       Quantidade termos       |  1545450  |
|       Quantidade chunks       |    476    |
|      Threshold de linhas      |   10000   |
| Tamanho indexação(pre-merge)  | 3177.18Mb |
| Tamanho indexação(pos-merge)  | 4513.71Mb |
| Tamanho indexação(compactada) | 1043.41Mb |


###Notas
As 30 palavras utilizadas sãos as 30 mais comuns na língua inglesa. Podem ser encontradas no seguinte link:
https://web.archive.org/web/20111226085859/http://oxforddictionaries.com/words/the-oec-facts-about-the-language

Os tempos de indexação **são da meta anterior**.
As métricas apresentam resultados **péssimos (aprox. 0)**, pelo que o problema deve estar no cálculo dos pesos?
Devido a complicações fora do meu controlo, **explícitas no mail ao professor**, não foi possível corrigir o erro
e atualizar os tempos.

