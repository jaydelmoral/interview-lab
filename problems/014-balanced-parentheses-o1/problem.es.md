# Paréntesis balanceados en espacio O(1)

Dada una cadena que contiene solo `(` y `)`, devuelve `true` si cada `)` cierra un `(` anterior y no queda ningún `(` abierto. El orden importa: `")("` es inválida aunque las cantidades coincidan.

Implementa `boolean isBalanced(String s)` en la clase `Solution`. **Sin colecciones ni arreglos extra**: usa espacio extra O(1).

```java
isBalanced("(())")  // true
isBalanced("(()")   // false
isBalanced(")(")    // false
isBalanced("")      // true
```
