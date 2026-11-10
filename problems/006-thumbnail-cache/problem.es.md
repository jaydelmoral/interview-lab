# Caché acotada con expulsión LRU

Una plataforma de video guarda en memoria las miniaturas vistas recientemente. Diseña una caché de capacidad fija: `get(key)` devuelve el valor guardado, o `-1` si no existe; `put(key, value)` inserta o actualiza. Cuando se excede la capacidad, expulsa la clave **menos recientemente usada**. Ambas operaciones deben ser O(1). Un `get` y un `put` sobre una clave existente cuentan como "uso".

Implementa la clase `LRUCache` con `LRUCache(int capacity)`, `int get(int key)` y `void put(int key, int value)`.

```java
LRUCache c = new LRUCache(2);
c.put(10, 100); c.put(20, 200);
c.put(10, 111);  // actualiza: la clave 20 pasa a ser la menos reciente
c.put(30, 300);  // expulsa la clave 20
c.get(20);       // -1
c.get(10);       // 111
```
