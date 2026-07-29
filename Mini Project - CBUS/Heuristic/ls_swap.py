import sys
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

    #Check validity of route
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

    # Calculate the expected delta when swapping two vertices by adding and subtracting edges
    def calculate_swap(route,i,j,c):
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

    route = Greedy(c,n,k)

    # 2-opt
    improved = True
    while improved and time.perf_counter() - start_time < 290:
        improved = False
        for i in range(N):
            for j in range(i+1, N):
                
                current_delta = calculate_swap(route, i, j, c)
                if current_delta < 0:
                    route[i], route[j] = route[j], route[i]
                    if is_valid(route, n, k):
                        improved = True
                        break 
                    else:
                        route[i], route[j] = route[j], route[i]  
            if improved:
                break 

    print(n)
    print(" ".join(map(str,route)))
if __name__ == '__main__':
    solve()
