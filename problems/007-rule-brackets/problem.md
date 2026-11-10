# Balanced Rule Expressions

A payments engine lets analysts write rules such as `{amount > 100 && [country == "MX"]}`. Before saving a rule, the engine checks its brackets. For this exercise the expression has been reduced to its brackets: the input contains only `( ) [ ] { }`, and it is valid when every opening bracket is closed by the same type, in the correct order.

Implement `boolean hasBalancedBrackets(String s)` in class `Solution`. Target complexity: O(n).

```java
hasBalancedBrackets("{[()]}")  // true
hasBalancedBrackets("(()")     // false
hasBalancedBrackets("{(})")    // false
hasBalancedBrackets("")        // true
```

**Java note:** prefer `Deque` (`ArrayDeque`) over the legacy synchronized `Stack` class.
