# First Non-Repeating Character

Given a string, find the first character that appears only once in the entire string.

**Requirements**

- Explain the chosen data structure and complexity (out loud, as in an interview).
- Use standard Java collections.
- Achieve O(n) time complexity.
- Handle `null` and empty strings: return `Optional.empty()`. Also return `Optional.empty()` if every character repeats.

Implement `Optional<Character> firstUnique(String s)` in class `Solution`.

**Example**

```java
new Solution().firstUnique("swiss")  // Optional[w]
new Solution().firstUnique("aabb")   // Optional.empty
new Solution().firstUnique(null)     // Optional.empty
```
