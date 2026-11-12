# Chapter 8: Worked solutions

### 1. Identify the failed property

**Suggested solution.** It should include `MISMATCH_TOTAL`. The calculation is \(2,500+1,200=3,700\) pence. This establishes a total relative to the supplied order and the simplified rule. Treating it as the correct business total additionally assumes that the supplied order is authoritative and applicable; arithmetic does not establish that assumption.

### 2. Separate properties

**Suggested solution.** Statement 1 is a safety property; 2 is liveness; 3 is an evidence property; and 4 is an authorisation property. They interact: if authenticity cannot be established, the gate may be unable to establish the precondition needed to preserve safety.

### 3. Analyse the budget

**Suggested solution.** The controller checks the wrong draft, records `MISMATCH_TOTAL`, then records `budget_exhausted` and escalates. A correct initial draft passes. The budget limits repairs, not the initial check. Neither outcome establishes that the supplied order is authoritative.

### 4. Analyse correlated checks

**Suggested solution.** No. Multiplication requires conditional independence of the misses on incorrect candidates. If both always miss the same 10% of cases, the combined miss rate remains 10%. Shared evidence or specifications can produce this dependence.

### 5. Follow a two-state loop

**Suggested solution.** The controller checks \(A\), repairs to \(B\), checks \(B\), then repairs back to \(A\). Before checking \(A\) again, it finds the full canonical state in `seen` and escalates. The short trace fingerprint is not used as the equality test. This reasoning assumes that each repairer call returns.

### 6. Specify rounding

**Suggested solution.** Line-level rounding gives \(1+1=2\) pence. Invoice-level rounding gives 10% of 10 pence, or 1 penny. The specification must select a policy; the tax rate alone is insufficient.

### 7. Respond to a timeout

**Suggested solution.** No. The first request may already have succeeded. Mark the external outcome unknown, preserve the original request and idempotency key, and reconcile with the provider or ledger. Retry only under the provider’s documented semantics and the applicable authorisation policy.

### 8. Critique a proposed improvement

**Suggested solution.** No. The pass rate may increase because the system has weakened the requirement. Evaluate against an independently controlled specification, retain adversarial and stale-evidence cases, and measure unsafe passes as well as completion. Changes to the specification need separate approval.

### 9. Assess a matching version

**Suggested solution.** The version strings are non-empty and equal; the draft also satisfies the laboratory’s structural and arithmetic comparisons against the supplied order. The strings do not authenticate one another. Further checks could establish the issuer’s identity and authority, integrity of the record, approval and expiry or revocation status, applicability to the tenant and transaction, and binding to the proposed beneficiary and amount. A separate action-authorisation decision is still needed. A laboratory `PASS` is conditional on the supplied record’s authority; it is not evidence that the record is authoritative.

### 10. Handle a failing repairer

**Suggested solution.** The exception propagates; `run` does not return a disposition or its accumulated trace. The exception test specifies this behaviour. A surrounding workflow should treat the outcome as failure or uncertainty, prevent the side effect and escalate according to policy. It should also consider how to retain diagnostics safely. A timeout and resource-isolated execution boundary are separately needed for a repairer that hangs or consumes excessive resources; catching an ordinary exception alone is insufficient.

### 11. Interpret execution identities

**Suggested solution.** The difference is not a defect. The chapter and extracted script are different byte sequences and have different identities. Check that the record identifies the intended run, that the script was extracted according to the relevant procedure, and that the command, environment, return code and reported test outcome support the proposed statement. The source-packet hash identifies a third artefact and is not expected to match either hash. A matching execution record still does not establish that the order is authoritative or that the system is safe for production use.
