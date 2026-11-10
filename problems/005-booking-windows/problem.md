# Merge Booking Windows

A hotel stores room blockings as windows `[start, end]` (hours of the day). To show availability, overlapping windows must be merged into one. Windows that only touch at an endpoint (`[8,10]` and `[10,12]`) are also merged. Return the merged windows sorted by start; the input may come in any order.

Implement `int[][] mergeWindows(int[][] windows)` in class `Solution`. Target complexity: O(n log n).

```java
mergeWindows(new int[][]{{9,12},{11,14},{16,18},{20,22}})  // {{9,14},{16,18},{20,22}}
mergeWindows(new int[][]{{8,10},{10,12}})                  // {{8,12}}
```

**Java 21 note:** `List.getLast()` (SequencedCollection) makes the "last merged window" access cleaner than `get(size() - 1)`.
