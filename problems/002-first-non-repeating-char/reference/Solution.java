import java.util.*;

class Solution {

    public Optional<Character> firstUnique(String s) {
        if (s == null || s.isEmpty()) return Optional.empty();
        Map<Character, Integer> counts = new LinkedHashMap<>();
        for (char c : s.toCharArray()) counts.merge(c, 1, Integer::sum);
        return counts.entrySet().stream().filter(e -> e.getValue() == 1).map(Map.Entry::getKey).findFirst();
    }
}
