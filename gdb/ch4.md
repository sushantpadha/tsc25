# Challenge 4: Broken Pathfinder

**Binary:** `astar` | **Source:** provided

> _"Simplicity is a great virtue but it requires hard work to achieve it and education to appreciate it. And to make matters worse: complexity sells better."   ~Edger Dijkstra_

Debug A* using GDB.

---

## Setup

```bash
g++ -O0 -g -no-pie astar.cpp -o astar
```

### Test input (save as `test.txt`)

```
5 5
0 0.0 0.0
1 5.0 0.0
2 1.0 0.0
3 2.0 3.0
4 4.0 3.0
0 2 0.1
2 3 0.1
3 4 0.1
4 1 0.1
0 1 1.0
0 1
```

```bash
./astar < test.txt
```

Expected:
```
MISMATCH — A* is wrong!
```

---

## Story

A* and Dijkstra run on the same graph. Dijkstra is correct by construction. A* disagrees. No crash, no assert — just a wrong answer. There are two bugs. Find them.

---

## Part A — Understand the algorithm

Before you debug, be clear on what A* is supposed to do:

- `g_score[v]` = true cost from source to `v` found so far
- `f_score[v]` = `g_score[v] + h(v)`, where `h(v)` is the heuristic estimate of remaining cost to target
- The heuristic must be **admissible**: `h(v) <= true_remaining_cost(v)`. If it overestimates, A* can return a suboptimal path.

---

## Part B — Watch the algorithm run

```bash
gdb ./astar
(gdb) b a_star
(gdb) r < test.txt
```

Set up live tracking of the score arrays:

```
(gdb) display g_score[0]
(gdb) display g_score[1]
(gdb) display g_score[2]
(gdb) display g_score[3]
(gdb) display g_score[4]
```

Step through the outer loop with `n`. After each iteration, look at which node was popped and how the g_scores changed. Do they ever update in a way that seems wrong?

Now go into the relaxation inner loop. After `f_score[v]` is computed:

```
(gdb) info locals
```

Look at every value. Is the heuristic term being computed correctly for *each* node `v`? Or is something reused?

---

## Part C — The stale entry check

Find the condition near the top of the outer loop that skips already-processed entries. Read it carefully.

Set a conditional breakpoint on that line. Try to construct a condition that fires when the skip *shouldn't* happen:

```
(gdb) b astar.cpp:<line> if <condition involving f and f_score and in_closed>
```

When it fires, print everything:

```
(gdb) p f
(gdb) p f_score[u]
(gdb) p in_closed[u]
```

Is this node being skipped when it shouldn't be?

---

## Part D — Execution control practice

Break inside `a_star` at the start of the edge relaxation loop.

Practice these three operations and understand the difference:
- `s` — step *into* the next function call
- `n` — step *over* it
- `finish` — run until the current function returns

Step into `euclidean`. Inspect its arguments:

```
(gdb) info args
```

Then `finish` back to `a_star`. The return value is in `$rax` (as a float, check with `p (double)$xmm0` on x86-64).

Now set a conditional breakpoint that fires only at the last iteration:

```
(gdb) b astar.cpp:<outer_while_line> if open.size() == 0
```

What is the state of `g_score` at that point?

---

## Part E — Fix and verify

Fix both bugs. Recompile. Run on `test.txt`.

```
Results agree.
```

---

## Hints

<details>
<summary>I can't see what's wrong in the locals</summary>

In the relaxation loop, look specifically at how `f_score[v]` is computed. Is the heuristic term a fresh computation for each `v`, or was it computed once and reused? Check whether the value changes as `v` changes.

</details>

<details>
<summary>The stale entry condition looks fine to me</summary>

Read it as two separate concerns: (1) is this entry outdated? (2) has this node already been finalized? The current code combines them with `&&`. Think about what happens when only one of those is true.

</details>

<details>
<summary>I fixed one bug but still get MISMATCH</summary>

There are two independent bugs. Fixing one may reduce the error but not eliminate it. Make sure both are addressed.

</details>

<details>
<summary>What exactly is admissibility and why does it matter here</summary>

If `h(v)` overestimates the true remaining distance, A* thinks node `v` is more expensive than it really is, so it may deprioritize a path that's actually optimal. In this case it picks a shorter-looking direct path over the cheap roundabout path. Dijkstra, using no heuristic, isn't fooled.

</details>
