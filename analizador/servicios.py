"""Lógica pura (sin Django) de conversión numérica y análisis de caracteres."""
from __future__ import annotations

from dataclasses import dataclass

BASES = (2, 8, 10, 16)
NOMBRES_BASE = {2: "binaria", 8: "octal", 10: "decimal", 16: "hexadecimal"}
DIGITOS_VALIDOS = {
    2: "01",
    8: "01234567",
    10: "0123456789",
    16: "0123456789ABCDEF",
}
VALOR_MINIMO = 0
VALOR_MAXIMO = 65535
MAX_CARACTERES = 20


class ErrorValidacion(ValueError):
    """Error de entrada del usuario con un mensaje claro en español."""


@dataclass(frozen=True)
class ResultadoNumero:
    base_origen: int
    valor: int
    decimal: str
    binario: str          # ajustado a múltiplo de 8 bits, agrupado por byte
    octal: str
    hexadecimal: str
    bits_significativos: int
    bytes_necesarios: int


@dataclass(frozen=True)
class FilaCaracter:
    caracter: str
    decimal: int
    punto_codigo: str     # U+00F1
    hexadecimal: str      # 0xF1
    bytes_utf8: str       # C3 B1
    cantidad_bytes: int


def parsear_numero(texto: str, base: int) -> int:
    """Convierte `texto` desde `base` a entero validando dígitos y rango."""
    if base not in BASES:
        raise ErrorValidacion("La base seleccionada no es válida. Elija 2, 8, 10 o 16.")

    limpio = (texto or "").strip()
    if not limpio:
        raise ErrorValidacion("Ingrese un número: el campo está vacío.")

    if limpio.startswith("-"):
        raise ErrorValidacion(
            "No se permiten valores negativos: el rango válido es de 0 a 65 535."
        )

    limpio = limpio.upper()
    permitidos = DIGITOS_VALIDOS[base]
    invalidos = []
    for c in limpio:
        if c not in permitidos and c not in invalidos:
            invalidos.append(c)
    if invalidos:
        lista = ", ".join(f"'{c}'" for c in invalidos)
        raise ErrorValidacion(
            f"Dígito(s) inválido(s) para la base {base} ({NOMBRES_BASE[base]}): {lista}. "
            f"Dígitos permitidos: {', '.join(permitidos)}."
        )

    valor = int(limpio, base)
    if valor > VALOR_MAXIMO:
        raise ErrorValidacion(
            f"Valor fuera de rango: {valor} en decimal. "
            f"El valor debe estar entre {VALOR_MINIMO} y 65 535 (16 bits)."
        )
    return valor


def bits_significativos(valor: int) -> int:
    """Bits necesarios para representar el valor (el 0 usa 1 bit)."""
    return max(1, valor.bit_length())


def bytes_necesarios(valor: int) -> int:
    bits = bits_significativos(valor)
    return (bits + 7) // 8


def binario_ajustado(valor: int) -> str:
    """Binario completado con ceros a la izquierda hasta el siguiente límite de byte."""
    ancho = bytes_necesarios(valor) * 8
    crudo = format(valor, "b").zfill(ancho)
    return " ".join(crudo[i:i + 8] for i in range(0, ancho, 8))


def convertir_numero(texto: str, base: int) -> ResultadoNumero:
    valor = parsear_numero(texto, base)
    return ResultadoNumero(
        base_origen=base,
        valor=valor,
        decimal=str(valor),
        binario=binario_ajustado(valor),
        octal=format(valor, "o"),
        hexadecimal=format(valor, "X"),
        bits_significativos=bits_significativos(valor),
        bytes_necesarios=bytes_necesarios(valor),
    )


def analizar_texto(texto: str) -> list[FilaCaracter]:
    """Analiza cada carácter (punto de código) de un texto de hasta 20 caracteres."""
    if texto is None or texto == "":
        raise ErrorValidacion("Ingrese un texto: el campo está vacío.")
    if len(texto) > MAX_CARACTERES:
        raise ErrorValidacion(
            f"El texto tiene {len(texto)} caracteres; el máximo permitido es {MAX_CARACTERES}."
        )

    filas = []
    for c in texto:
        codigo = ord(c)
        codificado = c.encode("utf-8")
        filas.append(
            FilaCaracter(
                caracter=c,
                decimal=codigo,
                punto_codigo=f"U+{codigo:04X}",
                hexadecimal=f"0x{codigo:X}",
                bytes_utf8=" ".join(f"{b:02X}" for b in codificado),
                cantidad_bytes=len(codificado),
            )
        )
    return filas
