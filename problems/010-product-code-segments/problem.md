# Product Code Segmentation

A warehouse scanner merges several product codes into one continuous string without separators. Given the string `code` and the list `catalog` of valid product codes, return `true` if `code` can be split into a sequence of one or more catalog codes (a catalog code can be used any number of times). An empty `code` counts as valid.

Implement `boolean canSegment(String code, List<String> catalog)` in class `Solution`. Target: O(n²).

```java
canSegment("redbluered", List.of("red", "blue"))           // true
canSegment("redgreenblue", List.of("red", "blue", "gre"))  // false
```
