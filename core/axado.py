# -*- coding: utf-8 -*-
__author__ = 'infante'

u"""Este módulo realiza leitura da base de informações e realiza calculo de fretes a partir de parâmetros de entrada
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
    u"""Calcula o arredontamento para cima do valor utilizando o número de casas decimais informadas"""
    return ceil((10**casas_decimais * valor)) / float(10**casas_decimais)


def checa_numerico(valor):
    u"""Verifica se a string valor contém um valor numérico (int, long, float)"""

    # Tenta separar a string no caractere ponto ('.', para tratar float) e verifica se caracteres resultantes da
    # separacao sao todos digitos (0 a 9), montando uma lista de booleanos (um para cada caractere avaliado).
    # Em seguida retorna a reducao da lista aplicando um 'AND' dois a dois dos booleanos
    return reduce(lambda x, y: x and y, [num.isdigit() for num in valor.split(".")])


def imprime_resultados():
    for k in sorted(RESULTADOS.keys()):
        if RESULTADOS[k]['prazo'] and RESULTADOS[k]['frete']:
            print "%s:%d, %.2f" % (k, RESULTADOS[k]['prazo'], RESULTADOS[k]['frete'])
        else:
            print "%s:-, -" % k


def constroi_dicionario_de_informacoes(arquivo, delimitador, dicionario_destino, tabela_destino):
    with open(arquivo, 'r') as csv_file:
        rotas = csv.reader(csv_file, delimiter=delimitador)
        referencia = {}
        for ind, r in enumerate(rotas):
            valores = {}
            for i, v in enumerate(r):
                if ind == 0:
                    referencia[i] = v
                else:
                    if checa_numerico(v):
                        valores[referencia[i]] = float(v)
                    else:
                        valores[referencia[i]] = v
            if valores:
                globals()[dicionario_destino][tabela_destino].append(valores)


def constroi_dicionarios():
    for t in os.listdir(DIR_TABELAS):
        ROTAS[t] = []
        PRECO_POR_KG[t] = []
        separador = SEPARADOR_PADRAO
        for f in next(os.walk(os.path.join(DIR_TABELAS, t)))[2]:
            nome, extensao = os.path.splitext(f)
            if extensao == CSV[0]:
                separador = CSV[1]
            elif extensao == TSV[0]:
                separador = TSV[1]
            constroi_dicionario_de_informacoes(os.path.join(DIR_TABELAS, t, f), separador, nome.upper(), t)


def pega_registro_rota(tabela, origem, destino):
    for reg in ROTAS[tabela]:
        if reg['origem'] == origem and reg['destino'] == destino:
            return reg
    return None


def pega_preco_faixa(tabela, nome, peso):
    for reg in PRECO_POR_KG[tabela]:
        if reg['nome'] == nome:
            if (isinstance(reg['final'], float) and reg['inicial'] <= peso <= reg['final'] - TOLERANCIA) or \
               (reg['final'] == '' and peso >= reg['inicial']):
                return reg['preco']
    return None


def excede_limite_peso(peso, limite):
    if peso > limite > 0:
        return True
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
    RESULTADOS_TESTE = RESULTADOS
    for k in sorted(RESULTADOS_TESTE.keys()):
        for kk in RESULTADOS_TESTE[k].keys():
            if RESULTADOS_TESTE[k][kk] == 0:
                RESULTADOS_TESTE[k][kk] = "-"
    return RESULTADOS_TESTE

if __name__ == '__main__':
    calcula_prazos_e_valores(sys.argv[1:])
    imprime_resultados()
