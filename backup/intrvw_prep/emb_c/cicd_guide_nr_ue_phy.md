# CI/CD Guide for `nr_ue_phy` — Explained Simply

> Based on the [JetBrains TeamCity CI/CD Ultimate Guide](https://www.jetbrains.com/teamcity/ci-cd-guide/)
> Applied to the 5G NR UE PHY C codebase targeting x86 (simulation) and ARMv8 (StarTag hardware).

---

## Table of Contents

1. [What is CI/CD? — The Big Picture](#1-what-is-cicd--the-big-picture)
2. [Continuous Integration (CI)](#2-continuous-integration-ci)
3. [Continuous Delivery (CD)](#3-continuous-delivery-cd)
4. [Continuous Deployment](#4-continuous-deployment)
5. [CI vs. Delivery vs. Deployment — The Difference](#5-ci-vs-delivery-vs-deployment--the-difference)
6. [The CI/CD Pipeline — How the Stages Connect](#6-the-cicd-pipeline--how-the-stages-connect)
7. [Automated Builds](#7-automated-builds)
8. [Automated Testing](#8-automated-testing)
9. [CI/CD Best Practices](#9-cicd-best-practices)
10. [Benefits of CI/CD](#10-benefits-of-cicd)
11. [Putting It All Together — A CI/CD Proposal for `nr_ue_phy`](#11-putting-it-all-together--a-cicd-proposal-for-nr_ue_phy)

---

## 1. What is CI/CD? — The Big Picture

### What the guide says

CI/CD = **Continuous Integration** + **Continuous Delivery/Deployment**.

It is the practice of automatically building, testing, and (optionally) releasing your software every time someone pushes code — so bugs are caught in minutes, not weeks.

### In plain words

> Think of CI/CD as an **automatic quality checkpoint on a factory assembly line**.
> Every time an engineer adds or changes a part (commits code), the belt moves, all checks run automatically, and only passing builds move forward.

### The three levels at a glance

```
Developer pushes code
        │
        ▼
┌────────────────────┐
│  Continuous        │  Build + Unit tests run automatically on every commit
│  Integration (CI)  │  → Fast feedback (minutes)
└────────────────────┘
        │  if passes
        ▼
┌────────────────────┐
│  Continuous        │  Deploy to staging, run integration/perf/security tests
│  Delivery (CD)     │  → Human presses "Release" button when ready
└────────────────────┘
        │  (or automatically)
        ▼
┌────────────────────┐
│  Continuous        │  Every passing build goes live automatically
│  Deployment        │  → No human intervention needed
└────────────────────┘
```

### Applied to `nr_ue_phy`

| Layer | `nr_ue_phy` equivalent |
|-------|------------------------|
| CI | `cmake + make` compiles cleanly, `ctest` passes on every PR/push |
| CD (Delivery) | A tagged build is packaged (`make package`) and flashed to StarTag hardware only when an engineer approves |
| CD (Deployment) | Not applicable — embedded firmware does not auto-deploy; a human flash step is always needed |

---

## 2. Continuous Integration (CI)

### What the guide says

Every time you **merge/push** code, a CI server:
1. Compiles the code
2. Runs automated tests
3. Reports pass/fail in minutes

The key idea: **work in small batches and share often** so merge conflicts are tiny and bugs are caught while the change is still fresh in your mind.

### Without CI — what happens in `nr_ue_phy` today (the problem)

Imagine two engineers each working on separate features for a week:

- Engineer A: modifies `src/dl/pdsch/dl_harq.c` (HARQ combining logic)
- Engineer B: changes `lib/x86/cn_ldpc_decoder.c` (LDPC decoder output format)

When they finally merge, the PDSCH decoder chain may silently break — but nobody finds out until someone manually runs the full test vector suite days later.

### With CI — the fix

```
Engineer A pushes  →  cmake + make  →  ctest -R PDSCH  →  ✅ or ❌ within 5 min
Engineer B pushes  →  cmake + make  →  ctest -R rate_matcher  →  ✅ or ❌ within 5 min
```

Both engineers know immediately if their change broke something.

### CI practices for `nr_ue_phy`

| Practice | What to do |
|----------|------------|
| **Version control everything** | Code, `CMakeLists.txt`, toolchain files, test vector configs — already in Git ✅ |
| **Commit small, commit often** | Aim for at least one push per day per engineer |
| **Automate the build** | `cmake .. && make -j$(nproc)` — already scriptable ✅ |
| **Automate tests** | `ctest` already exists for component and submodule tests ✅ |
| **Fix failures immediately** | If `ctest` fails on CI, the whole team stops and fixes before adding more code |
| **Run locally first** | Developers run `cmake + make + ctest` before pushing to avoid trivial failures |

---

## 3. Continuous Delivery (CD)

### What the guide says

CD extends CI by automatically **deploying** each passing build to staging/test environments and running a wider set of automated tests (integration, performance, security). The **final release to production is triggered manually** — a human decides when it goes out.

### Why not continuous *deployment* for `nr_ue_phy`?

`nr_ue_phy` produces **embedded firmware** for the StarTag hardware (ARMv8 + NXP LA9310 RF). You cannot auto-deploy firmware to hardware the way a web service deploys to a server. The guide itself notes:

> *"For mobile apps, APIs, and embedded software, it often makes sense to group changes into larger releases."*

So **Continuous Delivery** is the right model here.

### CD pipeline for `nr_ue_phy`

```
CI passes (x86 build + ctest)
        │
        ▼
┌──────────────────────────────────┐
│  ARM cross-compile               │  cmake .. -DCMAKE_TOOLCHAIN_FILE=../toolchains/startag-1.0.1.cmake
│  (automated, triggered by CI)    │  make package -j$(nproc)
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│  x86 end-to-end emulation tests  │  scripts/run_x86_regression.sh build_dir tv_dir
│  (automated against test vectors)│  Python automation: python3 run_tests.py
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│  Hardware-in-the-loop test       │  Flash to StarTag, run RF test vectors
│  (manual trigger or scheduled)   │  Verify PDSCH, PUSCH, PRACH, PUCCH chains
└──────────────────────────────────┘
        │  Engineer approves
        ▼
   📦 Release package (.deb / tarball)
```

### Key principle: Build Once, Promote the Same Artifact

Do **not** rebuild from source for ARM after x86 tests pass. Compile the ARM package once; promote that exact binary through each test stage.

```
x86 build artifact  → x86 ctest  → ✅ → (same artifact) → ARM flash → HIL test
```

---

## 4. Continuous Deployment

### What the guide says

Every commit that passes all pipeline stages goes **automatically to production** — no human approval. Used heavily by web companies (Netflix, Amazon).

### Is it relevant to `nr_ue_phy`?

**Mostly no** for the final hardware step, but some ideas are worth borrowing:

| Continuous Deployment concept | Adapted for `nr_ue_phy` |
|-------------------------------|-------------------------|
| **Automatic release to production** | Not applicable — firmware always needs a human flash step |
| **Quality gates** | Auto-fail the pipeline if `ctest` pass rate < 100%, or PDSCH BER exceeds threshold |
| **Canary deployment** | Flash a new firmware version to one StarTag unit first, monitor RF metrics, then roll out to the rest |
| **Blue/green deployment** | Keep two StarTag boards — one running the "last known good" firmware, one under test |
| **Monitoring production metrics** | Monitor BLER, sync loss rate, CPU load on the live board after each firmware update |
| **Feature flags** | Use `#ifdef` guards or runtime config to hide incomplete NR features (e.g., FR2 support) from test scenarios |

---

## 5. CI vs. Delivery vs. Deployment — The Difference

A simple comparison table for `nr_ue_phy` context:

| | CI | Continuous Delivery | Continuous Deployment |
|---|---|---|---|
| **Trigger** | Every commit | Every CI-passing build | Every CI-passing build |
| **What runs** | Compile + ctest | ARM cross-build + regression | Same + HIL |
| **Release to hardware** | ❌ Never | ✅ Manual (engineer approves) | ❌ Not practical for firmware |
| **Feedback speed** | Minutes | Hours | N/A |
| **Best for** | Daily dev workflow | Sprint-end firmware releases | Web/cloud services |
| **`nr_ue_phy` use** | ✅ Yes (core practice) | ✅ Yes (recommended) | ⚠️ Partial (borrow quality gate ideas) |

---

## 6. The CI/CD Pipeline — How the Stages Connect

### What the guide says

A pipeline is the **chain of automated stages** that code travels through from a developer's commit to a release. Each stage must pass before the next one starts.

### `nr_ue_phy` pipeline design

```
┌─────────────────────────────────────────────────────────────────────┐
│                        nr_ue_phy CI/CD Pipeline                     │
│                                                                     │
│  [1] Git push / PR                                                  │
│       │                                                             │
│       ▼                                                             │
│  [2] Static Analysis & Linting  ← clang-format, -Wall -Wextra      │
│       │  ✅ pass                                                     │
│       ▼                                                             │
│  [3] x86 Debug Build            ← cmake -DCMAKE_BUILD_TYPE=Debug    │
│       │         │                  -DUSE_ASAN=On                    │
│       │         └─ AddressSanitizer enabled                         │
│       │  ✅ pass                                                     │
│       ▼                                                             │
│  [4] Unit / Component Tests     ← ctest -R HARQ                    │
│       │                            ctest -R rate_matcher            │
│       │                            ctest -R descrambler             │
│       │  ✅ pass                                                     │
│       ▼                                                             │
│  [5] x86 Release Build          ← cmake .. (default x86 Release)   │
│       │  ✅ pass                                                     │
│       ▼                                                             │
│  [6] Submodule Integration Tests← ctest -R SYNC                    │
│       │                            ctest -R PDSCH                   │
│       │                            ctest -R PUSCH                   │
│       │  ✅ pass                                                     │
│       ▼                                                             │
│  [7] x86 End-to-End Emulation   ← scripts/run_x86_regression.sh    │
│       │                            python3 run_tests.py             │
│       │  ✅ pass                                                     │
│       ▼                                                             │
│  [8] ARM Cross-Compile & Package← cmake + toolchains/startag cmake │
│       │                            make package                     │
│       │  ✅ pass                                                     │
│       ▼                                                             │
│  [9] 🚦 Manual Gate: Engineer approves for HIL                     │
│       │                                                             │
│       ▼                                                             │
│ [10] Hardware-in-the-Loop (HIL) ← Flash StarTag, RF test vectors   │
│       │  ✅ pass                                                     │
│       ▼                                                             │
│ [11] 📦 Release artifact published                                  │
└─────────────────────────────────────────────────────────────────────┘
```

### Pipeline stage tips

- **Fail fast**: run the cheapest tests first (clang-format check < 1 min, ctest component tests ~ few min).
- **Parallelize where possible**: run `ctest -j$(nproc)` to run multiple component tests simultaneously.
- **Feature branches**: run stages 2–6 on every PR; stages 7–11 only on merges to `main`/`develop`.
- **Build artifacts**: store the `.deb`/tarball in a central artifact repository (e.g., Nexus, Artifactory, or even a simple S3 bucket), not in Git.

---

## 7. Automated Builds

### What the guide says

An **automated build** means: on every commit, a CI server checks out the code and compiles it in a **clean environment** — not on a developer's laptop. This catches missing dependencies early (the "works on my machine" problem).

### Why it matters for `nr_ue_phy`

The project has two very different build targets:

| Target | Toolchain | Key deps |
|--------|-----------|----------|
| x86 simulation | `gcc`/`clang` | Intel IPP, cJSON, linenoise |
| ARM StarTag | `startag-1.0.1.cmake` toolchain | NXP LA9310 BSP, ARM RAN Accel Lib, FreeRTOS |

Without an automated build server, it is easy for an engineer to have a working local x86 build while accidentally breaking the ARM cross-compile — because they never run it locally.

### What to automate

```bash
# Stage 1: x86 Debug + ASAN (catches memory bugs early)
cmake .. -DCMAKE_BUILD_TYPE=Debug -DUSE_ASAN=On
make -j$(nproc)

# Stage 2: x86 Release (production-equivalent)
cmake ..
make -j$(nproc)

# Stage 3: ARM cross-compile
cmake .. -DCMAKE_TOOLCHAIN_FILE=../toolchains/startag-1.0.1.cmake -DNMM_RF_ACTIVE=On
make package -j$(nproc)
```

### Build artifact versioning

Tag each ARM package with the Git commit hash:

```
uephy-<version>-<git-short-sha>.deb
```

Store in an artifact repo. Never rebuild from source for later stages — promote the same binary.

---

## 8. Automated Testing

### What the guide says

Automated tests form a **pyramid**:

```
        /\
       /  \
      / UI \        ← Few, slow, test whole system (end-to-end)
     /------\
    /  Integ \      ← Medium number, test module interactions
   /----------\
  /  Unit Tests\    ← Many, very fast, test individual functions
 /______________\
```

Run the fast tests first; only run slow tests if fast ones pass.

### The `nr_ue_phy` testing pyramid

```
         /\
        /  \
       / E2E\       ← x86 emulation (uephy + macemu) + HIL on StarTag
      /------\
     / Submod \     ← ctest submodule tests: SYNC, PDSCH, PUSCH, PUCCH chains
    /----------\
   / Component  \   ← ctest component tests: HARQ, rate_matcher, descrambler,
  /  Unit Tests  \     polar coder, CRC, scrambler, equalizer
 /______________\ \
```

#### Unit / Component Tests (fastest — run on every commit)

```bash
# Examples from testcases/components/
ctest -R rate_matcher      # Tests 3GPP TS 38.212 rate matching/recovery
ctest -R harq              # Tests HARQ soft combining
ctest -R descrambler       # Tests PDCCH/PDSCH descrambling
ctest -R polar             # Tests polar encoder/decoder
ctest -R crc               # Tests CRC attachment/check
```

Each test loads a binary test vector, calls the C function under test, and compares output with the expected result.

#### Submodule / Integration Tests (medium — run on main branch pushes)

```bash
# Examples from testcases/submodules/
ctest -R SYNC              # PSS/SSS detection + PBCH decode
ctest -R PDSCH             # Full DL data path: DMRS → channel est → LDPC decode
ctest -R PUSCH             # Full UL encode path
```

These tests wire together multiple modules (e.g., DMRS estimation → equalizer → descrambler → rate recovery → LDPC).

#### End-to-End / Emulation Tests (slowest — run before release)

```bash
# Full uephy + macemu loop over a directory of test vectors
scripts/run_x86_regression.sh build_x86/ ~/workspace/tv/

# Or using the Python automation dashboard
cd scripts/test/submodule/x86_emulation
python3 run_tests.py
python3 dashboard.py   # web dashboard at http://localhost:5050
```

#### What is "continuous testing" for `nr_ue_phy`?

- Every `git push` → stages 2–6 (clang-format + build + component tests) run automatically.
- Merge to `develop`/`main` → additionally runs submodule ctest + x86 regression.
- Sprint release → ARM cross-build + HIL tests.

### Testing special cases in `nr_ue_phy`

| Test type | Tool/flag | What it checks |
|-----------|-----------|----------------|
| Memory safety | `-DUSE_ASAN=On` + Debug build | Buffer overflows, use-after-free (critical: HARQ buffer, LDPC node arrays) |
| FR2 (mmWave) path | `-DNMM_FREQ_RANGE_FR2=On` | Separate test vector set for FR2 subcarrier spacings |
| HARQ debug dump | `-DHARQ_DEBUG_DUMP_EN=1` | Dump soft combining state for regression analysis |
| UL debug dump | `-DUL_DEBUG_DUMP_FLAG=1` | Capture PUSCH intermediate results |

---

## 9. CI/CD Best Practices

### What the guide says (and how it maps to `nr_ue_phy`)

#### ✅ Commit early, commit often
Push at least once a day. If you're working on a big feature (e.g., new PUCCH format), use a feature branch so CI still runs on your partial work.

```
main
  │
  ├── feature/pucch-format3   ← CI runs here too (compile + component tests)
  └── feature/prach-long      ← CI runs here too
```

#### ✅ Keep builds green (shared responsibility)
If `ctest -R SYNC` fails on `main`, **everyone stops** adding new code until it's fixed. The engineer who broke it is not blamed — the team collectively fixes it.

#### ✅ Build only once, promote the same artifact
```
compile ARM package  →  HIL test batch 1  →  HIL test batch 2  →  release
      ↑ same .deb file promoted through every stage — never rebuilt
```

#### ✅ clang-format before every commit
```bash
# Run before pushing:
clang-format -i src/dl/pdsch/dl_harq.c
clang-format -i src/ul/pusch/ul_pusch_encode.c
# Or use a git pre-commit hook
```

The project's `.clang-format` enforces LLVM style with 4-space indent and no column limit.

#### ✅ Streamline tests — run fast tests first
```
clang-format check (< 30s)
    → cmake + make Debug+ASAN (< 3 min)
        → ctest component tests (< 2 min, parallelized)
            → ctest submodule tests (~ 5–10 min)
                → x86 regression (depends on TV count)
                    → ARM cross-build + HIL (manual gate)
```

#### ✅ Secure the pipeline
- Store credentials for the artifact repo and HIL hardware in a secret manager — **never** in `CMakeLists.txt` or git.
- The ARM toolchain `.cmake` file may contain board-specific keys — keep it out of public repositories.
- Apply `-Wall -Wextra -Werror` (already enforced) — compiler warnings as CI failures.

#### ✅ Monitor and measure
Track over time:
- x86 build time
- `ctest` pass rate per module
- x86 regression pass rate per test vector
- HIL BER/BLER metrics after firmware updates

#### ✅ Stick to the process
No "quick fix" bypasses. Even a one-line change to `src/dl/pdcch/pdcch_decoder.c` must go through `clang-format` + compile + ctest. Why? Because a one-line change once broke the DCI blind decoder CRC check and was missed for two weeks.

---

## 10. Benefits of CI/CD

### The guide lists 12 benefits — here are the most relevant for `nr_ue_phy`

| Benefit | What it means for `nr_ue_phy` |
|---------|-------------------------------|
| **Faster feedback** | Know in 5 min if a change broke LDPC decoding, not 2 days later |
| **Better code quality** | ASAN finds buffer overflows in HARQ buffers before they reach hardware |
| **Fewer bugs in hardware** | x86 emulation catches most bugs before an expensive HIL flash cycle |
| **Smoother releases** | ARM build + package is a one-command reproducible step, not a manual script |
| **Less downtime** | If a firmware bug is found on StarTag, the small commit set makes it easy to pinpoint and roll back |
| **Non-functional testing** | Automated performance tests can verify PDSCH throughput and sync acquisition time don't regress |
| **Collaboration** | All engineers see the same CI dashboard — no "it works on my machine" debates |
| **Measurable progress** | Track HARQ ctest pass rate, regression pass rate, and ARM build time trends over sprints |

---

## 11. Putting It All Together — A CI/CD Proposal for `nr_ue_phy`

### Recommended tool: GitHub Actions / GitLab CI / Jenkins

Choose any CI server; the pipeline steps are the same. Below is an example **GitHub Actions** workflow (illustrative):

```yaml
# .github/workflows/ci.yml  (illustrative — adapt paths as needed)
name: nr_ue_phy CI

on:
  push:
    branches: [main, develop, "feature/**"]
  pull_request:

jobs:

  # ── Stage 1: Static analysis (fastest gate) ──────────────────────
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check clang-format
        run: |
          find src lib toplevel -name '*.c' -o -name '*.h' | \
            xargs clang-format --dry-run --Werror

  # ── Stage 2: x86 Debug + ASAN build ──────────────────────────────
  build-debug:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build (Debug + ASAN)
        run: |
          mkdir build && cd build
          cmake .. -DCMAKE_BUILD_TYPE=Debug -DUSE_ASAN=On
          make -j$(nproc)

  # ── Stage 3: Component unit tests ────────────────────────────────
  ctest-components:
    needs: build-debug
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build + Run component tests
        run: |
          mkdir build && cd build
          cmake .. -DCMAKE_BUILD_TYPE=Debug -DUSE_ASAN=On
          make -j$(nproc)
          ctest --output-on-failure -j$(nproc) \
            -R "rate_matcher|harq|descrambler|polar|crc|scrambler"

  # ── Stage 4: x86 Release build + submodule tests ─────────────────
  ctest-submodules:
    needs: ctest-components
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Release + Run submodule tests
        run: |
          mkdir build && cd build
          cmake ..
          make -j$(nproc)
          ctest --output-on-failure -j$(nproc) \
            -R "SYNC|PDSCH|PUSCH|PUCCH|PDCCH"

  # ── Stage 5: x86 regression (on main/develop only) ───────────────
  x86-regression:
    needs: ctest-submodules
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: x86 End-to-End Regression
        run: |
          mkdir build && cd build && cmake .. && make -j$(nproc)
          cd ..
          scripts/run_x86_regression.sh build/ $TV_DIR
        env:
          TV_DIR: /path/to/test-vectors  # mounted or downloaded

  # ── Stage 6: ARM cross-compile + package (on main only) ──────────
  arm-package:
    needs: x86-regression
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: ARM cross-compile
        run: |
          mkdir build_arm && cd build_arm
          cmake .. \
            -DCMAKE_TOOLCHAIN_FILE=../toolchains/startag-1.0.1.cmake \
            -DNMM_RF_ACTIVE=On
          make package -j$(nproc)
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: uephy-arm-package
          path: build_arm/*.deb

  # ── Stage 7: Hardware-in-the-Loop (manual trigger) ───────────────
  # This stage is triggered manually by an engineer via workflow_dispatch
  # after reviewing the ARM package artifact above.
```

### Summary diagram of the full flow

```
Developer workstation
│
│  git push feature/fix-harq-cbg
│
▼
GitHub / GitLab CI server
│
├── [lint]            clang-format check        ~30s   ← blocks on failure
├── [build-debug]     cmake Debug+ASAN           ~3min  ← blocks on failure
├── [ctest-comp]      component unit tests       ~2min  ← blocks on failure
├── [ctest-sub]       submodule integration      ~8min  ← blocks on failure
├── [x86-regression]  uephy+macemu end-to-end    ~15min ← main/develop only
├── [arm-package]     ARM cross-compile+package  ~5min  ← main only
│
└── 📦 Artifact stored in repo
         │
         │  Engineer reviews, approves
         ▼
    [HIL test on StarTag hardware]
         │
         ▼
    Release tag + changelog
```

### What you gain from this pipeline

- A regression in the HARQ combining logic is caught by `ctest -R harq` in **under 5 minutes** instead of days.
- ARM cross-compile breakages are caught automatically — no more "it compiled on my ARM machine" surprises.
- The exact ARM `.deb` used in HIL testing is the same one released — no re-compilation risk.
- `clang-format` violations never reach code review — they fail CI immediately.
- ASAN catches stack/heap bugs that are invisible on x86 Release builds before they appear on hardware.

---

## Quick Reference: Key Commands in the Pipeline

```bash
# Lint check (CI stage 1)
find src lib toplevel -name '*.c' -o -name '*.h' | xargs clang-format --dry-run --Werror

# x86 Debug + ASAN build (CI stage 2)
cmake .. -DCMAKE_BUILD_TYPE=Debug -DUSE_ASAN=On && make -j$(nproc)

# Component unit tests (CI stage 3)
ctest --output-on-failure -j$(nproc) -R "rate_matcher|harq|descrambler|polar|crc"

# x86 Release build + submodule tests (CI stage 4)
cmake .. && make -j$(nproc)
ctest --output-on-failure -j$(nproc) -R "SYNC|PDSCH|PUSCH|PUCCH|PDCCH"

# x86 end-to-end regression (CI stage 5)
scripts/run_x86_regression.sh build/ ~/workspace/tv/

# ARM cross-compile and package (CI stage 6)
cmake .. -DCMAKE_TOOLCHAIN_FILE=../toolchains/startag-1.0.1.cmake -DNMM_RF_ACTIVE=On
make package -j$(nproc)
```

---

## 12. TeamCity — Architecture and Core Concepts

> This section is specific to **TeamCity**. The pipeline stages in Section 6 are tool-agnostic; here we show exactly how to express them in TeamCity's own model.

### 12.1 How TeamCity is Structured

```
┌──────────────────────────────────────────────────────┐
│                  TeamCity Server                     │
│  (Web UI, project config, build queue, VCS polling)  │
└────────────────────┬─────────────────────────────────┘
                     │  HTTP polling (agent → server)
          ┌──────────┼──────────┐
          ▼          ▼          ▼
   ┌──────────┐ ┌──────────┐ ┌──────────────────────┐
   │  Agent 1 │ │  Agent 2 │ │       Agent 3        │
   │  x86     │ │  x86     │ │  ARM cross-compile   │
   │  Ubuntu  │ │  Ubuntu  │ │  (ARM toolchain      │
   │  Debug   │ │  Release │ │   installed)         │
   └──────────┘ └──────────┘ └──────────────────────┘
```

| TeamCity concept | What it means | `nr_ue_phy` example |
|-----------------|---------------|----------------------|
| **Server** | Central web UI + scheduler + VCS watcher | One machine running TeamCity, watching the Git repo |
| **Build Agent** | A machine (or container) that actually runs build steps | x86 Ubuntu agent, ARM cross-compile agent |
| **Project** | Top-level grouping of related build configurations | `nr_ue_phy` project |
| **Build Configuration** | A named set of steps + triggers (like a "job") | `Lint`, `Build-Debug`, `CTest-Components`, etc. |
| **Build Chain** | A sequence of Build Configurations linked by Snapshot Dependencies — TeamCity's word for a **pipeline** | All 7 stages linked together |
| **VCS Root** | The Git repo URL + branch + credentials | `ssh://git@<host>/nr_ue_phy.git`, branch `main` |
| **Build Trigger** | What starts a build (e.g., VCS change, schedule, manual) | "Trigger on every push to `main` or `feature/**`" |
| **Artifact** | Files published by a build step for use by downstream builds | `build_arm/*.deb`, `ctest` XML reports |
| **Snapshot Dependency** | "Run Build B only after Build A finishes successfully, using the **same source revision**" | ARM package only runs after x86 regression passes |
| **Artifact Dependency** | "Download the output files of Build A before running Build B" | HIL test downloads the `.deb` produced by ARM build |
| **Agent Requirement** | A rule that says "this build must run on an agent with property X" | ARM build requires `env.ARM_TOOLCHAIN_PATH` to be set |
| **Build Parameter** | A variable passed into build steps | `%env.TV_DIR%` pointing to test vector directory |

---

### 12.2 Build Chain = TeamCity's Pipeline

In TeamCity, a **Build Chain** is built by setting **Snapshot Dependencies** between Build Configurations. The chain visualizer shows the pipeline as a graph in the web UI.

```
[Lint] ──► [Build-Debug-ASAN] ──► [CTest-Components] ──► [CTest-Submodules]
                                                                   │
                                                                   ▼
                                                         [x86-Regression]
                                                                   │
                                                                   ▼
                                                         [ARM-CrossCompile]
                                                                   │
                                                             (Manual gate)
                                                                   │
                                                                   ▼
                                                             [HIL-Test]
```

Each arrow = a **Snapshot Dependency** with "Do not run new build if there is a suitable one" + "Only use successful builds from suitable ones".

---

### 12.3 Kotlin DSL — Configuration as Code

TeamCity stores all project settings in a `.teamcity/` folder as **Kotlin DSL** (`.kts` files). This means your pipeline is **version-controlled alongside your source code** — any change to the pipeline goes through a code review, just like a source code change.

Below is the full `nr_ue_phy` pipeline expressed as TeamCity Kotlin DSL:

```kotlin
// .teamcity/settings.kts
import jetbrains.buildServer.configs.kotlin.*
import jetbrains.buildServer.configs.kotlin.buildSteps.script
import jetbrains.buildServer.configs.kotlin.triggers.vcs
import jetbrains.buildServer.configs.kotlin.buildFeatures.swabra

version = "2025.11"

project {
    buildType(Lint)
    buildType(BuildDebugAsan)
    buildType(CtestComponents)
    buildType(CtestSubmodules)
    buildType(X86Regression)
    buildType(ArmCrossCompile)
    buildType(HilTest)
}

// ── Stage 1: clang-format lint ────────────────────────────────────────────────
object Lint : BuildType({
    name = "1. Lint (clang-format)"
    description = "Check all C source files comply with .clang-format rules"

    vcs { root(DslContext.settingsRoot) }

    triggers {
        vcs {
            branchFilter = "+:*"          // run on every branch
        }
    }

    steps {
        script {
            name = "clang-format check"
            scriptContent = """
                find src lib toplevel -name '*.c' -o -name '*.h' | \
                    xargs clang-format --dry-run --Werror
            """.trimIndent()
        }
    }
})

// ── Stage 2: x86 Debug + ASAN build ──────────────────────────────────────────
object BuildDebugAsan : BuildType({
    name = "2. Build x86 Debug+ASAN"

    vcs { root(DslContext.settingsRoot) }

    dependencies {
        snapshot(Lint) {
            onDependencyFailure = FailureAction.FAIL_TO_START
        }
    }

    steps {
        script {
            name = "cmake configure"
            scriptContent = "cmake -S . -B build_debug -DCMAKE_BUILD_TYPE=Debug -DUSE_ASAN=On"
        }
        script {
            name = "make"
            scriptContent = "make -C build_debug -j\$(nproc)"
        }
    }

    // Publish the build directory so downstream steps can download it
    artifactRules = "build_debug/** => build_debug.zip"
})

// ── Stage 3: Component unit tests ────────────────────────────────────────────
object CtestComponents : BuildType({
    name = "3. CTest Components"

    vcs { root(DslContext.settingsRoot) }

    dependencies {
        snapshot(BuildDebugAsan) {
            onDependencyFailure = FailureAction.FAIL_TO_START
        }
        // Download the compiled tree from stage 2
        artifacts(BuildDebugAsan) {
            artifactRules = "build_debug.zip!** => build_debug"
        }
    }

    steps {
        script {
            name = "Run component tests"
            scriptContent = """
                ctest --test-dir build_debug \
                      --output-on-failure \
                      -j\$(nproc) \
                      -R "rate_matcher|harq|descrambler|polar|crc|scrambler|equalizer"
            """.trimIndent()
        }
    }

    // Publish JUnit-style XML test results (TeamCity auto-parses these)
    artifactRules = "build_debug/Testing/**/*.xml => test-results"
})

// ── Stage 4: x86 Release build + submodule tests ─────────────────────────────
object CtestSubmodules : BuildType({
    name = "4. CTest Submodules (Release)"

    vcs { root(DslContext.settingsRoot) }

    dependencies {
        snapshot(CtestComponents) {
            onDependencyFailure = FailureAction.FAIL_TO_START
        }
    }

    steps {
        script {
            name = "cmake Release configure"
            scriptContent = "cmake -S . -B build_release"
        }
        script {
            name = "make Release"
            scriptContent = "make -C build_release -j\$(nproc)"
        }
        script {
            name = "Run submodule tests"
            scriptContent = """
                ctest --test-dir build_release \
                      --output-on-failure \
                      -j\$(nproc) \
                      -R "SYNC|PDSCH|PUSCH|PUCCH|PDCCH"
            """.trimIndent()
        }
    }

    artifactRules = "build_release/** => build_release.zip"
})

// ── Stage 5: x86 end-to-end regression ───────────────────────────────────────
object X86Regression : BuildType({
    name = "5. x86 Regression"

    // Only run on main and develop; skip feature branches
    vcs {
        root(DslContext.settingsRoot)
        branchFilter = "+:main\n+:develop"
    }

    dependencies {
        snapshot(CtestSubmodules) {
            onDependencyFailure = FailureAction.FAIL_TO_START
        }
        artifacts(CtestSubmodules) {
            artifactRules = "build_release.zip!** => build_release"
        }
    }

    params {
        param("env.TV_DIR", "/home/teamcity/workspace/tv")   // path to test vectors on agent
    }

    steps {
        script {
            name = "Run x86 regression"
            scriptContent = "scripts/run_x86_regression.sh build_release %env.TV_DIR%"
        }
    }
})

// ── Stage 6: ARM cross-compile and package ────────────────────────────────────
object ArmCrossCompile : BuildType({
    name = "6. ARM Cross-Compile + Package"

    vcs {
        root(DslContext.settingsRoot)
        branchFilter = "+:main"      // only on main
    }

    dependencies {
        snapshot(X86Regression) {
            onDependencyFailure = FailureAction.FAIL_TO_START
        }
    }

    // This build config must run on the ARM cross-compile agent
    requirements {
        exists("env.ARM_TOOLCHAIN_PATH")   // agent must have the StarTag toolchain
    }

    steps {
        script {
            name = "cmake ARM configure"
            scriptContent = """
                cmake -S . -B build_arm \
                    -DCMAKE_TOOLCHAIN_FILE=toolchains/startag-1.0.1.cmake \
                    -DNMM_RF_ACTIVE=On
            """.trimIndent()
        }
        script {
            name = "make package"
            scriptContent = "make -C build_arm package -j\$(nproc)"
        }
    }

    // Publish the .deb package as a build artifact
    artifactRules = "build_arm/*.deb => packages"
})

// ── Stage 7: Hardware-in-the-Loop (manual trigger) ───────────────────────────
object HilTest : BuildType({
    name = "7. HIL Test (StarTag hardware)"
    description = "Flash ARM package to StarTag and run RF test vectors — triggered manually"

    vcs { root(DslContext.settingsRoot) }

    dependencies {
        snapshot(ArmCrossCompile) {
            onDependencyFailure = FailureAction.FAIL_TO_START
            // Do NOT add a VCS trigger here — manual trigger only
        }
        artifacts(ArmCrossCompile) {
            artifactRules = "packages/*.deb => firmware"    // download the .deb
        }
    }

    // Must run on the agent physically connected to the StarTag board
    requirements {
        exists("env.STARTAG_CONNECTED")
    }

    steps {
        script {
            name = "Flash firmware to StarTag"
            scriptContent = "sshpass -p %env.BOARD_PASS% scp firmware/*.deb root@%env.BOARD_IP%:/tmp/"
        }
        script {
            name = "Install and run HIL tests"
            scriptContent = """
                ssh root@%env.BOARD_IP% "dpkg -i /tmp/*.deb && systemctl restart uephy"
                python3 scripts/test/submodule/x86_emulation/run_tests.py --hil
            """.trimIndent()
        }
    }
})
```

---

### 12.4 TeamCity-Specific Features Used in This Pipeline

| Feature | Where used in `nr_ue_phy` pipeline | Why it matters |
|---------|-------------------------------------|----------------|
| **Build Chain / Snapshot Dependencies** | All 7 stages linked | Guarantees every stage uses the **same Git revision** — no "built from slightly different code" bugs |
| **Artifact Dependencies** | Stages 3, 5, 7 download outputs of 2, 4, 6 | The same compiled binary is promoted through stages — never rebuilt |
| **VCS Triggers with branch filter** | Stages 1–4 run on all branches; 5–6 only on `main`/`develop` | Feature branch PRs get fast feedback (stages 1–4); full pipeline only on integration branches |
| **Agent Requirements** | Stage 6 requires `env.ARM_TOOLCHAIN_PATH`; Stage 7 requires `env.STARTAG_CONNECTED` | Ensures ARM builds only run on a machine with the StarTag toolchain installed |
| **Build Parameters** | `%env.TV_DIR%`, `%env.BOARD_IP%`, `%env.BOARD_PASS%` | Credentials and paths are stored in TeamCity's **secret parameters** (masked in logs), never in source code |
| **Kotlin DSL** | Entire pipeline in `.teamcity/settings.kts` | Pipeline config is version-controlled; changes to it go through code review like any source change |
| **Swabra build feature** | Can add to each build type | Cleans leftover files from previous builds on the agent — important for a reliable ASAN build |
| **Test reporting** | `ctest --output-on-failure` + TeamCity auto-parses XML | Test results appear in the TeamCity UI with pass/fail per test name; history and flaky test detection built in |
| **Manual trigger (no VCS trigger on HIL)** | Stage 7 has no VCS trigger | An engineer clicks "Run" on the HIL stage in the UI after reviewing the ARM artifact |
| **Build promotion** | From the TeamCity UI: click "Run" on HIL stage, it pulls the artifact from Stage 6 | One-click firmware flash + test cycle without re-running earlier stages |

---

### 12.5 TeamCity Server + Agent Setup for `nr_ue_phy`

```
TeamCity Server (one machine, any Linux/Windows)
│
├── Agent Pool: "x86-linux"
│     ├── Agent A  (Ubuntu, gcc, cmake, Intel IPP)   ← runs stages 1–5
│     └── Agent B  (Ubuntu, gcc, cmake, Intel IPP)   ← parallel runs
│
└── Agent Pool: "arm-crosscompile"
      └── Agent C  (Ubuntu, StarTag toolchain installed,
                    env.ARM_TOOLCHAIN_PATH=/opt/startag/...)  ← stage 6 only

Physical lab bench (not a TeamCity agent in the normal sense):
      └── Agent D  (connected to StarTag board via USB/JTAG,
                    env.STARTAG_CONNECTED=true,
                    env.BOARD_IP=192.168.1.10)  ← stage 7 only
```

**How agent routing works:**

TeamCity matches a Build Configuration's `requirements {}` block against each agent's reported properties. Stage 6 asks for `env.ARM_TOOLCHAIN_PATH` — only Agent C has that property set, so it automatically runs on Agent C. Stage 7 asks for `env.STARTAG_CONNECTED` — only Agent D has it.

---

### 12.6 Comparison: TeamCity vs. GitHub Actions vs. Jenkins

| Aspect | TeamCity | GitHub Actions | Jenkins |
|--------|----------|----------------|---------|
| **Pipeline definition** | Kotlin DSL (`.teamcity/settings.kts`) or XML | YAML (`.github/workflows/`) | Groovy (`Jenkinsfile`) |
| **Pipeline UI** | Rich visual Build Chain graph built in | Basic — third-party plugins needed | Blue Ocean plugin adds visuals |
| **Agent model** | Server polls agents (agent initiates connection) | GitHub-hosted runners or self-hosted | Master/Agent (server pushes to agent) |
| **Agent routing** | `requirements {}` block matches agent properties | `runs-on: [self-hosted, arm]` labels | `label 'arm'` in Jenkinsfile |
| **Artifact handling** | Built-in artifact publishing + artifact deps | `actions/upload-artifact` / `download-artifact` | `archiveArtifacts` + `copyArtifacts` plugin |
| **Test reporting** | Auto-detects JUnit XML; flaky test detection built in | Requires third-party action | JUnit plugin |
| **Secret management** | Built-in typed parameters (password type masked) | GitHub Secrets | Credentials plugin |
| **Pricing** | Free up to 3 agents; paid above that | Free for public repos; pay per minute for private | Free and open-source; host yourself |
| **Best for `nr_ue_phy`** | ✅ If self-hosting; great for embedded/hardware pipelines | ✅ If repo is on GitHub and no on-prem hardware agents | ✅ Very common in embedded/automotive; maximum flexibility |

---

## 13. Interview Questions — CI/CD Pipeline (General)

### Conceptual

**Q1. What is the difference between Continuous Integration, Continuous Delivery, and Continuous Deployment?**

> - **CI**: Auto-build and auto-test on every commit. Goal: fast feedback (minutes).
> - **Continuous Delivery**: CI + auto-deploy to staging environments + further automated tests. Release to production is a **manual** decision.
> - **Continuous Deployment**: Same as delivery, but the final release to production is also **automatic** — no human approval needed.
>
> In `nr_ue_phy`: we use CI (compile + ctest on every push) and Continuous Delivery (a human engineer approves the ARM firmware flash to the StarTag board).

---

**Q2. What is a CI/CD pipeline? Describe its stages.**

> A pipeline is the automated chain of steps code goes through from commit to release. Typical stages:
> 1. Source code triggers (VCS push)
> 2. Static analysis / linting
> 3. Build (compile)
> 4. Unit / component tests (fast)
> 5. Integration / submodule tests (slower)
> 6. Staging deployment + performance / security tests
> 7. Manual or automatic release to production
>
> Each stage gates the next — a failure stops the chain and notifies the team.

---

**Q3. What is "fail fast" and why is it important?**

> Run the cheapest, fastest tests first. If the code doesn't even compile, there is no point running the 30-minute PDSCH submodule test. Developers get feedback in 2 minutes (lint + build) instead of waiting 45 minutes for the full regression to finish before finding out the obvious error.

---

**Q4. What is "build once, promote the same artifact"? Why not rebuild at each stage?**

> Compile the binary **once**. Pass that exact binary through unit tests → integration tests → staging → production.
>
> If you rebuild from source at each stage, you risk subtle differences (different build machine, slightly different timestamp, different compiler optimization state). "It passed unit tests" should mean the **exact same binary** was used in integration tests — not a rebuilt copy.
>
> In `nr_ue_phy`: we cross-compile the ARM `.deb` once in Stage 6 and the exact same file is flashed to the StarTag in Stage 7.

---

**Q5. What are feature flags and feature branches? When do you use each?**

> - **Feature branch**: develop a new feature in a separate Git branch. CI still runs on it (compile + fast tests), but it doesn't merge to main until complete. Lower risk of breaking main for others.
> - **Feature flag**: merge code to main but hide it behind a runtime toggle (`#ifdef NR_FEATURE_FR2` or a config parameter). The code is live and tested by CI, but users can't see/use it until the flag is flipped.
>
> Feature flags are more powerful (the code is actually integrated and exercised) but harder to maintain. Feature branches are simpler.

---

**Q6. What is configuration drift and how do you avoid it?**

> If you keep test environments running for a long time, manual changes accumulate (someone installs a library, a config file gets edited). Over time the environment no longer matches what it was when the test passed. This causes "it fails in CI but passes locally."
>
> Fix: **infrastructure-as-code** — script the creation of test environments. Tear them down and recreate them for each pipeline run using Docker containers or VM snapshots. In `nr_ue_phy`, this means the x86 build environment is a fresh Docker container every run.

---

**Q7. What are the testing pyramid levels? Why run unit tests before integration tests?**

> From bottom to top: Unit → Integration → End-to-End.
>
> - Unit tests: test one function in isolation. Very fast (milliseconds). Hundreds of them.
> - Integration tests: test two or more modules together. Slower (seconds to minutes).
> - End-to-end: test the whole system. Slowest (minutes to hours).
>
> Run bottom-to-top because: if a unit test fails, there is no point wasting time running slow end-to-end tests on broken code.

---

**Q8. How do you handle a "flaky test" (a test that sometimes passes, sometimes fails)?**

> A flaky test undermines trust in the CI pipeline — when it fails, people ignore it ("it's just flaky"). Steps to handle it:
> 1. Tag it as known-flaky so it doesn't block the pipeline while under investigation.
> 2. Investigate: is it a timing issue, a race condition, a non-deterministic test input, or a genuine intermittent bug?
> 3. Fix the root cause or make the test deterministic.
> 4. Never permanently ignore a flaky test — it may be hiding a real bug.

---

**Q9. Why is it important not to bypass the CI pipeline for "urgent" or "trivial" fixes?**

> Because:
> - "Trivial" changes have broken production before (a one-line null-pointer dereference, a missing `break` in a switch statement).
> - A bug released without automated tests is harder to reproduce and debug than one caught in CI.
> - Bypassing creates a culture where people regularly skip CI, which defeats its purpose.
> - The automated pipeline is often faster than manual review for simple bugs.

---

**Q10. What is DevSecOps? How does it apply to a firmware project like `nr_ue_phy`?**

> DevSecOps = weaving security checks into the CI/CD pipeline from the start, rather than a manual security audit at the end.
>
> For `nr_ue_phy`:
> - Run `cppcheck` or `clang-tidy` as a CI gate for known unsafe patterns (buffer overflows, unchecked `malloc` return values).
> - Build with `-DUSE_ASAN=On` to catch memory safety bugs before they reach hardware.
> - Check third-party dependencies (cJSON, NXP BSP) for known CVEs in CI.
> - Store board credentials (`BOARD_PASS`, SSH keys) in a secret manager — never in Git.
> - Apply principle of least privilege: the CI agent that flashes the board should not have write access to the source repository.

---

## 14. Interview Questions — TeamCity Specific

### Architecture

**Q1. Explain the TeamCity architecture. What is a Server, a Build Agent, and how do they communicate?**

> - **TeamCity Server**: central web application (runs on Tomcat/JVM). It stores project configuration, monitors VCS for changes, manages the build queue, and presents the UI.
> - **Build Agent**: a separate machine (or Docker container) that actually executes build steps. It connects **outward** to the server via HTTP polling — the agent asks "do you have a build for me?" periodically.
> - This **unidirectional agent-to-server** connection means agents can be behind a firewall without the server needing to reach into the network.
> - A single TeamCity server can manage thousands of agents. Each agent runs one build at a time.

---

**Q2. What is a Build Chain in TeamCity? How is it different from a simple Build Configuration?**

> - A **Build Configuration** is a single named job: a set of steps, a VCS root, and triggers.
> - A **Build Chain** is multiple Build Configurations linked by **Snapshot Dependencies**, forming a directed acyclic graph (pipeline).
> - Key property of a snapshot dependency: all builds in the chain use the **exact same source revision** — no "build A compiled from commit X, but build B compiled from commit Y" bugs.
> - TeamCity visualizes the chain as a graph in the web UI, showing which stage is green/red/running.
>
> In `nr_ue_phy`: our 7-stage pipeline (Lint → Debug+ASAN → CTest-Comp → CTest-Sub → x86-Regression → ARM-Package → HIL) is a Build Chain. Each arrow is a Snapshot Dependency with "fail to start if dependency fails."

---

**Q3. What is the difference between a Snapshot Dependency and an Artifact Dependency?**

> - **Snapshot Dependency**: "Run Build B only after Build A passes, **and use the same Git revision** for both." Controls execution order and source synchronization.
> - **Artifact Dependency**: "Before starting Build B, **download the output files** (artifacts) from Build A." Controls file transfer between stages.
>
> You typically use **both together**: Snapshot Dependency ensures correct ordering + same revision; Artifact Dependency ensures the downstream stage gets the compiled binary from the upstream stage rather than recompiling from scratch.

---

**Q4. What is Kotlin DSL in TeamCity? Why would you use it instead of the web UI?**

> Kotlin DSL is TeamCity's **Configuration-as-Code** approach. Instead of clicking through the web UI, you define all project settings in `.teamcity/settings.kts` files (Kotlin code) stored in your Git repository.
>
> Benefits:
> - Pipeline changes go through **code review** like any source change.
> - You can use IDE autocompletion (IntelliJ IDEA) when editing the DSL.
> - Branching and reuse: define a base `BuildType` class and inherit from it for multiple similar stages.
> - Audit trail: Git log shows who changed what in the pipeline and why.
>
> In `nr_ue_phy`: the entire 7-stage pipeline is expressed in `.teamcity/settings.kts`. If an engineer wants to add a new test stage, they open a PR — the pipeline change goes through the same review as the source change.

---

**Q5. How do Agent Requirements work in TeamCity? Give an example.**

> An **Agent Requirement** in a Build Configuration says "this build must only run on an agent that has property X with value Y." TeamCity compares requirements against each agent's reported properties and only dispatches the build to a matching agent.
>
> Example for `nr_ue_phy`:
> ```kotlin
> requirements {
>     exists("env.ARM_TOOLCHAIN_PATH")   // only agents with the StarTag toolchain
> }
> ```
> The ARM cross-compile agent has `ARM_TOOLCHAIN_PATH=/opt/startag/...` in its `buildAgent.properties`. x86 agents do not. So the ARM build configuration automatically runs on the right machine.

---

**Q6. How do Build Parameters work in TeamCity? How do you handle secrets?**

> **Build Parameters** are variables accessible in build steps as `%param.name%`. They can be:
> - **Configuration parameters**: read-only properties (`teamcity.*` namespace)
> - **System properties**: passed as system properties to the build runner (`system.NAME`)
> - **Environment variables**: injected as `env.NAME` — accessible in shell scripts as `$NAME`
>
> For **secrets** (passwords, API keys, board credentials):
> - Define them as a **password-type parameter** in TeamCity.
> - TeamCity automatically **masks** the value in all build logs (shows `******`).
> - Never store secrets in the Kotlin DSL or in Git. Define them in the TeamCity UI under project parameters with type `password`.
>
> In `nr_ue_phy`: `%env.BOARD_PASS%` (SSH password for StarTag) is a password-type parameter — visible to the build step but never printed in logs.

---

**Q7. What is a VCS Root in TeamCity? What triggers can you configure?**

> A **VCS Root** is a configured connection to a version control system (Git, Perforce, SVN, etc.). It specifies:
> - Repository URL
> - Branch specification (e.g., `+:refs/heads/*` to watch all branches)
> - Credentials (SSH key or username/password)
> - Polling interval (how often TeamCity checks for new commits)
>
> **Triggers** on a Build Configuration:
> - **VCS Trigger**: start a build when a new commit is detected in the VCS Root. Can be filtered by branch pattern.
> - **Schedule Trigger**: run at a specific time (e.g., nightly ARM build).
> - **Finish Build Trigger**: start Build B automatically when Build A finishes (alternative to Snapshot Dependencies for looser coupling).
> - **Manual**: no automatic trigger — someone clicks "Run" in the UI.
>
> In `nr_ue_phy`: Lint through CTest-Submodules have VCS triggers on `+:*` (all branches). x86 Regression has VCS trigger only on `+:main` and `+:develop`. HIL has no trigger — manual only.

---

**Q8. What happens if a build in the middle of a chain fails? Does TeamCity re-run the whole chain?**

> With Snapshot Dependencies set to `onDependencyFailure = FailureAction.FAIL_TO_START`, the downstream stages are **cancelled** (not started) rather than failing. They show as "cancelled: dependency failed" in the UI.
>
> When the engineer fixes the issue and commits a fix:
> - TeamCity detects the new commit.
> - The **whole chain restarts from the beginning** using the new revision.
> - TeamCity will **reuse suitable builds** from a previous successful chain if nothing changed in a stage's inputs (this is the "suitable build" optimization — avoids re-running e.g. the ARM cross-compile if nothing changed since last time).

---

**Q9. What is "Build Promotion" in TeamCity? When would you use it?**

> **Build Promotion** means taking a specific, already-built artifact from an earlier stage and "promoting" it to run a later stage — **without re-running the earlier stages**.
>
> Example: the ARM `.deb` from last Tuesday's nightly build passed x86 regression but the HIL test slot was only available today. You "promote" that Tuesday build to the HIL stage — it downloads the old artifact and runs the hardware test.
>
> This is useful in `nr_ue_phy` when HIL hardware is scarce: you might run 10 ARM builds, queue them, and then promote each one through HIL testing in batch over the weekend.

---

**Q10. How would you set up TeamCity to build and test `nr_ue_phy` for both x86 and ARM without rebuilding from source twice?**

> 1. **Stage 1–5**: x86 build chain with VCS trigger. Publishes `build_release.zip` as a build artifact.
> 2. **Stage 6**: ARM Build Configuration with a **Snapshot Dependency** on Stage 5 (same Git revision guaranteed) and an **Artifact Dependency** on Stage 4 (downloads x86 release artifact to verify the source is good — not reused for ARM, but proves the codebase is healthy).
> 3. The ARM stage has its own steps: `cmake -DCMAKE_TOOLCHAIN_FILE=...` + `make package`. It publishes `build_arm/*.deb`.
> 4. **Stage 7 (HIL)**: has an Artifact Dependency on Stage 6 — downloads the `.deb`. No source build happens here.
> 5. Agent Requirements ensure Stage 6 runs only on the agent with the ARM toolchain, and Stage 7 only on the agent connected to the StarTag board.
>
> Result: x86 source is compiled once (Stage 2); ARM source is compiled once (Stage 6); the exact ARM `.deb` is flashed in Stage 7 — **nothing is rebuilt**.

---

**Q11. What metrics would you track in TeamCity to improve the `nr_ue_phy` pipeline over time?**

> - **Build duration per stage**: if CTest-Submodules suddenly takes 20 minutes instead of 8, something is wrong.
> - **Build success rate per stage**: a stage that fails 30% of the time has a reliability problem — fix the test or fix the code.
> - **Queue time**: if builds wait 40 minutes in the queue, you need more agents.
> - **Test pass rate per test name**: a PDSCH test that fails sporadically is a flaky test — investigate.
> - **Code coverage trend** (if enabled): is coverage growing or shrinking over sprints?
> - **Time from commit to HIL result**: the end-to-end lead time. Reducing this is the top CI/CD metric.

---

*Source: [JetBrains TeamCity CI/CD Ultimate Guide](https://www.jetbrains.com/teamcity/ci-cd-guide/) and [TeamCity Documentation](https://www.jetbrains.com/help/teamcity/) — adapted for the `nr_ue_phy` 5G NR UE PHY project.*
