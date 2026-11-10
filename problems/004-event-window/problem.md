# Longest Distinct Event Window

A telemetry service receives a stream of events, where each character is an event code. For a dashboard, it needs the length of the longest block of **consecutive** events in which no code repeats.

Implement `int longestDistinctWindow(String events)` in class `Solution`. Target complexity: O(n).

```java
longestDistinctWindow("ABCADEB")  // 5  ("CADEB")
longestDistinctWindow("zzzz")     // 1
longestDistinctWindow("")         // 0
```
