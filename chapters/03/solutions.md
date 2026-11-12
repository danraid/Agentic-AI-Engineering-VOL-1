# Chapter 3: Worked solutions

### 1. Final-action threshold

**Suggested solution.** Running has value \(4-16p\). At \(p=0.25\), that is \(0\), so run rather than repair for \(-2\). At \(p=0.375\), both actions have value \(-2\); either is optimal, although the laboratory chooses repair by convention. At \(p=0.5\), running is worth \(-4\), so repair is better.

### 2. Diagnostic cost

**Suggested solution.** Before diagnostic cost, expected continuation value is

\[
0.5(-2)+0.5(0.8)=-0.6.
\]

The diagnostic value is \(-0.6-d\). It exceeds immediate repair’s \(-2\) when \(d<1.4\). At \(d=1.4\), they tie. This assumes diagnosis does not change the state or cause delay-related harm.

### 3. Compare parameterisations

**Suggested solution.** The threshold remains \(0.375\), because it follows from unchanged final-action rewards. Under false-positive probability \(0.2\), posteriors after positive and negative results are \(0.8\) and \(0.2\), and the one-diagnostic value is \(-1.1\). Under probability \(0.1\), they are \(8/9\) and \(2/11\), and value is \(-0.8\). In both cases the agent repairs after a positive result and runs after a negative result.

### 4. An impossible observation

**Suggested solution.** The modelled positive-result probability is zero, so the denominator is zero and the posterior is undefined. Report the contradiction, retain raw evidence and use a specified fallback or escalation. Investigate the prior, diagnostic model, state vocabulary and intake. Substituting a posterior without an explicit revised model would conceal the problem.

### 5. Local cap versus trajectory constraint

**Suggested solution.** The first is a local rule based on conditional belief about current fault. It does not define outage or its relation to fault. The second is a probability over entire ten-action trajectories, including policy, transitions, observations and the event definition. Repeated exposure and state changes can affect that probability. The local threshold alone does not establish the trajectory constraint.

### 6. Correlated diagnostics

**Suggested solution.** One positive result gives \(4/7\). Applying the likelihood again gives \(16/19\), but treats the second result as independent evidence conditional on service state. A copied or shared stale log does not provide such evidence. Deduplicate the underlying measurement and, where distinct results share a failure cause, introduce a hidden log-freshness or sensor-health variable. Belief must then cover both service health and that shared cause.

### 7. A diagnostic that takes time

**Suggested solution.**

\[
p^-=(1-p)T_{HF}+pT_{FF}.
\]

Apply the result likelihood to \(p^-\), not the old \(p\). The code would need transition parameters and tests for identity transitions, deterioration and impossible observations. The model should also account for costs or harm during delay. A report measuring an earlier state requires different timing.

### 8. Replay and recovery

**Suggested solution.** The guard compares message identifiers, not stable identities of underlying measurements. Bind a stable measurement identity to source, target and measurement time, and authenticate it. Commit the belief update and consumption record atomically, or use an equivalent recoverable protocol. Deduplication alone does not model correlation between genuinely distinct measurements.

### 9. Optional diagnostics and monotonicity

**Suggested solution.** Every policy feasible with \(n\) opportunities remains feasible with \(n+1\): the agent can decline the extra opportunity. The maximum over the larger policy set cannot be lower. The argument fails if the extra diagnostic is compulsory or changes the environment merely by being available. It does not imply that every permitted diagnostic should be used.

### 10. Scope of a formal result

**Suggested solution.** Is the deployed controller exactly the checked controller? Does the formal property express the operational requirement, including horizon and event definition? Do transitions, observations and environmental assumptions cover the intended operating conditions? The result concerns the checked artefact and model, not the environment unconditionally.

### 11. Asynchronous commands and expiring credentials

**Suggested solution.** Represent at least whether a command is pending, its target and relevant status or age, and the credential’s validity and expiry. Depending on the interface, the model may also need possible completion outcomes, timeout state and whether retries are permitted. Remaining time and budget must remain explicit. Without these variables, identical fault beliefs can lead to different transition probabilities and admissible actions, so health belief alone is not sufficient.

### 12. Audit a proposed value

**Suggested solution.** Since \(111/125=0.888<0.94\), the proposed value violates optional-diagnostic monotonicity: a controller with two opportunities can follow the one-opportunity policy. For the direct calculation, the next result is positive with probability \(8/25\), producing belief \(1/2\), or negative with probability \(17/25\), producing belief \(1/17\). The respective one-opportunity values are \(-11/10\) and \(52/17\). Therefore,

\[
V_2(1/5)
=-\frac12+\frac8{25}\left(-\frac{11}{10}\right)
+\frac{17}{25}\left(\frac{52}{17}\right)
=\frac{307}{250}.
\]

An invariant is an efficient first check, but the branch calculation is still needed to establish the correct value.

### 13. Evidence discipline

**Suggested solution.** No. The packet permits ABSTRACT-tier material only as broad context; it does not support a numerical, empirical or paper-specific claim in the chapter. The author could omit the figure and discuss trajectory selection as a general design possibility, clearly distinguishing that discussion from a reported result. Alternatively, the author could seek an appropriately checked FULLTEXT excerpt and revise the claim only within the scope of that evidence. A model-generated summary is not a substitute for a checked excerpt.

### 14. Deterministic and stochastic policy trees

**Suggested solution.** If the two policies have values \(v_1\) and \(v_2\), choosing the first with probability \(q\) gives \(qv_1+(1-q)v_2\), which cannot exceed \(\max(v_1,v_2)\). Applying the same reasoning to choices at each finite decision point shows that deterministic contingent choices suffice for the stated expected-reward problem. It does not cover every objective: constraints or other criteria can make a randomised policy relevant.
