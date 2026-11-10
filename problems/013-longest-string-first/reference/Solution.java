import java.util.*;

class Solution {

    public String longestFirst(String[] arr) {
        if (arr == null || arr.length == 0) return "";
        String result = arr[0];
        for (int i = 1; i < arr.length; i++) {
            if (arr[i].length() > result.length()) result = arr[i];
        }
        return result;
    }
}
