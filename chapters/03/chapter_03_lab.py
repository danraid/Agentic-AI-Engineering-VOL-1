"""Hypothetical finite-horizon diagnostic laboratory.

All decision calculations use exact Fraction arithmetic.
This teaching model is not a production maintenance controller.
"""

from fractions import Fraction as F
from functools import lru_cache

SENSITIVITY = F(4, 5)
FALSE_POSITIVE = F(1, 5)
DIAGNOSTIC_COST = F(1, 2)


class ImpossibleObservation(ValueError):
    """The observation has zero probability under the model."""


class ReplayError(ValueError):
    """An identifier has already been accepted in this process."""


def check_probability(p):
    if not isinstance(p, F) or not F(0) <= p <= F(1):
        raise ValueError("probability must be a Fraction in [0, 1]")


def likelihoods(positive, sensitivity, false_positive):
    """Return result likelihoods in the faulty and healthy states."""
    if type(positive) is not bool:
        raise ValueError("positive must be a Boolean")
    check_probability(sensitivity)
    check_probability(false_positive)
    if positive:
        return sensitivity, false_positive
    return 1 - sensitivity, 1 - false_positive


def update(p, positive, sensitivity=SENSITIVITY,
           false_positive=FALSE_POSITIVE):
    """Return (result probability, posterior fault probability).

    The hidden state does not change during diagnosis.
    """
    check_probability(p)
    lf, lh = likelihoods(positive, sensitivity, false_positive)
    probability = p * lf + (1 - p) * lh
    if probability == 0:
        raise ImpossibleObservation("observation has zero probability")
    return probability, p * lf / probability


def terminal_values(p):
    """Final-action values in tie-breaking order."""
    check_probability(p)
    return [(F(-2), "repair"), (F(4) - 16 * p, "run")]


@lru_cache(maxsize=None)
def solve(p, n, sensitivity=SENSITIVITY,
          false_positive=FALSE_POSITIVE, cost=DIAGNOSTIC_COST):
    """Return (optimal value, action) with at most n diagnostics.

    Results are conditionally independent given the fixed state.
    Exact ties favour the first action in the choices list.
    """
    check_probability(p)
    check_probability(sensitivity)
    check_probability(false_positive)
    if type(n) is not int or n < 0:
        raise ValueError("n must be a non-negative integer")
    if not isinstance(cost, F) or cost < 0:
        raise ValueError("cost must be a non-negative Fraction")

    choices = terminal_values(p)
    if n > 0:
        diagnostic_value = -cost
        for positive in (True, False):
            lf, lh = likelihoods(
                positive, sensitivity, false_positive
            )
            probability = p * lf + (1 - p) * lh
            if probability > 0:
                _, posterior = update(
                    p, positive, sensitivity, false_positive
                )
                continuation, _ = solve(
                    posterior, n - 1,
                    sensitivity, false_positive, cost
                )
                diagnostic_value += probability * continuation
        choices.append((diagnostic_value, "diagnose"))

    return max(choices, key=lambda item: item[0])


class Intake:
    """In-memory duplicate-ID demonstration, not a security control."""

    def __init__(self):
        self.seen = set()

    def accept(self, event_id, positive, prior):
        if not isinstance(event_id, str) or not event_id:
            raise ValueError("a non-empty event ID is required")
        if event_id in self.seen:
            raise ReplayError("duplicate event ID")
        probability, posterior = update(prior, positive)
        # Not a durable transaction with a belief store.
        self.seen.add(event_id)
        return probability, posterior


def expect_error(error_type, function, *args):
    try:
        function(*args)
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


def tests():
    prior = F(1, 2)

    # Values independently derived in the chapter's branch table.
    assert solve(prior, 0) == (F(-2), "repair")
    assert solve(prior, 1) == (F(-11, 10), "diagnose")
    assert solve(prior, 2) == (F(-103, 100), "diagnose")
    assert solve(prior, 3) == (F(-443, 500), "diagnose")
    assert solve(F(1, 17), 1) == (F(52, 17), "run")
    assert solve(F(1, 5), 2) == (F(307, 250), "diagnose")
    assert solve(F(4, 5), 2) == (F(-2), "repair")
    assert solve(F(3, 8), 0) == (F(-2), "repair")
    assert solve(F(1, 4), 1) == (F(3, 5), "diagnose")

    # Recompute numerator and denominator for each result.
    models = ((F(4, 5), F(1, 5)),
              (F(4, 5), F(1, 10)),
              (F(1), F(0)))
    for sensitivity, false_positive in models:
        for numerator in range(11):
            p = F(numerator, 10)
            result_probabilities = []
            for positive in (True, False):
                lf = sensitivity if positive else 1 - sensitivity
                lh = false_positive if positive else 1 - false_positive
                faulty_mass = p * lf
                healthy_mass = (1 - p) * lh
                denominator = faulty_mass + healthy_mass
                result_probabilities.append(denominator)

                if denominator == 0:
                    expect_error(
                        ImpossibleObservation, update, p, positive,
                        sensitivity, false_positive
                    )
                else:
                    probability, posterior = update(
                        p, positive, sensitivity, false_positive
                    )
                    assert probability == denominator
                    assert posterior == faulty_mass / denominator
                    assert 1 - posterior == healthy_mass / denominator
                    assert F(0) <= posterior <= F(1)
            assert sum(result_probabilities, F(0)) == 1

    # Alternative likelihoods through the recursive solver.
    assert solve(prior, 1, F(4, 5), F(1, 10)) == (
        F(-4, 5), "diagnose"
    )
    # Perfect result: pay 1/2, then repair if faulty, run if healthy.
    assert solve(prior, 1, F(1), F(0)) == (
        F(1, 2), "diagnose"
    )
    # An uninformative, costly diagnostic is not worth taking.
    assert solve(prior, 2, F(1, 2), F(1, 2)) == (
        F(-2), "repair"
    )

    # An additional optional diagnostic cannot lower the optimum.
    for p in (F(0), F(1, 4), F(1, 2), F(3, 4), F(1)):
        values = [solve(p, n)[0] for n in range(4)]
        assert all(values[i + 1] >= values[i] for i in range(3))

    expect_error(ValueError, update, F(11, 10), True)
    expect_error(ValueError, update, prior, "positive")
    expect_error(ValueError, solve, prior, -1)

    intake = Intake()
    _, first = intake.accept("measurement-1", True, F(1, 4))
    assert first == F(4, 7)
    expect_error(
        ReplayError, intake.accept, "measurement-1", True, first
    )
    _, naive_replay = update(first, True)
    assert naive_replay == F(16, 19)


def main():
    tests()
    print("All deterministic tests passed.")
    prior = F(1, 2)
    for n in range(4):
        value, action = solve(prior, n)
        print(f"n={n}: action={action}, value={float(value):.3f}")

    for positive, label in ((True, "positive"), (False, "negative")):
        probability, posterior = update(prior, positive)
        print(
            f"{label}: probability={float(probability):.3f}, "
            f"posterior={float(posterior):.3f}"
        )

    _, first = update(F(1, 4), True)
    _, replay = update(first, True)
    print(
        f"one positive={float(first):.6f}; "
        f"naive replay={float(replay):.6f}"
    )


if __name__ == "__main__":
    main()
