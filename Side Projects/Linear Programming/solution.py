import sys
from ortools.linear_solver import pywraplp

def solve_lp():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    
    iterator = iter(input_data)
    
    try:
        N = int(next(iterator))
        M = int(next(iterator))
        
        bounds = [(float(next(iterator)), float(next(iterator))) for _ in range(N)]
        C = [float(next(iterator)) for _ in range(N)]
        A = [[float(next(iterator)) for _ in range(N)] for _ in range(M)]
        
        low = []
        up = []
        for _ in range(M):
            low.append(float(next(iterator)))
            up.append(float(next(iterator)))
            
    except StopIteration:
        pass

    solver = pywraplp.Solver.CreateSolver('GLOP')
    x = []
    for i in range(N):
        x.append(solver.NumVar(bounds[i][0], bounds[i][1], f'x{i}'))

    for i in range(M):
        constraint = solver.Constraint(low[i], up[i], f'c{i}')
        for j in range(N):
            constraint.SetCoefficient(x[j], A[i][j])

    objective = solver.Objective()
    for j in range(N):
        objective.SetCoefficient(x[j], C[j])
    
    objective.SetMaximization()
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        print(N)
        print(" ".join(f"{x[j].solution_value():.1f}" for j in range(N)))
    else:
        print("NOT_OPTIMAL")

if __name__ == '__main__':
    solve_lp()
