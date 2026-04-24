# Challenge 2: I Like PIE

**Binary:** `ilikepie` | **Source:** provided

This is not a GDB question.

> [_Michael had chicken pot pie for lunch._](https://www.reddit.com/r/DunderMifflin/comments/9lt6lv/michael_had_chicken_pot_pie_for_lunch_actually/)
> [_Actually, let me rephrase that._](https://www.reddit.com/r/DunderMifflin/comments/y5onye/steve_carells_golden_globes_acceptance_speech/)
> [_Michael had an entire chicken pot pie for lunch._](https://www.reddit.com/r/theoffice/comments/1j962m9/the_office_meme_dump/)
> [_And  let me be more specific. Michael ate an entire family-sized chicken pot pie for lunch._](https://www.reddit.com/r/DunderMifflin/comments/1e80ot9/office_memes/)

---

## Setup

```bash
gcc -O0 -g -pie -fPIE ilikepie.c -o ilikepie
gdb ./ilikepie
# first run: set disable-randomization off
# in GDB
```

---

## Story

Jim compiled this binary as a Position Independent Executable - which means every time it runs, it loads at a *different address*. You can't just hardcode anything.

The binary is, however, *suspiciously helpful*. It tells you where it is. Figure out the rest.

GDB is your reconnaissance tool here. The actual exploit runs without GDB.

---

## Note:
Run `set disable-randomization off` in GDB, to ensure ASLR isn't disabled.

## Part A - Recon

### What's in the binary?

```
(gdb) info functions
```

How many functions are there? Which ones look like they're never called during normal execution?

### Where do things live?

```
(gdb) b main
(gdb) r
```

Now ask GDB for the address of every interesting function:

```
(gdb) p main
(gdb) p <other_functions>
```

Run it again. Do the addresses change? Run it five times. What *doesn't* change?

---

## Part B - Disassembly

Look at `main` in assembly:

```
(gdb) disas main
```

Find the instruction that prints the address. What register holds it? What does `lea` or `mov` into that register tell you?

Now disassemble the function you want to reach. Where does it start relative to `main`?

```
(gdb) disas <target_function>
```

Compute the offset. Is it positive or negative? Is it consistent across runs?

```
(gdb) p (long)<target> - (long)main
```

---

## Part C - The exploit

Now run the binary *without* GDB:

```bash
./ilikepie
```

It prints an address. Using your offset, compute the address of the function you want to call. Feed it back to the program.

```bash
echo "0x<computed_addr>" | ./ilikepie
```

Did it work? What printed?

---

## Part D - Without GDB

Can you find the offset using only static analysis - no running the binary at all?

```bash
objdump -d ilikepie | grep -A5 "<main>"
objdump -d ilikepie | grep -A5 "<target>"
```

The addresses in `objdump` output are fixed (relative to binary base). The offset between two functions in `objdump` is the same offset you'd compute in GDB.

What does this tell you about the relationship between static analysis and dynamic analysis?

---

## Hints

<details>
<summary>I computed the offset but my address crashes the program</summary>

Double-check your arithmetic. The offset can be negative (target is *before* main in memory). Also verify you're computing: `leaked_main + offset`, not `leaked_main - offset` or something else.

</details>

<details>
<summary>The program segfaults instead of printing the flag</summary>

You may have jumped to a decoy. Go back to `info functions` and look more carefully - which function name sounds like it has something worth printing?

</details>

<details>
<summary>I can't find the offset with objdump</summary>

`objdump -d ilikepie` shows all functions. The addresses shown are *relative to the binary's load base* (usually starting near `0x1000`). The difference between two function addresses there is the same as the runtime offset.

</details>
