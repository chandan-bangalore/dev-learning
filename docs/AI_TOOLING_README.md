# AI Tooling — Portable Setup Guide

This repository drives three AI coding assistants — **Claude Code**, **OpenAI Codex**,
and **Cursor** — from a shared set of rules, slash commands, agents, skills, and hooks.
This document and its two companions package that setup so it can be **reused when
bootstrapping a new git repository**.

| Document | Scope | Reuse as-is? |
|----------|-------|--------------|
| [AI_GENERIC_GUIDE.md](AI_GENERIC_GUIDE.md) | Project-agnostic conventions, command contracts, agent/skill/hook patterns, permission model, MCP setup | ✅ Copy into any new repo, then fill in the blanks |
| [AI_DOMAIN_APPENDIX.md](AI_DOMAIN_APPENDIX.md) | The `nr_ue_phy` specifics: C critical-path rules, Python `rf_test` rules, 3GPP knowledge, concrete build/test commands | ⚠️ Keep only if the new repo is a sibling/related project; otherwise use as an example of how to fill the generic guide |
| This file | Index, tool-by-tool map, bootstrap checklist | ✅ Adapt the checklist |

The split is deliberate: the **generic guide** is the reusable skeleton; the **domain
appendix** shows what a fully-populated instance looks like.

---

## How each tool consumes its config

Different assistants read different files. The same *intent* (e.g. "review a branch")
is expressed once per tool, in that tool's native format.

### Claude Code

| Path | Purpose | Loaded |
|------|---------|--------|
| `CLAUDE.md` (root, `src/`, `scripts/`) | Always-on project rules. Nested files apply to their subtree. | Auto, every session |
| `.claude/commands/*.md` | Slash commands (`/build`, `/test`, …). Filename = command name. | On `/name` invocation |
| `.claude/agents/*.md` | Sub-agent role definitions (code-reviewer, test-engineer). | When an agent is spawned |
| `.claude/skills/*.md` | Domain knowledge packs surfaced when relevant. | On demand |
| `.claude/hooks/*` | Scripts/prompts fired on lifecycle events (post-edit, pre-commit). | Event-driven |
| `.claude/settings.json` | Shared, committed config: permissions + hook wiring. | Auto |
| `.claude/settings.local.json` | Per-developer overrides (allow/deny lists). **Not committed.** | Auto |

### OpenAI Codex

| Path | Purpose |
|------|---------|
| `.codex/commands/*.md` | Codex prompt files mirroring the Claude commands, rephrased for Codex tool semantics (`apply_patch`, `workdir`, `require_escalated`, `rg`). |
| `AGENTS.md` *(convention)* | Codex's always-on instructions file. **Not present here** — Codex currently inherits intent from the command files and `CLAUDE.md`. Add one in a new repo if you want always-on Codex rules. |

### Cursor

| Path | Purpose |
|------|---------|
| `.cursor/rules/*.mdc` | Scoped rules with YAML frontmatter (`description`, `globs`, `alwaysApply`). Cursor auto-attaches a rule when an edited file matches its `globs`. |
| `.cursor/mcp.json` | MCP server registry (GitLab, YouTrack, memory). **Contains secrets — redact before sharing.** |

---

## Source map — where each rule lives today

```
nr_ue_phy/
├── CLAUDE.md                     # repo & MR lifecycle, constants & citations  → generic guide
├── src/CLAUDE.md                 # C critical-path conventions                 → domain appendix
├── scripts/CLAUDE.md             # Python (rf_test / installer) conventions    → domain appendix
├── .claude/
│   ├── commands/                 # build, test, format, code-review,
│   │                             #   mr-review, proceed, investigate           → generic guide (contracts)
│   ├── agents/                   # code-reviewer, test-engineer                → generic + domain
│   ├── skills/                   # 3gpp-nr-phy, c-embedded-patterns            → domain appendix
│   ├── hooks/                    # post-edit-build-check.sh,
│   │                             #   pre-commit-format, pre-edit-safety        → generic guide (patterns)
│   ├── rules/                    # coding-standards, commit-messages           → generic guide
│   ├── settings.json             # permissions + hooks (committed)             → generic guide
│   └── settings.local.json       # allow/deny lists (per-dev, uncommitted)     → generic guide
├── .codex/commands/              # Codex variants: code-review, mr-review,
│                                 #   proceed                                   → generic guide
└── .cursor/
    ├── rules/*.mdc               # rf_test architecture/structure/standards/
    │                             #   testing + field-analysis Python           → domain appendix
    └── mcp.json                  # GitLab / YouTrack / memory MCP servers      → generic guide (redacted)
```

---

## Bootstrapping a new repository

1. **Copy the skeleton.** Bring `AI_GENERIC_GUIDE.md` into the new repo. Decide whether
   the domain appendix is relevant; if not, delete it and write a fresh appendix following
   the same shape.
2. **Author the always-on rules.** Create a root `CLAUDE.md` (and `AGENTS.md` if you use
   Codex). Lift the *Repository & MR Lifecycle* and *Commit Message* sections from the
   generic guide; replace the ticket prefix (`NRUEL1-`) and module-prefix table with the
   new project's values.
3. **Add per-language rules.** Create nested `CLAUDE.md` files (e.g. `src/CLAUDE.md`,
   `scripts/CLAUDE.md`) for each language/subtree, mirroring the appendix's structure.
4. **Define commands.** Copy the `.claude/commands/*.md` whose contract still applies
   (`/format`, `/code-review`, `/mr-review`, `/proceed`, `/investigate` are largely
   generic). Rewrite the concrete steps in `/build` and `/test` for the new build system.
   Mirror any you want in `.codex/commands/`.
5. **Wire hooks and permissions.** Adapt `.claude/settings.json` (hook paths are
   absolute — fix them) and seed `.claude/settings.local.json` with the deny list of
   destructive git operations from the generic guide. Add `.claude/settings.local.json`
   to `.gitignore`.
6. **Register MCP servers.** Copy `.cursor/mcp.json`, then **replace every token with a
   placeholder** and document where the real value comes from. Never commit live tokens.
7. **Cursor rules.** Add `.cursor/rules/*.mdc` with `globs` pointing at the new repo's
   source layout.

### Security note

`.cursor/mcp.json` in this repo contains live GitLab and YouTrack tokens. Throughout
these portable docs those values are shown as `<GITLAB_TOKEN>` / `<YOUTRACK_API_TOKEN>`.
Before copying the real file anywhere, rotate or redact the secrets, and keep the
populated file out of version control.
