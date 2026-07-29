import sys

def solve():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
        
    n = int(input_data[0])
    
    evens = list(range(2, n + 1, 2))
    odds = list(range(1, n + 1, 2))
    
    rem = n % 6
    if rem == 2:
        if len(odds) >= 2:
            odds[0], odds[1] = odds[1], odds[0]
        if len(odds) >= 3:
            odds.append(odds.pop(2))
            
    elif rem == 3:
        if len(evens) >= 1:
            evens.append(evens.pop(0))
        if len(odds) >= 2:
            odds.append(odds.pop(0))
            odds.append(odds.pop(0))
            
    ans = evens + odds
    
    print(n)
    print(" ".join(map(str, ans)))

if __name__ == '__main__':
    solve()
