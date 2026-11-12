# Chapter 3: Exercises

### 1. Final-action threshold

**Exercise.** With the main reward table and no diagnostic, find the best action at \(p=0.25\), \(p=0.375\) and \(p=0.5\).

### 2. Diagnostic cost

**Exercise.** At \(p=0.5\), keep the main likelihoods but replace diagnostic cost by \(d\). For which non-negative costs is one diagnostic strictly better than immediate repair?

### 3. Compare parameterisations

**Exercise.** Starting from \(p=0.5\), compare the main diagnostic with the sensitivity case in which only false-positive probability changes from \(0.2\) to \(0.1\). Does the final-action threshold change?

### 4. An impossible observation

**Exercise.** A perfect diagnostic has sensitivity \(1\) and false-positive probability \(0\). Current belief assigns probability zero to fault, but a positive result arrives. What does Bayes’ formula return, and what should the implementation do?

### 5. Local cap versus trajectory constraint

**Exercise.** Why is “run only when \(p\leq0.4\)” not the same statement as “the probability of any outage during the next ten actions is at most \(0.4\)”?

### 6. Correlated diagnostics

**Exercise.** Two positive messages are generated from the same stale log. The agent starts at \(p=0.25\). Why is applying the main likelihood twice inappropriate, and how might the model change?

### 7. A diagnostic that takes time

**Exercise.** A healthy service can become faulty during diagnosis. Let \(T_{HF}\) be the probability that healthy becomes faulty over the interval, and \(T_{FF}\) the probability that faulty remains faulty. Derive the predicted fault belief before conditioning on a result measured at the interval’s end.

### 8. Replay and recovery

**Exercise.** A diagnostic service retransmits an old measurement with a new message identifier. Why does the laboratory guard fail? What is needed to survive a crash between belief update and consumption recording?

### 9. Optional diagnostics and monotonicity

**Exercise.** Why can optimal value with at most \(n+1\) diagnostics not be lower than value with at most \(n\), even when diagnostics have positive cost?

### 10. Scope of a formal result

**Exercise.** A finite-state controller passes a formal model check. Give three questions to ask before interpreting the result operationally.

### 11. Asynchronous commands and expiring credentials

**Exercise.** Two histories have the same current fault belief. In one, a repair is awaiting acknowledgement and its credential expires shortly; in the other, no repair is pending and authority remains valid. What must be added to the state or decision context?

### 12. Audit a proposed value

**Exercise.** A proposed calculation asserts \(V_1(1/5)=0.94\) and \(V_2(1/5)=111/125\) for the optional-diagnostic model. Identify the inconsistency without calculating every policy branch. Then compute the correct \(V_2(1/5)\).

### 13. Evidence discipline

**Exercise.** A proposed chapter sentence reports a numerical improvement from [S20], for which the supplied packet contains an ABSTRACT but no checked FULLTEXT evidence. Is that an acceptable paper-specific empirical claim under this chapter’s evidence rule? What could the author do instead?

### 14. Deterministic and stochastic policy trees

**Exercise.** Explain why allowing a random choice between two finite-horizon contingent policies does not improve an unconstrained expected-reward optimum. Does this prove that randomisation is useless in every decision problem?
