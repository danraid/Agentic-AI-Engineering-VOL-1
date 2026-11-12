# Chapter 7: Worked solutions

### 6. Design recovery from an unknown outcome

**Suggested solution.** Record the request and a unique idempotency key before transmission. On timeout, mark the outcome unknown, query the target for operation status and escalate if status cannot be established within the permitted window. Retry only under a documented protocol that prevents a duplicate restart. This requires the target to recognise and durably retain the key, or an equivalent reliable reconciliation mechanism. Generating a key locally is insufficient.

### 7. Validate the model, not just the code

**Suggested solution.** Define the population and time period to which the prior applies; obtain labelled examples suitable for estimating sensor false-clear and false-alarm rates; assess source dependence and drift; and examine uncertainty in all estimates. Review the cap against the consequences of harm, applicable requirements and available fallback actions. Test decisions across plausible parameter ranges, especially near the boundary.

An obstacle is selective observation: outcomes after authorised restarts may not reveal what would have happened after deferred actions. Rare or delayed harms can also make calibration difficult. Passing the laboratory tests establishes none of these operational assumptions.

### 8. Explain a planning approximation

**Suggested solution.** It has given the surrogate planner better future information than the real agent has. This may make an action appear attractive because the surrogate expects to correct its course with knowledge it will not actually receive. The approximation should be labelled and evaluated against the original observation process. More generally, extra-information approximations must not be mistaken for actual sensor capability; the region-observable modelling idea in [S03] illustrates why the surrogate and original problem must be kept distinct.
