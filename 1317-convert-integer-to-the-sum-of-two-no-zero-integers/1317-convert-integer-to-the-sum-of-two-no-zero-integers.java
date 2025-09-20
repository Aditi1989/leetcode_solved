class Solution {
    public int[] getNoZeroIntegers(int n) {
        for( int i =1; i<n; i++ ){
            int a = i, b = n-i;
            if(isNoZero(a) && isNoZero(b)){
                return new int[]{a,b};
            }
        }
        return new int[]{1,1};
    }
    public boolean isNoZero(int num) {
    while (num > 0) {
        if (num % 10 == 0) return false;
        num /= 10;
    }
    return true;
    }
}