/*
 * Challenge 4: Broken Pathfinder
 * Compile: g++ -O0 -g -no-pie astar.cpp -o astar
 *
 * A* on a small graph. Should agree with Dijkstra. Sometimes doesn't.
 */

#include <cstdio>
#include <cmath>
#include <vector>
#include <queue>
#include <limits>
#include <algorithm>

static const double INF = std::numeric_limits<double>::infinity();

struct Node {
    int    id;
    double x, y;
};

struct Edge {
    int    dst;
    double weight;
};

struct Graph {
    int               V;
    std::vector<Node> nodes;
    std::vector<std::vector<Edge>> adj;

    Graph(int v) : V(v), nodes(v), adj(v) {}

    void add_edge(int u, int v, double w) {
        adj[u].push_back({v, w});
    }

    double euclidean(int u, int v) const {
        double dx = nodes[u].x - nodes[v].x;
        double dy = nodes[u].y - nodes[v].y;
        return std::sqrt(dx*dx + dy*dy);
    }
};

// ---- Dijkstra: ground truth ----
std::vector<double> dijkstra(const Graph& g, int src) {
    std::vector<double> dist(g.V, INF);
    using pdi = std::pair<double,int>;
    std::priority_queue<pdi, std::vector<pdi>, std::greater<pdi>> pq;
    dist[src] = 0.0;
    pq.push({0.0, src});
    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if (d > dist[u]) continue;
        for (const auto& e : g.adj[u]) {
            double nd = dist[u] + e.weight;
            if (nd < dist[e.dst]) {
                dist[e.dst] = nd;
                pq.push({nd, e.dst});
            }
        }
    }
    return dist;
}

// ---- A* with two bugs ----
struct AStarResult {
    std::vector<double> g_score;
    std::vector<int>    parent;
    double              cost;
    std::vector<int>    path;
};

AStarResult a_star(const Graph& g, int source, int target) {
    std::vector<double> g_score(g.V, INF);
    std::vector<double> f_score(g.V, INF);
    std::vector<bool>   in_closed(g.V, false);
    std::vector<int>    parent(g.V, -1);

    using pdi = std::pair<double,int>;
    std::priority_queue<pdi, std::vector<pdi>, std::greater<pdi>> open;

    g_score[source] = 0.0;

    const double HEURISTIC_WEIGHT = 2.5;
    f_score[source] = g.euclidean(source, target) * HEURISTIC_WEIGHT;
    open.push({f_score[source], source});

    while (!open.empty()) {
        auto [f, u] = open.top();
        open.pop();
        if (f >= f_score[u] && in_closed[u])   //
            continue;

        if (in_closed[u]) continue;
        in_closed[u] = true;

        if (u == target) break;

        for (const auto& e : g.adj[u]) {
            int    v          = e.dst;
            double tentative_g = g_score[u] + e.weight;

            if (tentative_g < g_score[v]) {
                parent[v]  = u;
                g_score[v] = tentative_g;
                f_score[v] = g_score[v] + g.euclidean(v, target) * HEURISTIC_WEIGHT;
                open.push({f_score[v], v});
            }
        }
    }

    // reconstruct path
    std::vector<int> path;
    if (g_score[target] < INF) {
        for (int cur = target; cur != -1; cur = parent[cur])
            path.push_back(cur);
        std::reverse(path.begin(), path.end());
    }

    return {g_score, parent, g_score[target], path};
}

int main() {
    int V, E;
    scanf("%d %d", &V, &E);

    Graph g(V);
    for (int i = 0; i < V; i++) {
        int id; double x, y;
        scanf("%d %lf %lf", &id, &x, &y);
        g.nodes[id] = {id, x, y};
    }
    for (int i = 0; i < E; i++) {
        int u, v; double w;
        scanf("%d %d %lf", &u, &v, &w);
        g.add_edge(u, v, w);
    }

    int src, dst;
    scanf("%d %d", &src, &dst);

    // Dijkstra ground truth
    auto dijk = dijkstra(g, src);

    // A* (buggy)
    auto res = a_star(g, src, dst);

    printf("Dijkstra cost:  %.4f\n", dijk[dst]);
    printf("A* cost:        %.4f\n", res.cost);

    if (std::abs(res.cost - dijk[dst]) > 1e-9)
        printf("MISMATCH: A* is wrong!\n");
    else
        printf("Results agree.\n");

    printf("A* path: ");
    for (int node : res.path) printf("%d ", node);
    printf("\n");

    return 0;
}
