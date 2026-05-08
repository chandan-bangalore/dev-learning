# C Theory — 150 Interview Questions with Answers and Code Examples

> Source: embeddedshiksha.com — Helping Embedded System Engineers to Clear Interviews

---

# Section 1: Pointers (Questions 1–30)

---

### Q1. What is a pointer in C?

A pointer is a variable that stores the **memory address** of another variable. Instead of holding a value directly, it holds the location where the value lives.

```c
#include <stdio.h>
int main() {
    int x = 10;
    int *p = &x;          // p stores address of x
    printf("Value of x: %d\n", x);       // 10
    printf("Address of x: %p\n", &x);    // e.g. 0x7fff5abc
    printf("Value of p: %p\n", p);       // same address
    printf("Value at p: %d\n", *p);      // 10 (dereferencing)
    return 0;
}
```

---

### Q2. What is the difference between pointer and reference?

| Feature | Pointer | Reference (C++ only) |
|---|---|---|
| Can be NULL | Yes | No |
| Can be reassigned | Yes | No |
| Needs dereferencing | Yes (`*p`) | No (transparent) |
| Has own address | Yes | No |

In C, references don't exist — only pointers. In embedded C, we always use pointers.

```c
int x = 5, y = 10;
int *p = &x;
p = &y;     // pointer reassigned to y — legal
*p = 20;    // y is now 20
```

---

### Q3. Explain pointer arithmetic.

When you add/subtract from a pointer, it moves by **multiples of the data type size**, not by raw bytes.

```c
#include <stdio.h>
int main() {
    int arr[] = {10, 20, 30, 40};
    int *p = arr;
    printf("%d\n", *p);      // 10
    p++;                      // moves 4 bytes forward (sizeof int)
    printf("%d\n", *p);      // 20
    p += 2;                   // moves 8 bytes forward
    printf("%d\n", *p);      // 40
    printf("Diff: %ld\n", p - arr);  // 3 (elements, not bytes)
    return 0;
}
```

---

### Q4. What happens when you increment a pointer?

The pointer moves forward by `sizeof(data_type)` bytes — NOT by 1 byte (unless it's a `char*`).

```c
int    *ip = (int*)100;    ip++;  // ip = 104 (int = 4 bytes)
char   *cp = (char*)100;   cp++;  // cp = 101 (char = 1 byte)
double *dp = (double*)100; dp++;  // dp = 108 (double = 8 bytes)
```

---

### Q5. Difference between `int *p` and `int **p`.

- `int *p` — pointer to an integer (one level of indirection)
- `int **p` — pointer to a pointer to an integer (two levels)

```c
#include <stdio.h>
int main() {
    int x = 42;
    int *p = &x;      // p points to x
    int **pp = &p;    // pp points to p

    printf("%d\n", x);    // 42
    printf("%d\n", *p);   // 42
    printf("%d\n", **pp); // 42

    **pp = 100;            // changes x through two levels
    printf("%d\n", x);    // 100
    return 0;
}
```

---

### Q6. What is a NULL pointer?

A NULL pointer is a pointer that points to **nothing** — it holds the value 0 (or `NULL`). It is used as a safe "empty" state for pointers. Dereferencing NULL causes a segmentation fault.

```c
#include <stdio.h>
int main() {
    int *p = NULL;

    if (p == NULL) {
        printf("Pointer is NULL — safe, do not dereference\n");
    } else {
        printf("%d\n", *p);  // only dereference if not NULL
    }
    return 0;
}
```

---

### Q7. What is a dangling pointer?

A dangling pointer is a pointer that points to **memory that has been freed or gone out of scope**. Accessing it causes undefined behavior — one of the most dangerous bugs in embedded systems.

```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int *p = (int*)malloc(sizeof(int));
    *p = 10;
    free(p);          // memory freed
    // p is now dangling — points to freed memory
    // *p = 20;       // UNDEFINED BEHAVIOR — do NOT do this

    p = NULL;         // fix: always NULL after free
    if (p != NULL) *p = 20;  // safe check
    return 0;
}
```

---

### Q8. What is a void pointer?

A `void*` is a **generic pointer** that can point to any data type. It cannot be dereferenced directly — you must cast it first. Used in `malloc`, `memcpy`, generic data structures.

```c
#include <stdio.h>
int main() {
    int x = 42;
    float f = 3.14f;

    void *p;
    p = &x;
    printf("%d\n", *(int*)p);    // cast to int* first

    p = &f;
    printf("%.2f\n", *(float*)p); // cast to float* first
    return 0;
}
```

---

### Q9. Can you perform arithmetic on a void pointer?

**No** — void pointer arithmetic is illegal in standard C because the compiler doesn't know the size of the type, so it can't calculate how many bytes to move. Some compilers (GCC) allow it as an extension treating void as 1 byte, but it's non-standard.

```c
void *p = (void*)100;
// p++;       // ERROR in standard C — size unknown
// p += 4;    // ERROR

// Fix: cast to known type first
char *cp = (char*)p;
cp++;         // legal — moves 1 byte
```

---

### Q10. What is pointer dereferencing?

Dereferencing means **accessing the value stored at the address** the pointer holds. Done with the `*` operator.

```c
#include <stdio.h>
int main() {
    int x = 99;
    int *p = &x;

    printf("Address: %p\n", p);   // address of x
    printf("Value: %d\n", *p);    // 99 — dereferencing

    *p = 200;                      // modify x through pointer
    printf("x is now: %d\n", x);  // 200
    return 0;
}
```

---

### Q11. What is the difference between pointer and array?

| Feature | Array | Pointer |
|---|---|---|
| Memory | Fixed block allocated | Stores an address |
| Reassignable | No | Yes |
| sizeof | Total array size | Size of pointer (4 or 8 bytes) |
| Arithmetic | Limited | Full arithmetic |

```c
int arr[5] = {1,2,3,4,5};
int *p = arr;

printf("%zu\n", sizeof(arr));  // 20 (5 * 4 bytes)
printf("%zu\n", sizeof(p));    // 8  (pointer size on 64-bit)

p++;    // legal — pointer moves
// arr++; // ILLEGAL — array name is constant
```

---

### Q12. Explain `*(p+1)` vs `p[1]`.

They are **exactly the same**. `p[1]` is just syntactic sugar for `*(p+1)`. The compiler converts array indexing to pointer arithmetic.

```c
#include <stdio.h>
int main() {
    int arr[] = {10, 20, 30};
    int *p = arr;

    printf("%d\n", p[1]);      // 20
    printf("%d\n", *(p+1));    // 20 — identical
    printf("%d\n", arr[2]);    // 30
    printf("%d\n", *(arr+2));  // 30 — identical
    return 0;
}
```

---

### Q13. What is a function pointer?

A function pointer stores the **address of a function**. It allows calling functions indirectly — essential for callbacks, ISR tables, and driver interfaces.

```c
#include <stdio.h>

int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }

int main() {
    int (*fp)(int, int);  // declare function pointer

    fp = add;
    printf("Add: %d\n", fp(5, 3));   // 8

    fp = sub;
    printf("Sub: %d\n", fp(5, 3));   // 2
    return 0;
}
```

---

### Q14. How do you pass a pointer to a function?

Pass the address of a variable using `&`. The function receives a pointer parameter and can modify the original variable through it.

```c
#include <stdio.h>

void double_it(int *p) {
    *p = *p * 2;  // modify original through pointer
}

int main() {
    int x = 5;
    double_it(&x);
    printf("x = %d\n", x);  // 10
    return 0;
}
```

---

### Q15. Explain pointer to structure.

You can have a pointer point to a struct. Use `->` operator (arrow) to access members through a pointer.

```c
#include <stdio.h>

typedef struct {
    int id;
    char name[20];
} Student;

int main() {
    Student s = {1, "Alice"};
    Student *p = &s;

    printf("ID: %d\n", p->id);        // arrow operator
    printf("Name: %s\n", p->name);
    // p->id is same as (*p).id
    return 0;
}
```

---

### Q16. What is pointer aliasing?

Pointer aliasing happens when **two pointers point to the same memory location**. Changes through one pointer affect the other. This can confuse compiler optimizations.

```c
#include <stdio.h>
int main() {
    int x = 10;
    int *p1 = &x;
    int *p2 = &x;   // both point to same location — aliasing

    *p1 = 20;
    printf("%d\n", *p2);  // 20 — changed through p1, visible via p2
    return 0;
}
```

---

### Q17. What is a wild pointer?

A wild pointer is a pointer that has **not been initialized** and contains a garbage address. Dereferencing it causes unpredictable behavior or crash.

```c
int *p;          // wild pointer — garbage address
// *p = 10;     // DANGEROUS — writing to unknown memory

// Fix: always initialize
int *p2 = NULL;  // safe null pointer
int x = 5;
int *p3 = &x;   // initialized to valid address
```

---

### Q18. Difference between `const int *p` and `int * const p`.

| Declaration | Pointer changeable? | Value changeable? |
|---|---|---|
| `const int *p` | Yes | No |
| `int * const p` | No | Yes |
| `const int * const p` | No | No |

```c
int x = 10, y = 20;

const int *p1 = &x;   // pointer to const int
// *p1 = 30;          // ERROR — can't change value
p1 = &y;              // OK — can change pointer

int * const p2 = &x;  // const pointer to int
*p2 = 30;             // OK — can change value
// p2 = &y;           // ERROR — can't change pointer
```

---

### Q19. What is double pointer used for?

Double pointer (`**`) is used to:
1. Modify a pointer inside a function (pass pointer by pointer)
2. Implement 2D dynamic arrays
3. Array of strings

```c
#include <stdio.h>
#include <stdlib.h>

void allocate(int **pp) {
    *pp = (int*)malloc(sizeof(int));  // modify the pointer
    **pp = 42;
}

int main() {
    int *p = NULL;
    allocate(&p);            // pass address of pointer
    printf("%d\n", *p);     // 42
    free(p);
    return 0;
}
```

---

### Q20. What happens if you dereference NULL?

It causes a **segmentation fault** (on Linux/desktop) or **hard fault** (on ARM Cortex-M). The program crashes because address 0 is either unmapped or protected.

```c
int *p = NULL;
// *p = 10;   // SEGFAULT — address 0 is invalid

// Always check before dereferencing
if (p != NULL) {
    *p = 10;
} else {
    printf("Cannot dereference NULL pointer\n");
}
```

---

### Q21. Explain pointer to pointer example.

```c
#include <stdio.h>
int main() {
    int   x  = 100;
    int  *p  = &x;    // p  holds address of x
    int **pp = &p;    // pp holds address of p

    printf("x   = %d\n",  x);    // 100
    printf("*p  = %d\n",  *p);   // 100
    printf("**pp= %d\n",  **pp); // 100

    **pp = 999;                   // change x through pp
    printf("x   = %d\n",  x);    // 999
    return 0;
}
```

---

### Q22. How are pointers used in dynamic memory allocation?

`malloc/calloc` return a `void*` pointer to the allocated heap memory. You must store this in a pointer variable and free it when done.

```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int n = 5;
    int *arr = (int*)malloc(n * sizeof(int));  // allocate array on heap

    if (arr == NULL) { printf("malloc failed\n"); return 1; }

    for (int i = 0; i < n; i++) arr[i] = i * 10;
    for (int i = 0; i < n; i++) printf("%d ", arr[i]);  // 0 10 20 30 40

    free(arr);    // must free — else memory leak
    arr = NULL;
    return 0;
}
```

---

### Q23. What is pointer casting?

Converting a pointer from one type to another. Common in embedded systems for accessing hardware registers.

```c
#include <stdio.h>
int main() {
    int x = 0x41424344;
    char *cp = (char*)&x;    // cast int* to char*

    // Access individual bytes of the integer
    for (int i = 0; i < 4; i++) {
        printf("byte[%d] = 0x%02X\n", i, (unsigned char)cp[i]);
    }
    // Output depends on endianness
    return 0;
}
```

---

### Q24. What is pointer comparison?

Pointers can be compared using `==`, `!=`, `<`, `>` etc. Meaningful only when comparing pointers into the **same array/object**.

```c
#include <stdio.h>
int main() {
    int arr[] = {1, 2, 3, 4, 5};
    int *start = arr;
    int *end   = arr + 5;
    int *p     = arr;

    while (p < end) {          // pointer comparison
        printf("%d ", *p++);
    }
    printf("\n");

    printf("Same? %d\n", start == arr);  // 1 (yes)
    return 0;
}
```

---

### Q25. What is pointer subtraction?

Subtracting two pointers gives the **number of elements** between them (not bytes). Only valid for pointers into the same array.

```c
#include <stdio.h>
int main() {
    int arr[] = {10, 20, 30, 40, 50};
    int *p1 = &arr[1];
    int *p2 = &arr[4];

    ptrdiff_t diff = p2 - p1;
    printf("Elements between: %td\n", diff);  // 3
    return 0;
}
```

---

### Q26. Can two pointers point to same location?

Yes. This is called **aliasing**. Both pointers refer to the same memory — modifying through one is visible through the other.

```c
int x = 5;
int *p1 = &x;
int *p2 = &x;   // both point to x

*p1 = 100;
printf("%d\n", *p2);  // 100 — same location
printf("Same? %d\n", p1 == p2);  // 1 (yes)
```

---

### Q27. What is pointer alignment?

Alignment means a pointer's address must be a **multiple of the data type's size**. Misaligned access can cause hardware faults on some CPUs.

```c
#include <stdio.h>
#include <stdint.h>
int main() {
    char buf[8] = {0};

    // Aligned access — address divisible by 4
    uint32_t *p = (uint32_t*)(buf);     // address % 4 == 0 — OK
    *p = 0xDEADBEEF;

    // Misaligned — address NOT divisible by 4
    // uint32_t *q = (uint32_t*)(buf+1); // may crash on ARM!

    printf("Value: 0x%X\n", *p);
    return 0;
}
```

---

### Q28. How does pointer arithmetic depend on data type?

Each increment moves the pointer by `sizeof(type)` bytes — so arithmetic is always type-aware.

```c
#include <stdio.h>
int main() {
    char   c_arr[4]; char   *cp = c_arr;
    int    i_arr[4]; int    *ip = i_arr;
    double d_arr[4]; double *dp = d_arr;

    printf("char   step: %ld bytes\n", (char*)(cp+1) - (char*)cp); // 1
    printf("int    step: %ld bytes\n", (char*)(ip+1) - (char*)ip); // 4
    printf("double step: %ld bytes\n", (char*)(dp+1) - (char*)dp); // 8
    return 0;
}
```

---

### Q29. What is pointer overflow?

Pointer overflow occurs when pointer arithmetic goes **beyond the valid range of the array** or allocated memory. It leads to undefined behavior.

```c
int arr[5] = {1,2,3,4,5};
int *p = arr;

for (int i = 0; i <= 5; i++) {  // BUG: i <= 5, not i < 5
    printf("%d\n", *p);          // at i=5, reads beyond array — OVERFLOW
    p++;
}
// Fix: use i < 5
```

---

### Q30. How to debug pointer bugs?

Use these techniques and tools:

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    int *p = NULL;

    // Technique 1: Always check NULL before dereference
    if (p == NULL) { printf("NULL pointer — skip\n"); }

    // Technique 2: Print address to check range
    int arr[5];
    int *ptr = arr;
    printf("Array start: %p\n", (void*)arr);
    printf("Current ptr: %p\n", (void*)ptr);

    // Technique 3: NULL after free to prevent dangling
    int *q = (int*)malloc(4);
    free(q);
    q = NULL;

    // Tools: valgrind, AddressSanitizer (-fsanitize=address)
    return 0;
}
```

---

# Section 2: Memory Management (Questions 31–55)

---

### Q31. What is stack memory?

Stack is a region of memory for **local variables and function call frames**. It grows and shrinks automatically as functions are called and return. It is fast but limited in size.

```c
void foo() {
    int x = 10;    // on stack — created when foo() called
    int y = 20;    // on stack
    // x and y automatically destroyed when foo() returns
}
int main() {
    foo();
    // x and y no longer exist here
    return 0;
}
```

---

### Q32. What is heap memory?

Heap is a region for **dynamic memory allocation**. You manually allocate with `malloc` and free with `free`. It persists until explicitly freed. Larger than stack but slower to access.

```c
#include <stdlib.h>
#include <stdio.h>
int main() {
    int *p = (int*)malloc(100 * sizeof(int));  // on heap
    if (!p) return 1;

    p[0] = 42;
    printf("%d\n", p[0]);  // 42

    free(p);   // must manually free
    p = NULL;
    return 0;
}
```

---

### Q33. Difference between stack and heap?

| Feature | Stack | Heap |
|---|---|---|
| Allocation | Automatic | Manual (malloc/free) |
| Size | Small (few KB–MB) | Large (limited by RAM) |
| Speed | Very fast | Slower |
| Management | Compiler | Programmer |
| Fragmentation | No | Yes |
| Lifetime | Function scope | Until freed |

---

### Q34. What is memory leak?

A memory leak occurs when dynamically allocated memory is **never freed**, consuming RAM permanently until the program ends (or system crashes in embedded).

```c
#include <stdlib.h>
void leaky_function() {
    int *p = (int*)malloc(100);
    // ... use p ...
    // FORGOT to call free(p) — memory leaked!
}

void safe_function() {
    int *p = (int*)malloc(100);
    if (!p) return;
    // ... use p ...
    free(p);    // always free
    p = NULL;
}
```

---

### Q35. What does malloc() do?

`malloc(size)` allocates `size` bytes on the heap and returns a `void*` pointer. Memory is **uninitialized** (contains garbage). Returns NULL on failure.

```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int *p = (int*)malloc(5 * sizeof(int));
    if (p == NULL) { printf("malloc failed\n"); return 1; }

    // memory is uninitialized — garbage values
    for (int i = 0; i < 5; i++) p[i] = i;
    for (int i = 0; i < 5; i++) printf("%d ", p[i]);

    free(p); p = NULL;
    return 0;
}
```

---

### Q36. What does calloc() do?

`calloc(n, size)` allocates memory for `n` elements of `size` bytes each and **initializes all bytes to zero**. Safer than malloc for arrays.

```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int *p = (int*)calloc(5, sizeof(int));
    if (!p) return 1;

    for (int i = 0; i < 5; i++)
        printf("%d ", p[i]);   // 0 0 0 0 0 — all zeros!

    free(p); p = NULL;
    return 0;
}
```

---

### Q37. Difference between malloc and calloc?

| Feature | malloc | calloc |
|---|---|---|
| Arguments | 1 (total bytes) | 2 (count, element size) |
| Initialization | No (garbage) | Yes (zeros) |
| Speed | Slightly faster | Slightly slower (zeroing) |
| Use case | General | Arrays where 0-init needed |

```c
int *a = (int*)malloc(5 * sizeof(int));   // garbage values
int *b = (int*)calloc(5, sizeof(int));    // all zeros
```

---

### Q38. What does realloc() do?

`realloc(ptr, new_size)` resizes a previously allocated memory block. May move the block to a new location. Old data is preserved up to the smaller of old/new size.

```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int *p = (int*)malloc(3 * sizeof(int));
    p[0]=1; p[1]=2; p[2]=3;

    p = (int*)realloc(p, 5 * sizeof(int));  // grow to 5
    if (!p) return 1;

    p[3]=4; p[4]=5;
    for (int i = 0; i < 5; i++) printf("%d ", p[i]);  // 1 2 3 4 5

    free(p); p = NULL;
    return 0;
}
```

---

### Q39. What happens if malloc fails?

`malloc` returns `NULL`. In embedded systems this is critical — **always check the return value** before using the pointer.

```c
#include <stdlib.h>
#include <stdio.h>
int main() {
    // Try to allocate very large amount
    int *p = (int*)malloc(1000000000 * sizeof(int));

    if (p == NULL) {
        printf("malloc failed — handle error!\n");
        return -1;   // or use static fallback buffer
    }
    // use p only if not NULL
    free(p);
    return 0;
}
```

---

### Q40. How do you free allocated memory?

Use `free(ptr)` with the **same pointer** returned by malloc/calloc/realloc. Always set to NULL after freeing.

```c
#include <stdlib.h>
int main() {
    int *p = (int*)malloc(10 * sizeof(int));
    if (!p) return 1;

    // use p...

    free(p);    // release memory back to heap
    p = NULL;   // prevent dangling pointer

    // free(p); // double free on NULL is safe (no-op)
    return 0;
}
```

---

### Q41. What happens if you free memory twice?

**Double free** is undefined behavior — it corrupts the heap data structures and can cause crashes or security vulnerabilities.

```c
int *p = (int*)malloc(4);
free(p);
// free(p);  // DOUBLE FREE — heap corruption!

// Fix: set NULL after free
p = NULL;
free(p);    // free(NULL) is safe — does nothing
```

---

### Q42. What is memory fragmentation?

Fragmentation happens when the heap has enough total free memory but **not enough contiguous free memory** to satisfy an allocation request.

```
Heap after several alloc/free cycles:
[FREE 10B][USED 20B][FREE 8B][USED 15B][FREE 10B]

Total free = 28 bytes
But malloc(25) FAILS — no single block of 25 bytes!
This is fragmentation.
```

In embedded systems, avoid repeated malloc/free — use memory pools instead.

---

### Q43. What is a segmentation fault?

A segfault occurs when a program tries to access a **memory address it is not allowed to access** — NULL dereference, out-of-bounds, use-after-free, etc.

```c
// Causes of segfault:
int *p = NULL;
*p = 10;              // 1. NULL dereference

int arr[5];
arr[10] = 5;          // 2. Out of bounds

int *q = (int*)malloc(4);
free(q);
*q = 99;              // 3. Use after free
```

---

### Q44. Explain static memory allocation.

Static allocation happens at **compile time** — arrays, global variables, static variables. Size is fixed and known before the program runs.

```c
#include <stdio.h>

int global_arr[100];             // static — data/BSS segment
static int file_arr[50];         // static — limited to this file

void foo() {
    static int count = 0;        // static local — persists across calls
    int local_arr[20];           // stack — not static
    count++;
    printf("Called %d times\n", count);
}

int main() { foo(); foo(); foo(); return 0; }  // prints 1, 2, 3
```

---

### Q45. Explain dynamic memory allocation.

Dynamic allocation happens at **runtime** using malloc/calloc/realloc. Size can be determined during execution. Must be manually freed.

```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int n;
    printf("How many elements? ");
    scanf("%d", &n);                        // size known at runtime

    int *arr = (int*)malloc(n * sizeof(int));  // dynamic allocation
    if (!arr) return 1;

    for (int i = 0; i < n; i++) arr[i] = i * 2;
    for (int i = 0; i < n; i++) printf("%d ", arr[i]);

    free(arr); arr = NULL;
    return 0;
}
```

---

### Q46. What happens when stack overflows?

Stack overflow occurs when the stack grows beyond its limit — typically from deep recursion or very large local arrays. Results in a crash or hard fault.

```c
// Stack overflow from infinite recursion:
void recurse() {
    int big_array[1000];  // 4KB on stack each call
    recurse();            // never returns — stack fills up!
}

// Stack overflow from large local array:
void foo() {
    int huge[1000000];    // ~4MB on stack — likely overflow!
    // Fix: use malloc instead for large data
}
```

---

### Q47. What is memory alignment?

Memory alignment means data is stored at an address that is a **multiple of its size**. CPUs access aligned data faster; some require it (ARM may fault on misaligned access).

```c
#include <stdio.h>
#include <stdint.h>
typedef struct {
    char  a;     // 1 byte at offset 0
                 // 3 bytes padding
    int   b;     // 4 bytes at offset 4 (aligned to 4)
    char  c;     // 1 byte at offset 8
                 // 3 bytes padding
} Aligned;

int main() {
    printf("Size: %zu\n", sizeof(Aligned));  // 12, not 6
    return 0;
}
```

---

### Q48. What is padding in structures?

The compiler inserts **invisible padding bytes** between struct members to ensure each member starts at its natural alignment boundary.

```c
#include <stdio.h>
struct Padded {
    char  a;    // 1 byte  [offset 0]
    // 3 bytes padding
    int   b;    // 4 bytes [offset 4]
    char  c;    // 1 byte  [offset 8]
    // 3 bytes padding
};              // total: 12 bytes

struct NoPad {
    int   b;    // 4 bytes [offset 0]
    char  a;    // 1 byte  [offset 4]
    char  c;    // 1 byte  [offset 5]
    // 2 bytes padding
};              // total: 8 bytes — reordering saves space!

int main() {
    printf("%zu\n", sizeof(struct Padded)); // 12
    printf("%zu\n", sizeof(struct NoPad));  // 8
    return 0;
}
```

---

### Q49. How does compiler allocate local variables?

Local variables are allocated on the **stack** by adjusting the stack pointer. The compiler calculates total space needed and reserves it at function entry.

```c
void foo() {
    // Compiler does: SP -= sizeof(int) + sizeof(float) + sizeof(char)
    int   x = 10;    // stack
    float f = 3.14f; // stack
    char  c = 'A';   // stack
    // All freed when function returns: SP restored
}
```

---

### Q50. What is global memory?

Global variables are allocated in the **data segment** (initialized) or **BSS segment** (uninitialized) and persist for the entire program lifetime.

```c
#include <stdio.h>

int initialized = 42;      // data segment — initialized globals
int uninitialized;         // BSS segment — zero-initialized

void modify() {
    initialized = 100;     // visible everywhere
}

int main() {
    modify();
    printf("%d\n", initialized);   // 100 — changed by modify()
    printf("%d\n", uninitialized); // 0 — zero-initialized
    return 0;
}
```

---

### Q51. What are static variables?

A `static` variable inside a function **retains its value** between function calls. It is initialized only once and lives in the data/BSS segment.

```c
#include <stdio.h>
void counter() {
    static int count = 0;  // initialized once, persists
    count++;
    printf("Count: %d\n", count);
}
int main() {
    counter();  // Count: 1
    counter();  // Count: 2
    counter();  // Count: 3
    return 0;
}
```

---

### Q52. What is BSS segment?

BSS (Block Started by Symbol) holds **uninitialized global and static variables**. The OS zero-initializes this segment at program start. It doesn't occupy space in the executable file.

```c
int a;              // BSS — uninitialized global (gets value 0)
static int b;       // BSS — uninitialized static (gets value 0)
int c = 5;          // DATA segment — initialized global

// In embedded: BSS is zeroed by startup code (crt0/startup.s)
// This is why global variables are 0 by default in C
```

---

### Q53. What is data segment?

The data segment holds **initialized global and static variables**. Their initial values are stored in the executable file and loaded into RAM at startup.

```c
int x = 100;           // data segment — value 100 in executable
static float pi = 3.14; // data segment

void foo() {
    static int id = 42; // data segment — even though inside function
}
// Contrast: local variables go on stack, not data segment
```

---

### Q54. What is memory corruption?

Memory corruption occurs when a program **writes to memory it shouldn't**, overwriting other variables, function pointers, or return addresses.

```c
#include <stdio.h>
int main() {
    int arr[5] = {0};
    int flag = 1;

    // Buffer overflow — corrupts 'flag'
    for (int i = 0; i <= 5; i++) {  // one too many!
        arr[i] = 0xFF;               // arr[5] writes into 'flag'
    }

    printf("flag = %d\n", flag);  // may be 0xFF — corrupted!
    return 0;
}
```

---

### Q55. How to detect memory leaks?

Use tools and best practices:

```c
// 1. Always match every malloc with a free
// 2. Set pointer to NULL after free
// 3. Use Valgrind: valgrind --leak-check=full ./program
// 4. Use AddressSanitizer: compile with -fsanitize=address

#include <stdlib.h>
void safe_alloc() {
    int *p = (int*)malloc(100);
    if (!p) return;
    // ... use p ...
    free(p);    // matched free
    p = NULL;
}
// Run: valgrind --leak-check=full ./a.out
// Output: "All heap blocks were freed -- no leaks are possible"
```

---

# Section 3: Bit Manipulation (Questions 56–80)

---

### Q56. What is bit masking?

A bit mask is a pattern used to **select, set, clear, or toggle specific bits** in a value using bitwise operators.

```c
#include <stdio.h>
int main() {
    uint8_t reg = 0b10110101;  // 0xB5

    uint8_t mask = 0b00001111; // lower 4 bits mask

    uint8_t lower = reg & mask;    // extract lower nibble: 0x05
    printf("Lower nibble: 0x%02X\n", lower);  // 0x05
    return 0;
}
```

---

### Q57. How to set a bit?

Use bitwise OR with a mask: `value |= (1 << n)` sets bit n to 1 without affecting others.

```c
#include <stdio.h>
int main() {
    uint8_t reg = 0b00000000;

    reg |= (1 << 3);   // set bit 3
    printf("0x%02X\n", reg);  // 0x08 = 0b00001000

    reg |= (1 << 0) | (1 << 7);  // set bits 0 and 7
    printf("0x%02X\n", reg);  // 0x89
    return 0;
}
```

---

### Q58. How to clear a bit?

Use bitwise AND with the complement: `value &= ~(1 << n)` clears bit n to 0.

```c
#include <stdio.h>
int main() {
    uint8_t reg = 0b11111111;  // all bits set

    reg &= ~(1 << 4);    // clear bit 4
    printf("0x%02X\n", reg);  // 0xEF = 0b11101111

    reg &= ~((1<<2)|(1<<6));  // clear bits 2 and 6
    printf("0x%02X\n", reg);  // 0xAB
    return 0;
}
```

---

### Q59. How to toggle a bit?

Use bitwise XOR: `value ^= (1 << n)` flips bit n — if it was 1 it becomes 0, and vice versa.

```c
#include <stdio.h>
int main() {
    uint8_t reg = 0b10101010;

    reg ^= (1 << 1);   // toggle bit 1
    printf("0x%02X\n", reg);  // 0b10101000

    reg ^= (1 << 1);   // toggle again — back to original
    printf("0x%02X\n", reg);  // 0b10101010
    return 0;
}
```

---

### Q60. How to check if a bit is set?

Use bitwise AND and check if result is non-zero: `(value >> n) & 1` or `value & (1 << n)`.

```c
#include <stdio.h>
int main() {
    uint8_t reg = 0b10110100;

    int n = 2;
    if ((reg >> n) & 1) {
        printf("Bit %d is SET\n", n);
    } else {
        printf("Bit %d is CLEAR\n", n);
    }

    // Alternative:
    if (reg & (1 << 4)) printf("Bit 4 is SET\n");
    return 0;
}
```

---

### Q61. What is bitwise AND?

AND (`&`) returns 1 only when **both** corresponding bits are 1. Used for masking (extracting) bits.

```c
  1010 1100
& 0000 1111
-----------
  0000 1100   ← lower 4 bits extracted

uint8_t a = 0xAC, mask = 0x0F;
printf("0x%02X\n", a & mask);  // 0x0C
```

---

### Q62. What is bitwise OR?

OR (`|`) returns 1 when **at least one** corresponding bit is 1. Used for setting bits.

```c
  1010 0000
| 0000 1111
-----------
  1010 1111   ← lower 4 bits set

uint8_t a = 0xA0;
printf("0x%02X\n", a | 0x0F);  // 0xAF
```

---

### Q63. What is bitwise XOR?

XOR (`^`) returns 1 when bits are **different**. Used for toggling, swap, finding duplicates.

```c
  1010 1100
^ 0000 1111
-----------
  1010 0011   ← lower 4 bits toggled

// XOR swap — no temp variable needed:
int a = 5, b = 3;
a ^= b;  b ^= a;  a ^= b;
printf("a=%d b=%d\n", a, b);  // a=3 b=5
```

---

### Q64. What is bitwise NOT?

NOT (`~`) flips **all bits** — 0 becomes 1, 1 becomes 0.

```c
#include <stdio.h>
int main() {
    uint8_t a = 0b10110101;  // 0xB5
    uint8_t b = ~a;           // 0b01001010 = 0x4A

    printf("~0x%02X = 0x%02X\n", a, b);  // ~0xB5 = 0x4A
    return 0;
}
```

---

### Q65. What is left shift operator?

`<<` shifts bits left by n positions. Equivalent to multiplying by 2^n. Zeros fill the right.

```c
int x = 1;
printf("%d\n", x << 0);  // 1  (2^0)
printf("%d\n", x << 1);  // 2  (2^1)
printf("%d\n", x << 3);  // 8  (2^3)
printf("%d\n", x << 4);  // 16 (2^4)

// Used to create bit masks:
uint8_t mask = 1 << 5;   // 0b00100000 — bit 5 mask
```

---

### Q66. What is right shift operator?

`>>` shifts bits right by n positions. For unsigned types, zeros fill the left. Equivalent to dividing by 2^n.

```c
int x = 32;
printf("%d\n", x >> 1);  // 16
printf("%d\n", x >> 2);  // 8
printf("%d\n", x >> 5);  // 1

// Extract bit n:
uint8_t reg = 0b10110000;
uint8_t bit5 = (reg >> 5) & 1;  // 1
uint8_t bit4 = (reg >> 4) & 1;  // 1
```

---

### Q67. Difference between logical and arithmetic shift?

| Shift type | Left bits filled with | Used for |
|---|---|---|
| Logical (unsigned) | 0 | unsigned numbers |
| Arithmetic (signed) | sign bit (0 or 1) | signed division |

```c
uint8_t u = 0b10000000;  // 128 unsigned
int8_t  s = 0b10000000;  // -128 signed

// Right shift:
printf("%u\n", u >> 1);  // 64  — logical: fills with 0
printf("%d\n", s >> 1);  // -64 — arithmetic: fills with 1 (sign)
```

---

### Q68. How to count number of set bits?

Use Brian Kernighan's algorithm: repeatedly clear the lowest set bit with `n & (n-1)`.

```c
#include <stdio.h>
int count_set_bits(int n) {
    int count = 0;
    while (n) {
        n &= (n - 1);  // clears lowest set bit
        count++;
    }
    return count;
}
int main() {
    printf("%d\n", count_set_bits(0b10110101));  // 5
    printf("%d\n", count_set_bits(0xFF));         // 8
    return 0;
}
```

---

### Q69. How to check if number is power of 2?

A power of 2 has exactly **one bit set**. Use `n & (n-1) == 0` (and n > 0).

```c
#include <stdio.h>
int is_power_of_2(int n) {
    return (n > 0) && ((n & (n - 1)) == 0);
}
int main() {
    printf("%d\n", is_power_of_2(8));   // 1 (yes: 1000)
    printf("%d\n", is_power_of_2(6));   // 0 (no:  0110)
    printf("%d\n", is_power_of_2(16));  // 1
    return 0;
}
```

---

### Q70. How to swap two numbers using XOR?

XOR swap works because `a XOR a = 0` and `a XOR 0 = a`.

```c
#include <stdio.h>
int main() {
    int a = 10, b = 25;
    printf("Before: a=%d b=%d\n", a, b);

    a ^= b;  // a = a XOR b
    b ^= a;  // b = b XOR (a XOR b) = a
    a ^= b;  // a = (a XOR b) XOR a = b

    printf("After:  a=%d b=%d\n", a, b);  // a=25 b=10
    return 0;
}
```

---

### Q71. How to clear lowest set bit?

Use `n & (n-1)` — this clears the **rightmost** 1 bit.

```c
#include <stdio.h>
int main() {
    int n = 0b10110100;  // 0xB4
    printf("Before: 0x%02X\n", n);     // 0xB4
    n = n & (n - 1);                    // clear lowest set bit
    printf("After:  0x%02X\n", n);     // 0xB0 (cleared bit 2)
    return 0;
}
```

---

### Q72. How to isolate lowest set bit?

Use `n & (-n)` or `n & (~n + 1)` — returns a value with only the lowest set bit.

```c
#include <stdio.h>
int main() {
    int n = 0b10110100;
    int lowest = n & (-n);   // isolate lowest set bit
    printf("Lowest set bit: 0x%02X\n", lowest);  // 0x04 (bit 2)
    return 0;
}
```

---

### Q73. What is bit field in struct?

Bit fields allow you to specify the exact **number of bits** each struct member uses. Ideal for hardware register modeling.

```c
#include <stdio.h>
typedef struct {
    unsigned int enable  : 1;  // 1 bit
    unsigned int mode    : 2;  // 2 bits
    unsigned int speed   : 3;  // 3 bits
    unsigned int reserved: 2;  // 2 bits
} GPIOConfig;                   // total: 8 bits = 1 byte

int main() {
    GPIOConfig cfg = {0};
    cfg.enable = 1;
    cfg.mode   = 2;
    cfg.speed  = 5;
    printf("Size: %zu bytes\n", sizeof(cfg));  // 4 (compiler may pad)
    return 0;
}
```

---

### Q74. What are bit masks used for in embedded systems?

Bit masks configure hardware registers — setting/clearing/reading individual bits that control peripheral behavior.

```c
// ARM Cortex-M GPIO example
#define GPIO_BASE    0x40020000
#define MODER_OFFSET 0x00
#define ODR_OFFSET   0x14

volatile uint32_t *GPIOA_MODER = (uint32_t*)(GPIO_BASE + MODER_OFFSET);
volatile uint32_t *GPIOA_ODR   = (uint32_t*)(GPIO_BASE + ODR_OFFSET);

void led_init() {
    *GPIOA_MODER &= ~(0x3 << (5*2));  // clear bits 10-11
    *GPIOA_MODER |=  (0x1 << (5*2));  // set output mode for pin 5
}
void led_on()  { *GPIOA_ODR |=  (1 << 5); }
void led_off() { *GPIOA_ODR &= ~(1 << 5); }
```

---

### Q75. What is register manipulation?

Directly reading/writing hardware registers using their **memory-mapped addresses** with volatile pointers.

```c
// Always use volatile for hardware registers
#define REG_ADDR 0x40020000
volatile uint32_t *reg = (volatile uint32_t*)REG_ADDR;

*reg = 0x01;           // write to register
uint32_t val = *reg;   // read from register

// Without volatile, compiler may optimize away repeated reads!
```

---

### Q76. How do you write to hardware register?

Cast the register address to a volatile pointer and use the dereference operator to write.

```c
// Enable GPIOA clock on STM32 (example)
#define RCC_AHB1ENR  (*(volatile uint32_t*)0x40023830)
#define GPIOAEN_BIT  0

void enable_gpioa_clock() {
    RCC_AHB1ENR |= (1 << GPIOAEN_BIT);  // set bit 0
}
// volatile ensures the write always happens — not optimized away
```

---

### Q77. What is endianness?

Endianness defines the **byte order** in which multi-byte values are stored in memory.

```
Value: 0x12345678

Big Endian (MSB first):      Little Endian (LSB first):
Addr: 00 01 02 03            Addr: 00 01 02 03
Data: 12 34 56 78            Data: 78 56 34 12
```

---

### Q78. Difference between little endian and big endian?

| Feature | Little Endian | Big Endian |
|---|---|---|
| LSB stored at | Lowest address | Highest address |
| MSB stored at | Highest address | Lowest address |
| Examples | x86, ARM (default) | Network protocols, MIPS |

```c
// x86 is little endian:
uint32_t x = 0x12345678;
uint8_t *p = (uint8_t*)&x;
printf("%02X %02X %02X %02X\n", p[0],p[1],p[2],p[3]);
// Output: 78 56 34 12  ← little endian (LSB first)
```

---

### Q79. How to detect endianness?

Check if the least significant byte is stored at the lowest address.

```c
#include <stdio.h>
int main() {
    uint32_t x = 1;
    uint8_t *p = (uint8_t*)&x;

    if (*p == 1) {
        printf("Little Endian\n");  // LSB at lowest address
    } else {
        printf("Big Endian\n");     // MSB at lowest address
    }
    return 0;
}
```

---

### Q80. Why bit manipulation is important in embedded systems?

In bare-metal embedded programming, every peripheral is controlled through **memory-mapped registers** — each bit has a specific hardware meaning. No library abstracts this away.

```c
// Real embedded example: configure UART on STM32
// Every bit in every register must be set precisely
#define USART2_CR1  (*(volatile uint32_t*)0x40004400)
#define UE_BIT   13  // UART enable
#define TE_BIT    3  // Transmitter enable
#define RE_BIT    2  // Receiver enable

void uart_init() {
    USART2_CR1 |= (1 << TE_BIT);  // enable TX
    USART2_CR1 |= (1 << RE_BIT);  // enable RX
    USART2_CR1 |= (1 << UE_BIT);  // enable UART
}
// Without bit manipulation, embedded programming is impossible
```

---

# Section 4: Structures and Unions (Questions 81–100)

---

### Q81. What is a structure?

A structure is a **user-defined data type** that groups variables of different types under one name.

```c
#include <stdio.h>
typedef struct {
    int   id;
    char  name[20];
    float grade;
} Student;

int main() {
    Student s = {1, "Alice", 95.5f};
    printf("ID: %d, Name: %s, Grade: %.1f\n",
           s.id, s.name, s.grade);
    return 0;
}
```

---

### Q82. What is a union?

A union is like a struct but all members **share the same memory**. Only one member holds a valid value at a time. Size = size of largest member.

```c
#include <stdio.h>
typedef union {
    uint32_t full_word;
    uint16_t half_words[2];
    uint8_t  bytes[4];
} Register;

int main() {
    Register r;
    r.full_word = 0x12345678;
    printf("Full: 0x%08X\n", r.full_word);
    printf("Byte[0]: 0x%02X\n", r.bytes[0]);  // depends on endianness
    return 0;
}
```

---

### Q83. Difference between struct and union?

| Feature | Struct | Union |
|---|---|---|
| Memory | Each member has own | All share same memory |
| Size | Sum of all members + padding | Size of largest member |
| Access | All members valid | Only last written is valid |
| Use | Group related data | Interpret same memory differently |

---

### Q84. What is structure padding?

Padding is extra bytes the compiler inserts to align struct members to their natural boundaries.

```c
struct Padded {
    char  c;   // 1 byte + 3 padding
    int   i;   // 4 bytes
};             // size = 8, not 5

struct Efficient {
    int   i;   // 4 bytes
    char  c;   // 1 byte + 3 padding
};             // size = 8, but better layout for access
```

---

### Q85. What is structure alignment?

Each member is aligned to a boundary equal to its size. The struct itself is aligned to the largest member's alignment.

```c
#include <stdio.h>
struct Example {
    char  a;    // offset 0 (1-byte aligned)
    // 3 bytes padding
    int   b;    // offset 4 (4-byte aligned)
    char  c;    // offset 8 (1-byte aligned)
    // 3 bytes padding
};              // total: 12 bytes

int main() {
    struct Example e;
    printf("Size: %zu\n", sizeof(e));  // 12
    printf("Offset b: %zu\n", offsetof(struct Example, b));  // 4
    return 0;
}
```

---

### Q86. How to access struct members?

Use `.` (dot) operator for struct variables, `->` (arrow) for struct pointers.

```c
typedef struct { int x; int y; } Point;

Point p = {3, 4};
printf("%d %d\n", p.x, p.y);   // dot operator

Point *pp = &p;
printf("%d %d\n", pp->x, pp->y); // arrow operator
// pp->x is same as (*pp).x
```

---

### Q87. What is pointer to struct?

A pointer that holds the address of a struct. Use `->` to access members.

```c
#include <stdio.h>
#include <stdlib.h>
typedef struct { int id; char name[10]; } Node;

int main() {
    Node *n = (Node*)malloc(sizeof(Node));
    n->id = 1;
    strcpy(n->name, "Bob");
    printf("%d %s\n", n->id, n->name);
    free(n);
    return 0;
}
```

---

### Q88. What is nested structure?

A struct that contains another struct as a member.

```c
#include <stdio.h>
typedef struct { float lat; float lon; } GPS;
typedef struct { int id; char name[20]; GPS location; } Device;

int main() {
    Device d = {1, "Sensor1", {12.97f, 77.59f}};
    printf("Device: %s at %.2f, %.2f\n",
           d.name, d.location.lat, d.location.lon);
    return 0;
}
```

---

### Q89. What is bit field struct?

A struct where members are specified in bits — used for hardware register modeling.

```c
typedef struct {
    unsigned int pin_mode  : 2;  // 2 bits: 00=input, 01=output
    unsigned int pin_speed : 2;  // 2 bits: speed setting
    unsigned int pull      : 2;  // 2 bits: pull-up/down
    unsigned int reserved  : 2;  // 2 bits: unused
} PinConfig;                      // 8 bits total
```

---

### Q90. What is packed struct?

A packed struct has **no padding** — compiler packs members tightly. Used for protocol packets where exact byte layout matters.

```c
#include <stdio.h>

typedef struct __attribute__((packed)) {
    uint8_t  header;    // 1 byte
    uint32_t data;      // 4 bytes
    uint8_t  checksum;  // 1 byte
} Packet;               // 6 bytes exactly (not 8 with padding)

int main() {
    printf("Size: %zu\n", sizeof(Packet));  // 6
    return 0;
}
```

---

### Q91. Why use union in embedded systems?

Unions allow **interpreting the same memory in multiple ways** — essential for register access, type punning, and protocol parsing.

```c
typedef union {
    uint32_t raw;          // access full 32-bit register
    struct {
        uint32_t enable : 1;
        uint32_t mode   : 2;
        uint32_t speed  : 3;
        uint32_t unused : 26;
    } bits;                // access individual fields
} ControlReg;

ControlReg reg;
reg.raw = 0;
reg.bits.enable = 1;
reg.bits.speed  = 3;
printf("Raw: 0x%08X\n", reg.raw);
```

---

### Q92. What is anonymous struct?

A struct without a tag name, usually inside a union, whose members are accessed directly.

```c
typedef union {
    uint32_t raw;
    struct {          // anonymous struct — no name needed
        uint8_t byte0;
        uint8_t byte1;
        uint8_t byte2;
        uint8_t byte3;
    };                // members accessed directly as union members
} Word;

Word w;
w.raw = 0x12345678;
printf("byte0 = 0x%02X\n", w.byte0);  // 0x78 on little endian
```

---

### Q93. How much memory does union occupy?

A union occupies memory equal to its **largest member** (plus any alignment padding).

```c
#include <stdio.h>
union Example {
    char  c;     // 1 byte
    int   i;     // 4 bytes
    double d;    // 8 bytes
};

int main() {
    printf("Size: %zu\n", sizeof(union Example));  // 8 (largest = double)
    return 0;
}
```

---

### Q94. Can struct contain function pointer?

Yes — this is the basis of **object-oriented patterns** in C and embedded driver interfaces.

```c
#include <stdio.h>
typedef struct {
    int  value;
    void (*print)(int);      // function pointer member
    int  (*compute)(int, int);
} Calculator;

void print_val(int v) { printf("Value: %d\n", v); }
int  add(int a, int b)  { return a + b; }

int main() {
    Calculator c = {0, print_val, add};
    c.print(42);               // 42
    printf("%d\n", c.compute(3, 4));  // 7
    return 0;
}
```

---

### Q95. What is typedef struct?

`typedef` creates an **alias** for a struct type, so you don't need to write `struct` every time.

```c
// Without typedef:
struct Point { int x; int y; };
struct Point p1;   // must write 'struct'

// With typedef:
typedef struct { int x; int y; } Point;
Point p2;          // no need for 'struct' keyword

// Common in embedded headers:
typedef struct { uint32_t CR1; uint32_t CR2; } UART_TypeDef;
```

---

### Q96. How are structs passed to functions?

By **value** (copy) or by **pointer** (reference). In embedded, always pass by pointer for large structs — avoid copying overhead.

```c
typedef struct { int x; int y; int z; } Vec3;

void by_value(Vec3 v) {
    v.x = 999;  // modifies local copy only
}

void by_pointer(Vec3 *v) {
    v->x = 999;  // modifies original
}

int main() {
    Vec3 v = {1, 2, 3};
    by_value(v);    printf("%d\n", v.x);  // 1   — unchanged
    by_pointer(&v); printf("%d\n", v.x);  // 999 — changed
    return 0;
}
```

---

### Q97. What happens when struct is copied?

A **shallow copy** of all members is made. Pointer members are copied (the pointer value, not what they point to) — both structs share the same pointed-to data.

```c
typedef struct { int x; int *data; } MyStruct;

int val = 100;
MyStruct a = {1, &val};
MyStruct b = a;     // shallow copy

b.x = 99;           // a.x unchanged
*b.data = 42;       // BOTH a.data and b.data point to val!
printf("%d\n", *a.data);  // 42 — affected by b's write!
```

---

### Q98. How to compare structures?

C does not support `==` for structs directly. Compare **member by member** or use `memcmp` (with care regarding padding bytes).

```c
#include <string.h>
#include <stdio.h>
typedef struct { int x; int y; } Point;

int points_equal(Point a, Point b) {
    return (a.x == b.x) && (a.y == b.y);  // member-by-member
}

int main() {
    Point p1 = {3, 4}, p2 = {3, 4}, p3 = {1, 2};
    printf("%d\n", points_equal(p1, p2));  // 1 (equal)
    printf("%d\n", points_equal(p1, p3));  // 0 (not equal)
    return 0;
}
```

---

### Q99. What is flexible array member?

A zero-length (or incomplete) array at the end of a struct, allowing variable-length structs in dynamic allocation.

```c
#include <stdio.h>
#include <stdlib.h>
typedef struct {
    int  length;
    char data[];   // flexible array member — no size specified
} Buffer;

int main() {
    int n = 10;
    Buffer *buf = (Buffer*)malloc(sizeof(Buffer) + n * sizeof(char));
    buf->length = n;
    buf->data[0] = 'A';
    printf("Length: %d, data[0]: %c\n", buf->length, buf->data[0]);
    free(buf);
    return 0;
}
```

---

### Q100. What is memory layout of struct?

Struct members are laid out sequentially in memory with padding for alignment. Use `offsetof` to find exact offsets.

```c
#include <stdio.h>
#include <stddef.h>
typedef struct {
    char  a;   // offset 0
    int   b;   // offset 4 (3 bytes padding after a)
    char  c;   // offset 8
    short d;   // offset 10 (1 byte padding after c)
} MyStruct;    // total: 12 bytes

int main() {
    printf("Size of struct: %zu\n", sizeof(MyStruct));
    printf("Offset of a: %zu\n", offsetof(MyStruct, a));   // 0
    printf("Offset of b: %zu\n", offsetof(MyStruct, b));   // 4
    printf("Offset of c: %zu\n", offsetof(MyStruct, c));   // 8
    printf("Offset of d: %zu\n", offsetof(MyStruct, d));   // 10
    return 0;
}
```

---

# Section 5: Arrays and Strings (Questions 101–120)

---

### Q101. What is array in C?

An array is a **contiguous block of memory** holding elements of the same type, accessed by index.

```c
#include <stdio.h>
int main() {
    int arr[5] = {10, 20, 30, 40, 50};

    for (int i = 0; i < 5; i++) {
        printf("arr[%d] = %d (addr: %p)\n",
               i, arr[i], &arr[i]);
    }
    // Addresses differ by 4 bytes (sizeof int)
    return 0;
}
```

---

### Q102. Difference between array and pointer?

An array name is a **constant pointer** to the first element. Key differences: sizeof, reassignment, and memory ownership.

```c
int arr[5] = {1,2,3,4,5};
int *p = arr;

printf("%zu\n", sizeof(arr));  // 20 — full array size
printf("%zu\n", sizeof(p));    // 8  — just pointer size

p = p + 1;   // legal — pointer can move
// arr = arr + 1;  // ILLEGAL — array name is constant
```

---

### Q103. How arrays passed to functions?

Arrays **decay to a pointer** when passed to functions. The function receives only the address — size information is lost.

```c
#include <stdio.h>
void print_array(int *arr, int size) {  // receives pointer, not array
    printf("sizeof inside function: %zu\n", sizeof(arr));  // 8 (pointer!)
    for (int i = 0; i < size; i++) printf("%d ", arr[i]);
}

int main() {
    int arr[5] = {1,2,3,4,5};
    printf("sizeof in main: %zu\n", sizeof(arr));  // 20
    print_array(arr, 5);
    return 0;
}
```

---

### Q104. What is multidimensional array?

An array of arrays. A 2D array is stored in **row-major order** in memory.

```c
#include <stdio.h>
int main() {
    int matrix[3][3] = {{1,2,3},{4,5,6},{7,8,9}};

    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            printf("%d ", matrix[i][j]);
        }
        printf("\n");
    }
    return 0;
}
```

---

### Q105. What is string in C?

A string is a **null-terminated char array**. The `'\0'` character marks the end of the string.

```c
#include <stdio.h>
int main() {
    char s1[] = "Hello";     // {'H','e','l','l','o','\0'}
    char s2[6] = {'H','e','l','l','o','\0'};

    printf("%s\n", s1);   // Hello
    printf("%zu\n", sizeof(s1));  // 6 (includes \0)
    return 0;
}
```

---

### Q106. What is null terminator?

`'\0'` (ASCII 0) marks the **end of a string**. String functions like `strlen`, `printf("%s")` read until they find `'\0'`.

```c
char s[] = {'H','e','l','l','o','\0'};  // explicit null terminator
printf("%s\n", s);   // Hello

char bad[] = {'H','e','l','l','o'};    // NO null terminator
// printf("%s\n", bad);  // undefined behavior — reads past array!
```

---

### Q107. What is strlen()?

Returns the **number of characters** in a string, not counting the null terminator.

```c
#include <stdio.h>
#include <string.h>
int main() {
    char s[] = "Hello";
    printf("strlen: %zu\n", strlen(s));   // 5
    printf("sizeof: %zu\n", sizeof(s));   // 6 (includes \0)

    // Manual implementation:
    int len = 0;
    char *p = s;
    while (*p++) len++;  // count until \0
    printf("Manual len: %d\n", len);  // 5
    return 0;
}
```

---

### Q108. What is strcpy()?

Copies a string from source to destination, **including the null terminator**. Dangerous if destination is too small.

```c
#include <stdio.h>
#include <string.h>
int main() {
    char src[] = "Hello";
    char dst[10];

    strcpy(dst, src);       // copies "Hello\0" into dst
    printf("%s\n", dst);    // Hello

    // Safer alternative:
    strncpy(dst, src, sizeof(dst) - 1);
    dst[sizeof(dst)-1] = '\0';
    return 0;
}
```

---

### Q109. Difference between strcpy and strncpy?

| Function | Copies n bytes? | Always null-terminates? | Safe? |
|---|---|---|---|
| strcpy | No limit | Yes (copies source \0) | No — overflow risk |
| strncpy | Yes | Not if source >= n | Safer — but add \0 manually |

```c
char dst[5];
strcpy(dst, "Hello World");    // OVERFLOW — "Hello World" > 5
strncpy(dst, "Hello World", 4); dst[4] = '\0';  // "Hell" — safe
```

---

### Q110. What is strcat()?

Appends (concatenates) source string to destination string. Destination must have enough space.

```c
#include <stdio.h>
#include <string.h>
int main() {
    char dest[20] = "Hello";
    char src[]    = " World";

    strcat(dest, src);         // dest = "Hello World"
    printf("%s\n", dest);

    // Safer: strncat
    strncat(dest, "!!!", 3);
    printf("%s\n", dest);      // Hello World!!!
    return 0;
}
```

---

### Q111. What is strcmp()?

Compares two strings lexicographically. Returns 0 if equal, negative if s1 < s2, positive if s1 > s2.

```c
#include <stdio.h>
#include <string.h>
int main() {
    printf("%d\n", strcmp("abc", "abc"));   // 0  (equal)
    printf("%d\n", strcmp("abc", "abd"));   // <0 (a<b at pos 2)
    printf("%d\n", strcmp("abd", "abc"));   // >0

    // Common use — string equality check:
    if (strcmp("hello", "hello") == 0) printf("Strings are equal\n");
    return 0;
}
```

---

### Q112. What happens if string not null terminated?

**Undefined behavior** — string functions keep reading memory past the array until they randomly find a zero byte.

```c
char bad[5] = {'H','e','l','l','o'};  // no \0
// strlen(bad) — reads beyond array, returns garbage length
// printf("%s", bad) — prints garbage after "Hello"
// strcpy with bad as source — copies garbage bytes

// Fix: always null terminate
char good[6] = {'H','e','l','l','o','\0'};
```

---

### Q113. How to reverse string?

Swap characters from both ends moving toward the middle.

```c
#include <stdio.h>
#include <string.h>
void reverse(char *s) {
    int left = 0, right = strlen(s) - 1;
    while (left < right) {
        char tmp = s[left];
        s[left]  = s[right];
        s[right] = tmp;
        left++; right--;
    }
}
int main() {
    char s[] = "Hello";
    reverse(s);
    printf("%s\n", s);  // olleH
    return 0;
}
```

---

### Q114. How to find substring?

Use `strstr()` — returns pointer to first occurrence of substring, or NULL if not found.

```c
#include <stdio.h>
#include <string.h>
int main() {
    char str[] = "Hello World";
    char *pos  = strstr(str, "World");

    if (pos) {
        printf("Found at index: %ld\n", pos - str);  // 6
        printf("Substring: %s\n", pos);               // World
    }
    return 0;
}
```

---

### Q115. How to convert string to integer?

Use `atoi()` for simple cases or `strtol()` for error handling.

```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    char s1[] = "123";
    char s2[] = "456abc";

    int n1 = atoi(s1);   // 123
    int n2 = atoi(s2);   // 456 (stops at non-digit)

    // Better — with error checking:
    char *endptr;
    long val = strtol("789", &endptr, 10);
    printf("%ld\n", val);  // 789

    return 0;
}
```

---

### Q116. What is buffer overflow?

Writing **more data than the buffer can hold**, corrupting adjacent memory. Critical security vulnerability.

```c
char buf[5];
// Buffer overflow:
strcpy(buf, "This string is too long!");  // writes beyond buf[5]

// Fix: always check size
char safe[5];
strncpy(safe, "This string is too long!", sizeof(safe) - 1);
safe[sizeof(safe)-1] = '\0';
printf("%s\n", safe);  // "This"
```

---

### Q117. How to avoid buffer overflow?

Always use size-limited functions and check lengths.

```c
#include <stdio.h>
#include <string.h>
int main() {
    char buf[10];
    const char *src = "Hello World This Is Long";

    // Safe copy:
    strncpy(buf, src, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';  // guarantee null termination

    // Safe input:
    // scanf("%9s", buf);           // limit to 9 chars
    // fgets(buf, sizeof(buf), stdin); // safer than gets()

    printf("%s\n", buf);  // "Hello Wor"
    return 0;
}
```

---

### Q118. How arrays stored in memory?

Arrays are stored **contiguously** — elements are adjacent in memory with no gaps.

```c
#include <stdio.h>
int main() {
    int arr[5] = {10, 20, 30, 40, 50};

    for (int i = 0; i < 5; i++) {
        printf("arr[%d] = %d, addr = %p\n", i, arr[i], &arr[i]);
    }
    // Each address is exactly 4 bytes apart (sizeof int)
    // arr[0] at 0x...00
    // arr[1] at 0x...04
    // arr[2] at 0x...08
    return 0;
}
```

---

### Q119. What is pointer to array?

A pointer that points to an **entire array** as a unit, not just the first element.

```c
#include <stdio.h>
int main() {
    int arr[5] = {1, 2, 3, 4, 5};

    int (*p)[5] = &arr;    // pointer to array of 5 ints

    printf("%d\n", (*p)[0]);   // 1
    printf("%d\n", (*p)[4]);   // 5

    // p+1 moves past the entire 5-element array (20 bytes)
    printf("Size of step: %ld bytes\n", (char*)(p+1) - (char*)p);  // 20
    return 0;
}
```

---

### Q120. What is array of pointers?

An array where each element is a pointer. Commonly used for arrays of strings.

```c
#include <stdio.h>
int main() {
    const char *names[] = {"Alice", "Bob", "Charlie", "Dave"};
    int n = 4;

    for (int i = 0; i < n; i++) {
        printf("%s\n", names[i]);
    }

    // Each names[i] is a char* pointing to a string literal
    // names itself is an array of char* pointers
    return 0;
}
```

---

# Section 6: Functions and Function Pointers (Questions 121–135)

---

### Q121. What is function in C?

A function is a **named block of code** that performs a specific task. It can accept inputs (parameters) and return an output.

```c
#include <stdio.h>

int add(int a, int b) {   // return type, name, parameters
    return a + b;          // return value
}

int main() {
    int result = add(3, 5);
    printf("Result: %d\n", result);  // 8
    return 0;
}
```

---

### Q122. What is function prototype?

A declaration of a function **before its definition** — tells the compiler the function's name, return type, and parameter types.

```c
// Prototype (declaration) — at top of file or in header
int multiply(int a, int b);

int main() {
    printf("%d\n", multiply(4, 5));  // 20 — compiler knows signature
    return 0;
}

// Definition — can come after main
int multiply(int a, int b) {
    return a * b;
}
```

---

### Q123. What is recursion?

A function that **calls itself**. Must have a base case to stop, otherwise it causes stack overflow.

```c
#include <stdio.h>
int factorial(int n) {
    if (n <= 1) return 1;         // base case — stops recursion
    return n * factorial(n - 1);  // recursive call
}
int main() {
    printf("5! = %d\n", factorial(5));  // 120
    return 0;
}
// Call stack: factorial(5) → 4 → 3 → 2 → 1 → unwinds
```

---

### Q124. What is inline function?

A hint to the compiler to **expand the function body at call site** instead of making a real function call. Reduces call overhead in tight loops.

```c
#include <stdio.h>

static inline int square(int x) {
    return x * x;
}

int main() {
    int a = square(5);   // compiler may replace with: int a = 5 * 5;
    printf("%d\n", a);   // 25
    return 0;
}
// Benefit in embedded: no call/return overhead in ISRs or tight loops
```

---

### Q125. What is static function?

A function with `static` keyword is **visible only within the file** it's defined in. Prevents name conflicts across multiple files in large projects.

```c
// file: uart.c
static void uart_helper(void) {  // private to uart.c
    // internal helper — not visible to other files
}

void uart_send(char c) {    // public — visible to other files
    uart_helper();
    // ...
}
```

---

### Q126. What is function pointer?

A variable that holds the **address of a function**, allowing functions to be called indirectly.

```c
#include <stdio.h>
void greet_en(void) { printf("Hello!\n"); }
void greet_de(void) { printf("Hallo!\n"); }

int main() {
    void (*greet)(void);   // function pointer declaration

    greet = greet_en;
    greet();               // Hello!

    greet = greet_de;
    greet();               // Hallo!
    return 0;
}
```

---

### Q127. How to declare function pointer?

Syntax: `return_type (*pointer_name)(param_types);`

```c
// Function: int add(int, int)
int (*fp)(int, int);       // pointer to function taking 2 ints

// Function: void callback(void)
void (*cb)(void);

// Using typedef (cleaner):
typedef int (*MathFunc)(int, int);
MathFunc operation;

int add(int a, int b) { return a + b; }
operation = add;
printf("%d\n", operation(3, 4));  // 7
```

---

### Q128. How to call function using pointer?

Two equivalent ways: direct dereference `(*fp)(args)` or implicit call `fp(args)`.

```c
#include <stdio.h>
int multiply(int a, int b) { return a * b; }

int main() {
    int (*fp)(int, int) = multiply;

    int r1 = (*fp)(3, 4);   // explicit dereference — 12
    int r2 = fp(3, 4);      // implicit call — also 12

    printf("%d %d\n", r1, r2);
    return 0;
}
```

---

### Q129. What are callbacks?

A callback is a function passed as a parameter (via function pointer) to be **called later** — when an event occurs or operation completes.

```c
#include <stdio.h>
typedef void (*Callback)(int result);

void async_compute(int x, Callback on_done) {
    int result = x * x;   // do computation
    on_done(result);       // call the callback with result
}

void my_handler(int result) {
    printf("Computation done! Result = %d\n", result);
}

int main() {
    async_compute(7, my_handler);  // passes my_handler as callback
    return 0;
}
```

---

### Q130. Where are function pointers used?

Everywhere in embedded systems — ISR tables, driver layers, RTOS task registration, state machines.

```c
// RTOS task registration
typedef void (*TaskFunc)(void*);
void register_task(TaskFunc task, void *arg, int priority);

// Driver interface
typedef struct {
    int (*init)(void);
    int (*read)(uint8_t*, int);
    int (*write)(const uint8_t*, int);
} DriverOps;

// State machine
typedef void (*StateFn)(void);
StateFn states[] = { state_idle, state_running, state_error };
states[current_state]();  // call current state's function
```

---

### Q131. How function pointer used in drivers?

Drivers expose a **uniform interface** through function pointers — the application doesn't need to know which specific hardware is underneath.

```c
typedef struct {
    void (*init)(uint32_t baud);
    void (*send)(uint8_t byte);
    uint8_t (*recv)(void);
} UART_Driver;

// STM32 specific implementation
void stm32_uart_init(uint32_t baud) { /* STM32 code */ }
void stm32_uart_send(uint8_t b)     { /* STM32 code */ }

UART_Driver uart = { stm32_uart_init, stm32_uart_send, NULL };
uart.init(115200);   // application calls through interface
```

---

### Q132. What is pointer to function returning pointer?

A function that returns a pointer, accessed through a function pointer.

```c
#include <stdio.h>
// Function that returns int*
int* get_max_ptr(int *a, int *b) {
    return (*a > *b) ? a : b;
}

int main() {
    int (*fp)(int*, int*);   // Wrong — doesn't match return type

    // Correct:
    int* (*fp2)(int*, int*) = get_max_ptr;

    int x = 10, y = 20;
    int *max = fp2(&x, &y);
    printf("Max = %d\n", *max);  // 20
    return 0;
}
```

---

### Q133. Can function return pointer?

Yes — functions can return pointers. Be careful not to return a pointer to a local variable.

```c
#include <stdio.h>
#include <stdlib.h>

// Safe: return pointer to heap memory
int* create_array(int size) {
    return (int*)malloc(size * sizeof(int));
}

// DANGEROUS: return pointer to local variable
int* bad_function() {
    int local = 42;
    return &local;   // local destroyed after return — dangling!
}

int main() {
    int *arr = create_array(5);
    arr[0] = 99;
    printf("%d\n", arr[0]);  // 99
    free(arr);
    return 0;
}
```

---

### Q134. What happens when function returns local variable pointer?

The local variable is destroyed when the function returns. The pointer is **dangling** — accessing it is undefined behavior.

```c
int* dangerous() {
    int x = 100;    // on stack
    return &x;      // stack frame destroyed after return!
}

int main() {
    int *p = dangerous();
    printf("%d\n", *p);  // UNDEFINED — may print 100, 0, or crash
    return 0;
}

// Fix: use static, heap, or global
int* safe_static() {
    static int x = 100;  // static — not destroyed on return
    return &x;
}
```

---

### Q135. Difference between macro and function?

| Feature | Macro | Function |
|---|---|---|
| Evaluation | Preprocessor (text substitution) | Compiler (actual code) |
| Type checking | None | Yes |
| Overhead | Zero (inline) | Call/return overhead |
| Debugging | Harder | Easier |
| Side effects | Dangerous with expressions | Safe |

```c
#define SQUARE_MACRO(x)  ((x) * (x))
int square_func(int x) { return x * x; }

int n = 3;
int a = SQUARE_MACRO(n++);  // (3++)*(3++) = 3*4 = 12 — SIDE EFFECT BUG!
int b = square_func(n);     // clean — n passed once
printf("a=%d b=%d n=%d\n", a, b, n);  // a=12 b=25 n=5
```

---

# Section 7: Debugging and Runtime Concepts (Questions 136–150)

---

### Q136. What is segmentation fault?

A crash that occurs when a program tries to access **memory it is not permitted to access** — NULL dereference, out-of-bounds, use-after-free.

```c
// Common causes:
int *p = NULL;   *p = 10;           // 1. NULL dereference
int arr[3];      arr[10] = 5;       // 2. Out of bounds
int *q = malloc(4); free(q); *q=1;  // 3. Use after free

char *s = "literal"; s[0] = 'X';   // 4. Write to read-only memory
```

---

### Q137. What is undefined behavior?

Code that the C standard says has **no defined outcome** — may work on one compiler/platform and crash on another. Dangerous in embedded.

```c
// Examples of undefined behavior:
int x = INT_MAX + 1;         // signed overflow
int arr[5]; int y = arr[5];  // out of bounds read
int *p; *p = 10;             // uninitialized pointer
int a = 5; int b = a++ + a++;  // multiple modification without sequence point

// UB is NOT an error you can catch — it may silently corrupt
```

---

### Q138. What is race condition?

When two threads/ISRs access the **same shared variable** without synchronization, producing unpredictable results depending on timing.

```c
// Global shared variable
volatile int counter = 0;

// Thread 1:              Thread 2:
// read counter (=0)      read counter (=0)
// increment to 1         increment to 1
// write 1                write 1
// Result: counter = 1, should be 2!

// Fix: use atomic or mutex
#include <stdatomic.h>
atomic_int safe_counter = 0;
atomic_fetch_add(&safe_counter, 1);  // atomic — no race
```

---

### Q139. What is deadlock?

Deadlock occurs when two or more threads are **waiting for each other** to release a resource — none can proceed.

```c
// Deadlock scenario:
// Thread 1: locks mutex_A, then tries to lock mutex_B
// Thread 2: locks mutex_B, then tries to lock mutex_A
// Both wait forever!

// Thread 1              Thread 2
// lock(A)               lock(B)
// ...waiting for B...   ...waiting for A...  ← DEADLOCK

// Fix: always lock mutexes in the SAME ORDER in all threads
// Thread 1: lock(A) then lock(B)
// Thread 2: lock(A) then lock(B)  ← consistent order, no deadlock
```

---

### Q140. What is volatile keyword?

`volatile` tells the compiler that a variable may be **changed by external sources** (hardware, ISR, another thread) and must never be cached in a register.

```c
volatile uint32_t *UART_STATUS = (volatile uint32_t*)0x40004400;

// WITHOUT volatile:
while (*UART_STATUS == 0) {}  // compiler may optimize to: while(1) {}

// WITH volatile:
while (*UART_STATUS == 0) {}  // always re-reads the register

// Rule: always use volatile for hardware registers and ISR-shared variables
```

---

### Q141. When should volatile be used?

Use `volatile` for:
1. Memory-mapped hardware registers
2. Variables modified by ISRs
3. Variables shared between threads (with mutex too)
4. Variables affected by `setjmp/longjmp`

```c
// 1. Hardware register
volatile uint32_t *GPIO_IDR = (volatile uint32_t*)0x40020010;

// 2. ISR-shared variable
volatile int data_ready = 0;
void UART_ISR(void) { data_ready = 1; }  // set by ISR
void main_loop(void) { while (!data_ready) {}; }  // wait in main

// 3. Delay loop (prevent optimization)
volatile int i;
for (i = 0; i < 10000; i++);  // delay — not optimized away
```

---

### Q142. What is const keyword?

`const` declares a variable as **read-only** — its value cannot be changed after initialization.

```c
#include <stdio.h>
int main() {
    const int MAX = 100;
    // MAX = 200;  // ERROR — cannot modify const

    // const pointer to const int (read-only register)
    const volatile uint32_t *STATUS_REG = (uint32_t*)0x40020010;
    uint32_t val = *STATUS_REG;  // read OK
    // *STATUS_REG = 5;          // ERROR — const data

    printf("MAX = %d\n", MAX);
    return 0;
}
```

---

### Q143. Difference between const and volatile?

| Keyword | Meaning | Who changes it? |
|---|---|---|
| `const` | Program cannot write it | Set once at init |
| `volatile` | Hardware/ISR can change it | External to program flow |
| `const volatile` | Program can't write, hardware can change | Read-only hardware status register |

```c
// Read-only status register — hardware updates it, CPU only reads
const volatile uint32_t *STATUS = (uint32_t*)0x40004400;
uint32_t s = *STATUS;  // OK — read
// *STATUS = 1;        // ERROR — const prevents write
```

---

### Q144. What is infinite loop bug?

An unintended loop that never exits — caused by wrong condition, missing update, or compiler optimizing away a loop variable.

```c
// Bug 1: wrong condition
int i = 0;
while (i >= 0) {  // always true for positive i!
    i++;
}

// Bug 2: missing volatile — compiler may cache value
int flag = 0;
// Another thread sets flag = 1
while (flag == 0) {}  // may loop forever — flag cached in register

// Fix:
volatile int vflag = 0;
while (vflag == 0) {}  // always re-reads flag
```

---

### Q145. What is stack overflow?

Stack overflow happens when the call stack exceeds its limit — from deep recursion or large local arrays.

```c
// Cause 1: Infinite recursion
void recurse() { recurse(); }  // stack fills up → crash

// Cause 2: Huge local array
void foo() {
    int huge[100000];    // ~400KB on stack — likely overflow!
    // Fix: use static or malloc
}

// Detection in embedded: stack canary
// Place known value at stack boundary, check it periodically
#define STACK_CANARY 0xDEADBEEF
uint32_t stack_guard = STACK_CANARY;
if (stack_guard != STACK_CANARY) { /* stack overflow detected */ }
```

---

### Q146. How to debug memory corruption?

```c
// Techniques:
// 1. Use AddressSanitizer: gcc -fsanitize=address prog.c
// 2. Use Valgrind: valgrind --tool=memcheck ./prog
// 3. Add boundary markers (guard bytes)
// 4. Check array bounds carefully

// Guard byte example:
uint8_t guard1 = 0xAA;
uint8_t buf[10];
uint8_t guard2 = 0xAA;

// after operations:
if (guard1 != 0xAA || guard2 != 0xAA) {
    printf("Memory corruption detected!\n");
}
```

---

### Q147. How to debug pointer issues?

```c
#include <stdio.h>
#include <stdlib.h>

// 1. Always print pointer value when suspicious
int x = 42;
int *p = &x;
printf("p = %p, *p = %d\n", (void*)p, *p);

// 2. Always NULL-check before dereference
if (p != NULL) { printf("%d\n", *p); }

// 3. NULL after free
int *q = malloc(4);
free(q);
q = NULL;

// 4. Use static analysis: cppcheck, clang-tidy
// 5. Compile with warnings: gcc -Wall -Wextra -Werror
```

---

### Q148. What tools help debugging C programs?

| Tool | Purpose | Usage |
|---|---|---|
| GDB | Interactive debugger | `gdb ./prog` |
| Valgrind | Memory leak/error detection | `valgrind ./prog` |
| AddressSanitizer | Buffer overflow, use-after-free | `-fsanitize=address` |
| UBSan | Undefined behavior | `-fsanitize=undefined` |
| cppcheck | Static analysis | `cppcheck src/` |
| JTAG/SWD | On-chip embedded debugging | OpenOCD + GDB |

```bash
# Compile with sanitizers:
gcc -g -fsanitize=address,undefined -o prog prog.c

# Run Valgrind:
valgrind --leak-check=full --show-leak-kinds=all ./prog

# GDB:
gdb ./prog
(gdb) break main
(gdb) run
(gdb) print variable_name
(gdb) backtrace
```

---

### Q149. What is core dump?

A core dump is a **snapshot of process memory** at the time of a crash. Used to post-mortem debug crashes without reproducing them.

```c
// Enable core dumps:
// ulimit -c unlimited   (on Linux shell)

// Program that crashes:
int *p = NULL;
*p = 42;  // SIGSEGV — generates core dump file

// Analyze with GDB:
// gdb ./prog core
// (gdb) backtrace  ← shows call stack at crash
// (gdb) print p    ← shows variable values

// In embedded: use JTAG/SWD + OpenOCD for similar analysis
```

---

### Q150. What is static analysis?

Static analysis is examining code for bugs **without running it** — the tool reads source code and reports potential issues like null dereference, buffer overflows, uninitialized variables.

```c
// Example of code that static analysis catches:

int *p = NULL;
if (some_condition) p = malloc(4);
*p = 10;   // static analysis warns: p may be NULL here!

int arr[5];
int x = arr[5];   // static analysis: out-of-bounds read!

// Run cppcheck:
// cppcheck --enable=all --error-exitcode=1 src/

// Run clang-tidy:
// clang-tidy prog.c -- -Wall
```

---

*End of 150 Theory Questions — Master these and you will be ready for any embedded C interview.*
