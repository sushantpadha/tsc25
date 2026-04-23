/*
 * Challenge 3: The Order Book
 * Compile: g++ -O0 -g -no-pie orderbook.cpp -o orderbook
 *
 * Run modes:
 *   ./orderbook simple   < orders.txt
 *   ./orderbook advanced < orders.txt
 *
 * Input format (simple mode):
 *   First line:  <n_orders> <capacity_hint>
 *   Then n_orders lines: <id> <trader_id> <price> <qty>
 *
 * Input format (advanced mode):
 *   L <id> <price> <qty> <post_only>    (LimitOrder)
 *   M <id> <qty> <urgency>              (MarketOrder)
 *   I <id> <price> <visible> <hidden>   (IcebergOrder)
 */

#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>
#include <string>
#include <cstdlib>

namespace Err {
    constexpr uint32_t NONE         = 0;
    constexpr uint32_t NEG_PRICE    = 1 << 0;
    constexpr uint32_t ZERO_QTY     = 1 << 1;
    constexpr uint32_t SELF_MATCH   = 1 << 2;
    constexpr uint32_t QTY_OVERFLOW = 1 << 3;
}

struct Fill {
    int    counterparty_id;
    double fill_price;
    int    fill_qty;
};

struct Order {
    int      id;
    int      trader_id;
    double   price;
    int      qty;
    uint32_t error_flags;
    Fill*    fill;
};

uint32_t validate_order(const Order& o) {
    uint32_t flags = Err::NONE;
    if (o.price <= 0.0)    flags |= Err::NEG_PRICE;
    if (o.qty < 0)         flags |= Err::QTY_OVERFLOW;
    if (o.trader_id == -1) flags |= Err::SELF_MATCH;
    return flags;
}

double compute_fill_value(const Order& o) {
    return o.fill->fill_price * o.fill->fill_qty;
}

void settle_order(const Order& o) {
    if (o.error_flags & Err::NEG_PRICE) {
        printf("  [settle] skipping order %d: negative price\n", o.id);
        return;
    }
    double val = compute_fill_value(o);
    printf("  [settle] order %d fill value: %.2f\n", o.id, val);
}

void match_order(const Order& o) {
    printf("  [match] processing order %d (qty=%d price=%.2f)\n",
           o.id, o.qty, o.price);
    settle_order(o);
}

struct SimpleOrderBook {
    std::vector<Order> storage;
    Order* last_inserted = nullptr;

    SimpleOrderBook(int capacity_hint) {
        storage.reserve(capacity_hint);
    }

    void insert(Order o) {
        storage.push_back(o);
        last_inserted = &storage.back();
    }

    void process_all() {
        for (auto& o : storage) {
            o.error_flags = validate_order(o);
            match_order(o);
        }
    }

    void print_last() {
        printf("  [book] last order: id=%d qty=%d price=%.2f\n",
               last_inserted->id, last_inserted->qty, last_inserted->price);
    }
};

// ============================================================

struct BaseOrder {
    int    id;
    double price;
    int    qty;
    Fill*  fill_history;
    int    fill_count;

    BaseOrder(int id_, double p, int q)
        : id(id_), price(p), qty(q), fill_count(0)
    {
        fill_history = new Fill[16];
        printf("  [ctor] BaseOrder %d\n", id);
    }

    BaseOrder(const BaseOrder& o)
        : id(o.id), price(o.price), qty(o.qty),
          fill_history(o.fill_history),
          fill_count(o.fill_count)
    {
        printf("  [copy-ctor] BaseOrder %d\n", id);
    }

    BaseOrder(BaseOrder&& o) noexcept
        : id(o.id), price(o.price), qty(o.qty),
          fill_history(o.fill_history), fill_count(o.fill_count)
    {
        o.fill_history = nullptr;
        o.fill_count   = 0;
        printf("  [move-ctor] BaseOrder %d\n", id);
    }

    virtual ~BaseOrder() {
        delete[] fill_history;
        printf("  [dtor] BaseOrder %d\n", id);
    }

    virtual std::string type_name() const { return "BaseOrder"; }
    virtual double effective_price() const { return price; }
    virtual void describe() const {
        printf("  [describe] %s id=%d price=%.2f qty=%d\n",
               type_name().c_str(), id, price, qty);
    }
};

struct LimitOrder : BaseOrder {
    double limit_price;
    bool   post_only;

    LimitOrder(int id_, double p, int q, bool po)
        : BaseOrder(id_, p, q), limit_price(p), post_only(po)
    {
        printf("  [ctor] LimitOrder %d\n", id);
    }

    std::string type_name() const override { return "LimitOrder"; }
    double effective_price() const override { return limit_price; }
    void describe() const override {
        printf("  [describe] LimitOrder id=%d limit=%.2f post_only=%d\n",
               id, limit_price, post_only);
    }
};

struct MarketOrder : BaseOrder {
    int urgency;

    MarketOrder(int id_, int q, int u)
        : BaseOrder(id_, 0.0, q), urgency(u)
    {
        printf("  [ctor] MarketOrder %d\n", id);
    }

    std::string type_name() const override { return "MarketOrder"; }
    double effective_price() const override { return 1e18; }
    void describe() const override {
        printf("  [describe] MarketOrder id=%d qty=%d urgency=%d\n",
               id, qty, urgency);
    }
};

struct IcebergOrder : LimitOrder {
    int visible_qty;
    int hidden_qty;

    IcebergOrder(int id_, double p, int visible, int hidden)
        : LimitOrder(id_, p, visible + hidden, false),
          visible_qty(visible), hidden_qty(hidden)
    {
        printf("  [ctor] IcebergOrder %d (visible=%d hidden=%d)\n",
               id, visible_qty, hidden_qty);
    }

    std::string type_name() const override { return "IcebergOrder"; }
    void describe() const override {
        printf("  [describe] IcebergOrder id=%d visible=%d hidden=%d price=%.2f\n",
               id, visible_qty, hidden_qty, limit_price);
    }
};

struct AdvancedOrderBook {
    std::vector<BaseOrder> orders;

    void insert(const BaseOrder& o) {
        orders.push_back(o);
    }

    void describe_all() const {
        for (const auto& o : orders)
            o.describe();
    }

    void process_all() const {
        for (const auto& o : orders)
            printf("  [process] effective_price=%.2f for id=%d\n",
                   o.effective_price(), o.id);
    }
};

// ============================================================

void run_simple() {
    printf("\n=== Mode 1: Simple Order Book ===\n");

    int n_orders, capacity_hint;
    if (scanf("%d %d", &n_orders, &capacity_hint) != 2) {
        fprintf(stderr, "expected: <n_orders> <capacity_hint>\n");
        return;
    }

    SimpleOrderBook book(capacity_hint);

    for (int i = 0; i < n_orders; i++) {
        int id, trader_id, qty;
        double price;
        if (scanf("%d %d %lf %d", &id, &trader_id, &price, &qty) != 4) {
            fprintf(stderr, "malformed order at index %d\n", i);
            return;
        }
        Fill* f = (qty > 0) ? new Fill{trader_id * 10, price, qty} : nullptr;
        Order o{id, trader_id, price, qty, Err::NONE, f};
        book.insert(o);
        book.print_last();
    }

    printf("\nProcessing all orders...\n");
    book.process_all();
}

void run_advanced() {
    printf("\n=== Mode 2: Advanced Order Book ===\n");

    AdvancedOrderBook book;
    char type;
    while (scanf(" %c", &type) == 1) {
        if (type == 'L') {
            int id, qty, po; double price;
            scanf("%d %lf %d %d", &id, &price, &qty, &po);
            LimitOrder lo(id, price, qty, po != 0);
            book.insert(lo);
        } else if (type == 'M') {
            int id, qty, urgency;
            scanf("%d %d %d", &id, &qty, &urgency);
            MarketOrder mo(id, qty, urgency);
            book.insert(mo);
        } else if (type == 'I') {
            int id, visible, hidden; double price;
            scanf("%d %lf %d %d", &id, &price, &visible, &hidden);
            IcebergOrder io(id, price, visible, hidden);
            book.insert(io);
        } else {
            fprintf(stderr, "unknown order type: %c\n", type);
            return;
        }
    }

    printf("\nDescribing:\n");
    book.describe_all();
    printf("\nProcessing:\n");
    book.process_all();
    printf("\nDone.\n");
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printf("Usage: %s [simple|advanced] < orders.txt\n", argv[0]);
        return 1;
    }
    if      (strcmp(argv[1], "simple")   == 0) run_simple();
    else if (strcmp(argv[1], "advanced") == 0) run_advanced();
    else { printf("Unknown mode: %s\n", argv[1]); return 1; }
    return 0;
}
