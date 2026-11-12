# Chapter 1: Exercises

Work each exercise under the laboratory’s stated assumptions. Changes to costs, fault behaviour or approval rules are hypothetical.

1. **Budget boundary.** What happens when a new valid case is run with a budget of 2 and approval already supplied? How much has been spent?
2. **Approval binding.** Suppose an operator approves a draft, after which another component changes its text before delivery. Why is a Boolean approval insufficient? Propose a record that would prevent this change from being silently authorised.
3. **Retry accounting.** A delivery costs 3 units per attempt, including unsuccessful attempts. The current code charges once when entering `pending`. Explain why this is unsuitable for a provider with per-attempt billing and propose an accounting rule.
4. **Uncertain external delivery.** A provider offers neither idempotency keys nor a reliable status lookup. The connection fails after submission. Design a response that avoids claiming an exactly-once guarantee, and state the trade-off.
5. **Concurrent budget.** Two workers each observe a remaining budget of 3 and each try to deliver a different message costing 3. Describe the race and an invariant-preserving remedy.

6. **Recalculate a posterior.** Consider a new hypothetical stock problem with prior probability of shortage 0.20, a positive detector reading with probability 0.80 given shortage, and false-positive probability 0.10 given adequate stock. Calculate the posterior shortage probability after a positive and after a negative result.
7. **Chance constraint versus expected cost.** One proposed purchasing policy has an assumed probability 0.02 of ordering without proper authorisation; the operational requirement is at most 0.005. A second policy is more expensive but has a verified deterministic approval gate. Which policy is feasible and which facts would you need to validate the gate?
8. **Architecture selection.** A team handles deterministic reorder requests, ambiguous natural-language supplier complaints, and irreversible transfer authorisations. Allocate responsibilities among a fixed workflow, one model-assisted agent, and an optional multi-agent system. Justify the placement of the authority boundary.
