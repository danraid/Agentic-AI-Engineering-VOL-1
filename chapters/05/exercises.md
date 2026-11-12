# Chapter 5: Exercises

### 1. Change a route cost

This is a **paper-and-pencil exercise**, independent of the canonical runner. Set \(A\to C\) to cost 5 in the hypothetical operational graph. What is the cheapest route when the door is open?

### 2. Reproduce the changed-cost search

Without modifying `route_lab.py` or its existing tests, create `changed_cost.py` in the same directory. Import `EDGES` and `uniform_cost`, copy the adjacency lists, and replace the \(A\to C\) cost with 5. Assert the result from Exercise 1.

### 3. Identify the state

A badge is collected at \(B\), and \(A\to C\) requires both an open door and a badge. Is location alone sufficient?

### 4. Distinguish claim types

An agent records: “The status service reported open at time 12; therefore the door will remain open. The caller is authorised to deliver. I requested a move. The request timed out, so the robot is still at \(A\).”

Classify each claim and identify the unsupported conclusion.

### 5. Goal discovery

Why must uniform-cost search not return as soon as it first discovers \(G\) in the worked graph?

### 6. Construct an inconsistent heuristic

Consider a directed graph with edges \(S\to A\) of cost 2, \(S\to B\) of cost 1, \(B\to A\) of cost \(0.5\), \(A\to G\) of cost 2, and \(B\to G\) of cost 100. Use

\[
h(S)=3.5,\quad h(A)=0,\quad h(B)=2.5,\quad h(G)=0.
\]

Show that the heuristic is admissible but inconsistent. What can happen if graph-search A* never reopens a closed state?

### 7. Freshness and timing

At time 10, with \(\tau=5\), classify open reports timestamped 5, 4 and 11. What if the report timestamped 5 is checked again at time 11?

### 8. Information value

In the hypothetical facility, suppose the probability of an open door is \(0.8\). The conservative route costs 5, the open-door route costs 4, and a perfect immediate check costs 0.1. What is the net expected route-cost benefit?

### 9. Ambiguous timeout

The actuator times out after a request to move from \(A\) to \(G\). Should the controller immediately resend it?

### 10. Design an additional laboratory test

Propose a test that distinguishes a correct search result from a valid operational decision.
