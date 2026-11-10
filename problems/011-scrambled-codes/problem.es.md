# Agrupar códigos desordenados

Dos escáneres de un centro logístico leen la misma etiqueta de paquete, pero a veces reportan sus caracteres en otro orden (por ejemplo `"A7B"` y `"7BA"`). Dado un arreglo de códigos escaneados, agrupa los códigos que son reordenamientos entre sí. El orden de los grupos, y el de los códigos dentro de un grupo, no importa. Los códigos repetidos se conservan.

Implementa `List<List<String>> groupScrambled(String[] codes)` en la clase `Solution`.

```java
groupScrambled(new String[]{"A7B", "XY", "7BA", "YX", "Q9", "B7A"})
// [["A7B","7BA","B7A"], ["XY","YX"], ["Q9"]]
```

**Pista:** dos códigos son reordenamientos entre sí si sus caracteres ordenados son iguales. `Map.computeIfAbsent` es la forma idiomática de armar los grupos.
