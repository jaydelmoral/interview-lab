# Expresiones de reglas balanceadas

Un motor de pagos permite que los analistas escriban reglas como `{amount > 100 && [country == "MX"]}`. Antes de guardar una regla, el motor revisa sus corchetes. En este ejercicio la expresión se redujo a sus corchetes: la entrada contiene solo `( ) [ ] { }` y es válida cuando cada apertura se cierra con el mismo tipo y en el orden correcto.

Implementa `boolean hasBalancedBrackets(String s)` en la clase `Solution`. Complejidad objetivo: O(n).

```java
hasBalancedBrackets("{[()]}")  // true
hasBalancedBrackets("(()")     // false
hasBalancedBrackets("{(})")    // false
hasBalancedBrackets("")        // true
```

**Nota de Java:** prefiere `Deque` (`ArrayDeque`) sobre la clase legada y sincronizada `Stack`.
