# Chapter 5: Worked solutions

### 1. Change a route cost

**Suggested solution.** \(S\to B\to C\to G\) costs \(2+1+2=5\). The route through \(A\) and \(C\) costs \(1+5+2=8\); each direct route costs 9. The open door does not make the \(A\) route optimal.

### 2. Reproduce the changed-cost search

**Suggested solution.**

```python
from route_lab import EDGES, uniform_cost

graph = {node: list(edges) for node, edges in EDGES.items()}
graph["A"] = [("C", 5), ("G", 8)]

result = uniform_cost(graph, "S", "G")
assert result == (5, ("S", "B", "C", "G"))
print(result)
```

Run `python3 changed_cost.py`. If the assertion succeeds, the programme prints:

```text
(5, ('S', 'B', 'C', 'G'))
```

This is an expected result derived from the hypothetical graph, not an embedded observed execution record. The exercise changes the graph supplied directly to search; it does not change the simulator’s separate `COST` table or test physical execution.

### 3. Identify the state

**Suggested solution.** No. Include badge possession in the state and define how actions change it. With the supplied directed graph, reaching \(B\) gives no route back to \(A\); adding such an edge without evidence would change the problem. The executor also needs an independent rule for checking the badge.

### 4. Distinguish claim types

**Suggested solution.** The service report is an observation attributed to a source and time. Continued openness is a prediction, not a consequence established by the report. Caller authorisation is a permission claim requiring its own authority. The move request is an attempt. A timeout is an observation about the response, not confirmation of the robot’s position. The final conclusion is unsupported until authoritative operation status or position is reconciled.

### 5. Goal discovery

**Suggested solution.** Expanding \(A\) discovers \(G\) at cost 9, while expanding \(C\) later discovers a route of cost 4. Under the stated non-negative-cost assumptions, the guarantee applies when a lowest-cost goal entry is removed from the priority queue.

### 6. Construct an inconsistent heuristic

**Suggested solution.** The true minimum remaining costs from \(S,A,B,G\) are respectively \(3.5,2,2.5,0\), so none of the heuristic values overestimates. However, consistency on \(B\to A\) would require \(h(B)\leq0.5+h(A)\); instead \(2.5>0.5\).

A* first removes \(A\), reached directly at \(g=2\), before \(B\), whose \(f\) is \(1+2.5=3.5\). Expanding \(A\) gives a goal of cost 4. Expanding \(B\) later finds \(A\) at the improved cost \(1.5\). If the implementation discards that improvement because \(A\) is closed, it can return cost 4, missing the optimal \(S\to B\to A\to G\) route of cost 3.5. Reopening \(A\) allows the improved route to be propagated.

### 7. Freshness and timing

**Suggested solution.** Timestamp 5 is usable at time 10 because its age is exactly 5. Timestamp 4 is stale; timestamp 11 is in the future. At time 11 the first report has age 6 and is no longer usable. A check at planning time therefore does not automatically remain valid at execution time.

### 8. Information value

**Suggested solution.** Expected route cost after the check is \(0.8(4)+0.2(5)=4.2\). The gross benefit is \(5-4.2=0.8\); after the check cost it is \(0.7\) units. The answer retains the assumptions of a perfect observation, no intervening change and no other costs.

### 9. Ambiguous timeout

**Suggested solution.** Not without an idempotency and status protocol. The action may have occurred despite the missing response. Query an authoritative operation record using the original identifier, reconcile position and retry only under a documented rule. If status cannot be established safely, stop or escalate.

### 10. Design an additional laboratory test

**Suggested solution.** Give the planner a fresh “open” report while an independent simulated actuator rejects \(A\to C\). Assert that the search initially proposes the shortcut, the actuator rejection is recorded, no move across the door is confirmed, and recovery either finds an authorised alternative or returns a distinct failure. The search can be correct relative to its input while its prediction is invalid in the simulated world.
