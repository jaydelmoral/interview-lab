# Mediana de latencia en tiempo real

Un monitor de red de telecomunicaciones recibe tiempos de respuesta (en milisegundos) uno por uno y debe reportar, en cualquier momento, la mediana de todo lo recibido hasta ahora. Con una cantidad par, la mediana es el promedio de los dos valores centrales.

Implementa la clase `LatencyTracker` con `void record(int ms)` (objetivo O(log n)) y `double median()` (objetivo O(1)).

```java
LatencyTracker t = new LatencyTracker();
t.record(40); t.record(60);
t.median();   // 50.0
t.record(100);
t.median();   // 60.0
```
