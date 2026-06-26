# TeamCity ↔ GitLab Setup Guide for `nr_ue_phy`

How to wire GitLab into TeamCity, tell TeamCity what/where/how to build, and
configure email notifications for build success/failure. Grounded in our
5G NR UE PHY repository (already has `scripts/ci/teamcity_build.sh` and
`scripts/ci/teamcity_test_non_rf.sh`).

---

## 1. Connecting GitLab with TeamCity

There are **three wires** between GitLab and TeamCity. Set up all three for
a healthy integration:

```
        GitLab                                TeamCity
        ------                                --------
   ┌─────────────┐  (A) clone over SSH/HTTPS  ┌─────────────┐
   │   nr_ue_phy ├──────────────────────────▶ │  VCS Root   │
   │    repo     │                            └─────────────┘
   │             │  (B) webhook on push       ┌─────────────┐
   │             ├──────────────────────────▶ │  Trigger    │
   │             │                            └─────────────┘
   │   MR #123   │ ◀──(C) status: pass/fail──┤Status Publish│
   └─────────────┘                            └─────────────┘
```

### Wire A — Let TeamCity read the repo (VCS Root)

In TeamCity → your project → **Edit Configuration** → **VCS Roots** →
**Create VCS Root → Git**:

| Field | Value |
| --- | --- |
| Fetch URL | `git@gitlab.example.com:your-org/nr_ue_phy.git` (SSH) or HTTPS |
| Default branch | `refs/heads/master` |
| Branch spec | `+:refs/heads/master`<br>`+:refs/heads/engineering/*` |
| Authentication | SSH key (preferred) or PAT |

For **SSH**: upload the private key under **Project → SSH Keys**, then add
the matching public key in GitLab as a **Deploy Key** (read access is
enough).

For **HTTPS**: use a GitLab **Personal Access Token** with
`read_repository` scope as the password.

Click **Test connection** to verify.

### Wire B — Trigger builds on every push

Two options:

**Option 1 — Polling (simplest, default):**
Add a **VCS Trigger** to your build config. TeamCity polls GitLab every
60 s by default. Easy, but slightly delayed.

**Option 2 — Webhook (real-time):**
In GitLab → **Settings → Webhooks**:

- URL: `https://teamcity.example.com/app/rest/vcs-root-instances/commitHookNotification?locator=vcsRoot:(id:NrUePhy_Master)`
- Trigger on: **Push events**, **Merge request events**
- Secret token (optional but good)

Now a `git push` reaches TeamCity in under a second.

### Wire C — Post pass/fail back onto the MR

Build Configuration → **Build Features → Add → Commit Status Publisher**:

| Field | Value |
| --- | --- |
| VCS Root | `nr_ue_phy` |
| Publisher | GitLab |
| GitLab URL | `https://gitlab.example.com/api/v4` |
| Access token | GitLab PAT with `api` scope |

Result: each MR shows a green/red tick like
`TeamCity / nr_ue_phy x86 build — passed`.

Also add the **Pull Requests** build feature (type: GitLab) so TeamCity
builds MR branches *before* they merge.

---

## 2. How TeamCity Knows What / Where / How to Run

These map onto three different TeamCity concepts.

### "What to build" → VCS Root + branch spec + checkout rules

```
Project: nr_ue_phy
└── VCS Root: gitlab nr_ue_phy
    └── Branch spec:  +:refs/heads/master
                      +:refs/heads/engineering/*
    └── Checkout rules:  +:.=>.   (full repo by default)
```

You can also run different build configs against different paths — useful
for our repo:

```
Build config "x86 build"      checkout rules:  +:.=>.
Build config "ARM package"    checkout rules:  +:.=>.
Build config "docs only"      checkout rules:  +:docs=>docs   (skip code)
```

### "Where to build" → Agent requirements + agent pools

Each TeamCity **agent** (worker machine) advertises *capabilities*. Each
build config declares *requirements*. TeamCity matches them.

For `nr_ue_phy` you'd want at least three agent pools:

| Pool | Capability advertised | Used by |
| --- | --- | --- |
| `x86-build-pool` | `os.name=Linux`, `cmake`, `gcc` | x86 build, ctest, macemu TV |
| `arm-cross-pool` | `aarch64-linux-gnu-gcc` present | StarTag toolchain build |
| `lab-rf-pool` | custom param `startag.attached=true` | flash + RF tests |

Configure under **Build Configuration → Agent Requirements**:

```
Parameter name        Condition    Value
------------------    ---------    -----
aarch64-linux-gnu-gcc exists       (any)
teamcity.agent.cpu    contains     x86_64
```

A build that needs the StarTag radio simply sets
`startag.attached exists`, and only lab agents with that flag pick it up.

### "How to run it" → Build steps

A build configuration is an ordered list of steps. Each step has a
**runner type**. For our shell-driven flow, almost everything is
**Command Line**.

Example build steps for the `nr_ue_phy x86` configuration:

| # | Runner | Command |
| --- | --- | --- |
| 1 | Command Line | `bash scripts/format/check_clang_format.sh` |
| 2 | CMake | `-B build -DCMAKE_BUILD_TYPE=Release` |
| 3 | Command Line | `make -C build -j%teamcity.agent.cpuCount%` |
| 4 | Command Line | `ctest --test-dir build --output-on-failure` |
| 5 | Command Line | `bash scripts/run_x86_regression.sh build %env.TV_DIR%` |

We already have the building blocks: `scripts/ci/teamcity_build.sh` and
`scripts/ci/teamcity_test_non_rf.sh`. Each becomes one step:

```
Step 1: bash scripts/ci/teamcity_build.sh
Step 2: bash scripts/ci/teamcity_test_non_rf.sh
```

### How TeamCity sees test results

Two ways to feed test pass/fail into the dashboard:

**Built-in parsers** — under **Build Features → Add → XML Report
Processing**:

| Report type | Path |
| --- | --- |
| Ctest | `build/Testing/**/*.xml` |
| JUnit | `**/junit-*.xml` |
| GoogleTest | `build/**/*-gtest.xml` |

**Service messages** — your script prints a magic line, TeamCity picks
it up:

```bash
echo "##teamcity[testStarted name='pdsch_dmrs_scs30']"
./tc_pdsch_dmrs_30
echo "##teamcity[testFinished name='pdsch_dmrs_scs30']"
```

`ctest` writes JUnit-style XML out of the box, so option 1 is the easy
path here.

### Putting it together — full picture

```
┌───────────────────────────────────────────────────────────────┐
│ TeamCity build configuration: "nr_ue_phy x86"                 │
├───────────────────────────────────────────────────────────────┤
│ WHAT  : VCS Root → gitlab/nr_ue_phy, branches engineering/*   │
│ WHERE : agent pool "x86-build-pool", needs cmake + gcc        │
│ HOW   : Steps:                                                │
│         1. clang-format check                                 │
│         2. cmake -B build                                     │
│         3. make -j                                            │
│         4. ctest                                              │
│ RESULT: parses build/Testing/**/*.xml for test pass/fail      │
│ STATUS: pushed back to GitLab MR via Commit Status Publisher  │
└───────────────────────────────────────────────────────────────┘
```

---

## 3. Email Notifications on Build Success / Failure

Two levels: server-level SMTP setup, then per-user (or per-mailing-list)
rules.

### Step 1 — Server admin: configure SMTP

**Administration → Email Notifier**:

| Field | Example |
| --- | --- |
| SMTP host | `smtp.e-space.com` |
| SMTP port | 587 |
| Secure connection | STARTTLS |
| Login / Password | service account |
| From | `teamcity@e-space.com` |

Click **Test connection / Send test email**.

### Step 2 — Personal notification rules

Each user (you) sets rules under **My Settings & Tools → Notifications →
Email Notifier → Add new rule**:

```
Watch:    Project "nr_ue_phy"
          (or specific build config "nr_ue_phy x86")
          (or "Builds with my changes" — only emails about your commits)

Notify when:
  ☑ Build fails
  ☑ The first failure after success ("build broken")
  ☑ Build is successful after failure ("build fixed")
  ☐ Build is successful (usually too noisy)
  ☑ Build is hanging / canceled
```

The **first failure after success** and **fixed** pair is the sweet spot —
you get told when something breaks and again when it's healed, without spam
on every green build.

### Step 3 — Team-wide email (mailing list)

Don't ask everyone to set up rules individually. Instead:

1. Create a **service user** in TeamCity, e.g. login `nrue-ci`, email
   `nrue-ci@e-space.com` (a mailing list).
2. As that user, add rules:
   - Project: `nr_ue_phy`
   - On: build fails / first failure / fixed
3. Anyone who joins the team gets emails by being added to the mailing
   list — no TeamCity admin work.

### Step 4 — Per-MR feedback

You don't need email for "did my MR pass" — the **Commit Status Publisher**
from §1C already puts a green/red tick on the MR plus a clickable link to
the build log. Email rules should focus on `master` regressions, not
per-MR builds.

### Format options

The Email Notifier rule has:

- **Plain text** vs **HTML** — HTML is nicer (clickable build link, failed
  test list inline).
- A custom template under **Administration → Notification Templates** if
  you want logs/links shaped a particular way (e.g. include the failing
  TV name).

### Other channels worth knowing about (same mechanism, different transport)

| Channel | How |
| --- | --- |
| Slack | Plugin "Slack Notifier" or generic webhook → Slack incoming webhook URL |
| Mattermost | Plugin or webhook |
| Jabber/XMPP | Built-in notifier |
| IDE pop-ups | TeamCity plugin in CLion/IntelliJ (works for our C codebase) |

---

## 4. Quick Starter Mapping for `nr_ue_phy`

| Question | Answer |
| --- | --- |
| Where do I configure the GitLab connection? | TeamCity → Project → VCS Roots |
| Where do I tell it to use `teamcity_build.sh`? | Build Configuration → Build Steps → Command Line runner |
| How do I add a "lab-only" build? | Add agent requirement `startag.attached exists` |
| How do I get an MR ✅ tick? | Add Commit Status Publisher build feature |
| How do I get an email when master breaks? | My Settings → Notifications → rule "Project nr_ue_phy, first failure after success" |

---

## 5. Recommended Order of Operations

If you're setting this up from scratch on a fresh TeamCity server:

1. **Admin** — configure SMTP (so notifications work from day one).
2. **Admin** — install agents, label them with capabilities (x86 / ARM /
   lab).
3. **Project** — create `nr_ue_phy` project in TeamCity.
4. **VCS Root** — connect to GitLab, test connection.
5. **Build config "x86 build"** — add VCS root, build steps, agent
   requirements, XML report processing, VCS trigger, Commit Status
   Publisher.
6. **Build config "ARM package"** — same, but `arm-cross-pool` requirement.
7. **Build config "TV regression"** — depends on x86 build's artifact.
8. **Build config "Lab flash"** — manual trigger, `lab-rf-pool` requirement.
9. **Personal notification rules** — subscribe yourself to master fail/fix
   events.
10. **Service user / mailing list** — subscribe the team to project-wide
    fail/fix events.
11. **GitLab webhook** — flip from polling to push-driven.
12. **Verify end-to-end** — push a no-op commit, watch TeamCity light up,
    confirm GitLab MR receives the status, confirm email arrives on a
    forced failure.

This order avoids the common "everything works except notifications" trap
where SMTP is added last and nobody knows what alerts they missed.
