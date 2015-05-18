# -*- coding: utf-8 -*-
__author__ = 'infante'

import csv
import os
import sys
from pprint import pprint

DIR_BASE = os.path.dirname(os.path.dirname(__file__))
DIR_TABELAS = os.path.join(DIR_BASE, 'tabelas')

ROTAS = {}
PRECO_POR_KG = {}
SEPARADOR_PADRAO = ','
CSV = ('.csv', ',')
TSV = ('.tsv', '\t')
ICMS_FIXO = 6
TOLERANCIA = 0.01
RESULTADOS = {}


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
                    if v.isdigit():
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


def calcula_tabela_um(*params):
    subtotal = 0
    origem, destino, nota, peso = params
    registro_rota = pega_registro_rota('tabela', origem, destino)
    if registro_rota:
        prazo = registro_rota['prazo']
        subtotal += float(nota * registro_rota['seguro'])/100
        subtotal += registro_rota['fixa']
        preco_faixa = pega_preco_faixa('tabela', registro_rota['kg'], peso)
        # TODO: refatorar para retornar "tabela:-, -" nos casos de excecao listados
        if preco_faixa:
            pass
        else:
            print u"O peso informado não se encaixa em nenhuma faixa de limites de pesos."
    else:
        print u"Não há registros de  disponível para a origem e destino informados."





def calcula_tabela_dois():
    pass


def calcula_total(params):
    try:
        script, origem, destino, nota, peso = params
        constroi_dicionarios()
        calcula_tabela_um(origem, destino, float(nota), float(peso))
        #calcula_tabela_dois(origem, destino, nota, peso)

    except ValueError:
        print u"Erro nos parâmetros de entrada. Verifique a entrada fornecida para o script e tente novamente."
        print u"Uso: python axado.py origem destino valor_nota peso"


if __name__ == '__main__':
    calcula_total(sys.argv)
