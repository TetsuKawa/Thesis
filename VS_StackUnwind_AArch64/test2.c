#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <string.h>

double fn2(double x, double y, double a, double b){
	return x + y + a + b;
}

int fn1(double *p, int size, double x, double y){
	double d;
	double d_dash;
	int num=0;

	d = fn2(x, y, p[0], p[1]);
	for(int i=1; i<size; i++){
		d_dash = fn2(x, y, p[i*2], p[i*2+1]);
		if(d > d_dash){
			d = d_dash;
			num=i;
		}
	}
	return num;
}

int main(int argc, char *argv[])
{
	FILE *input_file;
	int input;
	int count=0;
	double data[200][2];
	int label[200];
	int i=0;
	int j=0;

	input_file = fopen(argv[1],"r");
	if(input_file==NULL){
		printf("input error\n");
		return -1;
	}
	while( (input=fscanf(input_file, "%lf,%lf", &data[count][0], &data[count][1])) != EOF){
		count++;
	}

	double *p;
	int n;

	printf("Input a k : ");
	scanf("%d", &n);

	int N = 2*n;
	int array[n];

	p = (double *)malloc(N *sizeof(double)); 

	for(i=0; i<200; i++){
		label[i] = fn1(p, n, data[i][0], data[i][1]);
	}

	free(p);
	return 0;
}
