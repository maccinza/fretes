# -*- coding: utf-8 -*-
__author__ = 'infante'

u"""Módulo para realizar leitura da base de informações e cálculo de fretes a partir de parâmetros de entrada
que informam origem, destino, preço de nota e peso de um pacote.
"""

# importa modulo csv para ler os arquivos de base de dados, os para realizar tratamento de paths,
# sys para obter parametros de entrada do programa e a funcao ceil do modulo math para calulo do arredontamento
import csv
import os
import sys
from math import ceil

# define caminho para diretorio base do projeto e caminho para o diretorio de tabelas
DIR_BASE = os.path.dirname(os.path.dirname(__file__))
DIR_TABELAS = os.path.join(DIR_BASE, 'tabelas')

# Inicializa variaveis globais do programa e valores default
# ROTAS: dicionario com as informacoes coletadas dos arquivos rotas.csv e rotas.tsv
# PRECO_POR_KG: dicionario com as informacoes coletadas dos arquivos preco_por_kg.csv e preco_por_kg.tsv
# SEPARADOR_PADRAO: define um separador padrao a ser utilizado na leitura dos arquivos de dados
# CSV: tupla que relaciona extensao csv com o caractere a ser utilizado como separador no arquivo (csv)
# TSV: tupla que relaciona extensao tsv com o caractere a ser utilizado como separador no arquivo (tsv)
# ICMS_FIXO: valor de icms considerado para os calculos dos fretes de tabela
# TOLERANCIA: float indicando a tolerancia de diferenca entre os valores limites superiores de uma faixa e o peso
# CASAS_DECIMAIS: inteiro que define o numero de casas decimais utilizadas no arredontamento
# RESULTADOS: dicionario que armazena os resultados dos calculos de frete para todas as tabelas
ROTAS = {}
PRECO_POR_KG = {}
SEPARADOR_PADRAO = ','
CSV = ('.csv', ',')
TSV = ('.tsv', '\t')
ICMS_FIXO = 6
TOLERANCIA = 0.01
CASAS_DECIMAIS = 2
RESULTADOS = {}


def arredonda_para_cima(valor, casas_decimais):
    u"""Calcula e retorna o arredondamento para cima do valor utilizando o número de casas decimais informado."""
    return ceil((10**casas_decimais * valor)) / float(10**casas_decimais)


def checa_numerico(valor):
    u"""Verifica se a string 'valor' contém um valor numérico (int, long, float). Retorna verdadeiro em caso positivo
    e falso caso contrário.
    """

    # Tenta separar a string no caractere ponto ('.', para tratar float) e verifica se caracteres resultantes da
    # separacao sao todos digitos (0 a 9), montando uma lista de booleanos (um para cada caractere avaliado).
    # Em seguida retorna a reducao da lista aplicando um 'AND' dois a dois dos booleanos
    return reduce(lambda x, y: x and y, [num.isdigit() for num in valor.split(".")])


def imprime_resultados():
    u"""Imprime resultado dos cálculos armazenado na variável global RESULTADOS no formato de saída especificado."""

    # para cada chave (nome da tabela) do dicionario de resultados
    for k in sorted(RESULTADOS.keys()):
        # verifica se os valores de prazo e frete existem
        if RESULTADOS[k]['prazo'] and RESULTADOS[k]['frete']:
            # em caso positivo imprime os valores no formato de saida 'nome_tabela:prazo, frete'
            print "%s:%d, %.2f" % (k, RESULTADOS[k]['prazo'], RESULTADOS[k]['frete'])
        else:
            # caso contrario, imprime o padrao vazio 'nome_tabela:-, -'
            print "%s:-, -" % k


def constroi_dicionario_de_informacoes(arquivo, delimitador, dicionario_destino, tabela_destino):
    u"""Constrói dicionário com todas as informações (origem, destino, prazo, etc...) sobre os fretes a partir
    de um arquivo fonte de dados.
    """

    # abre para leitura o arquivo de fonte de dados passado como parametro utilizando o delimitador informado
    # como separador dos dados
    with open(arquivo, 'r') as csv_file:
        rotas = csv.reader(csv_file, delimiter=delimitador)
        # cria dicionario auxiliar vazio
        referencia = {}
        # para cada par (indice da linha, linha) do arquivo de informacoes
        for ind, r in enumerate(rotas):
            # dicionario auxiliar com os nomes das informacoes como chave e os valores das informacoes de uma linha
            # como valores
            valores = {}
            for i, v in enumerate(r):
                # utiliza dicionario auxiliar 'referencia' para relacionar os indices (ordem de aparecimento na linha)
                # aos nomes das informacoes (origem, destino, prazo, etc...) existentes caso seja a primeira linha do
                # arquivo (linha que contem os nomes das informacoes)
                if ind == 0:
                    referencia[i] = v
                else:
                    # para as demais linhas, converte o valor da informacao para float caso seja um valor numerico
                    # gravando-a na chave correta do dicionario de valores da linha (ex.: valores['prazo'] = 1.0)
                    if checa_numerico(v):
                        valores[referencia[i]] = float(v)
                    # ou simplesmente gravando-a como string na chave correta do dicionario de valores da linha
                    else:
                        valores[referencia[i]] = v
            # se foram lidos valores de informacoes para a linha
            if valores:
                # adiciona valores na 'tabela' (chave) do dicionario destino informados como parametros de entrada
                globals()[dicionario_destino][tabela_destino].append(valores)


def constroi_dicionarios():
    u"""Inspeciona diretórios de tabelas e chama a função de coleta de informações para os arquivos de informações sobre
    fretes encontrados.
    """

    # para cada diretorio (nome de tabela) no diretorio de tabelas
    for t in os.listdir(DIR_TABELAS):
        # atribui a chave 'nome_da_tabela' aos dicionarios de rotas e precos, inicializando os valores como listas
        # vazias
        ROTAS[t] = []
        PRECO_POR_KG[t] = []
        # utiliza separador padrao para o caso de nao conseguir inferir o separador a ser utilizado
        separador = SEPARADOR_PADRAO
        # para cada arquivo existente no diretorio que representa uma tabela
        for f in next(os.walk(os.path.join(DIR_TABELAS, t)))[2]:
            # pega nome e extensao do arquivo
            nome, extensao = os.path.splitext(f)
            # e decide qual separador de dados utilizar baseado na extensao do arquivo
            if extensao == CSV[0]:
                separador = CSV[1]
            elif extensao == TSV[0]:
                separador = TSV[1]
            # chama funcao de coleta de informacoes para construir os dicionarios de informacoes
            constroi_dicionario_de_informacoes(os.path.join(DIR_TABELAS, t, f), separador, nome.upper(), t)


def pega_registro_rota(tabela, origem, destino):
    u"""Procura um registro de rota a partir da origem (parâmetro de entrada), destino (parâmetro de entrada)
    e uma tabela (parâmetro de entrada)
    """

    # para cada registro da tabela de rotas informada
    for reg in ROTAS[tabela]:
        # verifica se a origem e o destino do registro coincidem com os valores desejados
        if reg['origem'] == origem and reg['destino'] == destino:
            # em caso positivo, retorna o registro
            return reg
    # retorna None caso nao encontre um registro de rota satisfatorio
    return None


def pega_preco_faixa(tabela, nome, peso):
    u"""Obtem preco a ser pago por kg para um pacote em uma tabela a partir do nome da tabela, do nome da faixa de
     precificação e do peso do pacote.
    """

    # para cada registro de precificacao da tabela indicada
    for reg in PRECO_POR_KG[tabela]:
        # se o registro possui o nome informado na chamada da funcao
        if reg['nome'] == nome:
            # verifica se o valor final do limite eh um valor float (pode ser string quando nao ha limite final)
            # e se o peso informado e maior ou igual ao valor inicial e menor ou igual ao valor final do limite
            # subtraida a tolerancia
            # OU se o nao existe valor final para o limite e o peso eh maior que o valor inicial do limite
            if (isinstance(reg['final'], float) and reg['inicial'] <= peso <= reg['final'] - TOLERANCIA) or \
               (reg['final'] == '' and peso >= reg['inicial']):
                # neste caso, retorna o preco por kg da faixa encontrada
                return reg['preco']
    # retorna None caso nao encontre um registro que satisfaca as condicoes
    return None


def excede_limite_peso(peso, limite):
    u"""Verifica se o valor de peso excede os limites de peso de uma rota a partir dos valore do peso e do limite"""

    # caso haja um limite e o peso exceda este limite
    if peso > limite > 0:
        # retorna verdadeiro
        return True
    # retorna falso caso o peso nao exceda o limite
    return False


def calcula_seguro(valor_nota, taxa_seguro):
    return float(valor_nota * taxa_seguro)/100


def calcula_preco_faixa(peso, taxa_faixa):
    return float(peso * taxa_faixa)


def calcula_alfandega(subtotal, alfandega):
    return subtotal * (float(alfandega) / 100)


def calcula_icms(subtotal, icms):
    return float(subtotal)/(float(100 - icms) / 100)


def calcula_tabela_um(*params):
    subtotal = 0
    origem, destino, nota, peso = params
    registro_rota = pega_registro_rota('tabela', origem, destino)
    if registro_rota:
        prazo = int(registro_rota['prazo'])
        subtotal += calcula_seguro(nota, registro_rota['seguro'])
        subtotal += registro_rota['fixa']
        preco_faixa = pega_preco_faixa('tabela', registro_rota['kg'], peso)

        if preco_faixa:
            subtotal += calcula_preco_faixa(peso, preco_faixa)
            subtotal = arredonda_para_cima(calcula_icms(subtotal, ICMS_FIXO), CASAS_DECIMAIS)
        else:
            prazo = 0
            subtotal = 0
    else:
        prazo = 0
        subtotal = 0

    RESULTADOS['tabela'] = {'prazo': prazo,
                            'frete': subtotal}


def calcula_tabela_dois(*params):
    subtotal = 0
    origem, destino, nota, peso = params
    registro_rota = pega_registro_rota('tabela2', origem, destino)
    if not registro_rota or excede_limite_peso(peso, registro_rota['limite']):
        prazo = 0
        subtotal = 0
    else:
        prazo = int(registro_rota['prazo'])
        subtotal += calcula_seguro(nota, registro_rota['seguro'])
        preco_faixa = pega_preco_faixa('tabela2', registro_rota['kg'], peso)
        if preco_faixa:
            subtotal += calcula_preco_faixa(peso, preco_faixa)
            subtotal += calcula_alfandega(subtotal, registro_rota['alfandega'])
            subtotal = arredonda_para_cima(calcula_icms(subtotal, registro_rota['icms']), CASAS_DECIMAIS)
        else:
            prazo = 0
            subtotal = 0

    RESULTADOS['tabela2'] = {'prazo': prazo,
                             'frete': subtotal}


def calcula_prazos_e_valores(params):
    try:
        origem, destino, nota, peso = params
        constroi_dicionarios()
        calcula_tabela_um(origem, destino, float(nota), float(peso))
        calcula_tabela_dois(origem, destino, float(nota), float(peso))

    except ValueError:
        print u"Erro nos parâmetros de entrada. Verifique a entrada fornecida para o script e tente novamente.\n" \
              u"Uso: python axado.py origem destino valor_nota peso"


def testa_calculos(params):
    calcula_prazos_e_valores(params)
    resultados_teste = RESULTADOS
    for k in sorted(resultados_teste.keys()):
        for kk in resultados_teste[k].keys():
            if resultados_teste[k][kk] == 0:
                resultados_teste[k][kk] = "-"
    return resultados_teste

if __name__ == '__main__':
    calcula_prazos_e_valores(sys.argv[1:])
    imprime_resultados()
