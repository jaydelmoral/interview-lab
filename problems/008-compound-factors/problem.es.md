# Factores compuestos sin el propio

Un banco calcula, para cada producto de un portafolio, el factor de riesgo combinado de **todos los demás** productos. Dado el arreglo `factors` (largo >= 2), devuelve un arreglo `result` donde `result[i]` es el producto de todos los elementos de `factors` excepto `factors[i]`. **No uses división.** Objetivo: tiempo O(n). Cualquier producto de un prefijo o de un sufijo cabe en un `int`.

Implementa `int[] factorsExcludingSelf(int[] factors)` en la clase `Solution`.

```java
factorsExcludingSelf(new int[]{2, 3, 4, 5})  // {60, 40, 30, 24}
```
