# Embedded_C_Code_2 (Intermediate - Code + Explanation)

## 1. ISR Simulation

```c
#include <stdio.h>
#include <stdint.h>

volatile int flag = 0;

void ISR() {
    flag = 1;
}

int main() {
    ISR(); // simulate interrupt

    if (flag) {
        printf("Interrupt handled\n");
    }
}
```

---

## 2. DMA Simulation

```c
#include <stdio.h>
#include <string.h>

int main() {
    char src[] = "HELLO";
    char dest[10];

    memcpy(dest, src, sizeof(src)); // CPU copy
    printf("Copied: %s\n", dest);
}
```

### Explanation
- memcpy = CPU copy
- DMA would do this in hardware

---

## 3. Critical Section

```c
#include <stdio.h>

int counter = 0;

void increment() {
    // simulate critical section
    counter++;
}

int main() {
    increment();
    printf("Counter = %d\n", counter);
}
```

---

## Key Learning
- ISR basics
- DMA vs memcpy
- critical section idea
