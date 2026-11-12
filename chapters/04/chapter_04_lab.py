"""Hypothetical attention, policy and mock-resource laboratory.

Python 3 standard library only. No transformer is trained and no real
document, identity provider or access service is used.
"""

import math
import unittest
from dataclasses import dataclass


THRESHOLD = 0.10
MAX_AGE_HOURS = 24.0
TOY_TRAIN = [(-2.0, 0), (-1.0, 0), (1.0, 1), (2.0, 1)]


def sigmoid(value):
    """Numerically stable logistic function."""
    if value >= 0:
        return 1.0 / (1.0 + math.exp(-value))
    exp_value = math.exp(value)
    return exp_value / (1.0 + exp_value)


def attention_example():
    """Fixed worked-example arithmetic; no projections are learned."""
    query = (1.0, 0.0)
    keys = ((1.0, 0.0), (0.0, 1.0))
    values = (1.0, 0.0)
    scores = [
        sum(q * k for q, k in zip(query, key)) / math.sqrt(len(query))
        for key in keys
    ]
    maximum = max(scores)
    exponentials = [math.exp(score - maximum) for score in scores]
    denominator = sum(exponentials)
    weights = [value / denominator for value in exponentials]
    output = sum(weight * value for weight, value in zip(weights, values))
    return weights, output


def matrix_shape(matrix):
    """Return dimensions of a non-empty rectangular list of rows."""
    if not matrix or not matrix[0]:
        raise ValueError("matrix must be non-empty")
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("matrix must be rectangular")
    return len(matrix), width


def matmul(left, right):
    """Small, explicit matrix multiplication for teaching."""
    rows, inner = matrix_shape(left)
    right_rows, columns = matrix_shape(right)
    if inner != right_rows:
        raise ValueError("incompatible matrix dimensions")
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(inner))
            for j in range(columns)
        ]
        for i in range(rows)
    ]


def causal_attention(inputs, w_query, w_key, w_value):
    """One projected causal-attention head: return weights and outputs.

    A position can attend to itself and earlier positions. Future positions
    receive exactly zero weight. Projection matrices are supplied, not fitted.
    """
    q = matmul(inputs, w_query)
    k = matmul(inputs, w_key)
    v = matmul(inputs, w_value)
    token_count, query_width = matrix_shape(q)
    key_count, key_width = matrix_shape(k)
    value_count, value_width = matrix_shape(v)

    if query_width != key_width:
        raise ValueError("query and key widths must match")
    if key_count != token_count or value_count != token_count:
        raise ValueError("projected token counts must match")

    all_weights = []
    outputs = []
    for i in range(token_count):
        # Construct permitted scores only, so no row is entirely masked.
        scores = [
            sum(q[i][d] * k[j][d] for d in range(query_width))
            / math.sqrt(query_width)
            for j in range(i + 1)
        ]
        maximum = max(scores)
        exponentials = [math.exp(score - maximum) for score in scores]
        denominator = sum(exponentials)
        permitted = [value / denominator for value in exponentials]
        weights = permitted + [0.0] * (token_count - i - 1)
        output = [
            sum(weights[j] * v[j][d] for j in range(token_count))
            for d in range(value_width)
        ]
        all_weights.append(weights)
        outputs.append(output)
    return all_weights, outputs


@dataclass(frozen=True)
class LogisticHead:
    weight: float
    bias: float

    def probability(self, feature):
        if not math.isfinite(feature):
            raise ValueError("feature must be finite")
        return sigmoid(self.weight * feature + self.bias)


def train_head(examples, steps=400, learning_rate=0.5):
    """Deterministic full-batch descent on binary cross-entropy."""
    if not examples:
        raise ValueError("training set must not be empty")
    if any(not math.isfinite(x) or y not in (0, 1) for x, y in examples):
        raise ValueError("expected finite features and binary labels")

    weight = 0.0
    bias = 0.0
    count = len(examples)

    for _ in range(steps):
        grad_weight = 0.0
        grad_bias = 0.0
        for feature, label in examples:
            prediction = sigmoid(weight * feature + bias)
            error = prediction - label
            grad_weight += error * feature
            grad_bias += error
        weight -= learning_rate * grad_weight / count
        bias -= learning_rate * grad_bias / count

    return LogisticHead(weight, bias)


@dataclass(frozen=True)
class Decision:
    action: str
    reason: str


def finite_number(value):
    """Accept ordinary finite numeric test inputs, excluding Booleans."""
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def decide(probability, authorised, evidence_age_hours):
    """Validate policy inputs before applying the toy threshold."""
    if not finite_number(probability) or not 0.0 <= probability <= 1.0:
        return Decision("review", "invalid_probability")

    # This Boolean represents an already obtained authorisation result;
    # it is not itself authentication or a trusted permission service.
    if authorised is not True:
        return Decision("review", "access_denied")

    if (
        not finite_number(evidence_age_hours)
        or evidence_age_hours < 0.0
        or evidence_age_hours > MAX_AGE_HOURS
    ):
        return Decision("review", "stale_or_invalid_metadata")

    # The documented tie policy is to skip at exactly the threshold.
    if probability <= THRESHOLD:
        return Decision("skip", "below_or_at_threshold")

    return Decision("retrieve", "eligible")


def simulate_request(probability, authorised, evidence_age_hours):
    """Return a policy trace; this function does not access a resource."""
    decision = decide(probability, authorised, evidence_age_hours)
    trace = [("decision", decision.action, decision.reason)]
    if decision.action == "retrieve":
        trace.append(("tool_call", "retrieve"))
    return decision, trace


def valid_identifier(value):
    """Small mock identifier rule, not a production identity validator."""
    return (
        isinstance(value, str)
        and bool(value)
        and value == value.strip()
        and all(ch.isascii() and (ch.isalnum() or ch in "-_")
                for ch in value)
    )


class RetrievalFailure(Exception):
    """Simulated failure of the mock retrieval service."""


class MockResource:
    """In-memory service with a permission check at every read."""

    def __init__(self):
        self.permissions = set()
        self.documents = {"incident-1": "hypothetical incident record"}
        self.fail_reads = False

    def grant(self, principal, document):
        self.permissions.add((principal, document))

    def revoke(self, principal, document):
        self.permissions.discard((principal, document))

    def allowed(self, principal, document):
        return (principal, document) in self.permissions

    def read(self, principal, document):
        if not self.allowed(principal, document):
            raise PermissionError("resource access denied")
        if self.fail_reads:
            raise RetrievalFailure("simulated retrieval failure")
        return self.documents[document]


def policy_then_read(resource, principal, document, probability, age,
                     revoke_before_read=False):
    """Exercise policy and resource boundaries in a fixed order."""
    if not valid_identifier(principal) or not valid_identifier(document):
        return Decision("review", "invalid_identifier"), None

    initially_allowed = resource.allowed(principal, document)
    decision = decide(probability, initially_allowed, age)
    if decision.action != "retrieve":
        return decision, None

    if revoke_before_read:
        resource.revoke(principal, document)

    try:
        content = resource.read(principal, document)
    except PermissionError:
        return Decision("review", "resource_access_denied"), None
    except KeyError:
        return Decision("review", "resource_missing"), None
    except RetrievalFailure:
        return Decision("review", "retrieval_failure"), None
    return decision, content


class LaboratoryTests(unittest.TestCase):
    def test_attention_arithmetic(self):
        weights, output = attention_example()
        self.assertAlmostEqual(sum(weights), 1.0)
        self.assertAlmostEqual(weights[0], 0.6697615, places=6)
        self.assertAlmostEqual(output, weights[0])

    def test_causal_weights_and_shapes(self):
        inputs = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
        identity = [[1.0, 0.0], [0.0, 1.0]]
        weights, outputs = causal_attention(
            inputs, identity, identity, identity
        )
        self.assertEqual(len(outputs), 3)
        self.assertEqual(len(outputs[0]), 2)
        for i, row in enumerate(weights):
            self.assertAlmostEqual(sum(row), 1.0)
            for j in range(i + 1, len(row)):
                self.assertEqual(row[j], 0.0)

    def test_future_change_does_not_change_earlier_outputs(self):
        identity = [[1.0, 0.0], [0.0, 1.0]]
        first = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
        changed = [[1.0, 0.0], [0.0, 1.0], [50.0, -30.0]]
        _, out_first = causal_attention(first, identity, identity, identity)
        _, out_changed = causal_attention(changed, identity, identity, identity)
        self.assertEqual(out_first[:2], out_changed[:2])

    def test_value_projection_is_applied(self):
        inputs = [[1.0, 2.0], [0.0, 1.0]]
        identity = [[1.0, 0.0], [0.0, 1.0]]
        w_value = [[2.0], [3.0]]
        _, outputs = causal_attention(inputs, identity, identity, w_value)
        self.assertAlmostEqual(outputs[0][0], 8.0)

    def test_incompatible_projection_is_rejected(self):
        inputs = [[1.0, 0.0]]
        identity = [[1.0, 0.0], [0.0, 1.0]]
        one_column = [[1.0], [0.0]]
        with self.assertRaises(ValueError):
            causal_attention(inputs, identity, one_column, identity)

    def test_training_is_deterministic(self):
        self.assertEqual(train_head(TOY_TRAIN), train_head(TOY_TRAIN))

    def test_toy_head_orders_features(self):
        head = train_head(TOY_TRAIN)
        self.assertGreater(head.weight, 0.0)
        self.assertAlmostEqual(head.bias, 0.0, places=12)
        self.assertLess(head.probability(-1.0), head.probability(1.0))

    def test_out_of_pattern_with_specified_head(self):
        # This test is independent of the optimisation trajectory.
        head = LogisticHead(weight=1.0, bias=0.0)
        feature, label = 0.80, 0
        prediction = int(head.probability(feature) >= 0.5)
        self.assertNotEqual(prediction, label)

    def test_opposing_labels_with_identical_feature(self):
        head = LogisticHead(weight=1.0, bias=0.0)
        cases = [(0.80, 0), (0.80, 1)]
        predictions = [
            int(head.probability(feature) >= 0.5)
            for feature, _ in cases
        ]
        self.assertEqual(predictions[0], predictions[1])
        correct = sum(
            prediction == label
            for prediction, (_, label) in zip(predictions, cases)
        )
        self.assertEqual(correct, 1)

    def test_threshold_and_tie(self):
        self.assertEqual(decide(0.10, True, 0).action, "skip")
        self.assertEqual(decide(0.11, True, 0).action, "retrieve")

    def test_denied_access_prevents_tool_call(self):
        decision, trace = simulate_request(0.9, False, 1)
        self.assertEqual(decision.reason, "access_denied")
        self.assertNotIn(("tool_call", "retrieve"), trace)

    def test_stale_metadata_prevents_tool_call(self):
        decision, trace = simulate_request(0.9, True, 25)
        self.assertEqual(decision.reason, "stale_or_invalid_metadata")
        self.assertNotIn(("tool_call", "retrieve"), trace)

    def test_invalid_inputs_route_to_review(self):
        self.assertEqual(decide(float("nan"), True, 1).action, "review")
        self.assertEqual(decide(1.1, True, 1).action, "review")
        self.assertEqual(decide(0.9, True, None).action, "review")
        self.assertEqual(decide(0.9, True, -1).action, "review")
        self.assertEqual(decide(0.9, None, 1).action, "review")
        decision, trace = simulate_request(0.9, True, float("nan"))
        self.assertEqual(decision.reason, "stale_or_invalid_metadata")
        self.assertNotIn(("tool_call", "retrieve"), trace)

    def test_mock_resource_allows_current_permission(self):
        resource = MockResource()
        resource.grant("alice", "incident-1")
        decision, content = policy_then_read(
            resource, "alice", "incident-1", 0.9, 1.0
        )
        self.assertEqual(decision.action, "retrieve")
        self.assertEqual(content, "hypothetical incident record")

    def test_revocation_between_policy_and_resource(self):
        resource = MockResource()
        resource.grant("alice", "incident-1")
        decision, content = policy_then_read(
            resource, "alice", "incident-1", 0.9, 1.0,
            revoke_before_read=True,
        )
        self.assertEqual(decision.action, "review")
        self.assertEqual(decision.reason, "resource_access_denied")
        self.assertIsNone(content)

    def test_low_score_does_not_bypass_validation(self):
        self.assertEqual(decide(0.01, False, 1).reason, "access_denied")
        self.assertEqual(
            decide(0.01, True, None).reason, "stale_or_invalid_metadata"
        )
        self.assertEqual(decide("0.01", True, 1).reason,
                         "invalid_probability")

    def test_missing_resource_routes_to_review(self):
        resource = MockResource()
        resource.grant("alice", "incident-missing")
        decision, content = policy_then_read(
            resource, "alice", "incident-missing", 0.9, 1.0
        )
        self.assertEqual(decision.reason, "resource_missing")
        self.assertEqual(decision.action, "review")
        self.assertIsNone(content)

    def test_retrieval_failure_routes_to_review(self):
        resource = MockResource()
        resource.grant("alice", "incident-1")
        resource.fail_reads = True
        decision, content = policy_then_read(
            resource, "alice", "incident-1", 0.9, 1.0
        )
        self.assertEqual(decision.reason, "retrieval_failure")
        self.assertEqual(decision.action, "review")
        self.assertIsNone(content)

    def test_malformed_identifier_routes_to_review(self):
        resource = MockResource()
        decision, content = policy_then_read(
            resource, "alice", "../incident-1", 0.01, 1.0
        )
        self.assertEqual(decision.reason, "invalid_identifier")
        self.assertEqual(decision.action, "review")
        self.assertIsNone(content)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(LaboratoryTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)

    weights, attention_output = attention_example()
    print("Attention weights:", [round(value, 4) for value in weights])
    print("Attention output:", round(attention_output, 4))
    print("Fixed-head probability:", round(sigmoid(attention_output), 4))

    identity = [[1.0, 0.0], [0.0, 1.0]]
    causal_weights, _ = causal_attention(
        [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]],
        identity, identity, identity,
    )
    print("First causal row:", causal_weights[0])

    head = train_head(TOY_TRAIN)
    probability = head.probability(0.5)
    decision, _ = simulate_request(probability, True, 1.0)
    print(f"Toy weight: {head.weight:.6f}; bias: {head.bias:.6f}")
    print(f"Toy probability: {probability:.6f}; action: {decision.action}")
