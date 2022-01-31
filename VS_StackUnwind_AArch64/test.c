#include <stdio.h>
#include <stdlib.h>

short a, b;
char d;

int fn4(int *v){
    return *v;
}

int fn3(){
    return 3;
}

int fn2(int j){
    int *i;

    i = (int*)malloc(sizeof(int));
    if (i == NULL) {
        printf("error: malloc");
        return -1;
    }

    scanf("%n", i);
    
    int r = *i;

    free(i);
    return 2 + j;
}

int fn1(int b, int b1, int b2, int b3, int b4, int b5, int b6, int b7, int b8, int b9, int b10, int b11, int b12, int b13, int b14, int b15, int b16, int b17, int b18, int b19, int b20, int b21, int b22, int b23, int b24, int b25, int b26, int b27, int b28, int b29, int b30){
    float c;
    
    b = b + b1 + b2 + b3 + b4 + b5 + b6 + b7 + b8 + b9 + b10 + b11 + b12 + b13 + b14 + b15 + b16 + b17 + b18 + b19 + b20 + b21 + b22 + b23 + b24 + b25 + b26 + b27 + b28 + b29 + b30;
    for (int i = 1; i < 2; i++) {
        int v[i];
        int *p;
        // fn2(16);
        c = c + fn3();
        // *p = fn4(v);
    }
    

    
    
    // b=fn2(16);
    // scanf("%f", &c);
    b = b + c;
    return b;
}

void main(){
    // printf("aaa");
    a=4;
    for (int i = 1; i < 2; i++) {
        int v[i];
        // fn2(16);
        d = d + fn3();
    }
    a=fn1(8, 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30);
}