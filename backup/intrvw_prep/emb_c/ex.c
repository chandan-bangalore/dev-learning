/******************************************************************************

Welcome to GDB Online.
  GDB online is an online compiler and debugger tool for C, C++, Python, PHP, Ruby, 
  C#, OCaml, VB, Perl, Swift, Prolog, Javascript, Pascal, COBOL, HTML, CSS, JS
  Code, Compile, Run and Debug online from anywhere in world.

*******************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

void print_str(char *x, int len) {
    for (int i = 0; i < len; i++) {
        printf("%c ",x[i]);
    }
    printf("\n");
}



int main()
{
	char x[7] = "chandan";
	printf("strlen = %ld\n\n", strlen(x));
	for (int i = 0; i < 14; i++) {
	    int j = (i < strlen(x)) ? i : 14 - i;
	    print_str(x, j);   
	}

    return 0;
}