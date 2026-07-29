import sys

n = 0                   
k = 0                   
c = []                  
c_min = float('inf')    
visited = []            
x = []                  
x_best = []             
z_best = float('inf')   
load = 0                
current_distance = 0    

def check(v):
    #Check constraints before assigning point v to the route
    global load, visited, n, k
    
    if visited[v]:
        return False
    
    if v > n: 
        if not visited[v - n]:
            return False
    else:
        if load + 1 > k:
            return False
            
    return True

def Try(step):
    """
    Core Branch and Bound recursive function
    """
    global load, current_distance, z_best, x_best, visited, x, n, c, c_min
    
    for v in range(1, 2 * n + 1):
        if check(v):
            x[step] = v
            visited[v] = True
            current_distance += c[x[step - 1]][v]
            if v <= n:
                load += 1
            else:
                load -= 1
                
            # Lower bound calculation: current distance + estimated remaining distance
            lower_bound = current_distance + (2 * n - step + 1) * c_min
            
            if lower_bound < z_best:
                if step == 2 * n:
                    total_distance = current_distance + c[x[2 * n]][0]
                    if total_distance < z_best:
                        z_best = total_distance
                        x_best = list(x)
                else:
                    Try(step + 1)
            
            # Backtracking state restoration
            visited[v] = False
            current_distance -= c[x[step - 1]][v]
            if v <= n:
                load -= 1
            else:
                load += 1

def solve_cbus():
    global n, k, c, c_min, visited, x, x_best, z_best, load, current_distance
    
    input_data = """5 3
0 5 8 11 12 8 3 3 7 5 5
5 0 3 5 7 5 3 4 2 2 2
8 3 0 7 8 8 5 7 1 6 5
11 5 7 0 1 5 9 8 6 5 6
12 7 8 1 0 6 10 10 7 7 7
8 5 8 5 6 0 8 5 7 3 4
3 3 5 9 10 8 0 3 4 5 4
3 4 7 8 10 5 3 0 6 2 2
7 2 1 6 7 7 4 6 0 5 4
5 2 6 5 7 3 5 2 5 0 1
5 2 5 6 7 4 4 2 4 1 0"""
    
    lines = input_data.strip().split('\n')
    n, k = map(int, lines[0].split())
    
    c = []
    for i in range(1, 2 * n + 2):
        row = list(map(int, lines[i].split()))
        c.append(row)
        for val in row:
            if 0 < val < c_min:
                c_min = val
                
    visited = [False] * (2 * n + 1)
    x = [0] * (2 * n + 1)
    x_best = [0] * (2 * n + 1)
    x[0] = 0
    
    Try(1)
    
    print(n)
    print(" ".join(map(str, x_best[1:])))

if __name__ == '__main__':
    solve_cbus()