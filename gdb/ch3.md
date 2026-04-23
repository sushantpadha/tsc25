# Challenge 3: Looky Looky an Order Booky

**Binary:** `orderbook` | **Source:** provided -- but try not to read it first

Debug a (simplistic) order book using GDB. View tc's in `simple.txt` and `advanced.txt`.

---

## Setup

```bash
g++ -O0 -g -no-pie orderbook.cpp -o orderbook
```

Two modes:
```bash
./orderbook simple
./orderbook advanced
```

---

# Mode 1: Simple Order Book

## Story

A trading firm's order book is crashing in production. Two separate bugs. Your manager is not happy. The error logs are useless. You have GDB.

---

## Bug 1

### Step 1: Run it

```bash
./orderbook simple
```

It crashes. Note roughly where — how many orders were processed before things went wrong?

### Step 2: Find the crash in GDB

```bash
gdb ./orderbook
(gdb) r simple
```

When it crashes:

```
(gdb) bt
```

Walk the stack. For each frame:

```
(gdb) frame <n>
(gdb) info locals
(gdb) info args
```

Which pointer caused the fault? Where was it last assigned? Work *up* the call stack, not down.

### Step 3: Find where the pointer is set

Identify the variable. Find `insert()` in the source — this is where it's assigned. Set a breakpoint and watch it:

```
(gdb) b SimpleOrderBook::insert
(gdb) r simple
```

After each `insert` returns, compare:

```
(gdb) p this->last_inserted
(gdb) p &this->storage.back()
```

Keep hitting `c`. At some point, these two values diverge. What happened between the previous insertion and this one?

### Step 4: Catch it live

Use a watchpoint to catch the exact moment the underlying storage moves:

```
(gdb) watch this->storage.size()
```

When it fires, check the capacity. Then check your pointer. What is `this->storage.data()` before vs after?

**Fix:** Don't cache raw pointers into a `std::vector` that can reallocate. What are your options?

---

## Bug 2

Fix Bug 1 (or just comment out `print_last()`), then run again. A different crash.

```
(gdb) r simple
(gdb) bt
```

The crash is deep. Walk up. At each frame — what are the arguments? Does the order that reaches the crash look correct to you?

```
(gdb) frame <crash frame>
(gdb) info args
(gdb) p o.qty
(gdb) p o.fill
```

Now walk up further to where this order came from. Something about it was never validated.

```
(gdb) p o.error_flags
```

What value is this? What *should* it be given the order's contents? Look at `validate_order` in the source. What case is missing?

**Fix:** Add the missing check.

---

# Mode 2: Advanced Order Book

## Story

A refactor introduced derived order types. Now the book behaves strangely — wrong output, no crash. Two more bugs.

---

## Bug 3

```bash
./orderbook advanced
```

Look at the `[describe]` lines. Something's off about the types being reported.

```bash
gdb ./orderbook
(gdb) b AdvancedOrderBook::describe_all
(gdb) r advanced
(gdb) n
```

Ask GDB what type the stored objects actually are:

```
(gdb) ptype orders[0]
(gdb) whatis orders[0]
```

Compare to what you *inserted*. Then check the vtable pointer directly:

```
(gdb) x/xg &orders[0]
```

Look up the vtable pointer of the original derived object on the stack:

```
(gdb) x/xg &lo
```

Are these the same? What does that mean for virtual dispatch?

Now find where the information is lost. Break on `AdvancedOrderBook::insert`, step into `push_back`, watch which constructor fires.

**Fix:** `std::vector<BaseOrder>` can't hold derived types. What container/strategy can?

---

## Bug 4

Run advanced mode to completion. Watch the destructor output carefully. Count.

Break inside the copy constructor:

```
(gdb) b 'BaseOrder::BaseOrder(BaseOrder const&)'
(gdb) r advanced
```

When it fires, compare:

```
(gdb) p this->fill_history
(gdb) p o.fill_history
```

These should never be equal. What happens when both objects are destroyed?

**Fix:** Write a proper deep-copying copy constructor.

---

## Part C — Disassembly

```
(gdb) disas 'BaseOrder::BaseOrder(int, double, int)'
```

Find the instruction near the top that stores a value into `[rdi]` (the `this` pointer). That's the vtable pointer being set. Note the address.

```
(gdb) disas 'LimitOrder::LimitOrder(int, double, int, bool)'
```

Same instruction, different address. These point to different vtables — that's polymorphism at the machine level. When slicing happens, only the base vtable pointer gets written.

---

## Hints

<details>
<summary>Bug 1: I can't tell when the pointer goes stale</summary>

The key event is vector reallocation. This happens when `size() == capacity()` and you insert one more. What was the initial capacity? Count your insertions.

</details>

<details>
<summary>Bug 2: I see the crash but don't understand why</summary>

Look at the member being dereferenced in the crash frame. Then look at the same member in the order that caused it. Under what input condition would that member never have been initialized?

</details>

<details>
<summary>Bug 3: ptype says BaseOrder but I inserted a LimitOrder</summary>

That's exactly the bug — you've confirmed it. Now find *where* the type is lost. The moment `push_back` copies the object, only the base subobject is preserved. The derived part is sliced off. This is called object slicing.

</details>

<details>
<summary>Bug 4: where exactly is the double-free?</summary>

The copy constructor copies the pointer, not the data. So two objects now point to the same heap allocation. When the first is destroyed, it's freed. When the second is destroyed, it's freed again. Use `p this->fill_history` in both the copy ctor and the dtor to see the same address appear twice.

</details>
