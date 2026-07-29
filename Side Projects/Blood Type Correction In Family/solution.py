import sys
from ortools.linear_solver import pywraplp
input = sys.stdin.readline
data = {}
n= int(input())
mom = [-1]*(n)
dad = [-1]*(n)
blood_type = ['O']*n
for i in range(n):
    k = input().split()
    child,blood,f,m = int(k[0]),k[1],int(k[2]),int(k[3])
    blood_type[child] = blood
    mom[child] = m
    dad[child] = f
data['mom'] = mom
data['dad'] = dad
data['blood_type'] = blood_type
solver = pywraplp.Solver.CreateSolver("SCIP")
infinity = solver.infinity()
# Khai báo biến x (Đại diện cho quyết định gán nhóm máu)
# x[1,i]: Nhóm O | x[2,i]: Nhóm A | x[3,i]: Nhóm B | x[4,i]: Nhóm AB
x = {}
for i in range(n):
    for j in range(4):
        x[j+1,i] = solver.IntVar(0,1,f'x[{j+1},{i}]')
    solver.Add(sum([x[j+1,i] for j in range(4)]) == 1)
    
# z[a,b] = 1 nếu a,b là bố mẹ, 0 nếu không phải
z = {}
for i in range(n):
    a,b = data['dad'][i],data['mom'][i]
    if a != -1 and b != -1:
        z[a,b] = solver.IntVar(0,1,f'z[{a},{b}]')
        solver.Add(z[a,b] <= x[2,a])
        solver.Add(z[a,b] <= x[3,b])
        solver.Add( x[2,a]+ x[3,b] <= z[a,b] + 1)
        z[b,a] = solver.IntVar(0,1,f'z[{b},{a}]')
        solver.Add(z[b,a] <= x[2,b])
        solver.Add(z[b,a] <= x[3,a])
        solver.Add( x[2,b]+ x[3,a] <= z[b,a] + 1)
            
#1. con là O thì bố mẹ không thể cùng là AB
for i in range(n):
    if data['dad'][i] != -1 and data['mom'][i] != -1:
        solver.Add( 2 * (1-x[1,i]) - x[4,data['dad'][i]] - x[4,data['mom'][i]] >= 0)
        
# 2. con là A thì bố hoặc mẹ là A hoặc AB
for i in range(n):
    if data['dad'][i] != -1 and data['mom'][i] != -1:
        solver.Add( (1 - x[2,i]) + x[4,data['dad'][i]] + x[4,data['mom'][i]] + x[2,data['dad'][i]] + x[2,data['mom'][i]] >= 1)
    
# 3. con là B thì bố hoặc mẹ là B hoặc AB
for i in range(n):
    if data['dad'][i] != -1 and data['mom'][i] != -1:
        solver.Add( (1 - x[3,i]) + x[4,data['dad'][i]] + x[4,data['mom'][i]] + x[3,data['dad'][i]] + x[3,data['mom'][i]] >= 1)
    
# 4. con là AB thì bố và mẹ không thể là O; bố hoặc mẹ là AB HOẶC bố là A, mẹ là B; và ngược lại
for i in range(n):
    if data['dad'][i] != -1 and data['mom'][i] != -1:
        solver.Add( (1 - x[4,i]) - x[1,data['dad'][i]] - x[1,data['mom'][i]] + z[data['dad'][i],data['mom'][i]] + z[data['mom'][i],data['dad'][i]] + x[4,data['mom'][i]] + x[4,data['dad'][i]] >= 1)
# Biến y[i] = 1 nếu nhóm máu của người i bị sai, 0 nếu đúng
y = {}
for i in range(n):
    y[i] = solver.IntVar(0,1,f'y[{i}]')
    if data['blood_type'][i] == 'O':
        solver.Add( y[i] == x[2,i] + x[3,i] + x[4,i])
    elif data['blood_type'][i] == 'A':
        solver.Add( y[i] == x[1,i] + x[3,i] + x[4,i])
    elif data['blood_type'][i] == 'B':
        solver.Add( y[i] == x[1,i] + x[2,i] + x[4,i])
    elif data['blood_type'][i] == 'AB':
        solver.Add( y[i] == x[1,i] + x[3,i] + x[2,i])
    
# objective
solver.Minimize(sum([y[i] for i in range(n)]))
    
status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    print(round(solver.Objective().Value()))
else:
    print("No result")
