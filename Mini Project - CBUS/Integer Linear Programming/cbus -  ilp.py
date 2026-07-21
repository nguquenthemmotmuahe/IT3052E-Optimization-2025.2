# Integer Linear Programming: Bản chẩt là bài toán Quy hoạch tuyến tính, tuy nhiên ILP có điều kiện nghiêm ngặt hơn
# là các biến tối ưu phải ít nhất có 1 biến nguyên (thường là tất cả đều phải nguyên). Vì vậy không thể chỉ sử dụng phương
# pháp Simplex cho bài toán ILP mà cần phải sử dụng Backtracking + Branch and Bound dựa trên điều kiện của Simplex

# OR-TOOLS có module cho ILP nên mình hoàn toàn có thể ngay lập tức sử dụng
import sys
from ortools.linear_solver import pywraplp

def ilp_cbus():
    # Xử lí dữ liệu 
    sys.stdin = open(r'E:\Project\IT3052E\input.txt', 'r')
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    
    n = int(input_data[0])
    K = int(input_data[1])
    
    total_nodes = 2 * n + 1  
    
    distance_matrix = []
    idx = 2
    for i in range(total_nodes):
        row = []
        for j in range(total_nodes):
            row.append(int(input_data[idx]))
            idx += 1
        distance_matrix.append(row)

    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        print("Không thể khởi tạo SCIP solver.")
        return
        
    x = {} # x[i, j] = 1 nếu xe đi từ i đến j
    for i in range(total_nodes):
        for j in range(total_nodes):
            if i != j:
                x[i, j] = solver.BoolVar(f'x_{i}_{j}')
                
    t = {}
    y = {} 
    for i in range(total_nodes):
        t[i] = solver.IntVar(0, total_nodes + 1, f't_{i}')
        y[i] = solver.IntVar(0, K, f'y_{i}')

    q = [0] * total_nodes
    for i in range(1, n + 1):
        q[i] = 1         
        q[i + n] = -1    

    
    for i in range(total_nodes):
        # Tổng luồng đi ra từ i bằng 1
        solver.Add(solver.Sum([x[i, j] for j in range(total_nodes) if i != j]) == 1)
        # Tổng luồng đi vào i bằng 1
        solver.Add(solver.Sum([x[j, i] for j in range(total_nodes) if i != j]) == 1)

    for i in range(1, n + 1):
        solver.Add(t[i] <= t[i + n])

    solver.Add(t[0] == 0)
    solver.Add(y[0] == 0)

    M_t = total_nodes + 2
    M_y = K + 2
    
    for i in range(total_nodes):
        for j in range(total_nodes):
            if i != j:
                if j != 0:
                    solver.Add(t[j] >= t[i] + 1 - M_t * (1 - x[i, j]))
                    solver.Add(y[j] - y[i] - q[j] <= M_y * (1 - x[i, j]))
                    solver.Add(y[j] - y[i] - q[j] >= -M_y * (1 - x[i, j]))

    objective = solver.Objective()
    for i in range(total_nodes):
        for j in range(total_nodes):
            if i != j:
                objective.SetCoefficient(x[i, j], distance_matrix[i][j])
    objective.SetMinimization()
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        route = []
        current_node = 0
        
        while True:
            for j in range(total_nodes):
                if current_node != j and x[current_node, j].solution_value() > 0.5:
                    if j != 0:
                        route.append(j)
                    current_node = j
                    break
            if current_node == 0:
                break
                
        print(n)
        print(" ".join(map(str, route)))
    else:
        print("Không tìm thấy nghiệm thỏa mãn.")

if __name__ == '__main__':
    ilp_cbus()