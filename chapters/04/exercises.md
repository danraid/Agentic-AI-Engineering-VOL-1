# Chapter 4: Exercises

### 1. Change the attention values

Keep the worked query and keys, but set \(v_1=0\) and \(v_2=1\). Calculate the output.

### 2. Derive another threshold

A missed necessary retrieval costs 19 units and an unnecessary retrieval costs one. Find the threshold and explain equality.

### 3. Compare hypothetical policies

On 200 independently labelled cases, a gate has 15 false negatives and 20 false positives. Missed retrieval costs nine units and unnecessary retrieval costs one. Thirty cases truly require retrieval. Compare the gate with always skipping.

### 4. Diagnose a feature collision

Two requests have the same scalar feature, but adjudicated labels \(0\) and \(1\). Can a deterministic logistic head classify both correctly?

### 5. Compare data splits

**Hypothetical example.** Incident A has messages “Incident A: rollback required” and “Incident A: rollback confirmed”. A random split places the first in training and the second in test. Explain the leakage risk and propose a stronger design.

### 6. Review skipped requests

Only 100 skipped requests can be reviewed each week. Propose a sampling plan.

### 7. Inject a metadata failure

What should a test of a high-score request with a non-finite evidence age assert?

### 8. Reason about a permissions race

Permission is allowed when the policy decides, then revoked before the document store responds. What should happen, and what does the laboratory establish?

### 9. Compare positional mechanisms

A model uses \(h_i=e(x_i)+p_i\). Another uses content-only queries and keys with relative bias \(b_{i-j}\). Where does position enter each score?

### 10. Calculate cached-attention comparisons

A cached decoder processes a prefix of \(P\) tokens and makes \(n\) subsequent query steps. Under the convention used in the chapter, how many key comparisons per head are involved in those steps?
