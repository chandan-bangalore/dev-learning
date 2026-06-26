# Embedded_C_Code.md
## Embedded C Code + Full Interview Practice (With Solutions)

---

# SECTION 1: Core Code Patterns

## Volatile Example
```c
#include <stdio.h>
#include <stdint.h>

volatile uint32_t REG = 0;

int main() {
    REG = 5;
    while (REG == 5) {
        REG = 10;
    }
    printf("REG = %u\n", REG);
}
```

---

## Bit Manipulation
```c
int reg = 0;
reg |= (1 << 2);   // set
reg &= ~(1 << 2);  // clear
reg ^= (1 << 2);   // toggle
```

---

## Circular Buffer (Concept)
```c
#define SIZE 8
int buf[SIZE];
int head = 0, tail = 0;
```

---

# SECTION 2: INTERVIEW PRACTICE (WITH SOLUTIONS)

---

## EASY LEVEL

### Q1: Set, Clear, Toggle a Bit

```c
#define SET_BIT(x,n)   ((x) |= (1U << (n)))
#define CLR_BIT(x,n)   ((x) &= ~(1U << (n)))
#define TOG_BIT(x,n)   ((x) ^= (1U << (n)))
```

---

### Q2: Check Power of 2

```c
int is_power_of_2(unsigned int x) {
    return x && !(x & (x - 1));
}
```

---

### Q3: Count Set Bits

```c
int count_bits(unsigned int x) {
    int count = 0;
    while (x) {
        x &= (x - 1);
        count++;
    }
    return count;
}
```

---

## MEDIUM LEVEL

### Q4: Full Circular Buffer

```c
#include <stdio.h>
#define SIZE 4

typedef struct {
    int buf[SIZE];
    int head;
    int tail;
} circbuf;

int is_full(circbuf *c) {
    return ((c->head + 1) % SIZE) == c->tail;
}

int is_empty(circbuf *c) {
    return c->head == c->tail;
}

void push(circbuf *c, int val) {
    if (!is_full(c)) {
        c->buf[c->head] = val;
        c->head = (c->head + 1) % SIZE;
    }
}

int pop(circbuf *c) {
    if (!is_empty(c)) {
        int val = c->buf[c->tail];
        c->tail = (c->tail + 1) % SIZE;
        return val;
    }
    return -1;
}
```

---

### Q5: Reverse Bits

```c
unsigned int reverse_bits(unsigned int x) {
    unsigned int r = 0;
    for (int i = 0; i < 32; i++) {
        r <<= 1;
        r |= (x & 1);
        x >>= 1;
    }
    return r;
}
```

---

### Q6: Extract Bit Field

```c
unsigned int extract(unsigned int reg, int shift, int width) {
    return (reg >> shift) & ((1U << width) - 1);
}
```

---

## HARD LEVEL

### Q7: ISR + Buffer Design

```c
volatile int flag = 0;

void ISR() {
    flag = 1;
}

void main_loop() {
    if (flag) {
        flag = 0;
        // process data
    }
}
```

---

### Q8: Parse Packet (Example)

```c
#include <stdint.h>

uint16_t read_be16(uint8_t *buf) {
    return (buf[0] << 8) | buf[1];
}
```

---

### Q9: Lock-Free Counter (Atomic)

```c
#include <stdatomic.h>

atomic_int counter = 0;

void increment() {
    atomic_fetch_add(&counter, 1);
}
```

---

# SECTION 3: SYSTEM DESIGN QUESTIONS (WITH ANSWER HINTS)

### Q10: Design UART RX system
Answer:
- Use DMA
- Circular buffer
- ISR sets flag
- Task processes data

---

### Q11: Avoid Race Condition
Answer:
- disable_irq OR atomic ops

---

### Q12: Why volatile not enough?
Answer:
- no atomicity
- no ordering guarantee

---

# FINAL STRATEGY

1. Write code without seeing solution
2. Explain logic out loud
3. Practice daily

---

You are now interview-ready if you can solve these without help.
