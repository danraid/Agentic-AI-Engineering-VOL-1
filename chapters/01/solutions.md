# Chapter 1: Worked solutions

**1.** Retrieval costs 1, leaving 1. Drafting costs 2, so the draft charge is blocked. The result is `budget`, spend is 1, the job remains `retrieved`, and no delivery exists. The supplied approval does not bypass the budget check.

**2.** A Boolean states only that some approval occurred; it does not identify what was approved. Store the reviewer identity, action, recipient, content digest, timestamp and expiry. Immediately before delivery, compare the current action and content with that record. If they differ or approval has expired, return the job to review. The digest must be computed over a canonical representation so that both parties agree on the bytes being approved.

**3.** In the laboratory, repeated pending calls do not incur another charge. If each real submission is billable, that undercounts spend. Before **each actual provider submission**, atomically reserve or charge its attempt cost and record a unique attempt number under the stable action key. Reconciliation queries may have separate costs. A retry should not occur when the remaining budget cannot cover its possible charge; the policy must also define how provider billing is reconciled with reservations.

**4.** Mark the action uncertain, preserve the original payload and evidence of submission, and escalate to a human or an agreed reconciliation process. Do not automatically send a second message if duplication is unacceptable. This sacrifices prompt completion to reduce duplicate risk; it still cannot prove whether the first message arrived. The recipient or another independent record may eventually help establish the outcome.

**5.** Both workers can pass a non-atomic “remaining budget” check, leading to total charges of 6 against 3 available. Use a shared durable transaction or equivalent atomic reservation that checks and updates the budget in one indivisible operation. One reservation succeeds; the other is refused or waits. Tests should force the interleaving, not merely run workers sequentially.

**6.** By Bayes' rule, the positive reading probability is \(0.2\times0.8+0.8\times0.1=0.24\). The shortage posterior is \(0.16/0.24=2/3\). For a negative reading, \(P(\text{negative})=0.2\times0.2+0.8\times0.9=0.76\), so the shortage posterior is \(0.04/0.76=1/19\). These figures are assumptions for practice, not measured detector performance.

**7.** The first policy violates the \(0.005\) chance constraint because \(0.02>0.005\), even if its expected price is attractive. The second policy might satisfy the constraint, but that requires testing that approval cannot be forged, bypassed, reused for altered content, or invalidated by concurrency and tool retries. A deterministic gate is a proposed design control, not empirical proof of zero risk.

**8.** Put routine threshold-and-approval purchases in a fixed workflow. Use a model-assisted agent for ambiguous complaints, restricted to suggesting actions and requesting missing facts. A multi-agent arrangement is only justified if independent specialised checks demonstrably improve separation, reliability or throughput. Keep money transfers behind explicit external authorisation, replay protection, bounded delegation and audit. Neither a multi-agent design nor persuasive model output grants authority.
