# Linux Shell Skills

This article covers the Linux text-processing tools that come up in interviews and daily work: grep, awk, sed, find, xargs, and friends. Then it answers the question you'll be asked at some point: "when do you use shell vs. Python?"

The goal is **fluency, not mastery**. You don't need to memorize every flag — you need to recognize which tool to reach for and know enough syntax to write a working one-liner.

## grep — Search Text

The bread and butter of log diagnosis. Search a file (or many) for lines matching a pattern.

```bash
grep "ERROR" app.log                       # lines containing ERROR
grep -i "error" app.log                    # case-insensitive
grep -v "DEBUG" app.log                    # INVERT — lines NOT containing DEBUG
grep -r "TODO" .                           # recursive in current dir
grep -n "ERROR" app.log                    # show line numbers
grep -c "ERROR" app.log                    # just count
grep -A 3 -B 1 "ERROR" app.log             # 3 lines After, 1 Before each match
grep -E "ERROR|WARN" app.log               # extended regex (or)
```

**Recognize when to use grep:** anytime you're searching plain text for a pattern. It's almost always the first tool you reach for when reading logs.

## awk — Column-Wise Processing

Awk treats each line as fields (default: whitespace-separated). Powerful for tabular data and per-line computation.

```bash
awk '{print $1}' file               # print first column
awk '{print $1, $3}' file           # 1st and 3rd
awk '{print $NF}' file              # last column ($NF = number of fields)
awk -F',' '{print $2}' file.csv     # CSV — comma-separated
awk '$3 > 100 {print $1}' file      # conditional: print col 1 where col 3 > 100
awk '{sum += $1} END {print sum}' file   # sum a column
awk 'NR > 1' file                   # skip first line (header)
```

**Recognize when to use awk:** when the data has columns and you need to filter, transform, or compute on those columns. Especially good for log files with structured formats.

## sed — Stream Editor (Find/Replace)

Sed's main job is substitution.

```bash
sed 's/old/new/' file                  # replace FIRST occurrence per line
sed 's/old/new/g' file                 # replace ALL occurrences (global)
sed -i 's/old/new/g' file              # in-place edit (modifies file directly)
sed -i.bak 's/old/new/g' file          # in-place edit with .bak backup
sed -n '5,10p' file                    # print lines 5-10 only
sed '/pattern/d' file                  # DELETE lines matching pattern
```

**Recognize when to use sed:** find/replace across one or many files, or extracting specific line ranges. Use `-i` carefully — it modifies files.

## find — Locate Files

Find files by name, type, size, modification time.

```bash
find . -name "*.py"                       # all .py files recursively
find . -type f -name "*.log"              # only regular files (not dirs)
find . -type d -name "logs"               # only directories
find . -mtime -7                          # modified in last 7 days
find . -mtime +30                         # modified MORE than 30 days ago
find . -size +100M                        # bigger than 100MB
find /var/log -name "*.log" -delete       # find AND delete (be careful)
```

**Recognize when to use find:** "find all X" questions — by name, age, size, or type.

## xargs — Pipe Output to Another Command

Some commands don't accept piped stdin (like `rm`). `xargs` converts piped input into command arguments.

```bash
find . -name "*.log" | xargs rm           # delete all .log files
find . -name "*.py" | xargs grep "TODO"   # grep TODO in all .py files
echo "1 2 3" | xargs -n 1 echo            # one arg per call
ls | xargs -I {} mv {} {}.bak             # rename each file to .bak
```

**Recognize when to use xargs:** when you want to feed `find` (or any text output) into a command like `rm`, `mv`, `cp`, `grep`.

## sort + uniq — The Classic Combo

```bash
sort file                                 # alphabetical
sort -n file                              # numerical
sort -rn file                             # numerical reverse
sort -k 2 file                            # sort by 2nd column

uniq file                                 # remove ADJACENT duplicates
sort file | uniq                          # actually unique (after sort)
sort file | uniq -c                       # with COUNT
sort file | uniq -c | sort -rn            # top by frequency
```

**The "count occurrences" combo:**
```bash
awk '{print $1}' log | sort | uniq -c | sort -rn | head -10
# Top 10 most frequent first-column values
```

Memorize this combo. It comes up constantly.

## Other Useful Commands

```bash
cut -d',' -f1,3 file.csv     # cut: columns by delimiter (lighter than awk)
head -20 file                # first 20 lines
tail -20 file                # last 20 lines
tail -f app.log              # FOLLOW (stream new lines as they arrive)
wc -l file                   # count lines
wc -w file                   # count words
tr 'A-Z' 'a-z' < file        # translate chars (lowercase here)
diff file1 file2             # line-by-line difference
```

## Pipes and Redirection

```bash
cmd1 | cmd2                  # stdout of cmd1 → stdin of cmd2
cmd > file                   # write stdout to file (overwrite)
cmd >> file                  # APPEND stdout to file
cmd 2> errors                # write STDERR to file
cmd > out 2>&1               # combine stdout and stderr into one file
cmd < input                  # read stdin from file
```

The combo you'll use most:
```bash
my_script.sh > out.log 2>&1 &      # run in background, capture everything
```

## When to Use Shell vs Python

This question comes up in interviews. Here's a clean answer:

| Use shell when... | Use Python when... |
|---|---|
| One-liner with pipes | More than 5 lines of logic |
| Quick text munging in a terminal | Need data structures (dicts, lists of objects) |
| Filtering or analyzing log files | Anything that needs unit tests |
| Composing standard Unix tools | Error handling beyond exit codes |
| Throwaway exploration | Will be re-run > 3 times |
| Single source of input | Multiple data sources to join |

**The rule of thumb:** if you find yourself writing `if`/`for`/function definitions in bash, you should be in Python.

**Bash strengths:** pipes are unbeatable for composing tools. `grep | awk | sort | uniq` is more concise than the Python equivalent.

**Bash weaknesses:** error handling, debugging, data structures, anything beyond ~20 lines becomes painful.

## Shell Scripting Basics (If You Need to Write One)

```bash
#!/bin/bash
set -euo pipefail     # exit on error, undefined var, or pipe failure

# Variables
NAME="world"
echo "Hello $NAME"

# Conditionals
if [ -f "/etc/hosts" ]; then
    echo "exists"
fi

# Loops
for file in *.log; do
    echo "processing $file"
done

# Functions
greet() {
    echo "hi $1"
}
greet "alice"

# Capture command output
COUNT=$(grep -c ERROR app.log)
echo "found $COUNT errors"
```

**Always include `set -euo pipefail` at the top.** It catches errors that bash would otherwise silently ignore — the difference between a robust script and a fragile one.

## What to Say in an Interview

> "For log analysis I lean on the standard chain — `grep` to filter, `awk` for column work, `sort | uniq -c | sort -rn` for frequency counting. For find/replace across multiple files, `sed -i`. Once the logic gets past a one-liner, I switch to Python because the error handling and data structure story is much better there."

That answer signals you've actually used these tools in anger, not just read about them.
