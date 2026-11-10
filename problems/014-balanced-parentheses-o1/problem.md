# Balanced Parentheses in O(1) Space

Given a string containing only `(` and `)`, return `true` if every `)` closes a previous `(` and no `(` is left open. The order matters: `")("` is invalid even though the counts match.

Implement `boolean isBalanced(String s)` in class `Solution`. **No collections and no extra arrays**: use O(1) extra space.

```java
isBalanced("(())")  // true
isBalanced("(()")   // false
isBalanced(")(")    // false
isBalanced("")      // true
```
