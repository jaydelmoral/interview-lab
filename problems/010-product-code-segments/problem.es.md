# Segmentación de códigos de producto

Un escáner de almacén junta varios códigos de producto en una sola cadena continua, sin separadores. Dada la cadena `code` y la lista `catalog` de códigos válidos, devuelve `true` si `code` se puede dividir en una secuencia de uno o más códigos del catálogo (un código del catálogo puede usarse cualquier número de veces). Un `code` vacío se considera válido.

Implementa `boolean canSegment(String code, List<String> catalog)` en la clase `Solution`. Objetivo: O(n²).

```java
canSegment("redbluered", List.of("red", "blue"))           // true
canSegment("redgreenblue", List.of("red", "blue", "gre"))  // false
```
