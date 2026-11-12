# Chapter 8: Exercises

The invoice and verifier figures in these exercises are **hypothetical teaching cases**, not empirical findings.

### 1. Identify the failed property

A draft uses the hypothetical supplied lines but reports 3,800 pence. Which diagnostic should the laboratory produce, and what total should a narrow repair insert?

### 2. Separate properties

Classify each statement as primarily safety, liveness, evidence or authorisation:

1. No payment is executed without a valid gate decision.
2. Every submitted case eventually completes or is escalated.
3. The approval record is authentic and current.
4. The actor may pay this beneficiary for this amount.

### 3. Analyse the budget

Run the controller conceptually with a wrong total, the normal repairer and `max_repairs=0`. What happens? What if the initial draft is correct?

### 4. Analyse correlated checks

Two checks each have a hypothetical 10% false-negative rate. Is their combined false-negative rate necessarily 1%?

### 5. Follow a two-state loop

A repairer alternates between invalid candidates \(A\) and \(B\). What happens with a budget of at least two repairs?

### 6. Specify rounding

Two taxable lines are each 5 pence. Tax is 10%, and half-pence is rounded up. Compute tax under line-level and invoice-level rounding.

### 7. Respond to a timeout

A payment provider receives a request, but the client times out. The order remains approved. Should the agent immediately submit another payment?

### 8. Critique a proposed improvement

An engineer allows a repair agent to alter the acceptance specification after three failures. The observed pass rate increases. Is that sufficient evidence of improvement?

### 9. Assess a matching version

A draft matches an order. Both version arguments supplied to the laboratory are `approval-7`. List what has been established and at least four further facts needed before relying on the order to make a payment.

### 10. Handle a failing repairer

A repairer raises an exception on its first call. What does the supplied laboratory do? What should a surrounding safety-conscious workflow do?

### 11. Interpret execution identities

A hypothetical execution record contains a `chapter_sha256` matching the exact chapter being read. Its `source_sha256` differs from the chapter hash but matches the extracted Python file. Is the difference between those two hashes a defect? What else must be checked before reporting the run’s result?
