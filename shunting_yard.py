"""Conversión de expresiones regulares infix a postfix con Shunting Yard."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CONCATENACION = "·"
OPERADORES_BINARIOS = {"|", CONCATENACION}
PRECEDENCIA = {"|": 1, CONCATENACION: 2}
SIMBOLOS_CONTROL = {"(", ")", "|", "*", "+", "?", CONCATENACION}


class ErrorExpresion(ValueError):
    """Indica que una expresión regular no se puede convertir."""


@dataclass(frozen=True)
class ResultadoConversion:
    original: str
    normalizada: str
    postfix: str
    pasos_tokenizacion: tuple[str, ...]
    pasos_extension: tuple[str, ...]
    pasos_shunting_yard: tuple[str, ...]


def _formatear(tokens: Iterable[str]) -> str:
    return " ".join(tokens) if tokens else "∅"


def tokenizar(expresion: str) -> tuple[list[str], list[str]]:
    """Separa la expresión y conserva cada carácter escapado como un operando."""
    tokens: list[str] = []
    pasos: list[str] = []
    indice = 0

    while indice < len(expresion):
        simbolo = expresion[indice]

        if simbolo.isspace():
            indice += 1
            continue

        if simbolo == "\\":
            if indice + 1 >= len(expresion):
                raise ErrorExpresion(
                    f"barra invertida sin carácter escapado en la posición {indice + 1}"
                )
            token = expresion[indice : indice + 2]
            tokens.append(token)
            pasos.append(
                f"Posición {indice + 1}: se reconoce '{token}' como un solo "
                "operando escapado."
            )
            indice += 2
            continue

        if simbolo == "[":
            inicio = indice
            indice += 1
            escapado = False
            while indice < len(expresion):
                actual = expresion[indice]
                if escapado:
                    escapado = False
                elif actual == "\\":
                    escapado = True
                elif actual == "]":
                    break
                indice += 1

            if indice >= len(expresion) or expresion[indice] != "]":
                raise ErrorExpresion(
                    f"clase de caracteres sin ']' desde la posición {inicio + 1}"
                )

            token = expresion[inicio : indice + 1]
            tokens.append(token)
            pasos.append(
                f"Posiciones {inicio + 1}-{indice + 1}: '{token}' es un solo operando."
            )
            indice += 1
            continue

        if simbolo == CONCATENACION:
            raise ErrorExpresion(
                f"el símbolo reservado '{CONCATENACION}' aparece en la posición "
                f"{indice + 1}"
            )

        tokens.append(simbolo)
        indice += 1

    if not tokens:
        raise ErrorExpresion("la expresión está vacía")

    return tokens, pasos


def _es_operando(token: str) -> bool:
    return token not in SIMBOLOS_CONTROL


def _inicio_ultimo_atomo(tokens: list[str]) -> int:
    if not tokens:
        raise ErrorExpresion("un cuantificador no tiene operando a su izquierda")

    indice = len(tokens) - 1
    while indice >= 0 and tokens[indice] == "*":
        indice -= 1

    if indice < 0:
        raise ErrorExpresion("un cuantificador no tiene operando a su izquierda")

    if tokens[indice] == ")":
        nivel = 1
        indice -= 1
        while indice >= 0:
            if tokens[indice] == ")":
                nivel += 1
            elif tokens[indice] == "(":
                nivel -= 1
                if nivel == 0:
                    return indice
            indice -= 1
        raise ErrorExpresion("paréntesis de cierre sin apertura")

    if _es_operando(tokens[indice]):
        return indice

    raise ErrorExpresion(
        "un cuantificador no tiene un operando válido a su izquierda"
    )


def expandir_extensiones(tokens: list[str]) -> tuple[list[str], list[str]]:
    """Convierte R+ a RR* y R? a (R|ε), incluso cuando R es un grupo."""
    resultado: list[str] = []
    pasos: list[str] = []

    for token in tokens:
        if token not in {"+", "?"}:
            resultado.append(token)
            continue

        inicio = _inicio_ultimo_atomo(resultado)
        atomo = resultado[inicio:]
        del resultado[inicio:]
        antes = _formatear(atomo)

        if token == "+":
            reemplazo = ["(", *atomo, ")", "(", *atomo, ")", "*"]
            regla = "R+ → RR*"
        else:
            reemplazo = ["(", *atomo, "|", "ε", ")"]
            regla = "R? → (R|ε)"

        resultado.extend(reemplazo)
        pasos.append(f"Se aplica {regla} a [{antes}]: {_formatear(resultado)}")

    if not pasos:
        pasos.append("La expresión no contiene extensiones '+' ni '?'.")

    return resultado, pasos


def _puede_terminar_atomo(token: str) -> bool:
    return _es_operando(token) or token in {")", "*"}


def _puede_iniciar_atomo(token: str) -> bool:
    return _es_operando(token) or token == "("


def insertar_concatenaciones(tokens: list[str]) -> list[str]:
    """Agrega el operador interno · donde la concatenación era implícita."""
    resultado: list[str] = []
    for token in tokens:
        if (
            resultado
            and _puede_terminar_atomo(resultado[-1])
            and _puede_iniciar_atomo(token)
        ):
            resultado.append(CONCATENACION)
        resultado.append(token)
    return resultado


def convertir_postfix(tokens: list[str]) -> tuple[list[str], list[str]]:
    """Ejecuta Shunting Yard sobre una expresión ya normalizada."""
    salida: list[str] = []
    pila: list[str] = []
    pasos: list[str] = []
    espera_operando = True

    def registrar(numero: int, token: str, accion: str) -> None:
        pasos.append(
            f"{numero:02}. Token '{token}': {accion} | "
            f"salida=[{_formatear(salida)}] | pila=[{_formatear(pila)}]"
        )

    for numero, token in enumerate(tokens, start=1):
        if _es_operando(token):
            if not espera_operando:
                raise ErrorExpresion(f"falta un operador antes de '{token}'")
            salida.append(token)
            espera_operando = False
            registrar(numero, token, "se envía a la salida")
            continue

        if token == "(":
            if not espera_operando:
                raise ErrorExpresion("falta concatenación antes de '('")
            pila.append(token)
            registrar(numero, token, "se apila")
            continue

        if token == ")":
            if espera_operando:
                raise ErrorExpresion(
                    "paréntesis vacío o cierre después de un operador"
                )
            while pila and pila[-1] != "(":
                salida.append(pila.pop())
            if not pila:
                raise ErrorExpresion("paréntesis ')' sin apertura")
            pila.pop()
            espera_operando = False
            registrar(numero, token, "se desapila hasta encontrar '('")
            continue

        if token == "*":
            if espera_operando:
                raise ErrorExpresion("el operador '*' no tiene operando")
            salida.append(token)
            registrar(numero, token, "operador postfix; se envía a la salida")
            continue

        if token in OPERADORES_BINARIOS:
            if espera_operando:
                raise ErrorExpresion(
                    f"el operador '{token}' no tiene operando izquierdo"
                )
            movidos: list[str] = []
            while (
                pila
                and pila[-1] in OPERADORES_BINARIOS
                and PRECEDENCIA[pila[-1]] >= PRECEDENCIA[token]
            ):
                movido = pila.pop()
                salida.append(movido)
                movidos.append(movido)
            pila.append(token)
            espera_operando = True
            accion = "se apila"
            if movidos:
                accion = f"se pasan {_formatear(movidos)} a salida y se apila"
            registrar(numero, token, accion)
            continue

        raise ErrorExpresion(f"token no reconocido: '{token}'")

    if espera_operando:
        raise ErrorExpresion("la expresión termina con un operador incompleto")

    while pila:
        operador = pila.pop()
        if operador == "(":
            raise ErrorExpresion("paréntesis '(' sin cierre")
        salida.append(operador)

    pasos.append(
        f"Fin: se vacía la pila | salida=[{_formatear(salida)}] | pila=[∅]"
    )
    return salida, pasos


def convertir_expresion(expresion: str) -> ResultadoConversion:
    tokens, pasos_tokenizacion = tokenizar(expresion)
    expandidos, pasos_extension = expandir_extensiones(tokens)
    normalizados = insertar_concatenaciones(expandidos)
    postfix, pasos_shunting_yard = convertir_postfix(normalizados)

    return ResultadoConversion(
        original=expresion,
        normalizada=_formatear(normalizados),
        postfix=_formatear(postfix),
        pasos_tokenizacion=tuple(pasos_tokenizacion),
        pasos_extension=tuple(pasos_extension),
        pasos_shunting_yard=tuple(pasos_shunting_yard),
    )


def procesar_lineas(lineas: Iterable[str]) -> tuple[str, bool]:
    bloques: list[str] = []
    hubo_error = False
    expresiones = 0

    for numero_linea, linea in enumerate(lineas, start=1):
        expresion = linea.rstrip("\r\n")
        if not expresion.strip():
            continue
        expresiones += 1

        encabezado = ["=" * 88, f"Línea {numero_linea}: {expresion}"]
        try:
            resultado = convertir_expresion(expresion)
        except ErrorExpresion as error:
            hubo_error = True
            bloques.append("\n".join([*encabezado, f"ERROR: {error}"]))
            continue

        tokenizacion = resultado.pasos_tokenizacion or (
            "No hay caracteres escapados ni clases que agrupar.",
        )
        bloque = [
            *encabezado,
            "\n1) Verificación de tokens:",
            *[f"   {paso}" for paso in tokenizacion],
            "\n2) Conversión de extensiones:",
            *[f"   {paso}" for paso in resultado.pasos_extension],
            f"\n3) Infix normalizada: {resultado.normalizada}",
            "   ('·' representa concatenación; '.' conserva el comodín del regex)",
            "\n4) Pasos de Shunting Yard:",
            *[f"   {paso}" for paso in resultado.pasos_shunting_yard],
            f"\nPOSTFIX: {resultado.postfix}",
        ]
        bloques.append("\n".join(bloque))

    if expresiones == 0:
        return "El archivo no contiene expresiones para procesar.", True
    return "\n".join(bloques), hubo_error


def imprimir_reporte(reporte: str, pausar: bool, lineas_por_pagina: int = 20) -> None:
    """Imprime el reporte completo o lo pagina para una demostración en pantalla."""
    if not pausar:
        print(reporte)
        return

    lineas = reporte.splitlines()
    for inicio in range(0, len(lineas), lineas_por_pagina):
        print("\n".join(lineas[inicio : inicio + lineas_por_pagina]))
        if inicio + lineas_por_pagina >= len(lineas):
            break

        try:
            respuesta = input(
                "\n--- Enter para continuar; escriba q y Enter para salir --- "
            )
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if respuesta.strip().lower() == "q":
            break


def main() -> int:
    # Una tubería de Windows puede seleccionar cp1252 aunque la terminal use UTF-8.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Convierte expresiones regulares infix a postfix con Shunting Yard."
    )
    parser.add_argument(
        "archivo",
        nargs="?",
        type=Path,
        default=Path(__file__).with_name("expresiones.txt"),
        help="archivo de entrada (por defecto: expresiones.txt)",
    )
    modos_pausa = parser.add_mutually_exclusive_group()
    modos_pausa.add_argument(
        "--pausar",
        action="store_true",
        help="pausa el reporte cada 20 líneas para facilitar la demostración",
    )
    modos_pausa.add_argument(
        "--paso-a-paso",
        action="store_true",
        help="pausa después de cada línea del reporte",
    )
    argumentos = parser.parse_args()

    try:
        lineas = argumentos.archivo.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        parser.error(f"no se encontró el archivo: {argumentos.archivo}")
    except OSError as error:
        parser.error(f"no se pudo leer el archivo: {error}")

    reporte, hubo_error = procesar_lineas(lineas)
    pausar = argumentos.pausar or argumentos.paso_a_paso
    lineas_por_pagina = 1 if argumentos.paso_a_paso else 20
    imprimir_reporte(reporte, pausar, lineas_por_pagina)
    return 1 if hubo_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
