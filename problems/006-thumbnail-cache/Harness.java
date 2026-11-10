import java.util.*;

public class Harness {
    public static void main(String[] a) {
        Runner.run(a[0], Harness::t);
    }

    static void t(String id) throws Throwable {
        
        switch (id) {
            case "example": {
                LRUCache c = new LRUCache(2);
                c.put(10, 100); c.put(20, 200);
                c.put(10, 111);
                c.put(30, 300);
                Check.eq(-1, c.get(20), Check.t("get(20) tras evictar", "get(20) after eviction"));
                Check.eq(111, c.get(10), "get(10)");
                Check.eq(300, c.get(30), "get(30)");
                c.put(40, 400);
                Check.eq(-1, c.get(10), Check.t("get(10) tras evictar", "get(10) after eviction"));
                Check.eq(400, c.get(40), "get(40)");
                return;
            }
            case "update": {
                LRUCache c = new LRUCache(2);
                c.put(1, 1); c.put(2, 2);
                c.put(1, 10);
                c.put(3, 3);
                Check.eq(-1, c.get(2), Check.t("la clave 2 era la menos usada", "key 2 was the least recently used"));
                Check.eq(10, c.get(1), Check.t("put sobre clave existente actualiza el valor", "put on an existing key updates the value"));
                return;
            }
            case "capacity1": {
                LRUCache c = new LRUCache(1);
                c.put(1, 1); c.put(2, 2);
                Check.eq(-1, c.get(1), "capacidad 1");
                Check.eq(2, c.get(2), "capacidad 1");
                return;
            }
            case "large": {
                LRUCache c = new LRUCache(50_000);
                Random rnd = new Random(7);
                for (int i = 0; i < 300_000; i++) {
                    c.put(i, i);
                    int k = i - rnd.nextInt(1000);
                    if (k >= 0) c.get(k);
                }
                Check.eq(299_999, c.get(299_999), Check.t("ultimo insertado", "last inserted"));
                Check.eq(-1, c.get(0), Check.t("el primero ya fue evictado", "the first one was already evicted"));
                return;
            }
            default: throw new AssertionError(Check.t("prueba desconocida", "unknown test"));
        }
    }

}
