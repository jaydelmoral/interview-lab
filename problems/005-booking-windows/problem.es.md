# Fusionar ventanas de reserva

Un hotel guarda los bloqueos de habitación como ventanas `[inicio, fin]` (horas del día). Para mostrar disponibilidad, las ventanas que se traslapan deben fusionarse en una. Las que solo se tocan en un extremo (`[8,10]` y `[10,12]`) también se fusionan. Devuelve las ventanas fusionadas ordenadas por inicio; la entrada puede venir en cualquier orden.

Implementa `int[][] mergeWindows(int[][] windows)` en la clase `Solution`. Complejidad objetivo: O(n log n).

```java
mergeWindows(new int[][]{{9,12},{11,14},{16,18},{20,22}})  // {{9,14},{16,18},{20,22}}
mergeWindows(new int[][]{{8,10},{10,12}})                  // {{8,12}}
```

**Nota de Java 21:** `List.getLast()` (SequencedCollection) deja el acceso a la "última ventana fusionada" más limpio que `get(size() - 1)`.
