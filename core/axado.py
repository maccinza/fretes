# -*- coding: utf-8 -*-
__author__ = 'infante'

import csv
import os
from pprint import pprint

DIR_BASE = os.path.dirname(os.path.dirname(__file__))
DIR_TABELAS = os.path.join(DIR_BASE, 'tabelas')

ROTAS = {}
PRECO_POR_KG = {}
SEPARADOR_PADRAO = ','
CSV = ('.csv', ',')
TSV = ('.tsv', '\t')

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


