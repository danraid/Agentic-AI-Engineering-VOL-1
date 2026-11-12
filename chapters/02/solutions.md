# Chapter 2: Worked solutions

### 1. Change the prior

**Suggested solution.** Entry has value

\[
10-110(0.05)=4.5>0.
\]

It is better than stopping and is admissible at the hypothetical \(0.05\) boundary. This comparison alone does not establish that entry is the best initial action: inspection must also be evaluated, including its cost and both report branches.

### 2. Change the loss

**Suggested solution.** Entry is worth

\[
10(1-p)-190p=10-200p.
\]

It is strictly better when \(p<0.05\); at \(p=0.05\) it ties with stopping. This is a utility threshold. A separate admissibility rule could be stricter or could use a different risk definition.

### 3. Distinguish a branch from a policy

**Suggested solution.** \(20/3\) is conditional on a clear report and excludes inspection cost. The blocked-report branch leads to stopping. Before cost, the complete policy is worth

\[
\frac{33}{50}\frac{20}{3}=\frac{22}{5}=4.4.
\]

With cost \(c\), its value is \(4.4-c\). Inspection is strictly better than stopping for \(c<4.4\), and ties at \(c=4.4\), assuming the same branch decisions.

### 4. Choose an architecture

**Suggested solution.** A deliberative planner can compare delivery sequences, but its computation and observations may not meet the obstacle-response deadline. A hybrid can place a prompt obstacle override alongside slower planning. It introduces an arbitration and interface burden: the override must have enforceable authority, and tests must cover events arriving between planning and command acceptance. The hybrid label alone does not establish independence or safety.

### 5. Extend the inspection contract

**Suggested solution.** After a valid decision, an authorised command could enter a pending state until accepted or rejected. Missing acknowledgement should trigger a defined escalation. A separate feedback state should record whether the expected physical result was observed; acknowledgement must not be treated as that observation.

A candidate invariant is that an accepted entry command has a valid unexpired decision and inactive interlock at acceptance. Test an emergency arriving after the planner’s check but before command acceptance. The laboratory ends at a decision result: it neither sends a command nor checks an interlock atomically at an actuator boundary.

### 6. Test correlated evidence

**Suggested solution.** Create a fixture in which the human report references the camera event identifier. Compare the belief produced from the camera report alone with the belief produced when the dependent report is added. The implementation must not multiply two likelihoods as independent merely because two messages arrived. Check that provenance is retained and that the result follows an explicit dependence model; if dependence is unknown, the specified fallback may be to stop.

### 7. Synthesis: specify a new policy

**Suggested solution.** Observations could include timestamped temperature readings, sensor health, vehicle identity and door status. Actions could include dispatch, request a new reading and hold the vehicle. A stakeholder-defined temperature constraint must be supplied externally; the exercise does not establish its value.

The belief update should distinguish a current reading from an old one and account for possible temperature change over time. Missing, stale, conflicting or unauthenticated evidence leads to hold and escalation, not an assumed safe temperature.

A hybrid could use a simple hold rule for invalid evidence and a deliberative component for delivery scheduling. Tests should include boundary readings under the supplied rule, stale and future timestamps, conflicting sensors, replayed messages, a failed refresh request and a dispatch acknowledgement that never arrives. Calibration, real transport conditions and physical refrigeration require separate validation.

### 8. Challenge the admissibility rule

**Suggested solution.**

1. **Prior drift:** the agent uses \(0.20\) when current conditions warrant a larger prior. Monitor and update the prior using justified evidence; monitoring can itself lag or miss an unrepresented change.
2. **Dependent reports:** two messages based on one image are multiplied as independent likelihoods. Record provenance and model dependence; provenance records do not guarantee that every shared cause is known.
3. **Omitted hazards:** the model covers pallets but not people or brake failures. Expand the hazard analysis and introduce suitable independent controls; an expanded model still requires validation and cannot be assumed complete.

In each case, satisfying a rule on a calculated posterior is not equivalent to establishing the real probability of harm.
