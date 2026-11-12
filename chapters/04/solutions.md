# Chapter 4: Worked solutions

### 1. Change the attention values

**Suggested solution.** The weights remain approximately \(0.670\) and \(0.330\), because queries and keys determine them. The output becomes approximately \(0.330\). Values affect what is mixed, not the weights in this calculation.

### 2. Derive another threshold

**Suggested solution.** Retrieval has lower simplified expected cost when the relevant probability exceeds

\[
\frac{1}{19+1}=0.05.
\]

At equality the costs are equal. A deterministic policy must document whether it retrieves, skips or applies another tie rule. An estimated score substitutes for the unknown population probability only as an approximation, and permission remains a separate constraint.

### 3. Compare hypothetical policies

**Suggested solution.** The gate costs \(15(9)+20(1)=155\). Always skipping costs \(30(9)=270\). This comparison assumes the same fixed costs and complete, reliable labels. It does not establish calibration, answer adequacy or authorisation.

### 4. Diagnose a feature collision

**Suggested solution.** No. It gives both the same probability and therefore the same thresholded prediction. Exactly one label is matched. Investigate whether a missing feature distinguishes the requests, whether the representation discarded relevant information, or whether the labels require an ambiguity category.

### 5. Compare data splits

**Suggested solution.** The shared identifier and incident-specific wording make the test message dependent on training information. A model may recognise incident A rather than generalise to a new incident. Assign all messages from A to one partition, do the same for every incident, and preferably reserve later incidents for a temporal test. Select the threshold on validation data before evaluating the fixed design on test data.

### 6. Review skipped requests

**Suggested solution.** Predefine probability bands and consequential request categories; retain a random component in every eligible group. Record inclusion probabilities and have reviewers assess necessity without seeing the gate’s score where practical. Report sample sizes, weighted estimates and uncertainty. If a group is too small or inaccessible, state the limitation rather than claiming a reliable rate.

### 7. Inject a metadata failure

**Suggested solution.** Call `simulate_request(0.9, True, float("nan"))`. Assert that the reason is `stale_or_invalid_metadata` and that `("tool_call", "retrieve")` is absent from the trace. Both checks appear in the laboratory’s invalid-input test. A corresponding low-score test is also important: invalid metadata must not be hidden by a skip decision.

### 8. Reason about a permissions race

**Suggested solution.** The resource service or enforcement proxy should check current permission at access time and deny the read. The assistant should follow a safe failure or review path, not retry with broader credentials. The laboratory models this sequence with an in-memory service and checks that no content is returned. A real integration test must additionally exercise actual identity, permission propagation and service behaviour.

### 9. Compare positional mechanisms

**Suggested solution.** In the first, \(p_i\) and \(p_j\) enter through the query and key projections, respectively; the value projection can also contain \(p_j\). In the second, the relative bias is added directly to the score. Neither mechanism alone proves that the model will handle positions or distances outside those supported during training.

### 10. Calculate cached-attention comparisons

**Suggested solution.** The count is

\[
\sum_{i=1}^{n}(P+i)=nP+\frac{n(n+1)}2.
\]

This excludes prefix processing and is a count of attention comparisons, not total inference time. Projections, feed-forward computation, vocabulary scoring, cache movement and implementation details also matter.
