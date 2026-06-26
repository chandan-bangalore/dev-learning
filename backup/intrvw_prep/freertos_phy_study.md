# FreeRTOS + VSPA PHY Study Guide

A defence-grounded walkthrough of the FreeRTOS / VSPA firmware in this repo,
written so each phrase of the CV bullet can be backed with file:line evidence.

---

## ⚠️ Important corrections to the CV bullet before the interview

The CV bullet says **"FreeRTOS-based firmware on NXP VSPA DSP (LA9310)"**.
Three of those framings do not match what this repo actually builds:

1. **The host running FreeRTOS is not a Cortex-M4** — it is the **NXP Power Architecture
   e200z7 (VLE)** core. See the toolchain in
   [scripts/make_scripts/config_e200.mk:19-22](scripts/make_scripts/config_e200.mk#L19-L22)
   (`CROSS_PREFIX = powerpc-eabivle-`) and
   [scripts/make_scripts/config_e200.mk:103](scripts/make_scripts/config_e200.mk#L103)
   (`-mcpu=e200z7`). LA9310's host *is* a Cortex-M4, but this repo does not target LA9310.
2. **The chip is not LA9310** — it is the NXP **"Geul" baseband family: LA1224 / LA9358 /
   LA1238CPE** (multi-core e200 + multiple VSPA-3 DSPs). See
   [scripts/make_scripts/config_e200.mk:33-38](scripts/make_scripts/config_e200.mk#L33-L38)
   and the linker scripts
   [lib/module/e200main/la1224_e200.ld](lib/module/e200main/la1224_e200.ld) and
   [lib/module/e200main/la9358_e200_core0.ld](lib/module/e200main/la9358_e200_core0.ld).
3. **FreeRTOS does not run on the VSPA** — VSPA-3 is bare-metal, event-driven, with
   its own assembler kernels. FreeRTOS runs on the e200 cores, which orchestrate
   the VSPA. The VSPA toolchain (`arch vspa3`, `au_count 16`, `core_type sp`) is in
   [scripts/make_scripts/config_vspa.mk:109-110](scripts/make_scripts/config_vspa.mk#L109-L110).

> **Recommended CV rewrite to align with the code you can defend**:
> *"Developed and maintained FreeRTOS-based firmware on NXP Geul (LA1224/LA9358)
> e200z7 cores orchestrating VSPA-3 DSPs, implementing real-time task scheduling,
> interrupt handling, and inter-core/IPC for gNB PHY pipeline execution."*

The rest of this document uses the actual architecture.

---

## 1. Platform context

### 1.1 SoC: NXP "Geul" (LA1224 / LA9358 / LA1238CPE)

NXP Layerscape Access baseband. From the build configuration:

- Host cores: **multiple Power Architecture e200z7 cores** running FreeRTOS
  (`-mcpu=e200z7 -mhard-float`,
  [scripts/make_scripts/config_e200.mk:103](scripts/make_scripts/config_e200.mk#L103)).
  Up to 8 VSPA cores are referenced
  ([applications/l1c/phyif/phyif_comp.c:378](applications/l1c/phyif/phyif_comp.c#L378),
  `NUM_VSPA_CORES`).
- Logical e200 split (the deployment expects at least three e200 cores per Geul):
  | Constant | Value | Role | Source |
  |---|---|---|---|
  | `GEUL_E200_MASTER_CORE` | 0 | Master / boot / heap init / LX-ARM IPC router | [lib/module/appinit/app_deployment.h:31](lib/module/appinit/app_deployment.h#L31) |
  | `GEUL_LX_IPC_E200_CORE` | 0 (alias) | Talks to LX2160 ARM via bbdev IPC | [lib/module/appinit/app_deployment.h:35](lib/module/appinit/app_deployment.h#L35) |
  | `GEUL_VSPA_IPC_E200_CORE` | 1 | Owns the VSPA messaging task / DMA IRQs | [lib/module/appinit/app_deployment.h:41](lib/module/appinit/app_deployment.h#L41) |
  | `GEUL_E200_FECA_CORE` | 1 (alias) | Owns the FECA (FEC accelerator) ISRs | [lib/module/appinit/app_deployment.h:46](lib/module/appinit/app_deployment.h#L46) |
- The slave e200s also run FreeRTOS — see the master/slave path in
  [lib/module/e200main/e200main.c:687-725](lib/module/e200main/e200main.c#L687-L725).

**Hardware accelerators referenced in the e200 code:**
- **FECA** (FEC Accelerator) — encode / channel decode / shared decode chains
  ([lib/module/feca/feca.c:337-532](lib/module/feca/feca.c#L337-L532)). Owns IRQs
  90 (SD/DCD out), 91 (CCD out), 92 (DCE out), 93 (CCE out).
- **TBGEN** — radio time base generator; produces the slot-tick IRQ
  ([applications/l1c/tbgen/driver/slotIndTbgen.c:161-296](applications/l1c/tbgen/driver/slotIndTbgen.c#L161-L296)).
- **QDMA / FlexSPI** — boot from PCIe (PEBM) or XSPI flash
  ([lib/module/e200main/e200main.c:315-334](lib/module/e200main/e200main.c#L315-L334)).
- **bbdev IPC** — DPDK-style queue from e200#0 ↔ LX2160 ARM host
  ([lib/module/mh/mh_link_bbdev.c:434-477](lib/module/mh/mh_link_bbdev.c#L434-L477)).

> **Follow-up: ask the original team** for the TRM / chip name actually printed
> on the silicon. The codepaths support LA1224 + LA9358 + LA1238CPE; which one
> ships in production may matter at interview.

### 1.2 VSPA-3 DSP

From [scripts/make_scripts/config_vspa.mk:108-110](scripts/make_scripts/config_vspa.mk#L108-L110):

```makefile
# VSPA architecture dependent flags
CFLAGS += -arch vspa3 -au_count 16 -core_type sp -ansi off -mvcpu -msgstyle gcc -env "$(VSPA3_ENVIRONMENT)"
LFLAGS += -arch vspa3 -au_count 16 -core_type sp -ansi off -mvcpu -msgstyle gcc -env "$(VSPA3_ENVIRONMENT)"
```

- **VSPA-3** core, **16 AU** (Arithmetic Units → 16-wide SIMD), single-precision
  (`-core_type sp`).
- Two pipelines per core: **VCPU** (scalar / control) and **IPPU** (input/output
  processor that overlaps DMA with compute).
- Memory map (from the e200's view of VSPA DMEM):
  - VCPU DMEM grows down from `IPPU_DMEM_BASE - PARAM_STRUCT_SIZE_VCPU_DMEM (0x400)`
  - IPPU DMEM grows down from `VSPA_DMEM_SIZE`
  - See [lib/module/osal/osal_e200.c:163-173](lib/module/osal/osal_e200.c#L163-L173).
- VSPA has its own DMA + 64 host-event flags + cycle counter
  ([lib/module/mh/mh_link_vspa.c:573-642](lib/module/mh/mh_link_vspa.c#L573-L642)).

### 1.3 Toolchain & build

| Aspect | e200 (FreeRTOS host) | VSPA-3 (bare-metal DSP) |
|---|---|---|
| Cross-compiler | `powerpc-eabivle-gcc 4.9.4` ([config_e200.mk:19-22](scripts/make_scripts/config_e200.mk#L19-L22)) | NXP CodeWarrior VSPA (`$VSPA3_ENVIRONMENT/bin`) ([config_vspa.mk:14](scripts/make_scripts/config_vspa.mk#L14)) |
| ISA | Power ISA VLE (`-mcpu=e200z7`) | VSPA-3, 16 AU, SP |
| FreeRTOS port | `FreeRTOS/Source/portable/GCC/PowerPC_MPIC` ([config_e200.mk:45](scripts/make_scripts/config_e200.mk#L45)) | n/a — VSPA does not run an RTOS |
| Heap | `heap_4.c` ([config_e200.mk:76](scripts/make_scripts/config_e200.mk#L76)) | DMEM bumping allocator in `osal_allocMemVspaDbg` |
| Linker script | [lib/module/e200main/la1224_e200.ld](lib/module/e200main/la1224_e200.ld) | per-VSPA `.lcf` in [lib/vspalib/lcf/](lib/vspalib/lcf/) |
| Per-core stack | `__STACK_SIZE = 2000` ([la1224_e200.ld:18](lib/module/e200main/la1224_e200.ld#L18)) | n/a |

The FreeRTOS source itself, FreeRTOSConfig.h, and the e200 port live in the
`external/EXT` or `external/e200_bsp2.2` git submodule
([.gitmodules](.gitmodules)) which is **not initialised in this checkout** —
all the FreeRTOS configuration values must be read out of that submodule. See
section 2 below for what the calling code asserts about them.

> **Follow-up: ask the original team** to `git submodule update --init` so
> `FreeRTOSConfig.h` becomes visible. Several config values are quoted in
> comments and code; the authoritative file is `external/e200_bsp2.2/<…>/FreeRTOSConfig.h`.

---

## 2. FreeRTOS in this codebase

Because the FreeRTOS kernel and `FreeRTOSConfig.h` live in an uninitialised
submodule, the values below come from how the application code uses them.
Where the value is provable from this repo, I quote it; where it isn't, I flag
it as a follow-up.

| Symbol | Evidence in this repo | Notes |
|---|---|---|
| FreeRTOS port | `PowerPC_MPIC` ([config_e200.mk:45](scripts/make_scripts/config_e200.mk#L45)) | MPIC = Multi-core Programmable Interrupt Controller |
| Heap impl | `heap_4.c` ([config_e200.mk:76](scripts/make_scripts/config_e200.mk#L76)) | `heap_4` supports allocation + free with coalescing — needed because `pvPortMalloc` / `vPortFree` are used at runtime |
| `configAPPLICATION_ALLOCATED_HEAP` | `==1` ([e200main.c:133](lib/module/e200main/e200main.c#L133)) | The app supplies the heap buffer rather than letting FreeRTOS declare it. |
| `configSHARED_HEAP` | `==1` build option exists ([e200main.c:134-141](lib/module/e200main/e200main.c#L134-L141)) | When set, `ucHeap[configTOTAL_HEAP_SIZE]` lives in `.heap_frtos`; otherwise it's placed in DMEM at `__dmem_heap_start` |
| `configTOTAL_HEAP_SIZE` | declared via `static uint8_t ucHeap[configTOTAL_HEAP_SIZE]` ([e200main.c:137](lib/module/e200main/e200main.c#L137)) | Numeric value lives in `FreeRTOSConfig.h` — follow-up |
| `configMAX_PRIORITIES` | 5 (per comment) ([osal_e200.c:197](lib/module/osal/osal_e200.c#L197)) | Application uses 0…6 indirectly: `OSAL_THREAD_PRIORITY_0..6` ([osal.h:127-133](lib/module/osal/osal.h#L127-L133)). Note the mismatch — see §3. |
| `configMINIMAL_STACK_SIZE` | used as a floor ([osal_e200.c:212](lib/module/osal/osal_e200.c#L212), [mh_link_vspa.c:417](lib/module/mh/mh_link_vspa.c#L417) hard-codes `2048`) | Numeric value lives in FreeRTOSConfig.h — follow-up |
| `configUSE_PREEMPTION` | the kernel is preemptive — `portYIELD_FROM_ISR` is used at [tm.c:274](lib/module/tm/tm.c#L274), [mh_link_bbdev.c:427](lib/module/mh/mh_link_bbdev.c#L427), [mh_link_vspa.c:649](lib/module/mh/mh_link_vspa.c#L649) | If cooperative, `portYIELD_FROM_ISR` would be a no-op and these would not be needed |
| `configCHECK_FOR_STACK_OVERFLOW` | enabled — `vApplicationStackOverflowHook` is implemented at [e200main.c:412-425](lib/module/e200main/e200main.c#L412-L425) | The hook fires only if 1 or 2 is set in the config |
| `configUSE_MALLOC_FAILED_HOOK` | enabled — `vApplicationMallocFailedHook` at [e200main.c:405-410](lib/module/e200main/e200main.c#L405-L410) | |
| `configUSE_IDLE_HOOK` | enabled — `vApplicationIdleHook` at [e200main.c:186-191](lib/module/e200main/e200main.c#L186-L191) increments an idle-cycle counter exposed to HIF | |
| `configTICK_RATE_HZ` | **not derivable** — `vTaskDelay(15000)` and `vTaskDelay(1000)` at [e200main.c:477,486](lib/module/e200main/e200main.c#L477) suggest milliseconds (so 1000 Hz) but this is only inferential | **Follow-up: ask the team** |
| `configSUPPORT_STATIC_ALLOCATION` | **no evidence in this repo** — every task is `xTaskCreate` (dynamic), no `xTaskCreateStatic` calls | |
| Tickless idle | **not used** — `vApplicationIdleHook` does work every tick, and no `portSUPPRESS_TICKS_AND_SLEEP` references exist | The chip is wall-powered (a small-cell baseband), so this is the expected choice. |
| Event groups / co-routines | `event_groups.c` and `croutine.c` are compiled in ([config_e200.mk:77-78](scripts/make_scripts/config_e200.mk#L77-L78)) but the only `event_groups.h` include is in OSAL ([osal_e200.c:45](lib/module/osal/osal_e200.c#L45)) — **no application code uses event groups** |
| Tracealyzer / SystemView | **not used** — the repo has its own `TRACE_LOG()` macro that writes to a circular buffer in PEBM and is decoded offline by scripts in [scripts/debug/](scripts/debug/) |

### Hooks summary (what they do here)

- **Idle hook** ([e200main.c:186-191](lib/module/e200main/e200main.c#L186-L191)) — bumps a 64-bit counter and stores it in HIF for the host to compute CPU load. There is also a calibration variant that takes idle snapshots after fixed `vTaskDelay`s ([e200main.c:472-506](lib/module/e200main/e200main.c#L472-L506)).
- **Stack overflow hook** ([e200main.c:412-425](lib/module/e200main/e200main.c#L412-L425)) — drops real-time mode, prints the task name, then `ASSERT(0)` → `while(1)`.
- **Malloc failed hook** ([e200main.c:405-410](lib/module/e200main/e200main.c#L405-L410)) — prints and `ASSERT(0)`.
- **Tick hook** — no `vApplicationTickHook` defined anywhere → either disabled or relies on default.

---

## 3. Real-time task scheduling (CV claim #1)

### 3.1 Every `xTaskCreate` call in the repo

There are only **four `xTaskCreate` call sites**, but two of them (`tm_init` via
`osal_startThread`, and the bbdev receive thread) are invoked **many times at
runtime per core**, creating one *Task Manager* thread per priority level and
one VSPA-RX / ARM-RX thread per link.

| # | Task name (FreeRTOS) | Entry function | Priority | Stack | Call-site | Purpose |
|---|---|---|---|---|---|---|
| 1 | `"Geul TMU Task"` | `vGeulTMUTask` | `TMU_TASK_PRIORITY` (from BSP) | `TMU_TASK_STACKSIZE` | [e200main.c:1008](lib/module/e200main/e200main.c#L1008) | Handles host-interrupt notifications from the TMU IP; just blocks on `xTaskNotifyWait(portMAX_DELAY)` and re-enables the TMU IRQ. |
| 2 | `"Geul Idle CPU Calibrate"` | `vIdleCalib` | `IDLE_CALIB_INIT_PRIORITY` | `IDLE_CALIB_INIT_TASK_STACKSIZE` | [e200main.c:1027](lib/module/e200main/e200main.c#L1027) | Periodic idle-time sampling for profiling; `vTaskDelete(NULL)` when done. Only built under `CONFIG_IDLE_CALIBRATE`. |
| 3 | `"Task#%d"` (per-priority TM thread) | `tm_thread` | `OSAL_THREAD_PRIORITY_1 + taskPrio` (so 1, 2, 3) | 2 KB (`2*1024`) | [tm.c:175](lib/module/tm/tm.c#L175), driven from [appinit.c:155-171](lib/module/appinit/appinit.c#L155-L171), `NUM_PRIORITIES=3` ([appinit.c:47](lib/module/appinit/appinit.c#L47)) | Three TM threads per e200 core. Each blocks on its counting semaphore ([tm.c:93](lib/module/tm/tm.c#L93)) and dispatches the next FIFO task. **This is where the PHY components actually execute.** |
| 4 | `"Task#%d"` (`OSAL_THREAD_ID_VSPA_RX`) | `mh_link_vspa_messagingTask` | `tskIDLE_PRIORITY + OSAL_THREAD_PRIORITY_5` | 2048 | [mh_link_vspa.c:419-424](lib/module/mh/mh_link_vspa.c#L419-L424) | Drains the VSPA → e200 message FIFO that the VSPA ISR fills. |
| 5 | `"Task#%d"` (`OSAL_THREAD_ID_ARM_RX`) | `mh_link_bbdev_receive_thread` | `OSAL_THREAD_PRIORITY_6` (highest) | 3000 | [mh_link_bbdev.c:468-472](lib/module/mh/mh_link_bbdev.c#L468-L472) | Drains the bbdev/DPDK queue from the LX2160 ARM host. Only on the LX-IPC core. |
| 6 | `"Task#%d"` (`OSAL_THREAD_ID_E200_RX`) | inferred — `mh_link_e200_ipc_init` registers an IPI callback but does not create a task | n/a | n/a | [mh_link_e200_ipc.c:130](lib/module/mh/mh_link_e200_ipc.c#L130) | E200↔E200 messages are delivered **directly in IPI ISR** via `mh_sendMsgFromISR` — no dedicated receive thread. |
| 7 | UART console | `vUARTCommandConsoleStart` (FreeRTOS+CLI) | `mainUART_COMMAND_CONSOLE_TASK_PRIORITY` (BSP) | `mainUART_COMMAND_CONSOLE_STACK_SIZE` | [e200main.c:875](lib/module/e200main/e200main.c#L875), [e200main.c:1066](lib/module/e200main/e200main.c#L1066) | Diora/CLI console only when `ENABLE_DIORA_CLI` or non-L1C. Spawns its own internal task. |
| 8 | `"VSPA Rx"`-like | via `osal_startThread` (calls `xTaskCreate` internally) | various | various | [osal_e200.c:217](lib/module/osal/osal_e200.c#L217) | The generic `osal_startThread` is the single dynamic-task entry point — UART, watchdog, VSPA RX, bbdev RX all funnel here. |

#### Priority numbering (CRITICAL to understand for the interview)

The OSAL priorities are **0..6** ([osal.h:127-133](lib/module/osal/osal.h#L127-L133)),
where **`OSAL_THREAD_PRIORITY_6` is the highest** and 0 is the lowest. But
`osal_e200.c:197` comments `configMAX_PRIORITIES (5)`. These are reconciled
because `xTaskCreate` is called with `tskIDLE_PRIORITY + priority`
([osal_e200.c:218](lib/module/osal/osal_e200.c#L218)), so `priority=6` becomes
FreeRTOS priority 7 (`tskIDLE_PRIORITY=0` typically). If `configMAX_PRIORITIES`
really is 5, priorities ≥ 5 would be **clamped by FreeRTOS to `configMAX_PRIORITIES-1`**.

> **Follow-up: ask the team** to confirm `configMAX_PRIORITIES` — the code uses
> priorities up to 6 but the comment says 5; either the comment is stale or
> `configMAX_PRIORITIES` is actually 7 or 8.

Effective ordering (numerical, higher = preempts lower):
- 6 — bbdev RX (host messages: highest because they configure new slots)
- 5 — VSPA RX (drains VSPA → e200 results)
- 1, 2, 3 — TM threads (per-priority dispatchers)
- 0 — idle hook / background

### 3.2 Core affinity

This is **AMP (Asymmetric Multi-Processing), not SMP**. Each e200 core boots a
**separate FreeRTOS instance** with the same binary (master vs slave path is
selected by `ulMpicCurrentCore()` at [e200main.c:687](lib/module/e200main/e200main.c#L687)).
There is no FreeRTOS SMP scheduler and no task affinity API. Pinning is done at
deployment-table level: each PHY component is statically assigned to a
`coreId` in the `appComp_t` table
([app_deployment.h:104-118](lib/module/appinit/app_deployment.h#L104-L118)),
and the message handler routes inter-core messages via the IPI link
([mh_link_e200_ipc.c:135-152](lib/module/mh/mh_link_e200_ipc.c#L135-L152)).
The LX2160 ARM host running Linux uses real SMP with `osal_mapThread(cpu)` for
explicit pinning ([tm.c:79-85](lib/module/tm/tm.c#L79-L85)), but that's a
different binary.

### 3.3 Preemption, time-slicing

The kernel is **preemptive** (`portYIELD_FROM_ISR` is used in every
`xxxFromISR` path: [tm.c:274](lib/module/tm/tm.c#L274),
[mh_link_bbdev.c:427](lib/module/mh/mh_link_bbdev.c#L427),
[mh_link_vspa.c:649](lib/module/mh/mh_link_vspa.c#L649)). When an ISR uses
`vTaskNotifyGiveFromISR` or `xSemaphoreGiveFromISR` and the woken task is
higher-priority than the running one, the ISR yields on exit. Time-slicing
between equal-priority tasks is the FreeRTOS default but isn't relied on here —
the three TM threads each have a distinct priority (1, 2, 3) so there's almost
never a tie.

### 3.4 Tickless idle / low-power

**Not used.** No `portSUPPRESS_TICKS_AND_SLEEP` definitions, no `configUSE_TICKLESS_IDLE`
hits in the codebase. The idle hook just increments a counter
([e200main.c:186-191](lib/module/e200main/e200main.c#L186-L191)). That's
appropriate for a small-cell baseband that is always powered.

### 3.5 Runtime stats / trace

- **No `vTaskGetRunTimeStats`** in this repo's e200 path.
- Custom trace: `TRACE_LOG()` writes 32-bit log entries into a per-core circular
  buffer that the host application drains and decodes via Python scripts in
  [scripts/debug/](scripts/debug/). Each component logs entry / exit / msg-id
  for every task execution at [tm.c:113-145](lib/module/tm/tm.c#L113-L145).
- Stack-high-water-mark stats are dumped via `printHeapStackStats`
  ([e200main.c:1147-1172](lib/module/e200main/e200main.c#L1147-L1172)).

---

## 4. Interrupt handling (CV claim #2)

### 4.1 The slot-boundary IRQ (the rhythm of the PHY)

This is the most important ISR to be able to describe.

**Source:** the **TBGEN** (Time-Base Generator) IP's Timed Interrupt module
fires a callback at every slot boundary. The callback is `tbgenSlotIntCallback_ISR`
in [applications/l1c/tbgen/driver/slotIndTbgen.c:161-296](applications/l1c/tbgen/driver/slotIndTbgen.c#L161-L296).

**Period:** depends on numerology — slot duration = `frameDuration / PHY_SLOTS_PER_FRAME`
where `frameDuration = 10 * PHYIF_TBGEN_CNT_INC_PER_MS * factor` and
`PHYIF_TBGEN_CNT_INC_PER_MS = 245760` ([tbgen_.h:39](applications/l1c/tbgen/tbgen_.h#L39))
(this is 30.72 MHz × 8 = 245.76 MHz, i.e. 245,760 ticks per ms).

| Numerology (µ) | SCS | Slots / 10 ms frame | Slot duration | Source |
|---|---|---|---|---|
| 0 | 15 kHz | 10 | 1000 µs | [nr.h:58](lib/system/nr.h#L58) |
| 1 | 30 kHz | 20 | **500 µs** (default config) | [nr.h:59](lib/system/nr.h#L59), [phy.h:156](lib/system/phy.h#L156) |
| 3 | 120 kHz | 80 | 125 µs (FR2) | [phy.h:133](lib/system/phy.h#L133) |

**What the ISR does** ([slotIndTbgen.c:121-158](applications/l1c/tbgen/driver/slotIndTbgen.c#L121-L158)):

```c
static void scheduleIntTasks(tbgenCompContext_t* tbgenCtx)
{
    if( tbgenCtx->tbgenIntMsgGenFlag ) {
        ASSERT( tbgenCtx->tbgenNumIntMsgs < TBGEN_NUM_OF_INT_MSGS );
        g_tbgenIntMsgCnt++;
        for(int i=0; i<tbgenCtx->tbgenNumIntMsgs; i++ ) {
            uint8_t compId = tbgenCtx->tbgenIntMsg[i].compId;
            uint8_t intMsgId = tbgenCtx->tbgenIntMsg[i].intMsgId;
            schContext_t *schCtx = (schContext_t *) g_schCtx[ compId ];
            uint32_t sfnSlot = (tbgenCtx->sfn << 16) | tbgenCtx->slot;
            sch_scheduleIntTaskFromISR( schCtx, intMsgId, (void *) sfnSlot );
        }
    }
}
```

It iterates a registered list of (component, intMsgId) pairs and enqueues an
INT task in each component's task table via the scheduler. For the L1C app the
table maps `PHYIF_SLOT_INT` → `phyifSlotInt` at `SCH_TASK_PRIORITY_2`
([phyif_comp.c:93](applications/l1c/phyif/phyif_comp.c#L93)), so the **slot
tick wakes the priority-2 TM thread** running on the PHYIF core.

`sch_scheduleIntTaskFromISR` ([scheduler.c:262-287](lib/module/sch/scheduler.c#L262-L287))
calls `tm_enqueueTaskFromISR` ([tm.c:228-277](lib/module/tm/tm.c#L228-L277)),
which writes a FIFO entry and **gives the TM counting semaphore from ISR**:

```c
BaseType_t r = xSemaphoreGiveFromISR(tmCtx->sema, &xHigherPriorityTaskWoken);
ASSERT(r == pdTRUE);
portYIELD_FROM_ISR( xHigherPriorityTaskWoken );
```

This is the canonical FreeRTOS "deferred work to task" pattern.

### 4.2 Every ISR handler in the repo

| ISR | Source | IRQ # | Registered at | What it wakes |
|---|---|---|---|---|
| `tbgenSlotIntCallback_ISR` | TBGEN slot timer (every slot) | Timed-int via TBGEN (no MPIC #) | [slotIndTbgen.c:299-340](applications/l1c/tbgen/driver/slotIndTbgen.c#L299-L340) | PHYIF / STAT INT tasks via `sch_scheduleIntTaskFromISR` |
| `mh_link_vspa_ISR` | VSPA per-core event flags + DMA IRQs | per VSPA core | [mh_link_vspa.c:702-723](lib/module/mh/mh_link_vspa.c#L702-L723) | VSPA messaging task (`vTaskNotifyGiveFromISR`) |
| `mh_link_bbdev_ISR` | LX2160 ARM MSI for bbdev op completions | MSI #145 / `DEVICE_SHARE_MESSAGE 5` | [mh_link_bbdev.c:457-465](lib/module/mh/mh_link_bbdev.c#L457-L465) | bbdev receive thread (`vTaskNotifyGiveFromISR`) |
| `dce_comp_feca_isr` | FECA Downlink Channel Encoder done | INT 92 | [feca.c:339-343](lib/module/feca/feca.c#L339-L343) | DCE component (via scheduler) |
| `dcd_comp_feca_isr` | FECA Downlink Channel Decoder (SD) done | INT 90 | [feca.c:504-510](lib/module/feca/feca.c#L504-L510) | DCD component → posts `dcd_slotCfgResp` via `mh_sendMsgFromISR` ([dcd_comp_feca.c:1132](applications/l1c/dcd/dcd_comp_feca.c#L1132)) |
| `cce_comp_feca_isr` | FECA Control Channel Encoder done | INT 93 | [feca.c:513-520](lib/module/feca/feca.c#L513-L520) | CCE component |
| `ccd_comp_feca_isr` | FECA Control Channel Decoder done | INT 91 | [feca.c:524-531](lib/module/feca/feca.c#L524-L531) | CCD component → `sch_scheduleIntTaskFromISR(_COMP_ID_CCD, CCD_BDEC_INT, …)` ([ccd_comp_feca.c:734](applications/l1c/ccd/ccd_comp_feca.c#L734)) |
| `mh_link_e200_ipc_isrCallback` | e200 ↔ e200 IPI (doorbell) | `IPI_EVT_ID0` | [mh_link_e200_ipc.c:130](lib/module/mh/mh_link_e200_ipc.c#L130) | Routes via `mh_sendMsgFromISR` to a destination component on this core |
| Geul-to-Geul IRQ | inter-Geul wakeup | EXTERNAL `IRQ_3_OFFSET` | [mh_link_geul_interrupt.c:65](lib/module/mh/mh_link_geul_interrupt.c#L65) | Per `mh_link_geul.c:120`: `mh_sendMsgFromISR(msgBuf)` |
| BM watchdog ISR | software heartbeat | n/a | [bm_interface.c:582](lib/component/bm/interface/bm_interface.c#L582) | `mh_sendMsgFromISR` |

### 4.3 NVIC priorities / `configMAX_SYSCALL_INTERRUPT_PRIORITY`

This is **PowerPC e200 with MPIC**, not ARM Cortex-M, so there is no NVIC. The
`configMAX_SYSCALL_INTERRUPT_PRIORITY` concept (the threshold above which
FreeRTOS APIs *must not* be called) is enforced differently — MPIC has 16
priority levels and the FreeRTOS port masks at one of them. The exact level
isn't visible without the BSP submodule.

> **Follow-up: ask the team** for the value of `configMAX_SYSCALL_INTERRUPT_PRIORITY`
> in `external/e200_bsp2.2/<…>/FreeRTOSConfig.h` and which MPIC priority level
> it maps to. The *meaning* still applies: any ISR that wants to call a
> `xxxFromISR` API has to run at a priority **at or below** that threshold
> (numerically higher on PowerPC MPIC). All the application ISRs registered via
> `lRegisterIrq` use the kernel-managed priority, so they are safe.

### 4.4 Representative deferred-work ISR (5–10 lines)

[mh_link_vspa.c:633-652](lib/module/mh/mh_link_vspa.c#L633-L652):

```c
xHigherPriorityTaskWoken = pdFALSE;

// Notify the VSPA Messaging Task.
vTaskNotifyGiveFromISR(msgTask->messagingTask, &xHigherPriorityTaskWoken);

mh_link_vspa_ISR_txNotifyCnt++;
mh_link_vspa_ISR_running = 0;

portYIELD_FROM_ISR( xHigherPriorityTaskWoken );
```

This is the textbook pattern: the ISR (a) reads device registers and stashes
the event flags into a small FIFO ([mh_link_vspa.c:618-632](lib/module/mh/mh_link_vspa.c#L618-L632)),
(b) gives a task notification, (c) yields if a higher-priority task became
ready. **All the heavy lifting (endian conversion of init indications,
component message dispatch) happens in the task context**, not the ISR.

`xTaskNotifyGive` / `vTaskNotifyGiveFromISR` is a one-counter-per-task
lightweight binary/counting semaphore built into every task's TCB. It is
faster than a separate `xSemaphoreCreateBinary` because it avoids creating a
queue object.

### 4.5 Critical sections

The codebase uses two layers:

1. **`osal_enterCritical()` / `osal_exitCritical()`** — wraps
   `portENTER_CRITICAL` / `portEXIT_CRITICAL`
   ([osal.h:230-232](lib/module/osal/osal.h#L230-L232)). On the PowerPC port
   this masks interrupts at or below the kernel level. Used at the boundary
   between tasks and ISRs that touch the same FIFO — e.g.
   [tm.c:193,217](lib/module/tm/tm.c#L193) wraps the FIFO write in
   `tm_enqueueTask`, and [tm.c:240,265](lib/module/tm/tm.c#L240) does the same
   for `tm_enqueueTaskFromISR`.
2. **`portDISABLE_INTERRUPTS()` direct** — used once in
   [osal_e200.c:186](lib/module/osal/osal_e200.c#L186) inside `__swbreak()` so
   the debugger software-breakpoint loop cannot be preempted.
3. **Spinlocks** for cross-core mutual exclusion (multiple e200 cores can
   contend) — `pxSpinLockAlloc`, `vSpinLockAcquire`, `vSpinLockRelease`
   ([heap.c:111-128](lib/module/heap/heap.c#L111-L128) protects the shared
   heap, [osal_e200.c:148-160](lib/module/osal/osal_e200.c#L148-L160) protects
   VSPA DMEM allocations, [dma_ppc.c:241-253](lib/module/dma/dma_ppc.c#L241-L253)
   protects VSPA DMA channel allocation per VSPA core).

`vTaskSuspendAll` / `xTaskResumeAll` is used to bracket the libc `free()` call
in `vGeulFree` ([e200main.c:1137-1142](lib/module/e200main/e200main.c#L1137-L1142))
— it prevents context switches without disabling interrupts.

---

## 5. Inter-task communication (CV claim #3)

There are **four cooperating IPC mechanisms** in this codebase. They are tiered
by scope: within an e200 core (FreeRTOS objects), across e200 cores on the
same Geul (IPI doorbells), e200 ↔ VSPA (DMA + event flags), Geul ↔ Geul
(external IRQ), and e200 ↔ host ARM (bbdev IPC queues + MSI).

### 5.1 Queues (`xQueueCreate`)

**There are NO direct `xQueueCreate` calls in this repo.** The application
sits on top of a custom Task Manager (TM) FIFO that is protected by a
**counting semaphore** rather than a queue — `xQueueCreate` is not used
because the entries are richer than a fixed-size value. See
[tm.h](lib/module/tm/tm.h) and the structure at
[tm.c:48,87-160](lib/module/tm/tm.c#L48).

The FreeRTOS+CLI `cOutputBuffer` ([e200main.c:151](lib/module/e200main/e200main.c#L151))
is a static buffer the CLI task fills; it isn't a queue.

> If asked "where are your `xQueueCreate` calls", the honest answer is "we
> deliberately built a custom TM FIFO instead of using FreeRTOS queues
> because (a) it stores function pointers + heterogenous args, (b) we wanted
> ISR-safe enqueue with a single counting-semaphore give per item, and (c) we
> wanted per-priority FIFO instances rather than a single queue. The
> equivalent FreeRTOS object would be 3 queues per core plus a separate
> semaphore for blocking — the TM merges them."

### 5.2 Semaphores

Every `osal_createSemaphore()` call. Note that `osal_createSemaphore` is
`xSemaphoreCreateCounting(OSAL_SEMA_MAX_VALUE=32, 0)` —
**counting**, not binary ([osal.h:235-237](lib/module/osal/osal.h#L235-L237)).
Why counting: because multiple producers (different ISRs, different tasks) can
all give the semaphore before the consumer wakes, and the consumer needs to
see the right number of items.

| Where | Purpose | File:line |
|---|---|---|
| `tmCtx->sema` | The heart of the system: the TM thread blocks on this; every `sch_scheduleTask`/`sch_scheduleIntTaskFromISR` gives it. | [tm.c:169](lib/module/tm/tm.c#L169), [tm.c:222](lib/module/tm/tm.c#L222), [tm.c:271](lib/module/tm/tm.c#L271) |
| `bmCtx->watchdog.sema` | Buffer-manager heartbeat wait | [bm.c:274](lib/component/bm/bm.c#L274) |
| `g_bmIfCtx.remoteOp.sema` | Per-core remote BM ops | [bm.c:242,257](lib/component/bm/bm.c#L242) |
| `dscIfCtx->remoteOpSema` | Data-stream-capture remote op wait | [dsc_interface.c:112](lib/component/dsc/interface/dsc_interface.c#L112) |
| `ifCtx->sema` | Stream-interconnect flag-allocation gate | [interconnect_flags.c:91](lib/module/interconnect_flags/interconnect_flags.c#L91) |
| `g_dumpMsgSema` | Debug message-dump serialisation | [mh.c:546](lib/module/mh/mh.c#L546) |
| `mhLinkVspaCtx->sendFromQSema` | VSPA send-from-queue gate | [mh_link_vspa.c:762](lib/module/mh/mh_link_vspa.c#L762) |
| `osal_msgBufPool_t.poolSema` | Linux/host-only pool gate (e200 uses a spinlock instead) | [osal_linux.c:97](lib/module/osal/osal_linux.c#L97) |

**No `xSemaphoreCreateBinary`** is used directly in this repo. Where a "wake
me up when X happens" pattern is needed, the code prefers `xTaskNotifyGive` /
`vTaskNotifyGiveFromISR` instead (see §5.4).

### 5.3 Mutexes

**No `xSemaphoreCreateMutex` calls in the e200 path.** Mutual exclusion in
this codebase is done with either:
- **Critical sections** (mask local interrupts, very short) — used when the
  contention is task ↔ ISR or task ↔ task on the same core.
- **Hardware spinlocks** — used when the contention is across e200 cores on
  the same Geul; e.g. the VSPA DMEM allocator
  ([osal_e200.c:148-160,652](lib/module/osal/osal_e200.c#L148-L160)), the
  shared heap ([heap.c:91-128](lib/module/heap/heap.c#L91-L128)), the print
  spinlock ([e200main.c:144,729](lib/module/e200main/e200main.c#L144)), and
  per-VSPA DMA channel locks ([dma_ppc.c:88](lib/module/dma/dma_ppc.c#L88)).

This means **priority inheritance is not in play** on the e200 side — there is
no `xSemaphoreCreateMutex` to provide it. Critical sections are too short to
cause priority inversion in practice. (The Linux host side does use
`pthread_mutex_t`.)

### 5.4 Direct-to-task notifications

This is the **preferred** wake-up mechanism in this repo. See
[e200main.c:459](lib/module/e200main/e200main.c#L459):

```c
xResult = xTaskNotifyWait( pdFALSE, UINT32_MAX, &ulNotifiedValue, portMAX_DELAY );
```

and the ISR side at [mh_link_vspa.c:637](lib/module/mh/mh_link_vspa.c#L637)
and [mh_link_bbdev.c:421](lib/module/mh/mh_link_bbdev.c#L421):

```c
vTaskNotifyGiveFromISR(bbdevCtx->threadHandle, &xHigherPriorityTaskWoken);
```

**Why notifications instead of semaphores here?** Each task has exactly one
producer — the ISR for its peripheral — so a per-task notification counter is
faster (no separate queue object, no kernel context switch through a queue API).
Notifications are also 32-bit values which lets the ISR pass a flag bitmask;
the TMU task uses that pattern at [e200main.c:459-468](lib/module/e200main/e200main.c#L459-L468)
to receive the interrupt-source bits in `ulNotifiedValue`.

### 5.5 e200 ↔ e200: IPI (inter-processor interrupt)

Used because each e200 core has its own FreeRTOS instance and they need to
exchange PHY messages.

- Message handler link type: `mh_link_e200_ipc`.
- Init registers an event handler: `vIPIEventRegister(IPI_EVT_ID0, NULL, mh_link_e200_ipc_isrCallback, ctx)`
  ([mh_link_e200_ipc.c:130](lib/module/mh/mh_link_e200_ipc.c#L130)).
- Sender:
  ```c
  vIPISendDatafromISR(destCoreId, IPI_EVT_ID0, (void*) msg);
  ```
  ([mh_link_e200_ipc.c:166](lib/module/mh/mh_link_e200_ipc.c#L166)) — the
  hardware doorbell raises an MPIC IRQ on the destination core.
- Receiver's ISR ([mh_link_e200_ipc.c:38-64](lib/module/mh/mh_link_e200_ipc.c#L38-L64)):
  ```c
  static void mh_link_e200_ipc_isrCallback(enum IPIEventID eventID, void* msg,
                                            void* _ctx, uint32_t srcCoreId)
  {
      mh_header_t *inMsg = (mh_header_t *) msg;
      mh_invMsg(inMsg);                          // cache invalidate
      mh_sendMsgFromISR(inMsg);                  // route to target component
  }
  ```

### 5.6 e200 ↔ VSPA: DMA + event flags

This is the M4↔VSPA-equivalent (but here e200↔VSPA).

- **Direction VSPA → e200:** the VSPA DMA hardware raises an IRQ on the e200
  side; the ISR reads `IPREG_VCPU_HOST_FLAGS0..1` (64 host event flags) and
  `IPREG_DMA_IRQ_STAT` ([mh_link_vspa.c:573-642](lib/module/mh/mh_link_vspa.c#L573-L642)),
  clears them, enqueues the (vspaCoreId, flags) tuple into a small task FIFO,
  and notifies the messaging task.
- **Direction e200 → VSPA:** the e200 writes the message into the VSPA
  incoming-message pool (a fixed buffer in VSPA DMEM whose address VSPA
  publishes via init indication at [mh_link_vspa.c:444-499](lib/module/mh/mh_link_vspa.c#L444-L499))
  and writes a flag in `IPREG_HOST_VCPU_FLAGS` (the VSPA polls these in its
  main loop).
- The **VSPA init indication** at boot ([osal_e200.c:1102-1138](lib/module/osal/osal_e200.c#L1102-L1138))
  is itself a DMA transfer from VSPA to a fixed SRAM buffer whose layout is
  declared in `vspa_initIndication_t`. The e200 endian-converts each field
  individually (PowerPC is big-endian, VSPA is little-endian).

### 5.7 e200 ↔ LX2160 ARM host: bbdev IPC (DPDK queue)

- The LX2160 ARM runs Linux + DPDK. e200#0 is the gateway.
- e200 calls `bbdev_ipc_queue_configure(BBDEV_IPC_DEV_ID_0, 0)`
  ([mh_link_bbdev.c:450](lib/module/mh/mh_link_bbdev.c#L450)).
- Outbound (e200 → ARM) — uses the bbdev enqueue descriptors at
  [mh_link_bbdev.c:486-499](lib/module/mh/mh_link_bbdev.c#L486-L499).
- Inbound — MSI #145 wakes `mh_link_bbdev_ISR`
  ([mh_link_bbdev.c:399-430](lib/module/mh/mh_link_bbdev.c#L399-L430)), which
  notifies `mh_link_bbdev_receive_thread`.

### 5.8 Cache coherency around shared-memory exchanges

The e200 has L1 data cache that is **NOT coherent** with the VSPA, FECA, or
the other cores accessing PEB/SRAM. Every shared-memory read must be
invalidate-then-read; every write is fine because the cache is **write-through**
([osal.h:256-258](lib/module/osal/osal.h#L256-L258), which makes
`osal_cacheWriteBack` and `osal_cacheWriteBackInvalidate` deliberate no-ops).

The pattern from [dcd_interface.c:88](applications/l1c/dcd/interface/dcd_interface.c#L88):

```c
harqSlotCfgs = g_qdmaSlotCfgs.slotCfgs_Ptr->harqSlotCfg[
                  (ulTti->slot + (ulTti->sfn & 1) * PHY_SLOTS_PER_FRAME)
                  % QDMA_NUM_OF_HARQ_SLOT_CFGS];
…
osal_cacheInvalidate(&harqSlotCfgs[0],
                     QDMA_MAX_NUM_OF_PUSCH_PDUS * sizeof(*harqSlotCfgs));
```

`osal_cacheInvalidate` is defined at [osal.h:254](lib/module/osal/osal.h#L254):

```c
#define osal_cacheInvalidate(ptr, size) \
    if( likely((uint32_t)ptr) ) { vL1DCacheInvLine((uint32_t)ptr, size); msync(); }
```

`msync` is a PowerPC memory-synchronisation instruction that flushes the
store buffer. The cache helpers are used heavily around HIF reads in PHYIF
([phyif_comp.c:249-286](applications/l1c/phyif/phyif_comp.c#L249-L286)) and
around BM message-pool descriptors ([bm_interface.c:1085-1162](lib/component/bm/interface/bm_interface.c#L1085-L1162)).

> **Follow-up: ask the team** to confirm the cache is configured write-through
> (the `osal_cacheWriteBack` macro is empty, which is *only* safe under that
> assumption). The MPU setup is in `vCreateMpuEntry`
> ([e200main.c:694-722](lib/module/e200main/e200main.c#L694-L722)).

---

## 6. The gNB PHY pipeline tie-in

### 6.1 Slot budget

Default build targets **SCS = 30 kHz, FR1** ([phy.h:156](lib/system/phy.h#L156)),
which gives:
- 20 slots per 10 ms radio frame
- **500 µs / slot**
- 14 OFDM symbols / slot ([nr.h:40](lib/system/nr.h#L40)) → ~35.7 µs / symbol

The TBGEN slot-tick is configured to fire **8/4 = 2 slots ahead of RF** so the
e200 has lead time to push config into VSPA before the radio symbols hit (see
the offset calculation at [slotIndTbgen.c:333](applications/l1c/tbgen/driver/slotIndTbgen.c#L333):
`pxTiParams->xTimerParams.uOffset = frameDuration-8*interval/4-2*interval/14;`
— translation: "fire at the start of frame − 2 slots − 1/7 of a slot", i.e.
~3.5 OFDM symbols of look-ahead).

### 6.2 Which task does which PHY stage

**Important:** the heavy DSP (FFT, channel estimation, equalisation, demod, etc.)
**runs on VSPA cores, not in FreeRTOS tasks**. FreeRTOS tasks are the
*orchestrators* — they translate FAPI L1 messages into VSPA component
configurations, push them via DMA + event flags, and demux the results.

Per-component mapping (L1C app, e200 cores):

| Component | What it owns | Where the task runs | Task table |
|---|---|---|---|
| PHYIF | nFAPI ↔ internal slot config; receives `PHYIF_SLOT_INT` per slot | e200 master core | [phyif_comp.c:80-94](applications/l1c/phyif/phyif_comp.c#L80-L94) |
| DLC | DL chain slot config + dispatch | e200 master | [dlc_comp.c:74](applications/l1c/dlc/dlc_comp.c#L74) |
| DCE | **D**ownlink **C**hannel **E**ncoder driver (FECA encode chain) | e200 FECA core | [dce_comp_feca.c:86](applications/l1c/dce/dce_comp_feca.c#L86) |
| CCE | Control Channel Encoder (PDCCH bits) on FECA | e200 FECA core | [cce_comp_feca.c:112](applications/l1c/cce/cce_comp_feca.c#L112) |
| ULC | UL chain slot config | e200 master | [ulc_comp.c](applications/l1c/ulc/ulc_comp.c) |
| DCD | **D**ownlink **C**hannel **D**ecoder (LDPC SD chain) driver | e200 FECA core | [dcd_comp_feca.c:60-68](applications/l1c/dcd/dcd_comp_feca.c#L60-L68) |
| CCD | Control Channel Decoder (PUCCH UCI block decode) | e200 FECA core | [ccd_comp_feca.c:51-57](applications/l1c/ccd/ccd_comp_feca.c#L51-L57) |
| RXFE / TXFE | RF front-end | VSPA cores 4-7 (see README) | n/a — VSPA |
| FFT / IFFT | OFDM (i)FFT | VSPA | [lib/component/fft/](lib/component/fft/) |
| CHEST | Channel estimation | VSPA | [lib/component/chest/](lib/component/chest/) |
| EQ | Equalisation | VSPA | [lib/component/eq/](lib/component/eq/) |
| DEMAP / DEMOD | Demap + demod | VSPA | [lib/component/demap/](lib/component/demap/), [lib/component/demod/](lib/component/demod/) |
| LDPC | **Hardware accelerator (FECA SD chain)**, driven by DCD on e200 | FECA HW + e200 driver | [lib/module/feca/feca.c:403-510](lib/module/feca/feca.c#L403-L510) |

### 6.3 End-to-end: slot-tick → decoded TB posted

UL receive (PUSCH → LDPC decode → TB CRC → response to MAC):

1. **TBGEN slot timer fires** → `tbgenSlotIntCallback_ISR`
   ([slotIndTbgen.c:161](applications/l1c/tbgen/driver/slotIndTbgen.c#L161)).
2. ISR calls `sch_scheduleIntTaskFromISR(g_schCtx[_COMP_ID_PHYIF], PHYIF_SLOT_INT, sfnSlot)`
   ([slotIndTbgen.c:155](applications/l1c/tbgen/driver/slotIndTbgen.c#L155)).
3. **`xSemaphoreGiveFromISR` on the PHYIF priority-2 TM thread**
   ([tm.c:271](lib/module/tm/tm.c#L271)) + `portYIELD_FROM_ISR`.
4. TM thread runs `phyifSlotInt` ([phyif_comp.c:362-580](applications/l1c/phyif/phyif_comp.c#L362-L580)) which:
   - Sends `L2IF_PHYIF_SLOT_IND` to MAC ([phyif_comp.c:411](applications/l1c/phyif/phyif_comp.c#L411)).
   - Builds `DLC_slotCfg_t` from cached DL_TTI.req / TX_DATA.req and posts it
     to DLC via `mh_sendMsg` ([phyif_comp.c:461-472](applications/l1c/phyif/phyif_comp.c#L461-L472)).
   - Similarly builds `ULC_slotCfg_t` for ULC.
5. **For UL:** the **VSPA RXFE** DMAs IQ samples to DDR, performs FFT, channel
   estimation, equalisation, demap → posts **PUSCH LLRs** to FECA HRAM via DMA.
6. ULC on e200 calls `dcd_prep_slotCfg` ([dcd_interface.c:88](applications/l1c/dcd/interface/dcd_interface.c#L88))
   to populate the **FECA SD command** and **HARQ buffer pointers**, with
   explicit `osal_cacheInvalidate` on the slot-cfg buffer.
7. DCD writes the FECA SD command — FECA hardware LDPC-decodes.
8. **FECA SD completion IRQ 90** → `dcd_comp_feca_isr` →
   `dcd_slotCfgResp` ([dcd_comp_feca.c:1088-1138](applications/l1c/dcd/dcd_comp_feca.c#L1088-L1138)),
   which constructs `DCD_slotCfgResp_t` and posts it back via
   **`mh_sendMsgFromISR`** ([dcd_comp_feca.c:1132](applications/l1c/dcd/dcd_comp_feca.c#L1132))
   — note the IPI hop to ULC's core if ULC isn't on the FECA core.
9. ULC merges responses and ships `L2IF_*` indications (RX_DATA.ind etc.)
   to the MAC over bbdev IPC.

The chain hops through (in order): MPIC TBGEN IRQ → counting-semaphore → TM
thread → `mh_sendMsg` (in-core) or IPI doorbell (cross-core) → VSPA DMA flag
→ VSPA component → DMA back → FECA IRQ → `mh_sendMsgFromISR` → IPI doorbell
→ ULC TM thread → bbdev IPC.

### 6.4 DMA scheduling

- Each VSPA component has a pre-configured set of DMA channels declared in
  `compSlotCfgBufs[]` at VSPA init time
  ([mh_link_vspa.c:486-495](lib/module/mh/mh_link_vspa.c#L486-L495)).
- The IPPU half of the VSPA fires DMAs in parallel with VCPU compute — this
  is what allows compute-DMA overlap inside the slot budget.
- On the e200 side, the FECA driver uses **QDMA circular buffers** for HARQ
  LLR storage ([lib/module/feca/feca_qdma.c](lib/module/feca/feca_qdma.c),
  initialised at [e200main.c:815-820](lib/module/e200main/e200main.c#L815-L820)).
  The HIF exposes the HARQ slot-cfg address to the ARM side so the MAC can
  pre-fetch.

### 6.5 WCET / timing budgets

There are no `#define WCET_*` constants and no `_perf.md` files in the repo.
The runtime stats infrastructure exists — every task entry/exit is logged with
a cycle-accurate timestamp via `TRACE_LOG` ([tm.c:121-150](lib/module/tm/tm.c#L121-L150))
and `schTaskLog_t` keeps per-component duration ([scheduler.c:298-319](lib/module/sch/scheduler.c#L298-L319))
— but the actual numbers are produced offline by the trace decoder.

The one timing assertion in the slot path is that PHYIF must consume the
previous slot's INT message **before** the next slot tick:
[slotIndTbgen.c:127-140](applications/l1c/tbgen/driver/slotIndTbgen.c#L127-L140)
(the ASSERT is currently commented out, but the check is there for debugging:
`if( g_tbgenIntMsgCnt != g_phyifIntMsgCnt ) { ASSERT(0); }` — that would catch
a missed slot deadline). The `bm_heartbeatReq()` at SFN rollover
([slotIndTbgen.c:287](applications/l1c/tbgen/driver/slotIndTbgen.c#L287))
is the rough "PHY is alive" indicator.

> **Follow-up: ask the team** for a WCET sheet — they almost certainly
> measured per-component cycle counts in the trace decoder. A common answer
> at SCS=30 kHz / 100 MHz BW: PHYIF slot-int ≈ a few tens of µs, FECA SD
> decode ≈ 50–150 µs depending on TB size, total slot path ≈ 200–400 µs of a
> 500 µs budget.

---

## 7. Likely interview questions with grounded answers

### Q1. What's the difference between a binary semaphore, a counting semaphore, a mutex, and a task notification — and when does this repo use which?

- **Binary semaphore** — single signalling token. *Not used directly in this repo.*
- **Counting semaphore** — N tokens. Used for the **TM dispatch FIFO** so an
  ISR can give it multiple times before the consumer wakes ([tm.c:169](lib/module/tm/tm.c#L169),
  `xSemaphoreCreateCounting(32, 0)` at [osal.h:237](lib/module/osal/osal.h#L237)).
- **Mutex** — like a binary semaphore but with **priority inheritance**.
  *Not used.* The codebase never calls `xSemaphoreCreateMutex`. Cross-core
  exclusion uses hardware spinlocks; same-core exclusion uses critical sections.
- **Task notification** — per-task counter / 32-bit value built into the TCB.
  Used for the VSPA ISR → messaging-task hand-off
  ([mh_link_vspa.c:637](lib/module/mh/mh_link_vspa.c#L637)) and bbdev ISR →
  bbdev RX thread ([mh_link_bbdev.c:421](lib/module/mh/mh_link_bbdev.c#L421)).
  Picked over a semaphore here because each task has exactly one producer ISR
  — notifications avoid the queue-object overhead.

### Q2. Does this repo's mutex usage need priority inheritance?

It doesn't have mutex usage. The closest analogue is the spinlock, which is
not part of the FreeRTOS kernel so PI doesn't apply. If asked the underlying
*concept*: PI prevents a low-priority task holding a mutex from being
preempted indefinitely by a medium-priority task while a high-priority task
waits — without PI, the high-priority task is blocked behind the medium one
(classic Mars Pathfinder bug). Since this repo uses critical sections
(interrupts off) for the analogous job, the holder cannot be preempted and PI
is moot.

### Q3. Why can't regular FreeRTOS APIs be called from an ISR, and what's the "FromISR" pattern?

Regular `xSemaphoreGive`, `xQueueSend` etc. may block, call the scheduler, or
manipulate kernel state without the ISR-level critical section. Calling them
from an ISR would either corrupt kernel state or hit an assertion. The
`xxxFromISR` variants:
1. Use a different critical-section primitive that doesn't try to suspend the
   scheduler.
2. Return a `pxHigherPriorityTaskWoken` flag instead of yielding immediately.
3. The ISR must call `portYIELD_FROM_ISR(xHigherPriorityTaskWoken)` on exit so
   the scheduler can preempt the interrupted task if a higher-priority one
   woke up.

Pattern from this repo ([mh_link_vspa.c:634-649](lib/module/mh/mh_link_vspa.c#L634-L649)):

```c
xHigherPriorityTaskWoken = pdFALSE;
vTaskNotifyGiveFromISR(msgTask->messagingTask, &xHigherPriorityTaskWoken);
…
portYIELD_FROM_ISR( xHigherPriorityTaskWoken );
```

### Q4. How is a task's stack size chosen, and what happens on overflow here?

It's set per-task at `xTaskCreate` time. The repo's choices:
- TM threads: **2 KB** ([tm.c:175](lib/module/tm/tm.c#L175))
- VSPA RX: **2048 bytes** ([mh_link_vspa.c:417](lib/module/mh/mh_link_vspa.c#L417))
- bbdev RX: **3000 bytes** ([mh_link_bbdev.c:436](lib/module/mh/mh_link_bbdev.c#L436))
- TMU task / Idle calib: `TMU_TASK_STACKSIZE` from BSP (follow-up)
- The osal layer enforces `>= configMINIMAL_STACK_SIZE` ([osal_e200.c:212-214](lib/module/osal/osal_e200.c#L212-L214))

In practice, sizing is iterative: deploy with a large value, run all paths,
read the high-water-mark via `usStackHighWaterMark` (printed by
`printHeapStackStats` at [e200main.c:1162-1168](lib/module/e200main/e200main.c#L1162-L1168)),
then trim.

On overflow ([e200main.c:412-425](lib/module/e200main/e200main.c#L412-L425)):
```c
void vApplicationStackOverflowHook( TaskHandle_t pxTask, char *pcTaskName )
{
    g_realTimeMode = FALSE;
    PRINTF("\r\n***** %s: STACK OVERFLOW *****\r\n", pcTaskName);
    PRINTF("\r\n GOING in WHILE(1)\r\n");
    ASSERT(0);
}
```

`ASSERT(0)` ultimately stops the cores ([osal_e200.c:1044-1046](lib/module/osal/osal_e200.c#L1044-L1046))
and tries to push the assert trace out via bbdev to the host.

### Q5. What is `configMAX_SYSCALL_INTERRUPT_PRIORITY` and what value does this build use?

It is the priority threshold above which the FreeRTOS port masks interrupts
during critical sections. **ISRs above this threshold may not call any
`xxxFromISR` API** because the kernel can't safely mask them. Below it, the
ISR is "kernel-aware" and can use the FromISR APIs.

Concrete value: the FreeRTOSConfig.h is in the submodule. **Follow-up: ask
the team.** The PowerPC MPIC has 16 priority levels; the threshold is typically
set so that bbdev (the highest-priority hardware IRQ in this build) is right
below it.

### Q6. Preemptive or cooperative scheduling? How is it visible in the code?

**Preemptive**. The evidence:
- `portYIELD_FROM_ISR(xHigherPriorityTaskWoken)` is called from every ISR
  ([tm.c:274](lib/module/tm/tm.c#L274) etc.). This only does something if the
  scheduler is preemptive.
- Multiple TM threads at different priorities run *concurrently* (priority 1,
  2, 3) — under a cooperative scheduler the lower-priority ones would never
  preempt the higher-priority ones, but here a slot tick (prio 2) does
  preempt a background prio-1 task.

### Q7. Walk me through a slot from the timer IRQ to the LDPC decode result being posted back.

See §6.3.

### Q8. What happens if a task misses its deadline?

Three layers:
1. **Soft check**: `g_tbgenIntMsgCnt vs g_phyifIntMsgCnt` mismatch detection
   in [slotIndTbgen.c:127-140](applications/l1c/tbgen/driver/slotIndTbgen.c#L127-L140).
   The `ASSERT(0)` is commented out in production but the check still logs.
2. **Hardware watchdog**: enabled in main via `vWatchdogStart(3000, wdogCallback)`
   ([e200main.c:1084](lib/module/e200main/e200main.c#L1084)) — 3 second
   timeout with a callback that returns 1 to pet the dog
   ([e200main.c:158-169](lib/module/e200main/e200main.c#L158-L169)). If the
   callback returns 0, the watchdog reset fires.
3. **Heartbeat**: `bm_heartbeatReq()` at SFN rollover
   ([slotIndTbgen.c:287](applications/l1c/tbgen/driver/slotIndTbgen.c#L287))
   tells the host "this Geul is alive".

Single missed slot ⇒ trace mismatch + the PHY tries to recover on next slot
(it's stateless per-slot for most components). Repeated misses ⇒ the host's
heartbeat watchdog times out and triggers PHY restart.

### Q9. How do you debug a deadlock between two queues in FreeRTOS?

For this repo specifically:
- Enable `TRACE_LOG` on the suspect TM threads — every enqueue/dequeue and
  every task entry/exit logs its msgId. The trace decoder produces a
  per-thread timeline; a deadlock shows as both threads blocked on their
  counting semaphore with the FIFO non-empty (impossible) or empty (so
  somebody dropped the give).
- `printHeapStackStats` ([e200main.c:1162-1168](lib/module/e200main/e200main.c#L1162-L1168))
  dumps task state — `eCurrentState=eBlocked` on both halves is the symptom.
- In production debug builds, the BM module also dumps message pool occupancy.
- Generic FreeRTOS technique: `vTaskList` / `uxTaskGetSystemState` (not
  currently wired in here but the BSP supports it).

### Q10. How does the e200 communicate to VSPA in this repo?

See §5.6. Two-way: VSPA → e200 via DMA-complete IRQ + event flags (drained by
the messaging task at [mh_link_vspa.c:419](lib/module/mh/mh_link_vspa.c#L419)).
e200 → VSPA by writing the message into the VSPA's incoming-message pool
(address obtained from the VSPA's init indication
[mh_link_vspa.c:466](lib/module/mh/mh_link_vspa.c#L466)) and raising a
host→VSPA event flag. There's no FreeRTOS object on the VSPA side — VSPA is
bare-metal and polls flags.

### Q11. What's the tick rate and why?

**Follow-up: ask the team.** Indirect evidence: `vTaskDelay(15000)`,
`vTaskDelay(1000)`, `vTaskDelay(271000)` and `vTaskDelay(10000)`
([e200main.c:477-497](lib/module/e200main/e200main.c#L477-L497)) for *seconds*
of wall-clock delay suggest **`configTICK_RATE_HZ = 1000`** (1 ms tick), which
is the conventional choice. A higher tick rate would just burn cycles in the
tick ISR; a lower one would coarsen `vTaskDelay`.

### Q12. How does the firmware handle a fault / hot reset on the DSP?

VSPA asserts are handled via the event flag `EVENT_FLAG_VSPA_ASSERT`
([mh_link_vspa.c:603-607](lib/module/mh/mh_link_vspa.c#L603-L607)) which calls
`osal_vspa_assert(vspaCoreId)` on the e200. That handler
([osal_e200.c:1052-1165](lib/module/osal/osal_e200.c#L1052-L1165)):
1. Enters critical section.
2. Reads the VSPA cycle counter and logs it (for trace time-alignment).
3. Stops the RXFE / TXFE VSPA cores ([osal_e200.c:1084](lib/module/osal/osal_e200.c#L1084)).
4. Stops the TBGEN slot indication ([osal_e200.c:1087](lib/module/osal/osal_e200.c#L1087)).
5. Endian-converts the VSPA's init-indication / assert-location buffer.
6. Sends `bm_traceInd()` + `bm_vspaAssertInd()` to the host so traces are
   preserved before the cores halt.
7. `while(1) {}` — the e200 stops scheduling.

There is no automatic re-init of the VSPA on assert; the host has to
power-cycle / reboot the modem. The dual-Geul code path
(`osal_geul_remoteAssert`, [osal_e200.c:916-969](lib/module/osal/osal_e200.c#L916-L969))
mirrors the same on the *other* Geul if one of them asserts.

### Q13. Why heap_4 and not heap_1/2/3/5?

- `heap_1` — alloc only, no free. Wouldn't work because `vGeulFree` and
  `vPortFree` are used at runtime (e.g. CLI buffers, OSAL message buffers
  released on task completion at [tm.c:155](lib/module/tm/tm.c#L155)).
- `heap_2` — supports free but no coalescing → fragmentation.
- `heap_3` — wraps newlib `malloc`. They actually use this for the libc
  heap (`g_libcHeapStart..End` at [e200main.c:612-614](lib/module/e200main/e200main.c#L612-L614))
  but FreeRTOS itself needs its own.
- `heap_4` — fast, supports coalescing, deterministic enough for hard-real-time
  if you size correctly. **This is what's compiled in**
  ([config_e200.mk:76](scripts/make_scripts/config_e200.mk#L76)).
- `heap_5` — for non-contiguous heap regions. Not needed because the e200
  heap is one contiguous DMEM region.

### Q14. What's an "AMP" vs "SMP" build, and which is this?

**AMP** = each core boots its own image / scheduler; cores communicate via
message passing. **SMP** = one scheduler dispatches tasks across cores.

This is **AMP**: `e200main.c:main` runs separately on every core
([e200main.c:687](lib/module/e200main/e200main.c#L687):
`crt_core_id = (uint8_t)ulMpicCurrentCore()`), and `vTaskStartScheduler`
([e200main.c:1088](lib/module/e200main/e200main.c#L1088)) starts an
independent FreeRTOS instance per core. The IPI link
([mh_link_e200_ipc.c](lib/module/mh/mh_link_e200_ipc.c)) is how the cores
talk to each other. FreeRTOS SMP exists (since v10.5) but isn't used here.

### Q15. If I add a new PHY component, what do I have to wire up?

1. Define the task table (message IDs ↔ task functions ↔ priorities) like
   [phyif_comp.c:80-94](applications/l1c/phyif/phyif_comp.c#L80-L94).
2. Add the component to the right `appDeployment_t` ([app_deployment.h:185-197](lib/module/appinit/app_deployment.h#L185-L197))
   — that's where the **core mapping** lives.
3. Provide `init`/`initShared` callbacks ([app_deployment.h:65-100](lib/module/appinit/app_deployment.h#L65-L100)).
4. If it talks to VSPA, register a DMA channel + event flag.
5. If it needs the slot tick, add an entry to `tbgenIntMsg[]` so the TBGEN
   ISR schedules it ([slotIndTbgen.c:144-156](applications/l1c/tbgen/driver/slotIndTbgen.c#L144-L156)).
6. If it has a hardware IRQ, call `lRegisterIrq(INTERNAL_IRQ_OFFSET + xIrqNo, isr, ctx)`
   and `bMpicEnable` like the FECA setup ([feca.c:339-344](lib/module/feca/feca.c#L339-L344)).

---

## 8. Cheat-sheet of FreeRTOS APIs used (for the RTOS-weak reader)

- **`xTaskCreate(func, name, stackWords, arg, prio, &handle)`** — dynamically
  allocate a task. `prio` is numeric, higher = preempts lower (up to
  `configMAX_PRIORITIES-1`).
- **`vTaskStartScheduler()`** — never returns. From this point the scheduler
  picks the highest-priority ready task each tick / preemption.
- **`xSemaphoreCreateCounting(max, init)`** — counting semaphore (32-deep
  in this repo, [osal.h:235](lib/module/osal/osal.h#L235)).
- **`xSemaphoreTake(sema, ticks)`** — block waiting; `portMAX_DELAY` = forever.
- **`xSemaphoreGive(sema)` / `xSemaphoreGiveFromISR(sema, &woken)`** — release.
  The ISR variant *must* be used from interrupt context.
- **`vTaskNotifyGiveFromISR(task, &woken)`** / **`ulTaskNotifyTake(clearOnExit, timeout)`** —
  per-task lightweight notify; faster than a separate semaphore. Used for
  per-peripheral wake-ups in this repo.
- **`xTaskNotifyWait(clearOnEntry, clearOnExit, &value, timeout)`** — wait for
  any of 32 bits. Used by the TMU task ([e200main.c:459](lib/module/e200main/e200main.c#L459))
  to receive interrupt-source bits.
- **`portYIELD_FROM_ISR(woken)`** — at the *end* of an ISR; tells the kernel
  to do a context switch on ISR exit if a higher-priority task became ready.
- **`portENTER_CRITICAL` / `portEXIT_CRITICAL`** — mask interrupts; very short
  windows only. Wrapped here as `osal_enterCritical()` / `osal_exitCritical()`.
- **`vTaskSuspendAll()` / `xTaskResumeAll()`** — disable scheduler without
  masking interrupts. Used here around `free()` ([e200main.c:1137-1142](lib/module/e200main/e200main.c#L1137-L1142)).
- **`pvPortMalloc` / `vPortFree`** — FreeRTOS heap-4 alloc/free; thread-safe.
- **`vApplicationXxxHook`** — user-supplied callbacks (idle, malloc-failed,
  stack-overflow). All implemented in [e200main.c:186-425](lib/module/e200main/e200main.c#L186-L425).

---

## 9. Open questions / things to clarify with the original team

1. The exact `configTICK_RATE_HZ`, `configMAX_PRIORITIES`,
   `configMAX_SYSCALL_INTERRUPT_PRIORITY`, `configTOTAL_HEAP_SIZE`,
   `configMINIMAL_STACK_SIZE`, `configCHECK_FOR_STACK_OVERFLOW` (1 or 2?) —
   all in the unfetched `external/e200_bsp2.2/.../FreeRTOSConfig.h`.
2. Whether the data cache is configured write-through (the code's
   `osal_cacheWriteBack` no-ops only work under that assumption).
3. The numeric `TMU_TASK_PRIORITY`, `TMU_TASK_STACKSIZE`, `TMU_TASK_CORE`,
   `mainUART_COMMAND_CONSOLE_TASK_PRIORITY`, `mainUART_COMMAND_CONSOLE_STACK_SIZE`
   — also in the BSP submodule.
4. Per-component WCET measurements — somebody on the team has them in the
   trace decoder; ask for the "slot timing PDF" / latest perf report.
5. The chip the production firmware ships on — LA1224, LA9358 or LA1238CPE
   — and confirm the CV claim should match it.
6. Whether priority numbers 5/6 used in OSAL actually take effect — they
   appear to exceed `configMAX_PRIORITIES (5)` per the comment, which FreeRTOS
   would clamp.

---

*Doc generated from a fresh read of the repo at `c:\Users\Smita.Sahu\Desktop\5GNR\nxpphy\NXPPHY`
on 2026-05-19. All file:line references are clickable and were live at the time of writing.*
