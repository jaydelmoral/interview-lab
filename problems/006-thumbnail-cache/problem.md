# Bounded Cache with LRU Eviction

A video platform keeps recently watched thumbnails in memory. Design a cache with a fixed capacity: `get(key)` returns the stored value, or `-1` if absent; `put(key, value)` inserts or updates. When the capacity is exceeded, evict the **least recently used** key. Both operations must run in O(1). A `get` and a `put` on an existing key both count as a "use".

Implement class `LRUCache` with `LRUCache(int capacity)`, `int get(int key)` and `void put(int key, int value)`.

```java
LRUCache c = new LRUCache(2);
c.put(10, 100); c.put(20, 200);
c.put(10, 111);  // update: key 20 is now the least recently used
c.put(30, 300);  // evicts key 20
c.get(20);       // -1
c.get(10);       // 111
```
