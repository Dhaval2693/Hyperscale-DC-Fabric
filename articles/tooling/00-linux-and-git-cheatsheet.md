# Linux + Git Cheat Sheet

A single-page reference for the shell and git skills that come up daily and in interviews. Read this before any technical screen.

---

## Linux: The Eight Commands You Use Constantly

| Command | One-liner | Example |
|---|---|---|
| `grep` | Search text in files | `grep "ERROR" app.log` |
| `awk` | Column-wise text processing | `awk '{print $1}' file` |
| `sed` | Find/replace in text | `sed 's/old/new/g' file` |
| `find` | Locate files by name/type/age | `find . -name "*.py"` |
| `xargs` | Pipe output as args to another command | `find . -name "*.log" \| xargs rm` |
| `sort` | Sort lines | `sort -n numbers.txt` |
| `uniq` | Deduplicate adjacent lines (after sort) | `sort file \| uniq -c` |
| `cut` | Slice columns from text | `cut -d',' -f1,3 file.csv` |

## Linux: Pipes and Redirection

| Symbol | Meaning |
|---|---|
| `\|` | Send stdout of left into stdin of right |
| `>` | Redirect stdout to file (overwrite) |
| `>>` | Redirect stdout to file (append) |
| `2>` | Redirect stderr |
| `2>&1` | Send stderr to where stdout goes |
| `<` | Read stdin from file |

**Common combo:** `command > out.log 2>&1` — capture everything (stdout + stderr) into one file.

## Linux: The "Use Shell vs Python" Rule

| Use shell when... | Use Python when... |
|---|---|
| One-liner with pipes | Logic > 5 lines |
| Quick text munging in a terminal | Data structures (dicts, lists of objects) |
| Filtering log files | Anything that needs unit tests |
| Combining a few standard commands | Anything that needs error handling beyond exit codes |
| Throwaway exploration | Anything you'll re-run > 3 times |

**Rule of thumb:** if you start writing `if`/`for` in bash, switch to Python.

## Linux: The 5 Most Useful One-Liners

```bash
# Count occurrences of each value in a column
awk '{print $1}' file | sort | uniq -c | sort -rn

# Find files modified in the last 7 days
find . -type f -mtime -7

# Search recursively in code for a pattern
grep -r "TODO" .

# Show lines from a log between two timestamps
sed -n '/2026-01-15 14:00/,/2026-01-15 15:00/p' app.log

# Replace a string across all .py files
sed -i 's/old/new/g' *.py
```

---

## Git: The Daily Eight

| Command | What it does |
|---|---|
| `git status` | Show what's changed |
| `git diff` | Show line-by-line changes |
| `git add <file>` | Stage a file for commit |
| `git commit -m "msg"` | Create a commit from staged changes |
| `git push` | Send commits to remote |
| `git pull` | Fetch + merge remote changes |
| `git log --oneline` | Show recent commits |
| `git checkout <branch>` | Switch branches |

## Git: Branching Workflow

```bash
git checkout -b feature/x        # create + switch to new branch
# ... make changes, commit ...
git push -u origin feature/x     # first push (sets upstream)
# ... open PR, get review ...
git checkout main
git pull
git branch -d feature/x          # delete local branch after merge
```

## Git: Merge vs Rebase (Common Interview Question)

| Merge | Rebase |
|---|---|
| Preserves history as it happened | Rewrites history to look linear |
| Creates a merge commit | No merge commit |
| Safe on shared branches | NEVER rebase a shared/public branch |
| Easy to undo | Harder to undo (`reflog` saves you) |

**Use merge when:** integrating completed work, especially on `main`.
**Use rebase when:** cleaning up your own feature branch before pushing.

**The golden rule:** *Never rebase commits that exist outside your local repo.*

## Git: Undoing Things

| Want to... | Use |
|---|---|
| Un-stage a file | `git restore --staged <file>` |
| Discard local changes (UNRECOVERABLE) | `git restore <file>` |
| Undo last commit, keep changes | `git reset --soft HEAD~1` |
| Undo last commit, discard changes | `git reset --hard HEAD~1` |
| Revert a pushed commit (safe) | `git revert <commit>` |
| Recover a "lost" commit | `git reflog` then `git checkout <hash>` |

**`reflog` is your safety net.** Even after `reset --hard`, the commit hash is recorded in reflog for ~30 days.

## Git: Conflict Resolution

When `git pull` or `git merge` hits a conflict:

1. `git status` shows conflicted files
2. Open each conflicted file. You'll see:
   ```
   <<<<<<< HEAD
   your version
   =======
   their version
   >>>>>>> branch-name
   ```
3. Edit to keep what you want. Remove the marker lines.
4. `git add <file>` to mark as resolved.
5. `git commit` (no -m needed; commit message is pre-filled).

## Git: The 5 Commands That Save You

```bash
git stash                  # save uncommitted changes for later
git stash pop              # restore them

git log --oneline --graph  # visualize branch history
git diff main..HEAD        # see what your branch added vs main
git cherry-pick <commit>   # apply a specific commit to current branch
git reflog                 # see every HEAD change (your time machine)
```

---

## What to Say in an Interview

For a "tell me about your git workflow" question:
> "I work on feature branches off main. For my own branches I sometimes rebase to keep history clean, but I never rebase shared branches. I use `git status` and `git diff` constantly before committing — I want to see exactly what's going in. When conflicts come up, I resolve them locally and verify the build before pushing."

For a "have you used grep/awk/sed?" question:
> "Daily. I reach for grep for plain searches, awk when I need columns or computed values, sed for find/replace. For anything with more than basic logic, I switch to Python."

These answers signal "experienced engineer, not just textbook user." That's the bar.
