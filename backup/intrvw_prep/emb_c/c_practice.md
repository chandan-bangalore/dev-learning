# Expected Output:
c
ch
cha
chan
chand
chanda
chandan
chanda
chand
chan
cha
ch
c

```
#include <stdio.h>
#include <string.h>

void print_str(char *str, int pos) {
    int cnt = 0;
    while(pos >= 0) {
        printf("%c",str[cnt]);
        cnt++; pos--;
    }
    printf("\n");
}

int main()
{
    char x[8] = "chandan";
    for(int i = 0, j = 0; i < 2*strlen(x); i++) {
        j = (i < strlen(x)) ? i : 2*strlen(x) - i - 2;
        print_str(x, j);
    }

    return 0;
}
```

# Expected o/p:
1  
1  2  
1  2  3  
1  2  3  4  
1  2  3  4  5  
1  2  3  4  5  6  
1  2  3  4  5  6  7  
1  2  3  4  5  6  7  8  
1  2  3  4  5  6  7  8  9  
1  2  3  4  5  6  7  8  
1  2  3  4  5  6  7  
1  2  3  4  5  6  
1  2  3  4  5  
1  2  3  4  
1  2  3  
1  2  
1  

```
#include <stdio.h>
#include <stdlib.h>

void print_num(int *num, int pos) {
    for (int i = 0; i < pos; i++) {
        printf("%d  ", num[i]);
    }
    printf("\n");
}

int main()
{
    int len = 9;
    int *x = (int *)malloc(len * sizeof(int));
    if (x == NULL) {
        printf("malloc failed!\n");
        return -1;
    }
    for (int i = 0; i < len; i++) {
        x[i] = i+1;
        //printf("%d, ",x[i]);
    }

    for (int i = 0, j = 0; i < 2*len; i++) {
        j = (i <= len) ? i : 2*len - i;
        print_num(x, j);
    }

    if (x != NULL) {
        free(x);
        x = NULL;
    }
    // Setting to NULL turns a silent corruption into a loud crash — much easier to debug.
    //printf("%d", x[0]);
    return 0;
}

```
#Expected output:
input byte = 32
converted bits: 0, 0, 1, 1, 0, 0, 1, 0, 
output byte = 32
```
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

void byte2bits(uint8_t *bits, uint8_t num, uint8_t len) {
    for (int i = 0; i < len; i++) {
        bits[i] = (num >> len - 1 - i) & 1;
    }
}

void bits2byte(uint8_t *byte, uint8_t *bits, uint8_t len) {
    uint8_t out = 0;
    for (int i = 0; i < len; i++) {
        out = (out << 1) | bits[i];
    }
    *byte = out;
}

int main()
{
    uint8_t num = 0x32;
    uint8_t bits[8] = {0};
    printf("input byte = %x\n", num);
    printf("converted to bits:\n");
    byte2bits(bits, num, 8);
    for (int i = 0; i < 8; i++) {
        printf("%u, ",bits[i]);   
    }
    
    uint8_t byteNew=0;
    bits2byte(&byteNew, bits, 8);
    printf("\noutput byte = %x\n", byteNew);
    
    return 0;
}

```
#Expected output:
input num = 45650321

pack to 4 bytes:
45, 65, 3, 21, 

bit sequence:
0 1 0 0 ,0 1 0 1 ,0 1 1 0 ,0 1 0 1 ,0 0 0 0 ,0 0 1 1 ,0 0 1 0 ,0 0 0 1 ,

bit sequence to bytes:
45 65 3 21 

bytes to bits:
0 1 0 0 ,0 1 0 1 ,0 1 1 0 ,0 1 0 1 ,0 0 0 0 ,0 0 1 1 ,0 0 1 0 ,0 0 0 1 ,

```
/******************************************************************************

Welcome to GDB Online.
GDB online is an online compiler and debugger tool for C, C++, Python, Java, PHP, Ruby, Perl,
C#, OCaml, VB, Swift, Pascal, Fortran, Haskell, Objective-C, Assembly, HTML, CSS, JS, SQLite, Prolog.
Code, Compile, Run and Debug online from anywhere in world.

*******************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

void num2bytes(uint8_t *byte, uint32_t num, uint8_t len) {
    uint8_t nb = len >> 3;
    for (int i = 0; i < nb; i++) {
        byte[i] = (num >> (len - (i+1)*8)) & 0xFF;
    }
}

void bitSequence(uint8_t *byte, uint32_t num, uint8_t len) {
    for (int i = 0; i < len; i++) {
        byte[i] = (num >> (len - 1 - i)) & 0x01;
    }
}

void bits2bytes(uint8_t *byte, uint8_t *bits, uint8_t len) {
    for (int i = 0; i < len>>3; i++) {
        for (int j = 0; j < 8; j++) {
            byte[i] = (byte[i] << 1) | bits[i*8 + j];
        }
    }
}

void bytes2bits(uint8_t *bits, uint8_t *byte, uint8_t len) {
    for (int i = 0; i < len>>3; i++) {
        for (int j = 0; j < 8; j++) {
            bits[i*8 + j] = (byte[i] >> (8 -1 - j) ) & 1u;
        }
    }
}

/* 
* 1. 32bit number to 4bytes
* 2. 32bit number to 32 bit sequences
* 3. long bit sequence to bytes
* 4. bytes to bits
*/
int main()
{
    uint32_t num = 0x32322323;
    uint8_t len = 32;
    uint8_t byte[4] = {0}; // re-use
    printf("input num = %x\n", num);
    //1. 32bit number to 4bytes
    printf("\npack to 4 bytes:\n");
    num2bytes(byte, num, len);
    for (int i = 0; i < 4; i++) {
        printf("%x, ",byte[i]);   
    }
    
    //2. 32bit number to bit sequence
    printf("\n\nbit sequence:\n");
    uint8_t bits[32];
    memset(bits, 0, len * sizeof(uint8_t));
    bitSequence(bits, num, len);
    for(int i = 0; i < len; i++) {
        printf("%u ",bits[i]);
        if (i%4 == 3) printf(",");
    }
    
    //3. long bit sequence to bytes
    printf("\n\nbit sequence to bytes:\n");
    memset(byte, 0, 4*sizeof(uint8_t));
    bits2bytes(byte, bits, len);
    for(int i = 0; i < len>>3; i++) {
        printf("%x ",byte[i]);
    }    
    
    
    //4. bytes to bits
    printf("\n\nbytes to bits:\n");
    bytes2bits(bits, byte, len);
    for(int i = 0; i < len; i++) {
        printf("%x ",bits[i]);
        if (i%4 == 3) printf(",");
    }     
    
    return 0;
}
```

# Check power of 2 and 4
powers of 4 pattern:
4^0, 4^1, ..., 4^n = {1, 4, 16, 64, ...} = {0b00000001, 0b00000100, 0b00010000, 0b01000000}
if you notice, 4^x always has 1's at odd index and 0's at even index

```
/* 2^x */
bool is_power_of_2(uint32_t n) {
    return n != 0 && ((n & (n - 1)) == 0);
}

/* 4^x */
bool is_power_of_4(uint32_t n) {
    return is_power_of_2(n) && (n & 0x55555555U);
}
```


#Remove duplicates in O(n)
Input : arr[] = {4, 2, 7, 2, 4, 9, 1, 7};
Output: arr[] = {4, 2, 7, 9, 1};

```
#include <stdio.h>

#define MAX_VAL 100

int remove_duplicates(int arr[], int n) {
    int seen[MAX_VAL + 1] = {0};
    int new_size = 0;

    for (int i = 0; i < n; i++) {
        if (seen[arr[i]] == 0) {
            seen[arr[i]] = 1;
            arr[new_size++] = arr[i];
        }
    }

    return new_size;
}

void print_array(int arr[], int n) {
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

int main() {
    int arr[] = {4, 2, 7, 2, 4, 9, 1, 7};
    int n = sizeof(arr) / sizeof(arr[0]);

    int new_size = remove_duplicates(arr, n);

    print_array(arr, new_size);

    return 0;
}
```
```

# flow between main() and subfunction():
# main calls the subfunction, it jumps to subfunction and comes back to main()
# where is main()? where is subfunction() in memory? how is it going and coming back to main?

Both main() and subfunc() code live in the Text segment (low address) — compiled as machine code sitting there permanently.

TEXT SEGMENT                         STACK

        ┌────────────────┐         HIGH 0xFF00
0x1000  │ int x = 10     │             │ empty     │
0x1004  │ call subfunc() │─────────┐   │ x = 10    │ ← main frame
0x1008  │ x = 30         │◄──────┐ │   │ ret 0x1008│
        ├────────────────┤       │ │   │ y = 20    │ ← subfunction frame
0x2000  │ int y = 20     │◄──────┘ │   │           │
0x2004  │ return         │─────────┘   │           │
        └────────────────┘         LOW 0xFEF4
                                   SP moves ↓ on call
                                   SP moves ↑ on return
								   							   
<*" One line summary of each register's job:
PC program counter — "what am I executing right now?" — Address of instruction currently executing
SP stack pointer — "where is the top of my stack?" — moves down on call, up on return
LR link register — "where do I go back when done?" — Stores return address when a function is called 
FP frame pointer — "where does my current frame start?" — Points to base of current stack frame, helps debugger find local variables								   
"*