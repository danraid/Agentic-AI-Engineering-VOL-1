# Chapter 6: Worked solutions

### 1. Trace an uncertain write

**Suggested solution.** If the deduplication contract and retention window remain valid, a retry must contain the same key, target, resource and expected revision. A new key creates a different logical operation; changing arguments under the old key violates request binding. Authority must still permit dispatch. Otherwise reconcile or escalate.

### 2. Prove an invariant

**Suggested solution.**

\[
\Box\bigl(\operatorname{issue}(p)\Rightarrow
\operatorname{approved}(p)\bigr).
\]

Initially no write has been issued. Non-issuing transitions introduce no violation. The only issuing transition has `approved(p)` as a guard for the same \(p\), so it preserves the property. The proof assumes the implementation sends the proposal tested by the guard and approval remains valid at emission. A mutable proposal or delayed dispatch after expiry breaks those assumptions.

### 3. Analyse two controllers

**Suggested solution.** At most one succeeds against revision 0. The other conflicts. The contract does not determine which target is preferable or whether the loser may replan. Automatic retry at revision 1 could overwrite the winner, so ownership or conflict resolution is still needed.

If checking the revision and updating it are not atomic, both requests might pass their checks before either update. The at-most-one conclusion then does not follow.

### 4. Complete a state machine

**Suggested solution.** It lacks bounded retry and deadline rules, distinguishes neither uncertainty from known non-effect nor same-request retry from a new operation, and specifies no deduplication contract. It also needs an authorisation gate, an evidence-based verification step and an escalation path. A timeout should enter `UNCERTAIN`; a retry must preserve the request and key only while the relevant contract and authority remain valid.

### 5. Select a claim

**Suggested solution.** No. The read may support `OBSERVED_TARGET`, assuming the relevant resource and other policy conditions are satisfied. `OpEvidence` is false without a receipt. Another actor may have established the target, or it may already have been present. The controller should report what was observed without asserting that its own operation caused it.

### 6. Construct a crash counterexample

**Suggested solution.** The client sends key `k`. The service applies the effect, then crashes before recording `k`. The client receives no acknowledgement and retries `k`. After recovery, the service finds no deduplication record and applies the effect again. Persisting the key at the client was necessary for identifying the retry, but did not atomically bind the remote effect to the service’s record.

If the operation sets a value, the final value may still look correct while an ancillary notification occurs twice. An atomic service transaction covering the relevant effect and record, plus appropriate durability and retry semantics, excludes this particular crash window. It does not automatically prove end-to-end exactly-once processing across other services.

### 7. Distinguish stale matching evidence from linked evidence

**Suggested solution.** The replica’s matching value predates operation `k`; it cannot establish that the current value is 20 or that the read includes `k`. Its arrival after the receipt does not make the underlying observation fresh.

An authenticated receipt bound to `k` and revision 7, together with an acceptable authoritative observation of value 20 at revision 7, would satisfy the revision-link portion of the hypothetical contract. A later revision can also suffice if the service establishes that it includes revision 7 in the same resource history and the observation still shows 20. Authentication, provenance, freshness and any additional policy conditions remain necessary.

### 8. Extend the laboratory without overstating its guarantee

**Suggested solution.** First call `store.put("k", 20, 0)`, then assert that `store.put("k", 20, 1)` raises `KeyReuse` and that `store.effects` remains 1. The request tuple includes both target and expected revision, so the second call is not identical.

The test exercises the sequential in-memory stub’s request binding. It does not prove concurrent deduplication, crash atomicity, persistence or authentication. Those require additional implementation and tests at the service boundary.

### 9. Examine liveness assumptions

**Suggested solution.** No. The first call may never return, so the controller never consumes the remaining budget or enters escalation. The termination argument additionally requires calls to return or generate a timeout event within a finite bound, fair scheduling of enabled controller steps, bounded recovery cycles and an escalation transition that does not itself block indefinitely.

Even when those conditions hold, reaching `ESCALATE` is not proof of external failure or eventual human resolution.
