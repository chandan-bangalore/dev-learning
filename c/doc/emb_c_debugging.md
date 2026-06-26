# Embedded Linux K — Logging & Debugging Study Notes

How nr_ue_phy emits, captures, and post-processes diagnostic information, and the
debugging tools you reach for when something goes wrong.

For each topic:
1. **Layman** — what it actually is, in plain English
2. **In this project** — how nr_ue_phy uses it
3. **Minimal example** — a tiny self-contained snippet you can compile on your RPi
4. **In tree** — concrete `file:line` pointer into nr_ue_phy

---

## Table of contents

- [K1. The LOG\_TRACE / logger.h family](#k1-the-log_trace--loggerh-family)
- [K2. Per-component log IDs and filters](#k2-per-component-log-ids-and-filters)
- [K3. Offline log decoding (toplevel/log\_decoder)](#k3-offline-log-decoding-topleveldlog_decoder)
- [K4. AddressSanitizer (USE\_ASAN)](#k4-addresssanitizer-use_asan)
- [K5. gdb on cross-compiled binaries (gdbserver)](#k5-gdb-on-cross-compiled-binaries-gdbserver)
- [K6. perf for hotspot analysis](#k6-perf-for-hotspot-analysis)
- [K7. strace for syscall debugging](#k7-strace-for-syscall-debugging)
- [K8. Wireshark integration](#k8-wireshark-integration)
- [K9. KPI counters as in-band telemetry](#k9-kpi-counters-as-in-band-telemetry)

---

## K1. The LOG_TRACE / logger.h family

**Layman.** Real-time code can't `printf` — printf takes a process-wide lock, may flush to
disk, and can stall a thread for milliseconds. The standard pattern in PHY/embedded code
is a **deferred logger**: the producer thread writes a small, fixed-size record into a
ring buffer and returns immediately. A separate, low-priority thread (or out-of-process
tool) drains that buffer and formats messages into human-readable text.

**In this project.** `lib/logger/` provides macros that all PHY code uses instead of
`printf`. There are levels, all with the same arity (a format string + three uintptr_t
arguments — fixed shape so the record size is known):

| Macro | Meaning |
|---|---|
| `LOG_ENTER()` / `LOG_EXIT()` | Function trace (compile-time gated by `ENTER_ENABLED` / `EXIT_ENABLED`) |
| `LOG_TRACE(fmt, a, b, c)` | Generic informational |
| `LOG_BRANCH(fmt)` | "We took this code path" |
| `LOG_SEND_MSG` / `LOG_RCVD_MSG` | ICM message send/receive |
| `LOG_EXCEPTION` | Unexpected but recoverable |
| `LOG_ERROR` | Fatal, will likely abort |
| `LOG_EXCEPTION_CNT(N, ...)` | Suppresses repeated logs to avoid flooding |

Logging is enabled via the `_ENABLE_LOGGING` compile flag (set in the top-level
CMakeLists). When disabled the macros expand to nothing — true zero overhead.

**Important quirk.** All `LOG_TRACE` arguments must be three `uintptr_t`s. If you have
fewer, pass `0`. If you want to log a string, cast: `(uintptr_t)"my string"`. The format
string `%s` will then dereference it. This is not standard printf; it's the project's
discipline.

**Minimal example (a deferred logger sketch).**
```c
#include <stdint.h>
#include <stdio.h>

typedef struct { const char *fmt; uintptr_t a, b, c; } log_rec_t;

static log_rec_t ring[1024];
static volatile uint32_t head;

static inline void mlog(const char *fmt, uintptr_t a, uintptr_t b, uintptr_t c) {
    uint32_t i = __atomic_fetch_add(&head, 1, __ATOMIC_RELAXED) & 1023;
    ring[i] = (log_rec_t){ fmt, a, b, c };       /* fast path */
}

/* run in a low-priority thread */
void drain(void) {
    static uint32_t tail;
    while (tail != head) {
        log_rec_t *r = &ring[tail++ & 1023];
        printf(r->fmt, r->a, r->b, r->c);
    }
}
```

**In tree.**
- The macro definitions and their compile-time gates:
  [lib/logger/logger.h:114-120](/home/cb24/workspace/nr_ue_phy/lib/logger/logger.h#L114-L120)
- Real usage in a thread:
  [toplevel/phy/trd_pdcch.c:131](/home/cb24/workspace/nr_ue_phy/toplevel/phy/trd_pdcch.c#L131) (LOG_ERROR),
  [toplevel/phy/trd_pdcch.c:139](/home/cb24/workspace/nr_ue_phy/toplevel/phy/trd_pdcch.c#L139) (LOG_EXCEPTION).

---

## K2. Per-component log IDs and filters

**Layman.** Every "component" (PDCCH, PDSCH, sync, etc.) registers a logger ID at startup
and tags every log message with that ID. A runtime filter table decides which ID/level
combinations are actually emitted. This way you can crank up sync's log level without
drowning in PDSCH chatter.

**In this project.** `LOGGER_REGISTER("TRD_DL_PDCCH")` returns a numeric ID stored in a
component-local `LOG_ID()` macro. The dispatch macro `LOGGER_WRITE_LOG` consults
`g_LoggerFilters[type][id]` and short-circuits if disabled. Filter levels are loaded from
the runtime config (see `lib/logger/logger.c` and the `[Logger]` section of the
configuration ini).

**In tree.**
- A thread registering itself:
  [toplevel/phy/trd_pdcch.c:123](/home/cb24/workspace/nr_ue_phy/toplevel/phy/trd_pdcch.c#L123)
- The compile-time `MAX_LOGGER_ID_NUMBER` (only 19 component slots — by design):
  [lib/logger/logger.h:19](/home/cb24/workspace/nr_ue_phy/lib/logger/logger.h#L19)
- The runtime filter table that LOGGER_WRITE_LOG indexes:
  ```bash
  grep -n "g_LoggerFilters" lib/logger/logger.c
  ```

---

## K3. Offline log decoding (toplevel/log_decoder)

**Layman.** The on-device logger writes a **binary** stream — record per line, just IDs
and three integers. Human-readable formatting happens **after the fact** on a developer
host, by feeding the binary file plus the ELF (which contains the format strings as
debug info) plus a metadata XML to a separate program. Net win: the on-device cost of one
log call is "memcpy 32 bytes."

**In this project.** `toplevel/log_decoder/` is a standalone binary that takes:
- the binary log file
- the ELF that produced it (so it can read the format strings)
- `uephy_rtdd.xml` — runtime data dictionary (component IDs → names, enum names, etc.)

and prints decoded text. This is also why every PHY developer keeps the matching ELF
around — without it the binary log is unreadable.

**Minimal example.** Write the same record format both into a binary file and read it back
formatting:
```c
/* writer */
fwrite(&rec, sizeof rec, 1, fp);

/* reader */
log_rec_t rec;
while (fread(&rec, sizeof rec, 1, fp) == 1)
    printf(rec.fmt, rec.a, rec.b, rec.c);  /* needs fmt resolved from a separate symbol table */
```
Real decoders look up `fmt` by an integer ID rather than a pointer, because pointers
aren't valid across processes.

**In tree.**
- The decoder binary's `main`:
  [toplevel/log_decoder/main.c:15](/home/cb24/workspace/nr_ue_phy/toplevel/log_decoder/main.c#L15)
- The `readLog` core:
  [toplevel/log_decoder/log_decoder.c](/home/cb24/workspace/nr_ue_phy/toplevel/log_decoder/log_decoder.c)
- The runtime data dictionary that the decoder consumes:
  [toplevel/log_decoder/uephy_rtdd.xml](/home/cb24/workspace/nr_ue_phy/toplevel/log_decoder/uephy_rtdd.xml)

---

## K4. AddressSanitizer (USE_ASAN)

**Layman.** ASan is a compile-time tool that instruments every memory access. At runtime,
heap allocations are wrapped with red-zones and a shadow memory map; if you read or write
out of bounds, ASan immediately aborts and prints the bad address, the stack trace of the
access, and the stack of the original allocation. Catches: heap overflows, use-after-free,
double-free, leaks, stack overflows. Cost: ~2× slower, ~3× more memory. Use in dev/CI,
not in production.

**In this project.** Enable with `-DUSE_ASAN=On`, only valid with `-DCMAKE_BUILD_TYPE=Debug`
(the top-level CMake will refuse otherwise). Adds `-fsanitize=address
-fstack-protector-all -fno-omit-frame-pointer` to all C/CXX flags. Does **not** work on
the M4/VSPA firmware — only on the Linux x86/ARM userspace builds.

**Minimal example.**
```c
#include <stdlib.h>
int main(void) {
    int *p = malloc(4 * sizeof(int));
    p[5] = 42;        /* heap-buffer-overflow — ASan catches this */
    free(p);
}
```
Compile and run on RPi:
```bash
gcc -fsanitize=address -g -O1 oob.c -o oob
./oob              # ASan prints a beautiful diagnostic and exits 1
```

**In tree.**
- The build option and where it inserts the flags:
  [CMakeLists.txt:43](/home/cb24/workspace/nr_ue_phy/CMakeLists.txt#L43) (option),
  [CMakeLists.txt:51-53](/home/cb24/workspace/nr_ue_phy/CMakeLists.txt#L51-L53) (flags),
  [CMakeLists.txt:213-215](/home/cb24/workspace/nr_ue_phy/CMakeLists.txt#L213-L215) (release-mode guard).

---

## K5. gdb on cross-compiled binaries (gdbserver)

**Layman.** When the binary runs on a different architecture (ARM target) than your dev
machine (x86), you can't just `gdb ./uephy`. The pattern is:
- On the **target**, run `gdbserver :2345 ./uephy <args>` — it stops the program and
  listens for a debugger connection.
- On the **host**, run a cross-debugger (`aarch64-linux-gnu-gdb`) pointed at the **same
  ELF** you flashed. From within gdb: `target remote <target-ip>:2345`.
- Set breakpoints, step, inspect — all over the network.

This works because gdb only needs symbols, not architecture: the ELF on the host has all
the debug info, gdbserver on the target reports register and memory state.

**In this project.** Standard pattern; no project-specific tooling. The ARM toolchain
(`aarch64-linux-gnu-gdb`) ships with the Linaro/Yocto SDK that builds the project. On
StarTag the binary is at `/opt/espace/uephy/`; just `cd` there and:
```bash
# on target
gdbserver :2345 ./uephy --config=...

# on host
aarch64-linux-gnu-gdb /path/to/local/uephy
(gdb) set sysroot /path/to/sysroot
(gdb) target remote 192.168.1.50:2345
(gdb) b TrdDlPdcch_initHandler
(gdb) c
```

**Try on RPi.** RPi is ARM but native, so even simpler:
```bash
sudo apt install gdb gdbserver
gdbserver :2345 ./my_program &
gdb ./my_program
(gdb) target remote :2345
```

**Tip.** Add `-g3` to release builds (the project already does — see
[CMakeLists.txt:63](/home/cb24/workspace/nr_ue_phy/CMakeLists.txt#L63) and
[CMakeLists.txt:99](/home/cb24/workspace/nr_ue_phy/CMakeLists.txt#L99)) so symbols are
present for postmortem debugging without taking the perf hit of `-O0`.

---

## K6. perf for hotspot analysis

**Layman.** `perf` is the Linux kernel's built-in profiler. It samples the running CPU
~thousands of times per second and records the instruction pointer + call stack. After
the run, `perf report` shows you which functions consumed CPU. For a real-time PHY, the
question is rarely "what's the average load" — it's "what jumped from 8 µs to 18 µs in
slot 4321." `perf sched` and `perf trace` answer that.

**In this project.** Not embedded into the codebase. Standard external tool. Three
recipes:

```bash
# 1. CPU hotspots in PDCCH
sudo perf record -F 999 -p $(pidof uephy) -g -- sleep 30
sudo perf report --stdio | head -50

# 2. Who preempts who (looking for jitter sources)
sudo perf sched record -- sleep 5
sudo perf sched latency

# 3. System call costs
sudo perf trace -p $(pidof uephy)
```

**Minimal example on RPi.**
```bash
sudo apt install linux-perf
perf stat -- ./oob       # cycles, instructions, cache misses, branch misses, in 5 lines
perf record -g ./your_program
perf report
```

**In tree.** None — pure external tooling. Pair it with `-g3 -fno-omit-frame-pointer` (the
project's release flags already do this, see
[CMakeLists.txt:63](/home/cb24/workspace/nr_ue_phy/CMakeLists.txt#L63)) so call stacks
resolve cleanly.

---

## K7. strace for syscall debugging

**Layman.** `strace` traces every system call a process makes, with arguments and return
values. Indispensable when something fails and you don't know why — strace reveals which
file open got `ENOENT`, which connect got `ECONNREFUSED`, which `ioctl` returned `EINVAL`.
Cost: orders of magnitude slowdown (every syscall is intercepted). Don't run a production
PHY under strace; do it on startup, simulator runs, or to chase a specific failure.

**In this project.** Most useful for:
- "uephy fails to start" — `strace -f ./uephy 2>&1 | grep -E 'open|bind|connect'`
- "macemu can't connect to uephy" — strace on either side, look at the socket calls
- DFE driver `ioctl` calls returning unexpectedly

```bash
strace -f -e trace=network -p $(pidof uephy)        # live, network syscalls only
strace -f -o trace.log ./uephy --config=...         # log everything to a file
```

**Try on RPi.**
```bash
strace ls -l /tmp 2>&1 | head -30      # see how ls discovers files
strace -e openat ls /tmp 2>&1 | tail   # only openat() calls
```

---

## K8. Wireshark integration

**Layman.** Wireshark normally captures network packets via `tcpdump`/`libpcap`. The
project repurposes the same wire format to capture **protocol-level events** that aren't
on the wire — DCI indications, slot transitions, internal control messages — by writing
them as fake packets. You then open the resulting `.pcap` in Wireshark with the project's
custom dissector and step through events with timestamps.

**In this project.** Every PHY → PAL message is also written as a wireshark record
through `Logger_sendPhyIfUeToWireshark`. The wrapper for this is in
`lib/logger/logger_wireshark.h`. The result is a `.pcap`-style stream that you can replay
later. This is how the team reasons about message ordering between PDCCH, PDSCH, MAC,
etc., without staring at log text.

**In tree.**
- Real call site — PDCCH sends DCI to PAL **and** to wireshark log:
  [toplevel/phy/trd_pdcch.c:105-110](/home/cb24/workspace/nr_ue_phy/toplevel/phy/trd_pdcch.c#L105-L110)
- The wireshark logging API:
  [lib/logger/logger_wireshark.h](/home/cb24/workspace/nr_ue_phy/lib/logger/logger_wireshark.h)

---

## K9. KPI counters as in-band telemetry

**Layman.** A KPI (Key Performance Indicator) is a counter of "this bad thing happened N
times." Cheap (`atomic++`), always-on, sampled periodically by an external monitor. KPIs
are how you discover problems at runtime without enabling expensive logs. In a healthy
system, queue-full and drop counters stay at 0; the moment one ticks, you know something
got behind.

**In this project.** `kpi.h` defines a fleet of `KPI_*()` macros — `KPI_PDCCH_CONFIG_QUEUE_FULL`,
`KPI_DROP_*`, etc. They're a dispatch flag in the path: when something bad happens you
don't crash and you don't necessarily log; you just bump the counter and continue. The L1C
thread periodically gathers these and reports them upstream (via the `INTERCOMP_MSG_ID_L1C_SEND_KPI_TIMER_EXPIRY`
event in [phy_icm_msg_ids.h:69](/home/cb24/workspace/nr_ue_phy/toplevel/phy/phy_icm_msg_ids.h#L69)).

**Minimal example.**
```c
#include <stdatomic.h>

static _Atomic uint64_t kpi_drop = 0;

static inline void on_drop(void) {
    atomic_fetch_add_explicit(&kpi_drop, 1, memory_order_relaxed);
}
```

**In tree.**
- The KPI used at the PDCCH drop site:
  [toplevel/phy/trd_pdcch.c:186](/home/cb24/workspace/nr_ue_phy/toplevel/phy/trd_pdcch.c#L186)
- Header that defines all KPI macros:
  ```bash
  grep -n "KPI_" toplevel/phy/kpi.h | head -40
  ```

---

# Suggested order of attack

1. **K1 + K2** (LOG_TRACE family + per-component IDs) — read the project's existing
   logs in real time first; you'll need this to debug anything else.
2. **K3** (offline decoder) — needed the moment you have a bug from someone else's run.
3. **K4** (ASan) — turn it on for any new feature work, catch UB before review.
4. **K5** (gdbserver) — when you finally need to attach to a running PHY.
5. **K6 + K7** (perf, strace) — once you're past "is it crashing" and into
   "is it fast enough."
6. **K8** (Wireshark) — when you need to reason about message ordering.
7. **K9** (KPIs) — keep a mental list of which counters mean which problem.
