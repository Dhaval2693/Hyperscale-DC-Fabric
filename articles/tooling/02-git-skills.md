# Git Skills

Git skills come up in interviews in two ways:
1. **Direct questions:** "Walk me through your git workflow." "How do you handle merge conflicts?" "What's the difference between merge and rebase?"
2. **Indirect signals:** during a coding screen, the interviewer watches how comfortably you navigate git when you're given a repo to work in.

This article covers the daily commands you should know cold, the concepts you'll be asked to explain, and the recovery commands that save you when things go wrong.

## The Daily Eight Commands

```bash
git status                  # what's changed?
git diff                    # what specifically changed?
git diff --staged           # what's STAGED for commit?
git add <file>              # stage a file
git add -p                  # stage hunks interactively
git commit -m "message"     # commit staged changes
git push                    # send to remote
git pull                    # fetch + merge from remote
git log --oneline           # recent history (one line per commit)
```

**Habit:** always run `git status` and `git diff` *before* committing. You want to see exactly what's going in.

## Branching Workflow

The standard feature-branch workflow:

```bash
git checkout main
git pull                              # start from latest main
git checkout -b feature/auth-fix      # create + switch to new branch

# ... make changes ...
git add .
git commit -m "fix auth bug"

# First push sets up the remote tracking branch
git push -u origin feature/auth-fix

# ... open PR, get review, merge ...

git checkout main
git pull
git branch -d feature/auth-fix        # delete local branch after merge
```

Naming convention varies by team: `feature/`, `bugfix/`, `chore/`, or just `username/description`. Whatever your team uses, follow it.

## Merge vs Rebase (Asked in Almost Every Interview)

This is the most common git interview question. Know the difference.

### Merge

```bash
git checkout main
git merge feature-branch
```

- Preserves history as it actually happened.
- Creates a "merge commit" that joins two branches.
- History looks like a graph (branches and merges visible).
- Safe — no rewriting.

### Rebase

```bash
git checkout feature-branch
git rebase main
```

- Rewrites your branch's commits to look like they were made on top of the latest main.
- No merge commit — history is linear.
- **Rewrites commit hashes** — that's why it's dangerous on shared branches.

### When to Use Which

| Use **merge** when... | Use **rebase** when... |
|---|---|
| Integrating completed work into `main` | Cleaning up your own feature branch before pushing |
| The branch has been pushed/shared | Catching up your local branch with latest `main` |
| You want to preserve "this is when we merged X" | You want a clean linear history |

### The Golden Rule

**Never rebase commits that exist outside your local repo.**

If you rebase commits you've already pushed, you've rewritten history for everyone. Their pulls will fail, their commits will be orphaned, and they'll hate you.

### How to Phrase It in an Interview

> "Merge preserves history; rebase rewrites it to look linear. I use rebase to keep my own feature branches clean before pushing, and merge when integrating into shared branches. The golden rule: never rebase commits I've already pushed."

## Resolving Merge Conflicts

When git can't auto-merge, you'll see:

```
Auto-merging file.py
CONFLICT (content): Merge conflict in file.py
Automatic merge failed; fix conflicts and then commit the result.
```

Steps:

```bash
git status                  # shows which files are conflicted
```

Open each conflicted file. Look for:

```
<<<<<<< HEAD
your version
=======
their version
>>>>>>> branch-name
```

Edit to keep what you want. Remove all the marker lines (`<<<<<<<`, `=======`, `>>>>>>>`).

```bash
git add <file>              # mark as resolved
git commit                  # finishes the merge (message pre-filled)
```

To abort a merge entirely:
```bash
git merge --abort
```

## Undoing Things (Critical to Know)

Most interview "git pitfalls" questions are about undoing operations. Know these by heart.

| Want to... | Command |
|---|---|
| Un-stage a file (after `git add`) | `git restore --staged <file>` |
| Discard local changes (DESTRUCTIVE) | `git restore <file>` |
| Undo last commit, KEEP changes staged | `git reset --soft HEAD~1` |
| Undo last commit, KEEP changes unstaged | `git reset HEAD~1` (default --mixed) |
| Undo last commit, DISCARD changes | `git reset --hard HEAD~1` |
| Revert a PUSHED commit (creates new commit) | `git revert <commit-hash>` |
| Recover a "lost" commit | `git reflog` then `git checkout <hash>` |

### Reset vs Revert (Often Asked)

- **`reset`** moves the branch pointer back. Rewrites history. Use only on local, unpushed commits.
- **`revert`** creates a new commit that undoes a previous commit. History is preserved. Safe on shared branches.

**Rule:** if it's pushed, use `revert`. If it's local, you can `reset`.

## The Reflog Is Your Safety Net

Every change to HEAD is recorded in the reflog for ~30 days, including resets and rebases.

```bash
git reflog                            # show recent HEAD movements
git checkout <hash-from-reflog>       # recover a "lost" commit
```

If you ever think you've lost work to a `reset --hard` or bad rebase, check the reflog before panicking.

## Stash — Save Uncommitted Work for Later

When you need to switch branches but have uncommitted changes:

```bash
git stash                          # save changes, clean working tree
git checkout other-branch
# ... do something ...
git checkout original-branch
git stash pop                      # restore the stashed changes

git stash list                     # see all stashes
git stash drop                     # delete most recent stash
```

## Cherry-Pick — Apply a Specific Commit

Copy a single commit from one branch to another:

```bash
git checkout target-branch
git cherry-pick <commit-hash>
```

Useful when you want a bug fix from one branch in another, without merging everything.

## Inspecting History

```bash
git log --oneline                       # one line per commit
git log --oneline --graph --all         # visualize branches/merges
git log --author="Dhaval"               # commits by an author
git log --since="2 weeks ago"           # by time
git log -p <file>                       # full diff for each commit touching <file>
git blame <file>                        # who last changed each line
git show <commit>                       # show the full diff of a commit
```

## .gitignore — What Not to Track

```
# Common entries
__pycache__/
*.pyc
.env
.venv/
node_modules/
*.log
.DS_Store

# Project-specific
secrets.yaml
build/
```

Once a file is committed, `.gitignore` won't untrack it. You need:
```bash
git rm --cached <file>     # remove from git, keep local
```
...then commit the removal.

## Common Interview Questions

**Q: "Walk me through your git workflow."**
> "I create a feature branch off main, make commits as I go, push to remote when ready for review. Before opening the PR I usually rebase onto latest main to keep history clean. After review and merge, I delete the local branch."

**Q: "What's the difference between merge and rebase?"**
> "Merge preserves history as it happened; rebase rewrites history to look linear. I use merge for shared branches, rebase to clean up my own work before sharing. Golden rule: never rebase pushed commits."

**Q: "How do you handle a merge conflict?"**
> "Run `git status` to see conflicted files. Open each, find the conflict markers, edit to keep the right version. `git add` to mark resolved, then `git commit`."

**Q: "What if you accidentally `git reset --hard` and lost commits?"**
> "Check the reflog — every HEAD change is recorded for about 30 days. Find the lost commit hash, then either `git checkout <hash>` to inspect or `git reset --hard <hash>` to restore."

**Q: "What's the difference between `git reset` and `git revert`?"**
> "Reset moves the branch pointer back — rewrites history, only safe for local commits. Revert creates a new commit that undoes a previous one — preserves history, safe to use on pushed commits."

## What to Memorize vs Look Up

**Memorize:**
- The Daily Eight
- Branching workflow
- Merge vs rebase + the golden rule
- Conflict resolution steps
- Reset vs revert distinction
- Reflog exists

**Don't bother memorizing:**
- Every flag on every command
- Sub-commands you rarely use (filter-branch, bisect, submodule)

In an interview, "I'd use git revert for this — I always look up the exact syntax" is a fine answer. Senior engineers don't pretend to memorize everything; they know what to reach for.
