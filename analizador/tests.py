from django.test import SimpleTestCase
from django.urls import reverse

from . import servicios
from .servicios import ErrorValidacion


class ConversionValidaTests(SimpleTestCase):
    def test_decimal_255_a_todas_las_bases(self):
        r = servicios.convertir_numero("255", 10)
        self.assertEqual(r.decimal, "255")
        self.assertEqual(r.binario, "11111111")
        self.assertEqual(r.octal, "377")
        self.assertEqual(r.hexadecimal, "FF")
        self.assertEqual((r.bits_significativos, r.bytes_necesarios), (8, 1))

    def test_binario_se_ajusta_a_limite_de_byte(self):
        # 256 necesita 9 bits -> 2 bytes -> 16 bits
        r = servicios.convertir_numero("256", 10)
        self.assertEqual(r.binario, "00000001 00000000")
        self.assertEqual((r.bits_significativos, r.bytes_necesarios), (9, 2))
        # 5 necesita 3 bits -> 1 byte -> 8 bits
        self.assertEqual(servicios.convertir_numero("5", 10).binario, "00000101")

    def test_hexadecimal_minusculas_y_valor_maximo(self):
        r = servicios.convertir_numero("ffff", 16)
        self.assertEqual(r.decimal, "65535")
        self.assertEqual(r.binario, "11111111 11111111")
        self.assertEqual(r.octal, "177777")
        self.assertEqual((r.bits_significativos, r.bytes_necesarios), (16, 2))

    def test_cero_usa_un_bit_y_un_byte(self):
        r = servicios.convertir_numero("0", 2)
        self.assertEqual(r.binario, "00000000")
        self.assertEqual((r.bits_significativos, r.bytes_necesarios), (1, 1))

    def test_octal_y_binario_de_origen(self):
        self.assertEqual(servicios.convertir_numero("377", 8).decimal, "255")
        self.assertEqual(servicios.convertir_numero("1010", 2).hexadecimal, "A")


class ValidacionTests(SimpleTestCase):
    def test_digito_invalido_para_la_base(self):
        with self.assertRaisesMessage(ErrorValidacion, "Dígito(s) inválido(s) para la base 2"):
            servicios.convertir_numero("1012", 2)
        with self.assertRaisesMessage(ErrorValidacion, "base 8"):
            servicios.convertir_numero("89", 8)
        with self.assertRaisesMessage(ErrorValidacion, "base 10"):
            servicios.convertir_numero("12A", 10)

    def test_entrada_vacia(self):
        with self.assertRaisesMessage(ErrorValidacion, "vacío"):
            servicios.convertir_numero("   ", 10)

    def test_valor_negativo(self):
        with self.assertRaisesMessage(ErrorValidacion, "negativos"):
            servicios.convertir_numero("-5", 10)

    def test_valor_fuera_de_rango(self):
        with self.assertRaisesMessage(ErrorValidacion, "fuera de rango"):
            servicios.convertir_numero("65536", 10)
        with self.assertRaisesMessage(ErrorValidacion, "fuera de rango"):
            servicios.convertir_numero("10000", 16)


class TextoUtf8Tests(SimpleTestCase):
    def test_caracter_enie_en_utf8(self):
        filas = servicios.analizar_texto("ñ")
        self.assertEqual(len(filas), 1)
        f = filas[0]
        self.assertEqual(f.caracter, "ñ")
        self.assertEqual(f.decimal, 241)
        self.assertEqual(f.punto_codigo, "U+00F1")
        self.assertEqual(f.hexadecimal, "0xF1")
        self.assertEqual(f.bytes_utf8, "C3 B1")

    def test_ascii_usa_un_byte(self):
        f = servicios.analizar_texto("A")[0]
        self.assertEqual((f.decimal, f.punto_codigo, f.bytes_utf8), (65, "U+0041", "41"))

    def test_texto_vacio_y_demasiado_largo(self):
        with self.assertRaisesMessage(ErrorValidacion, "vacío"):
            servicios.analizar_texto("")
        with self.assertRaisesMessage(ErrorValidacion, "máximo permitido es 20"):
            servicios.analizar_texto("a" * 21)
        self.assertEqual(len(servicios.analizar_texto("a" * 20)), 20)


class VistasTests(SimpleTestCase):
    def test_pagina_principal(self):
        r = self.client.get(reverse("analizador:index"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Analizador de representación de datos")

    def test_post_numero_valido_muestra_resultados(self):
        r = self.client.post(reverse("analizador:numero"), {"numero": "255", "base": "10"})
        self.assertContains(r, "11111111")
        self.assertContains(r, "377")

    def test_post_numero_invalido_muestra_error(self):
        r = self.client.post(reverse("analizador:numero"), {"numero": "1012", "base": "2"})
        self.assertContains(r, "inválido")

    def test_post_texto_con_enie(self):
        r = self.client.post(reverse("analizador:texto"), {"texto": "año"})
        self.assertContains(r, "U+00F1")
        self.assertContains(r, "C3 B1")
