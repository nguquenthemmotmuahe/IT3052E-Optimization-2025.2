# This approach has two phase, combining both Heuristics and Local Search
# 1. Quickly find the First Solution by using Heuristics (Parallell Cheapest Insertion strategy will be used)
# 2. Optimize using Local Search (Guided LS strategy will be used)
# We will apply the OR - TOOLS to solve this problem by computing in 3 dimensions: Distance, Capacity and Constraint
# 1. Distance: Track the total distance that the bus has run. We need to minimize this.
# 2. Capacity: Track the number of passengers on the bus. Limit by k as given.
# 3. Constraint: The bus can only visit point i+n after visiting point i

#CODE
import sys
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def solution():
    # 1. Input Handling    
    inputdata = sys.stdin.read().split()
    n = int(inputdata[0])
    k = int(inputdata[1])
    nodes = 2 * n + 1

    # 2. Distance matrix c (2-D arrays)
    idx = 2
    distance_matrix = []
    for i in range(nodes):
        row = []
        for j in range(nodes):
            row.append(int(inputdata[idx]))
            idx += 1
        distance_matrix.append(row)

    # 3. Model Initial Setting (The bus starts and ends at point 0)
    manager = pywrapcp.RoutingIndexManager(nodes, 1, 0)
    route = pywrapcp.RoutingModel(manager)

    # 4. Setup Distance dimension
    def distance_callback(from_idx, to_idx):
        from_node = manager.IndexToNode(from_idx)
        to_node = manager.IndexToNode(to_idx)
        return distance_matrix[from_node][to_node]
    
    distance_callback_idx = route.RegisterTransitCallback(distance_callback)
    route.SetArcCostEvaluatorOfAllVehicles(distance_callback_idx)
    route.AddDimension(distance_callback_idx, 0, 300000000, True, 'Distance')
    distance_dimension = route.GetDimensionOrDie('Distance')

    # 5. Setup Capacity dimension
    # Depot = 0, Pickup passengers(1->n) = 1, Dropoff passengers(n+1->2n) = -1. Capacity <= k
    capacity = [0] * nodes
    for i in range(1, n+1):
        capacity[i] = 1
        capacity [i+n] = -1
    def capacity_callback(from_idx):
        from_node = manager.IndexToNode(from_idx)
        return capacity[from_node]
    
    capacity_callback_idx = route.RegisterUnaryTransitCallback(capacity_callback)
    route.AddDimension(capacity_callback_idx, 0, k, True, 'Capacity')

    # 6. Constraint
    solver = route.solver()
    for i in range(1, n+1):
        start_idx = manager.NodeToIndex(i)
        end_idx = manager.NodeToIndex(i+n)

        route.AddPickupAndDelivery(start_idx, end_idx)
        solver.Add(distance_dimension.CumulVar(start_idx) <= distance_dimension.CumulVar(end_idx))

    # 7. Optimization Algorithm
    search = pywrapcp.DefaultRoutingSearchParameters()
    search.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)
    search.local_search_metaheuristic = (routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)

    # 8. Model running and return optimized solution
    result = route.SolveWithParameters(search)
    if result:
        print(n)
        index = route.Start(0)
        optimized_route = []
        while not route.IsEnd(index):
            node_idx = manager.IndexToNode(index)
            if node_idx != 0:
                optimized_route.append(str(node_idx))
            index = result.Value(route.NextVar(index))
        print(" ".join(optimized_route))

if __name__ == '__main__':
    solution()
