import sys
import random
import time

def solve():
    start_time = time.perf_counter()
    input_data = sys.stdin.read().split()
    
    n = int(input_data[0])
    k = int(input_data[1])
    N = 2*n
    c = []

    index = 2
    for _ in range(N+1):
        row = []
        for _ in range(N+1):
            row.append(int(input_data[index]))  
            index +=1
        c.append(row)
    
    def Greedy(c,n,k):
        route = []
        visited = [False]*(N+1)
        load = 0
        current_node = 0
        for i in range(N):
            best_next = -1
            min_distance = float('inf')
            for v in range(1,N+1):
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
    
    def is_valid(route,n,k):
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
    
    def remove_and_insert_and_calculate_cost(route, x, i, prev_cost):
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
    
    route = Greedy(c,n,k)
    prev_cost = c[0][route[0]]+c[route[-1]][0]
    for idx in range(N-1):
        prev_cost += c[route[idx]][route[idx+1]]

    best_cost = prev_cost
    # Random walk
    while time.perf_counter() - start_time < 290:
        x = random.randint(1,n)
        current_route = route[:]
        i = random.randint(0,N-1)
        current_cost, current_route = remove_and_insert_and_calculate_cost(current_route,x,i,prev_cost)
        
        prev_cost = current_cost
        j = random.randint(i,N-1)
        current_cost, current_route = remove_and_insert_and_calculate_cost(current_route,x+n,j,prev_cost)
        
        prev_cost = current_cost
        if current_cost < best_cost:
            if is_valid(current_route,n,k):
                best_cost = current_cost
                route = current_route[:]
                prev_cost = best_cost
            else:
                prev_cost = best_cost
        else:
            prev_cost = best_cost
    print(n)
    print(" ".join(map(str,route)))
if __name__ == '__main__':
    solve()