# Embedded_C_Code_1 (Beginner - Code + Explanation)

## 1. Volatile + Hardware Register Simulation

```c
#include <stdio.h>
#include <stdint.h>

volatile uint32_t REG = 0;

int main() {
    REG = 5;              // write to register
    printf("REG = %u\n", REG);

    while (REG == 5) {
        printf("Waiting for change...\n");
        REG = 10;         // simulate hardware change
    }

    printf("REG changed to %u\n", REG);
    return 0;
}
```

### Explanation
- `volatile` forces compiler to read memory every time
- simulates hardware register behavior

---

## 2. Bit Manipulation

```c
#include <stdio.h>

int main() {
    int reg = 0;

    reg |= (1 << 2);   // set bit 2
    printf("Set bit 2: %d\n", reg);

    reg &= ~(1 << 2); // clear bit 2
    printf("Clear bit 2: %d\n", reg);

    return 0;
}
```

---

## 3. Simple Circular Buffer

```c
#include <stdio.h>

#define SIZE 5

int buffer[SIZE];
int head = 0, tail = 0;

void push(int x) {
    buffer[head] = x;
    head = (head + 1) % SIZE;
}

int pop() {
    int val = buffer[tail];
    tail = (tail + 1) % SIZE;
    return val;
}

int main() {
    push(1); push(2); push(3);
    printf("%d\n", pop());
    printf("%d\n", pop());
}
```

---

## Key Learning
- volatile usage
- bit operations
- circular buffer basics
