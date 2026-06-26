# C Interview Preparation: 38 Questions with Hints, Explanations, and Runnable C Programs

This file covers 38 beginner-to-intermediate C interview questions. Each section includes:
- **Question**
- **Hint**
- **Simple explanation**
- **Runnable C program**

---

## 1. What is the difference between `char str[] = "hello"` and `char *str = "hello"`?

**Hint:** One creates an array, the other points to a string literal.

**Simple explanation:** `char str[] = "hello"` creates a modifiable character array containing `h e l l o \0`. `char *str = "hello"` points to a string literal, which should not be modified.

```c
#include <stdio.h>

int main() {
    char a[] = "hello";
    char *b = "hello";

    a[0] = 'H';
    printf("a = %s\n", a);
    printf("b = %s\n", b);

    /* b[0] = 'H'; */
    /* invalid: modifying string literal is undefined behavior */

    return 0;
}
```

---

## 2. What is pass-by-value vs pass-by-pointer in C?

**Hint:** C passes everything by value, but a pointer value can point to original data.

**Simple explanation:** In pass-by-value, the function gets a copy, so changes do not affect the original. With a pointer, the function gets the address and can modify the original variable through it.

```c
#include <stdio.h>

void byValue(int x) {
    x = 20;
}

void byPointer(int *x) {
    *x = 20;
}

int main() {
    int a = 10, b = 10;
    byValue(a);
    byPointer(&b);
    printf("a = %d, b = %d\n", a, b);
    return 0;
}
```

---

## 3. What is a NULL pointer? What happens if you dereference it?

**Hint:** NULL means the pointer points to no valid object.

**Simple explanation:** A NULL pointer does not point to usable memory. Dereferencing it causes undefined behavior, often a crash.

```c
#include <stdio.h>

int main() {
    int *p = NULL;
    printf("p = %p\n", (void *)p);
    if (p == NULL) {
        printf("Pointer is NULL, do not dereference it.\n");
    }
    return 0;
}
```

---

## 4. What is the difference between `const int *p` and `int * const p`?

**Hint:** One makes the value constant through the pointer, the other makes the pointer itself constant.

**Simple explanation:** `const int *p` means you cannot change the value through `p`, but `p` can point somewhere else. `int * const p` means `p` must keep pointing to the same address, but the value can be changed.

```c
#include <stdio.h>

int main() {
    int a = 10, b = 20;

    const int *p1 = &a;
    p1 = &b;
    printf("*p1 = %d\n", *p1);

    int * const p2 = &a;
    *p2 = 15;
    printf("a = %d\n", a);

    return 0;
}
```

---

## 5. What is the difference between declaration and definition?

**Hint:** Declaration introduces the name, definition creates storage or body.

**Simple explanation:** A declaration tells the compiler that something exists. A definition actually allocates memory for a variable or provides the function body.

```c
#include <stdio.h>

int add(int a, int b);      /* declaration */
int globalValue = 5;        /* definition */

int add(int a, int b) {     /* definition */
    return a + b;
}

int main() {
    printf("sum = %d, globalValue = %d\n", add(2, 3), globalValue);
    return 0;
}
```

---

## 6. What does `static` do?

**Hint:** Try it for a local variable inside a function.

**Simple explanation:** A static local variable is initialized only once and keeps its value between function calls.

```c
#include <stdio.h>

void counter(void) {
    static int x = 0;
    x++;
    printf("x = %d\n", x);
}

int main() {
    counter();
    counter();
    counter();
    return 0;
}
```

---

## 7. What is `extern` and when is it used?

**Hint:** It is used when the variable is defined somewhere else.

**Simple explanation:** `extern` declares a variable or function that is defined in another file or later in the same file. It does not allocate new storage.

```c
#include <stdio.h>

int x = 42;
extern int x;

int main() {
    printf("x = %d\n", x);
    return 0;
}
```

---

## 8. What is the difference between `printf` and `fprintf`?

**Hint:** One writes to standard output, the other writes to any stream.

**Simple explanation:** `printf` writes formatted output to the console. `fprintf` writes formatted output to a specified file or stream.

```c
#include <stdio.h>

int main() {
    FILE *fp = fopen("q8_output.txt", "w");
    if (fp == NULL) {
        printf("Failed to open file\n");
        return 1;
    }

    printf("This goes to console\n");
    fprintf(fp, "This goes to file\n");
    fclose(fp);
    return 0;
}
```

---

## 9. Why is `gets()` dangerous and what should be used instead?

**Hint:** Think about buffer size.

**Simple explanation:** `gets()` is dangerous because it does not know the destination buffer size and can overflow memory. Use `fgets()` instead because it limits how many characters are read.

```c
#include <stdio.h>

int main() {
    char buf[8];
    printf("Enter text: ");
    if (fgets(buf, sizeof(buf), stdin) != NULL) {
        printf("Read safely: %s", buf);
    }
    return 0;
}
```

---

## 10. What does `malloc()` return on failure?

**Hint:** Always compare against a special pointer value.

**Simple explanation:** `malloc()` returns `NULL` when memory allocation fails. You must check for `NULL` before using the pointer.

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    int *p = malloc(5 * sizeof(int));
    if (p == NULL) {
        printf("Allocation failed\n");
        return 1;
    }
    printf("Allocation succeeded\n");
    free(p);
    return 0;
}
```

---

## 11. Reverse a string without using library functions.

**Hint:** Use two indices or two pointers.

**Simple explanation:** Keep one pointer/index at the start and one at the end. Swap the characters and move inward until they meet.

```c
#include <stdio.h>

void reverse(char s[]) {
    int len = 0;
    while (s[len] != '\0') len++;

    int i = 0, j = len - 1;
    while (i < j) {
        char temp = s[i];
        s[i] = s[j];
        s[j] = temp;
        i++;
        j--;
    }
}

int main() {
    char s[] = "hello";
    reverse(s);
    printf("%s\n", s);
    return 0;
}
```

---

## 12. Find string length without using `strlen()`.

**Hint:** Count until `\0`.

**Simple explanation:** C strings end with a null terminator. Count characters until that terminator is reached.

```c
#include <stdio.h>

int my_strlen(const char s[]) {
    int count = 0;
    while (s[count] != '\0') {
        count++;
    }
    return count;
}

int main() {
    char s[] = "interview";
    printf("length = %d\n", my_strlen(s));
    return 0;
}
```

---

## 13. Reverse an array in place.

**Hint:** Swap first with last.

**Simple explanation:** Use two indices, one at the beginning and one at the end, and swap elements until the middle is reached.

```c
#include <stdio.h>

void reverseArray(int arr[], int n) {
    int i = 0, j = n - 1;
    while (i < j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
        i++;
        j--;
    }
}

int main() {
    int arr[] = {1, 2, 3, 4, 5};
    int n = 5;
    reverseArray(arr, n);
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
    return 0;
}
```

---

## 14. Find the largest and second largest elements in an array.

**Hint:** Track two values while scanning once.

**Simple explanation:** Keep one variable for the largest and one for the second largest. Update both carefully when a new maximum is found.

```c
#include <stdio.h>
#include <limits.h>

int main() {
    int arr[] = {5, 1, 9, 7, 3};
    int n = 5;
    int largest = INT_MIN, second = INT_MIN;

    for (int i = 0; i < n; i++) {
        if (arr[i] > largest) {
            second = largest;
            largest = arr[i];
        } else if (arr[i] > second && arr[i] != largest) {
            second = arr[i];
        }
    }

    printf("largest = %d, second = %d\n", largest, second);
    return 0;
}
```

---

## 15. Implement bubble sort.

**Hint:** Repeatedly compare adjacent elements.

**Simple explanation:** Bubble sort compares each pair of adjacent elements and swaps them if they are in the wrong order. After each pass, the largest unsorted element moves to the end.

```c
#include <stdio.h>

void bubbleSort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

int main() {
    int arr[] = {2, 1, 5, 3, 4};
    int n = 5;
    bubbleSort(arr, n);
    for (int i = 0; i < n; i++) printf("%d ", arr[i]);
    printf("\n");
    return 0;
}
```

---

## 16. Implement linear search.

**Hint:** Check each element one by one.

**Simple explanation:** Linear search scans the array from left to right until the target is found or the array ends.

```c
#include <stdio.h>

int linearSearch(int arr[], int n, int key) {
    for (int i = 0; i < n; i++) {
        if (arr[i] == key) return i;
    }
    return -1;
}

int main() {
    int arr[] = {4, 7, 2, 9, 1};
    printf("index = %d\n", linearSearch(arr, 5, 9));
    return 0;
}
```

---

## 17. Implement binary search and explain when it works.

**Hint:** It needs sorted data.

**Simple explanation:** Binary search repeatedly cuts the search space in half. It only works correctly when the array is sorted.

```c
#include <stdio.h>

int binarySearch(int arr[], int n, int key) {
    int low = 0, high = n - 1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        if (arr[mid] == key) return mid;
        if (arr[mid] < key) low = mid + 1;
        else high = mid - 1;
    }
    return -1;
}

int main() {
    int arr[] = {1, 2, 3, 4, 5, 6};
    printf("index = %d\n", binarySearch(arr, 6, 4));
    return 0;
}
```

---

## 18. What does `sizeof(arr)` return inside vs outside a function?

**Hint:** Arrays decay to pointers in function parameters.

**Simple explanation:** Outside the function, `sizeof(arr)` returns total size of the whole array. Inside a function parameter, the array is treated like a pointer, so `sizeof(arr)` returns pointer size.

```c
#include <stdio.h>

void showSize(int arr[]) {
    printf("Inside function: %zu\n", sizeof(arr));
}

int main() {
    int arr[5];
    printf("Outside function: %zu\n", sizeof(arr));
    showSize(arr);
    return 0;
}
```

---

## 19. What is buffer overflow and why is it dangerous?

**Hint:** It means writing past allocated memory.

**Simple explanation:** A buffer overflow happens when more data is written than a buffer can hold. It can corrupt memory, crash the program, or create security vulnerabilities.

```c
#include <stdio.h>
#include <string.h>

int main() {
    char dst[8];
    const char *src = "hello";

    strncpy(dst, src, sizeof(dst) - 1);
    dst[sizeof(dst) - 1] = '\0';

    printf("safe copy: %s\n", dst);
    return 0;
}
```

---

## 20. What is the difference between `malloc()` and `calloc()`?

**Hint:** One zero-initializes.

**Simple explanation:** `malloc()` allocates memory but does not initialize it. `calloc()` allocates memory and initializes all bytes to zero.

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    int *a = malloc(3 * sizeof(int));
    int *b = calloc(3, sizeof(int));

    if (a == NULL || b == NULL) {
        free(a);
        free(b);
        return 1;
    }

    printf("calloc values: %d %d %d\n", b[0], b[1], b[2]);

    free(a);
    free(b);
    return 0;
}
```

---

## 21. Swap two integers using pointers.

**Hint:** Pass addresses, not values.

**Simple explanation:** Use a temporary variable to exchange the values stored at the two addresses.

```c
#include <stdio.h>

void swap(int *a, int *b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int main() {
    int x = 5, y = 10;
    swap(&x, &y);
    printf("x = %d, y = %d\n", x, y);
    return 0;
}
```

---

## 22. What is a dangling pointer? Give an example.

**Hint:** It points to memory that is no longer valid.

**Simple explanation:** A dangling pointer points to memory that has already been freed or gone out of scope. Using it is undefined behavior. Assign the buf to NULL to avoid dangling pointer.

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    int *p = malloc(sizeof(int));
    if (p == NULL) return 1;

    *p = 123;
    free(p);
    p = NULL; /* avoid dangling pointer */

    if (p == NULL) {
        printf("Pointer cleared after free\n");
    }
    return 0;
}
```

---

## 23. What happens if `free()` is called twice on the same pointer?

**Hint:** It is undefined behavior.

**Simple explanation:** Calling `free()` twice on the same pointer can corrupt memory management structures and may crash the program. A common habit is to set the pointer to `NULL` after `free()`.

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    int *p = malloc(sizeof(int));
    if (p == NULL) return 1;

    free(p);
    p = NULL;

    if (p != NULL) {
        free(p);
    }

    printf("Freed safely once\n");
    return 0;
}
```

---

## 24. Write a function to dynamically allocate an array of N integers.

**Hint:** Use `malloc(n * sizeof(int))`.

**Simple explanation:** Allocate enough bytes for `N` integers, check for `NULL`, and return the pointer.

```c
#include <stdio.h>
#include <stdlib.h>

int *createArray(int n) {
    int *arr = malloc(n * sizeof(int));
    return arr;
}

int main() {
    int n = 5;
    int *arr = createArray(n);
    if (arr == NULL) {
        printf("Allocation failed\n");
        return 1;
    }

    for (int i = 0; i < n; i++) arr[i] = i + 1;
    for (int i = 0; i < n; i++) printf("%d ", arr[i]);
    printf("\n");

    free(arr);
    return 0;
}
```

---

## 25. How do you clean up resources properly using a single cleanup block (`goto cleanup`)?

**Hint:** Acquire resources, and on any failure jump to one cleanup section.

**Simple explanation:** In C, a common pattern is to use one cleanup label that releases resources in reverse order. This avoids duplicated cleanup code across many error paths.

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    FILE *fp = NULL;
    int *buf = NULL;
    int rc = 1;

    fp = fopen("q25.txt", "w");
    if (fp == NULL) goto cleanup;

    buf = malloc(10 * sizeof(int));
    if (buf == NULL) goto cleanup;

    fprintf(fp, "Resources acquired successfully\n");
    rc = 0;

cleanup:
    free(buf);
    if (fp != NULL) fclose(fp);
    printf("return code = %d\n", rc);
    return rc;
}
```

---

## 26. What is the difference between `struct` and `union`?

**Hint:** One stores all members separately, the other shares memory.

**Simple explanation:** In a `struct`, each member has its own storage. In a `union`, all members share the same memory, so only one member's stored value is meaningful at a time.

```c
#include <stdio.h>

struct S {
    int x;
    char c;
};

union U {
    int x;
    char c;
};

int main() {
    printf("sizeof(struct S) = %zu\n", sizeof(struct S));
    printf("sizeof(union U) = %zu\n", sizeof(union U));
    return 0;
}
```

---

## 27. How do you access struct members using a pointer?

**Hint:** Use `->`.

**Simple explanation:** If you have a pointer to a struct, use the `->` operator instead of the dot operator.

```c
#include <stdio.h>

struct Student {
    int age;
    float marks;
};

int main() {
    struct Student s = {21, 88.5f};
    struct Student *p = &s;
    printf("age = %d, marks = %.1f\n", p->age, p->marks);
    return 0;
}
```

---

## 28. Insert a node at the front of a singly linked list.

**Hint:** New node points to old head, then head becomes new node.

**Simple explanation:** Create the new node, set its `next` to the current head, and update the head pointer to the new node.

```c
#include <stdio.h>
#include <stdlib.h>

struct Node {
    int data;
    struct Node *next;
};

void insertFront(struct Node **head, int val) {
    struct Node *n = malloc(sizeof(struct Node));
    if (n == NULL) return;
    n->data = val;
    n->next = *head;
    *head = n;
}

void printList(struct Node *head) {
    while (head != NULL) {
        printf("%d ", head->data);
        head = head->next;
    }
    printf("\n");
}

int main() {
    struct Node *head = NULL;
    insertFront(&head, 30);
    insertFront(&head, 20);
    insertFront(&head, 10);
    printList(head);
    return 0;
}
```

---

## 29. Reverse a singly linked list.

**Hint:** Use `prev`, `curr`, and `next`.

**Simple explanation:** Walk through the list and reverse each `next` pointer one by one. At the end, `prev` becomes the new head.

```c
#include <stdio.h>
#include <stdlib.h>

struct Node {
    int data;
    struct Node *next;
};

void push(struct Node **head, int val) {
    struct Node *n = malloc(sizeof(struct Node));
    if (n == NULL) return;
    n->data = val;
    n->next = *head;
    *head = n;
}

void reverse(struct Node **head) {
    struct Node *prev = NULL, *curr = *head, *next = NULL;
    while (curr != NULL) {
        next = curr->next;
        curr->next = prev;
        prev = curr;
        curr = next;
    }
    *head = prev;
}

void printList(struct Node *head) {
    while (head != NULL) {
        printf("%d ", head->data);
        head = head->next;
    }
    printf("\n");
}

int main() {
    struct Node *head = NULL;
    push(&head, 30);
    push(&head, 20);
    push(&head, 10);

    printList(head);
    reverse(&head);
    printList(head);
    return 0;
}
```

---

## 30. Read a file line by line safely and write output to another file.

**Hint:** Use `fopen`, `fgets`, `fprintf`, and `fclose`.

**Simple explanation:** Open the input file for reading and the output file for writing. Use `fgets()` to read each line safely and `fprintf()` to write processed lines.

```c
#include <stdio.h>

int main() {
    FILE *fin = fopen("iq_input.txt", "r");
    FILE *fout = fopen("iq_output.txt", "w");
    char line[128];

    if (fin == NULL || fout == NULL) {
        printf("File open failed\n");
        if (fin) fclose(fin);
        if (fout) fclose(fout);
        return 1;
    }

    while (fgets(line, sizeof(line), fin) != NULL) {
        fprintf(fout, "Processed: %s", line);
    }

    fclose(fin);
    fclose(fout);
    printf("Done\n");
    return 0;
}
```

---

## 31. What are bitwise operators (`&`, `|`, `^`, `<<`, `>>`) and where are they used?

**Hint:** They work on bits, not full decimal values.

**Simple explanation:** Bitwise operators manipulate individual bits and are common in flags, masks, embedded programming, and performance-sensitive code.

```c
#include <stdio.h>

int main() {
    unsigned int a = 6;  /* 110 */
    unsigned int b = 3;  /* 011 */

    printf("a & b = %u\n", a & b);
    printf("a | b = %u\n", a | b);
    printf("a ^ b = %u\n", a ^ b);
    printf("a << 1 = %u\n", a << 1);
    printf("a >> 1 = %u\n", a >> 1);
    return 0;
}
```

reverse bits:
```
uint8_t reverse(uint8_t n) {
    n = ((n & 0x55) << 1) | ((n & 0xAA) >> 1); // swap adjacent bits
    n = ((n & 0x33) << 2) | ((n & 0xCC) >> 2); // swap bit pairs
    n = ((n & 0x0F) << 4) | ((n & 0xF0) >> 4); // swap nibbles
    return n;
}
```
2^n
```
1 << n
```
is_power_of_2(n)
```
uint8_t ispow2(uint8_t n) {
    return (n && !(n & (n-1)));
}
```

---

## 32. What is the difference between stack and heap memory?

**Hint:** One is automatic, one is dynamic.

**Simple explanation:** Stack memory stores local variables and is managed automatically. Heap memory is dynamically allocated using `malloc()`/`free()` and must be managed manually.

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    int a = 10;                 /* stack */
    int *p = malloc(sizeof(int)); /* heap */

    if (p == NULL) return 1;
    *p = 20;

    printf("stack a = %d, heap *p = %d\n", a, *p);
    free(p);
    return 0;
}
```

---

## 33. What is a function pointer and where is it used?

**Hint:** A pointer can store a function address too.

**Simple explanation:** A function pointer stores the address of a function. It is useful for callbacks, tables of operations, and flexible designs.

```c
#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int main() {
    int (*fp)(int, int) = add;
    printf("result = %d\n", fp(2, 3));
    return 0;
}
```

---

## 34. Explain pointer arithmetic with an example.

**Hint:** Adding 1 moves by the size of the pointed type.

**Simple explanation:** Pointer arithmetic advances in units of the pointed type. For an `int *`, `p + 1` points to the next `int`, not the next byte.

```c
#include <stdio.h>

int main() {
    int arr[] = {10, 20, 30};
    int *p = arr;

    printf("*p = %d\n", *p);
    printf("*(p + 1) = %d\n", *(p + 1));
    printf("*(p + 2) = %d\n", *(p + 2));
    return 0;
}
```

---

## 35. What are macros in C (`#define`) and how do macros with arguments work?

**Hint:** Macros are handled by the preprocessor.

**Simple explanation:** A macro is text substitution done before compilation. Macros with arguments look like functions, but they are not type-checked and should be written carefully with parentheses.

```c
#include <stdio.h>

#define MAX 100
#define SQUARE(x) ((x) * (x))

int main() {
    printf("MAX = %d\n", MAX);
    printf("SQUARE(5) = %d\n", SQUARE(5));
    return 0;
}
```

---

## 36. What is endianness (big-endian vs little-endian)?

**Hint:** It is about byte order in memory.

**Simple explanation:** Endianness describes how multi-byte data is stored in memory. In little-endian systems, the least significant byte comes first. In big-endian systems, the most significant byte comes first.

```c
#include <stdio.h>

int main() {
    unsigned int x = 0x11223344;
    unsigned char *p = (unsigned char *)&x;

    printf("First byte in memory: 0x%02X\n", p[0]);
    if (p[0] == 0x44) {
        printf("Likely little-endian\n");
    } else if (p[0] == 0x11) {
        printf("Likely big-endian\n");
    }
    return 0;
}
```

---

## 37. What is the `volatile` keyword and when is it used?

**Hint:** It tells the compiler that the value may change unexpectedly.

**Simple explanation:** `volatile` is used for variables that may change outside normal program flow, such as hardware registers, shared variables modified by interrupts, or certain concurrent situations.

```c
#include <stdio.h>

int main() {
    volatile int flag = 1;

    while (flag) {
        printf("flag = %d\n", flag);
        flag = 0;
    }

    return 0;
}
```

---

## 38. What are threads in C and how do you create one using `pthread`?

**Hint:** Threads allow multiple flows of execution inside one process.

**Simple explanation:** A thread is a lightweight unit of execution. In C on POSIX systems, threads are commonly created using the `pthread` library.

**POSIX** thread functions (pthread) are standard C functions used to create and manage threads in a program.

```c
#include <stdio.h>
#include <pthread.h>

typedef struct {
    int a;
    int b;
    int add;
    int sub;
    pthread_mutex_t lock;
}Data;

void *add(void *arg) {
    Data *d = (Data *)arg;
    pthread_mutex_lock(&d->lock);
    d->add = d->a + d->b;
    pthread_mutex_unlock(&d->lock);
    return NULL;
}

void *sub(void *arg) {
    Data *d = (Data *)arg;
    pthread_mutex_lock(&d->lock);
    d->sub = d->a - d->b;
    pthread_mutex_unlock(&d->lock);
    return NULL;
}

int main() {
    pthread_t t1, t2;
    Data d = {20, 5, 0, 0};
    pthread_mutex_init(&d.lock, NULL);
    pthread_create(&t1, NULL, add, &d);
    pthread_create(&t2, NULL, sub, &d);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("add = %d, sub = %d\n", d.add, d.sub);
    pthread_mutex_destroy(&d.lock);
    return 0;
}
```
**Without mutex** the below counter may give wrong output because counter++ = {read, add +1, write}. Therefore add mutex lock and unlock around counter++;

```
#include <stdio.h>
#include <pthread.h>

typedef struct {
    int a;
    int b;
} data;

void *add(void *arg) {
    data *d = (void *)arg;
    printf("add = %d\n", d->a + d->b);
}

void *sub(void *arg) {
    data *d = (void *)arg;
    printf("sub = %d\n", d->a - d->b);
}

int main()
{
    data d;
    d.a = 10;
    d.b = 20;
    pthread_t t1, t2;
    pthread_create(&t1, NULL, add, &d);
    pthread_create(&t2, NULL, sub, &d);
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    return 0;
}
```

**Compile note:**
```bash
gcc demo.c -o demo -pthread
```

---

## Suggested Usage

- Read one question at a time.
- Try answering it yourself before looking at the explanation.
- Compile and run each code example.
- Modify the code slightly to test your understanding.


## extra questions from linkedin
```
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* 1. Set / Clear / Toggle / Check nth bit */
uint32_t set_bit(uint32_t n, int pos) {
    return n | (1U << pos);
}

uint32_t clear_bit(uint32_t n, int pos) {
    return n & ~(1U << pos);
}

uint32_t toggle_bit(uint32_t n, int pos) {
    return n ^ (1U << pos);
}

int check_bit(uint32_t n, int pos) {
    return (n >> pos) & 1U;
}

/* 2. Count set bits */
int count_set_bits(uint32_t n) {
    int count = 0;

    while (n) {
        count += n & 1U;
        n >>= 1;
    }

    return count;
}

/* Faster version */
int count_set_bits_fast(uint32_t n) {
    int count = 0;

    while (n) {
        n = n & (n - 1);
        count++;
    }

    return count;
}

/* 3. Check power of 2 */
bool is_power_of_2(uint32_t n) {
    return n != 0 && (n & (n - 1)) == 0;
}

/* 4. Swap using XOR */
void xor_swap(int *a, int *b) {
    if (a == b) return;

    *a = *a ^ *b;
    *b = *a ^ *b;
    *a = *a ^ *b;
}

/* 5. Reverse bits of uint32_t */
uint32_t reverse_bits(uint32_t n) {
    n = ((n & 0x55555555U) << 1) | ((n & 0xAAAAAAAAU) >> 1);
    n = ((n & 0x33333333U) << 2) | ((n & 0xCCCCCCCCU) >> 2);
    n = ((n & 0x0F0F0F0FU) << 4) | ((n & 0xF0F0F0F0U) >> 4);
    n = ((n & 0x00FF00FFU) << 8) | ((n & 0xFF00FF00U) >> 8);
    n = (n << 16) | (n >> 16);

    return n;
}

/* 6. Find single non-repeating element */
int single_number(int arr[], int n) {
    int result = 0;

    for (int i = 0; i < n; i++) {
        result ^= arr[i];
    }

    return result;
}

/* 7. Pack and unpack boolean flags */
uint8_t pack_flags(bool f0, bool f1, bool f2, bool f3) {
    uint8_t flags = 0;

    flags |= (f0 ? 1U : 0U) << 0;
    flags |= (f1 ? 1U : 0U) << 1;
    flags |= (f2 ? 1U : 0U) << 2;
    flags |= (f3 ? 1U : 0U) << 3;

    return flags;
}

bool get_flag(uint8_t flags, int pos) {
    return (flags >> pos) & 1U;
}

/* 8. Multiply / divide by powers of 2 */
int multiply_by_power_of_2(int n, int power) {
    return n << power;
}

int divide_by_power_of_2(int n, int power) {
    return n >> power;
}

int main() {
    uint32_t n = 10; // binary: 1010

    printf("Set bit 1: %u\n", set_bit(n, 1));
    printf("Clear bit 3: %u\n", clear_bit(n, 3));
    printf("Toggle bit 0: %u\n", toggle_bit(n, 0));
    printf("Check bit 3: %d\n", check_bit(n, 3));

    printf("Set bits in 10: %d\n", count_set_bits(n));
    printf("Fast set bits in 10: %d\n", count_set_bits_fast(n));

    printf("Is 16 power of 2? %s\n", is_power_of_2(16) ? "Yes" : "No");

    int a = 5, b = 9;
    xor_swap(&a, &b);
    printf("After XOR swap: a=%d b=%d\n", a, b);

    printf("Reverse bits of 1: %u\n", reverse_bits(1));

    int arr[] = {4, 1, 2, 1, 2};
    printf("Single number: %d\n", single_number(arr, 5));

    uint8_t flags = pack_flags(true, false, true, true);
    printf("Packed flags: %u\n", flags);
    printf("Flag 0: %d\n", get_flag(flags, 0));
    printf("Flag 1: %d\n", get_flag(flags, 1));
    printf("Flag 2: %d\n", get_flag(flags, 2));
    printf("Flag 3: %d\n", get_flag(flags, 3));

    printf("5 * 8 = %d\n", multiply_by_power_of_2(5, 3));
    printf("40 / 8 = %d\n", divide_by_power_of_2(40, 3));

    return 0;
}
```

## extra questions from linkedin
```
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

/* 1. Reverse array in-place */
void reverse_array(int arr[], int n) {
    int i = 0, j = n - 1;
    while (i < j) {
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
        i++;
        j--;
    }
}

/* 2. Implement strlen */
size_t my_strlen(const char *s) {
    size_t len = 0;
    while (s[len] != '\0') {
        len++;
    }
    return len;
}

/* 3. Implement memcpy */
void *my_memcpy(void *dest, const void *src, size_t n) {
    unsigned char *d = dest;
    const unsigned char *s = src;

    for (size_t i = 0; i < n; i++) {
        d[i] = s[i];
    }

    return dest;
}

/* 4. Implement memmove */
void *my_memmove(void *dest, const void *src, size_t n) {
    unsigned char *d = dest;
    const unsigned char *s = src;

    if (d < s) {
        for (size_t i = 0; i < n; i++) {
            d[i] = s[i];
        }
    } else if (d > s) {
        for (size_t i = n; i > 0; i--) {
            d[i - 1] = s[i - 1];
        }
    }

    return dest;
}

/* 5. Find duplicates without heap: assumes values are in range 0..100 */
void find_duplicates(int arr[], int n) {
    int count[101] = {0};

    for (int i = 0; i < n; i++) {
        count[arr[i]]++;
    }

    printf("Duplicates: ");
    for (int i = 0; i <= 100; i++) {
        if (count[i] > 1) {
            printf("%d ", i);
        }
    }
    printf("\n");
}

/* 6. Check anagrams */
bool are_anagrams(const char *a, const char *b) {
    int count[256] = {0};

    while (*a) {
        count[(unsigned char)*a]++;
        a++;
    }

    while (*b) {
        count[(unsigned char)*b]--;
        b++;
    }

    for (int i = 0; i < 256; i++) {
        if (count[i] != 0) {
            return false;
        }
    }

    return true;
}

/* 7. Maximum sum subarray of size k */
int max_sum_k(int arr[], int n, int k) {
    if (k <= 0 || k > n) return 0;

    int sum = 0;
    for (int i = 0; i < k; i++) {
        sum += arr[i];
    }

    int max_sum = sum;

    for (int i = k; i < n; i++) {
        sum += arr[i] - arr[i - k];

        if (sum > max_sum) {
            max_sum = sum;
        }
    }

    return max_sum;
}

/* 8. Move zeros to end */
void move_zeros(int arr[], int n) {
    int pos = 0;

    for (int i = 0; i < n; i++) {
        if (arr[i] != 0) {
            arr[pos++] = arr[i];
        }
    }

    while (pos < n) {
        arr[pos++] = 0;
    }
}

/* 9. First non-repeating character */
char first_non_repeating(const char *s) {
    int count[256] = {0};

    for (int i = 0; s[i] != '\0'; i++) {
        count[(unsigned char)s[i]]++;
    }

    for (int i = 0; s[i] != '\0'; i++) {
        if (count[(unsigned char)s[i]] == 1) {
            return s[i];
        }
    }

    return '\0';
}

/* Helper for rotating array */
void reverse_range(int arr[], int left, int right) {
    while (left < right) {
        int temp = arr[left];
        arr[left] = arr[right];
        arr[right] = temp;
        left++;
        right--;
    }
}

/* 10. Rotate array right by k positions in-place */
void rotate_right(int arr[], int n, int k) {
    if (n <= 0) return;

    k = k % n;

    reverse_range(arr, 0, n - 1);
    reverse_range(arr, 0, k - 1);
    reverse_range(arr, k, n - 1);
}

/* 11. Check palindrome */
bool is_palindrome(const char *s) {
    int left = 0;
    int right = (int)my_strlen(s) - 1;

    while (left < right) {
        if (s[left] != s[right]) {
            return false;
        }

        left++;
        right--;
    }

    return true;
}

/* 12. Merge two sorted arrays into fixed output buffer */
int merge_sorted(int a[], int n, int b[], int m, int out[], int out_size) {
    if (out_size < n + m) {
        return -1;
    }

    int i = 0, j = 0, k = 0;

    while (i < n && j < m) {
        if (a[i] <= b[j]) {
            out[k++] = a[i++];
        } else {
            out[k++] = b[j++];
        }
    }

    while (i < n) {
        out[k++] = a[i++];
    }

    while (j < m) {
        out[k++] = b[j++];
    }

    return k;
}

void print_array(int arr[], int n) {
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}

int main() {
    int arr1[] = {1, 2, 3, 4, 5};
    reverse_array(arr1, 5);
    printf("Reverse array: ");
    print_array(arr1, 5);

    char s[] = "hello";
    printf("strlen: %zu\n", my_strlen(s));

    char src[] = "ABCDE";
    char dest[10];
    my_memcpy(dest, src, 6);
    printf("memcpy: %s\n", dest);

    char movebuf[] = "123456789";
    my_memmove(movebuf + 2, movebuf, 5);
    printf("memmove: %s\n", movebuf);

    int dup[] = {1, 2, 3, 2, 4, 5, 1};
    find_duplicates(dup, 7);

    printf("anagram: %s\n", are_anagrams("listen", "silent") ? "Yes" : "No");

    int win[] = {2, 1, 5, 1, 3, 2};
    printf("max sum k: %d\n", max_sum_k(win, 6, 3));

    int zeros[] = {0, 1, 0, 3, 12};
    move_zeros(zeros, 5);
    printf("move zeros: ");
    print_array(zeros, 5);

    char ch = first_non_repeating("swiss");
    printf("first non-repeating: %c\n", ch);

    int rot[] = {1, 2, 3, 4, 5};
    rotate_right(rot, 5, 2);
    printf("rotate right: ");
    print_array(rot, 5);

    printf("palindrome: %s\n", is_palindrome("madam") ? "Yes" : "No");

    int a[] = {1, 3, 5};
    int b[] = {2, 4, 6};
    int out[6];

    int merged_size = merge_sorted(a, 3, b, 3, out, 6);
    printf("merged: ");
    print_array(out, merged_size);

    return 0;
}
```