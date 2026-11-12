from dataclasses import dataclass
from fractions import Fraction as F

# Hypothetical parameters; none is a certified safety threshold.
PRIOR = F(1, 5)
SENSITIVITY = F(9, 10)     # P(blocked report | blocked)
SPECIFICITY = F(4, 5)      # P(clear report | clear)
INSPECTION_COST = F(1)
RISK_LIMIT = F(1, 20)
MAX_AGE = 5                # Time units in a common, assumed clock.


@dataclass(frozen=True)
class Context:
    prior: F
    belief_time: int
    now: int
    emergency: bool = False
    conflict: bool = False


def valid_probability(p):
    return isinstance(p, F) and F(0) <= p <= F(1)


def entry_value(p):
    if not valid_probability(p):
        raise ValueError("invalid probability")
    return 10 - 110 * p


def terminal_choice(p):
    """Choose between entry and stop; stop wins a utility tie."""
    value = entry_value(p)
    if p <= RISK_LIMIT and value > 0:
        return "enter", value
    return "stop", F(0)


def report_likelihoods(label):
    if label == "blocked":
        return SENSITIVITY, 1 - SPECIFICITY
    if label == "clear":
        return 1 - SENSITIVITY, SPECIFICITY
    raise ValueError("unknown report")


def update(prior, label):
    """Return posterior blockage probability and report probability."""
    if not valid_probability(prior):
        raise ValueError("invalid prior")
    likelihood_b, likelihood_c = report_likelihoods(label)
    joint_b = prior * likelihood_b
    joint_c = (1 - prior) * likelihood_c
    probability = joint_b + joint_c
    if probability == 0:
        raise ValueError("report impossible under model")
    return joint_b / probability, probability


def inspection_value(prior):
    """One inspection, then an admissible terminal choice."""
    if not valid_probability(prior):
        raise ValueError("invalid prior")
    total = -INSPECTION_COST
    details = []
    for label in ("blocked", "clear"):
        likelihood_b, likelihood_c = report_likelihoods(label)
        probability = (
            prior * likelihood_b + (1 - prior) * likelihood_c
        )
        if probability == 0:
            continue
        posterior, probability = update(prior, label)
        action, value = terminal_choice(posterior)
        total += probability * value
        details.append((label, probability, posterior, action, value))
    return total, details


def guard_reason(context):
    if context.emergency:
        return "emergency"
    if context.conflict:
        return "conflicting reports"
    if not valid_probability(context.prior):
        return "invalid belief"
    age = context.now - context.belief_time
    if age < 0 or age > MAX_AGE:
        return "stale or future-dated belief"
    return None


def decide(context, report=None):
    """
    With no report, choose stop, enter or inspect.
    With a report, update once and choose stop or enter.

    This function alone does not establish that a request existed.
    """
    reason = guard_reason(context)
    if reason is not None:
        return "stop", reason

    if report is not None:
        try:
            posterior, _ = update(context.prior, report)
        except ValueError:
            return "stop", "invalid report"
        action, _ = terminal_choice(posterior)
        return action, f"posterior={posterior}"

    action, terminal_value = terminal_choice(context.prior)
    inspect_value, _ = inspection_value(context.prior)
    if inspect_value > terminal_value:
        return "inspect", f"expected utility={inspect_value}"
    return action, f"expected utility={terminal_value}"


class InspectionEpisode:
    """
    Sequential, in-memory illustration of an inspection protocol.

    Source identity is a caller-supplied string, not authentication.
    A request expires at its deadline: valid arrival requires now < expiry.
    """

    def __init__(self, vehicle, aisle, allowed_sources):
        self.vehicle = vehicle
        self.aisle = aisle
        self.allowed_sources = set(allowed_sources)
        self.used_ids = set()
        self.pending = None

    def start(self, request_id, context, expiry):
        if self.pending is not None:
            return False, "request already pending"
        if not isinstance(request_id, str) or not request_id:
            return False, "invalid request id"
        if request_id in self.used_ids:
            return False, "reused request id"
        if expiry <= context.now:
            return False, "invalid expiry"

        action, reason = decide(context)
        if action != "inspect":
            return False, f"inspection not selected: {reason}"

        self.used_ids.add(request_id)
        self.pending = {
            "id": request_id,
            "prior": context.prior,
            "belief_time": context.belief_time,
            "issued": context.now,
            "expiry": expiry,
        }
        return True, "waiting"

    def receive(self, request_id, vehicle, aisle, source, label,
                event_time, now, emergency=False, conflict=False):
        if self.pending is None:
            return {"status": "rejected_closed", "action": None,
                    "reason": "no pending request", "pending": False}

        request = self.pending
        if emergency or conflict:
            self.pending = None
            return {"status": "closed", "action": "stop",
                    "reason": "emergency or conflict", "pending": False}

        # Expiry closes the pending episode, even if the reply is unmatched.
        if now >= request["expiry"]:
            self.pending = None
            return {"status": "closed", "action": "stop",
                    "reason": "request expired", "pending": False}

        if request_id != request["id"]:
            return {"status": "rejected_pending", "action": None,
                    "reason": "unmatched request", "pending": True}
        if vehicle != self.vehicle or aisle != self.aisle:
            return {"status": "rejected_pending", "action": None,
                    "reason": "wrong vehicle or aisle", "pending": True}
        if source not in self.allowed_sources:
            return {"status": "rejected_pending", "action": None,
                    "reason": "source not allowed", "pending": True}
        if label not in ("clear", "blocked"):
            return {"status": "rejected_pending", "action": None,
                    "reason": "invalid report", "pending": True}

        # Require an observation after issue, no later than receipt,
        # and no older than MAX_AGE. Clock trust is an external assumption.
        if (event_time < request["issued"] or event_time > now
                or now - event_time > MAX_AGE):
            return {"status": "rejected_pending", "action": None,
                    "reason": "invalid report time", "pending": True}

        context = Context(
            request["prior"], request["belief_time"], now
        )
        action, explanation = decide(context, label)
        # A correctly correlated report closes the request even if its
        # policy decision is stop; physical effects are not implemented.
        self.pending = None
        return {"status": "accepted", "action": action,
                "reason": explanation, "pending": False}

    def expire(self, now):
        # A local timeout requests a stop decision; it does not actuate brakes.
        if self.pending is None:
            return {"status": "no_change", "action": None,
                    "reason": "no pending request", "pending": False}
        if now >= self.pending["expiry"]:
            self.pending = None
            return {"status": "closed", "action": "stop",
                    "reason": "request expired", "pending": False}
        return {"status": "no_change", "action": None,
                "reason": "not expired", "pending": True}


def run_tests():
    base = Context(PRIOR, belief_time=100, now=100)
    value, details = inspection_value(PRIOR)

    assert entry_value(PRIOR) == -12
    assert value == F(17, 5)
    assert details == [
        ("blocked", F(17, 50), F(9, 17), "stop", F(0)),
        ("clear", F(33, 50), F(1, 33), "enter", F(20, 3)),
    ]
    assert decide(base)[0] == "inspect"
    assert decide(base, "clear")[0] == "enter"
    assert decide(base, "blocked")[0] == "stop"

    # Exact posterior-rule boundary and boundary priors.
    assert terminal_choice(F(1, 20))[0] == "enter"
    assert terminal_choice(F(5001, 100000))[0] == "stop"
    assert inspection_value(F(0))[0] == 9
    assert inspection_value(F(1))[0] == -1
    assert decide(Context(F(0), 100, 100))[0] == "enter"
    assert decide(Context(F(1), 100, 100))[0] == "stop"

    # Decision guards.
    assert decide(Context(PRIOR, 94, 100), "clear")[0] == "stop"
    assert decide(Context(PRIOR, 101, 100))[0] == "stop"
    assert decide(Context(PRIOR, 100, 100, conflict=True),
                  "clear")[0] == "stop"
    assert decide(Context(F(1, 100), 100, 100, emergency=True)
                  )[0] == "stop"
    assert decide(Context(F(3, 2), 100, 100))[0] == "stop"
    assert decide(base, "unknown")[0] == "stop"

    # Correlation, context and source checks leave a valid request pending.
    episode = InspectionEpisode("v1", "a1", {"inspector"})
    assert episode.start("r1", base, 105) == (True, "waiting")
    assert episode.receive("wrong", "v1", "a1", "inspector",
                           "clear", 101, 101)["reason"] == "unmatched request"
    assert episode.receive("r1", "v2", "a1", "inspector",
                           "clear", 101, 101)["reason"] == "wrong vehicle or aisle"
    assert episode.receive("r1", "v1", "a1", "other",
                           "clear", 101, 101)["reason"] == "source not allowed"
    assert episode.receive("r1", "v1", "a1", "inspector",
                           "clear", 102, 101)["reason"] == "invalid report time"

    result = episode.receive("r1", "v1", "a1", "inspector",
                             "clear", 101, 101)
    assert result == {"status": "accepted", "action": "enter",
                      "reason": "posterior=1/33", "pending": False}
    assert episode.receive("r1", "v1", "a1", "inspector",
                           "clear", 101, 101)["reason"] == "no pending request"
    assert episode.start("r1", base, 105)[1] == "reused request id"

    # Invalid replies do not generate a stop decision or close the request.
    invalid = InspectionEpisode("v1", "a1", {"inspector"})
    assert invalid.start("r9", base, 105)[0]
    rejected = invalid.receive("bad", "v1", "a1", "inspector", "clear", 101, 101)
    assert rejected["status"] == "rejected_pending"
    assert rejected["action"] is None and rejected["pending"]
    assert invalid.pending["id"] == "r9"
    assert invalid.receive("r9", "v1", "a1", "inspector",
                           "blocked", 101, 101)["status"] == "accepted"
    assert invalid.pending is None

    # Deadline is exclusive: arrival exactly at expiry is rejected.
    late = InspectionEpisode("v1", "a1", {"inspector"})
    assert late.start("r2", base, 105)[0]
    assert late.receive("r2", "v1", "a1", "inspector",
                        "clear", 104, 105)["reason"] == "request expired"
    assert late.expire(106)["status"] == "no_change"
    # Timer expiry and receive-side expiry agree on the stop-request contract.
    timed = InspectionEpisode("v1", "a1", {"inspector"})
    assert timed.start("r7", base, 105)[0]
    timeout = timed.expire(105)
    assert timeout == {"status": "closed", "action": "stop",
                       "reason": "request expired", "pending": False}
    assert timed.pending is None

    # Emergency closes the episode; an old response cannot resume it.
    urgent = InspectionEpisode("v1", "a1", {"inspector"})
    assert urgent.start("r3", base, 105)[0]
    assert urgent.receive("r3", "v1", "a1", "inspector",
                          "clear", 101, 101, emergency=True)["action"] == "stop"
    assert urgent.receive("r3", "v1", "a1", "inspector",
                          "clear", 101, 101)["reason"] == "no pending request"

    print("All deterministic tests passed.")
    print("Immediate entry:", entry_value(PRIOR))
    print("Immediate stop: 0")
    for label, prob, posterior, action, continuation in details:
        print(
            f"{label}: P(report)={prob}, P(blocked|report)={posterior}, "
            f"action={action}, continuation={continuation}"
        )
    print("Inspection:", value)
    print("Initial decision:", decide(base))
    print("Accepted correlated clear report:", result)


if __name__ == "__main__":
    run_tests()
