# Embedded Linux L — Hardware (LA9310, VSPA, M4, FreeRTOS) Study Notes

The "below the OS" half of the system: the NXP LA9310 RF SoC, its VSPA DSP, its
Cortex-M4 microcontroller, the FreeRTOS firmware they run, and the mechanisms by which
the host A35 (Linux) talks to them.

This section is **bonus territory** — skip it until you draw an RF/DFE ticket. But once
you do, you cannot avoid any of it.

For each topic:
1. **Layman** — what it actually is, in plain English
2. **In this project** — how nr_ue_phy uses it
3. **Minimal example** — a tiny self-contained snippet (where applicable on RPi)
4. **In tree** — concrete `file:line` pointer into nr_ue_phy

---

## Table of contents

- [L1. The big picture: A35 + M4 + VSPA on one SoC](#l1-the-big-picture-a35--m4--vspa-on-one-soc)
- [L2. NXP LA9310 RF SoC overview](#l2-nxp-la9310-rf-soc-overview)
- [L3. The VSPA DSP](#l3-the-vspa-dsp)
- [L4. The Cortex-M4 microcontroller](#l4-the-cortex-m4-microcontroller)
- [L5. FreeRTOS basics (only because the M4 firmware uses it)](#l5-freertos-basics-only-because-the-m4-firmware-uses-it)
- [L6. Memory-mapped I/O (MMIO)](#l6-memory-mapped-io-mmio)
- [L7. DMA — direct memory access](#l7-dma--direct-memory-access)
- [L8. Mailboxes — IPC between cores](#l8-mailboxes--ipc-between-cores)
- [L9. Shared memory between A35 and M4](#l9-shared-memory-between-a35-and-m4)
- [L10. The DFE/RF integration in nr\_ue\_phy](#l10-the-dferf-integration-in-nr_ue_phy)
- [L11. The 1-PPS clock and frequency calibration](#l11-the-1-pps-clock-and-frequency-calibration)

---

## L1. The big picture: A35 + M4 + VSPA on one SoC

**Layman.** A modern RF SoC isn't one CPU. It's:
- One or more **application processors** (ARM Cortex-A35 here, running Linux)
- A **microcontroller** (ARM Cortex-M4 here, running FreeRTOS) for tight, deterministic
  RF control
- A **DSP** (NXP's proprietary VSPA — Vector Signal Processing Architecture) for the
  inner numerical loop (FFT, mixing, decimation, baseband formatting)

They share DRAM but have their own boot images and instruction sets. They communicate via
**mailboxes** (small IRQ-backed registers) for events and **shared memory** for bulk data.
The A35 cannot directly call functions on the M4, and the M4 cannot directly call
functions on the VSPA — every cross-core action is "drop a request in shared memory,
ring the mailbox."

**In this project.** Each core runs different code:
- A35 — `uephy` binary (the PHY you've been reading)
- M4 — firmware in `3rdparty/nxp/la93xx_freertos/` and our extension code in
  `toplevel/dfec/` (built into a separate ELF flashed to M4 RAM)
- VSPA — firmware in `3rdparty/nxp/bsp_nlm_vspa/LA9310_cal/` (very different toolchain,
  built separately, see `NMM_REBUILD_VSPA` cmake option)

**Reading.** NXP LA9310 reference manual (in `3rdparty/nxp/` somewhere). Start with the
"system architecture" chapter; you don't need register-level depth until you debug.

---

## L2. NXP LA9310 RF SoC overview

**Layman.** The LA9310 is a complete software-defined-radio chip. Inputs: an antenna /
mixer / ADC chain. Outputs: digital baseband (I/Q samples) into the host's DRAM. Inside
it has the M4, the VSPA, an AVI (analog/digital interface) that interfaces with the ADCs
and DACs, plus all the glue (DMA controllers, mailboxes, timers, clock dividers).

The "Cortex-A35 host" sits *outside* the LA9310 on most boards (StarTag uses an
NXP Layerscape SoC for the host A35; the LA9310 is a co-processor on the same PCB).

**In this project.** The board variants are gated by CMake options:
- `RFHW_NXPRDB1` — NXP reference board
- `RFHW_STARTAG_*` — eSpace's StarTag boards (B0, 100, 101, 110)

These choose pin maps, mixer ICs (ADRF6755 / ADRF6850), and AVI configuration. Most code
that touches a register sits behind one of these `#ifdef`s.

**In tree.**
- Hardware feature flags:
  [CMakeLists.txt:79-93](/home/cb24/workspace/nr_ue_phy/CMakeLists.txt#L79-L93)
- The DFE component IDs and the M4-side context structure:
  [toplevel/dfec/ue_ctx.h](/home/cb24/workspace/nr_ue_phy/toplevel/dfec/ue_ctx.h)
- Per-board pin mapping for mixers — search `stg_ADRF6755_iqmod` and `stg_gpio` headers.

---

## L3. The VSPA DSP

**Layman.** VSPA is NXP's vector DSP. Think "very wide SIMD" — large vector registers,
dedicated multiply-accumulate units, and an instruction set tuned for FFTs and complex
arithmetic. It is *not* an ARM core. It boots independently, runs its own firmware, and
communicates back to the M4 over mailboxes. Everything time-critical in the inner DSP
loop runs there.

**In this project.** VSPA firmware lives in `3rdparty/nxp/bsp_nlm_vspa/LA9310_cal/` and
is built by a separate toolchain. The `NMM_REBUILD_VSPA` CMake option controls whether
the host build also rebuilds the VSPA image. The A35 PHY *never* talks directly to VSPA;
all VSPA messaging is brokered by the M4.

The host PHY's interest in VSPA is mostly through `Dfe_BasebandDataIndication_t` —
"VSPA finished a slot's downlink samples; here's the address in shared memory." See
[toplevel/dfec/trd_vspaMsgHndlr.c:92-105](/home/cb24/workspace/nr_ue_phy/toplevel/dfec/trd_vspaMsgHndlr.c#L92-L105).

**In tree.**
- VSPA top-level firmware entry:
  [3rdparty/nxp/bsp_nlm_vspa/LA9310_cal/Sources/_main.c](/home/cb24/workspace/nr_ue_phy/3rdparty/nxp/bsp_nlm_vspa/LA9310_cal/Sources/_main.c)
  — note `VCPU_SET_CONTROL`, `VCPU_SET_VERSION` MMIO writes at the very start.

---

## L4. The Cortex-M4 microcontroller

**Layman.** A Cortex-M4 is a small, cheap, 32-bit ARM microcontroller designed for
deterministic embedded control. No MMU, no virtual memory; runs from on-chip RAM/flash.
Wakes up on interrupts (peripheral, timer, mailbox) in microseconds. Used here as the
"RF traffic cop": handles mixer/ADC initialisation, slot timing, AGC, frequency control,
and forwards commands between the host A35 and VSPA.

**In this project.** All `toplevel/dfec/` files are M4 code. They use the FreeRTOS API
(see L5) — `xEventGroupWaitBits`, `xQueueSend`, `vTaskCreate`, etc. This is the *only*
part of the codebase that's not Linux user-space.

The flow on each slot:
1. M4 receives a slot-config request from A35 (mailbox + shared memory)
2. M4 forwards it to VSPA (mailbox + shared memory)
3. VSPA does the heavy DSP, drops result into shared memory, mailboxes M4
4. M4 packages a `Dfe_*Indication_t` and mailboxes A35

**In tree.**
- Real M4 task using FreeRTOS event groups + mailbox reads:
  [toplevel/dfec/trd_vspaMsgHndlr.c:43-59](/home/cb24/workspace/nr_ue_phy/toplevel/dfec/trd_vspaMsgHndlr.c#L43-L59)
- Slot indication handler — what runs when the AVI says "new slot":
  [toplevel/dfec/trd_slotInd.c](/home/cb24/workspace/nr_ue_phy/toplevel/dfec/trd_slotInd.c)
- M4 linker script — defines the address map the firmware is built into:
  [toplevel/dfec/la9310.ld](/home/cb24/workspace/nr_ue_phy/toplevel/dfec/la9310.ld)

---

## L5. FreeRTOS basics (only because the M4 firmware uses it)

**Layman.** FreeRTOS is a tiny preemptive RTOS for microcontrollers. It provides:
- **Tasks** — equivalent of threads, scheduled by priority
- **Queues** — fixed-element-size FIFOs between tasks (or task ↔ ISR)
- **Semaphores / mutexes** — same idea as POSIX, much smaller implementation
- **Event groups** — bitmasks of "events"; tasks block until any/all bits are set
- **Software timers** — callback-after-delay, executed in a service task

Crucially, FreeRTOS APIs come in two flavours: **regular** (call from task context) and
**FromISR** (call from interrupt context, with different semantics for safety). Get this
wrong and you corrupt the kernel.

**In this project.** Only the M4 firmware uses FreeRTOS. The A35 PHY uses POSIX. The
patterns you see in `toplevel/dfec/`:

| Need | FreeRTOS call |
|---|---|
| Wait until VSPA finishes | `xEventGroupWaitBits(grp, mask, clear, anyAll, timeout)` |
| Send slot config to VSPA | `qsend_generic(...)` (project wrapper around `xQueueSend`) |
| Periodic 1 ms tick | software timer / hardware-timer ISR |
| Run a job at slot edge | task waits on event bit set by AVI ISR |

You do **not** need to learn FreeRTOS in depth for nr_ue_phy work; learn the four APIs
above and you can read the M4 code.

**Minimal example (running on M4 — for reference, not on your RPi).**
```c
static EventGroupHandle_t evt;

void avi_isr(void) {
    BaseType_t hpw = pdFALSE;
    xEventGroupSetBitsFromISR(evt, BIT_NEW_SLOT, &hpw);
    portYIELD_FROM_ISR(hpw);
}

void slot_task(void *unused) {
    for (;;) {
        xEventGroupWaitBits(evt, BIT_NEW_SLOT, pdTRUE, pdFALSE, portMAX_DELAY);
        process_slot();
    }
}
```

**In tree.**
- The kernel itself (read `tasks.c` once if you want to understand scheduling):
  [3rdparty/nxp/la93xx_freertos/FreeRTOS-Kernel/](/home/cb24/workspace/nr_ue_phy/3rdparty/nxp/la93xx_freertos/FreeRTOS-Kernel/)
- Real `xEventGroupWaitBits` use:
  [toplevel/dfec/trd_vspaMsgHndlr.c:49-53](/home/cb24/workspace/nr_ue_phy/toplevel/dfec/trd_vspaMsgHndlr.c#L49-L53)

---

## L6. Memory-mapped I/O (MMIO)

**Layman.** "Reading a register" on a peripheral means dereferencing a specific physical
address. A timer reload value at, say, `0x40000010` is just a `volatile uint32_t *` you
write to. The CPU's bus matrix routes that write to the timer block instead of DRAM. The
key word is `volatile` — without it, the compiler may cache or reorder accesses, breaking
the protocol the hardware expects.

In Linux user-space you cannot dereference physical addresses directly — you have to
either (a) write a kernel driver and `mmap` `/dev/something`, or (b) use `/dev/mem` with
root and a known physical address. On the M4 (no MMU), all addresses are physical;
dereferencing is direct.

**In this project.** Direct MMIO is M4 territory. The macros at the top of
[3rdparty/nxp/bsp_nlm_vspa/LA9310_cal/Sources/_main.c:163-164](/home/cb24/workspace/nr_ue_phy/3rdparty/nxp/bsp_nlm_vspa/LA9310_cal/Sources/_main.c#L163-L164)
are textbook MMIO writes:
```c
#define VCPU_SET_CONTROL(x)  __ipwr(0x8 >> 2, x, x);
#define VCPU_SET_VERSION(x)  __ipwr(0x4 >> 2, x, 0xFFFFFFFF);
```
The host A35 sees the LA9310 through driver-managed memory regions; PHY code does not
touch raw registers — it goes through `dfelib`/`dfec_qsend`/mailbox APIs.

**Minimal example (RPi GPIO via /dev/gpiomem — the only safe MMIO target on RPi).**
```c
#include <fcntl.h>
#include <sys/mman.h>
#include <stdint.h>
#include <unistd.h>

int main(void) {
    int fd = open("/dev/gpiomem", O_RDWR | O_SYNC);
    volatile uint32_t *gpio = mmap(NULL, 0x1000, PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0);

    /* set GPIO 21 as output: GPFSEL2 bits 5:3 = 001 */
    gpio[2] = (gpio[2] & ~(7u << 3)) | (1u << 3);

    /* toggle it via GPSET0 / GPCLR0 */
    gpio[7]  = (1u << 21);     /* set high  */
    sleep(1);
    gpio[10] = (1u << 21);     /* set low   */

    munmap((void *)gpio, 0x1000);
    close(fd);
}
```
Run as root or in the `gpio` group. **Do not** poke `/dev/mem` blindly — you can crash
the system.

---

## L7. DMA — direct memory access

**Layman.** DMA is a peripheral that copies bytes between memory regions (or between a
device and memory) without involving the CPU. The CPU sets up a "descriptor" (source,
destination, length, options), kicks the DMA engine, and gets an interrupt when done.
The PHY uses DMA to move I/Q samples from the ADC FIFO into shared DRAM at line rate —
the CPU could not keep up with sample-by-sample copies.

**In this project.** Mostly hidden inside the NXP BSP drivers. The PHY interacts with
the *result* — a "buffer at this physical address now contains slot N's samples." On
the host side these buffers are described by `g_BufferPoolsInfo` entries (see
[toplevel/phy/phy_skeleton.c:35](/home/cb24/workspace/nr_ue_phy/toplevel/phy/phy_skeleton.c#L35))
which are pre-allocated, DMA-friendly memory pools.

**Key constraints DMA imposes that the codebase respects:**
- **Alignment** — DMA engines often require 16/64/128-byte alignment of source/dest. See
  `SKL_POOL_ALIGNMENT_HW_ACCEL`.
- **Cache coherency** — on cores without I/O coherent DMA, the CPU must invalidate or
  flush its cache around DMA operations. The BSP drivers handle this.
- **Physical contiguity** — virtual memory's `malloc` returns scattered physical pages;
  DMA wants one contiguous physical region. Hence the dedicated buffer pools.

**In tree.**
- Buffer pool definitions for DL antenna data, sized to slot/symbol budget:
  [toplevel/phy/phy_skeleton.c:44-83](/home/cb24/workspace/nr_ue_phy/toplevel/phy/phy_skeleton.c#L44-L83)

---

## L8. Mailboxes — IPC between cores

**Layman.** A mailbox is a pair of registers + an interrupt: one core writes a 32- or
64-bit value into the register, which sets a "new message" bit, which raises an IRQ on
the other core. The receiver reads the value, clears the IRQ. Bandwidth is tiny
(8 bytes per ring); use it for **events**, not bulk data. Bulk data goes through shared
memory; the mailbox just says "look at offset X."

**In this project.** Two mailbox interfaces matter:
- **A35 ↔ M4** — `la9310_mbox_v2h` (VSPA→host) and `la9310_mbox_h2v` (host→VSPA),
  brokered through M4. The function `vLa9310MbxRead` reads a pending VSPA message.
- **M4 ↔ VSPA** — within the LA9310, also via mailbox registers.

Each mailbox message is 64 bits split into `msb32` (the message type) and `lsb32`
(usually a pointer/offset into shared memory).

**In tree.**
- M4 reads mailbox messages from VSPA in a loop:
  [toplevel/dfec/trd_vspaMsgHndlr.c:63-69](/home/cb24/workspace/nr_ue_phy/toplevel/dfec/trd_vspaMsgHndlr.c#L63-L69)
- The dispatch on `msb32`:
  [toplevel/dfec/trd_vspaMsgHndlr.c:69-120](/home/cb24/workspace/nr_ue_phy/toplevel/dfec/trd_vspaMsgHndlr.c#L69-L120)

---

## L9. Shared memory between A35 and M4

**Layman.** A region of physical DRAM is mapped into the address spaces of both cores at
startup. Either side can write to it; the mailboxes carry "pointers" (offsets into this
region). For correctness you need:
- An agreed memory layout (struct definitions matched between sides)
- Cache management or uncached mappings — otherwise writes from core A may sit in A's
  L1 cache while B reads stale DRAM
- Atomic flags / version counters so the reader knows the data is finished

**In this project.** `g_shmAddrs` is the M4-side handle to the shared region. Pointers
returned in mailbox messages (`mbox_v2h.lsb32`) are offsets into it; the M4 dereferences
them as e.g. `(Dfe_BasebandDataIndication_t *)mbox_v2h.lsb32`. The host PHY receives
the same pointer (translated to the host's view of the region) wrapped in a
`PhyIfUe_*Indication`.

**In tree.**
- Reception handler unpacking shared-memory pointers from a mailbox:
  [toplevel/dfec/trd_vspaMsgHndlr.c:96-105](/home/cb24/workspace/nr_ue_phy/toplevel/dfec/trd_vspaMsgHndlr.c#L96-L105)
- The shared address mapping on the M4 side — search `g_shmAddrs`:
  ```bash
  grep -rn "g_shmAddrs" toplevel/dfec/ 3rdparty/nxp/ | head -10
  ```

---

## L10. The DFE/RF integration in nr_ue_phy

**Layman.** "DFE" stands for Digital Front End — the chain that turns analog RF into
digital baseband (and vice versa). In this project, "DFE" is shorthand for "everything on
the LA9310 / M4 / VSPA side." Two halves:
- **Host side** (`toplevel/phy/dfe_if/`) — Linux user-space code that owns the
  conversation with the LA9310 from above
- **Device side** (`toplevel/dfec/`, `src/dfelib/`) — runs on the M4

`src/dfelib/` is a small abstraction library (queues, debug helpers, and
host-callable functions to format requests for M4 consumption). `dbg_arma.c`,
`func_cmn.c`, `queue_cmn.c` are shared types/utilities used on both sides.

**In this project.** The compile flag `RF_ACTIVE` switches between:
- **RF active** — real LA9310 hardware in the loop
- **RF simulator** (default x86 build) — a software stub stands in for the LA9310,
  letting you run the entire PHY without hardware

Look for `#ifdef RF_ACTIVE` in PHY thread code (e.g. PDCCH dump code at
[toplevel/phy/trd_pdcch.c:82-84](/home/cb24/workspace/nr_ue_phy/toplevel/phy/trd_pdcch.c#L82-L84)).

**In tree.**
- Host-side DFE interface (timestamping, slot delivery):
  [toplevel/phy/dfe_if/9310/dfe_if_rx.c:218](/home/cb24/workspace/nr_ue_phy/toplevel/phy/dfe_if/9310/dfe_if_rx.c#L218)
- Device-side dfelib core:
  [src/dfelib/dfelib.c](/home/cb24/workspace/nr_ue_phy/src/dfelib/dfelib.c)
- The CMake split between RF active and simulator:
  [CMakeLists.txt:74-98](/home/cb24/workspace/nr_ue_phy/CMakeLists.txt#L74-L98)

---

## L11. The 1-PPS clock and frequency calibration

**Layman.** A 1-PPS (one pulse per second) input is a precision timing reference, often
from GPS. It's a square wave that goes high once a second on the absolute UTC second
boundary. Disciplining a local oscillator (VCXO) against PPS is how you keep your radio's
clock accurate enough for cellular (parts-per-billion).

**In this project.** The M4 owns the PPS handler (`vPhyTimerPPSINHandler`) and the VCXO
control loop. Once a second:
1. PPS interrupt fires
2. M4 reads the local timer at that exact moment
3. M4 computes the drift and updates the VCXO via DAC writes
4. Once converged, `ueState` transitions from `WAIT_VCXO_SYNC` to `RUNNING`

You'll see this state machine in `slotPeriodicScan`. The host A35 only sees "RUNNING" or
"not RUNNING" — it doesn't know about VCXO internals.

**In tree.**
- The state transition once VCXO converges:
  [toplevel/dfec/trd_slotInd.c:80-100](/home/cb24/workspace/nr_ue_phy/toplevel/dfec/trd_slotInd.c#L80-L100)
- The freq-control module called at PPS:
  [toplevel/dfec/freq_ctrl.c](/home/cb24/workspace/nr_ue_phy/toplevel/dfec/freq_ctrl.c)
  (read `freqCtrl_getCFO`, `freqCtrl_getVcxo`, `vFreqCalibration` in particular)

---

# Suggested order of attack (only if you draw an RF ticket)

1. **L1 + L2** (the system overview + LA9310) — read once, refer back as needed.
2. **L4 + L5** (Cortex-M4 + the four FreeRTOS APIs) — enough to read `toplevel/dfec/`.
3. **L8 + L9** (mailboxes + shared memory) — the bridge between sides; trace one
   end-to-end slot indication.
4. **L10** (DFE integration) — when you actually need to add or modify a DFE feature.
5. **L3** (VSPA) — only when you need to change DSP firmware. Different toolchain,
   different mental model.
6. **L6 + L7** (MMIO + DMA) — usually you live above this layer; learn it when something
   breaks below the BSP.
7. **L11** (PPS / VCXO) — only for sync/cal tickets.

If you never touch RF in your career here, you can stop after L1+L2+L8.
