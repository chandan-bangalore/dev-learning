# Embedded_C_Code_3 (Advanced - Code + Explanation)

## 1. Atomic Operation

```c
#include <stdio.h>
#include <stdatomic.h>

atomic_int counter = 0;

int main() {
    atomic_fetch_add(&counter, 1);
    printf("Counter = %d\n", counter);
}
```

---

## 2. Struct Padding Demo

```c
#include <stdio.h>

struct A {
    char a;
    int b;
};

int main() {
    printf("Size of struct A = %lu\n", sizeof(struct A));
}
```

---

## 3. Shared Memory Concept

```c
#include <stdio.h>

int shared = 0;

int main() {
    shared = 10;
    printf("Shared = %d\n", shared);
}
```

---

## Key Learning
- atomic operations
- struct padding
- shared memory basics
