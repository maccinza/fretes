# -*- coding: utf-8 -*-
__author__ = 'infante'

import unittest
from axado import testa_calculos, arredonda_para_cima, checa_numerico, excede_limite_peso,\
    calcula_seguro, calcula_preco_faixa, calcula_alfandega, calcula_icms


class TestAuxiliar(unittest.TestCase):

    def test_arredonda_para_cima(self):
        resultados = (10.91, 23.245, 0.47)
        self.assertEqual((arredonda_para_cima(10.9071, 2),
                          arredonda_para_cima(23.24412, 3),
                          arredonda_para_cima(0.46127, 2)), resultados)

    def test_checa_numerico(self):
        valores = ('string', '12.32', '0.225', '1', '10e2', '1000021340000')
        self.assertEqual([False, True, True, True, False, True], [checa_numerico(v) for v in valores])

    def test_excede_limite_peso(self):
        valores = ((10.5, 10), (0.25, 1), (0.331, 0), (40, 25))
        self.assertEqual([True, False, False, True], [excede_limite_peso(v[0], v[1]) for v in valores])

    def test_calculo_seguro(self):
        valores = ((50, 2), (70, 3), (5.5, 4), (21.5, 6))
        self.assertEqual([1, 2.1, 0.22, 1.29], [calcula_seguro(v[0], v[1]) for v in valores])

    def test_calcula_preco_faixa(self):
        valores = ((10.5, 10), (0.25, 1), (70, 3), (40, 25))
        self.assertEqual([105, 0.25, 210, 1000], [calcula_preco_faixa(v[0], v[1]) for v in valores])

    def test_calcula_alfandega(self):
        valores = ((50, 2), (70, 3), (5.5, 4), (21.5, 6))
        self.assertEqual([1, 2.1, 0.22, 1.29], [calcula_alfandega(v[0], v[1]) for v in valores])

    def test_calcula_icms(self):
        valores = ((50, 2), (70, 3), (5.5, 4), (21.5, 6))
        self.assertEqual([51.02040816326531, 72.16494845360825, 5.729166666666667, 22.872340425531917],
                         [calcula_icms(v[0], v[1]) for v in valores])


class TestAxado(unittest.TestCase):

    def test_flo_bra_50_1(self):
        resultado = {'tabela': {'prazo': 3, 'frete': 28.2}, 'tabela2': {'frete': 16.49, 'prazo': 2}}
        self.assertEqual(testa_calculos(('florianopolis', 'brasilia', '50', '1')), resultado)

    def test_flo_cur_55_5(self):
        resultado = {'tabela': {'prazo': 3, 'frete': 73.04}, 'tabela2': {'frete': 81.33, 'prazo': 2}}
        self.assertEqual(testa_calculos(('florianopolis', 'curitiba', '55', '5')), resultado)

    def test_flo_sao_60_10(self):
        # faixa de peso nao existe para tabela
        resultado = {'tabela': {'prazo': '-', 'frete': '-'}, 'tabela2': {'frete': 167.33, 'prazo': 3}}
        self.assertEqual(testa_calculos(('florianopolis', 'saopaulo', '60', '10')), resultado)

    def test_flo_for_65_15(self):
        resultado = {'tabela': {'prazo': 4, 'frete': 182.93}, 'tabela2': {'frete': 232.08, 'prazo': 4}}
        self.assertEqual(testa_calculos(('florianopolis', 'fortaleza', '65', '15')), resultado)

    def test_flo_bal_70_20(self):
        resultado = {'tabela': {'prazo': 4, 'frete': 219.58}, 'tabela2': {'frete': 290.59, 'prazo': 1}}
        self.assertEqual(testa_calculos(('florianopolis', 'balneario', '70', '20')), resultado)

    def test_flo_saj_75_25(self):
        resultado = {'tabela': {'prazo': 3, 'frete': 271.81}, 'tabela2': {'frete': 388.10, 'prazo': 12}}
        self.assertEqual(testa_calculos(('florianopolis', 'saojose', '75', '25')), resultado)

    def test_flo_pal_80_30(self):
        resultado = {'tabela': {'prazo': 1, 'frete': 163.41}, 'tabela2': {'frete': 447.29, 'prazo': 4}}
        self.assertEqual(testa_calculos(('florianopolis', 'palhoca', '80', '30')), resultado)

    def test_flo_val_85_35(self):
        resultado = {'tabela': {'prazo': 1, 'frete': 199.69}, 'tabela2': {'frete': 489.75, 'prazo': 1}}
        self.assertEqual(testa_calculos(('florianopolis', 'valparaiso', '85', '35')), resultado)

    def test_bra_flo_90_1(self):
        resultado = {'tabela': {'prazo': 3, 'frete': 22.13}, 'tabela2': {'frete': 12.56, 'prazo': 2}}
        self.assertEqual(testa_calculos(('brasilia', 'florianopolis', '90', '1')), resultado)

    def test_cur_flo_95_10(self):
        resultado = {'tabela': {'prazo': 4, 'frete': 93.46}, 'tabela2': {'frete': 104.75, 'prazo': 4}}
        self.assertEqual(testa_calculos(('curitiba', 'florianopolis', '95', '10')), resultado)

    def test_sao_flo_100_25(self):
        resultado = {'tabela': {'prazo': 1, 'frete': 251.07}, 'tabela2': {'frete': 233.43, 'prazo': 4}}
        self.assertEqual(testa_calculos(('saopaulo', 'florianopolis', '100', '25')), resultado)

    def test_for_flo_105_35(self):
        # peso excede limite maximo na tabela2
        resultado = {'tabela': {'prazo': 3, 'frete': 384.21}, 'tabela2': {'frete': '-', 'prazo': '-'}}
        self.assertEqual(testa_calculos(('fortaleza', 'florianopolis', '105', '35')), resultado)

    def test_bal_flo_110_3(self):
        resultado = {'tabela': {'prazo': 1, 'frete': 81.07}, 'tabela2': {'frete': 29.55, 'prazo': 1}}
        self.assertEqual(testa_calculos(('balneario', 'florianopolis', '110', '3')), resultado)

    def test_saj_flo_115_8(self):
        resultado = {'tabela': {'prazo': 4, 'frete': 121.60}, 'tabela2': {'frete': 48.11, 'prazo': 2}}
        self.assertEqual(testa_calculos(('saojose', 'florianopolis', '115', '8')), resultado)

    def test_pal_flo_120_9_25(self):
        resultado = {'tabela': {'prazo': 3, 'frete': 128.75}, 'tabela2': {'frete': 58.30, 'prazo': 3}}
        self.assertEqual(testa_calculos(('palhoca', 'florianopolis', '120', '9.25')), resultado)

    def test_val_flo_125_10_2(self):
        resultado = {'tabela': {'prazo': 3, 'frete': 89.63}, 'tabela2': {'frete': 60.91, 'prazo': 2}}
        self.assertEqual(testa_calculos(('valparaiso', 'florianopolis', '125', '10.2')), resultado)

    def test_bal_flo_80_0_27(self):
        resultado = {'tabela': {'prazo': 1, 'frete': 13.63}, 'tabela2': {'frete': 7.90, 'prazo': 1}}
        self.assertEqual(testa_calculos(('balneario', 'florianopolis', '80', '0.27')), resultado)

    def test_pal_flo_54_1_75(self):
        resultado = {'tabela': {'prazo': 3, 'frete': 47.16}, 'tabela2': {'frete': 32.31, 'prazo': 3}}
        self.assertEqual(testa_calculos(('palhoca', 'florianopolis', '54', '1.75')), resultado)

if __name__ == '__main__':
    unittest.main()
