# Challenge 1: Haha Password

**Binary:** `password` | **Source:** provided

Break in the steal the flag. There are 3 levels to this:
1. Noob: Read the source. Probably don't do this at all?
2. Pro: Do not use the source file, but use the debug symbols provided by `-g` flag.
3. Legend: assembly

TLDR: Basic GDB-based control flow manipulation

---

## Setup

```bash
cp password.c tmp.c && gcc -O0 -g -no-pie tmp.c -o password && rm tmp.c
gdb ./password
```

---

## Story

There's a flag locked behind a password. You don't know the password - and you don't need to. The goal isn't to find the password. The goal is to make the program *think* you did.

---

## Part A

### What's in here?

```
(gdb) info functions
```

How many functions are there? Which ones look interesting? Note that both the password check and the flag live somewhere in here.

### Break somewhere useful

Pick a function that looks like it makes a decision. Set a breakpoint. Run the program, type any password.

```
(gdb) b <function>
(gdb) r
```

You're now paused inside it. Look around:

```
(gdb) info args
(gdb) info locals
```

What do you see? Are any of these pointers? If so, what do they point to?

```
(gdb) x/s <pointer>
```

---

## Part B

You've found the check. Now you need to *bypass* it. You dont need the password.

Think about what the function returns and how the caller uses it. The function returns an `int`. Where does that `int` go after the function returns?

```
(gdb) finish
```

You're back in the caller, *before* the return value is used. Can you change it? There are two ways: modifying registers :fire:, or, a C variable :sad:

```
(gdb) set $rax = 1 // fire
(gdb) set <var> = 1 // sad: what variable is it?
(gdb) c
```

Did something happen? If not, think about what other breakpoints you should have set *before* running.

---

## Part C

You're now in the function that produces the flag. It doesn't print it immediately - it constructs it first.

Step through until the construction is done:

```
(gdb) n
(gdb) info locals
```

You should see a local buffer. Print it two ways:

```
(gdb) p <buffer_name>
(gdb) x/s <buffer_name>
```

What's the difference in output format between `p` and `x/s`?

---

## Part D - Read the assembly

This is where it gets real. Recompile stripped:

```bash
gcc -O0 -no-pie password.c -o password_stripped && strip password_stripped
gdb ./password_stripped
```

Now `info functions` is nearly empty. `info locals` shows nothing. You're flying blind.

```
(gdb) info functions
(gdb) b main
(gdb) r
(gdb) disas
```

Read the disassembly of `main`. What calls does it make? In x86-64, calls to unknown functions appear as `call 0x<addr>`. Set breakpoints on those addresses directly:

```
(gdb) b *0x<addr>
(gdb) c
```

When you land, disassemble what you're in:

```
(gdb) disas
```

Read the `cmp` and `je`/`jne` instructions. What is being compared? What happens if the comparison is equal vs not equal? Can you find the branch that leads to the flag, and jump straight to it?

```
(gdb) set $rip = 0x<addr_past_the_branch>
(gdb) c
```

The flag will be somewhere in memory after the decryption. Find the `call` that produces it, let it return, then scan the stack:

```
(gdb) x/s $rsp
(gdb) x/40xb $rsp
```

---

## Hints

<details>
<summary>I can't find the function that checks the password</summary>

There's no function literally named `check_password` - look at what `main` calls. Every `call` instruction in `main`'s disassembly is a candidate. Try them all.

</details>

<details>
<summary>set $rax = 1 didn't work</summary>

You need to be at the right moment - *after* `finish` returns you to the caller, *before* the `test`/`cmp` on `eax` executes. Step one instruction at a time with `ni` and watch when `eax` gets tested.

</details>

<details>
<summary>I can see the flag buffer but it's garbage</summary>

The decryption hasn't run yet. You broke too early. Step (`n`) until the call to the decryption function returns, *then* inspect the buffer.

</details>
