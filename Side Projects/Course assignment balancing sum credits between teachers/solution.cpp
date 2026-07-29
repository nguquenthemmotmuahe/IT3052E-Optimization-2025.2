#include <bits/stdc++.h>
using namespace std;

const int MAX_M = 15;
const int MAX_N = 35;
const int INF = 1e9;

int m, n;
bool can_teach[MAX_M][MAX_N]; 
bool conflict[MAX_N][MAX_N];  
int crd[MAX_N];              
int current_load[MAX_M];     
int assigned[MAX_N];          
int min_max_load = INF;      


bool check(int t, int c) {
    if (!can_teach[t][c]) return false;
    
    for (int i = 1; i < c; i++) {
        if (assigned[i] == t && conflict[i][c]) {
            return false;
        }
    }
    return true;
}

void Try(int c) {
    if (c > n) {
        int max_load = 0;
        for (int i = 1; i <= m; i++) {
            if (current_load[i] > max_load) {
                max_load = current_load[i];
            }
        }
        if (max_load < min_max_load) {
            min_max_load = max_load;
        }
        return;
    }

    for (int t = 1; t <= m; t++) {
        if (check(t, c)) {
            if (current_load[t] + crd[c] < min_max_load) {
                assigned[c] = t;
                current_load[t] += crd[c];
                Try(c + 1);
                assigned[c] = 0;
                current_load[t] -= crd[c];
            }
        }
    }
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    
    if (!(cin >> m >> n)) return 0;

    for (int i = 1; i <= m; i++) {
        int k; cin >> k;
        for (int j = 0; j < k; j++) {
            int c; cin >> c;
            can_teach[i][c] = true;
        }
    }

    for (int i = 1; i <= n; i++) {
        cin >> crd[i];
    }
    int k; cin >> k;
    for (int i = 0; i < k; i++) {
        int u, v; cin >> u >> v;
        conflict[u][v] = true;
        conflict[v][u] = true; 
    }
    
    Try(1);
    if (min_max_load == INF) {
        cout << -1 << "\n";
    } else {
        cout << min_max_load << "\n";
    }

    return 0;
}
