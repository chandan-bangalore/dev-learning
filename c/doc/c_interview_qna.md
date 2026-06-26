# C Interview Preparation — Complete Guide

> Covers: standard questions, tricky questions, output prediction, bug-find-and-fix, and embedded-specific questions across all 7 topic areas.

---

## How to use this file

| Section 					| What it tests |
|---|---|
| Standard Questions 		| Core concept recall |
| Tricky / Predict Output 	| Deep understanding, no assumptions |
| Bug Find & Fix 			| Debugging ability, attention to detail |
| Embedded-Specific 		| Hardware-aware C, real job scenarios |

Each question has: **concept**, **code**, **expected output or answer**, and where relevant, the **fix**.

---

# PART 1 — POINTERS

---

## Standard Questions

---

### 1. What does this print?

```c
#include <stdio.h>
int main() {
    int x = 10;
    int *p = &x;
    *p = 20;
    printf("%d\n", x);
    return 0;
}
```

**Answer:** `20`
**Why:** `p` points to `x`. Writing `*p = 20` modifies `x` through the pointer.

---

### 2. What is the size of a pointer?

```c
#include <stdio.h>
int main() {
    int    *ip;
    char   *cp;
    double *dp;
    printf("int*:    %zu\n", sizeof(ip));
    printf("char*:   %zu\n", sizeof(cp));
    printf("double*: %zu\n", sizeof(dp));
    return 0;
}
```

**Answer:** All print `8` on 64-bit systems, `4` on 32-bit.
**Why:** A pointer stores an address. Address size depends on architecture, not the type it points to.

---

### 3. Pointer arithmetic — what does this print?

```c
#include <stdio.h>
int main() {
    int arr[] = {10, 20, 30, 40, 50};
    int *p = arr;
    p++;
    printf("%d\n", *p);
    p += 2;
    printf("%d\n", *p);
    return 0;
}
```

**Answer:** `20` then `40`
**Why:** `p++` moves 4 bytes forward (one int). `p += 2` moves 8 more bytes.

---

### 4. What is the difference between these two?

```c
#include <stdio.h>
int main() {
    int x = 5;
    const int *p1 = &x;   // pointer to const int
    int * const p2 = &x;  // const pointer to int

    // *p1 = 10;  // illegal — cannot change value
    p1 = NULL;   // legal   — can change pointer

    *p2 = 10;    // legal   — can change value
    // p2 = NULL; // illegal — cannot change pointer

    printf("x = %d\n", x);
    return 0;
}
```

**Answer:** `x = 10`
**Rule:** `const` applies to whatever is immediately to its right. `const int *` = the int is const. `int * const` = the pointer is const.

---

### 5. Pointer to pointer — what prints?

```c
#include <stdio.h>
int main() {
    int x = 100;
    int *p = &x;
    int **pp = &p;

    **pp = 200;
    printf("%d\n", x);
    printf("%d\n", *p);
    printf("%d\n", **pp);
    return 0;
}
```

**Answer:** `200` `200` `200` — all three expressions access the same memory location.

---

## Tricky Questions — Predict the Output

---

### 6. TRICKY — pointer increment vs dereference precedence

```c
#include <stdio.h>
int main() {
    int arr[] = {10, 20, 30};
    int *p = arr;

    printf("%d\n", *p++);   // line A
    printf("%d\n", *p);     // line B
    printf("%d\n", (*p)++); // line C
    printf("%d\n", *p);     // line D
    return 0;
}
```

**Answer:**
```
10    // A: dereference p (=10), then increment p to arr[1]
20    // B: p now points to arr[1]
20    // C: dereference p (=20), then increment the VALUE at p to 21
21    // D: value at arr[1] is now 21
```
**Why:** `*p++` — postfix `++` has higher precedence than `*`, but postfix means the increment happens after the expression is evaluated. So you get the value first, then p moves. `(*p)++` — parentheses force dereference first, then the value is incremented.

---

### 7. TRICKY — what does sizeof give you?

```c
#include <stdio.h>
void func(int arr[]) {
    printf("inside func: %zu\n", sizeof(arr));
}
int main() {
    int arr[10];
    printf("in main: %zu\n", sizeof(arr));
    func(arr);
    return 0;
}
```

**Answer:**
```
in main:     40    (10 * 4 bytes)
inside func: 8     (just a pointer — array decayed)
```
**Why:** When an array is passed to a function it decays to a pointer. `sizeof` on a pointer gives pointer size, not array size. Always pass the length separately.

---

### 8. TRICKY — NULL pointer arithmetic

```c
#include <stdio.h>
int main() {
    int *p = NULL;
    printf("%p\n", (void*)(p + 1));
    return 0;
}
```

**Answer:** Prints an address like `0x4` (NULL=0, plus 4 bytes for int).
**Why:** This is undefined behavior in the C standard. The compiler may produce a result but you must never do this. Arithmetic on NULL is illegal.

---

### 9. TRICKY — array name is not always a pointer

```c
#include <stdio.h>
int main() {
    int arr[5] = {1,2,3,4,5};
    int *p = arr;

    printf("%d\n", sizeof(arr) / sizeof(arr[0]));  // A
    printf("%d\n", sizeof(p)   / sizeof(p[0]));    // B
    return 0;
}
```

**Answer:**
```
5    // A: 20/4 = 5 — correct element count
2    // B: 8/4 = 2 on 64-bit — WRONG, just pointer/int sizes
```
**Why:** `sizeof(arr)` knows the full array. `sizeof(p)` is just the pointer size. This is a common embedded bug when passing arrays.

---

### 10. TRICKY — void pointer

```c
#include <stdio.h>
int main() {
    int x = 0x41424344;
    void *p = &x;

    char *cp = (char*)p;
    printf("%c\n", *cp);        // what prints?
    printf("%c\n", *(cp + 1));  // what prints?
    return 0;
}
```

**Answer (little-endian system like x86):**
```
D    // byte 0 = 0x44 = 'D'
C    // byte 1 = 0x43 = 'C'
```
**Why:** On little-endian, LSB is stored at lowest address. `0x41424344` → bytes at address: `44 43 42 41`.

---

## Bug Find & Fix

---

### 11. BUG — dangling pointer

```c
#include <stdio.h>
#include <stdlib.h>

int* create_value() {
    int x = 42;
    return &x;           // BUG: returning address of local variable
}

int main() {
    int *p = create_value();
    printf("%d\n", *p);  // undefined behavior
    return 0;
}
```

**Bug:** `x` is on the stack and is destroyed when `create_value()` returns. `p` is a dangling pointer.

**Fix:**
```c
#include <stdio.h>
#include <stdlib.h>

int* create_value() {
    int *x = (int*)malloc(sizeof(int));  // heap — persists
    if (!x) return NULL;
    *x = 42;
    return x;
}

int main() {
    int *p = create_value();
    if (p) {
        printf("%d\n", *p);   // 42
        free(p);
        p = NULL;
    }
    return 0;
}
```

---

### 12. BUG — off-by-one in pointer traversal

```c
#include <stdio.h>
int sum(int *arr, int n) {
    int total = 0;
    int *end = arr + n;
    while (arr <= end) {      // BUG
        total += *arr++;
    }
    return total;
}
int main() {
    int a[] = {1, 2, 3, 4, 5};
    printf("%d\n", sum(a, 5));
    return 0;
}
```

**Bug:** `arr <= end` includes `end` itself which is one past the array. Should be `arr < end`.

**Fix:**
```c
#include <stdio.h>
int sum(int *arr, int n) {
    int total = 0;
    int *end = arr + n;
    while (arr < end) {       // FIX: strict less-than
        total += *arr++;
    }
    return total;
}
int main() {
    int a[] = {1, 2, 3, 4, 5};
    printf("%d\n", sum(a, 5));  // 15
    return 0;
}
```

---

### 13. BUG — wild pointer write

```c
#include <stdio.h>
int main() {
    int *p;
    *p = 100;              // BUG: p is uninitialized (wild pointer)
    printf("%d\n", *p);
    return 0;
}
```

**Bug:** `p` holds a garbage address. Writing to it corrupts unknown memory or segfaults.

**Fix:**
```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int *p = (int*)malloc(sizeof(int));  // FIX: initialize first
	```
	if (!p) return 1;
    *p = 100;
    printf("%d\n", *p);   // 100
	```
	```
    free(p);
	p = NULL;
    return 0;
}
```

---

### 14. BUG — double free

```c
#include <stdlib.h>
int main() {
    int *p = (int*)malloc(sizeof(int));
    *p = 42;
    free(p);
    free(p);    // BUG: double free — heap corruption
    return 0;
}
```

**Fix:**
```c
#include <stdlib.h>
int main() {
    int *p = (int*)malloc(sizeof(int));
    *p = 42;
    free(p);
    p = NULL;   // FIX: NULL after free
    free(p);    // free(NULL) is safe — does nothing
    return 0;
}
```

---

### 15. BUG — pointer comparison across arrays

```c
#include <stdio.h>
int main() {
    int a[] = {1, 2, 3};
    int b[] = {4, 5, 6};
    int *p = a;
    int *q = b;

    if (p < q) printf("a is before b\n");
    else        printf("b is before a\n");
    return 0;
}
```

**Bug:** Comparing pointers from different arrays is undefined behavior. Result is not meaningful.

**Fix:** Only compare pointers within the same array or object.

```c
#include <stdio.h>
int main() {
    int arr[] = {1, 2, 3, 4, 5};
    int *p = &arr[1];
    int *q = &arr[3];

    if (p < q) printf("p is before q\n");  // well-defined — same array
    return 0;
}
```

---
```

# PART 2 — MEMORY MANAGEMENT

---

## Standard Questions

---

### 16. What do these print?

```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main() {
    int *a = (int*)malloc(5 * sizeof(int));
    int *b = (int*)calloc(5, sizeof(int));

    printf("malloc[0] = %d\n", a[0]);  // A
    printf("calloc[0] = %d\n", b[0]);  // B

    free(a); free(b);
    return 0;
}
```

**Answer:**
```
malloc[0] = <garbage>   // A: malloc does NOT initialize
calloc[0] = 0           // B: calloc zero-initializes
```

---

### 17. Stack vs heap — what is the scope?

```c
#include <stdio.h>
#include <stdlib.h>

int* stack_val() {
    int x = 10;
    return &x;      // WRONG — stack variable
}
int* heap_val() {
    int *x = malloc(sizeof(int));
    *x = 10;
    return x;       // OK — heap persists
}
int main() {
    int *p = heap_val();
    printf("%d\n", *p);   // 10 — safe
    free(p);
    return 0;
}
```

**Answer:** `10`. The heap version is safe. The stack version would be a dangling pointer.

---

### 18. What happens to memory here?

```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int *p = (int*)malloc(10 * sizeof(int));
    p = (int*)malloc(20 * sizeof(int));  // reassign
    free(p);
    return 0;
}
```

**Answer:** The first `malloc` block (40 bytes) is leaked. The pointer to it was overwritten before it was freed.

**Fix:**
```c
int *p = (int*)malloc(10 * sizeof(int));
free(p);                                   // free first
p = (int*)malloc(20 * sizeof(int));        // then reassign
free(p);
```

---

## Tricky Questions

---

### 19. TRICKY — realloc behavior

```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int *p = (int*)malloc(3 * sizeof(int));
    p[0]=1; p[1]=2; p[2]=3;

    int *q = (int*)realloc(p, 5 * sizeof(int));
    if (q == NULL) {
        free(p);   // realloc failed — p still valid
        return 1;
    }
    // Q: is p still safe to use here?
    q[3]=4; q[4]=5;
    for (int i=0; i<5; i++) printf("%d ", q[i]);
    free(q);
    return 0;
}
```

**Answer:** `1 2 3 4 5`
**Trap:** After `realloc` succeeds, `p` may be invalid (memory may have moved). Never use `p` after `realloc` — only use `q`. That is why you should never write `p = realloc(p, size)` — if realloc fails it returns NULL, and you lost your only pointer to the original block.

---

### 20. TRICKY — static variable lifetime

```c
#include <stdio.h>
int* get_counter() {
    static int count = 0;
    count++;
    return &count;
}
int main() {
    int *p1 = get_counter();
    int *p2 = get_counter();
    int *p3 = get_counter();

    printf("%d %d %d\n", *p1, *p2, *p3);
    return 0;
}
```

**Answer:** `3 3 3`
**Why:** `count` is static — there is only ONE instance. All three pointers point to the same variable. After three calls it equals 3, so all pointers show 3.

---

### 21. TRICKY — BSS vs data segment

```c
#include <stdio.h>
int a;           // BSS
int b = 0;       // data segment (explicitly initialized to 0)
int c = 5;       // data segment

int main() {
    printf("%d %d %d\n", a, b, c);
    return 0;
}
```

**Answer:** `0 0 5`
**Why:** Both `a` and `b` are zero. But `b` takes space in the executable file (because it has an initializer), while `a` is in BSS (no space in executable, zeroed by OS at load time). In embedded, BSS is zeroed by startup code.

---

## Bug Find & Fix

---

### 22. BUG — using pointer after realloc

```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int *p = (int*)malloc(3 * sizeof(int));
    p[0]=1; p[1]=2; p[2]=3;

    int *q = (int*)realloc(p, 10 * sizeof(int));
    printf("%d\n", p[0]);  // BUG: p may be invalid after realloc
    free(q);
    return 0;
}
```

**Fix:**
```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int *p = (int*)malloc(3 * sizeof(int));
    p[0]=1; p[1]=2; p[2]=3;

    int *q = (int*)realloc(p, 10 * sizeof(int));
    if (!q) { free(p); return 1; }
    p = NULL;              // FIX: invalidate p immediately
    printf("%d\n", q[0]); // use q only
    free(q);
    return 0;
}
```

---

### 23. BUG — malloc return not checked

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main() {
    char *buf = (char*)malloc(1000000000); // huge allocation
    strcpy(buf, "Hello");                  // BUG: buf may be NULL
    printf("%s\n", buf);
    free(buf);
    return 0;
}
```

**Fix:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main() {
    char *buf = (char*)malloc(1000000000);
    if (!buf) {                            // FIX: always check
        fprintf(stderr, "malloc failed\n");
        return 1;
    }
    strcpy(buf, "Hello");
    printf("%s\n", buf);
    free(buf);
    return 0;
}
```

---

### 24. BUG — memory leak in loop

```c
#include <stdlib.h>
void process(int n) {
    for (int i = 0; i < n; i++) {
        int *buf = (int*)malloc(100 * sizeof(int));
        buf[0] = i;
        // BUG: buf is never freed — leaks 400 bytes per iteration
    }
}
int main() {
    process(1000);  // leaks 400,000 bytes
    return 0;
}
```

**Fix:**
```c
#include <stdlib.h>
void process(int n) {
    for (int i = 0; i < n; i++) {
        int *buf = (int*)malloc(100 * sizeof(int));
        if (!buf) return;
        buf[0] = i;
        free(buf);   // FIX: free inside the loop
    }
}
int main() {
    process(1000);
    return 0;
}
```

---

# PART 3 — BIT MANIPULATION

---

## Standard Questions

---

### 25. Set, clear, toggle, check — all in one

```c
#include <stdio.h>
#include <stdint.h>

#define BIT_SET(r,n)   ((r) |=  (1U << (n)))
#define BIT_CLR(r,n)   ((r) &= ~(1U << (n)))
#define BIT_TOG(r,n)   ((r) ^=  (1U << (n)))
#define BIT_CHK(r,n)   (((r) >> (n)) & 1U)

int main() {
    uint8_t reg = 0x00;

    BIT_SET(reg, 3);
    printf("After SET  bit3: 0x%02X\n", reg);  // 0x08

    BIT_TOG(reg, 3);
    printf("After TOG  bit3: 0x%02X\n", reg);  // 0x00

    BIT_SET(reg, 7);
    BIT_CLR(reg, 7);
    printf("After CLR  bit7: 0x%02X\n", reg);  // 0x00

    BIT_SET(reg, 5);
    printf("Bit 5 set? %d\n", BIT_CHK(reg, 5)); // 1
    return 0;
}
```

---

### 26. Count set bits (Brian Kernighan)

```c
#include <stdio.h>
int count_bits(unsigned int n) {
    int count = 0;
    while (n) {
        n &= (n - 1);   // clears lowest set bit each iteration
        count++;
    }
    return count;
}
int main() {
    printf("%d\n", count_bits(0b10110101));  // 5
    printf("%d\n", count_bits(0xFF));         // 8
    printf("%d\n", count_bits(0));            // 0
    return 0;
}
```

---

### 27. Power of 2 check

```c
#include <stdio.h>
int is_power_of_2(unsigned int n) {
    return (n > 0) && ((n & (n - 1)) == 0);
}
int main() {
    printf("%d\n", is_power_of_2(0));    // 0
    printf("%d\n", is_power_of_2(1));    // 1
    printf("%d\n", is_power_of_2(8));    // 1
    printf("%d\n", is_power_of_2(6));    // 0
    printf("%d\n", is_power_of_2(256));  // 1
    return 0;
}
```

---

## Tricky Questions

---

### 28. TRICKY — what does this print?

```c
#include <stdio.h>
int main() {
    unsigned char x = 0xFF;
    x = x << 1;
    printf("0x%02X\n", x);
    return 0;
}
```

**Answer:** `0xFE`
**Why:** Left shift by 1 on `0xFF` (11111111) = `11111110` = `0xFE`. The MSB falls off. If this were `int`, integer promotion applies and the result would be `0x1FE` before truncation.

---

### 29. TRICKY — signed vs unsigned shift

```c
#include <stdio.h>
int main() {
    signed   int s = -8;
    unsigned int u = -8;  // same bit pattern, different type

    printf("signed   >> 1: %d\n",  s >> 1);
    printf("unsigned >> 1: %u\n",  u >> 1);
    return 0;
}
```

**Answer:**
```
signed   >> 1: -4          (arithmetic shift — sign bit replicated)
unsigned >> 1: 2147483644  (logical shift — zero filled)
```
**Why:** Right shift on signed integers is implementation-defined in C. On most systems it does arithmetic shift (replicates sign bit). On unsigned, it always zero-fills. Never right-shift a signed negative number in portable code.

---

### 30. TRICKY — XOR swap trap

```c
#include <stdio.h>
int main() {
    int a = 5;
    int *p = &a;

    // XOR swap with itself via pointer
    a    ^= *p;
    *p   ^= a;
    a    ^= *p;

    printf("a = %d\n", a);
    return 0;
}
```

**Answer:** `a = 0`
**Why:** `p` points to `a`, so this is `a ^= a; a ^= a; a ^= a;` — XOR with itself always gives 0. XOR swap only works when the two variables are at different memory addresses.

---

### 31. TRICKY — integer promotion in bit ops

```c
#include <stdio.h>
int main() {
    unsigned char a = 0xFF;
    unsigned char b = ~a;
    printf("b = %d\n", b);
    return 0;
}
```

**Answer:** `b = 0`
**Why:** `~a` promotes `a` to `int` first (0x000000FF), then complements to `0xFFFFFF00`, then truncates back to `unsigned char` = `0x00` = 0.

---

### 32. TRICKY — endianness detection

```c
#include <stdio.h>
int main() {
    unsigned int x = 0x01020304;
    unsigned char *p = (unsigned char*)&x;
    printf("byte[0] = 0x%02X\n", p[0]);
    if (p[0] == 0x04) printf("Little Endian\n");
    else               printf("Big Endian\n");
    return 0;
}
```

**Answer (x86):** `byte[0] = 0x04` → `Little Endian`
**Why:** x86 stores LSB at the lowest address. So byte 0 of `0x01020304` is `0x04`.

---

## Bug Find & Fix

---

### 33. BUG — wrong mask clears wrong bits

```c
#include <stdio.h>
#include <stdint.h>
int main() {
    uint8_t reg = 0xFF;
    // Intent: clear bits 4 and 5
    reg &= (3 << 4);    // BUG: this KEEPS bits 4&5, clears everything else
    printf("0x%02X\n", reg);  // prints 0x30, not 0xCF
    return 0;
}
```

**Fix:**
```c
#include <stdio.h>
#include <stdint.h>
int main() {
    uint8_t reg = 0xFF;
    reg &= ~(3 << 4);   // FIX: complement the mask to clear bits 4&5
    printf("0x%02X\n", reg);  // 0xCF = 11001111
    return 0;
}
```

---

### 34. BUG — shift amount too large

```c
#include <stdio.h>
int main() {
    unsigned int x = 1;
    int shift = 32;
    printf("0x%X\n", x << shift);   // BUG: undefined behavior
    return 0;
}
```

**Bug:** Shifting a 32-bit value by 32 or more is undefined behavior in C.

**Fix:**
```c
#include <stdio.h>
#include <stdint.h>
int main() {
    uint64_t x = 1;
    int shift = 32;
    printf("0x%llX\n", (unsigned long long)(x << shift)); // use 64-bit
    return 0;
}
```

---

### 35. BUG — read-modify-write on hardware register

```c
#include <stdint.h>
// Intended: set bit 3 in GPIO output register
// Actual register value: 0b10110010
volatile uint32_t *GPIO_ODR = (volatile uint32_t*)0x40020014;

void led_on() {
    *GPIO_ODR = (1 << 3);    // BUG: overwrites ALL other bits!
}
```

**Fix:**
```c
void led_on() {
    *GPIO_ODR |= (1 << 3);   // FIX: read-modify-write preserves other bits
}
void led_off() {
    *GPIO_ODR &= ~(1 << 3);  // clear only bit 3
}
```

---

# PART 4 — STRUCTURES AND UNIONS

---

## Standard Questions

---

### 36. What does sizeof give for this struct?

```c
#include <stdio.h>
struct A {
    char  a;    // 1 byte
    int   b;    // 4 bytes
    char  c;    // 1 byte
};
struct B {
    int   b;    // 4 bytes
    char  a;    // 1 byte
    char  c;    // 1 byte
};
int main() {
    printf("A: %zu\n", sizeof(struct A));  // ?
    printf("B: %zu\n", sizeof(struct B));  // ?
    return 0;
}
```

**Answer:**
```
A: 12    (1 + 3pad + 4 + 1 + 3pad)
B: 8     (4 + 1 + 1 + 2pad)
```
**Lesson:** Reordering members from largest to smallest reduces padding and struct size.

---

### 37. Union memory sharing

```c
#include <stdio.h>
#include <stdint.h>
typedef union {
    uint32_t  full;
    uint8_t   bytes[4];
} Word;

int main() {
    Word w;
    w.full = 0x12345678;
    printf("bytes: %02X %02X %02X %02X\n",
           w.bytes[0], w.bytes[1], w.bytes[2], w.bytes[3]);
    printf("size: %zu\n", sizeof(w));
    return 0;
}
```

**Answer (little-endian):**
```
bytes: 78 56 34 12
size: 4
```

---

## Tricky Questions

---

### 38. TRICKY — struct copy is shallow

```c
#include <stdio.h>
#include <stdlib.h>
typedef struct {
    int  id;
    int *data;
} Node;

int main() {
    int val = 99;
    Node a = {1, &val};
    Node b = a;           // shallow copy

    b.id = 2;
    *b.data = 42;         // modifies val through b

    printf("a.id=%d a.data=%d\n", a.id, *a.data);
    printf("b.id=%d b.data=%d\n", b.id, *b.data);
    return 0;
}
```

**Answer:**
```
a.id=1 a.data=42    // a.data changed because a and b share the same pointer
b.id=2 b.data=42
```
**Lesson:** Struct assignment copies the pointer value, not what it points to. Both structs now point to the same `val`.

---

### 39. TRICKY — bit field behavior

```c
#include <stdio.h>
typedef struct {
    unsigned int a : 3;   // 3 bits
    unsigned int b : 3;   // 3 bits
    unsigned int c : 2;   // 2 bits
} Flags;

int main() {
    Flags f;
    f.a = 7;   // max for 3 bits is 7 (0b111)
    f.b = 8;   // 8 = 0b1000 — overflows 3-bit field!
    f.c = 3;

    printf("a=%u b=%u c=%u\n", f.a, f.b, f.c);
    return 0;
}
```

**Answer:** `a=7 b=0 c=3`
**Why:** `8` in binary is `1000`. Storing in a 3-bit field truncates to `000` = 0. Assigning out-of-range values to bit fields silently wraps.

---

### 40. TRICKY — anonymous union inside struct

```c
#include <stdio.h>
#include <stdint.h>
typedef struct {
    uint8_t type;
    union {
        uint32_t int_val;
        float    float_val;
        uint8_t  bytes[4];
    };   // anonymous — members accessed directly
} Variant;

int main() {
    Variant v;
    v.type      = 1;
    v.int_val   = 0x3F800000;  // IEEE 754 = 1.0f
    printf("as int:   0x%08X\n", v.int_val);
    printf("as float: %.1f\n",   v.float_val);
    printf("size: %zu\n", sizeof(v));
    return 0;
}
```

**Answer:**
```
as int:   0x3F800000
as float: 1.0
size: 8     (1 byte type + 3 pad + 4 union)
```

---

## Bug Find & Fix

---

### 41. BUG — packed struct misaligned access

```c
#include <stdio.h>
#include <stdint.h>
typedef struct __attribute__((packed)) {
    uint8_t  a;
    uint32_t b;   // at offset 1 — NOT 4-byte aligned
} Packed;

int main() {
    Packed p;
    p.a = 1;
    p.b = 0x12345678;
    uint32_t *ptr = &p.b;
    printf("0x%X\n", *ptr);   // BUG: misaligned access — may crash on ARM
    return 0;
}
```

**Fix:** Never take a pointer to a field inside a packed struct. Copy it out first.

```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>
typedef struct __attribute__((packed)) {
    uint8_t  a;
    uint32_t b;
} Packed;

int main() {
    Packed p;
    p.a = 1;
    p.b = 0x12345678;

    uint32_t val;
    memcpy(&val, &p.b, sizeof(val));  // FIX: safe byte-by-byte copy
    printf("0x%X\n", val);
    return 0;
}
```

---

### 42. BUG — comparing structs with ==

```c
#include <stdio.h>
typedef struct { int x; int y; } Point;

int main() {
    Point a = {1, 2};
    Point b = {1, 2};

    if (a == b) {           // BUG: struct comparison not supported in C
        printf("equal\n");
    }
    return 0;
}
```

**Fix:**
```c
#include <stdio.h>
typedef struct { int x; int y; } Point;

int points_equal(Point a, Point b) {
    return (a.x == b.x) && (a.y == b.y);  // member by member
}
int main() {
    Point a = {1, 2};
    Point b = {1, 2};
    if (points_equal(a, b)) printf("equal\n");  // equal
    return 0;
}
```

---

# PART 5 — ARRAYS AND STRINGS

---

## Standard Questions

---

### 43. String literals — what prints?

```c
#include <stdio.h>
#include <string.h>
int main() {
    char arr[] = "Hello";
    char *ptr  = "Hello";

    arr[0] = 'J';    // legal — arr is a copy on stack
    // ptr[0] = 'J'; // ILLEGAL — ptr points to read-only literal

    printf("arr: %s\n", arr);    // Jello
    printf("len: %zu\n", strlen(arr));  // 5
    printf("siz: %zu\n", sizeof(arr)); // 6 (includes \0)
    return 0;
}
```

**Answer:**
```
arr: Jello
len: 5
siz: 6
```

---

### 44. 2D array layout

```c
#include <stdio.h>
int main() {
    int m[2][3] = {{1,2,3},{4,5,6}};

    // Three ways to access m[1][2]:
    printf("%d\n", m[1][2]);          // standard
    printf("%d\n", *(*(m+1)+2));      // pointer arithmetic
    printf("%d\n", *((int*)m + 5));   // flat offset: 1*3+2 = 5
    return 0;
}
```

**Answer:** `6` `6` `6` — all three access the same element.

---

## Tricky Questions

---

### 45. TRICKY — string not null terminated

```c
#include <stdio.h>
#include <string.h>
int main() {
    char s[5] = {'H','e','l','l','o'};  // no \0
    printf("len: %zu\n", strlen(s));     // undefined behavior!
    return 0;
}
```

**Answer:** Undefined behavior — `strlen` reads past `s[4]` looking for `\0`, reads garbage memory.

**Fix:**
```c
char s[6] = {'H','e','l','l','o','\0'};  // explicit terminator
// or:
char s[] = "Hello";                        // compiler adds \0
```

---

### 46. TRICKY — strncpy does not always null-terminate

```c
#include <stdio.h>
#include <string.h>
int main() {
    char dst[5];
    strncpy(dst, "Hello World", 5);   // copies "Hello", NO \0 added
    printf("%s\n", dst);               // undefined — no null terminator
    return 0;
}
```

**Answer:** Undefined behavior — `dst` has no `\0` because the source is longer than `n`.

**Fix:**
```c
#include <stdio.h>
#include <string.h>
int main() {
    char dst[5];
    strncpy(dst, "Hello World", sizeof(dst) - 1);
    dst[sizeof(dst) - 1] = '\0';   // always manually null-terminate
    printf("%s\n", dst);            // "Hell"
    return 0;
}
```

---

### 47. TRICKY — array vs pointer string modification

```c
#include <stdio.h>
int main() {
    char    arr[] = "hello";  // copy on stack — mutable
    char   *ptr   = "hello";  // pointer to read-only literal

    arr[0] = 'H';   // OK
    // ptr[0] = 'H'; // CRASH — write to read-only memory

    printf("%s\n", arr);  // Hello
    return 0;
}
```

---

## Bug Find & Fix

---

### 48. BUG — gets() buffer overflow

```c
#include <stdio.h>
int main() {
    char buf[10];
    gets(buf);           // BUG: gets has no size limit — banned in C11
    printf("%s\n", buf);
    return 0;
}
```

**Fix:**
```c
#include <stdio.h>
int main() {
    char buf[10];
    fgets(buf, sizeof(buf), stdin);  // FIX: size-limited
    printf("%s\n", buf);
    return 0;
}
```

---

### 49. BUG — off-by-one in string copy

```c
#include <stdio.h>
#include <string.h>
int main() {
    char src[] = "Hello";
    char dst[5];              // BUG: "Hello" needs 6 bytes (5 + '\0')
    strcpy(dst, src);         // writes '\0' to dst[5] — overflow!
    printf("%s\n", dst);
    return 0;
}
```

**Fix:**
```c
#include <stdio.h>
#include <string.h>
int main() {
    char src[] = "Hello";
    char dst[6];              // FIX: strlen("Hello")+1 = 6
    strcpy(dst, src);
    printf("%s\n", dst);      // Hello
    return 0;
}
```

---

### 50. BUG — modifying string literal

```c
#include <stdio.h>
int main() {
    char *s = "embedded";
    s[0] = 'E';               // BUG: string literal is read-only
    printf("%s\n", s);
    return 0;
}
```

**Fix:**
```c
#include <stdio.h>
int main() {
    char s[] = "embedded";    // FIX: copy to writable stack array
    s[0] = 'E';
    printf("%s\n", s);        // Embedded
    return 0;
}
```

---

# PART 6 — FUNCTIONS AND FUNCTION POINTERS

---

## Standard Questions

---

### 51. Function pointer basics

```c
#include <stdio.h>
int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }
int mul(int a, int b) { return a * b; }

int main() {
    int (*op)(int, int);   // function pointer

    op = add; printf("add: %d\n", op(10, 3));
    op = sub; printf("sub: %d\n", op(10, 3));
    op = mul; printf("mul: %d\n", op(10, 3));
    return 0;
}
```

**Answer:** `add: 13` `sub: 7` `mul: 30`

---

### 52. Callback pattern

```c
#include <stdio.h>
typedef void (*Handler)(int);

void on_success(int code) { printf("OK code=%d\n", code); }
void on_error  (int code) { printf("ERR code=%d\n", code); }

void process(int val, Handler success, Handler error) {
    if (val > 0) success(val);
    else         error(val);
}
int main() {
    process( 10, on_success, on_error);   // OK code=10
    process(-5,  on_success, on_error);   // ERR code=-5
    return 0;
}
```

---

### 53. Array of function pointers — state machine

```c
#include <stdio.h>
void state_idle()    { printf("idle\n"); }
void state_running() { printf("running\n"); }
void state_error()   { printf("error\n"); }

typedef void (*StateFn)(void);

StateFn states[] = { state_idle, state_running, state_error };

int main() {
    for (int i = 0; i < 3; i++) {
        states[i]();   // call each state function
    }
    return 0;
}
```

**Answer:** `idle` `running` `error`

---

## Tricky Questions

---

### 54. TRICKY — recursion stack depth

```c
#include <stdio.h>
int fib(int n) {
    if (n <= 1) return n;
    return fib(n-1) + fib(n-2);
}
int main() {
    printf("%d\n", fib(10));
    return 0;
}
```

**Answer:** `55`
**Trap:** `fib(50)` would take minutes — exponential time O(2^n). In embedded, deep recursion also risks stack overflow. Interviewers often ask: "how would you optimize this?" Answer: memoization, or convert to iterative with an array.

---

### 55. TRICKY — static function scope

```c
// file1.c
static int helper() { return 42; }   // not visible outside file1.c
int public_func()   { return helper(); }

// file2.c — if you call helper() here, you get a linker error
```

**Interviewer question:** "Why use static on a function?"
**Answer:** Limits visibility to the translation unit (file). Prevents name conflicts in large projects. In embedded drivers, each driver has its own `static` helpers — they don't pollute the global namespace.

---

### 56. TRICKY — inline function vs macro

```c
#include <stdio.h>
#define SQUARE_MACRO(x) ((x) * (x))
static inline int square_inline(int x) { return x * x; }

int main() {
    int n = 3;
    printf("%d\n", SQUARE_MACRO(n++));   // what happens?
    n = 3;
    printf("%d\n", square_inline(n++));  // what happens?
    return 0;
}
```

**Answer:**
```
12     // macro: (3++)*(3++) = 3*4 = 12, n becomes 5
9      // inline: n=3 passed once, n++ happens after call, result=9
```
**Why:** Macro expands to `(n++)*(n++)` — `n` is incremented twice. The inline function evaluates `n` once, then increments.

---

## Bug Find & Fix

---

### 57. BUG — returning local variable

```c
#include <stdio.h>
char* get_message() {
    char msg[] = "Hello from function";
    return msg;    // BUG: msg is on stack — destroyed on return
}
int main() {
    char *s = get_message();
    printf("%s\n", s);   // undefined behavior
    return 0;
}
```

**Fix options:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Option 1: static (persists, but shared — not thread-safe)
char* get_message_static() {
    static char msg[] = "Hello from function";
    return msg;
}

// Option 2: heap allocation (caller must free)
char* get_message_heap() {
    char *msg = (char*)malloc(20);
    if (!msg) return NULL;
    strcpy(msg, "Hello from function");
    return msg;
}

int main() {
    printf("%s\n", get_message_static());

    char *s = get_message_heap();
    if (s) { printf("%s\n", s); free(s); }
    return 0;
}
```

---

### 58. BUG — wrong function pointer typedef

```c
#include <stdio.h>
typedef int* (*FuncPtr)(int);   // pointer to function returning int*

int result;
int* compute(int x) {
    result = x * 2;
    return &result;
}

int main() {
    FuncPtr fp = compute;
    int *r = fp(5);
    printf("%d\n", *r);   // 10
    return 0;
}
```

This is actually correct. The tricky part is reading the declaration.
**Rule:** To read a complex declaration, start at the name and spiral outward: `FuncPtr` is a pointer to a function taking `int` and returning `int*`.

---

# PART 7 — DEBUGGING AND RUNTIME

---

## Standard Questions

---

### 59. volatile — why is it needed?

```c
#include <stdint.h>
volatile uint32_t *STATUS = (volatile uint32_t*)0x40004400;

void wait_ready() {
    while ((*STATUS & 0x01) == 0) {
        // spin until bit 0 set by hardware
    }
}
```

**Without volatile:** compiler caches `*STATUS` in a register and never re-reads it — infinite loop even when hardware sets the bit.
**With volatile:** every loop iteration re-reads the actual register address.

---

### 60. What causes a segfault? List 5 causes.

```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    // 1. NULL dereference
    int *p1 = NULL;
    // *p1 = 5;

    // 2. Out of bounds
    int arr[3];
    // arr[10] = 5;

    // 3. Use after free
    int *p2 = malloc(4);
    free(p2);
    // *p2 = 5;

    // 4. Stack overflow (infinite recursion)
    // void f() { f(); }

    // 5. Write to string literal
    char *s = "hello";
    // s[0] = 'H';

    printf("All segfault causes demonstrated (safely)\n");
    return 0;
}
```

---

## Tricky Questions

---

### 61. TRICKY — undefined behavior with signed overflow

```c
#include <stdio.h>
#include <limits.h>
int main() {
    int x = INT_MAX;
    printf("%d\n", x + 1);   // undefined behavior!
    return 0;
}
```

**Answer:** Undefined behavior. Most compilers produce `INT_MIN` (wraps around) but this is NOT guaranteed. The optimizer can assume signed overflow never happens and generate completely unexpected code.
**Fix:** Use `unsigned int` if you need wrapping, or check before adding:

```c
if (x < INT_MAX) x++;
```

---

### 62. TRICKY — sequence point undefined behavior

```c
#include <stdio.h>
int main() {
    int i = 5;
    printf("%d %d\n", i++, i++);   // undefined behavior
    return 0;
}
```

**Answer:** Undefined behavior — modifying `i` twice between sequence points. Different compilers produce different results (`5 6`, `6 5`, or anything else).
**Fix:** Split into separate statements.

---

### 63. TRICKY — const does not mean immutable

```c
#include <stdio.h>
int main() {
    const int x = 10;
    int *p = (int*)&x;   // cast away const — undefined behavior
    *p = 99;
    printf("%d\n", x);   // may print 10 or 99 or something else
    printf("%d\n", *p);
    return 0;
}
```

**Answer:** Undefined behavior. The compiler may keep `x = 10` in a register and never read memory for it, so `printf("%d\n", x)` prints `10` even though `*p = 99` wrote `99` to that address. `const` means "I promise not to change this" — breaking that promise invokes UB.

---

### 64. TRICKY — race condition with volatile

```c
#include <stdint.h>
volatile int flag = 0;

// ISR (called by hardware interrupt):
void UART_IRQ_Handler(void) {
    flag = 1;
}

// Main loop:
void main_loop(void) {
    while (!flag) { /* wait */ }
    // process...
    flag = 0;
}
```

**Question:** Is this safe for a single producer (ISR) and single consumer (main)?
**Answer:** On single-core bare-metal embedded, yes — `volatile` ensures re-reading and single-instruction write is atomic for aligned int. On multi-core, no — you need memory barriers or atomics (`stdatomic.h`).

---

## Bug Find & Fix — Debugging Section

---

### 65. BUG — missing volatile on ISR-shared variable

```c
#include <stdint.h>
int data_ready = 0;          // BUG: not volatile

void ISR_handler(void) {
    data_ready = 1;
}

void main_loop(void) {
    while (data_ready == 0) {   // compiler may hoist this out of loop!
        // wait
    }
    // process
}
```

**Fix:**
```c
volatile int data_ready = 0;  // FIX: volatile prevents caching
```

---

### 66. BUG — stack overflow from large local array

```c
#include <stdio.h>
void process_image() {
    int pixels[1920 * 1080];    // BUG: ~8MB on stack — guaranteed overflow
    for (int i = 0; i < 1920*1080; i++) pixels[i] = 0;
    printf("done\n");
}
int main() {
    process_image();
    return 0;
}
```

**Fix:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
void process_image() {
    int *pixels = (int*)malloc(1920 * 1080 * sizeof(int));  // FIX: heap
    if (!pixels) return;
    memset(pixels, 0, 1920 * 1080 * sizeof(int));
    printf("done\n");
    free(pixels);
}
int main() {
    process_image();
    return 0;
}
```

---

### 67. BUG — integer overflow in size calculation

```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int rows = 50000, cols = 50000;
    // BUG: rows*cols overflows int before multiply!
    int *matrix = (int*)malloc(rows * cols * sizeof(int));
    if (!matrix) printf("failed\n");
    else { printf("allocated\n"); free(matrix); }
    return 0;
}
```

**Fix:**
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
int main() {
    size_t rows = 50000, cols = 50000;
    size_t total = (size_t)rows * cols * sizeof(int);  // FIX: size_t
    int *matrix = (int*)malloc(total);
    if (!matrix) printf("failed\n");  // will fail — too big, but no overflow
    else { printf("allocated\n"); free(matrix); }
    return 0;
}
```

---

### 68. BUG — use after free in linked list

```c
#include <stdio.h>
#include <stdlib.h>
typedef struct Node { int val; struct Node *next; } Node;

void delete_list(Node *head) {
    while (head) {
        free(head);
        head = head->next;   // BUG: accessing freed memory!
    }
}
```

**Fix:**
```c
void delete_list(Node *head) {
    while (head) {
        Node *next = head->next;   // FIX: save next BEFORE freeing
        free(head);
        head = next;
    }
}
```

---

# PART 8 — MIXED TRICKY QUESTIONS (interview favorites)

---

### 69. What is the output? (printf format)

```c
#include <stdio.h>
int main() {
    printf("%d\n",  1 + 2 * 3);     // A
    printf("%d\n",  7 / 2);          // B
    printf("%f\n",  7 / 2);          // C
    printf("%f\n",  7.0 / 2);        // D
    printf("%d\n",  (int)3.9);       // E
    return 0;
}
```

**Answer:**
```
7        // A: standard precedence
3        // B: integer division — truncates
0.000000 // C: integer 3 passed as float argument — undefined behavior
3.500000 // D: 7.0 forces float division
3        // E: cast truncates toward zero
```

---

### 70. What is the output? (operator precedence trap)

```c
#include <stdio.h>
int main() {
    int a = 5, b = 3;
    printf("%d\n", a & b);     // A
    printf("%d\n", a | b);     // B
    printf("%d\n", a ^ b);     // C
    printf("%d\n", a && b);    // D
    printf("%d\n", a || b);    // E
    printf("%d\n", !a);        // F
    return 0;
}
```

**Answer:**
```
1     // A: 0101 & 0011 = 0001
7     // B: 0101 | 0011 = 0111
6     // C: 0101 ^ 0011 = 0110
1     // D: logical AND — both non-zero, result is 1
1     // E: logical OR  — at least one non-zero, result is 1
0     // F: logical NOT — 5 is truthy, !5 = 0
```

---

### 71. What is the output? (pre vs post increment)

```c
#include <stdio.h>
int main() {
    int i = 5;
    printf("%d\n", i++);   // A
    printf("%d\n", ++i);   // B
    printf("%d\n", i--);   // C
    printf("%d\n", --i);   // D
    return 0;
}
```

**Answer:**
```
5     // A: use 5, then increment → i=6
7     // B: increment i=7, then use
7     // C: use 7, then decrement → i=6
5     // D: decrement i=5, then use
```

---

### 72. What is the output? (short circuit evaluation)

```c
#include <stdio.h>
int side_effect(int x) {
    printf("called with %d\n", x);
    return x;
}
int main() {
    if (side_effect(0) && side_effect(1)) {}  // A
    printf("---\n");
    if (side_effect(1) || side_effect(2)) {}  // B
    return 0;
}
```

**Answer:**
```
called with 0       // A: 0 is false, short-circuit — side_effect(1) NOT called
---
called with 1       // B: 1 is true, short-circuit — side_effect(2) NOT called
```

---

### 73. What is the output? (comma operator)

```c
#include <stdio.h>
int main() {
    int a = (1, 2, 3, 4, 5);   // comma operator
    int b;
    b = 1, 2, 3;                // assignment has lower precedence
    printf("a=%d b=%d\n", a, b);
    return 0;
}
```

**Answer:** `a=5 b=1`
**Why:** Comma operator evaluates left to right and returns the rightmost value. `a = (1,2,3,4,5)` → `a=5`. For `b`: `=` has higher precedence than `,`, so it parses as `(b=1), 2, 3` → `b=1`.

---

### 74. What is the output? (ternary nesting)

```c
#include <stdio.h>
int main() {
    int x = 5;
    printf("%s\n", x > 3 ? x > 7 ? "big" : "medium" : "small");
    return 0;
}
```

**Answer:** `medium`
**Why:** `x>3` is true → evaluate `x>7` → false → return `"medium"`.

---

### 75. Tricky sizeof questions

```c
#include <stdio.h>
int main() {
    printf("%zu\n", sizeof(char));           // A
    printf("%zu\n", sizeof(char*));          // B
    printf("%zu\n", sizeof("hello"));        // C
    printf("%zu\n", sizeof(int[5]));         // D
    printf("%zu\n", sizeof(void));           // E — what happens?
    return 0;
}
```

**Answer:**
```
1     // A: always 1
8     // B: pointer size (64-bit)
6     // C: 5 chars + null terminator
20    // D: 5 * sizeof(int)
      // E: sizeof(void) is 1 in GCC (extension), illegal in standard C
```

---

### 76. Find the bug — printf format mismatch

```c
#include <stdio.h>
int main() {
    int   x = 65;
    float f = 3.14f;
    printf("%f\n", x);    // BUG A
    printf("%d\n", f);    // BUG B
    printf("%c\n", x);    // is this a bug?
    return 0;
}
```

**Answer:**
- A: `%f` expects a double but gets an int — undefined behavior (likely prints 0.000000)
- B: `%d` expects an int but gets a float — undefined behavior
- C: `%c` with int 65 is valid — prints `A` (ASCII 65)

**Fix:** Always match format specifier to type. Use `%d` for int, `%f` for float/double, `%c` for char.

---

### 77. BUG — scanf buffer overflow

```c
#include <stdio.h>
int main() {
    char name[10];
    scanf("%s", name);    // BUG: no length limit
    printf("Hello %s\n", name);
    return 0;
}
```

**Fix:**
```c
#include <stdio.h>
int main() {
    char name[10];
    scanf("%9s", name);    // FIX: limit to 9 chars + \0
    printf("Hello %s\n", name);
    return 0;
}
```

---

### 78. TRICKY — what is the value of i after this loop?

```c
#include <stdio.h>
int main() {
    int i;
    for (i = 0; i < 10; i++) {
        if (i == 5) break;
    }
    printf("i = %d\n", i);
    return 0;
}
```

**Answer:** `i = 5`
**Why:** `break` exits the loop immediately without running `i++` again. `i` retains its value at the time of `break`.

---

### 79. TRICKY — global vs local scope

```c
#include <stdio.h>
int x = 100;

void func() {
    int x = 200;           // shadows global x
    printf("%d\n", x);    // A: 200
    {
        int x = 300;       // shadows local x
        printf("%d\n", x); // B: 300
    }
    printf("%d\n", x);    // C: 200 — inner x gone
}
int main() {
    func();
    printf("%d\n", x);    // D: 100 — global x unchanged
    return 0;
}
```

**Answer:** `200` `300` `200` `100`

---

### 80. TRICKY — memcmp vs strcmp

```c
#include <stdio.h>
#include <string.h>
int main() {
    char a[] = "Hello\0World";  // contains embedded null
    char b[] = "Hello\0Earth";

    printf("strcmp:  %d\n", strcmp(a, b));           // A
    printf("memcmp:  %d\n", memcmp(a, b, 12));       // B
    printf("memcmp2: %d\n", memcmp(a, b, 6));        // C
    return 0;
}
```

**Answer:**
```
strcmp:  0    // A: strcmp stops at first \0 — sees "Hello" == "Hello"
memcmp:  <0  // B: memcmp compares all 12 bytes — 'W' vs 'E', W > E so negative? actually 'W'=87>'E'=69 so positive
memcmp2: 0    // C: first 6 bytes are identical (Hello\0)
```
**Lesson:** `strcmp` is not safe for binary data with embedded nulls. Use `memcmp` for binary comparison.

---

# PART 9 — EMBEDDED-SPECIFIC INTERVIEW QUESTIONS

---

### 81. Write a safe register read-modify-write

```c
#include <stdint.h>
#define GPIOA_ODR  (*(volatile uint32_t*)0x40020014)
#define PIN5_BIT   5

void pin5_set()    { GPIOA_ODR |=  (1U << PIN5_BIT); }
void pin5_clear()  { GPIOA_ODR &= ~(1U << PIN5_BIT); }
void pin5_toggle() { GPIOA_ODR ^=  (1U << PIN5_BIT); }
int  pin5_read()   { return (GPIOA_ODR >> PIN5_BIT) & 1; }

int main() {
    pin5_set();
    pin5_toggle();
    pin5_clear();
    return 0;
}
```

---

### 82. Why must ISR variables be volatile?

```c
#include <stdint.h>
#include <stdio.h>

volatile uint8_t uart_byte;      // shared with ISR
volatile int     rx_ready = 0;

void UART_RX_IRQHandler(void) {
    uart_byte = *(volatile uint8_t*)0x40004804; // read UART data reg
    rx_ready = 1;
}

void main_loop(void) {
    while (!rx_ready);           // without volatile: optimized to infinite loop
    printf("Got: 0x%02X\n", uart_byte);
    rx_ready = 0;
}

int main() {
    // In real embedded, interrupts fire here
    // Simulated:
    uart_byte = 0xAB;
    rx_ready  = 1;
    main_loop();
    return 0;
}
```

---

### 83. Circular buffer — embedded classic

```c
#include <stdio.h>
#include <stdint.h>
#define BUF_SIZE 8

typedef struct {
    uint8_t buf[BUF_SIZE];
    uint8_t head;  // write index
    uint8_t tail;  // read index
    uint8_t count;
} RingBuf;

int rb_push(RingBuf *rb, uint8_t byte) {
    if (rb->count == BUF_SIZE) return -1;  // full
    rb->buf[rb->head] = byte;
    rb->head = (rb->head + 1) % BUF_SIZE;
    rb->count++;
    return 0;
}
int rb_pop(RingBuf *rb, uint8_t *byte) {
    if (rb->count == 0) return -1;          // empty
    *byte = rb->buf[rb->tail];
    rb->tail = (rb->tail + 1) % BUF_SIZE;
    rb->count--;
    return 0;
}
int main() {
    RingBuf rb = {0};
    rb_push(&rb, 0xAA);
    rb_push(&rb, 0xBB);
    rb_push(&rb, 0xCC);

    uint8_t b;
    while (rb_pop(&rb, &b) == 0)
        printf("0x%02X\n", b);   // 0xAA 0xBB 0xCC
    return 0;
}
```

---

### 84. BUG — non-atomic flag in multi-core (no mutex)

```c
// BUG: non-atomic shared flag between two cores or threads
int shared_flag = 0;

// Core 0:
void core0() {
    shared_flag = 1;   // BUG: not atomic — may tear on some architectures
}
// Core 1:
void core1() {
    if (shared_flag) { /* process */ }
}
```

**Fix:**
```c
#include <stdatomic.h>
atomic_int shared_flag = 0;

void core0() { atomic_store(&shared_flag, 1); }
void core1() { if (atomic_load(&shared_flag)) { /* process */ } }
```

---

### 85. Endianness conversion — common in protocol parsing

```c
#include <stdio.h>
#include <stdint.h>

// Convert 32-bit value between little and big endian
uint32_t swap32(uint32_t val) {
    return ((val & 0xFF000000) >> 24) |
           ((val & 0x00FF0000) >>  8) |
           ((val & 0x0000FF00) <<  8) |
           ((val & 0x000000FF) << 24);
}
int main() {
    uint32_t le = 0x12345678;          // little endian value
    uint32_t be = swap32(le);
    printf("LE: 0x%08X\n", le);        // 0x12345678
    printf("BE: 0x%08X\n", be);        // 0x78563412
    return 0;
}
```

---

### 86. BUG — interrupt not re-entrant (missed the volatile + atomic pattern)

```c
// UART ISR — fills a buffer
#define BUF_SIZE 64
static uint8_t rx_buf[BUF_SIZE];
static int     rx_idx = 0;     // BUG: no volatile, no bounds check

void UART_ISR(void) {
    rx_buf[rx_idx] = read_uart();   // BUG: rx_idx may overflow!
    rx_idx++;
}
```

**Fix:**
```c
static volatile uint8_t rx_buf[BUF_SIZE];
static volatile int     rx_idx = 0;

void UART_ISR(void) {
    if (rx_idx < BUF_SIZE) {             // FIX: bounds check
        rx_buf[rx_idx++] = read_uart();
    }
    // else: buffer full — drop or set error flag
}
```

---

### 87. What does __attribute__((packed)) do and when is it dangerous?

```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>

// Network packet — must match wire format exactly
typedef struct __attribute__((packed)) {
    uint8_t  version;
    uint16_t length;
    uint32_t src_ip;
    uint32_t dst_ip;
} IPHeader;   // exactly 10 bytes — no padding

int main() {
    printf("Size: %zu\n", sizeof(IPHeader));  // 10

    uint8_t raw[] = {0x45, 0x00, 0x28, 0xC0, 0xA8, 0x01, 0x01, 0xC0, 0xA8, 0x01, 0x64};
    IPHeader *hdr = (IPHeader*)raw;

    printf("Version: %d\n", hdr->version);
    // WARNING: accessing hdr->length on ARM without byte-copy is UB
    // because the field is at offset 1 — not 2-byte aligned

    uint16_t len;
    memcpy(&len, &hdr->length, sizeof(len));  // safe copy
    printf("Length: %d\n", len);
    return 0;
}
```

---

# PART 10 — PREDICT THE OUTPUT (mixed rapid-fire)

---

### 88.
```c
#include <stdio.h>
int main() {
    int a = 10, b = 20;
    printf("%d\n", a == 10 ? b++ : b--);
    printf("%d\n", b);
    return 0;
}
```
**Answer:** `20` then `21`. Condition true → `b++` (post-increment: return 20, then b=21).

---

### 89.
```c
#include <stdio.h>
int main() {
    int x = 10;
    if (x = 5) printf("true\n");
    else        printf("false\n");
    printf("x = %d\n", x);
    return 0;
}
```
**Answer:** `true` then `x = 5`. `x = 5` is assignment (not comparison), assigns 5, which is truthy.

---

### 90.
```c
#include <stdio.h>
int main() {
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (j == 1) break;
            printf("%d%d ", i, j);
        }
    }
    return 0;
}
```
**Answer:** `00 10 20` — `break` only exits the inner loop.

---

### 91.
```c
#include <stdio.h>
int main() {
    int i = 0;
    while (i++ < 3) printf("%d ", i);
    return 0;
}
```
**Answer:** `1 2 3` — `i++` post-increments, so by the time `printf` runs, `i` is already incremented.

---

### 92.
```c
#include <stdio.h>
int f(int x) { return x > 0 ? x + f(x-1) : 0; }
int main() { printf("%d\n", f(4)); return 0; }
```
**Answer:** `10` — `f(4)` = 4+3+2+1+0 = 10.

---

### 93.
```c
#include <stdio.h>
int main() {
    char c = 255;
    if (c == 255) printf("equal\n");
    else           printf("not equal\n");
    return 0;
}
```
**Answer:** `not equal` on most systems.
**Why:** `char` may be signed (implementation-defined). Signed char with value 255 overflows to -1. `-1 != 255`. Use `unsigned char` for values > 127.

---

### 94.
```c
#include <stdio.h>
int main() {
    int arr[] = {1, 2, 3, 4, 5};
    int *p = arr + 5;        // one past end — valid pointer
    printf("%d\n", p - arr); // pointer difference
    // printf("%d\n", *p);   // would be UB — don't dereference
    return 0;
}
```
**Answer:** `5` — pointer difference is in elements.

---

### 95.
```c
#include <stdio.h>
int main() {
    int x = 0;
    x = x++;   // undefined behavior
    printf("%d\n", x);
    return 0;
}
```
**Answer:** Undefined behavior — modifying `x` and using its value without a sequence point between them. Never do this. Different compilers give 0 or 1.

---

### 96.
```c
#include <stdio.h>
int main() {
    printf("%d\n", sizeof('A'));
    return 0;
}
```
**Answer:** `4` (not 1!)
**Why:** In C (not C++), character literals like `'A'` are of type `int`, not `char`. So `sizeof('A')` = `sizeof(int)` = 4.

---

### 97.
```c
#include <stdio.h>
int main() {
    int a = 5, b = 10, c = 15;
    int result = a < b ? b < c ? c : b : a;
    printf("%d\n", result);
    return 0;
}
```
**Answer:** `15` — ternary is right-associative: `a<b` → true → evaluate `b<c` → true → return `c` = 15.

---

### 98. BUG — classic swap function that doesn't work

```c
#include <stdio.h>
void swap(int a, int b) {    // BUG: passed by value
    int temp = a;
    a = b;
    b = temp;
}
int main() {
    int x = 5, y = 10;
    swap(x, y);
    printf("x=%d y=%d\n", x, y);   // still 5 and 10!
    return 0;
}
```

**Fix:**
```c
#include <stdio.h>
void swap(int *a, int *b) {  // FIX: pass by pointer
    int temp = *a;
    *a = *b;
    *b = temp;
}
int main() {
    int x = 5, y = 10;
    swap(&x, &y);
    printf("x=%d y=%d\n", x, y);   // x=10 y=5
    return 0;
}
```

---

### 99. BUG — integer division loses precision

```c
#include <stdio.h>
int main() {
    int total = 7, count = 2;
    float avg = total / count;   // BUG: integer division happens first
    printf("%.2f\n", avg);       // 3.00, not 3.50
    return 0;
}
```

**Fix:**
```c
float avg = (float)total / count;   // FIX: cast before division
printf("%.2f\n", avg);              // 3.50
```

---

### 100. Final boss — what does this whole program print?

```c
#include <stdio.h>
#include <string.h>

int global = 10;

int func(int x) {
    static int call_count = 0;
    call_count++;
    global += x;
    return call_count;
}

int main() {
    int a = func(5);
    int b = func(3);
    int c = func(2);

    printf("a=%d b=%d c=%d\n", a, b, c);
    printf("global=%d\n", global);

    char str[] = "Hello World";
    char *p = strchr(str, ' ');
    if (p) *p = '\0';
    printf("%s\n", str);

    return 0;
}
```

**Answer:**
```
a=1 b=2 c=3
global=20
Hello
```
**Walkthrough:**
- `func(5)`: call_count=1, global=15, returns 1
- `func(3)`: call_count=2, global=18, returns 2
- `func(2)`: call_count=3, global=20, returns 3
- `strchr` finds the space, replaces with `\0` — `printf` stops there → "Hello"

---

*End of C Interview Preparation Guide — 100 questions covering all major interview scenarios.*
