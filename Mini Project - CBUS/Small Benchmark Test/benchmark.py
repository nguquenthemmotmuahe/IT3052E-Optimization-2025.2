import sys
import time
import random
import os
import json
from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt

class TimeoutException(Exception):
    pass

def generate_test_case(n, k, max_distance=50):
    total_nodes = 2 * n + 1
    c = [[0] * total_nodes for _ in range(total_nodes)]
    for i in range(total_nodes):
        for j in range(total_nodes):
            if i != j:
                c[i][j] = random.randint(1, max_distance)
    return n, k, c

def save_test_case(n, k, c, folder_path="test_cases"):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = os.path.join(folder_path, f"test_case_N{n}_K{k}.json")
    data = {
        "N": n,
        "K_capacity": k,
        "Total_Nodes": 2 * n + 1,
        "Distance_Matrix_C": c
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    return filename

def greedy_init(c, n, k):
    N = 2 * n
    route = []
    visited = [False] * (N + 1)
    load = 0
    current_node = 0
    for _ in range(N):
        best_next = -1
        min_distance = float('inf')
        for v in range(1, N + 1):
            if visited[v]: continue
            if v <= n and load >= k: continue
            if v > n and not visited[v - n]: continue
            if c[current_node][v] < min_distance:
                min_distance = c[current_node][v]
                best_next = v
        visited[best_next] = True
        current_node = best_next
        route.append(best_next)
        if best_next <= n: load += 1
        else: load -= 1
    return route

def is_valid_route(route, n, k):
    N = 2 * n
    load = 0
    visited = [False] * (N + 1)
    for i in route:
        if i <= n:
            load += 1
            visited[i] = True
            if load > k: return False
        else:
            if not visited[i - n]: return False
            load -= 1
    return True

def total_cost(route, c):
    cost = c[0][route[0]]
    for idx in range(len(route) - 1):
        cost += c[route[idx]][route[idx + 1]]
    cost += c[route[-1]][0]
    return cost

def calculate_swap(route, i, j, c):
    if i > j: i, j = j, i
    pre_i = route[i-1] if i > 0 else 0
    pre_j = route[j-1] if j > 0 else 0
    next_i = route[i+1] if i < len(route)-1 else 0
    next_j = route[j+1] if j < len(route)-1 else 0
    if j == i+1:
        delta = c[pre_i][route[j]] + c[route[j]][route[i]] + c[route[i]][next_j]
        delta -= (c[pre_i][route[i]] + c[route[i]][route[j]] + c[route[j]][next_j])
    else:
        delta = c[pre_i][route[j]] + c[route[j]][next_i] + c[pre_j][route[i]] + c[route[i]][next_j]
        delta -= (c[pre_i][route[i]] + c[route[i]][next_i] + c[pre_j][route[j]] + c[route[j]][next_j])
    return delta

def remove_insert_cost(route, x, i, prev_cost, c):
    cost = prev_cost
    idx_x = route.index(x)
    pre_x = route[idx_x - 1] if idx_x > 0 else 0
    next_x = route[idx_x + 1] if idx_x < len(route) - 1 else 0

    cost -= (c[pre_x][x] + c[x][next_x])
    cost += c[pre_x][next_x]

    new_route = route[:idx_x] + route[idx_x+1:]
    pre_i = new_route[i - 1] if i > 0 else 0
    next_i = new_route[i] if i < len(new_route) else 0

    cost -= c[pre_i][next_i]
    cost += (c[pre_i][x] + c[x][next_i])
    new_route.insert(i, x)
    return cost, new_route

def run_greedy(n, k, c, time_limit):
    start_time = time.perf_counter()
    route = greedy_init(c, n, k)
    cost = total_cost(route, c)
    return cost, time.perf_counter() - start_time

def run_local_search(n, k, c, time_limit):
    start_time = time.perf_counter()
    route = greedy_init(c, n, k)
    N = 2 * n
    improved = True
    time_to_best = time.perf_counter() - start_time
    best_cost = total_cost(route, c)

    while improved and time.perf_counter() - start_time < time_limit:
        improved = False
        for i in range(N):
            for j in range(i+1, N):
                delta = calculate_swap(route, i, j, c)
                if delta < 0:
                    route[i], route[j] = route[j], route[i]
                    if is_valid_route(route, n, k):
                        improved = True
                        best_cost += delta
                        time_to_best = time.perf_counter() - start_time
                        break
                    else:
                        route[i], route[j] = route[j], route[i]
            if improved: break
    return best_cost, time_to_best

def run_random_walk(n, k, c, time_limit):
    start_time = time.perf_counter()
    route = greedy_init(c, n, k)
    best_cost = total_cost(route, c)
    prev_cost = best_cost
    N = 2 * n
    time_to_best = time.perf_counter() - start_time

    while time.perf_counter() - start_time < time_limit:
        x = random.randint(1, n)
        current_route = route[:]
        i = random.randint(0, N-1)
        current_cost, current_route = remove_insert_cost(current_route, x, i, prev_cost, c)

        j = random.randint(i, N-1)
        current_cost, current_route = remove_insert_cost(current_route, x+n, j, current_cost, c)

        if current_cost < best_cost:
            if is_valid_route(current_route, n, k):
                best_cost = current_cost
                route = current_route[:]
                time_to_best = time.perf_counter() - start_time
                prev_cost = best_cost
            else:
                prev_cost = best_cost
        else:
            prev_cost = best_cost
    return best_cost, time_to_best

def run_tabu_search(n, k, c, time_limit):
    start_time = time.perf_counter()
    route = greedy_init(c, n, k)
    current = route[:]
    current_cost = total_cost(current, c)
    best = current[:]
    best_cost = current_cost
    time_to_best = time.perf_counter() - start_time

    N = 2 * n
    tabu_list = {}
    it = 0
    no_improve = 0
    T_min = max(5, int(0.5 * (n)**(1/2)))
    T_max = max(15, int(1.5 * (n)**(1/2)))

    while time.perf_counter() - start_time < time_limit:
        best_delta = float('inf')
        best_pair = None
        best_move = None

        for i in range(N):
            for j in range(i+1, N):
                delta = calculate_swap(current, i, j, c)
                if delta >= best_delta: continue

                a, b = current[i], current[j]
                move = (a, b) if a < b else (b, a)
                is_tabu = move in tabu_list and tabu_list[move] > it
                if is_tabu and (current_cost + delta) >= best_cost: continue

                current[i], current[j] = current[j], current[i]
                feasible = is_valid_route(current, n, k)
                current[i], current[j] = current[j], current[i]

                if feasible:
                    best_delta = delta
                    best_pair = (i, j)
                    best_move = move

            if time.perf_counter() - start_time >= time_limit: break

        if best_pair is None: break

        i, j = best_pair
        current[i], current[j] = current[j], current[i]
        current_cost += best_delta

        dynamic_tenure = random.randint(T_min, T_max)
        tabu_list[best_move] = it + dynamic_tenure + random.randint(0, dynamic_tenure//10)
        tabu_list = {m: exp for m, exp in tabu_list.items() if exp > it}

        if current_cost < best_cost:
            best = current[:]
            best_cost = current_cost
            time_to_best = time.perf_counter() - start_time
            no_improve = 0
        else:
            no_improve += 1

        it += 1
        if no_improve > 200:
            current = best[:]
            t_feasible = False
            it_escape = 0
            while not t_feasible and it_escape < 200:
                i = random.randint(0, N-1)
                j = random.randint(i, N-1)
                current[i], current[j] = current[j], current[i]
                t_feasible = (is_valid_route(current, n, k) and ((i,j) not in tabu_list))
                if not t_feasible:
                    current[i], current[j] = current[j], current[i]
                it_escape += 1
            current_cost = total_cost(current, c)
            no_improve = 0

    return best_cost, time_to_best

def run_cp_sat(n, k, c, time_limit):
    start_time = time.perf_counter()
    model = cp_model.CpModel()
    total_nodes = 2 * n + 1

    customer = [model.NewIntVar(0, k, f'customer{i}') for i in range(total_nodes + 1)]
    point = [model.NewIntVar(0, total_nodes - 1, f'point{i}') for i in range(total_nodes + 1)]
    index = {i : model.NewIntVar(1, total_nodes - 1, f'index{i}') for i in range(1, total_nodes)}
    step_dist = [model.NewIntVar(0, 1000000, f'step_dist_{i}') for i in range(total_nodes)]

    model.Add(point[0] == 0)
    model.Add(point[total_nodes] == 0)
    model.Add(customer[0] == 0)
    model.Add(customer[total_nodes] == 0)

    model.AddAllDifferent(point[1:total_nodes])

    for i in range(1, total_nodes):
        for j in range(1, total_nodes):
            b = model.NewBoolVar(f"index_{j}_is_{i}")
            model.Add(index[j] == i).OnlyEnforceIf(b)
            model.Add(index[j] != i).OnlyEnforceIf(b.Not())
            model.Add(point[i] == j).OnlyEnforceIf(b)

    for i in range(1, n + 1):
        model.Add(index[i] < index[i + n])

    for i in range(1, total_nodes):
        pickup = model.NewBoolVar(f'pickup_{i}')
        delivery = model.NewBoolVar(f'delivery_{i}')
        model.Add(point[i] <= n).OnlyEnforceIf(pickup)
        model.Add(point[i] >= n+1).OnlyEnforceIf(pickup.Not())
        model.Add(point[i] >= n+1).OnlyEnforceIf(delivery)
        model.Add(point[i] <= n).OnlyEnforceIf(delivery.Not())
        model.Add(customer[i] == customer[i - 1] + 1).OnlyEnforceIf(pickup)
        model.Add(customer[i] == customer[i - 1] - 1).OnlyEnforceIf(delivery)

    flat_matrix = [c[i][j] for i in range(total_nodes) for j in range(total_nodes)]

    for i in range(total_nodes):
        matrix_idx = model.NewIntVar(0, total_nodes*total_nodes - 1, f'idx_{i}')
        model.Add(matrix_idx == point[i]*total_nodes + point[i+1])
        model.AddElement(matrix_idx, flat_matrix, step_dist[i])

    model.Minimize(sum(step_dist))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.Solve(model)
    exec_time = time.perf_counter() - start_time

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        return solver.ObjectiveValue(), exec_time
    return float('inf'), exec_time

def run_ilp(n, K, c, time_limit):
    start_time = time.perf_counter()
    total_nodes = 2 * n + 1
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver: return float('inf'), 0
    solver.set_time_limit(int(time_limit * 1000))

    x = {}
    for i in range(total_nodes):
        for j in range(total_nodes):
            if i != j: x[i, j] = solver.BoolVar(f'x_{i}_{j}')

    t, y = {}, {}
    for i in range(total_nodes):
        t[i] = solver.IntVar(0, total_nodes + 1, f't_{i}')
        y[i] = solver.IntVar(0, K, f'y_{i}')

    q = [0] * total_nodes
    for i in range(1, n + 1):
        q[i] = 1
        q[i + n] = -1

    for i in range(total_nodes):
        solver.Add(solver.Sum([x[i, j] for j in range(total_nodes) if i != j]) == 1)
        solver.Add(solver.Sum([x[j, i] for j in range(total_nodes) if i != j]) == 1)

    for i in range(1, n + 1): solver.Add(t[i] <= t[i + n])
    solver.Add(t[0] == 0)
    solver.Add(y[0] == 0)

    M_t, M_y = total_nodes + 2, K + 2
    for i in range(total_nodes):
        for j in range(total_nodes):
            if i != j and j != 0:
                solver.Add(t[j] >= t[i] + 1 - M_t * (1 - x[i, j]))
                solver.Add(y[j] - y[i] - q[j] <= M_y * (1 - x[i, j]))
                solver.Add(y[j] - y[i] - q[j] >= -M_y * (1 - x[i, j]))

    objective = solver.Objective()
    for i in range(total_nodes):
        for j in range(total_nodes):
            if i != j: objective.SetCoefficient(x[i, j], c[i][j])
    objective.SetMinimization()

    status = solver.Solve()
    exec_time = time.perf_counter() - start_time
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        return objective.Value(), exec_time
    return float('inf'), exec_time

def run_ilp_another_model(n, K_cap, c, time_limit):
    start_time = time.perf_counter()
    total_nodes = 2 * n + 1
    total_steps = 2 * n

    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver: return float('inf'), 0
    solver.set_time_limit(int(time_limit * 1000))

    W = {}
    for s in range(total_steps + 1):
        for v in range(total_nodes):
            W[s, v] = solver.BoolVar(f'W_{s}_{v}')

    Pos = {v: solver.IntVar(0, total_steps, f'Pos_{v}') for v in range(total_nodes)}
    L = {s: solver.IntVar(0, K_cap, f'L_{s}') for s in range(total_steps + 1)}
    D = {s: solver.NumVar(0, solver.infinity(), f'D_{s}') for s in range(total_steps)}

    q = [0] * total_nodes
    for i in range(1, n + 1):
        q[i] = 1
        q[i + n] = -1

    solver.Add(W[0, 0] == 1)
    solver.Add(W[total_steps, 0] == 1)
    solver.Add(L[0] == 0)

    for s in range(1, total_steps):
        solver.Add(W[s, 0] == 0)

    for v in range(1, total_nodes):
        solver.Add(W[0, v] == 0)
        solver.Add(W[total_steps, v] == 0)

    for s in range(1, total_steps):
        solver.Add(solver.Sum([W[s, v] for v in range(1, total_nodes)]) == 1)

    for v in range(1, total_nodes):
        solver.Add(solver.Sum([W[s, v] for s in range(1, total_steps)]) == 1)

    for v in range(1, total_nodes):
        solver.Add(Pos[v] == solver.Sum([s * W[s, v] for s in range(1, total_steps)]))

    for i in range(1, n + 1):
        solver.Add(Pos[i] <= Pos[i + n])

    for s in range(1, total_steps + 1):
        solver.Add(L[s] == L[s-1] + solver.Sum([q[v] * W[s, v] for v in range(1, total_nodes)]))

    M = max(max(row) for row in c) * 2
    for s in range(total_steps):
        for u in range(total_nodes):
            for v in range(total_nodes):
                if u != v:
                    solver.Add(D[s] >= c[u][v] - M * (2 - W[s, u] - W[s+1, v]))

    objective = solver.Objective()
    for s in range(total_steps):
        objective.SetCoefficient(D[s], 1)
    objective.SetMinimization()
    status = solver.Solve()
    exec_time = time.perf_counter() - start_time

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        return objective.Value(), exec_time
    return float('inf'), exec_time

def run_branch_and_bound(n, k, c, time_limit):
    start_time = time.perf_counter()
    z_best = float('inf')
    load = 0
    current_distance = 0
    visited = [False] * (2 * n + 1)
    x = [0] * (2 * n + 1)

    c_min = float('inf')
    for i in range(2 * n + 1):
        for j in range(2 * n + 1):
            if 0 < c[i][j] < c_min: c_min = c[i][j]

    def check(v):
        if visited[v]: return False
        if v > n and not visited[v - n]: return False
        if v <= n and load + 1 > k: return False
        return True

    def Try(step):
        nonlocal z_best, load, current_distance
        if time.perf_counter() - start_time > time_limit:
            raise TimeoutException()

        for v in range(1, 2 * n + 1):
            if check(v):
                x[step] = v
                visited[v] = True
                current_distance += c[x[step - 1]][v]
                if v <= n: load += 1
                else: load -= 1

                lower_bound = current_distance + (2 * n - step + 1) * c_min
                if lower_bound < z_best:
                    if step == 2 * n:
                        total_distance = current_distance + c[x[2 * n]][0]
                        if total_distance < z_best:
                            z_best = total_distance
                    else:
                        Try(step + 1)

                visited[v] = False
                current_distance -= c[x[step - 1]][v]
                if v <= n: load -= 1
                else: load += 1

    try:
        Try(1)
        return z_best, time.perf_counter() - start_time
    except TimeoutException:
        return z_best, time_limit

def main_benchmark():
    test_sizes = [5, 8, 12, 20, 30, 50]
    k_capacity = 3
    time_limit_per_test = 30.0

    print(f"{'N':<5} | {'Method':<20} | {'Cost':<10} | {'Time to Best (s)':<15}")
    print("-" * 58)

    methods = [
        ("Greedy", run_greedy),
        ("Local Search", run_local_search),
        ("Tabu Search", run_tabu_search),
        ("CP-SAT", run_cp_sat),
        ("ILP - 01", run_ilp),
        ("ILP - 02", run_ilp_another_model),
        ("Branch & Bound", run_branch_and_bound)
    ]

    results_cost = {name: [] for name, _ in methods}
    results_time = {name: [] for name, _ in methods}

    for n in test_sizes:
        _, _, c = generate_test_case(n, k_capacity)

        saved_file = save_test_case(n, k_capacity, c)
        print(f"\n[INFO] Test Case N={n} saved to: {saved_file}\n")

        for name, func in methods:
            cost, time_to_best = func(n, k_capacity, c, time_limit_per_test)

            results_cost[name].append(cost if cost != float('inf') else None)
            results_time[name].append(time_to_best)

            cost_str = f"{cost:.2f}" if cost != float('inf') else "N/A"
            print(f"{n:<5} | {name:<20} | {cost_str:<10} | {time_to_best:<15.4f}")
        print("-" * 58)

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
    markers = ['o', 's', '^', 'D', 'v', 'p', '*']

    for i, (name, _) in enumerate(methods):
        valid_n_cost = [n for j, n in enumerate(test_sizes) if results_cost[name][j] is not None]
        valid_cost = [c for c in results_cost[name] if c is not None]

        valid_n_time = test_sizes
        valid_time = results_time[name]

        ax1.plot(valid_n_time, valid_time, marker=markers[i%len(markers)], color=colors[i%len(colors)], label=name, linewidth=2, markersize=8)
        ax2.plot(valid_n_cost, valid_cost, marker=markers[i%len(markers)], color=colors[i%len(colors)], label=name, linewidth=2, markersize=8)

    ax1.set_yscale('linear')
    ax1.set_ylim(bottom=0, top=30.5)
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(0.5))
    ax1.tick_params(axis='y', labelsize=8)
    ax1.axhline(y=30.0, color='black', linestyle='--', alpha=0.7, linewidth=2, label='Time Limit (30s)')

    ax1.set_title('Runtime Comparison vs Problem Size (N)', fontsize=14, pad=15)
    ax1.set_xlabel('Number of Passengers (N)', fontsize=12)
    ax1.set_ylabel('Execution Time (seconds)', fontsize=12)
    ax1.legend(fontsize=10, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)

    ax2.set_title('Solution Cost Comparison vs Problem Size (N)', fontsize=14, pad=15)
    ax2.set_xlabel('Number of Passengers (N)', fontsize=12)
    ax2.set_ylabel('Total Travel Distance (Cost)', fontsize=12)
    ax2.legend(fontsize=10, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=4)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.5)
    plt.show()

if __name__ == '__main__':
    main_benchmark()
