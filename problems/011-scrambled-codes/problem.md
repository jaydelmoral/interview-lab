# Group Scrambled Codes

Two scanners at a logistics hub read the same parcel label but sometimes report its characters in a different order (for example `"A7B"` and `"7BA"`). Given an array of scanned codes, group together the codes that are rearrangements of each other. The order of groups, and of codes inside a group, does not matter. Repeated codes are kept.

Implement `List<List<String>> groupScrambled(String[] codes)` in class `Solution`.

```java
groupScrambled(new String[]{"A7B", "XY", "7BA", "YX", "Q9", "B7A"})
// [["A7B","7BA","B7A"], ["XY","YX"], ["Q9"]]
```

**Hint:** two codes are rearrangements of each other if their sorted characters are equal. `Map.computeIfAbsent` is the idiomatic way to build the groups.
