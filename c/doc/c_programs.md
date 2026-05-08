# C Programming Problems — 150 Programs with Expected Output

> Source: embeddedshiksha.com — Helping Embedded System Engineers to Clear Interviews

---

# Section 1: Pointer Problems (Programs 1–25)

---

### P1. Swap two numbers using pointers.
**Expected Output:** `Before: a=5 b=10 | After: a=10 b=5`
```c
#include <stdio.h>
void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}
int main() {
    int a = 5, b = 10;
    printf("Before: a=%d b=%d\n", a, b);
    swap(&a, &b);
    printf("After:  a=%d b=%d\n", a, b);
    return 0;
}
```

---

### P2. Reverse an array using pointers.
**Expected Output:** `10 20 30 40 50` → `50 40 30 20 10`
```c
#include <stdio.h>
void reverse(int *arr, int n) {
    int *left = arr, *right = arr + n - 1;
    while (left < right) {
        int tmp = *left; *left = *right; *right = tmp;
        left++; right--;
    }
}
int main() {
    int arr[] = {10, 20, 30, 40, 50};
    int n = 5;
    reverse(arr, n);
    for (int i = 0; i < n; i++) printf("%d ", arr[i]);
    printf("\n");
    return 0;
}
```

---

### P3. Find the largest element using pointer traversal.
**Expected Output:** `Largest: 90`
```c
#include <stdio.h>
int find_max(int *arr, int n) {
    int *p = arr, max = *p;
    for (p = arr + 1; p < arr + n; p++)
        if (*p > max) max = *p;
    return max;
}
int main() {
    int arr[] = {10, 90, 30, 70, 50};
    printf("Largest: %d\n", find_max(arr, 5));
    return 0;
}
```

---

### P4. Implement strlen() using pointer arithmetic.
**Expected Output:** `Length: 5`
```c
#include <stdio.h>
int my_strlen(const char *s) {
    const char *p = s;
    while (*p) p++;
    return p - s;
}
int main() {
    printf("Length: %d\n", my_strlen("Hello"));
    return 0;
}
```

---

### P5. Implement strcpy() using pointers.
**Expected Output:** `Copied: Hello`
```c
#include <stdio.h>
char* my_strcpy(char *dst, const char *src) {
    char *d = dst;
    while ((*dst++ = *src++));
    return d;
}
int main() {
    char dst[20];
    my_strcpy(dst, "Hello");
    printf("Copied: %s\n", dst);
    return 0;
}
```

---

### P6. Implement strcmp() using pointers.
**Expected Output:** `Equal: 1 | NotEqual: 0`
```c
#include <stdio.h>
int my_strcmp(const char *a, const char *b) {
    while (*a && (*a == *b)) { a++; b++; }
    return *a - *b;
}
int main() {
    printf("Equal: %d\n",    my_strcmp("abc", "abc") == 0);
    printf("NotEqual: %d\n", my_strcmp("abc", "abd") == 0);
    return 0;
}
```

---

### P7. Write a function that returns pointer to maximum element.
**Expected Output:** `Max = 99 at index 3`
```c
#include <stdio.h>
int* max_ptr(int *arr, int n) {
    int *max = arr;
    for (int i = 1; i < n; i++)
        if (arr[i] > *max) max = &arr[i];
    return max;
}
int main() {
    int arr[] = {10, 30, 20, 99, 50};
    int *m = max_ptr(arr, 5);
    printf("Max = %d at index %ld\n", *m, m - arr);
    return 0;
}
```

---

### P8. Implement memcpy().
**Expected Output:** `Destination: Hello`
```c
#include <stdio.h>
void* my_memcpy(void *dst, const void *src, int n) {
    char *d = (char*)dst;
    const char *s = (const char*)src;
    while (n--) *d++ = *s++;
    return dst;
}
int main() {
    char src[] = "Hello";
    char dst[10] = {0};
    my_memcpy(dst, src, 6);
    printf("Destination: %s\n", dst);
    return 0;
}
```

---

### P9. Implement memmove() handling overlap.
**Expected Output:** `Result: World`
```c
#include <stdio.h>
void* my_memmove(void *dst, const void *src, int n) {
    char *d = (char*)dst;
    const char *s = (const char*)src;
    if (d < s) {
        while (n--) *d++ = *s++;
    } else {
        d += n; s += n;
        while (n--) *--d = *--s;
    }
    return dst;
}
int main() {
    char buf[] = "Hello World";
    my_memmove(buf, buf + 6, 6);  // overlapping copy
    printf("Result: %s\n", buf);  // World
    return 0;
}
```

---

### P10. Print array using pointer increment.
**Expected Output:** `1 2 3 4 5`
```c
#include <stdio.h>
int main() {
    int arr[] = {1, 2, 3, 4, 5};
    int *p = arr;
    int *end = arr + 5;
    while (p < end) printf("%d ", *p++);
    printf("\n");
    return 0;
}
```

---

### P11. Find sum of array elements using pointer.
**Expected Output:** `Sum: 150`
```c
#include <stdio.h>
int main() {
    int arr[] = {10, 20, 30, 40, 50};
    int *p = arr, sum = 0;
    for (int i = 0; i < 5; i++) sum += *p++;
    printf("Sum: %d\n", sum);
    return 0;
}
```

---

### P12. Reverse string using pointer.
**Expected Output:** `Reversed: olleH`
```c
#include <stdio.h>
#include <string.h>
void reverse_str(char *s) {
    char *end = s + strlen(s) - 1;
    while (s < end) {
        char tmp = *s; *s = *end; *end = tmp;
        s++; end--;
    }
}
int main() {
    char s[] = "Hello";
    reverse_str(s);
    printf("Reversed: %s\n", s);
    return 0;
}
```

---

### P13. Implement pointer-based matrix traversal.
**Expected Output:** `1 2 3 4 5 6 7 8 9`
```c
#include <stdio.h>
int main() {
    int m[3][3] = {{1,2,3},{4,5,6},{7,8,9}};
    int *p = &m[0][0];
    for (int i = 0; i < 9; i++) printf("%d ", *p++);
    printf("\n");
    return 0;
}
```

---

### P14. Swap two pointers.
**Expected Output:** `*p=20, *q=10`
```c
#include <stdio.h>
void swap_ptrs(int **p, int **q) {
    int *tmp = *p; *p = *q; *q = tmp;
}
int main() {
    int a = 10, b = 20;
    int *p = &a, *q = &b;
    swap_ptrs(&p, &q);
    printf("*p=%d, *q=%d\n", *p, *q);
    return 0;
}
```

---

### P15. Write function returning pointer to static variable.
**Expected Output:** `Value: 42`
```c
#include <stdio.h>
int* get_static() {
    static int val = 42;
    return &val;   // safe — static persists after return
}
int main() {
    int *p = get_static();
    printf("Value: %d\n", *p);
    return 0;
}
```

---

### P16. Find difference between two pointers.
**Expected Output:** `Difference: 3 elements`
```c
#include <stdio.h>
int main() {
    int arr[] = {10, 20, 30, 40, 50};
    int *p1 = &arr[1];
    int *p2 = &arr[4];
    printf("Difference: %ld elements\n", p2 - p1);
    return 0;
}
```

---

### P17. Copy array using pointer arithmetic.
**Expected Output:** `10 20 30 40 50`
```c
#include <stdio.h>
int main() {
    int src[] = {10, 20, 30, 40, 50};
    int dst[5];
    int *s = src, *d = dst;
    while (s < src + 5) *d++ = *s++;
    for (int i = 0; i < 5; i++) printf("%d ", dst[i]);
    printf("\n");
    return 0;
}
```

---

### P18. Detect null pointer before dereferencing.
**Expected Output:** `Pointer is NULL — skip` then `Value: 10`
```c
#include <stdio.h>
void safe_print(int *p) {
    if (p == NULL) { printf("Pointer is NULL — skip\n"); return; }
    printf("Value: %d\n", *p);
}
int main() {
    int x = 10;
    safe_print(NULL);
    safe_print(&x);
    return 0;
}
```

---

### P19. Write program demonstrating double pointer.
**Expected Output:** `x=42, *p=42, **pp=42`
```c
#include <stdio.h>
int main() {
    int x = 42;
    int *p = &x;
    int **pp = &p;
    printf("x=%d, *p=%d, **pp=%d\n", x, *p, **pp);
    **pp = 100;
    printf("After **pp=100: x=%d\n", x);
    return 0;
}
```

---

### P20. Reverse linked list using pointers.
**Expected Output:** `5 4 3 2 1`
```c
#include <stdio.h>
#include <stdlib.h>
typedef struct Node { int val; struct Node *next; } Node;

Node* new_node(int v) {
    Node *n = malloc(sizeof(Node));
    n->val = v; n->next = NULL;
    return n;
}
Node* reverse(Node *head) {
    Node *prev = NULL, *curr = head, *next;
    while (curr) { next = curr->next; curr->next = prev; prev = curr; curr = next; }
    return prev;
}
int main() {
    Node *head = new_node(1);
    head->next = new_node(2); head->next->next = new_node(3);
    head->next->next->next = new_node(4);
    head->next->next->next->next = new_node(5);
    head = reverse(head);
    for (Node *p = head; p; p = p->next) printf("%d ", p->val);
    printf("\n");
    return 0;
}
```

---

### P21. Implement pointer-based search in array.
**Expected Output:** `Found 30 at index 2`
```c
#include <stdio.h>
int* search(int *arr, int n, int target) {
    for (int *p = arr; p < arr + n; p++)
        if (*p == target) return p;
    return NULL;
}
int main() {
    int arr[] = {10, 20, 30, 40, 50};
    int *p = search(arr, 5, 30);
    if (p) printf("Found %d at index %ld\n", *p, p - arr);
    return 0;
}
```

---

### P22. Write program printing addresses of variables.
**Expected Output:** Addresses of a, b, c (actual values vary)
```c
#include <stdio.h>
int main() {
    int   a = 1;
    float b = 2.5f;
    char  c = 'X';
    printf("Address of a: %p\n", (void*)&a);
    printf("Address of b: %p\n", (void*)&b);
    printf("Address of c: %p\n", (void*)&c);
    printf("a=%d, b=%.1f, c=%c\n", a, b, c);
    return 0;
}
```

---

### P23. Implement pointer-based bubble sort.
**Expected Output:** `1 2 3 4 5`
```c
#include <stdio.h>
void bubble_sort(int *arr, int n) {
    for (int i = 0; i < n-1; i++)
        for (int j = 0; j < n-i-1; j++)
            if (*(arr+j) > *(arr+j+1)) {
                int tmp = *(arr+j);
                *(arr+j) = *(arr+j+1);
                *(arr+j+1) = tmp;
            }
}
int main() {
    int arr[] = {5, 3, 1, 4, 2};
    bubble_sort(arr, 5);
    for (int i = 0; i < 5; i++) printf("%d ", arr[i]);
    printf("\n");
    return 0;
}
```

---

### P24. Swap two structures using pointers.
**Expected Output:** `a:{2,Bob} b:{1,Alice}`
```c
#include <stdio.h>
typedef struct { int id; char name[10]; } Person;
void swap_struct(Person *a, Person *b) {
    Person tmp = *a; *a = *b; *b = tmp;
}
int main() {
    Person a = {1, "Alice"}, b = {2, "Bob"};
    swap_struct(&a, &b);
    printf("a:{%d,%s} b:{%d,%s}\n", a.id, a.name, b.id, b.name);
    return 0;
}
```

---

### P25. Implement dynamic array using pointers.
**Expected Output:** `0 10 20 30 40`
```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int n = 5;
    int *arr = (int*)malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) arr[i] = i * 10;
    for (int i = 0; i < n; i++) printf("%d ", arr[i]);
    printf("\n");
    free(arr);
    return 0;
}
```

---

# Section 2: Memory Management Problems (Programs 26–45)

---

### P26. Allocate array dynamically using malloc.
**Expected Output:** `1 2 3 4 5`
```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int n = 5;
    int *arr = (int*)malloc(n * sizeof(int));
    if (!arr) return 1;
    for (int i = 0; i < n; i++) arr[i] = i + 1;
    for (int i = 0; i < n; i++) printf("%d ", arr[i]);
    printf("\n");
    free(arr);
    return 0;
}
```

---

### P27. Allocate matrix dynamically.
**Expected Output:** `3x3 matrix with values i*j`
```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int rows = 3, cols = 3;
    int **m = (int**)malloc(rows * sizeof(int*));
    for (int i = 0; i < rows; i++)
        m[i] = (int*)malloc(cols * sizeof(int));

    for (int i = 0; i < rows; i++)
        for (int j = 0; j < cols; j++)
            m[i][j] = i * cols + j + 1;

    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) printf("%3d", m[i][j]);
        printf("\n");
    }
    for (int i = 0; i < rows; i++) free(m[i]);
    free(m);
    return 0;
}
```

---

### P28. Implement custom malloc() conceptually.
**Expected Output:** `Allocated 40 bytes. Values: 0 1 2 3 4 5 6 7 8 9`
```c
#include <stdio.h>
#include <stdlib.h>
// Simplified pool allocator concept
#define POOL_SIZE 1024
static char pool[POOL_SIZE];
static int pool_offset = 0;

void* pool_alloc(int size) {
    if (pool_offset + size > POOL_SIZE) return NULL;
    void *ptr = &pool[pool_offset];
    pool_offset += size;
    return ptr;
}

int main() {
    int *arr = (int*)pool_alloc(10 * sizeof(int));
    if (!arr) { printf("Alloc failed\n"); return 1; }
    printf("Allocated 40 bytes. Values: ");
    for (int i = 0; i < 10; i++) { arr[i] = i; printf("%d ", arr[i]); }
    printf("\n");
    return 0;
}
```

---

### P29. Write program demonstrating memory leak.
**Expected Output:** Shows leak (use valgrind to detect)`
```c
#include <stdio.h>
#include <stdlib.h>
void leaky() {
    int *p = (int*)malloc(100 * sizeof(int));
    // INTENTIONAL: forgot to free(p) — memory leaked
    printf("Allocated but not freed — run with valgrind to detect\n");
}
void safe() {
    int *p = (int*)malloc(100 * sizeof(int));
    printf("Allocated\n");
    free(p); p = NULL;  // properly freed
    printf("Freed\n");
}
int main() {
    leaky();
    safe();
    return 0;
}
```

---

### P30. Write program showing dangling pointer.
**Expected Output:** Shows dangling pointer risk and safe fix
```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int *p = (int*)malloc(sizeof(int));
    *p = 42;
    printf("Before free: %d\n", *p);

    free(p);
    p = NULL;   // fix: set to NULL immediately

    if (p == NULL) {
        printf("Pointer is NULL — safe, not accessed\n");
    }
    return 0;
}
```

---

### P31. Demonstrate double free bug.
**Expected Output:** Safe version: no crash. Unsafe: heap corruption.
```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int *p = (int*)malloc(sizeof(int));
    *p = 10;
    printf("Value: %d\n", *p);

    free(p);
    p = NULL;   // always NULL after free

    free(p);    // free(NULL) is safe — no double free bug
    printf("Safe double-free (on NULL) — OK\n");
    return 0;
}
```

---

### P32. Implement dynamic string copy.
**Expected Output:** `Copied: Hello World`
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
char* dyn_strcpy(const char *src) {
    char *dst = (char*)malloc(strlen(src) + 1);
    if (!dst) return NULL;
    strcpy(dst, src);
    return dst;
}
int main() {
    char *s = dyn_strcpy("Hello World");
    printf("Copied: %s\n", s);
    free(s);
    return 0;
}
```

---

### P33. Implement dynamic array resizing.
**Expected Output:** `1 2 3 4 5 6 7 8 9 10`
```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int size = 5;
    int *arr = (int*)malloc(size * sizeof(int));
    for (int i = 0; i < size; i++) arr[i] = i + 1;

    // Resize to 10
    size = 10;
    arr = (int*)realloc(arr, size * sizeof(int));
    for (int i = 5; i < size; i++) arr[i] = i + 1;

    for (int i = 0; i < size; i++) printf("%d ", arr[i]);
    printf("\n");
    free(arr);
    return 0;
}
```

---

### P34. Write program to simulate stack overflow.
**Expected Output:** Prints recursion depth before crash (or OS limit)
```c
#include <stdio.h>
// WARNING: This will crash — demonstrates stack overflow
int depth = 0;
void recurse() {
    depth++;
    // Uncomment to see actual overflow (will crash eventually):
    // recurse();
    printf("Depth: %d\n", depth);  // Safe: only one level for demo
}
int main() {
    printf("Simulating stack overflow risk...\n");
    recurse();
    printf("In real recursion without base case, this would crash\n");
    return 0;
}
```

---

### P35. Allocate struct dynamically.
**Expected Output:** `ID:1 Name:Alice`
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct { int id; char name[20]; } Student;
int main() {
    Student *s = (Student*)malloc(sizeof(Student));
    s->id = 1;
    strcpy(s->name, "Alice");
    printf("ID:%d Name:%s\n", s->id, s->name);
    free(s);
    return 0;
}
```

---

### P36. Create dynamic linked list.
**Expected Output:** `1 2 3 4 5`
```c
#include <stdio.h>
#include <stdlib.h>
typedef struct Node { int val; struct Node *next; } Node;
int main() {
    Node *head = NULL, *tail = NULL;
    for (int i = 1; i <= 5; i++) {
        Node *n = malloc(sizeof(Node));
        n->val = i; n->next = NULL;
        if (!head) { head = tail = n; }
        else { tail->next = n; tail = n; }
    }
    for (Node *p = head; p; p = p->next) printf("%d ", p->val);
    printf("\n");
    // Free:
    Node *curr = head;
    while (curr) { Node *tmp = curr->next; free(curr); curr = tmp; }
    return 0;
}
```

---

### P37. Free entire linked list memory.
**Expected Output:** `List freed — 5 nodes released`
```c
#include <stdio.h>
#include <stdlib.h>
typedef struct Node { int val; struct Node *next; } Node;
void free_list(Node *head) {
    int count = 0;
    while (head) {
        Node *tmp = head->next;
        free(head);
        head = tmp;
        count++;
    }
    printf("List freed — %d nodes released\n", count);
}
int main() {
    Node *head = malloc(sizeof(Node)); head->val = 1;
    head->next = malloc(sizeof(Node)); head->next->val = 2;
    head->next->next = malloc(sizeof(Node)); head->next->next->val = 3;
    head->next->next->next = malloc(sizeof(Node)); head->next->next->next->val=4;
    head->next->next->next->next = malloc(sizeof(Node));
    head->next->next->next->next->val = 5;
    head->next->next->next->next->next = NULL;
    free_list(head);
    return 0;
}
```

---

### P38. Allocate memory using calloc and print values.
**Expected Output:** `0 0 0 0 0` (all zeros from calloc)
```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int *arr = (int*)calloc(5, sizeof(int));
    if (!arr) return 1;
    for (int i = 0; i < 5; i++) printf("%d ", arr[i]);
    printf("\n");
    free(arr);
    return 0;
}
```

---

### P39. Implement memory pool concept.
**Expected Output:** `Pool alloc: ptr1=OK ptr2=OK | Pool used: 8 bytes`
```c
#include <stdio.h>
#define POOL 256
static char pool[POOL];
static int  offset = 0;
void* palloc(int sz) {
    if (offset + sz > POOL) return NULL;
    void *p = pool + offset;
    offset += sz;
    return p;
}
void preset() { offset = 0; }  // reset pool
int main() {
    int   *p1 = (int*)palloc(sizeof(int));
    float *p2 = (float*)palloc(sizeof(float));
    *p1 = 42; *p2 = 3.14f;
    printf("ptr1=%s ptr2=%s\n", p1?"OK":"FAIL", p2?"OK":"FAIL");
    printf("Pool used: %d bytes\n", offset);
    return 0;
}
```

---

### P40. Write program showing heap fragmentation.
**Expected Output:** Demonstrates fragmentation concept
```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    // Allocate and free alternating blocks — causes fragmentation
    int *a = malloc(100); int *b = malloc(200);
    int *c = malloc(100); int *d = malloc(200);

    free(a);  // free block 1
    free(c);  // free block 3

    // Now try to allocate 150 bytes — may fail on fragmented heap
    // (a=100 free, c=100 free — neither alone is 150)
    int *e = malloc(150);
    printf("Large alloc after fragmentation: %s\n", e ? "OK" : "FAILED");

    if (e) free(e);
    free(b); free(d);
    printf("Fragmentation demo complete\n");
    return 0;
}
```

---

### P41. Use realloc to resize array.
**Expected Output:** `1 2 3 4 5 6 7 8`
```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int *arr = (int*)malloc(4 * sizeof(int));
    for (int i = 0; i < 4; i++) arr[i] = i + 1;

    arr = (int*)realloc(arr, 8 * sizeof(int));
    for (int i = 4; i < 8; i++) arr[i] = i + 1;

    for (int i = 0; i < 8; i++) printf("%d ", arr[i]);
    printf("\n");
    free(arr);
    return 0;
}
```

---

### P42. Detect memory allocation failure.
**Expected Output:** `malloc failed — handle error gracefully`
```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    // Try to allocate unreasonably large block
    size_t huge = (size_t)1024 * 1024 * 1024 * 4;  // 4GB
    int *p = (int*)malloc(huge);
    if (p == NULL) {
        printf("malloc failed — handle error gracefully\n");
        // In embedded: use static fallback, log error, reset
        return -1;
    }
    free(p);
    return 0;
}
```

---

### P43. Write program storing strings dynamically.
**Expected Output:** `Alice Bob Charlie`
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main() {
    const char *names[] = {"Alice", "Bob", "Charlie"};
    int n = 3;
    char **arr = (char**)malloc(n * sizeof(char*));

    for (int i = 0; i < n; i++) {
        arr[i] = (char*)malloc(strlen(names[i]) + 1);
        strcpy(arr[i], names[i]);
    }
    for (int i = 0; i < n; i++) printf("%s ", arr[i]);
    printf("\n");
    for (int i = 0; i < n; i++) free(arr[i]);
    free(arr);
    return 0;
}
```

---

### P44. Simulate buffer overflow (safe demo).
**Expected Output:** Shows safe vs unsafe behavior
```c
#include <stdio.h>
#include <string.h>
int main() {
    char buf[5];

    // UNSAFE (commented out to prevent actual overflow):
    // strcpy(buf, "Hello World");  // overflows buf[5]

    // SAFE:
    strncpy(buf, "Hello World", sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';
    printf("Safe copy: '%s'\n", buf);  // "Hell"
    printf("Buffer size: %zu, string fits safely\n", sizeof(buf));
    return 0;
}
```

---

### P45. Write safe dynamic string copy function.
**Expected Output:** `Safe copy: Hello Wor` (truncated to fit)
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
char* safe_strdup(const char *src, int max_len) {
    int len = strlen(src);
    if (len > max_len) len = max_len;
    char *dst = (char*)malloc(len + 1);
    if (!dst) return NULL;
    strncpy(dst, src, len);
    dst[len] = '\0';
    return dst;
}
int main() {
    char *s = safe_strdup("Hello World", 9);
    printf("Safe copy: %s\n", s);  // Hello Wor
    free(s);
    return 0;
}
```

---

# Section 3: Bit Manipulation Problems (Programs 46–70)

---

### P46. Set nth bit in number.
**Expected Output:** `Result: 0x09 (bit 3 set in 0x01)`
```c
#include <stdio.h>
int set_bit(int n, int pos) { return n | (1 << pos); }
int main() {
    printf("Result: 0x%02X\n", set_bit(0x01, 3));  // 0x09
    return 0;
}
```

---

### P47. Clear nth bit.
**Expected Output:** `Result: 0xF7 (bit 3 cleared from 0xFF)`
```c
#include <stdio.h>
int clear_bit(int n, int pos) { return n & ~(1 << pos); }
int main() {
    printf("Result: 0x%02X\n", clear_bit(0xFF, 3));  // 0xF7
    return 0;
}
```

---

### P48. Toggle nth bit.
**Expected Output:** `0xFF -> 0xEF (bit 4 toggled)`
```c
#include <stdio.h>
int toggle_bit(int n, int pos) { return n ^ (1 << pos); }
int main() {
    printf("0xFF -> 0x%02X\n", toggle_bit(0xFF, 4));  // 0xEF
    return 0;
}
```

---

### P49. Check if bit is set.
**Expected Output:** `Bit 3 is SET | Bit 2 is CLEAR`
```c
#include <stdio.h>
int is_set(int n, int pos) { return (n >> pos) & 1; }
int main() {
    int val = 0b00001000;  // only bit 3 set
    printf("Bit 3 is %s\n", is_set(val, 3) ? "SET" : "CLEAR");
    printf("Bit 2 is %s\n", is_set(val, 2) ? "SET" : "CLEAR");
    return 0;
}
```

---

### P50. Count number of set bits.
**Expected Output:** `Set bits in 0xAB: 5`
```c
#include <stdio.h>
int count_bits(int n) {
    int c = 0;
    while (n) { n &= (n-1); c++; }
    return c;
}
int main() {
    printf("Set bits in 0xAB: %d\n", count_bits(0xAB));  // 5
    return 0;
}
```

---

### P51. Check if number is power of 2.
**Expected Output:** `8: YES | 6: NO | 16: YES`
```c
#include <stdio.h>
int is_pow2(int n) { return n > 0 && (n & (n-1)) == 0; }
int main() {
    printf("8:  %s\n", is_pow2(8)  ? "YES" : "NO");
    printf("6:  %s\n", is_pow2(6)  ? "YES" : "NO");
    printf("16: %s\n", is_pow2(16) ? "YES" : "NO");
    return 0;
}
```

---

### P52. Swap numbers using XOR.
**Expected Output:** `Before: a=5 b=10 | After: a=10 b=5`
```c
#include <stdio.h>
int main() {
    int a = 5, b = 10;
    printf("Before: a=%d b=%d\n", a, b);
    a ^= b; b ^= a; a ^= b;
    printf("After:  a=%d b=%d\n", a, b);
    return 0;
}
```

---

### P53. Reverse bits of a byte.
**Expected Output:** `Reverse of 0b10110001 = 0b10001101`
```c
#include <stdio.h>
uint8_t reverse_bits(uint8_t b) {
    uint8_t r = 0;
    for (int i = 0; i < 8; i++) {
        r = (r << 1) | (b & 1);
        b >>= 1;
    }
    return r;
}
int main() {
    uint8_t v = 0b10110001;
    printf("Input:  0x%02X | Reversed: 0x%02X\n", v, reverse_bits(v));
    return 0;
}
```

---

### P54. Extract bits between positions.
**Expected Output:** `Bits [5:2] of 0b11110100 = 0b1101`
```c
#include <stdio.h>
int extract_bits(int n, int high, int low) {
    int mask = ((1 << (high - low + 1)) - 1) << low;
    return (n & mask) >> low;
}
int main() {
    int v = 0b11110100;
    printf("Bits[5:2] = 0x%X\n", extract_bits(v, 5, 2));  // 0xD = 1101
    return 0;
}
```

---

### P55. Set multiple bits using mask.
**Expected Output:** `0x00 | mask 0x0F = 0x0F`
```c
#include <stdio.h>
int main() {
    uint8_t reg = 0x00;
    uint8_t mask = 0x0F;   // set lower 4 bits
    reg |= mask;
    printf("Result: 0x%02X\n", reg);  // 0x0F
    return 0;
}
```

---

### P56. Clear multiple bits using mask.
**Expected Output:** `0xFF & ~0x0F = 0xF0`
```c
#include <stdio.h>
int main() {
    uint8_t reg = 0xFF;
    uint8_t mask = 0x0F;
    reg &= ~mask;             // clear lower 4 bits
    printf("Result: 0x%02X\n", reg);  // 0xF0
    return 0;
}
```

---

### P57. Check parity of number.
**Expected Output:** `0b10110101 has ODD parity`
```c
#include <stdio.h>
int parity(int n) {
    int p = 0;
    while (n) { p ^= (n & 1); n >>= 1; }
    return p;  // 1=odd, 0=even
}
int main() {
    int v = 0b10110101;
    printf("Parity: %s\n", parity(v) ? "ODD" : "EVEN");
    return 0;
}
```

---

### P58. Find first set bit.
**Expected Output:** `First set bit position in 0b10110000: 4`
```c
#include <stdio.h>
int first_set_bit(int n) {
    for (int i = 0; i < 32; i++)
        if ((n >> i) & 1) return i;
    return -1;
}
int main() {
    printf("First set bit: %d\n", first_set_bit(0b10110000));  // 4
    return 0;
}
```

---

### P59. Find lowest set bit.
**Expected Output:** `Lowest set bit value: 4 (bit 2)`
```c
#include <stdio.h>
int main() {
    int n = 0b10110100;
    int lowest = n & (-n);   // isolate lowest set bit
    printf("Lowest set bit value: %d\n", lowest);  // 4
    return 0;
}
```

---

### P60. Convert binary to decimal.
**Expected Output:** `Binary 1011 = Decimal 11`
```c
#include <stdio.h>
int bin_to_dec(const char *bin) {
    int result = 0;
    while (*bin) { result = result * 2 + (*bin++ - '0'); }
    return result;
}
int main() {
    printf("Binary 1011 = Decimal %d\n", bin_to_dec("1011"));  // 11
    return 0;
}
```

---

### P61. Implement bit rotation.
**Expected Output:** `Rotate left 0b00000001 by 2 = 0b00000100`
```c
#include <stdio.h>
#include <stdint.h>
uint8_t rotate_left(uint8_t v, int n) {
    n %= 8;
    return (v << n) | (v >> (8 - n));
}
uint8_t rotate_right(uint8_t v, int n) {
    n %= 8;
    return (v >> n) | (v << (8 - n));
}
int main() {
    printf("RotL: 0x%02X\n", rotate_left(0x01, 2));   // 0x04
    printf("RotR: 0x%02X\n", rotate_right(0x80, 2));  // 0x20
    return 0;
}
```

---

### P62. Pack two numbers in one byte.
**Expected Output:** `Packed: 0xAB (high=0xA, low=0xB)`
```c
#include <stdio.h>
#include <stdint.h>
int main() {
    uint8_t high = 0xA, low = 0xB;
    uint8_t packed = (high << 4) | (low & 0x0F);
    printf("Packed: 0x%02X\n", packed);  // 0xAB

    // Unpack:
    uint8_t h = (packed >> 4) & 0x0F;
    uint8_t l =  packed       & 0x0F;
    printf("Unpacked: high=0x%X low=0x%X\n", h, l);
    return 0;
}
```

---

### P63. Extract high nibble and low nibble.
**Expected Output:** `0xAB: high=0xA low=0xB`
```c
#include <stdio.h>
#include <stdint.h>
int main() {
    uint8_t val = 0xAB;
    uint8_t high = (val >> 4) & 0x0F;
    uint8_t low  =  val       & 0x0F;
    printf("0x%02X: high=0x%X low=0x%X\n", val, high, low);
    return 0;
}
```

---

### P64. Check endianness using bit operations.
**Expected Output:** `System is Little Endian` or `Big Endian`
```c
#include <stdio.h>
#include <stdint.h>
int main() {
    uint32_t x = 1;
    uint8_t *p = (uint8_t*)&x;
    printf("System is %s Endian\n", (*p == 1) ? "Little" : "Big");
    return 0;
}
```

---

### P65. Implement register bit manipulation macro.
**Expected Output:** Demonstrates SET/CLEAR/TOGGLE/READ macros
```c
#include <stdio.h>
#include <stdint.h>

#define BIT_SET(reg, n)    ((reg) |=  (1U << (n)))
#define BIT_CLR(reg, n)    ((reg) &= ~(1U << (n)))
#define BIT_TOG(reg, n)    ((reg) ^=  (1U << (n)))
#define BIT_RD(reg, n)     (((reg) >> (n)) & 1U)

int main() {
    uint8_t reg = 0x00;
    BIT_SET(reg, 3);  printf("After SET  bit3: 0x%02X\n", reg);  // 0x08
    BIT_TOG(reg, 3);  printf("After TOG  bit3: 0x%02X\n", reg);  // 0x00
    BIT_SET(reg, 7);
    BIT_CLR(reg, 7);  printf("After CLR  bit7: 0x%02X\n", reg);  // 0x00
    return 0;
}
```

---

### P66. Multiply by 2 using shift.
**Expected Output:** `5 * 2 = 10 | 5 * 4 = 20`
```c
#include <stdio.h>
int main() {
    int x = 5;
    printf("%d * 2 = %d\n", x, x << 1);   // 10
    printf("%d * 4 = %d\n", x, x << 2);   // 20
    printf("%d * 8 = %d\n", x, x << 3);   // 40
    return 0;
}
```

---

### P67. Divide by 2 using shift.
**Expected Output:** `40 / 2 = 20 | 40 / 4 = 10`
```c
#include <stdio.h>
int main() {
    int x = 40;
    printf("%d / 2 = %d\n", x, x >> 1);   // 20
    printf("%d / 4 = %d\n", x, x >> 2);   // 10
    printf("%d / 8 = %d\n", x, x >> 3);   // 5
    return 0;
}
```

---

### P68. Find missing number using XOR.
**Expected Output:** `Missing number: 4`
```c
#include <stdio.h>
int main() {
    // Array has 1..5 but missing 4
    int arr[] = {1, 2, 3, 5};
    int n = 5;
    int xor_all = 0, xor_arr = 0;

    for (int i = 1; i <= n; i++) xor_all ^= i;
    for (int i = 0; i < n-1; i++) xor_arr ^= arr[i];

    printf("Missing number: %d\n", xor_all ^ xor_arr);  // 4
    return 0;
}
```

---

### P69. Implement bit field manipulation.
**Expected Output:** GPIO config register with bit fields set
```c
#include <stdio.h>
#include <stdint.h>
typedef struct {
    uint8_t enable  : 1;
    uint8_t mode    : 2;
    uint8_t speed   : 3;
    uint8_t unused  : 2;
} GPIOConfig;

int main() {
    GPIOConfig cfg = {0};
    cfg.enable = 1;
    cfg.mode   = 2;  // 0b10
    cfg.speed  = 5;  // 0b101

    printf("Enable: %d\n", cfg.enable);
    printf("Mode:   %d\n", cfg.mode);
    printf("Speed:  %d\n", cfg.speed);
    return 0;
}
```

---

### P70. Write function simulating hardware register write.
**Expected Output:** Register read-back shows written value
```c
#include <stdio.h>
#include <stdint.h>

// Simulated hardware register (in real code: volatile uint32_t* at fixed address)
static uint32_t sim_register = 0;

void reg_write(uint32_t val) { sim_register = val; }
uint32_t reg_read(void)      { return sim_register; }
void reg_set_bits(uint32_t mask)   { sim_register |=  mask; }
void reg_clr_bits(uint32_t mask)   { sim_register &= ~mask; }

int main() {
    reg_write(0x00);
    reg_set_bits(1 << 3);     // set bit 3
    reg_set_bits(1 << 7);     // set bit 7
    printf("Register: 0x%08X\n", reg_read());  // 0x00000088
    reg_clr_bits(1 << 3);     // clear bit 3
    printf("Register: 0x%08X\n", reg_read());  // 0x00000080
    return 0;
}
```

---

# Section 4: Structures and Unions Problems (Programs 71–90)

---

### P71. Define struct for student record and print details.
**Expected Output:** `ID:1 Name:Alice Grade:95.50`
```c
#include <stdio.h>
typedef struct { int id; char name[20]; float grade; } Student;
int main() {
    Student s = {1, "Alice", 95.5f};
    printf("ID:%d Name:%s Grade:%.2f\n", s.id, s.name, s.grade);
    return 0;
}
```

---

### P72. Sort array of structures.
**Expected Output:** Sorted by grade: Bob(75) Alice(90) Charlie(95)
```c
#include <stdio.h>
#include <string.h>
typedef struct { char name[20]; int grade; } Student;
void sort(Student *arr, int n) {
    for (int i = 0; i < n-1; i++)
        for (int j = 0; j < n-i-1; j++)
            if (arr[j].grade > arr[j+1].grade) {
                Student tmp = arr[j]; arr[j] = arr[j+1]; arr[j+1] = tmp;
            }
}
int main() {
    Student s[] = {{"Alice",90},{"Bob",75},{"Charlie",95}};
    sort(s, 3);
    for (int i = 0; i < 3; i++) printf("%s(%d) ", s[i].name, s[i].grade);
    printf("\n");
    return 0;
}
```

---

### P73. Pass struct to function and modify data.
**Expected Output:** `Before: 0 | After: 99`
```c
#include <stdio.h>
typedef struct { int value; } Box;
void set_value(Box *b, int v) { b->value = v; }
int main() {
    Box b = {0};
    printf("Before: %d\n", b.value);
    set_value(&b, 99);
    printf("After: %d\n", b.value);
    return 0;
}
```

---

### P74. Create array of structures.
**Expected Output:** 3 employees with id and salary
```c
#include <stdio.h>
typedef struct { int id; char name[15]; float salary; } Employee;
int main() {
    Employee emp[] = {{1,"Alice",50000},{2,"Bob",60000},{3,"Eve",55000}};
    for (int i = 0; i < 3; i++)
        printf("ID:%d %s $%.0f\n", emp[i].id, emp[i].name, emp[i].salary);
    return 0;
}
```

---

### P75. Compare two structures.
**Expected Output:** `p1 and p2 are EQUAL | p1 and p3 are NOT EQUAL`
```c
#include <stdio.h>
typedef struct { int x; int y; } Point;
int equal(Point a, Point b) { return a.x == b.x && a.y == b.y; }
int main() {
    Point p1={3,4}, p2={3,4}, p3={1,2};
    printf("p1 and p2 are %s\n", equal(p1,p2)?"EQUAL":"NOT EQUAL");
    printf("p1 and p3 are %s\n", equal(p1,p3)?"EQUAL":"NOT EQUAL");
    return 0;
}
```

---

### P76. Calculate size of struct with padding.
**Expected Output:** Size with padding vs packed size
```c
#include <stdio.h>
struct Normal { char a; int b; char c; };
struct __attribute__((packed)) Packed { char a; int b; char c; };
int main() {
    printf("Normal size: %zu\n", sizeof(struct Normal));   // 12
    printf("Packed size: %zu\n", sizeof(struct Packed));   // 6
    return 0;
}
```

---

### P77. Implement structure for hardware register.
**Expected Output:** GPIO register bits configured and printed
```c
#include <stdio.h>
#include <stdint.h>
typedef union {
    uint32_t raw;
    struct { uint32_t enable:1; uint32_t mode:2; uint32_t speed:3; uint32_t res:26; } bits;
} GPIOReg;
int main() {
    GPIOReg r = {.raw = 0};
    r.bits.enable = 1;
    r.bits.mode   = 2;
    r.bits.speed  = 5;
    printf("Raw: 0x%08X\n", r.raw);
    printf("Enable:%d Mode:%d Speed:%d\n", r.bits.enable, r.bits.mode, r.bits.speed);
    return 0;
}
```

---

### P78. Demonstrate union memory sharing.
**Expected Output:** Writing to one member changes the others
```c
#include <stdio.h>
#include <stdint.h>
typedef union { uint32_t full; uint8_t bytes[4]; } Word;
int main() {
    Word w;
    w.full = 0x12345678;
    printf("Full: 0x%08X\n", w.full);
    printf("bytes[0]=0x%02X [1]=0x%02X [2]=0x%02X [3]=0x%02X\n",
           w.bytes[0], w.bytes[1], w.bytes[2], w.bytes[3]);
    return 0;
}
```

---

### P79. Create linked list using structures.
**Expected Output:** `10 -> 20 -> 30 -> NULL`
```c
#include <stdio.h>
#include <stdlib.h>
typedef struct Node { int val; struct Node *next; } Node;
int main() {
    Node *n1 = malloc(sizeof(Node)); n1->val = 10;
    Node *n2 = malloc(sizeof(Node)); n2->val = 20;
    Node *n3 = malloc(sizeof(Node)); n3->val = 30;
    n1->next = n2; n2->next = n3; n3->next = NULL;
    for (Node *p = n1; p; p = p->next)
        printf("%d -> ", p->val);
    printf("NULL\n");
    free(n1); free(n2); free(n3);
    return 0;
}
```

---

### P80. Implement stack using structures.
**Expected Output:** `Push 1,2,3 | Pop: 3 2 1`
```c
#include <stdio.h>
#define MAX 10
typedef struct { int data[MAX]; int top; } Stack;
void push(Stack *s, int v) { if(s->top<MAX-1) s->data[++s->top]=v; }
int  pop (Stack *s)        { return s->top>=0 ? s->data[s->top--] : -1; }
int main() {
    Stack s = {.top = -1};
    push(&s,1); push(&s,2); push(&s,3);
    printf("Pop: %d %d %d\n", pop(&s), pop(&s), pop(&s));
    return 0;
}
```

---

### P81. Implement queue using structures.
**Expected Output:** `Enqueue 1,2,3 | Dequeue: 1 2 3`
```c
#include <stdio.h>
#define MAX 10
typedef struct { int data[MAX]; int front, rear; } Queue;
void enqueue(Queue *q, int v) { q->data[q->rear++] = v; }
int  dequeue(Queue *q)        { return q->data[q->front++]; }
int main() {
    Queue q = {.front=0, .rear=0};
    enqueue(&q,1); enqueue(&q,2); enqueue(&q,3);
    printf("Dequeue: %d %d %d\n", dequeue(&q), dequeue(&q), dequeue(&q));
    return 0;
}
```

---

### P82. Nested structure example.
**Expected Output:** `Device: Sensor at 12.97, 77.59`
```c
#include <stdio.h>
typedef struct { float lat, lon; } GPS;
typedef struct { char name[20]; GPS loc; int id; } Device;
int main() {
    Device d = {"Sensor", {12.97f, 77.59f}, 1};
    printf("Device: %s at %.2f, %.2f\n", d.name, d.loc.lat, d.loc.lon);
    return 0;
}
```

---

### P83. Structure with function pointer.
**Expected Output:** `Area of rectangle: 50`
```c
#include <stdio.h>
typedef struct {
    int width, height;
    int (*area)(int, int);
} Shape;
int rect_area(int w, int h) { return w * h; }
int main() {
    Shape s = {5, 10, rect_area};
    printf("Area: %d\n", s.area(s.width, s.height));  // 50
    return 0;
}
```

---

### P84. Create struct representing sensor data.
**Expected Output:** Sensor readings printed
```c
#include <stdio.h>
typedef struct {
    uint8_t  sensor_id;
    float    temperature;
    float    humidity;
    uint32_t timestamp;
} SensorData;
int main() {
    SensorData data = {1, 25.5f, 60.2f, 1234567890};
    printf("Sensor:%d Temp:%.1f Humidity:%.1f Time:%u\n",
           data.sensor_id, data.temperature, data.humidity, data.timestamp);
    return 0;
}
```

---

### P85. Convert struct to byte stream.
**Expected Output:** Raw bytes of struct printed
```c
#include <stdio.h>
#include <stdint.h>
typedef struct __attribute__((packed)) { uint16_t x; uint16_t y; } Point;
int main() {
    Point p = {0x1234, 0x5678};
    uint8_t *bytes = (uint8_t*)&p;
    printf("Bytes: ");
    for (size_t i = 0; i < sizeof(p); i++)
        printf("0x%02X ", bytes[i]);
    printf("\n");
    return 0;
}
```

---

### P86. Demonstrate packed struct.
**Expected Output:** `Packed:6 Normal:8`
```c
#include <stdio.h>
struct Normal { uint8_t a; uint32_t b; uint8_t c; };
struct __attribute__((packed)) Packed { uint8_t a; uint32_t b; uint8_t c; };
int main() {
    printf("Normal:%zu Packed:%zu\n",
           sizeof(struct Normal), sizeof(struct Packed));
    return 0;
}
```

---

### P87. Union representing multiple data types.
**Expected Output:** Same 4 bytes shown as int, float, and bytes
```c
#include <stdio.h>
typedef union { int i; float f; uint8_t b[4]; } MultiType;
int main() {
    MultiType m;
    m.i = 0x40490FDB;  // IEEE 754 for pi
    printf("As int:   %d\n",  m.i);
    printf("As float: %.4f\n", m.f);
    printf("As bytes: %02X %02X %02X %02X\n", m.b[0],m.b[1],m.b[2],m.b[3]);
    return 0;
}
```

---

### P88. Structure pointer traversal.
**Expected Output:** All students printed via pointer
```c
#include <stdio.h>
typedef struct { int id; char name[10]; } Student;
int main() {
    Student arr[] = {{1,"Alice"},{2,"Bob"},{3,"Eve"}};
    Student *p = arr;
    for (int i = 0; i < 3; i++, p++)
        printf("ID:%d Name:%s\n", p->id, p->name);
    return 0;
}
```

---

### P89. Implement struct-based configuration system.
**Expected Output:** Config loaded and applied
```c
#include <stdio.h>
typedef struct {
    uint32_t baud_rate;
    uint8_t  data_bits;
    uint8_t  stop_bits;
    uint8_t  parity;
} UARTConfig;

void uart_apply_config(const UARTConfig *cfg) {
    printf("UART Config: baud=%u data=%d stop=%d parity=%d\n",
           cfg->baud_rate, cfg->data_bits, cfg->stop_bits, cfg->parity);
}
int main() {
    UARTConfig cfg = {115200, 8, 1, 0};
    uart_apply_config(&cfg);
    return 0;
}
```

---

### P90. Serialize struct to file.
**Expected Output:** Struct written and read back correctly
```c
#include <stdio.h>
typedef struct { int id; float value; } Record;
int main() {
    Record w = {42, 3.14f};
    FILE *f = fopen("record.bin", "wb");
    fwrite(&w, sizeof(Record), 1, f);
    fclose(f);

    Record r = {0};
    f = fopen("record.bin", "rb");
    fread(&r, sizeof(Record), 1, f);
    fclose(f);

    printf("Read back: id=%d value=%.2f\n", r.id, r.value);
    remove("record.bin");
    return 0;
}
```

---

# Section 5: Arrays and Strings Problems (Programs 91–115)

---

### P91. Reverse array.
**Expected Output:** `5 4 3 2 1`
```c
#include <stdio.h>
int main() {
    int arr[] = {1,2,3,4,5}, n = 5;
    for (int l=0,r=n-1; l<r; l++,r--) {
        int t=arr[l]; arr[l]=arr[r]; arr[r]=t;
    }
    for (int i=0; i<n; i++) printf("%d ", arr[i]);
    printf("\n");
    return 0;
}
```

---

### P92. Find maximum element in array.
**Expected Output:** `Max: 99`
```c
#include <stdio.h>
int main() {
    int arr[] = {10, 99, 20, 55, 33};
    int max = arr[0];
    for (int i=1; i<5; i++) if (arr[i]>max) max=arr[i];
    printf("Max: %d\n", max);
    return 0;
}
```

---

### P93. Find second largest number.
**Expected Output:** `Second largest: 55`
```c
#include <stdio.h>
#include <limits.h>
int main() {
    int arr[] = {10, 99, 20, 55, 33}, n = 5;
    int first = INT_MIN, second = INT_MIN;
    for (int i=0; i<n; i++) {
        if (arr[i]>first) { second=first; first=arr[i]; }
        else if (arr[i]>second && arr[i]!=first) second=arr[i];
    }
    printf("Second largest: %d\n", second);
    return 0;
}
```

---

### P94. Remove duplicates from array.
**Expected Output:** `1 2 3 4 5`
```c
#include <stdio.h>
int remove_dups(int *arr, int n) {
    int new_n = 0;
    for (int i=0; i<n; i++) {
        int found = 0;
        for (int j=0; j<new_n; j++) if (arr[j]==arr[i]) { found=1; break; }
        if (!found) arr[new_n++] = arr[i];
    }
    return new_n;
}
int main() {
    int arr[] = {1,2,2,3,4,3,5,1};
    int n = remove_dups(arr, 8);
    for (int i=0; i<n; i++) printf("%d ", arr[i]);
    printf("\n");
    return 0;
}
```

---

### P95. Rotate array left by k positions.
**Expected Output:** `{1,2,3,4,5} rotated left by 2: 3 4 5 1 2`
```c
#include <stdio.h>
void rot_left(int *a, int n, int k) {
    k %= n;
    int tmp[n];
    for (int i=0; i<n; i++) tmp[i] = a[(i+k)%n];
    for (int i=0; i<n; i++) a[i] = tmp[i];
}
int main() {
    int arr[] = {1,2,3,4,5};
    rot_left(arr, 5, 2);
    for (int i=0; i<5; i++) printf("%d ", arr[i]);
    printf("\n");
    return 0;
}
```

---

### P96. Rotate array right by k positions.
**Expected Output:** `{1,2,3,4,5} rotated right by 2: 4 5 1 2 3`
```c
#include <stdio.h>
void rot_right(int *a, int n, int k) {
    k %= n;
    int tmp[n];
    for (int i=0; i<n; i++) tmp[(i+k)%n] = a[i];
    for (int i=0; i<n; i++) a[i] = tmp[i];
}
int main() {
    int arr[] = {1,2,3,4,5};
    rot_right(arr, 5, 2);
    for (int i=0; i<5; i++) printf("%d ", arr[i]);
    printf("\n");
    return 0;
}
```

---

### P97. Merge two arrays.
**Expected Output:** `1 2 3 4 5 6`
```c
#include <stdio.h>
int main() {
    int a[]={1,3,5}, b[]={2,4,6}, merged[6];
    int i=0,j=0,k=0;
    while (i<3 && j<3)
        merged[k++] = a[i]<b[j] ? a[i++] : b[j++];
    while (i<3) merged[k++]=a[i++];
    while (j<3) merged[k++]=b[j++];
    for (int x=0; x<6; x++) printf("%d ", merged[x]);
    printf("\n");
    return 0;
}
```

---

### P98. Find missing number in array.
**Expected Output:** `Missing: 4`
```c
#include <stdio.h>
int main() {
    int arr[] = {1,2,3,5}, n = 5;  // 1..5 missing 4
    int expected = n*(n+1)/2;
    int actual = 0;
    for (int i=0; i<n-1; i++) actual += arr[i];
    printf("Missing: %d\n", expected - actual);
    return 0;
}
```

---

### P99. Reverse string without library functions.
**Expected Output:** `Reversed: olleH`
```c
#include <stdio.h>
int my_len(char *s) { int l=0; while(s[l]) l++; return l; }
void rev(char *s) {
    int l=0, r=my_len(s)-1;
    while (l<r) { char t=s[l]; s[l]=s[r]; s[r]=t; l++; r--; }
}
int main() {
    char s[] = "Hello";
    rev(s);
    printf("Reversed: %s\n", s);
    return 0;
}
```

---

### P100. Check palindrome string.
**Expected Output:** `racecar: YES | hello: NO`
```c
#include <stdio.h>
#include <string.h>
int is_palindrome(char *s) {
    int l=0, r=strlen(s)-1;
    while (l<r) { if (s[l]!=s[r]) return 0; l++; r--; }
    return 1;
}
int main() {
    printf("racecar: %s\n", is_palindrome("racecar") ? "YES" : "NO");
    printf("hello:   %s\n", is_palindrome("hello")   ? "YES" : "NO");
    return 0;
}
```

---

### P101. Count vowels and consonants.
**Expected Output:** `Vowels:2 Consonants:3 (Hello)`
```c
#include <stdio.h>
int is_vowel(char c) {
    c |= 32;  // to lowercase
    return c=='a'||c=='e'||c=='i'||c=='o'||c=='u';
}
int main() {
    char s[] = "Hello";
    int v=0, c=0;
    for (int i=0; s[i]; i++) {
        if (s[i]>='A' && s[i]<='z') {
            if (is_vowel(s[i])) v++; else c++;
        }
    }
    printf("Vowels:%d Consonants:%d\n", v, c);
    return 0;
}
```

---

### P102. Implement strlen().
**Expected Output:** `Length: 5`
```c
#include <stdio.h>
int my_strlen(const char *s) {
    int len = 0;
    while (*s++) len++;
    return len;
}
int main() {
    printf("Length: %d\n", my_strlen("Hello"));
    return 0;
}
```

---

### P103. Implement strcat().
**Expected Output:** `Hello World`
```c
#include <stdio.h>
char* my_strcat(char *dst, const char *src) {
    char *d = dst;
    while (*d) d++;          // go to end of dst
    while ((*d++ = *src++)); // copy src
    return dst;
}
int main() {
    char buf[20] = "Hello ";
    my_strcat(buf, "World");
    printf("%s\n", buf);
    return 0;
}
```

---

### P104. Implement strcmp().
**Expected Output:** `0 (equal) | -1 (less)`
```c
#include <stdio.h>
int my_strcmp(const char *a, const char *b) {
    while (*a && *a == *b) { a++; b++; }
    return (*a > *b) - (*a < *b);
}
int main() {
    printf("%d\n", my_strcmp("abc","abc"));  // 0
    printf("%d\n", my_strcmp("abc","abd"));  // -1
    printf("%d\n", my_strcmp("abd","abc"));  // 1
    return 0;
}
```

---

### P105. Find frequency of characters.
**Expected Output:** `a:1 e:1 h:1 l:3 o:2`
```c
#include <stdio.h>
int main() {
    char s[] = "hello world";
    int freq[128] = {0};
    for (int i=0; s[i]; i++) if (s[i]!=' ') freq[(int)s[i]]++;
    for (int i=0; i<128; i++)
        if (freq[i]) printf("%c:%d ", (char)i, freq[i]);
    printf("\n");
    return 0;
}
```

---

### P106. Remove spaces from string.
**Expected Output:** `HelloWorld`
```c
#include <stdio.h>
void remove_spaces(char *s) {
    int i=0, j=0;
    while (s[i]) { if (s[i]!=' ') s[j++]=s[i]; i++; }
    s[j] = '\0';
}
int main() {
    char s[] = "Hello World";
    remove_spaces(s);
    printf("%s\n", s);
    return 0;
}
```

---

### P107. Convert lowercase to uppercase.
**Expected Output:** `HELLO WORLD`
```c
#include <stdio.h>
void to_upper(char *s) {
    while (*s) { if (*s>='a' && *s<='z') *s -= 32; s++; }
}
int main() {
    char s[] = "hello world";
    to_upper(s);
    printf("%s\n", s);
    return 0;
}
```

---

### P108. Find substring in string.
**Expected Output:** `Found 'World' at index 6`
```c
#include <stdio.h>
int find_sub(const char *s, const char *sub) {
    for (int i=0; s[i]; i++) {
        int j=0;
        while (sub[j] && s[i+j]==sub[j]) j++;
        if (!sub[j]) return i;
    }
    return -1;
}
int main() {
    int idx = find_sub("Hello World", "World");
    printf("Found 'World' at index %d\n", idx);
    return 0;
}
```

---

### P109. Tokenize string manually.
**Expected Output:** `Token: Hello | Token: World | Token: Test`
```c
#include <stdio.h>
#include <string.h>
int main() {
    char s[] = "Hello World Test";
    char *token = strtok(s, " ");
    while (token) {
        printf("Token: %s\n", token);
        token = strtok(NULL, " ");
    }
    return 0;
}
```

---

### P110. Implement string compression.
**Expected Output:** `aabbccc -> a2b2c3`
```c
#include <stdio.h>
void compress(const char *s, char *out) {
    int i=0, j=0;
    while (s[i]) {
        out[j++] = s[i];
        int cnt = 0;
        char ch = s[i];
        while (s[i]==ch) { i++; cnt++; }
        out[j++] = '0' + cnt;
    }
    out[j] = '\0';
}
int main() {
    char out[50];
    compress("aabbccc", out);
    printf("%s\n", out);  // a2b2c3
    return 0;
}
```

---

### P111. Reverse words in sentence.
**Expected Output:** `World Hello`
```c
#include <stdio.h>
#include <string.h>
void rev_str(char *s, int l, int r) {
    while (l<r) { char t=s[l]; s[l]=s[r]; s[r]=t; l++; r--; }
}
void rev_words(char *s) {
    int n = strlen(s);
    rev_str(s, 0, n-1);
    int start = 0;
    for (int i=0; i<=n; i++) {
        if (s[i]==' ' || s[i]=='\0') {
            rev_str(s, start, i-1);
            start = i+1;
        }
    }
}
int main() {
    char s[] = "Hello World";
    rev_words(s);
    printf("%s\n", s);
    return 0;
}
```

---

### P112. Implement circular buffer.
**Expected Output:** Buffer wrap-around demonstrated
```c
#include <stdio.h>
#define SIZE 4
typedef struct { int buf[SIZE]; int head, tail, count; } CircBuf;
void cb_push(CircBuf *b, int v) {
    if (b->count<SIZE) { b->buf[b->tail]= v; b->tail=(b->tail+1)%SIZE; b->count++; }
}
int cb_pop(CircBuf *b) {
    if (!b->count) return -1;
    int v = b->buf[b->head]; b->head=(b->head+1)%SIZE; b->count--;
    return v;
}
int main() {
    CircBuf cb = {.head=0,.tail=0,.count=0};
    cb_push(&cb,10); cb_push(&cb,20); cb_push(&cb,30); cb_push(&cb,40);
    cb_push(&cb,50);  // overflow — dropped
    printf("%d %d %d %d\n", cb_pop(&cb),cb_pop(&cb),cb_pop(&cb),cb_pop(&cb));
    return 0;
}
```

---

### P113. Find common elements in arrays.
**Expected Output:** `Common: 3 5`
```c
#include <stdio.h>
int main() {
    int a[] = {1,2,3,4,5}, b[] = {3,5,7,9};
    for (int i=0; i<5; i++)
        for (int j=0; j<4; j++)
            if (a[i]==b[j]) printf("%d ", a[i]);
    printf("\n");
    return 0;
}
```

---

### P114. Implement binary search.
**Expected Output:** `Found 40 at index 3`
```c
#include <stdio.h>
int binary_search(int *arr, int n, int target) {
    int lo=0, hi=n-1;
    while (lo<=hi) {
        int mid = (lo+hi)/2;
        if (arr[mid]==target) return mid;
        else if (arr[mid]<target) lo=mid+1;
        else hi=mid-1;
    }
    return -1;
}
int main() {
    int arr[] = {10,20,30,40,50};
    int idx = binary_search(arr, 5, 40);
    printf("Found 40 at index %d\n", idx);
    return 0;
}
```

---

### P115. Implement array based stack.
**Expected Output:** `Push 1,2,3 | Pop: 3 2 1 | Empty: yes`
```c
#include <stdio.h>
#define MAX 10
int stk[MAX], top = -1;
void push(int v) { if (top<MAX-1) stk[++top]=v; }
int  pop()       { return top>=0 ? stk[top--] : -1; }
int  empty()     { return top == -1; }
int main() {
    push(1); push(2); push(3);
    printf("Pop: %d %d %d\n", pop(), pop(), pop());
    printf("Empty: %s\n", empty() ? "yes" : "no");
    return 0;
}
```

---

# Section 6: Function and Recursion Problems (Programs 116–135)

---

### P116. Factorial using recursion.
**Expected Output:** `5! = 120`
```c
#include <stdio.h>
int fact(int n) { return n<=1 ? 1 : n * fact(n-1); }
int main() { printf("5! = %d\n", fact(5)); return 0; }
```

---

### P117. Fibonacci using recursion.
**Expected Output:** `0 1 1 2 3 5 8 13 21 34`
```c
#include <stdio.h>
int fib(int n) { return n<=1 ? n : fib(n-1)+fib(n-2); }
int main() {
    for (int i=0; i<10; i++) printf("%d ", fib(i));
    printf("\n");
    return 0;
}
```

---

### P118. Binary search using recursion.
**Expected Output:** `Found 30 at index 2`
```c
#include <stdio.h>
int bsearch_r(int *a, int lo, int hi, int t) {
    if (lo>hi) return -1;
    int mid=(lo+hi)/2;
    if (a[mid]==t) return mid;
    return a[mid]<t ? bsearch_r(a,mid+1,hi,t) : bsearch_r(a,lo,mid-1,t);
}
int main() {
    int arr[] = {10,20,30,40,50};
    printf("Found 30 at index %d\n", bsearch_r(arr,0,4,30));
    return 0;
}
```

---

### P119. Tower of Hanoi.
**Expected Output:** Move sequence for 3 disks
```c
#include <stdio.h>
void hanoi(int n, char from, char to, char via) {
    if (n==1) { printf("Move disk 1 from %c to %c\n", from, to); return; }
    hanoi(n-1, from, via, to);
    printf("Move disk %d from %c to %c\n", n, from, to);
    hanoi(n-1, via, to, from);
}
int main() { hanoi(3, 'A', 'C', 'B'); return 0; }
```

---

### P120. Check prime number using function.
**Expected Output:** `7: prime | 10: not prime`
```c
#include <stdio.h>
int is_prime(int n) {
    if (n<2) return 0;
    for (int i=2; i*i<=n; i++) if (n%i==0) return 0;
    return 1;
}
int main() {
    printf("7:  %s\n", is_prime(7)  ? "prime" : "not prime");
    printf("10: %s\n", is_prime(10) ? "prime" : "not prime");
    return 0;
}
```

---

### P121. GCD using recursion.
**Expected Output:** `GCD(48,18) = 6`
```c
#include <stdio.h>
int gcd(int a, int b) { return b==0 ? a : gcd(b, a%b); }
int main() { printf("GCD(48,18) = %d\n", gcd(48,18)); return 0; }
```

---

### P122. Power function using recursion.
**Expected Output:** `2^10 = 1024`
```c
#include <stdio.h>
long power(int base, int exp) {
    if (exp==0) return 1;
    return base * power(base, exp-1);
}
int main() { printf("2^10 = %ld\n", power(2,10)); return 0; }
```

---

### P123. Implement callback function.
**Expected Output:** `Event fired! Result = 100`
```c
#include <stdio.h>
typedef void (*Callback)(int);
void on_done(int result) { printf("Event fired! Result = %d\n", result); }
void process(int x, Callback cb) { cb(x * x); }
int main() { process(10, on_done); return 0; }
```

---

### P124. Demonstrate function pointer usage.
**Expected Output:** `Add:8 Sub:2 Mul:15`
```c
#include <stdio.h>
int add(int a,int b){return a+b;}
int sub(int a,int b){return a-b;}
int mul(int a,int b){return a*b;}
int main() {
    int (*ops[])(int,int) = {add, sub, mul};
    const char *names[] = {"Add","Sub","Mul"};
    for (int i=0; i<3; i++)
        printf("%s:%d\n", names[i], ops[i](5,3));
    return 0;
}
```

---

### P125. Write function returning pointer.
**Expected Output:** `Max: 20`
```c
#include <stdio.h>
int* get_max(int *a, int *b) { return (*a > *b) ? a : b; }
int main() {
    int x=10, y=20;
    int *m = get_max(&x, &y);
    printf("Max: %d\n", *m);
    return 0;
}
```

---

### P126. Pass function pointer to another function.
**Expected Output:** `Applied: 25`
```c
#include <stdio.h>
int square(int x) { return x*x; }
int apply(int x, int(*fn)(int)) { return fn(x); }
int main() { printf("Applied: %d\n", apply(5, square)); return 0; }
```

---

### P127. Implement calculator using function pointers.
**Expected Output:** `+:8 -:2 *:15 /:1`
```c
#include <stdio.h>
int add(int a,int b){return a+b;}
int sub(int a,int b){return a-b;}
int mul(int a,int b){return a*b;}
int dvd(int a,int b){return b?a/b:0;}
int main() {
    int(*calc[])(int,int)={add,sub,mul,dvd};
    char ops[]="{+,-,*,/}";
    char sym[]="+-*/";
    for(int i=0;i<4;i++) printf("%c:%d\n",sym[i],calc[i](5,3));
    return 0;
}
```

---

### P128. Write function to swap structures.
**Expected Output:** `After swap: a={2,Bob} b={1,Alice}`
```c
#include <stdio.h>
typedef struct { int id; char name[10]; } Person;
void swap(Person *a, Person *b) { Person t=*a; *a=*b; *b=t; }
int main() {
    Person a={1,"Alice"}, b={2,"Bob"};
    swap(&a, &b);
    printf("a={%d,%s} b={%d,%s}\n", a.id,a.name, b.id,b.name);
    return 0;
}
```

---

### P129. Recursive string reversal.
**Expected Output:** `Reversed: olleH`
```c
#include <stdio.h>
#include <string.h>
void rev(char *s, int l, int r) {
    if (l>=r) return;
    char t=s[l]; s[l]=s[r]; s[r]=t;
    rev(s, l+1, r-1);
}
int main() {
    char s[]="Hello";
    rev(s, 0, strlen(s)-1);
    printf("Reversed: %s\n", s);
    return 0;
}
```

---

### P130. Recursive linked list traversal.
**Expected Output:** `1 2 3 4 5`
```c
#include <stdio.h>
#include <stdlib.h>
typedef struct Node { int v; struct Node *next; } Node;
void print_r(Node *n) { if(!n) {printf("\n");return;} printf("%d ",n->v); print_r(n->next); }
int main() {
    Node *h=malloc(sizeof(Node)); h->v=1;
    h->next=malloc(sizeof(Node)); h->next->v=2;
    h->next->next=malloc(sizeof(Node)); h->next->next->v=3;
    h->next->next->next=malloc(sizeof(Node)); h->next->next->next->v=4;
    h->next->next->next->next=malloc(sizeof(Node));
    h->next->next->next->next->v=5;
    h->next->next->next->next->next=NULL;
    print_r(h);
    return 0;
}
```

---

### P131. Sum digits using recursion.
**Expected Output:** `Sum of digits of 1234 = 10`
```c
#include <stdio.h>
int sum_digits(int n) { return n==0 ? 0 : n%10 + sum_digits(n/10); }
int main() { printf("Sum of digits of 1234 = %d\n", sum_digits(1234)); return 0; }
```

---

### P132. Reverse number using recursion.
**Expected Output:** `Reverse of 12345 = 54321`
```c
#include <stdio.h>
void rev_num(int n) {
    if (n==0) return;
    printf("%d", n%10);
    rev_num(n/10);
}
int main() { printf("Reverse of 12345 = "); rev_num(12345); printf("\n"); return 0; }
```

---

### P133. Print binary representation.
**Expected Output:** `Binary of 13: 1101`
```c
#include <stdio.h>
void print_bin(int n) {
    if (n>1) print_bin(n/2);
    printf("%d", n%2);
}
int main() { printf("Binary of 13: "); print_bin(13); printf("\n"); return 0; }
```

---

### P134. Recursive array traversal.
**Expected Output:** `1 2 3 4 5`
```c
#include <stdio.h>
void print_arr(int *a, int n) {
    if (n==0) { printf("\n"); return; }
    printf("%d ", *a);
    print_arr(a+1, n-1);
}
int main() {
    int arr[] = {1,2,3,4,5};
    print_arr(arr, 5);
    return 0;
}
```

---

### P135. Recursive tree traversal simulation.
**Expected Output:** Inorder traversal: 1 2 3 4 5
```c
#include <stdio.h>
#include <stdlib.h>
typedef struct Node { int v; struct Node *left, *right; } Node;
Node* new_node(int v) {
    Node *n=malloc(sizeof(Node)); n->v=v; n->left=n->right=NULL; return n;
}
void inorder(Node *n) {
    if (!n) return;
    inorder(n->left);
    printf("%d ", n->v);
    inorder(n->right);
}
int main() {
    Node *root = new_node(3);
    root->left = new_node(2); root->right = new_node(5);
    root->left->left = new_node(1); root->right->left = new_node(4);
    printf("Inorder: ");
    inorder(root);
    printf("\n");
    return 0;
}
```

---

# Section 7: Debugging and Runtime Problems (Programs 136–150)

---

### P136. Find bug in pointer dereference code.
**Expected Output:** Shows bug and fix
```c
#include <stdio.h>
#include <stdlib.h>
// BUGGY version:
void buggy() {
    int *p;          // uninitialized — wild pointer
    // *p = 10;      // BUG: dereferencing wild pointer!
    printf("Bug: dereferencing uninitialized pointer\n");
}
// FIXED version:
void fixed() {
    int *p = NULL;
    p = (int*)malloc(sizeof(int));
    if (p) { *p = 10; printf("Fixed: value = %d\n", *p); free(p); }
}
int main() { buggy(); fixed(); return 0; }
```

---

### P137. Detect memory leak in program.
**Expected Output:** Shows leak vs clean version
```c
#include <stdio.h>
#include <stdlib.h>
void with_leak() {
    int *p = malloc(100);
    printf("Allocated — NOT freed (leak!)\n");
    // missing free(p)
}
void without_leak() {
    int *p = malloc(100);
    printf("Allocated\n");
    free(p); p=NULL;
    printf("Freed — no leak\n");
}
int main() { with_leak(); without_leak(); return 0; }
// Run with: valgrind --leak-check=full ./prog
```

---

### P138. Fix buffer overflow bug.
**Expected Output:** Safe: `Hell` (truncated, not crashed)
```c
#include <stdio.h>
#include <string.h>
int main() {
    char buf[5];
    const char *src = "Hello World";
    // BUGGY: strcpy(buf, src);  // overflow!

    // FIXED:
    strncpy(buf, src, sizeof(buf)-1);
    buf[sizeof(buf)-1] = '\0';
    printf("Safe result: '%s'\n", buf);
    return 0;
}
```

---

### P139. Fix dangling pointer issue.
**Expected Output:** Safe access, no dangling pointer
```c
#include <stdio.h>
#include <stdlib.h>
int main() {
    int *p = (int*)malloc(sizeof(int));
    *p = 42;
    printf("Value: %d\n", *p);

    free(p);
    p = NULL;  // FIX: always NULL after free

    if (p != NULL) { printf("%d\n", *p); }  // won't execute
    else { printf("Pointer is NULL — safe\n"); }
    return 0;
}
```

---

### P140. Detect race condition example.
**Expected Output:** Shows problem and mutex fix
```c
#include <stdio.h>
// Simulated race condition (single-threaded illustration):
int shared_counter = 0;

// In multi-threaded code, two threads doing this simultaneously
// would produce incorrect results:
void unsafe_increment() {
    // Thread 1: reads 0
    // Thread 2: reads 0  <-- race!
    // Thread 1: writes 1
    // Thread 2: writes 1  <-- lost update! should be 2
    shared_counter++;
}

int main() {
    for (int i = 0; i < 100; i++) unsafe_increment();
    printf("Counter (single thread): %d\n", shared_counter);
    printf("In multi-thread without mutex, result would be wrong\n");
    printf("Fix: use pthread_mutex_lock/unlock around counter++\n");
    return 0;
}
```

---

### P141. Identify stack overflow cause.
**Expected Output:** Identifies deep recursion as cause
```c
#include <stdio.h>
// DEMONSTRATES the cause — not actual overflow (limited depth)
int depth = 0;
void show_overflow_cause(int limit) {
    if (depth >= limit) {
        printf("Stopped at depth %d (would overflow without limit)\n", depth);
        return;
    }
    depth++;
    show_overflow_cause(limit);
}
int main() {
    printf("Showing recursion depth (limited for safety):\n");
    show_overflow_cause(10);
    printf("Real stack overflow: infinite recursion or huge local arrays\n");
    return 0;
}
```

---

### P142. Debug segmentation fault.
**Expected Output:** Shows causes and safe fix
```c
#include <stdio.h>
#include <stdlib.h>
// Common segfault causes and fixes:
int main() {
    // Cause 1: NULL deref — FIXED
    int *p = NULL;
    if (p) printf("%d\n", *p); else printf("Fix1: NULL check prevents segfault\n");

    // Cause 2: Out of bounds — FIXED
    int arr[3] = {1,2,3};
    int idx = 2;  // was 5 — out of bounds
    if (idx < 3) printf("Fix2: arr[%d]=%d\n", idx, arr[idx]);

    // Cause 3: Use after free — FIXED
    int *q = malloc(4); *q = 99;
    free(q); q = NULL;
    if (q) printf("%d\n", *q); else printf("Fix3: NULL check after free\n");

    return 0;
}
```

---

### P143. Find incorrect pointer arithmetic bug.
**Expected Output:** Shows wrong vs correct pointer stepping
```c
#include <stdio.h>
int main() {
    int arr[] = {10, 20, 30, 40, 50};

    // BUGGY: treating int* as byte pointer
    char *bad = (char*)arr;
    // bad += 1 would move 1 byte, not 4!

    // FIXED: use correct type
    int *good = arr;
    for (int i = 0; i < 5; i++) {
        printf("arr[%d] = %d (addr: %p)\n", i, *good, (void*)good);
        good++;  // correctly moves 4 bytes
    }
    return 0;
}
```

---

### P144. Fix string copy overflow.
**Expected Output:** Safe truncated copy
```c
#include <stdio.h>
#include <string.h>
// Safe string copy with guaranteed null termination
void safe_copy(char *dst, const char *src, int dst_size) {
    strncpy(dst, src, dst_size - 1);
    dst[dst_size - 1] = '\0';
}
int main() {
    char small_buf[6];
    // BUGGY: strcpy(small_buf, "Hello World"); — overflow!
    // FIXED:
    safe_copy(small_buf, "Hello World", sizeof(small_buf));
    printf("Safe copy: '%s'\n", small_buf);  // "Hello"
    return 0;
}
```

---

### P145. Analyze uninitialized variable bug.
**Expected Output:** Shows risk and fix
```c
#include <stdio.h>
int main() {
    // BUGGY: uninitialized variable
    int x;  // garbage value
    // if (x > 0)  // UB: x is not initialized!

    // FIXED: always initialize
    int y = 0;
    if (y > 0) printf("Positive\n");
    else printf("Fixed: y=%d (properly initialized to 0)\n", y);

    // In embedded: uninitialized vars can cause spurious behavior
    printf("Always initialize variables!\n");
    return 0;
}
```

---

### P146. Fix infinite loop bug.
**Expected Output:** `Loop ran 5 times — terminated correctly`
```c
#include <stdio.h>
int main() {
    int i = 0;
    int count = 0;

    // BUGGY: while (i >= 0) { i++; }  // never exits!

    // FIXED: correct termination condition
    while (i < 5) {
        i++;
        count++;
    }
    printf("Loop ran %d times — terminated correctly\n", count);
    return 0;
}
```

---

### P147. Debug struct alignment issue.
**Expected Output:** Shows padding and how to fix it
```c
#include <stdio.h>
#include <stddef.h>

struct Inefficient { char a; int b; char c; };   // 12 bytes with padding
struct Efficient   { int b; char a; char c; };   // 8 bytes — reordered

int main() {
    printf("Inefficient size: %zu\n", sizeof(struct Inefficient));  // 12
    printf("Efficient   size: %zu\n", sizeof(struct Efficient));    // 8

    printf("Offset a in Inefficient: %zu\n", offsetof(struct Inefficient, a));  // 0
    printf("Offset b in Inefficient: %zu\n", offsetof(struct Inefficient, b));  // 4
    printf("Offset c in Inefficient: %zu\n", offsetof(struct Inefficient, c));  // 8

    return 0;
}
```

---

### P148. Detect array out-of-bounds error.
**Expected Output:** Shows bounds checking
```c
#include <stdio.h>
#define SIZE 5
int safe_get(int *arr, int n, int idx) {
    if (idx < 0 || idx >= n) {
        printf("ERROR: index %d out of bounds [0..%d]\n", idx, n-1);
        return -1;
    }
    return arr[idx];
}
int main() {
    int arr[SIZE] = {10, 20, 30, 40, 50};
    printf("arr[2] = %d\n",  safe_get(arr, SIZE, 2));   // 30
    printf("arr[7] = %d\n",  safe_get(arr, SIZE, 7));   // ERROR
    printf("arr[-1] = %d\n", safe_get(arr, SIZE, -1));  // ERROR
    return 0;
}
```

---

### P149. Analyze incorrect bit manipulation.
**Expected Output:** Shows wrong vs correct bit ops
```c
#include <stdio.h>
int main() {
    uint8_t reg = 0xFF;

    // BUGGY: forgetting to mask — may affect wrong bits
    reg = reg | 1<<8;   // BUG: bit 8 doesn't exist in uint8_t!
    printf("Bug result (8-bit reg): 0x%X\n", reg);  // 0xFF — overflowed

    // FIXED: stay within bit width
    reg = 0xFF;
    reg |= (1 << 3);   // correct — bit 3 within 8-bit range
    printf("Fix result: 0x%02X\n", reg);  // 0xFF (already set)

    reg = 0x00;
    reg |= (1 << 3);
    printf("Set bit 3: 0x%02X\n", reg);  // 0x08
    return 0;
}
```

---

### P150. Debug incorrect dynamic memory usage.
**Expected Output:** Shows common dynamic memory bugs and fixes
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    // BUG 1: Not checking malloc return
    // FIXED:
    int *p = (int*)malloc(5 * sizeof(int));
    if (!p) { printf("malloc failed\n"); return 1; }
    printf("Fix1: checked malloc return\n");

    // BUG 2: Accessing beyond allocated size
    // FIXED: stay within bounds
    for (int i = 0; i < 5; i++) p[i] = i;  // correct: 0..4 only
    printf("Fix2: p[4]=%d (within bounds)\n", p[4]);

    // BUG 3: Double free
    // FIXED: NULL after free
    free(p); p = NULL;
    free(p);  // safe: free(NULL) is no-op
    printf("Fix3: safe double-free (NULL after first free)\n");

    return 0;
}
```

---

*End of 150 Programming Problems — Practice all of these and you will be fully prepared for any embedded C coding interview.*
