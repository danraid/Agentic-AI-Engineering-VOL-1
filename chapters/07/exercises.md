# Chapter 7: Exercises

### 1. Change the loss threshold

**Exercise.** Replace the danger utility \(-12\) with \(-32\), retaining safe utility \(8\) and deferral utility \(0\). At what danger probability is restart indifferent to deferral?

**Solution.** Restart has expected utility

\[
8(1-p)-32p=8-40p.
\]

It equals zero at \(p=0.2\). At the original prior \(0.3\), deferral is preferable without further information. A separate risk cap could make the authorised threshold lower still.

### 2. Name the values and baselines

**Exercise.** Under the original unconstrained model, identify the gross policy value, net policy value, gross value of information and net value of information at inspection cost \(1\). What is the break-even cost? Then repeat the break-even comparison when the \(0.1\) cap forbids immediate restart.

**Solution.** Gross policy value is \(3.76\), and net policy value is \(3.76-1=2.76\). Against immediate restart worth \(2\), gross value of information is \(1.76\) and net value of information is \(0.76\). The unconstrained break-even cost is \(1.76\).

With the cap, immediate deferral is the authorised baseline, worth zero. The fixed inspection policy breaks even against it at cost \(3.76\), assuming its clear branch remains authorised and there are no other costs.

### 3. Modify a source-correlation model

**Exercise.** Two reports \(C_1,C_2\) each have the original marginal clear likelihoods: \(P(C_i\mid D)=0.2\) and \(P(C_i\mid S)=0.8\). Instead of conditional independence, suppose

\[
P(C_1,C_2\mid D)=0.12,\qquad
P(C_1,C_2\mid S)=0.70.
\]

Calculate the posterior after two clear reports. Explain which assumption changed and whether the marginal likelihoods alone determine the answer.

**Solution.** Bayes’ rule using the *joint* likelihood gives

\[
P(D\mid C_1,C_2)
=
\frac{0.3(0.12)}
{0.3(0.12)+0.7(0.70)}
=
\frac{18}{263}
\approx0.0684.
\]

The independence assumption was replaced by a correlated joint observation model. The marginals alone do not determine the joint probabilities: reports can share causes or be partially duplicated. The result lies between the independent calculation, approximately \(0.0261\), and the exact-copy calculation, approximately \(0.0968\). Those comparisons apply to these particular hypothetical joint models, not to every possible dependence structure.

### 4. Test the freshness boundary

**Exercise.** Modify the laboratory so that evidence exactly 30 seconds old is rejected. Which comparison and test must change?

**Solution.** Replace `age > MAX_AGE_SECONDS` with `age >= MAX_AGE_SECONDS`. Change `test_freshness_boundary` to expect `DEFER`. The 40-second stale injection should still pass. This is an operational policy change, not a consequence of Bayesian updating.

### 5. Propagate belief to execution

**Exercise.** Suppose danger can arise after a clear inspection. Let \(q\) be the probability of changing from safe to dangerous before execution, and assume a dangerous state remains dangerous. Derive the execution-time danger probability and find the largest \(q\) that permits restart under the \(0.1\) cap after the nominal clear result.

**Solution.** If the post-inspection belief is \(p'\),

\[
p_{\text{exec}}=p'+(1-p')q.
\]

With \(p'=3/31\), require

\[
\frac{3}{31}+\frac{28}{31}q\leq\frac{1}{10}.
\]

Hence

\[
q\leq\frac{1}{280}\approx0.00357.
\]

The gate must compare the execution-time belief with the cap. The result assumes the stated transition applies over the interval and that no other event changes the state.

### 6. Design recovery from an unknown outcome

**Exercise.** An executor sends a restart request but receives no response. Give a recovery protocol and one assumption it requires.

### 7. Validate the model, not just the code

**Exercise.** Propose checks for the prior, observation likelihoods and risk cap before applying the hypothetical design to a real service. Explain one obstacle to interpreting observed outcomes.

### 8. Explain a planning approximation

**Exercise.** A planner assumes that after its next action the true state will be revealed, although the real service will still produce noisy observations. What simplification has it made, and what decision error might follow?
