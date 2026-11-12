# Chapter 2: Exercises

### 1. Change the prior

**Exercise.** With the original utilities, let \(P(B)=0.05\). Is immediate entry better than stopping? Does that answer alone establish that entry is the best initial action?

### 2. Change the loss

**Exercise.** If blocked entry has utility \(-190\), clear entry remains \(+10\), and stopping remains \(0\), for which blockage probabilities is entry strictly better than stopping?

### 3. Distinguish a branch from a policy

**Exercise.** A colleague says inspection is worth \(20/3\), because that is the value after a clear report. Correct the statement and find the maximum inspection cost for which inspection is strictly better than stopping at the original prior.

### 4. Choose an architecture

**Exercise.** A vehicle must react promptly to an obstacle but also schedule deliveries around temporary aisle closures. Compare a purely deliberative planner with a hybrid design. Identify one assurance burden introduced by the hybrid.

### 5. Extend the inspection contract

**Exercise.** Extend the laboratory design to cover command acknowledgement and physical feedback. Give an invariant and one race to test. Explain why the existing `InspectionEpisode` does not already establish the invariant.

### 6. Test correlated evidence

**Exercise.** A human reports “clear” after viewing the same camera image used by the automated inspection. Propose a test against naive double counting.

### 7. Synthesis: specify a new policy

**Exercise.** Design a policy for a hypothetical refrigerated-delivery agent deciding whether to dispatch a vehicle when temperature data may be stale. Specify observations, actions, constraints, belief updates, fallback behaviour, an architecture choice and test evidence. Do not invent a certified temperature limit.

### 8. Challenge the admissibility rule

**Exercise.** Give three ways in which the warehouse agent could satisfy its calculated posterior rule while the calculation fails to support the intended safety claim. For each, identify a possible mitigation and its limitation.
