# Laboratorio 2 - Problema 3: algoritmo de Shunting Yard

Esta rama resuelve el Problema 3 del Laboratorio 2. El programa lee expresiones
regulares en formato infix desde `expresiones.txt`, las convierte a formato postfix
mediante el algoritmo de Shunting Yard y muestra todos los pasos realizados.

## ¿Qué es el algoritmo de Shunting Yard?

Shunting Yard fue diseñado por Edsger W. Dijkstra para convertir expresiones en
notación infix a postfix o para construir un árbol sintáctico. Su nombre se inspira
en la organización de vagones en una estación ferroviaria: los operandos avanzan
directamente hacia la salida, mientras que los operadores esperan temporalmente en
una pila.

El algoritmo recorre la expresión una sola vez de izquierda a derecha:

1. Si encuentra un operando, lo envía directamente a la salida.
2. Si encuentra `(`, lo coloca en la pila.
3. Si encuentra `)`, mueve operadores de la pila hacia la salida hasta hallar `(`.
4. Si encuentra un operador, primero extrae los operadores de mayor o igual
   precedencia y después lo apila.
5. Al terminar la entrada, mueve los operadores restantes de la pila a la salida.

Para una expresión normalizada de longitud `n`, el recorrido tiene complejidad
temporal `O(n)` y utiliza `O(n)` espacio en el peor caso.

## Adaptación para expresiones regulares

La versión implementada utiliza esta precedencia, de mayor a menor:

| Prioridad | Operador | Significado |
|---:|:---:|---|
| 1 | `*` | Cerradura de Kleene, operador postfix |
| 2 | `·` | Concatenación |
| 3 | `\|` | Unión |

La concatenación suele estar implícita. Por ejemplo, `ab` significa que `a` debe
estar seguido de `b`. El programa inserta internamente `·`, convirtiendo `ab` en
`a·b` antes de ejecutar Shunting Yard.

El punto `.` escrito originalmente en una expresión se conserva como comodín de
regex. El símbolo `·` se utiliza exclusivamente para distinguir la concatenación
agregada por el programa.

### Extensiones `+` y `?`

Shunting Yard trabaja después de eliminar estas extensiones:

- `R+` se convierte en `RR*`: una o más apariciones de `R`.
- `R?` se convierte en `(R|ε)`: cero o una aparición de `R`.

La conversión funciona tanto con símbolos individuales como con grupos y clases de
caracteres. Por ejemplo:

```text
[ae]+  →  [ae][ae]*
(ab)?  →  ((ab)|ε)
```

### Caracteres escapados y clases

El tokenizador verifica la barra invertida `\` y une el carácter siguiente en un
solo token. Por eso `\(` representa un paréntesis literal y no altera la pila de
operadores. Una barra invertida sin carácter posterior se reporta como error.

Las clases como `[ae]`, `[jl]` y `[ae03]` también se procesan como operandos
individuales, sin separar sus caracteres internos.

## Ejemplo breve

Para la expresión `(a | t)c`, primero se agrega la concatenación:

```text
(a|t)·c
```

Algunos pasos principales son:

| Token | Acción | Salida | Pila |
|:---:|---|---|---|
| `(` | Apilar | vacía | `(` |
| `a` | Enviar a salida | `a` | `(` |
| `\|` | Apilar | `a` | `( \|` |
| `t` | Enviar a salida | `a t` | `( \|` |
| `)` | Desapilar hasta `(` | `a t \|` | vacía |
| `·` | Apilar | `a t \|` | `·` |
| `c` | Enviar a salida | `a t \| c` | `·` |
| Fin | Vaciar pila | `a t \| c ·` | vacía |

Resultado:

```text
POSTFIX: a t | c ·
```

## Archivos

- `shunting_yard.py`: implementación, validaciones y generación del reporte.
- `expresiones.txt`: las ocho expresiones del Problema 1, una por línea.

Los resultados no están codificados de forma fija: el programa abre el archivo
indicado en la línea de comandos y procesa dinámicamente cada línea no vacía.

## Link al video

https://youtu.be/G0R_zyYNLys

