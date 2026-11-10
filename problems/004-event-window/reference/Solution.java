import java.util.*;

class Solution {

    public int longestDistinctWindow(String s) {
        Map<Character, Integer> lastIndex = new HashMap<>();
        int max = 0, left = 0;
        for (int right = 0; right < s.length(); right++) {
            char c = s.charAt(right);
            Integer prev = lastIndex.get(c);
            if (prev != null && prev >= left) left = prev + 1;
            lastIndex.put(c, right);
            max = Math.max(max, right - left + 1);
        }
        return max;
    }
}
