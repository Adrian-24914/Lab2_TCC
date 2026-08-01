"""Verifica el balance de delimitadores en expresiones regulares infix."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PAREJAS = {"(": ")", "[": "]", "{": "}"}
CIERRES = {cierre: apertura for apertura, cierre in PAREJAS.items()}


@dataclass(frozen=True)
class ResultadoBalance:
    balanceada: bool
    pasos: tuple[str, ...]


def _mostrar_pila(pila: list[tuple[str, int]]) -> str:
    return "[" + ", ".join(simbolo for simbolo, _ in pila) + "]"


def balancear_expresion(expresion: str) -> ResultadoBalance:
    """Valida delimitadores y devuelve todos los pasos realizados con la pila."""
    pila: list[tuple[str, int]] = []
    pasos: list[str] = ["Pila inicial: []"]
    escapado = False

    for posicion, simbolo in enumerate(expresion, start=1):
        if escapado:
            pasos.append(
                f"Posición {posicion}: '{simbolo}' está escapado; pila {_mostrar_pila(pila)}"
            )
            escapado = False
            continue

        if simbolo == "\\":
            escapado = True
            pasos.append(
                f"Posición {posicion}: inicia escape; pila {_mostrar_pila(pila)}"
            )
            continue

        if simbolo in PAREJAS:
            pila.append((simbolo, posicion))
            pasos.append(
                f"Posición {posicion}: apilar '{simbolo}' -> {_mostrar_pila(pila)}"
            )
            continue

        if simbolo not in CIERRES:
            continue

        if not pila:
            pasos.append(
                f"Posición {posicion}: ERROR, cierre '{simbolo}' sin apertura; pila []"
            )
            return ResultadoBalance(False, tuple(pasos))

        apertura, posicion_apertura = pila[-1]
        apertura_esperada = CIERRES[simbolo]
        if apertura != apertura_esperada:
            esperado = PAREJAS[apertura]
            pasos.append(
                f"Posición {posicion}: ERROR, llegó '{simbolo}' pero se esperaba "
                f"'{esperado}' para la apertura de la posición {posicion_apertura}; "
                f"pila {_mostrar_pila(pila)}"
            )
            return ResultadoBalance(False, tuple(pasos))

        pila.pop()
        pasos.append(
            f"Posición {posicion}: desapilar '{apertura}' con '{simbolo}' -> "
            f"{_mostrar_pila(pila)}"
        )

    if pila:
        pendientes = ", ".join(
            f"'{simbolo}' (posición {posicion})" for simbolo, posicion in reversed(pila)
        )
        pasos.append(
            f"Fin: ERROR, faltan cierres para {pendientes}; pila {_mostrar_pila(pila)}"
        )
        return ResultadoBalance(False, tuple(pasos))

    pasos.append("Fin: pila vacía []")
    return ResultadoBalance(True, tuple(pasos))


def procesar_lineas(lineas: Iterable[str]) -> str:
    """Procesa líneas no vacías y genera el reporte legible de la ejecución."""
    bloques: list[str] = []
    numero_expresion = 0

    for numero_linea, linea in enumerate(lineas, start=1):
        expresion = linea.rstrip("\r\n")
        if not expresion.strip():
            continue

        numero_expresion += 1
        resultado = balancear_expresion(expresion)
        estado = "BALANCEADA" if resultado.balanceada else "NO BALANCEADA"
        bloque = [
            "=" * 72,
            f"Línea {numero_linea}: {expresion}",
            *[f"  {paso}" for paso in resultado.pasos],
            f"Resultado: {estado}",
        ]
        bloques.append("\n".join(bloque))

    if numero_expresion == 0:
        return "El archivo no contiene expresiones para procesar."

    return "\n".join(bloques)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Comprueba el balance de (), [] y {} en expresiones infix."
    )
    parser.add_argument(
        "archivo",
        nargs="?",
        type=Path,
        default=Path(__file__).with_name("expresiones.txt"),
        help="archivo de entrada (por defecto: expresiones.txt)",
    )
    argumentos = parser.parse_args()

    try:
        lineas = argumentos.archivo.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        parser.error(f"no se encontró el archivo: {argumentos.archivo}")
    except OSError as error:
        parser.error(f"no se pudo leer el archivo: {error}")

    print(procesar_lineas(lineas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
