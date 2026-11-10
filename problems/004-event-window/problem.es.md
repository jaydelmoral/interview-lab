# Ventana de eventos distintos más larga

Un servicio de telemetría recibe un flujo de eventos, donde cada carácter es un código de evento. Para un tablero necesita la longitud del bloque más largo de eventos **consecutivos** en el que ningún código se repite.

Implementa `int longestDistinctWindow(String events)` en la clase `Solution`. Complejidad objetivo: O(n).

```java
longestDistinctWindow("ABCADEB")  // 5  ("CADEB")
longestDistinctWindow("zzzz")     // 1
longestDistinctWindow("")         // 0
```
