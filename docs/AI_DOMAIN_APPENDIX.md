# AI Tooling — Domain Appendix (`nr_ue_phy`)

The `nr_ue_phy`-specific instances of every pattern in
[AI_GENERIC_GUIDE.md](AI_GENERIC_GUIDE.md). Kept faithful to the live config so a sibling
5G-PHY project can copy and trim. For an unrelated project, read this as a worked example
of how to populate the generic guide.

**Project:** a 3GPP 5G New Radio (NR) UE physical layer. Real-time DSP: timing is
unforgiving, math is heavy, undefined behaviour is fatal. The rules below are
review-blocking, not advisory.

- **Ticket prefix:** `NRUEL1-` (YouTrack). **Default branch:** `master`.

---

## 1. Commit Module Prefixes

```
sync:    — PSS/SSS/PBCH/cell search
pdcch:   — PDCCH/DCI
pdsch:   — PDSCH/HARQ/DLSCH
pusch:   — PUSCH/ULSCH
pucch:   — PUCCH
prach:   — PRACH
cn:      — Common NR algorithms (LDPC, polar, CRC, rate matching)
lib:     — Platform libraries (x86, ARM, IPP)
dfe:     — DFE/RF interface
macemu:  — MAC emulator
test:    — Test cases and infrastructure
build:   — CMake, toolchain, CI
scripts: — Automation scripts
```

Examples: `pdsch: fix HARQ soft-combining for retransmission RV2` ·
`cn: optimize LDPC decoder early termination` ·
`test: add PUSCH DMRS test vectors for SCS 30kHz`.

---

## 2. C Conventions — The Critical Path (`src/CLAUDE.md`)

### Architecture & memory
- **No malloc on the critical path.** `malloc`/`calloc`/`free` are forbidden in the
  real-time loop (slot-based processing, RX/TX threads). Allocate all buffers at init.
- **Ownership.** Whoever `malloc`s a resource is solely responsible for `free`ing it;
  zero the pointer immediately after.
- **Module prefix mandatory.** Prefix every non-`static` function/struct/macro with the
  owning module. Library prefixes: `cn_*`, `dl_*`, `ul_*`, `parser_*`, `queue*`.
  Channel-model submodules: `tdl_*`, `awgn_*`, `rng_*`. No bare verbs at global scope.
- **Struct naming.** `typedef struct` uses `UpperCamelCase` with a leading-underscore tag
  (`_DlPdsch_Config`) and a plain `UpperCamelCase` typedef (`DlPdsch_Config`). Custom
  numeric types follow `nr_<type>_t` (`nr_ci16_t`, `nr_cf32_t`).
- **Formatting.** `.clang-format` at repo root (LLVM style, 4-space indent, no column
  limit). Run before every commit; CI flags divergence.
- **Opaque pointers.** Hide struct definitions in `.c` files for long-lived heap handles
  whose size the caller never needs. Do **not** hide stack-allocated structs — that
  forces heap use and breaks the no-malloc rule.

### DSP, data & binary formats
- **Table-drive duplicated logic.** Two functions differing only by a data table
  (delays, gains, K-factor) → shared generator + profile struct.
- **Versioned binary formats.** Describe on-disk formats (IQ captures, test vectors) as a
  C struct at the top of both writer and reader, with a `uint32_t version` at offset 0.
- **SIMD & math types.** Isolate AVX2/AVX-512/NEON intrinsics in their own files or behind
  abstraction macros. `int16_t`/`int32_t` for Q-format fixed-point; `float`/`double
  complex` only where strictly necessary.

### Control flow & error handling
- **`goto function_exit;`** — single label for error paths; keep the existing label name.
- **Return codes.** Integer functions return `< 0` on error, `0` on success;
  pointer-returning functions return `NULL`. Return data via pointer arguments.
- **CLI parsing.** Use `getopt_long` or a flag table beyond two flags — not a `strcmp`
  chain (hard to extend, silently rejects typos).

### Tests
- **Assert behaviour, not tables.** `assert(taps[3] == -13.4)` re-copying production data
  catches zero bugs — drop it.
- **Shared defaults.** One set of test constants (`TEST_FS_HZ`, `TEST_DS_NORM_S`, …) at
  the top; never repeat a literal.
- **Float equality** uses an `ASSERT_NEAR`-style helper, never `==` on `double`/`float`.

### Coding standards (`.claude/rules/coding-standards.md`)
4-space indent, no tabs, no column limit, right-aligned pointers (`int *ptr`),
clang-format before commit. Functions/files `snake_case`; types `snake_case_t`;
macros/constants `UPPER_SNAKE_CASE`. Platform-specific code in `lib/`, never `src/`. No
SIMD intrinsics in `src/` — use `cn_*` abstractions. Threads communicate only via ICM
message queues. Public APIs declared in `inc/`. Stack-allocate where possible; check every
`malloc`; free in the allocating module; validate with AddressSanitizer. Int status codes
(`0` ok, `< 0` error); log via `logger.h` macros, never `printf`; never ignore an error
return. Reference the spec section for non-obvious calculations
(`// TS 38.211 Table 7.4.1.1.2-1`).

---

## 3. Python Conventions (`scripts/CLAUDE.md`)

Three sub-projects at different maturity:
- **`scripts/test/rf_test/`** — modern: Python 3.11+, fully typed, ruff + mypy + pytest.
  All rules apply unconditionally.
- **`scripts/python_scripts/`** — legacy: untyped. Apply rules to new/touched code; don't
  block solely on surrounding legacy.
- **`scripts/installer/`** — standalone CLIs: `argparse` required; `print()` fine,
  `logging` not required; no hardcoded absolute paths; ASCII-only output (no emoji).

**Imports** — all at top; order stdlib → third-party → local (blank-line separated);
`from __future__ import annotations` first; pin new deps (`pyproject.toml` for rf_test,
`requirements.txt` for python_scripts).

**Tooling (rf_test)** — `ruff` (py311, line length 99, rules E/F/W/I/UP/B/SIM/RUF);
`mypy` (`warn_return_any`, `warn_unused_configs`; no bare `# type: ignore`); `pytest`
(`testpaths = ["tests"]`, hardware tests need `--run-hardware`).

**Naming** — `snake_case` functions/modules/files; `UpperCamelCase` classes/dataclasses;
`UPPER_SNAKE` constants. Acronym whitelist: EXG, CQI, SCPI, RPi, PHY, UE, NR, PDSCH,
PDCCH, CRC, RSRP, RSRQ, SINR, MCS, TV, RLF, CFO, TDL, AWGN.

**Types & docs** — annotate every public signature; PEP 604 unions (`X | None`);
`typing.Protocol` for callbacks; `numpy.typing.NDArray` with dtype+shape in the docstring;
Google-style docstrings in imperative mood.

**Numerical** — epsilon for float equality (`pytest.approx` in tests); prefer numpy
builtins (`np.vdot`, `np.fft.fft`, `a.conj()`) over manual `real + 1j*imag`; normalise
once via shared helpers.

**Errors & logging** — no bare `except: pass`; catch the narrowest type; `logging` not
`print()` in library code; `logger = logging.getLogger(__name__)`; lazy formatting
(`logger.info("Power %s dBm", power)`); levels DEBUG/INFO/WARNING/ERROR.

**Testing & hardware** — pytest only (no `unittest.TestCase`); tests in `tests/`, absolute
imports, never touch `sys.path`; mock at the boundary (socket/SSH/fs), patch the package
path with `spec=True`; assert behaviour not tables; mark hardware tests
`@pytest.mark.hardware` (never in CI) and use `try/finally` to leave radios off, PAs
disabled, streams closed.

---

## 4. Skills

### `3gpp-nr-phy` — 5G NR Physical Layer
- **Specs:** TS 38.211 (channels & modulation), 38.212 (coding: LDPC/polar/rate
  matching/CRC), 38.213 (procedures: cell search, PRACH, TA, power control), 38.214
  (data: MCS, HARQ, TBS).
- **Chains:**
  - PDSCH: RE demap → chan est (DMRS) → equalize → demod → descramble → rate de-match →
    HARQ combine → LDPC decode → CRC.
  - PDCCH: RE demap → chan est → equalize → demod → descramble → polar decode →
    CRC (RNTI) → DCI parse.
  - PUSCH: TB → CRC → LDPC encode → rate match → scramble → modulate → layer map →
    DMRS insert → RE map.
  - Sync: PSS → SSS → PBCH DMRS → PBCH decode → MIB → SFN/cell ID/beam.
- **Pitfalls:** CP length differs on first vs subsequent OFDM symbols; DMRS sequences
  depend on slot/symbol/scrambling-ID; HARQ soft-buffer limits are per-UE-category;
  LDPC rate-match circular-buffer wrapping differs from LTE turbo; SCS affects slot
  duration and numerology throughout.

### `c-embedded-patterns`
Stack/static buffers for determinism; pair malloc/free and check returns; align for SIMD
(`__attribute__((aligned(32)))`); mind 64-byte cache lines. Targets x86 (sim) + ARMv8
(StarTag); platform code in `lib/x86/` and `lib/platform/arm_ran/`; use `cn_*`, never
intrinsics from `src/`; test x86 first, then cross-compile. Threads talk via ICM queues;
use `wrp_*` wrappers (`lib/os/`); avoid global mutable state. Debug with
`-DCMAKE_BUILD_TYPE=Debug -DUSE_ASAN=On`, dumps via `-DHARQ_DEBUG_DUMP_EN=1` /
`-DUL_DEBUG_DUMP_FLAG=1`, the `log_decoder` tool, and MATLAB refs in `matlab_util/`.

---

## 5. Agents

- **code-reviewer** — focus order: memory safety (critical: array indexing with
  variable RE/RB counts, null deref, stack overflow from large locals, uninitialised) →
  3GPP compliance (critical: cross-ref TS 38.211/212/213/214, table lookups, sequence
  generation, numerology params) → concurrency (high: PHY-thread races, ICM queue use,
  lock ordering) → performance (medium: hot-path copies, NEON) → maintainability (medium:
  magic numbers, `cn_*` API consistency).
- **test-engineer** — tiers: component tests (`testcases/components/`, vector-driven,
  registered in CTest) · submodule tests (`testcases/submodules/`, full chains) · x86
  emulation (`scripts/test/submodule/x86_emulation/`, uephy + macemu via `run_tests.py`).
  Each test needs `config.txt` + binary I/O vectors; use `lib/test_fileio/` and
  `lib/parser/`; register via `add_test()`. Debug with `ctest -V -R <pattern>`, debug
  dumps, and MATLAB comparison.

---

## 6. Concrete Build / Test / Format Commands

### `/build [platform]`
- `x86` (default): `cd build_x86 && rm -rf * && cmake .. && make -j$(nproc)`
- `x86-debug`: `… cmake .. -DCMAKE_BUILD_TYPE=Debug …`
- `x86-asan`: `… cmake .. -DCMAKE_BUILD_TYPE=Debug -DUSE_ASAN=On …`
- `arm`: `cd build_star && rm -rf * && cmake .. -DCMAKE_TOOLCHAIN_FILE=../toolchains/startag-1.1.0.cmake -DNMM_RF_ACTIVE=On && make package -j$(nproc)`

Report warnings, errors, success.

### `/test [pattern]`
`cd build_x86` → clean build (`rm -rf *`, `cmake ..`, `make -j8`) → `ctest -V -R "$PATTERN"`
(or `ctest` for all). Report totals, failing names + error output, likely causes.

### `/format <target>`
`staged` → format staged `.c`/`.h` (`git diff --cached --name-only --diff-filter=ACMR --
'*.c' '*.h'`); directory → all `.c`/`.h`; file → `clang-format -i <file>`. Report modified
files.

### `/mr-review <branch>`
Uses GitLab via `glab` (`glab mr list --source-branch … --output json`,
`glab mr note list <iid> --output json`). Applies fixes following the C style above
(4-space, snake_case, right-aligned pointers, no SIMD in `src/`, int status codes, cite
3GPP), runs `/format`, summarises per comment.

### `/investigate <description>`
Trace input → failure; check off-by-one, array dims, 3GPP parameter misuse, endianness,
alignment. Output Root cause / Evidence / Fix / Risk.

---

## 7. Hooks

- **`post-edit-build-check.sh`** (`PostToolUse` on `Edit|Write|MultiEdit`, `timeout 600`,
  `asyncRewake`): builds **both** x86 (`build_x86`: `cmake .. && make -j$(nproc)`) and ARM
  (`build_star` with `startag-1.1.0.cmake -DNMM_RF_ACTIVE=On && make package`). On failure
  greps the first 10 ` error:` lines and feeds them back as `additionalContext` (exit 2).
- **`pre-commit-format.md`**: dry-run `clang-format --Werror` on staged `.c`/`.h`,
  auto-format + re-stage offenders, warn the user.
- **`pre-edit-safety.md`**: before editing `src/`, `lib/`, `toplevel/` — no SIMD
  intrinsics in `src/` (→ `lib/x86/` or `lib/platform/`); never weaken `-Werror`; no
  `3rdparty/` edits without approval; never touch `.git/` or `build_*/`; preserve
  copyright/license headers.

---

## 8. Permissions (observed)

Local deny list (`.claude/settings.local.json`): `rm`, `rmdir`, and write-side git
(`push`, `reset`, `rebase`, `commit`, `checkout`, `restore`, `clean`, `branch`). Allow
list covers build/test (`cmake`, `make`, `ctest`, `ninja`, `clang-format`, `clang-tidy`,
`cppcheck`), read-only git + `glab mr list/view/diff/note list`, project binaries
(`./rs_*`, `./tc_*`, `./test_*`, `build_x86/*`, `build_arm/*`), remote exec
(`sshpass`/`ssh`/`scp`, incl. `timeout`-wrapped), and `/tmp`-scoped `rm`. Hook script is
explicitly allowed. `settings.json` adds `additionalDirectories`
(`<workspace-root>`, `/tmp`) and reads from `dumps_rpi/`.

---

## 9. MCP Servers (tokens redacted)

From `.cursor/mcp.json`. **The live file contains real tokens — rotate/redact before
copying.**

| Server | Package | Endpoint | Secret |
|--------|---------|----------|--------|
| `gitlab` | `@zereight/mcp-gitlab` | `<your-gitlab-host>` | `<GITLAB_TOKEN>` |
| `youtrack` | `youtrack-mcp-tonyzorin` | `<your-tracker-host>` | `<YOUTRACK_API_TOKEN>` |
| `memory` | `@modelcontextprotocol/server-memory` | `MEMORY_FILE_PATH=~/.<tool>/nr_ue_phy_memory.json` | — |

Both forge/tracker servers set `NODE_TLS_REJECT_UNAUTHORIZED=0` and `*_VERIFY_SSL=false`
for the internal self-signed hosts.

---

## 10. Cursor Rules (`.cursor/rules/*.mdc`)

| File | `globs` | Gist |
|------|---------|------|
| `rf-test-architecture.mdc` | `scripts/test/rf_test/**/*.py` | Single source of truth — one `EXGController`, one CRC parser, one auto-range; `monitor/` *wraps* top-level, never reimplements. Named constants, shared `PDSCH_CRC_RE`, strict dependency direction, context-managed connections, locked global state. |
| `rf-test-project-structure.mdc` | `scripts/test/rf_test/**/*.py` | PyPA flat layout: importable `rf_test/` package, tests in `tests/` outside it, `bin/` for shell scripts, `analysis/` inside the package. Canonical `pyproject.toml` (setuptools, ruff, mypy, pytest markers). `pip install -e ".[dev]"`. |
| `rf-test-python-standards.mdc` | `scripts/test/rf_test/**/*.py` | Imports at top + `from __future__ import annotations`; annotate every public signature (PEP 604, `Protocol`); `PascalCase`/`snake_case`/`UPPER_SNAKE`; Google docstrings; narrow exceptions + domain errors (`EXGError`); module logger, lazy formatting. |
| `rf-test-testing.mdc` | `scripts/test/rf_test/tests/**/*.py` | pytest only; absolute imports; unit (mocked, CI) vs hardware (`@pytest.mark.hardware`, never CI) tiers; mock at the boundary patching the package path with `spec=True`; `yield` fixtures; `pytest.approx`; `test_<behavior>_<scenario>` naming. |
| `nr-phy-channel-analysis-python.mdc` | `scripts/test/field/**/*.py` | Field channel-analysis modularity: single-responsibility modules (`reference_signals`, `channel_estimation`, …); 3GPP-anchored docstrings citing exact TS sections; `@dataclass` results; pytest with deterministic fixtures; `_EPS = 1e-30` division guards; vectorised numpy; pure reference-signal generators; `argparse` CLI callable programmatically. |
