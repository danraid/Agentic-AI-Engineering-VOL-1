from dataclasses import dataclass
import math
import unittest

PRIOR_DANGER = 0.3
P_CLEAR_GIVEN_DANGER = 0.2
P_CLEAR_GIVEN_SAFE = 0.8
RISK_CAP = 0.1
MAX_AGE_SECONDS = 30
EXPECTED_PROFILE = "sensor-v1"
INSPECTION_COST = 1.0


@dataclass(frozen=True)
class Evidence:
    reading: str
    observed_at: int
    profile: str


@dataclass(frozen=True)
class Decision:
    action: str
    reason: str
    posterior: float | None


def posterior_danger(reading: str) -> float:
    """Update the fixed prior using the fixed hypothetical model."""
    if reading == "CLEAR":
        likelihood_danger = P_CLEAR_GIVEN_DANGER
        likelihood_safe = P_CLEAR_GIVEN_SAFE
    elif reading == "ALARM":
        likelihood_danger = 1.0 - P_CLEAR_GIVEN_DANGER
        likelihood_safe = 1.0 - P_CLEAR_GIVEN_SAFE
    else:
        raise ValueError("unknown reading")

    numerator = PRIOR_DANGER * likelihood_danger
    denominator = numerator + (1.0 - PRIOR_DANGER) * likelihood_safe
    if not math.isfinite(denominator) or denominator <= 0.0:
        raise ValueError("observation impossible under model")
    return numerator / denominator


def decide(evidence: Evidence, now: int) -> Decision:
    """Return a recommendation; never execute an operation."""
    if type(now) is not int or type(evidence.observed_at) is not int:
        return Decision("DEFER", "invalid timestamp", None)

    age = now - evidence.observed_at
    if age < 0 or age > MAX_AGE_SECONDS:
        return Decision("DEFER", "evidence not fresh", None)

    if evidence.profile != EXPECTED_PROFILE:
        return Decision("DEFER", "unapproved sensor profile", None)

    try:
        p = posterior_danger(evidence.reading)
    except ValueError:
        return Decision("DEFER", "invalid observation", None)

    restart_utility = 8.0 - 20.0 * p
    if p <= RISK_CAP and restart_utility > 0.0:
        return Decision("RESTART", "nominal checks passed", p)
    return Decision("DEFER", "risk or utility check failed", p)


def inspection_value(cost: float) -> float:
    """Expected value of clear->restart, alarm->defer."""
    safe_clear = (1.0 - PRIOR_DANGER) * P_CLEAR_GIVEN_SAFE
    danger_clear = PRIOR_DANGER * P_CLEAR_GIVEN_DANGER
    return 8.0 * safe_clear - 12.0 * danger_clear - cost


class RestartLabTests(unittest.TestCase):
    def test_exact_values(self):
        self.assertAlmostEqual(posterior_danger("CLEAR"), 3 / 31)
        self.assertAlmostEqual(posterior_danger("ALARM"), 12 / 19)
        self.assertAlmostEqual(inspection_value(0.0), 3.76)
        self.assertAlmostEqual(inspection_value(INSPECTION_COST), 2.76)

    def test_fresh_clear_recommends_restart(self):
        result = decide(Evidence("CLEAR", 990, "sensor-v1"), 1000)
        self.assertEqual(result.action, "RESTART")
        self.assertLessEqual(result.posterior, RISK_CAP)

    def test_alarm_defers(self):
        result = decide(Evidence("ALARM", 990, "sensor-v1"), 1000)
        self.assertEqual(result.action, "DEFER")
        self.assertGreater(result.posterior, RISK_CAP)

    def test_failure_injection_stale_evidence(self):
        result = decide(Evidence("CLEAR", 960, "sensor-v1"), 1000)
        self.assertEqual(result.action, "DEFER")
        self.assertEqual(result.reason, "evidence not fresh")
        self.assertIsNone(result.posterior)

    def test_failure_injection_wrong_profile(self):
        result = decide(Evidence("CLEAR", 990, "sensor-v2"), 1000)
        self.assertEqual(result.action, "DEFER")
        self.assertEqual(result.reason, "unapproved sensor profile")

    def test_future_and_malformed_evidence(self):
        future = decide(Evidence("CLEAR", 1001, "sensor-v1"), 1000)
        malformed = decide(Evidence("UNKNOWN", 990, "sensor-v1"), 1000)
        self.assertEqual(future.action, "DEFER")
        self.assertEqual(malformed.action, "DEFER")

    def test_freshness_boundary(self):
        boundary = decide(Evidence("CLEAR", 970, "sensor-v1"), 1000)
        self.assertEqual(boundary.action, "RESTART")


if __name__ == "__main__":
    unittest.main(verbosity=2)
