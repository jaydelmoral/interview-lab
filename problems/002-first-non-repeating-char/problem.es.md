# Primer carácter que no se repite

Dada una cadena, encuentra el primer carácter que aparece una sola vez en toda la cadena.

**Requisitos**

- Explica la estructura de datos elegida y la complejidad (en voz alta, como en una entrevista).
- Usa colecciones estándar de Java.
- Logra complejidad de tiempo O(n).
- Maneja `null` y cadenas vacías: devuelve `Optional.empty()`. También devuelve `Optional.empty()` si todos los caracteres se repiten.

Implementa `Optional<Character> firstUnique(String s)` en la clase `Solution`.

**Ejemplo**

```java
new Solution().firstUnique("swiss")  // Optional[w]
new Solution().firstUnique("aabb")   // Optional.empty
new Solution().firstUnique(null)     // Optional.empty
```
