class Solution {

    public boolean isBalanced(String s) {
        int open = 0;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '(') open++;
            else if (c == ')') open--;
            if (open < 0) return false;
        }
        return open == 0;
    }
}
