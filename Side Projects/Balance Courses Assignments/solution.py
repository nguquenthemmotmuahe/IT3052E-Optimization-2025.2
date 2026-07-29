import sys

def solve():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
        
    m = int(input_data[0])
    n = int(input_data[1])
    
    idx = 2
    can_teach = [[] for _ in range(n + 1)]
    for t in range(1, m + 1):
        k = int(input_data[idx])
        idx += 1
        for _ in range(k):
            c = int(input_data[idx])
            can_teach[c].append(t)
            idx += 1
            
    k_conflicts = int(input_data[idx])
    idx += 1
    conflict = [[False] * (n + 1) for _ in range(n + 1)]
    for _ in range(k_conflicts):
        u = int(input_data[idx])
        v = int(input_data[idx+1])
        conflict[u][v] = True
        conflict[v][u] = True
        idx += 2
        
    courses = list(range(1, n + 1))
    courses.sort(key=lambda c: len(can_teach[c]))
    
    assigned = [[] for _ in range(m + 1)]
    
    def check(c_idx, limit):
        if c_idx == n:
            return True
            
        c = courses[c_idx]
        for t in can_teach[c]:
            if len(assigned[t]) < limit:
                if not any(conflict[c][prev_c] for prev_c in assigned[t]):
                    assigned[t].append(c)
                    if check(c_idx + 1, limit):
                        return True
                    assigned[t].pop()
        return False

    low, high = 1, n
    res = -1
    while low <= high:
        mid = (low + high) // 2
        for i in range(1, m + 1):
            assigned[i].clear()
            
        if check(0, mid):
            res = mid
            high = mid - 1
        else:
            low = mid + 1
            
    print(res)

if __name__ == '__main__':
    solve()
