import sys
import time
import random

def solve():
    start_time = time.perf_counter()
    input_data = sys.stdin.read().split()

    n = int(input_data[0])
    k = int(input_data[1])

    c = []
    index = 2
    N = 2*n
    for _ in range(N+1):
        row = []
        for _ in range(N+1):
            row.append(int(input_data[index]))
            index += 1
        c.append(row)

    def Greedy(c, n, k):
        route = []
        visited = [False]*(N+1)
        load = 0
        current_node = 0
        for i in range(N):
            best_next = -1
            min_distance = float('inf')
            for v in range(1, N+1):
                if visited[v]:
                    continue
                if v <= n and load >= k:
                    continue
                if v > n and not visited[v-n]:
                    continue
                if c[current_node][v] < min_distance:
                    min_distance = c[current_node][v]
                    best_next = v
            visited[best_next] = True
            current_node = best_next
            route.append(best_next)
            if best_next <= n:
                load += 1
            else:
                load -= 1
        return route

    def is_valid(route, n, k):
        load = 0
        visited = [False]*(N+1)
        for i in route:
            if i <= n:
                load += 1
                visited[i] = True
                if load > k:
                    return False
            else:
                if visited[i-n] == False:
                    return False
                load -= 1
        return True

    def calculate_swap(route, i, j, c):
        if i > j:
            i, j = j, i
        pre_i = route[i-1] if i > 0 else 0
        pre_j = route[j-1] if j > 0 else 0
        next_i = route[i+1] if i < len(route)-1 else 0
        next_j = route[j+1] if j < len(route)-1 else 0
        if j == i+1:
            delta = c[pre_i][route[j]] + c[route[j]][route[i]] + c[route[i]][next_j]
            delta -= (c[pre_i][route[i]] + c[route[i]][route[j]] + c[route[j]][next_j])
        else:
            delta = c[pre_i][route[j]]+c[route[j]][next_i]+c[pre_j][route[i]]+c[route[i]][next_j]
            delta -= c[pre_i][route[i]]+c[route[i]][next_i]+c[pre_j][route[j]]+c[route[j]][next_j]
        return delta

    def total_cost(route, c):
        cost = c[0][route[0]]
        for idx in range(len(route)-1):
            cost += c[route[idx]][route[idx+1]]
        cost += c[route[-1]][0]
        return cost
    
    
    route = Greedy(c, n, k)
    current = route[:]
    current_cost = total_cost(current, c)
    best = current[:]
    best_cost = current_cost


    # A move (swapping two elements) will be added to tabu_list if it is accepted
    # That move is forbidden for [tenure] iterations
    # This prevents the code to fall back into local optima while trying to escape
    tabu_list = {}  
    it = 0
    no_improve = 0
    T_min = max(5, int(0.5 * (n)**(1/2)))
    T_max = max(15, int(1.5 * (n)**(1/2)))

    while time.perf_counter() - start_time < 290:
        best_delta = float('inf')
        best_pair = None
        best_move = None

        for i in range(N):
            for j in range(i+1, N):
                delta = calculate_swap(current, i, j, c)
                if delta >= best_delta:
                    continue
                a, b = current[i], current[j]
                move = (a, b) if a < b else (b, a)
                # is_tabu = Node is 'forbidden', but if better result then can be choosen
                is_tabu = move in tabu_list and tabu_list[move] > it
                if is_tabu and (current_cost + delta) >= best_cost:
                    continue
                current[i], current[j] = current[j], current[i]
                feasible = is_valid(current, n, k)
                current[i], current[j] = current[j], current[i]

                if feasible:
                    best_delta = delta
                    best_pair = (i, j)
                    best_move = move

            if time.perf_counter() - start_time >= 290:
                break

        if best_pair is None:
            break

        i, j = best_pair
        current[i], current[j] = current[j], current[i]
        current_cost += best_delta

        dynamic_tenure = random.randint(T_min, T_max)
        tabu_list[best_move] = it + dynamic_tenure + random.randint(0,dynamic_tenure//10)
        # Remove expired nodes
        tabu_list = {m: exp for m, exp in tabu_list.items() if exp > it}

        if current_cost < best_cost:
            best = current[:]
            best_cost = current_cost
            no_improve = 0
        else:
            no_improve += 1

        it += 1
        # If no improvement was made for a while, go back and search other way
        # Escape Local Optima mechanism
        if no_improve > 200:
            current = best[:]
            t_feasible = False
            it = 0
            while not t_feasible and it < 200:
                i = random.randint(0,N-1)
                j = random.randint(i,N-1)
                current[i], current[j] = current[j], current[i]
                t_feasible = (is_valid(current, n, k) and ((i,j) not in tabu_list))
                if not t_feasible:
                    current[i], current[j] = current[j], current[i]
                it+=1
            current_cost = total_cost(current,c)
            no_improve = 0

    print(n)
    print(" ".join(map(str, best)))

if __name__ == '__main__':
    solve()