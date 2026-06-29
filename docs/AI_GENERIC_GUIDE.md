# AI Tooling — Generic Guide (Portable)

Project-agnostic conventions, command contracts, and agent/hook/permission patterns.
Copy this into a new repository and fill in the bracketed `<placeholders>`. The
companion [AI_DOMAIN_APPENDIX.md](AI_DOMAIN_APPENDIX.md) shows a fully-populated instance.

> Convention used below: replace `<TICKET-PREFIX>` (e.g. `JIRA-`, `NRUEL1-`),
> `<default-branch>` (e.g. `main`, `master`), and `<module-prefixes>` with your project's
> values.

---

## 1. Repository & MR/PR Lifecycle

These belong in the root `CLAUDE.md` / `AGENTS.md` so they are always in context.

- **One concern per MR.** Do not mix a feature, a refactor, an analysis sweep, and a
  validation report on one branch. Link related MRs from the tracker ticket.
- **Branch name = ticket.** e.g. `<TICKET-PREFIX>1361`. Branches without a ticket are
  rejected in review.
- **Commit subjects** start with an imperative verb (`Add …`, `Fix …`, `Refactor …`,
  `Remove …`) and stay under 72 characters. Detail goes in the body.
- **Reference the ticket** in the body for multi-commit changes: `Refs <TICKET-PREFIX>1361.`
- **Defend the scope.** When a reviewer asks for out-of-scope work, reply
  "deferred to <TICKET-PREFIX>yyyy" rather than silently growing the MR.
- **What not to commit.** Generated artifacts (HTML, PDFs, build dirs), IDE metadata,
  `__pycache__/`, personal logs — anything that rebuilds from source. No hard-coded
  absolute paths; expose machine-specific dirs as CLI flags with repo-relative defaults.
- **No dead code.** Don't ship legacy wrappers on first commit. If a function has no
  in-tree caller after a refactor, delete it.
- **Ticket every TODO.** `// TODO(<TICKET-PREFIX>xxxx): …`. Un-ticketed TODOs rot forever.
- **No AI authorship trailers.** Do not add `Co-Authored-By:` lines for AI tools.

### Constants & citations

- **No magic numbers.** Every non-trivial literal gets a named constant (`#define` /
  `static const` / module-level `UPPER_SNAKE`).
- **Cite non-obvious numbers.** Point at the source in a comment (spec section, paper,
  standard). Normalisation factors, RNG multipliers, thresholds all need a citation.
- **One concern per file.** A script that defines models, runs a sweep, and plots is
  three files.

---

## 2. Commit Message Format

```
<module>: <concise description>
```

- Subject under 72 chars; body for anything non-trivial.
- Maintain a fixed table of **module prefixes** so history is greppable. Example shape:

  ```
  <area-1>:  — short description of the subsystem
  <area-2>:  —
  test:      — test cases and infrastructure
  build:     — build system, toolchain, CI
  scripts:   — automation scripts
  ```

  See the domain appendix for a real prefix table.

---

## 3. Coding Standards (skeleton)

Keep language-specific rules *next to the code they govern* (a nested `CLAUDE.md` per
subtree), not all in the root. The root only references them.

**Formatting** — pick one auto-formatter and make it mandatory pre-commit (CI flags
divergence). Fix indent width, pointer alignment, column policy once and check in the
config file (`.clang-format`, `ruff`, `prettier`, …).

**Naming** — define one casing per kind (functions, types, constants, files) and an
acronym whitelist for domain terms. Mandate a **module prefix** on every non-static
symbol so global scope stays collision-free.

**Architecture** — state the layering rule explicitly: where platform-specific code is
allowed, what the public API surface is, how threads/modules communicate. Forbid the
common violation up front (e.g. "no platform intrinsics outside `lib/`").

**Memory** — stack/static by default; heap only when size is runtime-determined; always
check allocation returns; free in the allocating scope; zero pointers after free.

**Error handling** — one convention for status (e.g. int return codes, `0` = success,
`< 0` = error; pointers return `NULL`). Never silently ignore an error return. Log
through the project logger, never raw `print`/`printf`.

**Tests** — assert *behaviour*, not static tables (re-copying a table the code reads
catches zero bugs). Share test constants; never repeat a literal. Use an epsilon helper
for float equality, never `==`.

---

## 4. Slash Command Catalogue

Each command is one markdown file (`.claude/commands/<name>.md`; mirror in
`.codex/commands/`). **Contract every command follows:**

- First lines describe what it does.
- `--help` prints usage + examples and stops.
- Then numbered, deterministic steps.
- End by reporting the result (counts, pass/fail, what changed).

| Command | Generic? | Purpose |
|---------|----------|---------|
| `/build [target]` | Rewrite per build system | Clean-build a named target; report warnings/errors/success. |
| `/test [pattern]` | Rewrite per test runner | Clean build, then run the test runner filtered by pattern; summarise pass/fail and likely causes. |
| `/format <target>` | Mostly generic | Run the formatter on a file, directory, or `staged` set; report what changed. |
| `/code-review <branch> [--staged\|--file\|--files]` | Generic | Diff a branch against `<default-branch>` (or read named files), review against a checklist, output severity-tagged findings + verdict. |
| `/mr-review <branch>` | Generic | Fetch open MR/PR comments, apply minimal fixes per comment, format, re-verify, summarise per-comment status. |
| `/investigate <description>` | Generic | Trace a bug from symptom to root cause; output **Root cause / Evidence / Fix / Risk**. |
| `/proceed` | Generic | Auto-run *safe* commands without per-call confirmation (see §7). |

### `/code-review` checklist (generic core)

1. Memory/resource safety (bounds, null deref, use-after-free, leaks, uninitialised vars)
2. Spec/contract compliance (deviations from the governing standard or API contract)
3. Architecture/abstraction boundaries respected
4. Concurrency (locks, queues, shared state, data races)
5. Style matches the checked-in formatter config
6. Error handling — every path handled, return codes checked, warnings-as-errors clean
7. Performance — avoidable copies/allocations, missed optimisations
8. Logic — undefined behaviour, off-by-one, edge cases
9. Tests — coverage for the changed behaviour

Output shape: `[CRITICAL] / [MAJOR] / [MINOR] / [NIT]` with `file:line`, then open
questions, a test-gap note, and a short verdict.

### `/mr-review` flow (generic core)

Validate the branch arg → resolve the MR via the forge CLI (`glab`/`gh`, JSON output;
auto-pick if exactly one, else ask) → fetch comments, skip system/resolved/outdated →
print a `# | Author | File:Line | Comment` table → apply the *minimal* fix per actionable
comment (ask when ambiguous) → format touched files → run focused build/tests → final
`Comment # | Status | File | What was done` table with statuses
`FIXED / SKIPPED / NEEDS CLARIFICATION / BLOCKED`.

---

## 5. Sub-Agents

One markdown file per role under `.claude/agents/`. A role defines a *posture* and a
*focus checklist*, not steps. Two reusable archetypes:

- **Code Reviewer** — rigorous safety/correctness reviewer. Focus areas ordered by
  severity: memory safety (critical) → spec compliance (critical) → concurrency (high) →
  performance (medium) → maintainability (medium).
- **Test Engineer** — writes/debugs/maintains tests. Knows the test tiers (unit /
  integration / end-to-end), how vectors and fixtures are structured, how tests are
  registered with the runner, and how to debug failures verbosely.

Adapt the focus lists to the project; keep the severity ordering.

---

## 6. Skills

One markdown file per knowledge pack under `.claude/skills/`. A skill front-loads
domain knowledge the assistant otherwise wouldn't have: key specs/standards, processing
chains, and a **"common pitfalls"** list. These are almost entirely domain-specific —
write one per major subsystem. (See the appendix for examples.)

---

## 7. The `/proceed` Safe-Command Policy

A reusable allow/deny policy so the assistant can keep momentum without rubber-stamping
dangerous operations.

**Auto-run (no confirmation):** read-only inspection (`ls`, `find`, `grep`, `cat`,
`head`, `tail`, `wc`, `diff`, `file`, `stat`); build/configure inside the workspace
(`make`, `cmake`, `ninja`, `bear`); analysis (`clang-tidy`, `cppcheck`,
`gcc -fsyntax-only`, formatter in-place on touched files); test runners and project test
binaries; read-only git (`status`, `diff`, `log`, `show`, `branch`, `stash list`);
read-only forge queries (`glab/gh … list/view/diff`); non-destructive fs helpers
(`mkdir -p`, `touch`, `cp` without overwrite); `jq`, `timeout`-wrapped safe commands.

**Always ask / escalate first:** `rm`/`rmdir`/`unlink` (except scoped to `/tmp` and build
dirs); git writes (`add`, `commit`, `push`, `merge`, `rebase`, `reset`, `checkout`,
`restore`, `clean`); package/system changes (`apt`, `pip install`, `chmod`, `chown`);
remote writes (`glab/gh … merge/close/create/comment`); overwriting `mv`/`cp -f`;
privileged/hardware/deploy commands.

### Tool-call discipline (so the matcher can auto-approve)

The permission matcher inspects the **full command string**, not pipeline segments.
`cd X && make Y` does *not* match `Bash(make:*)` and prompts. Therefore:

1. **Never `cd`.** Use `make -C <dir>`, `ctest --test-dir <dir>`, absolute binary paths,
   or the tool's `workdir` parameter (Codex).
2. **Split `&&` / `;` chains into separate tool calls** so each is individually
   classifiable. Exception: read-only tail pipes (`| grep`, `| head`, `| wc`, …) stay
   attached.
3. **Keep redirections attached** (`cmd > file`, `cmd 2>&1`).
4. **Prefer `$(cmd)` over pipelines** when the outer command is what matters
   (`make -j$(nproc)`).

---

## 8. Hooks

Lifecycle automation. Two forms: shell scripts wired in `settings.json`, or prompt-style
markdown the assistant reads before an action. Three reusable patterns:

- **Post-edit build check** (`PostToolUse` on `Edit|Write`): recompile affected targets
  after every edit; on failure, feed the first ~10 error lines back as context. Use
  `asyncRewake` so a long build doesn't block. *(Build for every target you ship —
  catching a cross-compile break early is cheap.)*
- **Pre-commit format**: before committing, dry-run the formatter on staged files,
  auto-format and re-stage any that would change, and warn which.
- **Pre-edit safety**: before editing protected trees, enforce invariants — don't weaken
  warnings-as-errors flags, don't touch vendored/third-party code without approval, don't
  modify build artifacts or `.git/`, preserve license headers.

Wiring example (`.claude/settings.json`) — **note hook paths are absolute; fix them per
machine/repo:**

```json
{
  "permissions": {
    "additionalDirectories": ["<extra-readable-dir>"]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "<repo>/.claude/hooks/post-edit-build-check.sh",
            "timeout": 600,
            "statusMessage": "Build check...",
            "asyncRewake": true
          }
        ]
      }
    ]
  }
}
```

A hook script signals "feed this back to the assistant" by exiting `2` and printing JSON:

```json
{ "hookSpecificOutput": { "hookEventName": "PostToolUse", "additionalContext": "<text>" } }
```

---

## 9. Permission Model

Split committed vs local:

- **`.claude/settings.json`** — committed. Shared permissions + hook wiring. Keep it
  minimal and safe for everyone.
- **`.claude/settings.local.json`** — per-developer, **git-ignored**. Holds the
  individual's allow/deny lists.

**Recommended deny list** (destructive/irreversible — block by default, approve case by
case):

```json
"deny": [
  "Bash(rm:*)", "Bash(rmdir:*)",
  "Bash(git push:*)", "Bash(git reset:*)", "Bash(git rebase:*)",
  "Bash(git commit:*)", "Bash(git checkout:*)", "Bash(git restore:*)",
  "Bash(git clean:*)", "Bash(git branch:*)"
]
```

**Allow list** — grow it from real usage to cut prompt fatigue. Patterns mirror the
`/proceed` safe set: read-only tools (`Bash(cat:*)`, `Bash(grep:*)`, `Bash(find:*)`),
build/test (`Bash(cmake:*)`, `Bash(make:*)`, `Bash(ctest:*)`), read-only git
(`Bash(git diff:*)`, `Bash(git log:*)`, `Bash(git status:*)`), read-only forge
(`Bash(glab mr list:*)`, `Bash(glab mr view:*)`), and `/tmp`-scoped cleanup
(`Bash(rm -rf /tmp/*:*)`). Scope risky tools narrowly to specific paths rather than
allowing them wholesale.

> Tip: the `/fewer-permission-prompts` skill can scan transcripts and propose an allow
> list from commands you actually run.

---

## 10. MCP Servers

Register external integrations (issue tracker, forge, persistent memory) so the
assistant can query them. Cursor uses `.cursor/mcp.json`; Claude Code uses its own MCP
config. **Never commit live tokens** — use placeholders and document the source.

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "npx",
      "args": ["-y", "@zereight/mcp-gitlab"],
      "env": {
        "GITLAB_TOKEN": "<GITLAB_TOKEN>",
        "GITLAB_API_URL": "<https://your-gitlab-host>",
        "NODE_TLS_REJECT_UNAUTHORIZED": "0"
      }
    },
    "issue-tracker": {
      "command": "npx",
      "args": ["-y", "<tracker-mcp-package>"],
      "env": {
        "TRACKER_URL": "<https://your-tracker-host>",
        "TRACKER_API_TOKEN": "<TRACKER_API_TOKEN>"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": { "MEMORY_FILE_PATH": "<path-to-memory.json>" }
    }
  }
}
```

`NODE_TLS_REJECT_UNAUTHORIZED: "0"` disables TLS verification — only for trusted internal
hosts with self-signed certs; never for public endpoints.

---

## 11. Cursor `.mdc` Rule Format

Cursor rules are markdown with YAML frontmatter; Cursor auto-attaches one when an edited
file matches its `globs`.

```mdc
---
description: <one-line summary shown in the rule picker>
globs: <path/glob/**/*.ext>          # comma-separate multiple globs
alwaysApply: false                    # true = always in context, ignore globs
---

# <Rule Title>

<rule body — same conventions as the CLAUDE.md sections, scoped to the glob>
```

Keep each rule single-purpose (architecture, structure, standards, testing) and point its
`globs` at the subtree it governs.
