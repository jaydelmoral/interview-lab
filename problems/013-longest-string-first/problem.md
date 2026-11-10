# First Longest String in an Array

Given an array of strings, return the **first** one with the maximum length. If several share the maximum length, return the first that appears. Return `""` for a `null` or empty array. Do not modify the input array.

Implement `String longestFirst(String[] arr)` in class `Solution`. Target: O(n).

```java
longestFirst(new String[]{"cat", "elephant", "dog", "hippo", "bee"})  // "elephant"
longestFirst(new String[]{"aaa", "bbb", "c"})                          // "aaa"
```

**Java note:** `Stream.max(comparator)` and `Collectors.maxBy` also return the *first* element on a tie (verified on Java 21).
