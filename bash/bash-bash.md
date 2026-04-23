# TSC TIME
## sudo bash bash bash

### bash basics

- **`echo -e`** enables escape chars — `\e[31m`=red, `32m`=green, `34m`=blue, `0m`=reset

---

- **Word splitting** — bash collapses unquoted whitespace and splits on `$IFS`
```bash
a="1  2  3"
for i in $a;   do echo "$i"; done   # splits: 1 / 2 / 3
for i in "$a"; do echo "$i"; done   # no split: "1  2  3"
```

- Variables defined **without spaces** around `=`
```bash
foo="abc    def"; bar=1234
echo $foo$bar      # abc def1234       (word splitting ✓)
echo "$foo$bar"    # abc    def1234    (word splitting ✗)
echo "${foo}XX"    # abc    defXX      (${} to delimit var name)
```

- **Quoting rules:**
  - no quotes → word splitting + glob substitution
  - `"..."` → no splitting, but `$ \` `` ` `` still special
  - `'...'` → everything literal

> [!warning]
> `ls *.sh` matches files ending in `.sh` — `ls "*.sh"` looks for a file literally named `*.sh`

---

#### Variable defaults

**`${var:-default}`** — use `default` if `var` is unset or empty

| Syntax | Meaning |
|--------|---------|
| `${var:-val}` | use `val` if unset/empty |
| `${var:=val}` | use `val` AND assign to `var` if unset/empty |
| `${var:+val}` | use `val` if set (opposite) |
| `${var:?msg}` | error + exit if unset/empty |

---

### ways of running a script

| Method | Current Shell | Needs `chmod +x` | Vars persist | Shebang |
| --- | --- | --- | --- | --- |
| `source a.sh` | YES | NO | YES | NO |
| `./a.sh` | NO (child) | YES | NO | YES |
| `bash a.sh` | NO (child) | NO | NO | NO |

---

### Env vars
Print all using **`env`**

| Variable | Description | Example |
| --- | --- | --- |
| `$HOME` | home directory | `/home/user` |
| `$PATH` | colon-separated executable dirs | `/usr/local/bin:/usr/bin` |
| `$PWD` / `$OLDPWD` | current / previous working dir | |
| `$SHELL` | current shell binary | `/bin/bash` |
| `$USER` / `$UID` / `$EUID` | user name / id / effective id | |
| `$IFS` | internal field separator (word splitting!) | `<space><tab><newline>` |
| `$PS1` / `$PS2` | primary / secondary prompt | `\u@\h:\w\$` |
| `$?` | last exit status (0=success) | |
| `$$` / `$!` | PID of shell / last bg process | |
| `$0` | script name | |
| `$1, $2...` / `$#` | positional args / arg count | |
| `$@` | all args as separate strings | |
| `$*` | all args as one string | |
| `$RANDOM` | random 0–32767 | |
| `$LINENO` | current line number | |

---

### conditional love

> [!note] **Always use spaces inside `[ ]` and `[[ ]]` — bash tokenizes on whitespace**

| Feature | `[ ]` | `[[ ]]` | `(( ))` |
| --- | --- | --- | --- |
| Use for | basic (deprecated) | strings + regex | arithmetic |
| Int compare | `-eq -lt -gt` | `-eq -lt -gt` | `< > == !=` |
| Str compare | `== !=` (quoted) | `== != > < =~` | ✗ |
| Logical | `-a -o !` | `&& \|\| !` | `&& \|\| !` |
| Word splitting | YES | NO | NO |
| File tests | `-f -d -e` | `-f -d -e` | NO |
| `$` prefix | required | preferred | not needed |

> [!note]
> In `[[ ]]`, `>` and `<` are **lexicographic** — `[[ 10 > 2 ]]` is false. Use `-gt`/`-lt` for numbers.

String tests: **`-z`** empty, **`-n`** non-empty
File tests: **`-e`** exists, **`-f`** file, **`-d`** dir, **`-s`** non-empty, **`-r/w/x`** perms

---

#### Arithmetic — `let`, `(( ))`, `$(( ))`

```bash
let "a = 5 + 4"   # evaluates in place, a=9
let "a++"          # a=10
declare -i num     # forces integer; num="asdf" → 0, num=7.5 → error
```

> [!note] **`(( ))` vs `$(( ))`**

**`(( ))`** — evaluates, returns exit status (nonzero result = true, zero = false)
```bash
if (( a > b )); then echo "yes"; fi

y=1
(( y+=1 )) && echo "non-zero" || echo "zero"   # non-zero
(( y-=2 )) && echo "non-zero" || echo "zero"   # zero
```

**`$(( ))`** — evaluates and **returns the value**
```bash
result=$(( a + b ))
echo "next: $(( i + 1 ))"
```

---

#### Floating-point with `bc`

Bash truncates integer division — `4/3` → `1`. Use `bc`:

```bash
echo "3/4" | bc -l                           # .75000...  (-l sets scale=20)
echo "scale=3; 10 / 3" | bc                  # 3.333
echo "(5/3 + 1) * 3 ; 5 < 3 ; 10 > 2" | bc  # 6 / 0 / 1
```

**`-l`** loads mathlib: `s(x)` `c(x)` `l(x)` `e(x)` `a(x)` = sin, cos, log, exp, arctan; also `sqrt(x)`

> [!note]
> ```
> exit code 0 == SUCCESS == TRUE
> exit code 1 == FAILURE == FALSE
> ```
> applies to commands AND conditional expressions `((...))`, `[...]`, etc.

---

### control flow and loops

```bash
if [[ -f file.txt ]]; then
    echo "file"
elif [[ -d file.txt ]]; then
    echo "dir"
fi

# use command exit status directly
if ls somedir &>/dev/null; then echo "exists"; fi

# $? anti-pattern — prefer the above
some_cmd
if [[ $? -ne 0 ]]; then echo "failed"; fi   # ok but verbose
```

> [!warning] **No parentheses in bash `for`**

```bash
for i in foo bar baz; do echo "$i"; done        # foo / bar / baz
for i in "foo bar baz"; do echo "$i"; done      # foo bar baz  (one element)
for i in {1..5..2}; do echo "$i"; done          # 1 3 5  (start..end..step)
for i in "${arr[@]}"; do echo "$i"; done        # iterate array safely
```

```bash
a=5
while (( a < 7 )); do echo $((a++)); done   # 5 6 ; a=7

b=5
until (( b > 7 )); do echo $((b++)); done   # 5 6 7 ; b=8
```

---

#### Functions

- **`return n`** — return exit status code
- **`exit n`** — exit the whole script
- **Return values via stdout** — capture with `$(fn)`

```bash
factorial() {
    if [[ $1 -le 1 ]]; then
        echo 1
    else
        local temp=$(( $1 - 1 ))
        local result=$(factorial "$temp")
        echo $(( $1 * result ))
    fi
}
```

- **`local`** — scoped to function; default is global
- **`export`** — visible to child processes

---

#### Reading input

```bash
while IFS= read -r line; do    # IFS= preserves leading whitespace
    echo "$line"
done < "$file"
```

| Option | Meaning |
| --- | --- |
| **`-r`** | raw — don't interpret `\` |
| `-p` | prompt string |
| `-a` | read into array |
| `-n N` | read N chars |
| `-s` | silent (passwords) |
| `-t N` | timeout N seconds |

> [!note] **Heredoc vs herestring**
> ```bash
> cmd <<EOF          # heredoc — multi-line, var expansion on
> cmd <<"EOF"        # heredoc — var expansion OFF
> cmd <<< "string"   # herestring — single string
> ```
> **Split CSV into array:** `IFS=',' read -ra arr <<< "a,b,c"`

---

#### pretty printing

**`printf "FORMAT" args`** — like C printf, repeats format for multiple arg sets

| Spec | Meaning | Example |
| --- | --- | --- |
| `%-10s` | left-align in 10 chars | `"abc"` → `"abc       "` |
| `%5s` | right-align | `"abc"` → `"  abc"` |
| `%04d` | zero-pad int | `5` → `0005` |
| `%.2f` | 2 decimal places | `3.14159` → `3.14` |
| `%x` | hex | `32` → `20` |

```bash
printf "Line: %d\n" {1..3}                  # repeats format per arg
greeting=$(printf "Hello, %s!" "$name")     # capture with $()
```

---

#### Arrays

```bash
arr=(foo bar baz "ohio rizz")   # 0-indexed

echo "${arr[1]}"          # bar
echo "${arr[@]}"          # all elements
echo "${#arr[@]}"         # count

echo "${arr[@]:1:2}"      # bar baz      (slice: start, len)
echo "${arr[@]: -2}"      # baz "ohio rizz"  (from end)

unset 'arr[1]'            # deletes element, leaves hole
```

> [!warning] **Deleted slots leave holes** — `${#arr[@]}` counts remaining elements but indices don't repack. Same gotcha as JS sparse arrays.

---

#### Assoc Arrays (Bash 4+)

```bash
declare -A capitals
capitals[India]="New Delhi"
capitals[France]="Paris"

echo "${!capitals[@]}"    # all keys
echo "${capitals[@]}"     # all values

for k in "${!capitals[@]}"; do
    echo "$k => ${capitals[$k]}"
done
```

---

### Shell Globbing

| Pattern | Matches |
|---------|---------|
| `*` | zero or more chars (not `/`) |
| `?` | exactly one char |
| `[abc]` | one char from set |
| `[a-z]` | one char in range |
| `[^abc]` / `[!abc]` | negation |

**Extended** (`shopt -s extglob`):

| Pattern | Meaning |
|---------|---------|
| `?(pat)` | zero or one |
| `*(pat)` | zero or more |
| `+(pat)` | one or more |
| `@(pat)` | exactly one |
| `!(pat)` | anything except |

Use `|` for alternatives inside parens: `+(foo|bar)`

**`shopt` flags:**

| Flag | Effect |
|------|--------|
| `nullglob` | unmatched glob → empty (not literal) |
| `failglob` | unmatched glob → error |
| `dotglob` | `*` includes dotfiles |
| `globstar` | `**` matches recursively |

---

#### Prefix/Suffix Removal

**`%`/`#` = trim from end/start; double = greedy**

```bash
str="report_final_version.txt"
echo "${str%_*}"    # report_final       (end, short)
echo "${str%%_*}"   # report             (end, greedy)
echo "${str#*_}"    # final_version.txt  (start, short)
echo "${str##*_}"   # version.txt        (start, greedy)
```

**Idiomatic uses:**
```bash
path="/usr/local/bin/"
echo "${path%/}"          # /usr/local/bin      (strip trailing slash)

url="https://example.com/foo/bar"
echo "${url##*/}"         # bar                 (basename)
echo "${url%/*}"          # https://example.com/foo  (dirname)

file="archive.tar.gz"
echo "${file%%.*}"        # archive             (strip all extensions)
echo "${file#*.}"         # tar.gz              (after first dot)
```

> `basename`/`dirname` commands exist but parameter expansion avoids a subprocess.

---

#### Regex in `[[ =~ ]]`

**ERE** (same as `egrep`). Leave pattern **unquoted** or store in variable — quoting makes it literal.

```bash
email="foo@example.com"
[[ $email =~ ([a-z]+)@([a-z]+\.[a-z]+) ]]
echo "${BASH_REMATCH[0]}"   # full match
echo "${BASH_REMATCH[1]}"   # foo
echo "${BASH_REMATCH[2]}"   # example.com

regex='^([0-9]{4})-([0-9]{2})-([0-9]{2})$'
[[ "2025-04-25" =~ $regex ]] && echo "${BASH_REMATCH[1]}"   # 2025
```

---

### String Manipulation

```bash
str="Hello, World!"
echo ${#str}              # 13           (length)
echo ${str:7:5}           # World        (substr: start, len)
echo ${str:7}             # World!       (to end)

echo ${str/World/Bash}    # Hello, Bash! World!   (first)
echo ${str//World/Bash}   # Hello, Bash! Bash!    (global)

echo ${str^^}             # HELLO, WORLD!   (upper)
echo ${str,,}             # hello, world!   (lower)
echo ${str^}              # Hello, World!   (first char only)
```

Whitespace trimming (gnarly but pure bash — or just use `awk '{$1=$1};1'`):
```bash
trimmed="${str#"${str%%[![:space:]]*}"}"    # leading
trimmed="${str%"${str##*[![:space:]]}"}"    # trailing
```

---

### Redirection & File Descriptors

**`0`**=stdin **`1`**=stdout **`2`**=stderr

```bash
echo "err" >&2          # stdout → stderr
cmd 2>&1                # stderr → stdout
cmd 2>/dev/null         # silence stderr
cmd &>/dev/null         # silence both
cmd >out.txt 2>&1       # both to file ✅
cmd 2>&1 >out.txt       # ❌ stderr → terminal, stdout → file
```

> [!warning] **Order matters** — `2>&1` snapshots where stdout points *at that moment*

`&>file` is bash shorthand only — not POSIX. `2&>1` is **not valid**.

---

### bashception

| Command | Mechanism | Shell Level | Behavior |
| --- | --- | --- | --- |
| **`$(cmd)`** | Subshell | Child | Captures stdout as string |
| **`exec`** | Overlay | Replacement | Replaces current process image |
| **`eval`** | Re-parse | Current | Executes string as shell syntax |

---

#### `$( )` Command Substitution
```bash
current_user=$(whoami)
echo "The date is $(date +%D)"
```

#### `exec`
**Replaces the current shell** — nothing after it runs.
```bash
exec top                          # terminal becomes top; close top = session ends
exec ./my_heavy_application       # hand off to binary in wrapper scripts
```

#### `eval`
**Re-parses a string as shell syntax** — pipes, redirects, expansions all work.
```bash
task="ls -l | sort -r"
eval $task

eval "USER_$name=$val"            # dynamic variable names

pointer="target"; target="Hello"
eval "echo \$$pointer"            # indirect reference → Hello

range="{1..5}"
eval echo $range                  # brace expansion → 1 2 3 4 5
```

**Key use case — environment hooks:**
```bash
eval $(ssh-agent -s)   # output contains export statements; eval applies them to current shell
```

---

# sed

### Invocation

```bash
sed [OPTIONS] [SCRIPT] [INPUT]
```

| Flag | Meaning |
| --- | --- |
| `-e script` | inline script |
| `-f file` | script from file |
| **`-n`** | suppress auto-print |
| `-i[SUFFIX]` | in-place (optional backup) |
| `-E` / `-r` | extended regex |

---

### Addressing

| Address | Effect |
| --- | --- |
| `N` | line N |
| `M,N` | lines M–N |
| `/pat/` | matching lines |
| `/start/,/end/` | range (inclusive) |
| `/pat/!` | **non**-matching lines |
| `$` | last line |

```bash
sed -n '/^BEGIN/,/^END/p' file     # print between markers
sed '/ERROR/!d' log                # keep only ERROR lines
sed -n 'N;$!P;$p' file            # print second-last line
```

---

### Commands

**`d`** delete, **`p`** print, **`q`** quit, **`a`** append, **`i`** insert, **`c`** change

```bash
sed '1,5d' file                    # delete lines 1-5
sed '/^$/d' file                   # delete blank lines
sed -n '/scream/p' file            # print matching only
sed '5q' file                      # first 5 lines then quit
sed '2a tomato' fruits             # append after line 2
sed '2c aam' fruits                # replace line 2
sed '/mango/c aam' fruits          # replace matching lines
```

---

### Substitute `s/pat/repl/[flags]`

| Flag | Meaning |
| --- | --- |
| `g` | all occurrences |
| `n` | nth occurrence |
| `p` | print if substituted |
| `I` | case-insensitive |

**`&`** = whole match; **`\1 \2`** = capture groups

```bash
sed 's/wolf/fox/3gI' file                          # 3rd+ occurrence, case-insensitive
echo "AA BB" | sed 's/\([A-Z]\)\1/XX/g'            # replace doubles → XX
echo "5 apples" | sed 's/[0-9]\+/[&]/g'            # wrap numbers → [5]
echo "light bulb" | sed 's/light/tube/g; s/bulb/light/g'  # order matters!
```

---

### Non-Trivial Tricks

```bash
sed 's/\(.*\)foo/\1bar/' file          # replace LAST occurrence of foo
sed 's/.*,//' file                     # delete everything before last comma
sed -E 's/.*:([^:]+)/\1/' /etc/passwd # last colon-delimited field
sed '10,20!d' file                     # keep only lines 10-20
sed '/ERROR/{p;q;}' log               # print first ERROR then quit
```

---

### Hold Space

**Secondary buffer** — pattern space is the current line; hold space persists across lines.

| Cmd | Action |
| --- | --- |
| `h` / `H` | copy / append pattern → hold |
| `g` / `G` | copy / append hold → pattern |
| `x` | exchange |

```bash
sed -n '1!G;h;$p' file                          # reverse file (tac)
sed '$!N; /^\(.*\)\n\1$/!P; D' file             # remove consecutive duplicates
```

---

## awk

#### Reading input w `getline`

> **`getline [var] [< file]`** — reads next line from file into var (default: `$0` from current input)

```
$ awk '{ getline line < "-"; print line, length(line) }' <<EOF
tooez
ggs
fly
EOF
```

![awk-on-getline.png]

---

#### Reading from a command

**`cmd | getline var`** — reads one line at a time from command output; call `close(cmd)` to reset.

```bash
while((cmd | getline line) > 0) { print line }   # idiomatic
```

`getline` returns `1` (ok), `0` (EOF), `-1` (error).

---

#### Built-in Variables

| Variable | Meaning | Default |
| --- | --- | --- |
| **`NR`** | record number (global) | |
| **`NF`** | field count in current record | |
| **`FS`** | input field separator | `" "` |
| **`OFS`** | output field separator | `" "` |
| `RS` | input record separator | `"\n"` |
| `ORS` | output record separator | `"\n"` |
| `FNR` | record number within current file | |
| `FILENAME` | current file name | |

---

#### BEGIN / END

```bash
awk 'BEGIN { FS=":"; print "start" }
     { sum += $1 }
     END { print "total:", sum }' file

awk 'BEGIN { FS=":" } { print $1 }' /etc/passwd   # same as -F":"
```

---

#### String Functions

> [!note] Strings are **1-indexed**. Regex returns **longest leftmost match**.

- **`length(s)`**, **`substr(s, start[, len])`**, **`index(s, find)`** (0 if not found)
- **`tolower(s)`** / **`toupper(s)`**
- **`split(s, arr, delim)`** — splits into array, returns count
- **`gensub(re, repl, how[, target])`** — `how="g"` or integer; returns new string
- **`match(s, re[, arr])`** — `arr[0]`=full match, `arr[1]`...=groups
- **`patsplit(s, arr, pat)`** — like split but uses pattern
- **`fflush()`** — flush output buffer

**Rebuilding `$0`:**
```bash
$1=$1    # forces $0 to be rebuilt using OFS instead of original FS
```

---

#### FS Behavior

![awk-on-fs.png]

- **`FS=" "`** (default) — split on runs of whitespace, trim leading/trailing
- **`FS="x"`** (single char) — split on every occurrence; consecutive → empty fields
- **`FS="regexp"`** — split on regex matches
- **`FS=""`** — each character becomes its own field
