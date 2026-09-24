# Mixed Integer Linear Programming (MILP) Gate Assignment Model

## 1. Sets and Indices
* $\mathcal{F} = \{1, 2, \dots, N\}$: Set of flights to be scheduled.
* $\mathcal{G} = \{1, 2, \dots, M\}$: Set of available airport gates.
* $\mathcal{C} = \{(f_1, f_2) \in \mathcal{F} \times \mathcal{F} \mid f_1 < f_2 \text{ and } [t^{arr}_{f_1} + \delta_{f_1}, t^{dep}_{f_1} + b] \cap [t^{arr}_{f_2} + \delta_{f_2}, t^{dep}_{f_2} + b] \neq \emptyset\}$: Set of flight pairs whose effective occupancy intervals overlap when accounting for predicted delay $\delta$ and operational buffer $b$.
* $\mathcal{K}_{f} \subseteq \mathcal{G}$: Set of compatible gates for flight $f$ satisfying aircraft type and terminal compatibility.

## 2. Decision Variables
* $x_{f, g} \in \{0, 1\}$: Binary decision variable equal to $1$ if flight $f$ is assigned to gate $g$, and $0$ otherwise.
* $u_f \in \{0, 1\}$: Binary slack variable equal to $1$ if flight $f$ cannot be assigned to any compatible gate due to capacity saturation (unassigned flight penalty).

## 3. Objective Function
$$\min \sum_{f \in \mathcal{F}} \sum_{g \in \mathcal{K}_f} c_{f, g} \cdot x_{f, g} + \sum_{f \in \mathcal{F}} P_{unassigned} \cdot u_f$$

Where the individual assignment cost $c_{f, g}$ is defined as a weighted multi-term penalty:
$$c_{f, g} = w_2 \cdot \text{WalkScore}(g) + w_3 \cdot \left(\frac{\delta_f}{10}\right) \cdot \mathbb{I}(\delta_f > 15) + w_4 \cdot \text{ReassignPenalty}(f, g)$$

### Default Objective Weights:
1. $w_1 = 1000$ (Gate Conflict / Unassigned Penalty $P_{unassigned} = 2 \times w_1$)
2. $w_2 = 1.0$ (Passenger Walking Distance Penalty)
3. $w_3 = 10.0$ (Delay Propagation Vulnerability Penalty)
4. $w_4 = 5.0$ (Gate Reassignment from Baseline Plan)
5. $w_5 = 1.0$ (Unused Gate Distribution Penalty)

## 4. Constraints

### Constraint 1: Exact / Feasible Assignment
Every flight must be assigned to exactly one compatible gate, or flagged as unassigned via the slack variable:
$$\sum_{g \in \mathcal{K}_f} x_{f, g} + u_f = 1 \quad \forall f \in \mathcal{F}$$

### Constraint 2: Gate Compatibility Restriction
Incompatible gates cannot be assigned:
$$x_{f, g} = 0 \quad \forall g \notin \mathcal{K}_f, \; \forall f \in \mathcal{F}$$

### Constraint 3: No Overlapping Flights on the Same Gate (Non-Overlap)
For any pair of flights $(f_1, f_2) \in \mathcal{C}$ whose time windows intersect with buffer $b$:
$$x_{f_1, g} + x_{f_2, g} \le 1 \quad \forall g \in \mathcal{K}_{f_1} \cap \mathcal{K}_{f_2}, \; \forall (f_1, f_2) \in \mathcal{C}$$

### Constraint 4: Turnaround Time and Delay Dynamics
The occupancy window of flight $f$ at gate $g$ begins at effective arrival $t^{arr}_f + \max(0, \delta_f)$ and terminates at $\max(t^{dep}_f, t^{arr}_f + \delta_f + \text{Turnaround}_f)$.

### Constraint 5: Gate Availability & Operational State
$$x_{f, g} = 0 \quad \forall g \text{ where } \text{IsAvailable}(g) = \text{False}$$

## 5. Solver Abstraction
The optimization engine exposes a common `BaseOptimizer` interface allowing seamless switching between:
- **Google OR-Tools (SCIP/CBC)** for open-source high-throughput optimization.
- **Gurobi Optimizer** for enterprise performance with automated fallback.
