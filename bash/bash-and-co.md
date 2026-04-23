# TSC TIME
## sudo bash bash bash

### bash basics

- `echo -e` enables escape chars
- `\e`=esc char, `[`=starts ANSI seq
- `\e[31m`=red, `32m`=green, `34m`=blue, `0m`=reset

- `echo word1     word2` (tabs or extended spaces) are collapsed
   this is called *word splitting* =>**happens when " " are NOT used**
-  `echo "word1     word2"` spaces are NOT collapsed becase "..." prevent word splitting

> word splitting also happens on unquoted variables
```bash
a="1  2  3"
for i in $a; do echo "$i"; done  # splits into 1, 2, 3
```

Variables are defined WITHOUT SPACES AROUND `=` operator as literal strings
`foo="abc    def"; bar=1234` then
- `echo $foo$bar` ==> `abc def1234` (word splitting $\checkmark$)
- `echo "$foo$bar"` ==> `abc    def1234` (word splitting $\times$)
- `echo "${foo}XX${bar}` ==> `abc    defXX1234` (`${...}` to explicitly seperate variable names)

Command subst: `$(..)` or `` `...` ``

Note: *without double quotes* bash does WORD SPLITTING and GLOB SUBSTITUTION
*with double quotes* None (but allows ``$ ` !`` special chars)
*with single quotes* everything is literal

> [!warn]
> `ls *.sh` => all files ending in .sh ; `ls "*.sh"` => the file named `*.sh`

#### Variable defaults
`${var:-default}` -- if `var` is unset or empty, use `default` instead.
So `"${x:-30}"` means: use `x` if provided, else `30`.

| Syntax | Meaning |
|--------|---------|
| `${var:-val}` | use `val` if unset/empty |
| `${var:=val}` | use `val` AND assign it to `var` if unset/empty |

### ways of running a script

| Method        | Runs in Current Shell | Needs `chmod +x` | Variables persist in current shell? | Requires Shebang |
| ------------- | --------------------- | ---------------- | ----------------------------------- | ---------------- |
| `source a.sh` | YES                   | NO               | YES                                 | NO               |
| `./a.sh`      | NO (child proc)       | YES              | NO                                  | YES              |
| `bash a.sh`   | NO (child proc)       | NO               | NO                                  | NO               |


### Env vars
Print all using `env`

| Variable            | Description                                                               | Example Value                  |
| ------------------- | ------------------------------------------------------------------------- | ------------------------------ |
| `$HOME`             | Path to the current user's home directory                                 | `/home/user`                   |
| `$USER`             | Username of the currently logged-in user                                  | `john_doe`                     |
| `$PATH`             | Colon-separated list of directories for executable files                  | `/usr/local/bin:/usr/bin:/bin` |
| `$SHELL`            | Path to the user's default shell                                          | `/bin/bash`                    |
| `$PWD`              | Present working directory                                                 | `/home/user/projects`          |
| `$OLDPWD`           | Previous working directory                                                | `/home/user`                   |
| `$EDITOR`           | Default text editor for the user                                          | `vim` or `nano`                |
| `$LANG`             | System language and locale settings                                       | `en_US.UTF-8`                  |
| `$TERM`             | Terminal type (used by terminal emulators)                                | `xterm-256color`               |
| `$UID`              | User ID of the current user                                               | `1000`                         |
| `$EUID`             | Effective user ID (useful in scripts for checking root privileges)        | `0` (if root)                  |
| `$PS1`              | Primary prompt string (used for customizing shell prompt)                 | `\u@\h:\w\$`                   |
| `$PS2`              | Secondary prompt string (used for multi-line commands)                    | `>`                            |
| `$IFS`              | Internal field separator (controls word splitting)                        | `<space><tab><newline>`        |
| `$?`                | Exit status of the last executed command (0 = success, nonzero = failure) | `0` or `1`                     |
| `$$`                | Process ID (PID) of the current shell instance                            | `12345`                        |
| `$!`                | PID of the last background process                                        | `6789`                         |
| `$0`                | Name of the currently running script                                      | `script.sh`                    |
| `$1, $2, ...`       | Positional parameters (arguments passed to the script)                    | `arg1`, `arg2`, ...            |
| `$#`                | Number of arguments passed to the script                                  | `2`                            |
| `$*`                | All arguments as a single string                                          | `"arg1 arg2 arg3"`             |
| `$@`                | All arguments as separate strings                                         | `"arg1" "arg2" "arg3"`         |
| `$RANDOM`           | Generates a random number between 0 and 32767                             | `15862`                        |
| `$SECONDS`          | Number of seconds since the shell started                                 | `234`                          |
| `$LINENO`           | Current line number in a script (useful for debugging)                    | `42`                           |
| `$OSTYPE`           | Operating system type                                                     | `linux-gnu`                    |
| `$HOSTNAME`         | System hostname                                                           | `my-computer`                  |
| `$DISPLAY`          | X11 display server identifier (for GUI applications)                      | `:0`                           |
| `$XDG_SESSION_TYPE` | Current session type (e.g., X11 or Wayland)                               | `wayland`                      |

### conditional love

> **Always use spaces, do not trust Bash's tokenizing**

| Feature             | `[ ]`                      | `[[ ]]`                                                | `(( ))`                                   |
| ------------------- | -------------------------- | ------------------------------------------------------ | ----------------------------------------- |
| Remark              | basic condnl (depr)        | adv condl                                              | arith evals                               |
| Int compar          | `-eq, -lt, -gt`            | `-eq, -lt, -gt`                                        | `< > == !=`                               |
| Str compar          | `!=, ==`(requires quoting) | `!=, ==, >, <, =~` (regex)                             | X                                         |
| Logical op          | `-a (AND), -o (OR), !`     | `&& \|\| !`                                            | `&& \|\| !`                               |
| Word Splitting      | YES                        | NO                                                     | NO                                        |
| File testing        | `-f, -d, -e`               | `-f, -d, -e`                                           | NO                                        |
| Requires `$` prefix | YES                        | NO but preferred                                       | NO                                        |
| Supports `<=, =>`   | NO only -le, -ge           | NO only `> <` for str comp;<br>but can use -le,-ge<br> | YES numerically<br>& cant use -lt,-le,... |

> [!note]
> 1. In `[[ ]]`, `>,<` works on *strings* so `[[ 10 > 2 ]] && echo "yes"` does not work
>    Use `-gt, -lt` for numerical
> 2. Based on slides and some testing, inside `[[ ]]` or `(( ))`: `=` works same as ==

#### More on arithmetic
- `let "expr"` evaluates arithmetic expr in scope
```bash
let "a = 5 + 4"
echo $a  # 9
let "a++"
echo $a  # 10
```
- `declare -i num` forces variable to integer type
- `num=7.5` gives "error token .5"
- `num="asdf"` sets it to 0

#### Difference Between `(( ))` and `$(( ))` in Bash
*Both don't need $ prefixed variable names*

> **That's a lot of zeros.**

**`(( ))` = Arithmetic Evaluation then return 0/1 status**
- returns 0 or **true** if result != 0 ; returns 1 or **false** if result == 0
- used with `if` statements
```bash
a=5
b=3
if (( a < b || ! (a > 10) )); then
    echo "a is greater than b"
fi
# a is greater than b
```
- also used for in-place modification w/o returning value
```bash
y=1
(( y+=1 )) && echo "non-zero" || echo "zero"
(( y-=2 )) && echo "non-zero" || echo "zero"
(( y-=1 )) && echo "non-zero" || echo "zero"
# non-zero
# zero
# non-zero
```

**`$(( ))` = Arithmetic Evaluation and result is returned**
- used for returning exact values
```bash
a=3
b=5
result=$((a + b))  # 8
```


#### Floating-point
Bash does not support so need to use `bc` or `awk` as
`echo "3/4" | bc -l` prints `.75000000000000000000`

default scale (num of digits after `.` is 20)

supports internal variables as well as calling bash (external) variables with $ prefix

`echo "scale=3; a = 10; b = 3; a / b" | bc -l` prints `3.333`

> [!note] By default, shell *truncates* after dec point so `4/3, 5/3` both evalute to `1` (inside `let expr`)

#### On `bc` (basic calculator)
- In default mode, supports integer calculations
- `-l, --mathlib` Define the standard math library
- enables the use of `s(x)`, `c(x)`, `l(x)`, `e(x)`, `a(x)`;  [**sin, cos, log, exp, arctan**], respectively.
- also `sqrt(x)`
- sets precision to 20 (default) enabling floating point calculations
```bash
$ echo "(5 / 3 + 1) * 3 ; scale=3; (4 / 3 + 1) * 3 ; 5 < 3 ; 10 > 2" | bc
6
6.999
0
1
```

> [!note]
> ```
> Success == exit code 0 == TRUE
> Failure == exit code 1 == FALSE
> ```
> applies to both commands and condl expressions like `((...)), [...],...` 


### control flow and loops
String:
`-z` empty ; `-n` non-empty
File:
`-e` exists ; `-f` is file ; `-d` is directory ; `-s` is non empty ; `-r/w/x` is r/w/x

> Status code == 0 evals to TRUE but arithmetic 0 evals to FALSE

```bash
# \[\[ ]] for string and/or numeric expressions

if [[ -f file.txt ]]; then
	echo "its a file"
elif [[ -d file.txt ]]; then
	echo "its a directory"
else
	echo "its not a file or directory"
fi

# > works lexically!!! can be replaced with -gt
# NOTE: >= <= will NOT work in \[\[ ]]

if [[ 3 > 1 && (-z $someUndefinedVarASDF) ]]; then
	echo "should run"
fi

# (( )) for numeric expressions (non zero evals to true)

if ls non_existent_directory &>/dev/null; then
	echo "Printed if successful ie status code = 0"
else
	echo "Printed if fails ie status code != 0"
fi

some_command
if [[ $? ]]; then
	echo "Printed if fails ie status code != 0"
else
	echo "Printed if successful ie status code = 0"
# this is bad tho, prefer:
# if [[ $? -ne 0 ]]; then
# if some_command; then
fi
```

> [!warning] Notice the lack of parentheses in bash `for`

```bash
for i in foo bar baz; do
	echo "$i"  # prints foo\nbar\nbaz
done

for i in "foo bar baz"; do
	echo "$i"  # prints foo bar baz (single element)
done

for i in {1..5..2}; do
	echo "$i"  # prints 1\n3\n5 (start stop step, inclusive)
done

for i in "${arr[@]}"; do
	echo "$i"  # prints each el on new line (`"` disables word splitting)
done
```

```bash
a=5
while (( a < 7 )); do echo $((a++)); done
# prints 5 6 8 ; finally, a=7

b=5
until (( b > 7 )); do echo $((b++)); done
# prints 5 6 7 ; finally, b=8
```

#### Special Vars (for script and/or functions)
- `$0` name of script
- `$1, $2...` posnl arguments
- `$#` num of args
- `$@` all args separately (enclose in double quotes and iterate over it to get `$1, $2...`)
- `$*` all args as one string
- `$?` last exit status code
- `$$` shell's PID
- `$!` PID of last bg task
- `$_` last arg of last command

#### FUnctions
- `return n` to return status code
- `exit n` to exit script with status code
- For capturing/reusing/returning meaningful output stick to stdout (`echo`)

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

- default variables are global
- `local` to create variable scoped to immediate fn scope
- `export` to allow usage in child processes (like ENV vars are always usable in all child procs)

#### Reading input
```bash
while read -r line; do   # reads raw text into variable line
	echo "Line: $line"
done < "$file"           # redirects contents of $file into the above

# alternatively for mentioning it in script use: heredocs!!!
done <<EOF
This is Line 1
This is Line 2
EOF

# alternatively for long strings: herestrings!!!
done <<< "hello world!"
```

#### Read options

See `read.sh`!

| Option  | Meaning                                                |
| ------- | ------------------------------------------------------ |
| `-r`    | Don't interpret backslashes (`\`) as escape characters |
| `-p`    | Prompt before reading input                            |
| `-a`    | Read into an array                                     |
| `-n N`  | Read N characters only                                 |
| `-s`    | Silent input (e.g., for passwords)                     |
| `-t N`  | Timeout after N seconds                                |
| `-u FD` | Read from file descriptor FD                           |

> [!note] Use `IFS= read -r line` to prevent word splitting / trimming for reading files as it is

> [!note] heredocs and herestrings
> create heredocs with `<<SYMBOL`
> ```bash
> cat <<"EOF" > file
> hello
> world
> EOF
> ```
> quoting EOF disables var expansion inside heredoc
> 
> 
> create herestrings with `<< "string $someVar"`
> ```bash
> cat <<< "a singular string" > file
> ```
> 
> **GOATED SHIT: Reading separate fields/words into an array**
> `IFS=',' read -ar arr <<< "apple,orange,banana"` reads them individually as elements into array `arr`


#### pretty printing

`printf "%-10s %s %.2f %x\n" "str1" "str2" "3.156" "32"`
prints `str1       str2 3.16 20`

`%d`: decimal
`%x`: hex

| Syntax | Meaning                        | Example            |
| ------ | ------------------------------ | ------------------ |
| `%5s`  | Right-align string in 5 spaces | `"abc"` → `" abc"` |
| `%-5s` | Left-align                     | `"abc"` → `"abc "` |
| `%04d` | Pad integer with leading zeros | `5` → `0005`       |
| `%.2f` | 2 decimal places (rounding)    | `3.14159` → `3.14` |
- `printf` prints one string for each argument set passed!

```bash
printf "Line: %d\n" {1..3} > file.txt

name="John"
greeting=$(printf "Hello, %s!" "$name")
```


#### Arrays (read from slides thats it?)
```bash
arr=(foo bar baz "ohio rizz")  # 0 indexed

echo "${arr[1]}"  # bar
echo "${arr[@]}"      # all elements separately
echo "${#arr[@]}"     # number of elements

arr[2]="orange"

# slicing bash 4+
# arr[@]:start:length
echo "${arr[@]:1:2}"  # bar orange
echo "${arr[@]: -3: 2}"  # bar orange

unset 'arr[1]'  # delete, but keep slot empty
```

Speaking of empty slots:
```javascript
const arr = new Array(5);
arr.forEach((e) => {console.log(`{e}`); });
for(const e of arr) {console.log(`{e}`); }
```
---

### Assoc Arrays (Bash 4+)
```bash
declare -A capitals
capitals[India]="New Delhi"
capitals[France]="Paris"
capitals[Philly]="Scranton"

echo "${capitals[India]}"

echo "${!capitals[@]}"    # all keys
echo "${capitals[@]}"    # all values

for country in "${!capitals[@]}"; do
  echo "$country => ${capitals[$country]}"
done

```

### Shell Globbing
#### basic
|Pattern|Matches|
|---|---|
|`*`|Matches **zero or more** characters (except `/` in pathnames)|
|`?`|Matches **exactly one** character (except `/`)|
|`[abc]`|Matches **one** character from the set `a`, `b`, or `c`|
|`[a-z]`|Matches any **single character** in the range `a` to `z`|
|`[^abc]`|Matches a character **not** in the set|
|`[!abc]`|Same as `[^abc]` (negation)|

#### extended (works for me on bash 5.1)
requires enabling as `shopt -s extglob`

|Pattern|Meaning|
|---|---|
|`?(pattern)`|Matches **zero or one** occurrence|
|`*(pattern)`|Matches **zero or more** occurrences|
|`+(pattern)`|Matches **one or more** occurrences|
|`@(pattern)`|Matches **exactly one** occurrence|
|`!(pattern)`|Matches anything **except** the pattern|

> You can use `|` to separate alternatives inside the parentheses.

You can use glob patterns in **variable substitution** to manipulate strings (not files).
#### Prefix/Suffix Removal

One `%`/`#` = shortest match, two = longest (greedy).

```bash
str="report_final_version.txt"
echo "${str%_*}"   # report_final       (trim from end, short)
echo "${str%%_*}"  # report             (trim from end, greedy)
echo "${str#*_}"   # final_version.txt  (trim from start, short)
echo "${str##*_}"  # version.txt        (trim from start, greedy)
```

Idiomatic uses — these come up constantly:
```bash
path="/usr/local/bin/"
echo "${path%/}"          # /usr/local/bin   (strip trailing slash)

url="https://example.com/foo/bar"
echo "${url##*/}"         # bar              (basename)
echo "${url%/*}"          # https://example.com/foo  (dirname)

file="archive.tar.gz"
echo "${file%%.*}"        # archive          (strip all extensions)
echo "${file#*.}"         # tar.gz           (everything after first dot)
```

> Note: `basename` and `dirname` commands exist but the parameter expansion is faster in scripts (no subprocess).

#### shopt flags for globbing

| Flag | Effect |
|------|--------|
| `nullglob` | unmatched glob expands to nothing instead of literal |
| `failglob` | unmatched glob errors |
| `dotglob` | includes dotfiles in `*` matches |
| `globstar` | enables `**` for recursive matching |

#### Regex in `[[ =~ ]]`

ERE (same as `egrep`). Leave pattern unquoted or assign to variable first — quoting it makes bash treat it as a literal string.

```bash
# groups land in BASH_REMATCH
email="foo@example.com"
if [[ $email =~ ([a-z]+)@([a-z]+\.[a-z]+) ]]; then
  echo "${BASH_REMATCH[1]}"   # foo
  echo "${BASH_REMATCH[2]}"   # example.com
fi

# store pattern in var to use special chars safely
regex='^([0-9]{4})-([0-9]{2})-([0-9]{2})$'
[[ "2025-04-25" =~ $regex ]] && echo "${BASH_REMATCH[1]}"  # 2025
```

### String Manipulation

```bash
str="Hello, World!"
echo ${#str}        # 13         (length)
echo ${str:7:5}     # World      (substr: start, len)
echo ${str:7}       # World!     (substr: to end)

echo ${str/World/Bash}   # Hello, Bash! World!  (first)
echo ${str//World/Bash}  # Hello, Bash! Bash!   (global)

echo ${str^^}  # HELLO, WORLD!  (upper)
echo ${str,,}  # hello, world!  (lower)
echo ${str^}   # Hello, World!  (first char only)
```

Splitting into array:
```bash
IFS=',' read -ra arr <<< "apple,orange,banana"
echo ${arr[0]}   # apple
```

Whitespace trimming (gnarly but pure bash):
```bash
trimmed="${str#"${str%%[![:space:]]*}"}"   # leading
trimmed="${str%"${str##*[![:space:]]}"}"   # trailing
```
Or just pipe through `awk '{$1=$1};1'` for both sides.

---

### Note on redir

`0`=stdin, `1`=stdout, `2`=stderr

```bash
echo "err" >&2          # stdout → stderr (1>&2)
cmd 2>&1                # stderr → stdout
cmd 2>/dev/null         # silence stderr
cmd &>/dev/null         # silence both (shorthand for >f 2>&1)
cmd >out.txt 2>&1       # both to file
```

> [!warning] Order matters
> `cmd >out.txt 2>&1` Y both to file
> `cmd 2>&1 >out.txt` N stderr → terminal, stdout → file
> `2>&1` snapshots where stdout points *at that moment*

`&>file` is bash shorthand only -- not POSIX. ! `2&>1` is not valid syntax.

---

### bashception

| Command | Mechanism | Shell Level | Behavior |
| :--- | :--- | :--- | :--- |
| **`$(cmd)`** | **Subshell** | Child | Captures `stdout` as a string. |
| **`exec`** | **Overlay** | Replacement | Replaces current process image. |
| **`eval`** | **Re-parse** | Current | Executes a string as shell syntax. |

---

#### **1. Command Substitution `$( )`**
Used to nest the output of one command into another.
```bash
# Capture output into a variable
current_user=$(whoami)

# Use output directly as an argument
echo "The date is $(date +%D)"
```

#### **2. Process Replacement `exec`**
Replaces the current shell. The script stops here because the shell process is gone.
```bash
# Terminal becomes 'top'; closing 'top' exits the session
exec top

# Common in wrappers to hand off to another binary
exec ./my_heavy_application --daemon
```

#### **3. Evaluation `eval`**
Processes shell logic (pipes, redirects, variables) hidden inside strings.
```bash
# Execute complex syntax in variables
task="ls -l | sort -r"
eval $task

# Dynamic variable creation
name="ID"
val="123"
eval "USER_$name=$val"  # Creates $USER_ID

# Indirect referencing
pointer="target"
target="Hello World"
eval "echo \$$pointer"  # Accesses $target via $pointer

# Forcing brace expansion
range="{1..5}"
eval echo $range        # Expands to 1 2 3 4 5
```


#### **Specific `eval` Use Case: Environment Hooks**
Necessary for commands that output `export` statements intended to modify your **current** session.
```bash
# Without eval: output is just text
# With eval: variables like SSH_AUTH_SOCK are actually set
eval $(ssh-agent -s)
```

# sed

### Invocation & Flags

```bash
sed [OPTIONS]… [SCRIPT] [INPUT…]
```

| Flag        | Meaning                              |
| ----------- | ------------------------------------ |
| `-e script` | add script inline                    |
| `-f file`   | load script from file                |
| `-n`        | suppress automatic printing          |
| `-i[SUFFIX]`| edit in-place (optional backup)      |
| `-E` / `-r` | enable extended regex                |

### 1. Addressing Lines

| Address             | Effect                                     |
| ------------------- | ------------------------------------------ |
| `N`                 | line number N                              |
| `M,N`               | lines M through N                          |
| `/pat/`             | any line matching pat                      |
| `/start/,/end/`     | range from first `/start/` to next `/end/` |
| `/pat/!`            | any line **not** matching pat              |
| `$`                 | last line                                  |

```bash
sed -n '1,5d; /^$/!p' file.txt        # delete lines 1-5, print non-empty
sed '/ERROR/!d' logfile               # keep only lines matching ERROR
sed -n '/^BEGIN/,/^END/p' file.txt    # print between markers (inclusive)
sed '$d' file.txt                     # delete last line
sed -n '$p' file.txt                  # print last line
sed -n 'N;$!P;$p' file.txt           # print second-last line
```

### 2. Delete (`d`)

```bash
sed '6d' file.txt          # line 6
sed '1,5d' file.txt        # lines 1-5
sed '/^$/d' file.txt       # blank lines
```

### 3. Substitute (`s/pat/repl/[flags]`)

| Flag | Meaning                              |
| ---- | ------------------------------------ |
| `n`  | replace only nth occurrence per line |
| `g`  | global (all occurrences)             |
| `p`  | print line if substitution was made  |
| `I`  | case-insensitive                     |

```bash
sed 's/wolf/fox/' bigfile                          # first occurrence
sed '3s/wolf/fox/' bigfile                         # only on line 3
sed 's/wolf/fox/3gI' bigfile                       # 3rd+, case-insensitive
echo "Welcome To CS104" | sed 's/\(\b[A-Z]\)/(\1)/g'  # wrap capitals
```

### 4. Print (`p`)

```bash
sed '1p' bigfile               # line 1 (prints twice without -n)
sed -n '/scream/p' bigfile     # only matching lines
```

### 5. Append / Insert / Change

```bash
sed '2a tomato' fruits.txt     # append after line 2
sed '2i tomato' fruits.txt     # insert before line 2
sed '2c aam' fruits.txt        # replace line 2 entirely
sed '/mango/c aam' fruits.txt  # replace every line matching /mango/
```

### 6. Quit Early (`q`)

```bash
sed '5q' fruits.txt   # print first 5 lines then exit
```

### 7. Multiple Commands

```bash
sed 's/mango/aam/; s/banana/kela/' fruits.txt
sed -e 's/mango/aam/' -e 's/banana/kela/' fruits.txt

# order matters!
echo "please fix the light bulb!" \
  | sed 's/light/tube/g; s/bulb/light/g'
```

### 8. Back-References & `&`

`&` = the whole matched string; `\1`, `\2`, ... = captured groups

```bash
echo "AA BB CC" | sed 's/\([A-Z]\)\1/XX/g'           # replace doubles → XX
echo "I have 5 apples" | sed 's/[0-9]\+/[&]/g'        # wrap numbers in [ ]
```

### 9. In-Place Editing & Scripts

```bash
sed -i.bak 's/DEBUG/INFO/g' *.log   # edit in-place, backup to .bak
sed -f commands.sed file.txt         # run from script file
```

### 10. Non-Trivial Pattern Tricks

```bash
# last occurrence of "foo" on each line
sed 's/\(.*\)foo/\1bar/' file.txt

# second-last occurrence
sed -E 's/(.*)(foo)(.*)(foo)/\1\3bar/' file.txt

# delete everything before last comma
sed 's/.*,//' file.csv

# last colon-delimited field
sed -E 's/.*:([^:]+)/\1/' /etc/passwd

# lines outside range 10-20
sed '10,20!d' file.txt

# stop at first ERROR
sed '/ERROR/{p;q;}' logfile
```

### 11. Hold Space

The hold space is a secondary buffer separate from the pattern space. Useful for multi-line tricks.

| Command | Meaning                                      |
| ------- | -------------------------------------------- |
| `h`     | copy pattern space → hold space              |
| `H`     | append pattern space → hold space            |
| `g`     | copy hold space → pattern space              |
| `G`     | append hold space → pattern space            |
| `x`     | exchange pattern and hold space              |

```bash
# reverse file order (tac equivalent)
sed -n '1!G;h;$p' file.txt

# accumulate all lines, print once at end
sed -n 'H;${g;p}' file.txt

# remove duplicate consecutive lines
sed '$!N; /^\(.*\)\n\1$/!P; D' file.txt
```

---

## awk
#### Reading input w `getline`
`fruits` has 4 lines (input is only 3 lines so last one is repeated)

```
$ awk '
{
getline line < "-"
print "You typed: " line " (" length(line) ")"
}' <<EOF
tooez
ggs
fly
EOF
You typed: tooez (5)
You typed: ggs (3)
You typed: fly (3)
You typed: fly (3)
```

> [!abstract] `getline [var] [< file]`
> reads a line from file (by default the current input file) into var (or $0 if not specified)

![awk-on-getline.png]

#### Reading input from a command
Can be done via `<command> | getline <var to store it in>`
- Note, this only reads the first line of input.
- the next time u run the same statment, it reads the next line!
- to prevent this run `close(<command>)` to close the buffer or whatever
- `getline` returns
	- `1` if a record is successfully read
	- `0` if end of file (EOF) is reached
	- `-1` on error
- so a typical idiom is `while((cmd | getline) > 0) { ... }`

- Note, same happens when you do `getline line < "<filepath>" or "-" for stdout`
- run `close(<filename>)` to prevent reading from next line (it will reset to first line always)

#### Built-in Variables

| Variable | Meaning                                              | Default          |
| -------- | ---------------------------------------------------- | ---------------- |
| `NR`     | current record (line) number across all files        |                  |
| `NF`     | number of fields in current record                   |                  |
| `FS`     | input field separator                                | `" "` (whitespace) |
| `OFS`    | output field separator                               | `" "`            |
| `RS`     | input record separator                               | `"\n"`           |
| `ORS`    | output record separator                              | `"\n"`           |
| `FNR`    | record number within current file (resets per file)  |                  |
| `FILENAME` | name of current input file                         |                  |

#### BEGIN / END blocks

```bash
# BEGIN runs before any input is read; END runs after all input
awk 'BEGIN { print "start" } { sum += $1 } END { print "total:", sum }' file

# set FS in BEGIN instead of -F flag
awk 'BEGIN { FS=":" } { print $1 }' /etc/passwd
```

#### String manipulation and more
> [!note] NOTE
> 1. strings are **1-indexed**
> 2. regex matching (usually) returns ***longest, leftmost match***

- `length(string)`
- `substr(string, start[, len])` 
- `!~` for negating regex match

- `gensub(regexp, replacement, how [, target])` returns substituted string
  `how` = `"g"` means global, else pass number >= 1
  `target` is `$0` by default

- `index(in, find)` ret 0 if not found 
  
- `match(string, regexp[, array])` clears array and `arr[0]` full match and subsequent elements give matched groups
  
	- NOTE: for regexp as strings here, remember you have to **ESCAPE TWICE** so to match a literal `[` u need regex `\[` and hence use `\\[` in the definition of the regex pattern as a string

- `tolower/toupper`

- `split(string, array, delimiter)` splits the `string` into an array based on the `delimiter` (which defaults to whitespace). It returns the number of elements in the resulting array.
  
- `patsplit(string, array, pattern)` uses pattern instead of fixed delimiter

- `fflush([filename])` flush the buffer (stdout by default)
  
- `$0` gives whole record by default but running `$1=$1` forces it to reprocess and `$0` is rejoined using OFS instead of FS (which it was earlier)

- ![awk-on-fs.png]
- `FS == " "`
  Fields are separated by runs of whitespace. Leading and trailing whitespace are ignored. This is the default.

- `FS == any other single character`
  Fields are separated by each occurrence of the character. Multiple successive occurrences delimit empty fields, as do leading and trailing occurrences. The character can even be a regexp metacharacter; it does not need to be escaped.

- `FS == regexp`
  Fields are separated by occurrences of characters that match regexp. Leading and trailing matches of regexp delimit empty fields.

- `FS == ""`
  Each individual character in the record becomes a separate field. (This is a common extension; it is not specified by the POSIX standard.)
