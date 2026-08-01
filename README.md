# Laboratorio 2 - Problema 2

El programa lee expresiones regulares en formato infix desde un archivo de texto y
verifica el balance de paréntesis `()`, corchetes `[]` y llaves `{}` mediante una
pila. Para cada línea muestra las operaciones de apilar y desapilar, la posición de
los errores y el resultado final.

## Ejecución

Se necesita Python 3.10 o posterior. Desde la carpeta del proyecto ejecute:

```powershell
python balanceador.py expresiones.txt
```

El argumento es opcional; sin él, el programa busca `expresiones.txt` junto al
script:

```powershell
python balanceador.py
```

El archivo de entrada debe contener una expresión por línea. Los cinco ejemplos del
PDF están incluidos en `expresiones.txt`.


La solución también reconoce delimitadores escapados, por lo que `\(` y `\)` se
tratan como caracteres literales y no modifican la pila.
