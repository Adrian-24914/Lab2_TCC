# Laboratorio 2 - Problema 3

Esta rama implementa el algoritmo **Shunting Yard** para convertir expresiones
regulares en formato infix a postfix. El programa lee una expresión por línea,
verifica caracteres escapados, convierte las extensiones `+` y `?`, agrega la
concatenación implícita y muestra cada cambio de la salida y de la pila.

## Cómo funciona Shunting Yard

Shunting Yard recorre la expresión de izquierda a derecha. Los operandos pasan
directamente a la salida; los operadores se guardan temporalmente en una pila. Antes
de apilar un operador, se extraen los que tengan mayor o igual precedencia. Un
paréntesis de apertura se apila y uno de cierre vacía la pila hasta encontrar su
apertura. Al terminar la entrada, los operadores restantes pasan a la salida.

Para expresiones regulares se utiliza esta precedencia:

1. Cerradura de Kleene `*` (operador postfix).
2. Concatenación `·`.
3. Unión `|`.

La concatenación, que normalmente está implícita, se representa internamente con
`·`. El punto `.` escrito en las expresiones originales se conserva como el comodín
de una expresión regular, por lo que ambos símbolos no se confunden.

Antes de aplicar Shunting Yard se eliminan las extensiones mediante equivalencias:

- `R+` se convierte en `RR*`.
- `R?` se convierte en `(R|ε)`.

El verificador agrupa clases como `[ae03]` en un solo operando y también agrupa cada
carácter escapado con su barra invertida. Por ejemplo, `\(` representa un paréntesis
literal y no modifica la pila de operadores. Una barra invertida al final se reporta
como error.

## Ejecución

Se necesita Python 3.10 o posterior. Ejecute desde la carpeta del repositorio:

```powershell
python shunting_yard.py expresiones.txt
```

El argumento es opcional; sin él se usa automáticamente el archivo incluido:

```powershell
python shunting_yard.py
```

Para una demostración en video, puede paginar el reporte sin usar tuberías:

```powershell
python shunting_yard.py expresiones.txt --pausar
```

Presione `Enter` para mostrar las siguientes 20 líneas o escriba `q` y presione
`Enter` para terminar la visualización.

La salida presenta, para cada línea:

1. La verificación de tokens y caracteres escapados.
2. La conversión de `+` y `?`.
3. La expresión infix normalizada.
4. Cada paso del algoritmo con la salida y la pila.
5. La expresión final en formato postfix.

`expresiones.txt` contiene las ocho expresiones solicitadas en el PDF.
