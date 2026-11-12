# Chapter 6: Exercises

### 1. Trace an uncertain write

A write with key `job:1`, target 20 and expected revision 4 loses its response. What may the next write contain?

### 2. Prove an invariant

A machine has `GATE`, `EXECUTE` and `DONE`. Its only transition emitting `issue(p)` goes from `GATE` to `EXECUTE` and has guard `approved(p)`. Other transitions emit no writes. State an invariant and outline the induction.

### 3. Analyse two controllers

Controllers A and B read value 10 at revision 0. A proposes 20; B proposes 15. Both issue conditional writes expecting revision 0. What follows from an atomic conditional-write contract?

### 4. Complete a state machine

A design has `READ → WRITE → DONE` on success and `WRITE → RETRY` on timeout. `RETRY` always returns to `WRITE`. Identify missing elements.

### 5. Select a claim

An authoritative, sufficiently fresh read shows the requested value. No receipt or operation-status record is available. Can the controller claim `OPERATION_VERIFIED`?

### 6. Construct a crash counterexample

A service writes a value and then separately records a deduplication key. The client persists the key before dispatch. Construct a trace in which the intended effect occurs twice.

### 7. Distinguish stale matching evidence from linked evidence

Consider a resource history: revision 5 has value 20; revision 6 changes it to 10; operation `k` changes it to 20 at revision 7. A replica returns value 20 at revision 5 after the controller receives a receipt for revision 7. What can the controller conclude? What additional observation could support the stronger claim?

### 8. Extend the laboratory without overstating its guarantee

Add a test in which a duplicate key is submitted with the same target but a different expected revision. What should the test assert, and what would it not prove?

### 9. Examine liveness assumptions

A controller has a three-write budget, but each remote call can block indefinitely. Does the budget prove that it reaches `DONE` or `ESCALATE`?
