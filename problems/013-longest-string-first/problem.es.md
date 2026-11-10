# Primera cadena más larga de un arreglo

Dado un arreglo de cadenas, devuelve la **primera** con la longitud máxima. Si varias comparten la longitud máxima, devuelve la que aparece primero. Devuelve `""` para un arreglo `null` o vacío. No modifiques el arreglo recibido.

Implementa `String longestFirst(String[] arr)` en la clase `Solution`. Objetivo: O(n).

```java
longestFirst(new String[]{"cat", "elephant", "dog", "hippo", "bee"})  // "elephant"
longestFirst(new String[]{"aaa", "bbb", "c"})                          // "aaa"
```

**Nota de Java:** `Stream.max(comparator)` y `Collectors.maxBy` también devuelven el *primer* elemento en un empate (verificado en Java 21).
