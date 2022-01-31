#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <string.h>



void Rnd(int *ip, int n){//初期確定座標を設定
	int frag;
	int random;
	for(int i=0; i<n; i++){
		do{
			frag=0;
			srand((unsigned int) time(NULL));
			random=rand()%200;

			for(int j=0; j<i; j++){		//ランダムに選ばれた座標がすでに確定座標になっていないかチェック
				if(random == ip[j])	frag=1;	//すでに確定座標になっていたらfragを1立てる。
			}
		}while(frag==1);//frag＝＝１ならやり直し
		ip[i]=random;//
	}
}

double Distance(double x, double y, double a, double b){//２点座標間距離計算
	return 0; //sqrt(pow(x-a,2)+pow(y-b,2));
}

int Clustering(double *CoG, int size, double x, double y){//ある座標におけるクラスタラベルを返す
	double d;
	double d_dash;
	int class_number=0;

	//一番近い確定座標を検索
	d = Distance(x, y, CoG[0], CoG[1]);
	for(int i=1; i<size; i++){
		d_dash = Distance(x, y, CoG[i*2], CoG[i*2+1]);
		if(d > d_dash){
			d = d_dash;
			class_number=i;
		}
	}
	return class_number;
}

//確定座標を更新
void Update_CoG(double *CoG, int size, int *label, double data[200][2]){
	double gra_x;
	double gra_y;
	int count;

	for(int i=0; i<size; i++){
		gra_x=0;
		gra_y=0;
		count=0;
		for(int j=0; j<200; j++){
			if(label[j] == i){
				gra_x+=data[j][0];
				gra_y+=data[j][1];
				count++;
			}
		}
		CoG[i*2] = gra_x/count;
		CoG[i*2+1] = gra_y/count;
	}
}

//確定座標に変化がない場合は０を、変化がある場合は１を返す。
int Check_CoG(double *CoG, double *CoG_pre, int N){
	int count = 0;
	for(int i=0;i<N;i++){
		if(CoG_pre[i] == CoG[i])	count++;
	}
	if(count==N) return 0;
	else	return 1;
}

int main(int argc, char *argv[])
{
	FILE *fp_in, *fp_out, *gn;
	int input;
	int count=0;
	double data[200][2];// the number of data is 200
	int label[200];//各データにおけるクラスタ番号
	int i=0;
	int j=0;
	int Frag;


	//Input//
	// fp_in = fopen(argv[1],"r");
	// if(fp_in==NULL){
	// 	printf("fail: cannot open the input-file. Change the name of input-file. \n");
	// 	return -1;
	// }

	// while( (input=fscanf(fp_in, "%lf,%lf", &data[count][0], &data[count][1])) != EOF){
	// 	//printf("%lf %lf\n", data[count][0], data[count][1]);
	// 	count++;
	// }

	//k-means//
	//indicate a number of Culster
	double *CoG;
	int n;
	//クラスタ数を入力 //
	printf("Input a k : ");
	scanf("%d", &n);
	int N = 2*n;

	//CoG = (double *)malloc(N *sizeof(double));  // メモリ領域の確保 :確定座標保存配列のポインタ//
//注意：クラスタ番号iの確定座標（ｘ、ｙ）=(CoG[2*i],CoG[2*i+1])

	//int ip[n];//初期の確定座標番号を保持する配列
	// Rnd(ip,n);//初期確定座標番号決定


	// for(i=0; i<n; i++){//CoGに初期確定座標を代入
	// 	for(j=0; j<2; j++){
	// 		CoG[i*2+j] = data[ip[i]][j];
	// 	}
	// }

//確定座標およびクラスタ更新
	// double CoG_pre[N];
	// Frag = 1;
	// while(Frag){
		//クラスタラベル更新
		for(i=0; i<200; i++){
			label[i] = Clustering(CoG, n, data[i][0], data[i][1]);
		}

		// for(i=0;i<N;i++){
		// 	CoG_pre[i] = CoG[i];
		// }
		// Update_CoG(CoG, n, label, data);//確定座標更新
		// Frag = Check_CoG(CoG,CoG_pre,N);//確定座標の変化をチェック
	// }


	///////////

	//Output//
	// fp_out = fopen(argv[2],"w");
	// if(fp_out==NULL){
	// 	printf("fail: cannot open the output-file. Change the name of output-file.  \n");
	// 	return -1;
	// }


	// for(i=0;i<200;i++){
	// 	fprintf(fp_out, "%lf,%lf,%d\n", data[i][0], data[i][1], label[i]);
	// }

	// free(CoG);


	//gnuplot gragh//

/*	gn = popen("gnuplot -persist\n","w");
	fprintf(gn,"plot '-' with point lt 7 lc 1, '-' with point lt 7 lc 2, '-' with point lt 7 lc 3, '-' with point lt 7 lc 4\n");
	for(i=0; i<n; i++){
		for(j=0; j<200; j++){
			if(label[j]==i){
				fprintf(gn,"%f\t%f\n", data[j][0], data[j][1]);    // データの書き込み
			}
  	}
  	fprintf(gn,"e\n");
	}

  pclose(gn);
*/
	return 0;
}
