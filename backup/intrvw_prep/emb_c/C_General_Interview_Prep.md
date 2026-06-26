# General C Interview Prep
### Basic to Intermediate — Any Company Hiring C Developers

---

## How to use this guide
- Each topic has a **concept summary**, **interview questions**, and a **runnable C program**
- Paste programs into [onlinegdb.com](https://onlinegdb.com) → select **C (C11)** → Run
- Try to predict the output *before* running — that is the real practice

---

# Topic 1: Data Types, Sizes & Type Conversions

## Concept summary

C has no guaranteed sizes for `int`, `long` etc. — they depend on the platform and compiler.
Always use `<stdint.h>` fixed-width types (`uint8_t`, `int32_t`, etc.) when size matters.

**Implicit conversions** (integer promotion rules):
- Smaller types (`char`, `short`) are promoted to `int` in expressions
- Mixing signed and unsigned can cause subtle bugs — unsigned "wins"
- Narrowing (assigning a larger type to a smaller one) silently truncates

## Interview questions
1. What is the size of `int` on a 32-bit system? Is it guaranteed?
2. What is the difference between `signed char` and `unsigned char`?
3. What happens when you assign `-1` to an `unsigned int`?
4. What is integer overflow? Is it defined behavior for signed types?
5. Why should you use `uint32_t` instead of `unsigned int` in portable code?

## Answers
1. Typically 4 bytes, but **not guaranteed** — the C standard only requires `int` be at least 16 bits; size is implementation-defined.
2. `signed char` holds −128 to 127 (high bit is sign); `unsigned char` holds 0 to 255 (high bit is value); plain `char` signedness is implementation-defined.
3. Well-defined: wraps modulo 2^32,  so `-1` becomes `UINT_MAX` (4294967295 on 32-bit).
4. Exceeding a type's representable range; **unsigned overflow is defined** (wraps mod 2^n), but **signed overflow is undefined behavior** — compilers may optimize assuming it never occurs.
5. `unsigned int` width is implementation-defined (16/32/64-bit); `uint32_t` from `<stdint.h>` is **exactly 32 bits**, guaranteed — essential for protocols, file formats, and cross-platform code.

## Runnable program

```c
#include <stdio.h>
#include <stdint.h>
#include <limits.h>

int main() {
    printf("=== Data Types & Sizes ===\n\n");

    printf("Platform sizes:\n");
    printf("  sizeof(char)      = %zu byte\n",  sizeof(char));
    printf("  sizeof(short)     = %zu bytes\n", sizeof(short));
    printf("  sizeof(int)       = %zu bytes\n", sizeof(int));
    printf("  sizeof(long)      = %zu bytes\n", sizeof(long));
    printf("  sizeof(long long) = %zu bytes\n", sizeof(long long));
    printf("  sizeof(float)     = %zu bytes\n", sizeof(float));
    printf("  sizeof(double)    = %zu bytes\n", sizeof(double));
    printf("  sizeof(pointer)   = %zu bytes\n\n", sizeof(void*));

    printf("Fixed-width types (always portable):\n");
    printf("  sizeof(uint8_t)  = %zu\n", sizeof(uint8_t));
    printf("  sizeof(uint16_t) = %zu\n", sizeof(uint16_t));
    printf("  sizeof(uint32_t) = %zu\n", sizeof(uint32_t));
    printf("  sizeof(uint64_t) = %zu\n\n", sizeof(uint64_t));

    printf("Implicit conversion traps:\n");

    /* signed vs unsigned comparison */
    int           s = -1;
    unsigned int  u = 1;
    printf("  (int)-1 < (unsigned)1 evaluates to: %s\n",
           (s < (int)u) ? "TRUE (correct)" : "FALSE (trap! -1 became huge uint)");

    unsigned int bad = (unsigned int)s;  /* -1 as unsigned */
    printf("  (unsigned int)(-1) = %u  (0x%X)\n\n", bad, bad);

    /* Overflow */
    uint8_t byte = 255;
    byte++;
    printf("  uint8_t 255 + 1 = %u  (wraps to 0)\n", byte);

    int8_t sbyte = 127;
    sbyte++;
    printf("  int8_t  127 + 1 = %d  (undefined behavior; usually -128 on 2's complement)\n\n", sbyte);

    printf("INT limits:\n");
    printf("  INT_MAX  = %d\n",  INT_MAX);
    printf("  INT_MIN  = %d\n",  INT_MIN);
    printf("  UINT_MAX = %u\n\n", UINT_MAX);

    return 0;
}
```

---

# Topic 2: Pointers — Basics to Intermediate

## Concept summary

Pointers are the most tested topic in C interviews.

- A pointer stores the **address** of a variable
- `*ptr` dereferences (reads the value at that address)
- `&var` gives the address of a variable
- `ptr++` advances by `sizeof(*ptr)` bytes — not 1 byte
- `NULL` pointer dereference = undefined behavior (crash in practice)
- **Pointer to pointer** (`int **pp`) — used when a function needs to modify a pointer

**Common mistakes**:
- Returning address of a local variable (dangling pointer)
- Using a pointer after `free()` (use-after-free)
- Not initializing a pointer before use (wild pointer)

## Interview questions
1. What is the difference between `int *p` and `int p[]` as a function parameter?
2. What is a NULL pointer? What happens if you dereference it?
3. What is a dangling pointer? Give an example.
4. What is the difference between `const int *p` and `int * const p`?
5. Write a function that swaps two integers using pointers.

## Answers
1. `int *p` and `int p[]` are equivalent as function parameters, both representing a pointer to the first element of an array.
2. A NULL pointer points to no valid memory location, and dereferencing it causes undefined behavior (usually a crash).
3. A dangling pointer is a pointer to freed or invalid memory, e.g., `int *p = malloc(sizeof(int)); free(p); *p = 10;`.
4. `const int *p` means the value cannot be changed via the pointer, while `int * const p` means the pointer cannot point elsewhere.
5. `void swap(int *a, int *b) { int temp = *a; *a = *b; *b = temp; }`
## Runnable program

```c
#include <stdio.h>
#include <stdint.h>

/* Swap using pointers — classic interview question */
void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

/* Modifying a pointer from a function requires pointer-to-pointer */
void reset_pointer(int **pp) {
    *pp = NULL;
}

/* const pointer variations */
void const_demo() {
    int x = 10, y = 20;

    const int *p1 = &x;   /* pointer to const int: can't change *p1, can change p1 */
    /* *p1 = 99; */        /* COMPILE ERROR */
    p1 = &y;              /* OK */

    int * const p2 = &x;  /* const pointer to int: can change *p2, can't change p2 */
    *p2 = 99;             /* OK */
    /* p2 = &y; */        /* COMPILE ERROR */

    printf("const int *p1: p1 can move, *p1 is read-only. x=%d\n", x);
    printf("int * const p2: *p2 can change, p2 cannot move. x=%d\n", x);
}

/* Pointer arithmetic */
void pointer_arithmetic() {
    int arr[] = {10, 20, 30, 40, 50};
    int *p = arr;

    printf("\nPointer arithmetic on int array:\n");
    for (int i = 0; i < 5; i++) {
        printf("  p+%d → addr %p, value %d\n", i, (void*)(p+i), *(p+i));
    }
    printf("  Step size: %ld bytes (= sizeof(int))\n",
           (long)((char*)(p+1) - (char*)p));
}

/* Returning pointer to local = DANGEROUS */
int* bad_function() {
    int local = 42;
    return &local;   /* local destroyed after return — dangling pointer! */
}

int main() {
    printf("=== Pointers Demo ===\n\n");

    int a = 5, b = 10;
    printf("Before swap: a=%d, b=%d\n", a, b);
    swap(&a, &b);
    printf("After swap:  a=%d, b=%d\n\n", a, b);

    int val = 100;
    int *p = &val;
    printf("val=%d, &val=%p, p=%p, *p=%d\n\n",
           val, (void*)&val, (void*)p, *p);

    printf("Double pointer (reset to NULL):\n");
    int *ptr = &val;
    printf("  Before reset: ptr = %p\n", (void*)ptr);
    reset_pointer(&ptr);
    printf("  After reset:  ptr = %p\n\n", (void*)ptr);

    const_demo();
    pointer_arithmetic();

    printf("\nDangling pointer warning:\n");
    printf("  bad_function() returns address of a local variable.\n");
    printf("  Dereferencing the result is UNDEFINED BEHAVIOR.\n");
    printf("  Never return &local_variable from a function.\n");

    return 0;
}
```

---

# Topic 3: Arrays and Strings

## Concept summary

- In C, an array name decays to a pointer to its first element in most expressions
- `sizeof(arr)` gives total bytes — but only when `arr` is the actual array, not a pointer
- Strings are null-terminated `char` arrays — `"hello"` is 6 bytes (5 + `'\0'`)
- No bounds checking — writing past the end is undefined behavior (common source of bugs)

**String functions** (`<string.h>`): `strlen`, `strcpy`, `strncpy`, `strcmp`, `strcat`, `memset`, `memcpy`

**`memset` vs `memcpy`**: `memset` fills with a byte value; `memcpy` copies bytes from source to destination.

## Interview questions
1. What is the difference between `char str[] = "hello"` and `char *str = "hello"`?
2. Why is `gets()` dangerous? What should you use instead?
3. What does `sizeof(arr)` return when `arr` is passed to a function?
4. How do you find the length of a string without `strlen`?
5. What is a buffer overflow? Why is it dangerous?

## Answers
1. `char str[] = "hello"` creates a modifiable character array stored in memory, while `char *str = "hello"` points to a string literal that should not be modified.
2. `gets()` is dangerous because it does not check input size and can overflow the buffer; use `fgets()` instead.
3. When `arr` is passed to a function, `sizeof(arr)` returns the size of a pointer, not the full array size. If it's in main(), it return full size of an array.
4. You can find string length without `strlen` by looping until the `'\0'` null terminator is reached and counting characters.
5. A buffer overflow happens when data writes past a buffer’s limit, which can corrupt memory, crash the program, or create security vulnerabilities.

## Runnable program

```c
#include <stdio.h>
#include <string.h>
#include <stdint.h>

/* strlen without library */
size_t my_strlen(const char *s) {
    size_t len = 0;
    while (*s++) len++;
    return len;
}

/* strcpy without library */
char* my_strcpy(char *dst, const char *src) {
    char *start = dst;
    while ((*dst++ = *src++) != '\0');
    return start;
}

/* String reverse in-place */
void reverse_string(char *s) {
    int l = 0, r = (int)strlen(s) - 1;
    while (l < r) {
        char tmp = s[l]; s[l] = s[r]; s[r] = tmp;
        l++; r--;
    }
}

void sizeof_trap(int arr[], int n) {
    /* sizeof(arr) here is sizeof(int*) — pointer, not array! */
    printf("  sizeof inside function = %zu (pointer size, NOT array size)\n", sizeof(arr));
}

int main() {
    printf("=== Arrays & Strings ===\n\n");

    /* Array vs pointer */
    int arr[] = {1, 2, 3, 4, 5};
    printf("sizeof(arr) in main()    = %zu bytes (%zu elements)\n",
           sizeof(arr), sizeof(arr)/sizeof(arr[0]));
    sizeof_trap(arr, 5);

    printf("\nArray decay — arr == &arr[0]: %s\n\n",
           (void*)arr == (void*)&arr[0] ? "TRUE" : "FALSE");

    /* String literal vs char array */
    char str_arr[] = "hello";         /* modifiable copy on stack */
    const char *str_ptr = "hello";    /* points to read-only literal */

    printf("char str_arr[] = \"hello\"\n");
    printf("  sizeof = %zu, strlen = %zu\n", sizeof(str_arr), strlen(str_arr));
    str_arr[0] = 'H';                 /* OK — it's a copy */
    printf("  After str_arr[0]='H': %s\n\n", str_arr);

    printf("const char *str_ptr = \"hello\"\n");
    printf("  sizeof = %zu (pointer!), strlen = %zu\n\n",
           sizeof(str_ptr), strlen(str_ptr));
    /* str_ptr[0] = 'H'; */           /* CRASH — modifying string literal */

    /* my_strlen */
    printf("my_strlen(\"firmware\") = %zu\n", my_strlen("firmware"));

    /* my_strcpy */
    char buf[20];
    my_strcpy(buf, "Qualcomm");
    printf("my_strcpy result: %s\n", buf);

    /* reverse */
    char rev[] = "embedded";
    reverse_string(rev);
    printf("reverse(\"embedded\") = %s\n\n", rev);

    /* memset and memcpy */
    uint8_t data[8];
    memset(data, 0xAB, sizeof(data));
    printf("After memset(0xAB): ");
    for (int i = 0; i < 8; i++) printf("0x%02X ", data[i]);
    printf("\n");

    uint8_t src[] = {1, 2, 3, 4};
    uint8_t dst[4];
    memcpy(dst, src, 4);
    printf("After memcpy: ");
    for (int i = 0; i < 4; i++) printf("%d ", dst[i]);
    printf("\n");

    return 0;
}
```

---

# Topic 4: Functions, Scope & Storage Classes

## Concept summary

**Scope** — where a variable is visible:
- Block scope: inside `{}`
- File scope: outside all functions (global)
- Function prototype scope: parameter names in declarations

**Storage classes**:
| Keyword | Lifetime | Scope | Default init |
|---|---|---|---|
| `auto` (default for locals) | Block | Block | Undefined |
| `static` (local) | Program | Block | Zero |
| `static` (global) | Program | File | Zero |
| `extern` | Program | Program | Zero |
| `register` | Block | Block | Undefined |

**Pass by value vs pass by pointer**: C is always pass-by-value. To modify a variable in the caller, pass its address.

## Interview questions
1. What is the difference between pass-by-value and pass-by-pointer in C?
2. What does a `static` local variable do differently from a regular local?
3. Can a function return a pointer to a local variable? Why or why not?
4. What is `extern` and when do you need it?
5. What is the difference between declaration and definition?

## Answers
1. Pass-by-value copies the variable so changes don’t affect the original, while pass-by-pointer passes the address allowing modification of the original.
2. A static local variable retains its value between function calls, unlike a regular local variable which is reinitialized each time.
3. No, because local variables are destroyed after the function returns, leaving the pointer dangling.
4. `extern` declares a variable defined in another file or scope, allowing it to be shared across multiple files.
5. Declaration tells the compiler about a variable/function’s type, while definition allocates memory or provides the actual implementation.

## Runnable program

```c
#include <stdio.h>

/* Declaration vs definition */
extern int global_counter;   /* declaration — defined below */
int global_counter = 0;      /* definition  */

/* static function — private to this file */
static int clamp(int val, int lo, int hi) {
    if (val < lo) return lo;
    if (val > hi) return hi;
    return val;
}

/* static local — call counter */
int next_id() {
    static int id = 0;    /* initialized once, persists */
    return ++id;
}

/* pass by value — caller's x unchanged */
void increment_val(int x) {
    x++;
    printf("  inside increment_val: x = %d\n", x);
}

/* pass by pointer — caller's x IS changed */
void increment_ptr(int *x) {
    (*x)++;
    printf("  inside increment_ptr: *x = %d\n", *x);
}

/* scope demonstration */
void scope_demo() {
    int x = 1;
    printf("  outer x = %d\n", x);
    {
        int x = 2;   /* new x, shadows outer */
        printf("  inner x = %d\n", x);
    }
    printf("  outer x after block = %d (unchanged)\n", x);
}

int main() {
    printf("=== Functions, Scope & Storage Classes ===\n\n");

    printf("Pass by value vs pointer:\n");
    int x = 10;
    increment_val(x);
    printf("  caller x after increment_val: %d (unchanged)\n\n", x);

    increment_ptr(&x);
    printf("  caller x after increment_ptr: %d (changed)\n\n", x);

    printf("static local (ID generator):\n");
    for (int i = 0; i < 5; i++)
        printf("  id = %d\n", next_id());

    printf("\nclamp(150, 0, 100) = %d\n", clamp(150, 0, 100));
    printf("clamp(-5,  0, 100) = %d\n\n", clamp(-5, 0, 100));

    printf("Scope demo:\n");
    scope_demo();

    printf("\nglobal_counter = %d\n", global_counter);

    return 0;
}
```

---

# Topic 5: Structs, Unions & Enums

## Concept summary

**Struct**: groups related variables. Members accessed with `.` (value) or `->` (pointer).

**Union**: all members share the same memory. Size = size of largest member. Used for type-punning and memory-efficient variants.

**Enum**: named integer constants. Improves readability over `#define` for state machines, error codes, etc.

**Typedef**: creates an alias — `typedef struct {...} MyStruct;` lets you use `MyStruct` without the `struct` keyword.

**Struct padding** (brief — covered more in embedded file): compiler aligns members; use `sizeof` to verify, never assume.

## Interview questions
1. What is the difference between a struct and a union?
2. How do you access struct members through a pointer?
3. What is `typedef` and why is it used with structs?
4. What is the size of a union with a `char` and an `int` member?
5. Write a struct to represent a network packet header.

# Answers
1. A struct gives each member its own memory so all members can hold values at once, while a union shares the same memory among all members so only one member’s value is meaningful at a time.
2. You access struct members through a pointer using the `->` operator, for example `ptr->age`.
3. `typedef` creates a shorter alias for a type, and with structs it avoids repeatedly writing `struct Student s1`, you can write `Student s1`.
4. The size of a union with a `char` and an `int` is usually the size of `int`, because a union’s size is the size of its largest member (possibly with alignment padding).
5. `struct PacketHeader { unsigned short srcPort; unsigned short destPort; unsigned int seqNum; unsigned char flags; };`

## Runnable program

```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>

/* typedef struct — clean usage */
typedef struct {
    uint8_t  src_addr;
    uint8_t  dst_addr;
    uint16_t length;
    uint32_t checksum;
} PacketHeader;

/* Nested struct */
typedef struct {
    PacketHeader header;
    uint8_t      payload[16];
} Packet;

/* Union: same memory, different interpretations */
typedef union {
    uint32_t as_uint32;
    uint8_t  as_bytes[4];
    float    as_float;
} Word32;

/* Enum for state machine */
typedef enum {
    STATE_IDLE    = 0,
    STATE_INIT    = 1,
    STATE_RUNNING = 2,
    STATE_ERROR   = 3,
} SystemState;

const char* state_name(SystemState s) {
    switch(s) {
        case STATE_IDLE:    return "IDLE";
        case STATE_INIT:    return "INIT";
        case STATE_RUNNING: return "RUNNING";
        case STATE_ERROR:   return "ERROR";
        default:            return "UNKNOWN";
    }
}

void print_packet(const Packet *p) {
    printf("  src=%u dst=%u len=%u chk=0x%08X\n",
           p->header.src_addr, p->header.dst_addr,
           p->header.length,   p->header.checksum);
}

int main() {
    printf("=== Structs, Unions & Enums ===\n\n");

    /* Struct init */
    PacketHeader h = { .src_addr = 1, .dst_addr = 2,
                       .length = 64, .checksum = 0xDEADBEEF };
    printf("PacketHeader: src=%u dst=%u len=%u chk=0x%08X\n",
           h.src_addr, h.dst_addr, h.length, h.checksum);
    printf("sizeof(PacketHeader) = %zu bytes\n\n", sizeof(PacketHeader));

    /* Pointer access with -> */
    Packet pkt;
    memset(&pkt, 0, sizeof(pkt));
    pkt.header.src_addr  = 10;
    pkt.header.dst_addr  = 20;
    pkt.header.length    = sizeof(pkt.payload);
    pkt.header.checksum  = 0x12345678;
    printf("Packet via pointer:\n");
    print_packet(&pkt);

    /* Union */
    printf("\nUnion (Word32) — all members share same 4 bytes:\n");
    Word32 w;
    w.as_uint32 = 0x41200000UL;   /* IEEE 754 for 10.0f */
    printf("  as_uint32 = 0x%08X\n", w.as_uint32);
    printf("  as_float  = %.2f\n",   w.as_float);
    printf("  as_bytes  = [0x%02X, 0x%02X, 0x%02X, 0x%02X]\n",
           w.as_bytes[0], w.as_bytes[1], w.as_bytes[2], w.as_bytes[3]);
    printf("  sizeof(Word32) = %zu (size of largest member)\n\n", sizeof(Word32));

    /* Enum state machine */
    printf("State machine:\n");
    SystemState state = STATE_IDLE;
    SystemState transitions[] = { STATE_INIT, STATE_RUNNING, STATE_ERROR, STATE_IDLE };
    printf("  Current: %s\n", state_name(state));
    for (int i = 0; i < 4; i++) {
        state = transitions[i];
        printf("  → %s\n", state_name(state));
    }

    return 0;
}
```

---

# Topic 6: Memory Management (malloc, free, common bugs)

## Concept summary

C has manual memory management — you allocate and must free. The compiler does not help.

**Heap functions**: `malloc(n)` — allocate n bytes; `calloc(n, size)` — allocate and zero; `realloc(ptr, n)` — resize; `free(ptr)` — release.

**Common bugs**:
| Bug | Description |
|---|---|
| Memory leak | `malloc` without `free` |
| Use-after-free | Dereferencing after `free()` |
| Double-free | Calling `free()` twice on same pointer |
| Buffer overflow | Writing past allocated size |
| Null deref | Not checking `malloc` return value |

**Rule**: every `malloc` must have exactly one `free`. After `free`, set pointer to `NULL`.

## Interview questions
1. What does `malloc` return if it fails?
2. What is a memory leak? How do you detect one?
3. What is the difference between `malloc` and `calloc`?
4. What happens if you call `free()` twice on the same pointer?
5. Write a function that creates a dynamic array of N integers and returns it.

## Answers
1. `malloc` returns `NULL` if memory allocation fails.
2. A memory leak occurs when allocated memory is not freed, and it can be detected using tools like Valgrind or by monitoring memory usage.
3. `malloc` allocates uninitialized memory, while `calloc` allocates memory and initializes it to zero.
4. Calling `free()` twice on the same pointer causes undefined behavior, potentially leading to crashes or security issues.
5. 
```
int* createArray(int n) {
    int *arr = (int*) malloc(n * sizeof(int));
    if (arr == NULL) return NULL;
    return arr;
}
```

## Runnable program

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* Safe malloc wrapper — always check return */
void* safe_malloc(size_t n) {
    void *p = malloc(n);
    if (!p) {
        fprintf(stderr, "malloc(%zu) failed!\n", n);
        exit(1);
    }
    return p;
}

/* Dynamic array */
int* create_array(int n, int fill_value) {
    int *arr = (int*)safe_malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) arr[i] = fill_value;
    return arr;   /* caller must free */
}

/* Dynamic string duplication */
char* my_strdup(const char *s) {
    size_t len = strlen(s) + 1;
    char *copy = (char*)safe_malloc(len);
    memcpy(copy, s, len);
    return copy;   /* caller must free */
}

/* calloc vs malloc */
void calloc_demo() {
    printf("malloc (uninitialized):\n");
    int *p1 = (int*)malloc(5 * sizeof(int));
    /* Contents undefined — but let's print anyway (demo only) */
    /* In practice: always initialize before reading */
    for (int i = 0; i < 5; i++) p1[i] = i + 1;  /* initialize explicitly */
    for (int i = 0; i < 5; i++) printf("  p1[%d] = %d\n", i, p1[i]);
    free(p1); p1 = NULL;

    printf("calloc (zero-initialized):\n");
    int *p2 = (int*)calloc(5, sizeof(int));
    for (int i = 0; i < 5; i++) printf("  p2[%d] = %d\n", i, p2[i]);
    free(p2); p2 = NULL;
}

/* realloc — grow a buffer */
void realloc_demo() {
    printf("\nrealloc demo:\n");
    int *arr = (int*)safe_malloc(3 * sizeof(int));
    arr[0] = 1; arr[1] = 2; arr[2] = 3;

    /* Grow to 6 elements */
    arr = (int*)realloc(arr, 6 * sizeof(int));
    if (!arr) { fprintf(stderr, "realloc failed\n"); return; }
    arr[3] = 4; arr[4] = 5; arr[5] = 6;

    printf("  After realloc to 6: ");
    for (int i = 0; i < 6; i++) printf("%d ", arr[i]);
    printf("\n");
    free(arr); arr = NULL;
}

int main() {
    printf("=== Memory Management ===\n\n");

    /* Dynamic array */
    int *arr = create_array(5, 7);
    printf("create_array(5, 7): ");
    for (int i = 0; i < 5; i++) printf("%d ", arr[i]);
    printf("\n");
    free(arr); arr = NULL;

    /* Dynamic string */
    char *s = my_strdup("firmware_dev");
    printf("my_strdup: %s\n\n", s);
    free(s); s = NULL;

    calloc_demo();
    realloc_demo();

    /* NULL after free — good practice */
    printf("\nAfter free, set to NULL:\n");
    int *p = (int*)safe_malloc(sizeof(int));
    *p = 42;
    printf("  *p = %d\n", *p);
    free(p);
    p = NULL;
    printf("  p after free+NULL = %p\n", (void*)p);
    /* Now safe: if (p != NULL) dereference — won't crash */

    return 0;
}
```

---

# Topic 7: Control Flow & Preprocessor Basics

## Concept summary

**Control flow**: `if/else`, `switch`, `for`, `while`, `do-while`, `break`, `continue`, `goto` (rare, but seen in error-handling in C).

**`switch` rules**: must use `break` to prevent fall-through. `default` handles unmatched cases. Only works with integer/char types.

**Preprocessor** (`#define`, `#include`, `#ifdef`):
- Runs before compilation — pure text substitution
- `#define` macros have no type checking
- `#ifdef` / `#endif` used for conditional compilation (platform-specific code, debug builds)
- Include guards prevent double-inclusion

## Interview questions
1. What is fall-through in a `switch` statement? When is it useful?
2. What is the difference between `while` and `do-while`?
3. What does `break` do inside a `for` loop vs a `switch`?
4. What is the purpose of include guards?
5. What is the difference between `#define MAX 100` and `const int MAX = 100`?

## Answers
1. Fall-through in a `switch` occurs when execution continues into the next case without a `break`, and it is useful when multiple cases share the same logic.
2. A `while` loop checks the condition before executing the body, while a `do-while` loop executes the body at least once before checking the condition.
3. `break` exits the nearest enclosing loop in a `for` loop, while in a `switch` it exits the switch block to prevent fall-through.
4. Include guards prevent multiple inclusions of the same header file, avoiding redefinition errors during compilation.
```
file: myheader.h
suppose this .h file is included in multiple files, compiler sees "struct Node" twice (redefinition error)


#ifndef MYHEADER_H
#define MYHEADER_H

struct Node {
    int data;
};

#endif
```
5. `#define MAX 100` is a preprocessor macro with no type or scope, while `const int MAX = 100` is a typed variable with scope and better type safety.

## Runnable program

```c
#include <stdio.h>
#include <stdint.h>

/* Include guard (shown here in comments — used in header files) */
/*
#ifndef MY_HEADER_H
#define MY_HEADER_H
  ... header content ...
#endif
*/

/* Conditional compilation */
#define DEBUG 1

#if DEBUG
  #define LOG(msg) printf("[DEBUG] %s\n", msg)
#else
  #define LOG(msg)
#endif

/* switch with intentional fall-through */
void log_level(int level) {
    switch(level) {
        case 3:
            printf("  [CRITICAL] ");
            /* fall through intentional */
        case 2:
            printf("[ERROR] ");
            /* fall through intentional */
        case 1:
            printf("[WARN] message\n");
            break;
        case 0:
            printf("  [INFO] message\n");
            break;
        default:
            printf("  Unknown level\n");
    }
}

/* do-while: body executes at least once */
int read_valid_input(int *values, int count) {
    int attempts = 0;
    int i = 0;
    do {
        values[i++] = (attempts + 1) * 10;  /* simulated input */
        attempts++;
    } while (i < count);
    return attempts;
}

/* goto for error handling — acceptable pattern in C */
int process_data(int *buf, int n) {
    if (!buf) goto err_null;
    if (n <= 0) goto err_range;

    for (int i = 0; i < n; i++) buf[i] *= 2;
    return 0;

err_null:
    printf("  Error: null buffer\n");
    return -1;
err_range:
    printf("  Error: invalid size %d\n", n);
    return -2;
}

int main() {
    printf("=== Control Flow & Preprocessor ===\n\n");

    LOG("system starting");

    /* switch fall-through */
    printf("switch fall-through (level=3 logs all):\n");
    log_level(3);
    printf("switch (level=1):\n");
    log_level(1);
    printf("switch (level=0):\n");
    log_level(0);

    /* for with break and continue */
    printf("\nfor loop — skip even, stop at 7:\n");
    for (int i = 0; i < 10; i++) {
        if (i % 2 == 0) continue;   /* skip even */
        if (i == 7)     break;      /* stop at 7 */
        printf("  i = %d\n", i);
    }

    /* do-while */
    printf("\ndo-while (always runs at least once):\n");
    int vals[3];
    int n = read_valid_input(vals, 3);
    printf("  read %d values: %d %d %d\n", n, vals[0], vals[1], vals[2]);

    /* goto error handling */
    printf("\ngoto error handling:\n");
    int buf[4] = {1, 2, 3, 4};
    process_data(buf, 4);
    printf("  doubled: %d %d %d %d\n", buf[0], buf[1], buf[2], buf[3]);
    process_data(NULL, 4);
    process_data(buf, 0);

    /* #define vs const */
    printf("\n#define MAX 100 vs const int MAX:\n");
    printf("  #define: no type, no scope, pure substitution\n");
    printf("  const int: typed, scoped, visible to debugger\n");

    return 0;
}
```

---

# Topic 8: File I/O

## Concept summary

C file I/O uses the `FILE *` type from `<stdio.h>`.

**Key functions**:
| Function | Purpose |
|---|---|
| `fopen(path, mode)` | Open file; returns `NULL` on failure |
| `fclose(fp)` | Close and flush |
| `fprintf(fp, ...)` | Write formatted text |
| `fscanf(fp, ...)` | Read formatted text |
| `fgets(buf, n, fp)` | Read a line safely |
| `fread/fwrite` | Binary block read/write |
| `fseek/ftell` | Navigate file position |

**Modes**: `"r"` read, `"w"` write (truncate), `"a"` append, `"rb"/"wb"` binary.

**Always check `fopen` return** — `NULL` means failure (file not found, permissions, etc.).

## Interview questions
1. What does `fopen` return if the file does not exist?
2. What is the difference between text mode and binary mode?
3. Why must you call `fclose`? What happens if you don't?
4. What is the difference between `fprintf` and `printf`?
5. How do you read a file line by line safely?

## Answers + Extras
## Answers
1. `fopen` returns `NULL` if the file does not exist (in read mode) or cannot be opened.
2. Text mode may translate characters like `\n` depending on the system, while binary mode reads/writes raw bytes without any translation.
3. You must call `fclose` to flush buffers and release resources; otherwise data may not be written properly and resources may leak.
4. `printf` writes formatted output to the console (stdout), while `fprintf` writes formatted output to a specified file stream.
5. You can read a file line by line safely using `fgets(buffer, size, file_pointer)` which prevents buffer overflow.
## Extras
```
#include <stdio.h>

int main() {
    // 🔹 Open text files
    FILE *fin = fopen("iq_input.txt", "r");
    FILE *fout = fopen("iq_output.txt", "w");

    if (fin == NULL || fout == NULL) {
        printf("Error opening text files\n");
        return 1;
    }

    char line[100];

    // 🔹 Read line by line using fgets and write using fprintf
    while (fgets(line, sizeof(line), fin)) {
        fprintf(fout, "Processed: %s", line);
    }

    // 🔹 Check file position
    long pos = ftell(fin);
    printf("Current position in input file: %ld\n", pos);

    // 🔹 Move back to beginning
    fseek(fin, 0, SEEK_SET);

    fclose(fin);
    fclose(fout);

    // ===========================
    // 🔹 Binary file operations
    // ===========================

    FILE *fbin_in = fopen("iq_input.bin", "rb");
    FILE *fbin_out = fopen("iq_output.bin", "wb");

    if (fbin_in == NULL || fbin_out == NULL) {
        printf("Error opening binary files\n");
        return 1;
    }

    int buffer[5];

    // 🔹 Read binary data
    size_t n = fread(buffer, sizeof(int), 5, fbin_in);

    // 🔹 Write binary data
    fwrite(buffer, sizeof(int), n, fbin_out);

    fclose(fbin_in);
    fclose(fbin_out);

    return 0;
}
```


## Runnable program

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FILENAME "test_output.txt"

void write_demo() {
    FILE *fp = fopen(FILENAME, "w");
    if (!fp) {
        perror("fopen write");
        return;
    }
    fprintf(fp, "Line 1: firmware\n");
    fprintf(fp, "Line 2: embedded\n");
    fprintf(fp, "Line 3: Qualcomm\n");
    fprintf(fp, "Value: %d\n", 42);
    fclose(fp);
    printf("Wrote to %s\n", FILENAME);
}

void read_line_by_line() {
    FILE *fp = fopen(FILENAME, "r");
    if (!fp) {
        perror("fopen read");
        return;
    }
    char line[128];
    int linenum = 1;
    printf("\nReading line by line:\n");
    while (fgets(line, sizeof(line), fp)) {
        /* Remove trailing newline */
        line[strcspn(line, "\n")] = '\0';
        printf("  [%d] %s\n", linenum++, line);
    }
    fclose(fp);
}

void binary_rw_demo() {
    /* Write binary */
    int data[] = {10, 20, 30, 40, 50};
    FILE *fp = fopen("binary.bin", "wb");
    if (!fp) { perror("fopen bin write"); return; }
    fwrite(data, sizeof(int), 5, fp);
    fclose(fp);

    /* Read binary */
    int readback[5] = {0};
    fp = fopen("binary.bin", "rb");
    if (!fp) { perror("fopen bin read"); return; }
    size_t n = fread(readback, sizeof(int), 5, fp);
    fclose(fp);

    printf("\nBinary read back (%zu ints): ", n);
    for (int i = 0; i < 5; i++) printf("%d ", readback[i]);
    printf("\n");

    remove("binary.bin");
}

void append_demo() {
    FILE *fp = fopen(FILENAME, "a");
    if (!fp) { perror("fopen append"); return; }
    fprintf(fp, "Line 5: appended\n");
    fclose(fp);
    printf("\nAppended a line.\n");
}

int main() {
    printf("=== File I/O ===\n\n");
    write_demo();
    read_line_by_line();
    append_demo();
    read_line_by_line();
    binary_rw_demo();
    remove(FILENAME);
    return 0;
}
```

---

# Topic 9: Error Handling Patterns in C

## Concept summary

C has no exceptions. Common patterns:

1. **Return code**: function returns `0` on success, negative on error (most common in Linux/POSIX and embedded)
2. **Global `errno`**: set by standard library functions; read with `perror()` or `strerror()`
3. **Sentinel value**: return `NULL` or `-1` to signal failure
4. **Output parameter + return code**: return status, output via pointer parameter

**Best practices**:
- Always check return values of functions that can fail
- Use `enum` for error codes (readable)
- Clean up resources on error paths (close files, free memory)

## Interview questions
1. How does C report errors from standard library functions?
2. What is `errno` and how do you use it?
3. Design error codes for a small packet processing module.
4. Why is it important to check the return value of `malloc`?
5. How do you clean up resources on multiple error paths cleanly in C?

## Answers
1. C standard library functions usually report errors through special return values like `NULL`, `EOF`, or `-1`, and may also set `errno` for more details.
2. `errno` is a global error indicator set by some library/system calls on failure, and you use it after checking a function failed to learn the reason.
3. Example error codes: `PKT_OK = 0`, `PKT_ERR_NULL = -1`, `PKT_ERR_LEN = -2`, `PKT_ERR_CRC = -3`, `PKT_ERR_ALLOC = -4`, `PKT_ERR_FORMAT = -5`.
4. It is important to check `malloc` because if allocation fails it returns `NULL`, and using that pointer causes undefined behavior or a crash.
5. A clean way is to use one cleanup section with `goto` so every error path releases already-acquired resources before returning.

## Runnable program

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdint.h>

/* Error codes via enum */
typedef enum {
    ERR_OK            =  0,
    ERR_NULL_PTR      = -1,
    ERR_INVALID_PARAM = -2,
    ERR_OUT_OF_MEMORY = -3,
    ERR_BUFFER_FULL   = -4,
} ErrorCode;

const char* err_str(ErrorCode e) {
    switch(e) {
        case ERR_OK:            return "OK";
        case ERR_NULL_PTR:      return "null pointer";
        case ERR_INVALID_PARAM: return "invalid parameter";
        case ERR_OUT_OF_MEMORY: return "out of memory";
        case ERR_BUFFER_FULL:   return "buffer full";
        default:                return "unknown error";
    }
}

/* Output parameter pattern */
ErrorCode parse_packet(const uint8_t *data, size_t len,
                       uint8_t *out_type, uint16_t *out_length) {
    if (!data || !out_type || !out_length) return ERR_NULL_PTR;
    if (len < 3) return ERR_INVALID_PARAM;

    *out_type   = data[0];
    *out_length = (uint16_t)((data[1] << 8) | data[2]);
    return ERR_OK;
}

/* Multi-resource cleanup with goto */
ErrorCode complex_init(uint8_t **buf1, uint8_t **buf2) {
    *buf1 = (uint8_t*)malloc(64);
    if (!*buf1) return ERR_OUT_OF_MEMORY;

    *buf2 = (uint8_t*)malloc(128);
    if (!*buf2) {
        free(*buf1); *buf1 = NULL;
        return ERR_OUT_OF_MEMORY;
    }
    /* Both allocated successfully */
    memset(*buf1, 0xAA, 64);
    memset(*buf2, 0xBB, 128);
    return ERR_OK;
}

int main() {
    printf("=== Error Handling Patterns ===\n\n");

    /* errno from standard library */
    printf("errno demo:\n");
    FILE *fp = fopen("nonexistent_file.txt", "r");
    if (!fp) {
        printf("  fopen failed: %s (errno=%d)\n\n", strerror(errno), errno);
    }

    /* Return code pattern */
    uint8_t packet[] = { 0x02, 0x00, 0x10, 0xAA, 0xBB };
    uint8_t  type;
    uint16_t length;

    ErrorCode rc = parse_packet(packet, sizeof(packet), &type, &length);
    printf("parse_packet result: %s\n", err_str(rc));
    if (rc == ERR_OK)
        printf("  type=0x%02X, length=%u\n\n", type, length);

    /* Error case */
    rc = parse_packet(NULL, 5, &type, &length);
    printf("parse_packet(NULL): %s\n\n", err_str(rc));

    rc = parse_packet(packet, 2, &type, &length);
    printf("parse_packet(too short): %s\n\n", err_str(rc));

    /* Multi-resource cleanup */
    uint8_t *b1 = NULL, *b2 = NULL;
    rc = complex_init(&b1, &b2);
    printf("complex_init: %s\n", err_str(rc));
    if (rc == ERR_OK) {
        printf("  b1[0]=0x%02X, b2[0]=0x%02X\n", b1[0], b2[0]);
        free(b1); b1 = NULL;
        free(b2); b2 = NULL;
    }

    return 0;
}
```

---

# Quick Reference Cheat Sheet

## Type sizes (32-bit system)
```
char   = 1 byte    short = 2 bytes
int    = 4 bytes   long  = 4 or 8 bytes
float  = 4 bytes   double = 8 bytes
pointer = 4 bytes (32-bit) or 8 bytes (64-bit)
```

## Pointer patterns
```c
int *p = &x;          /* pointer to int */
const int *p = &x;    /* pointer to const int (value read-only) */
int * const p = &x;   /* const pointer to int (address read-only) */
int **pp = &p;        /* pointer to pointer */
void (*fp)(int) = fn; /* function pointer */
```

## String essentials
```c
strlen(s)             /* length without '\0' */
strcpy(dst, src)      /* unsafe — no bounds check */
strncpy(dst, src, n)  /* safer — always null-terminate manually */
strcmp(a, b)          /* 0 if equal, <0 or >0 otherwise */
memset(p, val, n)     /* fill n bytes with val */
memcpy(dst, src, n)   /* copy n bytes */
```

## Memory rules
```c
/* Every malloc needs exactly one free */
T *p = malloc(n * sizeof(T));
if (!p) handle_error();
/* ... use p ... */
free(p);
p = NULL;   /* always nullify after free */
```

## Error handling pattern
```c
int result = do_something();
if (result < 0) {
    /* handle error */
    cleanup();
    return result;
}
```

---

*This covers basic-to-intermediate C that any company hiring C developers will test.*
