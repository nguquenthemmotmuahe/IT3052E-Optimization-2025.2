
# CBUS: Capacitated Bus Routing Problem
**Fundamental Optimization Course Project — HUST**

---

## 1. Project Overview & Formulation
This project evaluates four optimization paradigms to solve the **Capacitated Bus Routing Problem (CBUS)**. The objective is to determine the optimal closed-loop routing trajectory for a single vehicle originating and terminating at a central depot (node 0), minimizing total travel distance while strictly satisfying three core constraints:

* **Visit Exactness:** Every designated pickup and delivery location must be visited exactly once.
* **Precedence:** For each passenger $i\in\{1,\dots,n\}$, pickup node $i$ must be visited before its corresponding delivery node $i+n$.
* **Vehicle Capacity:** The instantaneous passenger load must never exceed the maximum vehicle capacity $K$.

### Implemented Optimization Paradigms
1.  **Branch and Bound (B&B):** Exact combinatorial tree search with lower-bound pruning.
2.  **Mixed-Integer Linear Programming (MILP):** Exact mathematical programming solved via the SCIP backend.
3.  **Constraint Programming (CP-SAT):** High-level domain propagation via Google OR-Tools.
4.  **Heuristics & Metaheuristics:** Greedy constructive initialization, Local Search (Pairwise Swap & Random Walk), and Memory-Guided Tabu Search for large-scale scalability.

---

## 2. Repository Structure
```text
.
├── BranchAndBound/
│   └── branch_and_bound.py      # Method 1: Tree-search with LB pruning
├── ILP/
│   └── ilp_cbus.py              # Method 2: MILP formulation via SCIP
├── CP_SAT/
│   └── CBUS.py                  # Method 3: CP formulation via OR-Tools
├── Heuristics_Metaheuristics/
│   ├── Greedy.py                # Method 4.0: Greedy initialization
│   ├── LS_Swap.py               # Method 4.1: Local Search (Pairwise swap)
│   ├── LS_RandomWalk.py         # Method 4.2: Local Search (Stochastic exploration)
│   └── TabuSearch.py            # Method 4.3: Memory-guided Tabu Search
├── Slides.pdf / Report.pdf      # Presentation slide deck and technical report
└── README.md                    # Primary project documentation

```

---

## 3. Standard I/O Specifications

### Input Format (`stdin`)

```text
n K
d[0][0] d[0][1] ... d[0][2n]
...
d[2n][0] d[2n][1] ... d[2n][2n]

```

* **Node 0:** Central depot (origin & destination terminal).
* **Nodes $1 \dots n$:** Pickup locations for passengers $1 \dots n$.
* **Nodes $n+1 \dots 2n$:** Delivery locations (node $i+n$ is the destination for passenger $i$).
* **$d[i][j]$:** Non-negative integer travel distance from node $i$ to node $j$.

### Output Format

* **Feasible Solution:** Prints total passengers $n$ on line 1, followed by the optimal tour sequence $v_1, v_2, \dots, v_{2n}$ (excluding depot node 0).
* **Infeasible Instance:** Prints `No feasible solution`.

---

## 4. Execution Guide

**Prerequisites:** Python $\ge 3.10$, Google OR-Tools (`pip install ortools`).

```bash
# Method 1: Branch and Bound
python BranchAndBound/branch_and_bound.py < testcases/input.txt

# Method 2: Integer Linear Programming (Ensure local disk file-open paths are commented out)
python ILP/ilp_cbus.py < testcases/input.txt

# Method 3: Constraint Programming (CP-SAT)
python CP_SAT/CBUS.py < testcases/input.txt

# Method 4: Heuristics & Metaheuristics
python Heuristics_Metaheuristics/Greedy.py < testcases/input.txt
python Heuristics_Metaheuristics/LS_Swap.py < testcases/input.txt
python Heuristics_Metaheuristics/LS_RandomWalk.py < testcases/input.txt
python Heuristics_Metaheuristics/TabuSearch.py < testcases/input.txt

```

---

## 5. Algorithmic Comparison

| Method | Computational Engine | Optimality | Time Complexity | Recommended Application Context |
| --- | --- | --- | --- | --- |
| **B&B** | Tree Search + LB Pruning | Global Optimal | Exponential $O((2n)!)$ | Highly constrained, very small instances ($n\le 10$). Foundational baseline for exactness verification. |
| **ILP** | SCIP (MILP / Branch-and-Cut) | Global Optimal | Exponential | Small to medium instances ($n\le 15$). Provides rigorous mathematical dual bounds and analytical proofs. |
| **CP-SAT** | Boolean SAT + Propagation | Global Optimal | Exponential | Medium instances ($n\le 25$). Superior speed over ILP when handling complex disjunctive precedence rules. |
| **Metaheuristics** | Local Search + Tabu Memory | Near-Optimal | Polynomial $O(N^2)$ / iter | Large-scale, real-world instances ($n>50$). Generates high-quality feasible routing schedules within seconds. |

---

## 6. Technical Notes & Mathematical Rationale

### ILP Precedence and Capacity Formulation

To enforce that passenger $i$ is picked up prior to delivery at node $i+n$, continuous arrival time variables $t_i$ are constrained as:


$$t_i\le t_{i+n}\quad\forall i\in\{1,\dots,n\}$$

Instantaneous vehicle load transitions between consecutive nodes $i$ and $j$ are linearized using Big-M conditional constraints:


$$y_j-y_i-q_j\le M_y(1-x_{i,j})$$

$$y_j-y_i-q_j\ge-M_y(1-x_{i,j})$$

Where:

* $x_{i,j}$: Binary decision variable ($1$ if traveling directly from node $i$ to $j$, $0$ otherwise).
* $y_i$: Vehicle load departing from node $i$.
* $M_y$: Sufficiently large positive constant ($K+2$).
* $q_j$: Passenger load delta at node $j$, defined as:
* $q_j=+1$ for pickup locations ($1\le j\le n$)
* $q_j=-1$ for delivery locations ($n+1\le j\le 2n$)
* $q_0=0$ for the central depot



### CP-SAT vs. ILP Efficiency

ILP relies on continuous linear relaxations that frequently degrade in strength when modeling disjunctive scheduling and logical orderings. In contrast, **CP-SAT** operates directly on discrete domains using boolean satisfiability and constraint propagation. For the CBUS problem, where precedence relationships strictly restrict valid tour permutations, CP-SAT achieves faster domain pruning and establishes initial feasible solutions significantly quicker than traditional branch-and-cut MILP solvers.

---

## 7. Attribution

* **Course:** Fundamental Optimization — Hanoi University of Science and Technology (HUST)
* **Department:** School of Information and Communication Technology (SOICT) / Cyber Security
* **Authors:**
* Student Name 1 - Student ID 1
* Student Name 2 - Student ID 2
* Student Name 3 - Student ID 3



```

```
