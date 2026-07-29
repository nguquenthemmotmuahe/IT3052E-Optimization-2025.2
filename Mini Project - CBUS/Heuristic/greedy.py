import sys

def solve():
    input_data = sys.stdin.read().split()

    n = int(input_data[0])
    k = int(input_data[1])

    c = []

    index = 2
    for _ in range(2*n+1):
        row = []
        for _ in range(2*n+1):
            row.append(int(input_data[index]))
            index +=1
        c.append(row)

    route = [] 
    visited = [False]*(2*n+1)
    load = 0
    current_node = 0
    # Journey of the bus going from first stop to last stop 
    for i in range(2*n):
        best_next = -1
        min_distance = float('inf')
        # Finding the next best node from current node by iterating
        for v in range(1,2*n+1):
            # Constraints
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
            
    print(n)
    print(" ".join(map(str,route)))
if __name__ == '__main__':
    solve()