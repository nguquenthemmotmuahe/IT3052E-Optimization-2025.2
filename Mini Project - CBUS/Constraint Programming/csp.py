from ortools.sat.python import cp_model

def read_input():
    n, k = map(int, input().split())
    distance = []
    for i in range(2*n + 1):
        dis = list(map(int, input().split()))
        distance.append(dis)
    return n, k, distance

def flatten_matrix(matrix):
    flat = []
    for row in matrix:
        flat.extend(row)
    return flat

def build_model(n, k, distance):
    model = cp_model.CpModel()

    # Variable declaration
    # since there are 2n+1 place (including 0), there are 2n+2 steps as bus return to 0

    customer = [model.NewIntVar(0, k, f'customer{i}') for i in range(2*n + 2)]              # number of customer at step i
    point = [model.NewIntVar(0, 2*n, f'point{i}') for i in range(2*n + 2)]                  # point duoc tham at step i
    index = {i : model.NewIntVar(1, 2*n, f'index{i}') for i in range(1, 2*n + 1)}           # step that position i duoc tham
    step_dist = [model.NewIntVar(0, 1000000, f'step_dist_{i}') for i in range(2*n + 1)]

    # Constraints

    model.Add(point[0] == 0)
    model.Add(point[2*n + 1] == 0)
    model.Add(customer[0] == 0)
    model.Add(customer[2*n + 1] == 0)

    model.AddAllDifferent(point[1:2*n+1])

    # Channeling between point[] and index[]
    for i in range(1, 2*n + 1):
        for j in range(1, 2*n + 1):
            b = model.NewBoolVar(f"index_{j}_is_{i}")
            model.Add(index[j] == i).OnlyEnforceIf(b)
            model.Add(index[j] != i).OnlyEnforceIf(b.Not())
            model.Add(point[i] == j).OnlyEnforceIf(b)
            model.Add(point[i] != j).OnlyEnforceIf(b.Not())

    # Pickup before delivery
    for i in range(1, n + 1):
        model.Add(index[i] < index[i + n])

    # Vehicle capacity
    for i in range(1, 2*n + 1):
        pickup = model.NewBoolVar(f'pickup_{i}')
        delivery = model.NewBoolVar(f'delivery_{i}')
        model.Add(point[i] <= n).OnlyEnforceIf(pickup)
        model.Add(point[i] >= n+1).OnlyEnforceIf(pickup.Not())
        model.Add(point[i] >= n+1).OnlyEnforceIf(delivery)
        model.Add(point[i] <= n).OnlyEnforceIf(delivery.Not())
        model.Add(customer[i] == customer[i - 1] + 1).OnlyEnforceIf(pickup)
        model.Add(customer[i] == customer[i - 1] - 1).OnlyEnforceIf(delivery)

    # Distance computation
    flat_matrix = flatten_matrix(distance) 
    for i in range(2*n + 1):
        matrix_idx = model.NewIntVar(0, (2*n + 1)*(2*n + 1) - 1, f'idx_{i}')
        model.Add(matrix_idx == point[i]*(2*n+1) + point[i+1])
        model.AddElement(matrix_idx, flat_matrix, step_dist[i])

    # Objective
    model.Minimize(sum(step_dist))
    return model, point


def solve(model):
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    return solver, status


def print_solution(solver, status, point, n):
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(n)
        print(*(solver.Value(point[i]) for i in range(1, 2 * n + 1)))
    else:
        print("No feasible solution")


def main():
    n, k, distance = read_input()
    model, point = build_model(n, k, distance)
    solver, status = solve(model)
    print_solution(solver, status, point, n)


if __name__ == "__main__":
    main()