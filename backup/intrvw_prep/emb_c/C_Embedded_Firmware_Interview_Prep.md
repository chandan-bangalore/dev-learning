# Embedded Firmware C Interview Prep
### For Any Company Hiring Embedded C Engineers — 5G RAN / Modem / Real-Time Systems

---

## How to use this guide
- Each topic has a **concept summary**, **interview questions**, and a **runnable C program**
- Paste programs into [onlinegdb.com](https://onlinegdb.com) → select **C (C11)** → Run
- Programs simulate firmware behavior on a host PC — `volatile` effects and hardware registers are simulated

---

# Topic 1: Volatile Keyword & Hardware Register Access

## Concept summary

`volatile` is the most fundamental keyword in embedded C. It tells the compiler:
> "This variable may change outside the program's control — do NOT optimize reads/writes."

**Without `volatile`**, the compiler may:
- Cache a value in a CPU register and never re-read memory
- Optimize away a polling loop: `while(reg == 0){}` → `if(reg == 0) { while(1){} }`
- Reorder or eliminate writes it considers redundant

**Where `volatile` is required**:
| Scenario | Why |
|---|---|
| Memory-mapped hardware registers | Hardware changes value independently |
| Variables modified in ISRs | ISR runs outside normal flow |
| Shared variables with DMA | DMA writes directly to memory |
| Multicore shared memory (partial) | Another core writes independently |

**What `volatile` does NOT do**:
- Does NOT guarantee atomicity
- Does NOT prevent race conditions on multi-bit variables
- Does NOT act as a memory barrier on all architectures 

**Memory-mapped register access pattern**:
```c
#define PERIPH_BASE     0xA0010000UL
#define TX_CTRL_OFFSET  0x00
#define RX_CTRL_OFFSET  0x04

volatile uint32_t * const TX_CTRL = (volatile uint32_t *)(PERIPH_BASE + TX_CTRL_OFFSET);
volatile uint32_t * const RX_CTRL = (volatile uint32_t *)(PERIPH_BASE + RX_CTRL_OFFSET);
```

## Interview questions
1. Why must memory-mapped registers be declared `volatile`?
2. What is the difference between `volatile int *p` and `int * volatile p`?
3. Does `volatile` guarantee atomicity? Why or why not?
4. What happens if you forget `volatile` on a register polled in a loop?
5. Is `volatile` sufficient for sharing a variable between two cores?

## Runnable program

```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Simulated hardware registers — in real HW these are physical addresses */
static volatile uint32_t SIM_STATUS_REG  = 0x00000000UL;
static volatile uint32_t SIM_CTRL_REG    = 0x00000000UL;
static volatile uint32_t SIM_DATA_REG    = 0x00000000UL;

/* Bit definitions */
#define STATUS_RX_READY   (1U << 0)
#define STATUS_TX_BUSY    (1U << 1)
#define STATUS_ERROR      (1U << 7)
#define CTRL_TX_ENABLE    (1U << 0)
#define CTRL_RX_ENABLE    (1U << 1)
#define CTRL_RESET        (1U << 31)

/* Simulated "hardware" sets RX_READY after some event */
void simulate_hardware_rx_ready(void) {
    SIM_STATUS_REG |= STATUS_RX_READY;
    SIM_DATA_REG    = 0xABCD1234UL;
}

/* Safe read-modify-write */
static inline void reg_set_bits(volatile uint32_t *reg, uint32_t mask) {
    *reg |= mask;
}
static inline void reg_clr_bits(volatile uint32_t *reg, uint32_t mask) {
    *reg &= ~mask;
}
static inline bool reg_check_bit(volatile uint32_t *reg, uint32_t mask) {
    return (*reg & mask) != 0;
}

/* Poll until RX ready — volatile ensures fresh read each iteration */
uint32_t poll_rx_data(void) {
    int timeout = 1000;
    while (!reg_check_bit(&SIM_STATUS_REG, STATUS_RX_READY)) {
        if (--timeout == 0) {
            printf("  [TIMEOUT] RX not ready\n");
            return 0;
        }
    }
    uint32_t data = SIM_DATA_REG;
    reg_clr_bits(&SIM_STATUS_REG, STATUS_RX_READY);   /* clear flag */
    return data;
}

/* volatile pointer variations */
void volatile_pointer_demo(void) {
    uint32_t x = 42;

    volatile uint32_t *p1 = &x;
    /* pointer to volatile uint32: *p1 access is volatile, p1 itself can change */

    uint32_t * volatile p2 = &x;
    /* volatile pointer to uint32: p2 itself is volatile (address), *p2 is not */

    volatile uint32_t * volatile p3 = &x;
    /* both the pointer and the pointed-to value are volatile */

    printf("  *p1 (volatile value)    = %u\n", *p1);
    printf("  *p2 (volatile pointer)  = %u\n", *p2);
    printf("  *p3 (both volatile)     = %u\n", *p3);
}

int main() {
    printf("=== Volatile & Hardware Register Access ===\n\n");

    /* Initialize: enable TX and RX */
    reg_set_bits(&SIM_CTRL_REG, CTRL_TX_ENABLE | CTRL_RX_ENABLE);
    printf("CTRL_REG after enable TX+RX: 0x%08X\n\n", SIM_CTRL_REG);

    /* Poll for RX data */
    printf("Polling for RX data (hardware not ready yet)...\n");
    /* Simulate hardware firing — in real FW this would be an interrupt or HW event */
    simulate_hardware_rx_ready();
    uint32_t data = poll_rx_data();
    printf("Received data: 0x%08X\n\n", data);

    /* Error check */
    if (reg_check_bit(&SIM_STATUS_REG, STATUS_ERROR))
        printf("Error detected in status register\n");
    else
        printf("No errors in status register\n\n");

    /* volatile pointer variations */
    printf("volatile pointer variations:\n");
    volatile_pointer_demo();

    /* Reset */
    reg_set_bits(&SIM_CTRL_REG, CTRL_RESET);
    printf("\nAfter reset: CTRL_REG = 0x%08X\n", SIM_CTRL_REG);
    reg_clr_bits(&SIM_CTRL_REG, CTRL_RESET);

    printf("\nKey rule: every hardware register pointer must be volatile.\n");
    printf("Without it, the compiler may cache the value and your poll loop never exits.\n");

    return 0;
}
```

---

# Topic 2: Bit Manipulation — Register Fields

## Concept summary

Bit manipulation is the core skill of firmware development. Every peripheral, protocol header, and control register is configured through bit operations.

**The read-modify-write (RMW) pattern**:
```c
reg = (reg & ~MASK) | ((value << SHIFT) & MASK);
```

**Why `1U` and `0xFU` instead of `1` and `0xF`**:
- `1 << 31` is undefined behavior (signed overflow)
- `1U << 31` is well-defined (unsigned shift)
- Always use `U` suffix on bit masks

**Field extraction and insertion** — the most tested pattern:
```c
/* Extract bits [11:8] */
uint32_t val = (reg >> 8) & 0xFU;

/* Insert value into bits [11:8] */
reg = (reg & ~(0xFU << 8)) | ((val & 0xFU) << 8);
```

## Interview questions
1. Write macros to set, clear, toggle, and check a single bit.
2. How do you extract a 4-bit field from bits [11:8] of a 32-bit register?
3. What is the danger of `1 << 31` vs `1U << 31`?
4. How do you set bits [15:12] to value 7 without disturbing other bits?
5. How do you count the number of set bits without a library?

## Runnable program

```c
#include <stdio.h>
#include <stdint.h>

/* ---- Core bit macros ---- */
#define BIT(n)                      (1UL << (n))
#define SET_BIT(reg, n)             ((reg) |=  BIT(n))
#define CLR_BIT(reg, n)             ((reg) &= ~BIT(n))
#define TOG_BIT(reg, n)             ((reg) ^=  BIT(n))
#define CHK_BIT(reg, n)             (((reg) >> (n)) & 1U)

/* ---- Multi-bit field macros ---- */
#define FIELD_MASK(shift, width)    (((1UL << (width)) - 1UL) << (shift))
#define GET_FIELD(reg, shift, width) \
    (((reg) >> (shift)) & ((1UL << (width)) - 1UL))
#define SET_FIELD(reg, shift, width, val) \
    ((reg) = ((reg) & ~FIELD_MASK(shift, width)) | \
             (((uint32_t)(val) & ((1UL << (width)) - 1UL)) << (shift)))

/* ---- Algorithms ---- */

/* Count set bits — Brian Kernighan */
uint32_t popcount(uint32_t x) {
    uint32_t n = 0;
    while (x) { x &= x - 1; n++; }
    return n;
}

/* Reverse bits */
uint32_t reverse_bits(uint32_t x) {
    uint32_t r = 0;
    for (int i = 0; i < 32; i++) {
        r = (r << 1) | (x & 1);
        x >>= 1;
    }
    return r;
}

/* Is power of 2 */
int is_pow2(uint32_t x) { return x && !(x & (x - 1)); }

/* Isolate lowest set bit */
uint32_t lowest_set_bit(uint32_t x) { return x & (uint32_t)(-(int32_t)x); }

/* Print binary (lower 16 bits) */
void print_bin16(const char *label, uint32_t val) {
    printf("%-38s 0x%08X  ", label, val);
    for (int i = 15; i >= 0; i--) {
        printf("%d", (val >> i) & 1);
        if (i && i % 4 == 0) printf(" ");
    }
    printf("\n");
}

/* Simulated RF channel register */
/* [15:12]=TX_POWER [11:8]=RX_GAIN [7:4]=CHANNEL [3:2]=MODE [1]=TX_EN [0]=RX_EN */
#define RF_TX_POWER_SHIFT   12
#define RF_TX_POWER_WIDTH    4
#define RF_RX_GAIN_SHIFT     8
#define RF_RX_GAIN_WIDTH     4
#define RF_CHANNEL_SHIFT     4
#define RF_CHANNEL_WIDTH     4
#define RF_TX_EN_BIT         1
#define RF_RX_EN_BIT         0

int main() {
    printf("=== Bit Manipulation — Register Fields ===\n\n");

    uint32_t rf_reg = 0x00000000UL;
    print_bin16("Initial RF reg:", rf_reg);

    SET_BIT(rf_reg, RF_RX_EN_BIT);
    print_bin16("Enable RX (bit 0):", rf_reg);

    SET_BIT(rf_reg, RF_TX_EN_BIT);
    print_bin16("Enable TX (bit 1):", rf_reg);

    SET_FIELD(rf_reg, RF_CHANNEL_SHIFT, RF_CHANNEL_WIDTH, 5);
    print_bin16("Set CHANNEL=5 [7:4]:", rf_reg);

    SET_FIELD(rf_reg, RF_RX_GAIN_SHIFT, RF_RX_GAIN_WIDTH, 0xA);
    print_bin16("Set RX_GAIN=0xA [11:8]:", rf_reg);

    SET_FIELD(rf_reg, RF_TX_POWER_SHIFT, RF_TX_POWER_WIDTH, 7);
    print_bin16("Set TX_POWER=7 [15:12]:", rf_reg);

    printf("\nReading fields back:\n");
    printf("  CHANNEL  = %u\n", GET_FIELD(rf_reg, RF_CHANNEL_SHIFT, RF_CHANNEL_WIDTH));
    printf("  RX_GAIN  = 0x%X\n", GET_FIELD(rf_reg, RF_RX_GAIN_SHIFT, RF_RX_GAIN_WIDTH));
    printf("  TX_POWER = %u\n", GET_FIELD(rf_reg, RF_TX_POWER_SHIFT, RF_TX_POWER_WIDTH));
    printf("  TX_EN    = %u\n", CHK_BIT(rf_reg, RF_TX_EN_BIT));
    printf("  RX_EN    = %u\n\n", CHK_BIT(rf_reg, RF_RX_EN_BIT));

    CLR_BIT(rf_reg, RF_RX_EN_BIT);
    print_bin16("Disable RX:", rf_reg);
    TOG_BIT(rf_reg, RF_TX_EN_BIT);
    print_bin16("Toggle TX:", rf_reg);

    printf("\nAlgorithms:\n");
    uint32_t tests[] = {0, 1, 3, 0xFF, 0x12345678, 0xFFFFFFFF};
    for (int i = 0; i < 6; i++)
        printf("  popcount(0x%08X) = %u\n", tests[i], popcount(tests[i]));

    printf("\n");
    uint32_t pow2[] = {0, 1, 2, 3, 4, 8, 16, 255};
    for (int i = 0; i < 8; i++)
        printf("  is_pow2(%3u) = %s\n", pow2[i], is_pow2(pow2[i]) ? "YES" : "NO");

    printf("\nreverse_bits(0x80000001) = 0x%08X\n", reverse_bits(0x80000001UL));
    printf("lowest_set_bit(0b10110100) = 0x%08X\n", lowest_set_bit(0b10110100));

    return 0;
}
```

---

# Topic 3: Struct Padding, Alignment & Packed Structs

## Concept summary

In firmware, structs are used to:
- Overlay on hardware register blocks
- Represent protocol headers (LTE/5G MAC, RLC, PDCP headers)
- Pack data for DMA transfers

**Alignment rule**: a member of type `T` must start at an address divisible by `sizeof(T)`. The compiler inserts padding silently.

**Consequences in 5G RAN**:
- A poorly ordered struct wastes precious on-chip RAM
- A struct used as a register overlay MUST match hardware layout exactly → use `__attribute__((packed))` or reorder carefully
- Misaligned access on ARM Cortex-A/R can cause a fault (unless unaligned access support is enabled)

**Best practices**:
- Order members: largest to smallest → minimizes padding
- Use `static_assert(sizeof(MyStruct) == N)` to catch layout changes
- Use `__attribute__((packed))` only when necessary (protocol headers, register maps)
- Verify with `offsetof()`

## Interview questions
1. Why is `sizeof(struct A)` larger than the sum of its members?
2. How do you ensure a struct used as a protocol header is exactly N bytes?
3. What is `offsetof` and when do you use it?
4. What are the risks of `__attribute__((packed))` on ARM?
5. Given a struct, how do you minimize its size by reordering members?

## Runnable program

```c
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>

/* Poorly ordered — wastes memory */
struct PaddedMsg {
    uint8_t  type;       /* 1 byte  + 3 pad */
    uint32_t timestamp;  /* 4 bytes */
    uint8_t  channel;    /* 1 byte  + 1 pad */
    uint16_t length;     /* 2 bytes */
    uint8_t  flags;      /* 1 byte  + 3 pad */
    uint32_t checksum;   /* 4 bytes */
};                       /* Total: 20 bytes (members = 13) */

/* Optimized — same members, largest first */
struct OptimizedMsg {
    uint32_t timestamp;  /* 4 bytes */
    uint32_t checksum;   /* 4 bytes */
    uint16_t length;     /* 2 bytes */
    uint8_t  type;       /* 1 byte  */
    uint8_t  channel;    /* 1 byte  */
    uint8_t  flags;      /* 1 byte  + 3 pad */
};                       /* Total: 16 bytes */

/* Protocol header — must be exact, packed */
struct __attribute__((packed)) NR_MACHeader {
    uint8_t  lcid     : 6;    /* Logical Channel ID */
    uint8_t  f_bit    : 1;    /* Format bit */
    uint8_t  r_bit    : 1;    /* Reserved */
    uint16_t payload_len;     /* 2 bytes */
};                            /* Total: 3 bytes, exactly */

/* Register block overlay — must match hardware layout */
struct __attribute__((packed)) ModemRegBlock {
    volatile uint32_t ctrl;        /* offset 0x00 */
    volatile uint32_t status;      /* offset 0x04 */
    volatile uint32_t tx_data;     /* offset 0x08 */
    volatile uint32_t rx_data;     /* offset 0x0C */
    volatile uint32_t interrupt;   /* offset 0x10 */
};                                 /* Total: 20 bytes */

/* Compile-time size assertion */
typedef char _check_mac_hdr[(sizeof(struct NR_MACHeader) == 3) ? 1 : -1];
typedef char _check_reg_blk[(sizeof(struct ModemRegBlock) == 20) ? 1 : -1];

void print_offsets_padded() {
    printf("PaddedMsg offsets:\n");
    printf("  type:      %2zu  (size %zu)\n", offsetof(struct PaddedMsg, type),      sizeof(((struct PaddedMsg*)0)->type));
    printf("  timestamp: %2zu  (size %zu)\n", offsetof(struct PaddedMsg, timestamp), sizeof(((struct PaddedMsg*)0)->timestamp));
    printf("  channel:   %2zu  (size %zu)\n", offsetof(struct PaddedMsg, channel),   sizeof(((struct PaddedMsg*)0)->channel));
    printf("  length:    %2zu  (size %zu)\n", offsetof(struct PaddedMsg, length),    sizeof(((struct PaddedMsg*)0)->length));
    printf("  flags:     %2zu  (size %zu)\n", offsetof(struct PaddedMsg, flags),     sizeof(((struct PaddedMsg*)0)->flags));
    printf("  checksum:  %2zu  (size %zu)\n", offsetof(struct PaddedMsg, checksum),  sizeof(((struct PaddedMsg*)0)->checksum));
}

int main() {
    printf("=== Struct Padding, Alignment & Packed Structs ===\n\n");

    printf("Struct sizes:\n");
    printf("  PaddedMsg:     %2zu bytes  (members sum to 13)\n", sizeof(struct PaddedMsg));
    printf("  OptimizedMsg:  %2zu bytes  (same members, reordered)\n", sizeof(struct OptimizedMsg));
    printf("  NR_MACHeader:  %2zu bytes  (packed — must be 3)\n", sizeof(struct NR_MACHeader));
    printf("  ModemRegBlock: %2zu bytes  (register overlay)\n\n", sizeof(struct ModemRegBlock));

    print_offsets_padded();

    printf("\nOptimizedMsg offsets:\n");
    printf("  timestamp: %2zu\n", offsetof(struct OptimizedMsg, timestamp));
    printf("  checksum:  %2zu\n", offsetof(struct OptimizedMsg, checksum));
    printf("  length:    %2zu\n", offsetof(struct OptimizedMsg, length));
    printf("  type:      %2zu\n", offsetof(struct OptimizedMsg, type));
    printf("  channel:   %2zu\n", offsetof(struct OptimizedMsg, channel));
    printf("  flags:     %2zu\n\n", offsetof(struct OptimizedMsg, flags));

    /* Register block access */
    struct ModemRegBlock sim_regs;
    memset(&sim_regs, 0, sizeof(sim_regs));
    sim_regs.ctrl   = 0x00000003UL;
    sim_regs.status = 0x00000001UL;
    printf("ModemRegBlock sim:\n");
    printf("  ctrl   @ offset %2zu = 0x%08X\n", offsetof(struct ModemRegBlock, ctrl),   sim_regs.ctrl);
    printf("  status @ offset %2zu = 0x%08X\n", offsetof(struct ModemRegBlock, status), sim_regs.status);

    /* MAC header */
    struct NR_MACHeader mac = { .lcid = 3, .f_bit = 1, .r_bit = 0, .payload_len = 128 };
    printf("\nNR MAC header: lcid=%u f=%u payload_len=%u  (size=%zu)\n",
           mac.lcid, mac.f_bit, mac.payload_len, sizeof(mac));

    printf("\nKey rule: always verify struct size with static_assert or sizeof check.\n");
    printf("A silent padding change can corrupt DMA transfers or register overlays.\n");

    return 0;
}
```

---

# Topic 4: Static, Extern & Inline in Firmware Drivers

## Concept summary

In embedded firmware, code is organized into drivers and modules (e.g., `uart_driver.c`, `rf_config.c`, `mac_layer.c`). Proper use of `static`, `extern`, and `inline` is essential for:
- **Encapsulation**: hiding internal driver state
- **Performance**: `static inline` avoids function call overhead in hot paths
- **Correctness**: `static` variables in ISR functions persist between calls

**Rules for firmware drivers**:
- All internal functions → `static`
- All internal state variables → `static` global in the `.c` file
- Public API functions → declared in `.h`, defined in `.c` without `static`
- ISR-shared variables → `volatile` + possibly `static`
- Inline utilities → `static inline` in `.h` files

**BSS vs data segment** (matters for embedded):
- `static uint32_t x;` → BSS (zero in flash, zeroed by startup code — saves flash)
- `static uint32_t x = 5;` → Data segment (initial value stored in flash, copied to RAM at startup)

## Interview questions
1. Why would you mark a function `static` in a firmware driver?
2. What is the difference between a `static` local variable and a global variable?
3. Where does a `static uint32_t x` live in memory? What is its initial value?
4. What is the BSS segment and why does it matter for flash-constrained devices?
5. When would you use `static inline` instead of a `#define` macro?

## Runnable program

```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* ================================================================
   Simulated UART driver module — shows proper static/extern usage
   In a real project this would be split into uart_driver.c / .h
   ================================================================ */

/* Internal driver state — hidden from other modules */
static volatile uint32_t uart_rx_count   = 0;
static volatile uint32_t uart_tx_count   = 0;
static volatile uint8_t  uart_last_error = 0;
static bool              uart_initialized = false;

/* Internal (private) function */
static void uart_update_stats(bool is_tx) {
    if (is_tx) uart_tx_count++;
    else        uart_rx_count++;
}

/* ISR-like function: static variable persists between calls */
void uart_rx_isr(uint8_t byte) {
    static uint8_t  rx_buf[8];    /* persists between ISR calls */
    static uint32_t buf_idx = 0;

    rx_buf[buf_idx % 8] = byte;
    buf_idx++;
    uart_update_stats(false);

    if (buf_idx % 8 == 0)
        printf("  [UART ISR] Buffer filled. Total bytes: %u\n", buf_idx);
}

/* Public API */
bool uart_init(uint32_t baud_rate) {
    if (uart_initialized) return false;
    printf("UART init at %u baud\n", baud_rate);
    uart_initialized = true;
    uart_rx_count = uart_tx_count = uart_last_error = 0;
    return true;
}

uint32_t uart_get_rx_count(void)  { return uart_rx_count;   }
uint32_t uart_get_tx_count(void)  { return uart_tx_count;   }
uint8_t  uart_get_last_error(void){ return uart_last_error; }

/* static inline utility — zero overhead, type safe */
static inline uint8_t clamp_u8(uint32_t val) {
    return (val > 0xFFU) ? 0xFFU : (uint8_t)val;
}

static inline bool is_aligned(const void *ptr, size_t align) {
    return ((uintptr_t)ptr % align) == 0;
}

/* BSS vs Data segment demo */
static uint32_t bss_var;              /* BSS: zero, no flash cost    */
static uint32_t data_var  = 0xC0DE;  /* Data: stored in flash       */
static const uint32_t rom_const = 0xDEAD; /* const: stays in flash  */

int main() {
    printf("=== Static, Extern & Inline in Firmware Drivers ===\n\n");

    uart_init(115200);

    printf("\nSimulating 10 RX bytes through ISR:\n");
    for (uint8_t i = 1; i <= 10; i++)
        uart_rx_isr(i * 0x11);

    printf("\nUART stats:\n");
    printf("  RX count:   %u\n", uart_get_rx_count());
    printf("  TX count:   %u\n", uart_get_tx_count());
    printf("  Last error: %u\n\n", uart_get_last_error());

    /* static inline */
    printf("static inline clamp_u8:\n");
    printf("  clamp_u8(100)  = %u\n", clamp_u8(100));
    printf("  clamp_u8(300)  = %u\n", clamp_u8(300));
    printf("  clamp_u8(1000) = %u\n\n", clamp_u8(1000));

    /* Alignment check */
    uint32_t aligned_val;
    uint8_t  unaligned_buf[5];
    printf("Alignment checks:\n");
    printf("  uint32_t (expect aligned): %s\n",
           is_aligned(&aligned_val, 4) ? "aligned" : "UNALIGNED");
    printf("  &unaligned_buf[1] (expect unaligned to 4): %s\n",
           is_aligned(&unaligned_buf[1], 4) ? "aligned" : "unaligned");

    /* Memory segments */
    printf("\nMemory segments:\n");
    printf("  bss_var   = 0x%08X (zero-initialized, no flash storage)\n", bss_var);
    printf("  data_var  = 0x%08X (initial value in flash)\n",   data_var);
    printf("  rom_const = 0x%08X (const, lives in flash/ROM)\n", rom_const);

    return 0;
}
```

---

# Topic 5: Circular Buffer — The Core Embedded Data Structure

## Concept summary

The circular (ring) buffer is the single most important data structure in embedded firmware. Used in:
- **UART/SPI/I2C** RX and TX buffers
- **DMA descriptor rings** in 5G modem baseband
- **Inter-task message passing** in RTOS
- **RF sample buffers** (IQ data between PHY and MAC)
- **Log buffers** for post-mortem debug

**Key properties**:
- Fixed size — no dynamic allocation
- O(1) enqueue and dequeue
- Power-of-2 size allows fast `& (SIZE-1)` instead of `% SIZE`
- Single-producer single-consumer (SPSC) is lock-free on ARM if head/tail are `uint32_t`

**SPSC lock-free rule**: if only ONE writer and ONE reader, no mutex needed as long as `head` and `tail` are naturally atomic (`uint32_t` on 32-bit ARM). This is the basis of how UART ISR → task communication works.

## Interview questions
1. Why is a power-of-2 size preferred for a circular buffer?
2. How do you distinguish a full buffer from an empty one?
3. How would you make a circular buffer safe between an ISR (producer) and a task (consumer)?
4. What is SPSC and why can it be lock-free?
5. Implement `cbuf_peek` — read without removing.

## Runnable program

```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* ---- Byte circular buffer ---- */

#define CBUF_SIZE   16U   /* must be power of 2 */
#define CBUF_MASK   (CBUF_SIZE - 1U)

typedef struct {
    uint8_t  data[CBUF_SIZE];
    uint32_t head;     /* write index — producer owns this */
    uint32_t tail;     /* read index  — consumer owns this */
} CircBuf;

/* head and tail are never masked — they grow forever.
   Masking happens only at data access: data[head & MASK].
   This avoids the full/empty ambiguity without a count field,
   and works safely as long as uint32_t wraps naturally. */

void     cbuf_init   (CircBuf *cb)              { cb->head = cb->tail = 0; }
bool     cbuf_empty  (const CircBuf *cb)        { return cb->head == cb->tail; }
bool     cbuf_full   (const CircBuf *cb)        { return (cb->head - cb->tail) == CBUF_SIZE; }
uint32_t cbuf_count  (const CircBuf *cb)        { return cb->head - cb->tail; }
uint32_t cbuf_space  (const CircBuf *cb)        { return CBUF_SIZE - cbuf_count(cb); }

bool cbuf_push(CircBuf *cb, uint8_t byte) {
    if (cbuf_full(cb)) return false;
    cb->data[cb->head & CBUF_MASK] = byte;
    cb->head++;          /* single write — atomic on 32-bit ARM */
    return true;
}

bool cbuf_pop(CircBuf *cb, uint8_t *out) {
    if (cbuf_empty(cb)) return false;
    *out = cb->data[cb->tail & CBUF_MASK];
    cb->tail++;          /* single write — atomic on 32-bit ARM */
    return true;
}

bool cbuf_peek(const CircBuf *cb, uint8_t *out) {
    if (cbuf_empty(cb)) return false;
    *out = cb->data[cb->tail & CBUF_MASK];
    /* tail not advanced — non-destructive read */
    return true;
}

/* Bulk push — for DMA-style transfers */
uint32_t cbuf_push_bulk(CircBuf *cb, const uint8_t *src, uint32_t n) {
    uint32_t written = 0;
    while (written < n && !cbuf_full(cb)) {
        cb->data[cb->head & CBUF_MASK] = src[written++];
        cb->head++;
    }
    return written;
}

void cbuf_print_state(const CircBuf *cb, const char *label) {
    printf("%-30s head=%-4u tail=%-4u count=%-3u space=%-3u | ",
           label, cb->head, cb->tail, cbuf_count(cb), cbuf_space(cb));
    uint32_t idx = cb->tail;
    for (uint32_t i = 0; i < cbuf_count(cb); i++)
        printf("0x%02X ", cb->data[idx++ & CBUF_MASK]);
    printf("\n");
}

/* ---- SPSC explanation ---- */
void spsc_explanation() {
    printf("\nSPSC (Single-Producer Single-Consumer) lock-free rule:\n");
    printf("  Producer writes head, reads tail  → no conflict\n");
    printf("  Consumer writes tail, reads head  → no conflict\n");
    printf("  uint32_t read/write is atomic on 32-bit ARM (single instruction)\n");
    printf("  → No mutex needed for one ISR producer + one task consumer\n");
    printf("  (Add memory barriers on ARM Cortex-A for strict ordering)\n\n");
}

int main() {
    printf("=== Circular Buffer ===\n\n");

    CircBuf cb;
    cbuf_init(&cb);
    cbuf_print_state(&cb, "Initial:");

    /* Push 8 bytes */
    uint8_t tx_data[] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
    uint32_t wrote = cbuf_push_bulk(&cb, tx_data, 8);
    printf("Bulk pushed %u bytes\n", wrote);
    cbuf_print_state(&cb, "After bulk push 8:");

    /* Peek without removing */
    uint8_t peek_val;
    cbuf_peek(&cb, &peek_val);
    printf("Peek: 0x%02X (count unchanged)\n", peek_val);
    cbuf_print_state(&cb, "After peek:");

    /* Pop 5 */
    printf("\nPopping 5 bytes: ");
    uint8_t out;
    for (int i = 0; i < 5; i++) {
        cbuf_pop(&cb, &out);
        printf("0x%02X ", out);
    }
    printf("\n");
    cbuf_print_state(&cb, "After pop 5:");

    /* Fill to capacity */
    printf("\nFilling to capacity:\n");
    for (int i = 0; i < 20; i++) {
        bool ok = cbuf_push(&cb, (uint8_t)(0xA0 + i));
        if (!ok) printf("  Full at i=%d — dropping 0x%02X\n", i, 0xA0 + i);
    }
    cbuf_print_state(&cb, "After fill attempt:");

    /* Drain */
    printf("\nDraining:\n");
    while (!cbuf_empty(&cb)) {
        cbuf_pop(&cb, &out);
        printf("0x%02X ", out);
    }
    printf("\n");
    cbuf_print_state(&cb, "After drain:");

    /* Wrap-around test */
    printf("\nWrap-around test (head/tail cross CBUF_SIZE boundary):\n");
    for (int i = 0; i < 20; i++) {
        cbuf_push(&cb, (uint8_t)i);
        cbuf_pop(&cb, &out);
    }
    cbuf_print_state(&cb, "After 20 push+pop cycles:");
    printf("  head and tail wrapped naturally — no special handling needed\n");

    spsc_explanation();
    return 0;
}
```

---

# Topic 6: FIFO Message Queue (Typed, Embedded-Style)

## Concept summary

A typed FIFO queue is how tasks and ISRs communicate in real-time firmware — the backbone of any RTOS-based modem stack.

In a 5G RAN context:
- **L1 → L2 message passing**: PHY layer pushes `TTI_IND` messages to MAC
- **Command queues**: host processor sends config commands to DSP
- **Event queues**: hardware interrupt fires, ISR pushes event to task queue

**Design requirements for embedded FIFO**:
- Fixed capacity (no malloc)
- O(1) push and pop
- ISR-safe (if SPSC, no lock needed; if MPSC, need critical section)
- Typed messages (use a struct + enum, not raw bytes)

**Full policy choices**:
| Policy | Use case |
|---|---|
| Drop newest | Protect existing data (log buffers) |
| Drop oldest | Always have latest data (sensor readings) |
| Block | RTOS tasks with semaphore |

## Interview questions
1. How do you make a message queue safe to use from an ISR?
2. What is the difference between drop-oldest and drop-newest full policies?
3. How would you add a priority to this queue?
4. How does this differ from an RTOS queue (e.g., FreeRTOS `xQueueSend`)?
5. What is the maximum latency to process a message in a polling design vs interrupt-driven?

## Runnable program

```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* ---- Message types (5G RAN flavour) ---- */
typedef enum {
    MSG_TTI_INDICATION   = 0x01,   /* L1 → L2: slot timing */
    MSG_UL_DATA_IND      = 0x02,   /* L1 → L2: uplink data ready */
    MSG_DL_CONFIG_REQ    = 0x03,   /* L2 → L1: downlink config */
    MSG_HARQ_FEEDBACK    = 0x04,   /* L1 → L2: HARQ ACK/NACK */
    MSG_RESET_REQ        = 0xFF,   /* system reset */
} MsgId;

typedef struct {
    MsgId    id;
    uint32_t timestamp_us;    /* microsecond timestamp */
    uint32_t payload;
    uint8_t  rnti;            /* Radio Network Temp ID */
    uint8_t  harq_pid;        /* HARQ process ID */
} Message;

/* ---- Fixed-capacity typed FIFO ---- */
#define QUEUE_SIZE   8U

typedef struct {
    Message  buf[QUEUE_SIZE];
    uint32_t head;
    uint32_t tail;
    uint32_t count;
    uint32_t dropped;         /* stats: how many were dropped */
} MsgQueue;

void     mq_init    (MsgQueue *q) { q->head = q->tail = q->count = q->dropped = 0; }
bool     mq_empty   (const MsgQueue *q) { return q->count == 0; }
bool     mq_full    (const MsgQueue *q) { return q->count == QUEUE_SIZE; }
uint32_t mq_count   (const MsgQueue *q) { return q->count; }

/* Push — drop-newest policy (protect existing messages) */
bool mq_push(MsgQueue *q, const Message *m) {
    if (mq_full(q)) {
        q->dropped++;
        return false;
    }
    q->buf[q->head % QUEUE_SIZE] = *m;
    q->head++;
    q->count++;
    return true;
}

/* Push — drop-oldest policy (always accept, discard oldest) */
bool mq_push_overwrite(MsgQueue *q, const Message *m) {
    if (mq_full(q)) {
        q->tail++;     /* discard oldest */
        q->count--;
        q->dropped++;
    }
    q->buf[q->head % QUEUE_SIZE] = *m;
    q->head++;
    q->count++;
    return true;
}

bool mq_pop(MsgQueue *q, Message *out) {
    if (mq_empty(q)) return false;
    *out = q->buf[q->tail % QUEUE_SIZE];
    q->tail++;
    q->count--;
    return true;
}

bool mq_peek(const MsgQueue *q, Message *out) {
    if (mq_empty(q)) return false;
    *out = q->buf[q->tail % QUEUE_SIZE];
    return true;
}

const char* msg_name(MsgId id) {
    switch(id) {
        case MSG_TTI_INDICATION: return "TTI_IND";
        case MSG_UL_DATA_IND:    return "UL_DATA";
        case MSG_DL_CONFIG_REQ:  return "DL_CFG ";
        case MSG_HARQ_FEEDBACK:  return "HARQ_FB";
        case MSG_RESET_REQ:      return "RESET  ";
        default:                 return "UNKNOWN";
    }
}

void mq_print(const MsgQueue *q) {
    printf("  Queue [%u/%u, dropped=%u]:\n", q->count, QUEUE_SIZE, q->dropped);
    uint32_t idx = q->tail;
    for (uint32_t i = 0; i < q->count; i++) {
        const Message *m = &q->buf[idx++ % QUEUE_SIZE];
        printf("    [%u] %-8s ts=%6uus payload=0x%08X rnti=0x%02X harq=%u\n",
               i, msg_name(m->id), m->timestamp_us,
               m->payload, m->rnti, m->harq_pid);
    }
}

/* Simulate L1 ISR pushing TTI every slot */
static MsgQueue g_l1_to_l2_queue;

void l1_tti_isr(uint32_t slot_num) {
    Message m = {
        .id           = MSG_TTI_INDICATION,
        .timestamp_us = slot_num * 500,   /* 500us per slot in 5G NR */
        .payload      = slot_num,
        .rnti         = 0,
        .harq_pid     = 0,
    };
    if (!mq_push(&g_l1_to_l2_queue, &m))
        printf("  [L1 ISR] slot %u dropped — queue full!\n", slot_num);
}

/* Simulate L2 MAC task consuming messages */
void l2_mac_task_process(void) {
    Message m;
    while (mq_pop(&g_l1_to_l2_queue, &m)) {
        printf("  [L2 MAC] Processing %-8s slot=%u\n",
               msg_name(m.id), m.payload);
    }
}

int main() {
    printf("=== Typed FIFO Message Queue (5G RAN style) ===\n\n");

    MsgQueue q;
    mq_init(&q);

    /* Populate with realistic messages */
    Message msgs[] = {
        { MSG_TTI_INDICATION, 1000, 2,  0xA1, 0 },
        { MSG_UL_DATA_IND,    1500, 64, 0xA1, 1 },
        { MSG_DL_CONFIG_REQ,  2000, 0,  0xB2, 0 },
        { MSG_HARQ_FEEDBACK,  2500, 1,  0xA1, 1 },
        { MSG_TTI_INDICATION, 3000, 3,  0,    0 },
    };
    printf("Pushing 5 messages:\n");
    for (int i = 0; i < 5; i++) {
        bool ok = mq_push(&q, &msgs[i]);
        printf("  push %-8s: %s\n", msg_name(msgs[i].id), ok ? "OK" : "DROPPED");
    }
    mq_print(&q);

    /* Pop 2 and process */
    printf("\nProcessing 2 messages:\n");
    Message out;
    for (int i = 0; i < 2; i++) {
        if (mq_pop(&q, &out))
            printf("  processed: %-8s ts=%uus\n", msg_name(out.id), out.timestamp_us);
    }
    mq_print(&q);

    /* Test drop-newest overflow */
    printf("\nOverflow test (drop-newest, filling %u more than capacity):\n", QUEUE_SIZE);
    MsgQueue q2; mq_init(&q2);
    for (int i = 0; i < 12; i++) {
        Message m = { MSG_TTI_INDICATION, (uint32_t)(i*500), (uint32_t)i, 0, 0 };
        bool ok = mq_push(&q2, &m);
        if (!ok) printf("  dropped slot %d\n", i);
    }
    mq_print(&q2);

    /* Test drop-oldest overflow */
    printf("\nOverflow test (drop-oldest policy):\n");
    MsgQueue q3; mq_init(&q3);
    for (int i = 0; i < 12; i++) {
        Message m = { MSG_TTI_INDICATION, (uint32_t)(i*500), (uint32_t)i, 0, 0 };
        mq_push_overwrite(&q3, &m);
    }
    mq_print(&q3);
    printf("  (only the 8 most recent slots are kept)\n\n");

    /* L1 ISR → L2 task simulation */
    printf("L1 ISR → L2 MAC task simulation:\n");
    mq_init(&g_l1_to_l2_queue);
    for (uint32_t slot = 0; slot < 5; slot++)
        l1_tti_isr(slot);
    l2_mac_task_process();

    return 0;
}
```

---

# Topic 7: ISR Safety, Critical Sections & Race Conditions

## Concept summary

This is the topic that trips up engineers who come from application software backgrounds. In firmware, **code can be interrupted at any point** by a hardware interrupt. This creates race conditions on shared data.

**Race condition example**:
```c
/* Non-atomic on most architectures — 3 instructions: load, add, store */
shared_counter++;   /* ISR fires between load and store → count lost */
```

**Critical section**: a region of code that must not be interrupted.
```c
disable_interrupts();
/* ... access shared data ... */
enable_interrupts();
```

**SPSC (single-producer single-consumer)**: if exactly one ISR writes and one task reads, and both access different variables (`head` vs `tail`), no critical section is needed on 32-bit ARM — but memory barriers may be needed on Cortex-A.

**Volatile is NOT enough for atomicity**: `volatile` ensures the compiler reads from memory, but a multi-step RMW on a `volatile` variable is still non-atomic — the ISR can fire between steps.

## Interview questions
1. What is a race condition? Give a firmware example.
2. What is the difference between `volatile` and a critical section?
3. When can you safely avoid a mutex in ISR↔task communication?
4. What is priority inversion and how does it occur?
5. What happens if an ISR fires during a `malloc` call?

## Runnable program

```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* ---- Simulated critical section (on real HW: disable/enable IRQ) ---- */
static int irq_disabled_count = 0;

void critical_section_enter(void) {
    irq_disabled_count++;   /* on ARM: CPSID I  or  __disable_irq() */
}

void critical_section_exit(void) {
    irq_disabled_count--;   /* on ARM: CPSIE I  or  __enable_irq()  */
}

bool in_critical_section(void) { return irq_disabled_count > 0; }

/* ---- Shared state between "ISR" and task ---- */
static volatile uint32_t isr_event_count   = 0;
static volatile uint32_t task_event_count  = 0;
static volatile uint8_t  shared_flags      = 0x00;

#define FLAG_DATA_READY   (1U << 0)
#define FLAG_ERROR        (1U << 1)
#define FLAG_OVERFLOW     (1U << 2)

/* Simulate ISR — sets a flag and increments counter */
void simulate_isr(uint8_t new_flag) {
    /* ISR context: short, fast, no blocking */
    isr_event_count++;
    shared_flags |= new_flag;   /* atomic OR on single byte on ARM */
    printf("  [ISR] event %u, flags=0x%02X\n", isr_event_count, shared_flags);
}

/* Task: reads and clears flags atomically */
uint8_t task_read_and_clear_flags(void) {
    uint8_t flags;
    critical_section_enter();
    flags = shared_flags;
    shared_flags = 0x00;        /* read-modify-write — must be in critical section */
    critical_section_exit();
    return flags;
}

/* ---- Race condition demonstration ---- */
typedef struct {
    uint32_t high;
    uint32_t low;
} Counter64;

static volatile Counter64 g_counter = {0, 0};

/* Non-atomic 64-bit increment — ISR can corrupt this */
void unsafe_increment(void) {
    g_counter.low++;
    /* If ISR fires here and reads g_counter, it sees inconsistent state */
    if (g_counter.low == 0)
        g_counter.high++;
}

/* Safe 64-bit increment with critical section */
void safe_increment(void) {
    critical_section_enter();
    g_counter.low++;
    if (g_counter.low == 0)
        g_counter.high++;
    critical_section_exit();
}

/* ---- SPSC: no lock needed ---- */
#define SPSC_SIZE 4U

typedef struct {
    uint32_t data[SPSC_SIZE];
    volatile uint32_t head;  /* producer (ISR) writes */
    volatile uint32_t tail;  /* consumer (task) writes */
} SpscQueue;

void spsc_init(SpscQueue *q)  { q->head = q->tail = 0; }
bool spsc_full (SpscQueue *q) { return (q->head - q->tail) == SPSC_SIZE; }
bool spsc_empty(SpscQueue *q) { return q->head == q->tail; }

bool spsc_push(SpscQueue *q, uint32_t val) {
    if (spsc_full(q)) return false;
    q->data[q->head % SPSC_SIZE] = val;
    q->head++;   /* single store — ISR-safe on 32-bit ARM */
    return true;
}

bool spsc_pop(SpscQueue *q, uint32_t *out) {
    if (spsc_empty(q)) return false;
    *out = q->data[q->tail % SPSC_SIZE];
    q->tail++;   /* single store — task-safe */
    return true;
}

int main() {
    printf("=== ISR Safety, Critical Sections & Race Conditions ===\n\n");

    /* ISR sets flags, task reads them */
    printf("ISR → Task flag passing:\n");
    simulate_isr(FLAG_DATA_READY);
    simulate_isr(FLAG_DATA_READY | FLAG_ERROR);

    uint8_t f = task_read_and_clear_flags();
    printf("  [Task] read flags=0x%02X (DATA_READY=%u ERROR=%u)\n\n",
           f, !!(f & FLAG_DATA_READY), !!(f & FLAG_ERROR));

    f = task_read_and_clear_flags();
    printf("  [Task] read flags=0x%02X (cleared by previous read)\n\n", f);

    /* Safe counter */
    printf("Safe 64-bit counter (with critical section):\n");
    for (int i = 0; i < 5; i++) safe_increment();
    printf("  g_counter = {high=%u, low=%u}\n\n", g_counter.high, g_counter.low);

    /* SPSC */
    printf("SPSC queue (lock-free):\n");
    SpscQueue sq;
    spsc_init(&sq);

    printf("  ISR pushing: ");
    for (uint32_t i = 0; i < 4; i++) {
        spsc_push(&sq, i * 100);
        printf("%u ", i * 100);
    }
    printf("\n  Task popping: ");
    uint32_t val;
    while (!spsc_empty(&sq)) {
        spsc_pop(&sq, &val);
        printf("%u ", val);
    }
    printf("\n\n");

    printf("Key rules:\n");
    printf("  1. volatile ensures fresh memory access — NOT atomicity\n");
    printf("  2. multi-step RMW on shared data needs a critical section\n");
    printf("  3. SPSC with uint32_t head/tail is lock-free on 32-bit ARM\n");
    printf("  4. ISR functions must be short — never call malloc/free in ISR\n");
    printf("  5. disable interrupts for the shortest time possible\n");

    return 0;
}
```

---

# Topic 8: Endianness & Protocol Header Parsing

## Concept summary

In 5G RAN firmware, you constantly parse and build protocol headers:
- **5G NR MAC headers** (TS 38.321)
- **IP/UDP headers** for F1/E1/N2/N3 interfaces
- **Custom IQ framing** for fronthaul (eCPRI, O-RAN 7.2x)

Networks use **big-endian** (MSB first). Most modern processors (ARM, x86) are **little-endian**. You must convert between them.

**Detection at runtime**:
```c
uint32_t val = 1;
bool little_endian = *(uint8_t*)&val == 1;
```

**Byte swap functions**:
- GCC built-in: `__builtin_bswap32(x)`, `__builtin_bswap16(x)` — compiles to a single `REV` instruction on ARM
- Manual: portable, always works

**Network-to-host macros** (from `<arpa/inet.h>` on Linux, manual in bare-metal):
```c
#define NTOHL(x)  bswap32_if_le(x)
#define NTOHS(x)  bswap16_if_le(x)
#define HTONL(x)  bswap32_if_le(x)
```

## Interview questions
1. What is endianness? How do you detect it at runtime?
2. Why do network protocols use big-endian byte order?
3. How do you parse a 16-bit big-endian field from a byte buffer?
4. What is the difference between `ntohl` and `htonl`?
5. Write a function to parse a 5G NR MAC subheader from a byte array.

## Runnable program

```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

/* ---- Endianness detection ---- */
bool system_is_little_endian(void) {
    uint32_t val = 1;
    return *(uint8_t*)&val == 1;
}

/* ---- Byte swap functions ---- */
uint16_t bswap16(uint16_t x) {
    return (uint16_t)(((x & 0xFF00U) >> 8) | ((x & 0x00FFU) << 8));
}

uint32_t bswap32(uint32_t x) {
    return ((x & 0xFF000000UL) >> 24) |
           ((x & 0x00FF0000UL) >>  8) |
           ((x & 0x0000FF00UL) <<  8) |
           ((x & 0x000000FFUL) << 24);
}

/* Network-to-host (on little-endian system) */
#define NTOHS(x) bswap16(x)
#define NTOHL(x) bswap32(x)
#define HTONS(x) bswap16(x)
#define HTONL(x) bswap32(x)

/* ---- Read big-endian values from byte buffer (no alignment assumed) ---- */
uint16_t read_be16(const uint8_t *buf) {
    return (uint16_t)((buf[0] << 8) | buf[1]);
}

uint32_t read_be32(const uint8_t *buf) {
    return ((uint32_t)buf[0] << 24) |
           ((uint32_t)buf[1] << 16) |
           ((uint32_t)buf[2] <<  8) |
           ((uint32_t)buf[3]);
}

void write_be16(uint8_t *buf, uint16_t val) {
    buf[0] = (val >> 8) & 0xFF;
    buf[1] =  val       & 0xFF;
}

void write_be32(uint8_t *buf, uint32_t val) {
    buf[0] = (val >> 24) & 0xFF;
    buf[1] = (val >> 16) & 0xFF;
    buf[2] = (val >>  8) & 0xFF;
    buf[3] =  val        & 0xFF;
}

/* ---- Simplified 5G NR MAC subheader parser (TS 38.321) ---- */
/* Short format (2 bytes): [R|F=0|LCID][L]
   Long  format (3 bytes): [R|F=1|LCID][L_MSB][L_LSB] */
typedef struct {
    uint8_t  lcid;
    uint16_t payload_len;
    uint8_t  header_bytes;   /* 2 or 3 */
} NR_SubHeader;

bool parse_nr_mac_subheader(const uint8_t *buf, size_t buf_len, NR_SubHeader *out) {
    if (!buf || buf_len < 2) return false;

    uint8_t byte0 = buf[0];
    uint8_t f_bit = (byte0 >> 6) & 1;
    out->lcid     =  byte0 & 0x3F;

    if (f_bit == 0) {
        /* Short: payload length in byte 1 */
        out->payload_len  = buf[1];
        out->header_bytes = 2;
    } else {
        /* Long: payload length in bytes 1-2 (big-endian) */
        if (buf_len < 3) return false;
        out->payload_len  = read_be16(&buf[1]);
        out->header_bytes = 3;
    }
    return true;
}

/* ---- Print bytes ---- */
void print_bytes(const char *label, const uint8_t *buf, int n) {
    printf("%-30s", label);
    for (int i = 0; i < n; i++) printf("%02X ", buf[i]);
    printf("\n");
}

int main() {
    printf("=== Endianness & Protocol Header Parsing ===\n\n");

    printf("This system: %s-endian\n\n",
           system_is_little_endian() ? "LITTLE" : "BIG");

    /* Byte ordering demo */
    uint32_t val = 0x12345678UL;
    uint8_t *b   = (uint8_t*)&val;
    printf("0x%08X in memory (little-endian): %02X %02X %02X %02X\n",
           val, b[0], b[1], b[2], b[3]);
    printf("  byte[0]=0x%02X is %s byte\n\n",
           b[0], b[0] == 0x78 ? "LEAST significant (little-endian)" : "MOST significant (big-endian)");

    /* bswap */
    printf("Byte swap:\n");
    printf("  bswap16(0x1234)     = 0x%04X\n", bswap16(0x1234U));
    printf("  bswap32(0x12345678) = 0x%08X\n\n", bswap32(0x12345678UL));

    /* Write and read big-endian field (network-style) */
    printf("Big-endian field in byte buffer:\n");
    uint8_t buf[8] = {0};
    write_be32(buf, 0xDEADBEEFUL);
    print_bytes("  write_be32(0xDEADBEEF):", buf, 4);
    printf("  read_be32 back: 0x%08X\n\n", read_be32(buf));

    write_be16(buf, 500);
    print_bytes("  write_be16(500):", buf, 2);
    printf("  read_be16 back: %u\n\n", read_be16(buf));

    /* 5G NR MAC subheader parsing */
    printf("5G NR MAC subheader parsing:\n");

    /* Short format: F=0, LCID=3, length=64 */
    uint8_t mac_short[] = { 0x03, 0x40 };  /* LCID=3, L=64 */
    print_bytes("  Short subheader bytes:", mac_short, 2);
    NR_SubHeader hdr;
    if (parse_nr_mac_subheader(mac_short, sizeof(mac_short), &hdr))
        printf("  → LCID=%u len=%u header_bytes=%u\n\n",
               hdr.lcid, hdr.payload_len, hdr.header_bytes);

    /* Long format: F=1, LCID=4, length=1024 */
    uint8_t mac_long[] = { 0x44, 0x04, 0x00 };  /* F=1,LCID=4, L=1024 */
    print_bytes("  Long subheader bytes:", mac_long, 3);
    if (parse_nr_mac_subheader(mac_long, sizeof(mac_long), &hdr))
        printf("  → LCID=%u len=%u header_bytes=%u\n\n",
               hdr.lcid, hdr.payload_len, hdr.header_bytes);

    printf("Rule: always use read_be16/read_be32 from byte arrays.\n");
    printf("Never cast a uint8_t* directly to uint16_t* — unaligned access fault on ARM.\n");

    return 0;
}
```

---

# Quick Reference: Embedded Firmware Cheat Sheet

## Volatile rules
```c
volatile uint32_t *REG = (volatile uint32_t *)0xA0010000UL; /* hardware register */
volatile uint32_t isr_flag;   /* modified in ISR */
/* volatile = fresh read/write. NOT atomic. NOT a memory barrier. */
```

## Bit manipulation
```c
reg |=  (1U << N)              /* set bit N   */
reg &= ~(1U << N)              /* clear bit N */
reg ^=  (1U << N)              /* toggle bit N */
(reg >> N) & 1U                /* check bit N */
/* field [M:N]: */
mask = ((1U << width) - 1U) << shift
reg  = (reg & ~mask) | ((val << shift) & mask)
```

## Struct in firmware
```c
/* Rule: largest member first → minimize padding */
/* Use __attribute__((packed)) for protocol headers */
/* Use static_assert(sizeof(S) == N) to catch regressions */
```

## Critical section pattern (bare-metal ARM)
```c
__disable_irq();    /* or: uint32_t primask = __get_PRIMASK(); __disable_irq(); */
/* ... access shared data ... */
__enable_irq();     /* or: __set_PRIMASK(primask); */
```

## Circular buffer size trick
```c
/* Power-of-2 size → use mask instead of modulo */
buf[head & (SIZE - 1)] = val;   /* faster than buf[head % SIZE] */
```

## Endianness in protocol parsing
```c
/* NEVER: uint16_t *p = (uint16_t*)buf; val = *p; — unaligned fault! */
/* ALWAYS: */
uint16_t val = (uint16_t)((buf[0] << 8) | buf[1]);  /* safe big-endian read */
```

## ISR rules
```c
/* ISR must be: short, non-blocking, no malloc, no printf */
/* Signal task via: flag, semaphore, or SPSC queue */
/* Shared multi-byte data: use critical section */
/* SPSC uint32_t head/tail: lock-free on 32-bit ARM */
```

---

*This covers embedded firmware C as tested by companies in 5G RAN, modem, and real-time systems.*
