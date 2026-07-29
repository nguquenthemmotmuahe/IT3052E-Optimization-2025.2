import sys
from ortools.linear_solver import pywraplp

def solve():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    
    K = int(input_data[0])
    N = int(input_data[1])
    
    c = [int(input_data[i]) for i in range(2, 2 + K)]
    idx = 2 + K

    r = [0] + [int(input_data[i]) for i in range(idx, idx + N)] 
    idx += N
    
    V = N + 1 
    D = []
    for i in range(V):
        row = []
        for j in range(V):
            row.append(int(input_data[idx]))
            idx += 1
        D.append(row)
        
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return

    X = {}
    for i in range(V):
        for j in range(V):
            for k in range(K):
                X[i, j, k] = solver.IntVar(0, 1, f'X_{i}_{j}_{k}')
                
    U = {}
    for i in range(1, V):
        U[i] = solver.NumVar(0, max(c), f'U_{i}')
    
    for i in range(1, V):
        solver.Add(sum(X[i, j, k] for j in range(V) for k in range(K) if i != j) == 1)
        
    for h in range(V):
        for k in range(K):
            solver.Add(sum(X[i, h, k] for i in range(V) if i != h) == sum(X[h, j, k] for j in range(V) if j != h))
            

    for k in range(K):
        solver.Add(sum(X[0, j, k] for j in range(1, V)) == 1)
        solver.Add(sum(X[i, 0, k] for i in range(1, V)) == 1)

    M = max(c)
    for k in range(K):
        for i in range(1, V):
            solver.Add(U[i] >= r[i])
            solver.Add(U[i] <= c[k] + M * (1 - sum(X[j, i, k] for j in range(V))))
            
            for j in range(1, V):
                if i != j:
                    solver.Add(U[j] >= U[i] + r[j] - M * (1 - X[i, j, k]))

    objective = solver.Objective()
    for i in range(V):
        for j in range(V):
            for k in range(K):
                if i != j:
                    objective.SetCoefficient(X[i, j, k], D[i][j])
    objective.SetMinimization()

    status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL:
        print(K) 
        for k in range(K):
            route = []
            curr = 0 
            while True:
                next_node = -1
                for j in range(V):
                    if curr != j and X[curr, j, k].solution_value() > 0.5:
                        next_node = j
                        break
                if next_node == -1 or next_node == 0:
                    break
                route.append(next_node)
                curr = next_node

            if route:
                print(f"{len(route)} " + " ".join(map(str, route)))
            else:
                print("0")

if __name__ == '__main__':
    solve()
