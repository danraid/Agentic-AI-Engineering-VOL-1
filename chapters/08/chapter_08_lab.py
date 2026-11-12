"""Deterministic, hypothetical order-checking laboratory.

Run with: python3 order_lab.py
No network, credentials, model or third-party package is required.
"""

from copy import deepcopy
import hashlib
import json
import unittest


SPEC_VERSION = "order-spec-1"
SOURCE_VERSION = "approval-7"

# Hypothetical record; amounts are integer pence and tax is omitted.
ORDER = {
    "order_id": "O-104",
    "currency": "GBP",
    "lines": [
        {"item": "sensor", "quantity": 2, "unit_price": 1250},
        {"item": "cable", "quantity": 3, "unit_price": 400},
    ],
}

MAX_DEPTH = 12
MAX_NODES = 500
MAX_STRING = 256
MAX_INTEGER = 10**12
MAX_LINES = 50


class InvalidInput(ValueError):
    """Input is outside this laboratory's deliberately bounded domain."""


def _check_json_value(value, depth, remaining, active):
    """Check types and bounds before JSON encoding or deep copying."""
    remaining[0] -= 1
    if remaining[0] < 0 or depth > MAX_DEPTH:
        raise InvalidInput("input too large or too deeply nested")

    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if abs(value) > MAX_INTEGER:
            raise InvalidInput("integer out of range")
        return
    if type(value) is str:
        if len(value) > MAX_STRING:
            raise InvalidInput("string too long")
        return
    if type(value) not in (list, dict):
        raise InvalidInput("unsupported JSON type")

    identity = id(value)
    if identity in active:
        raise InvalidInput("cyclic structure")
    active.add(identity)
    try:
        if type(value) is list:
            for child in value:
                _check_json_value(child, depth + 1, remaining, active)
        else:
            for key, child in value.items():
                if type(key) is not str or len(key) > MAX_STRING:
                    raise InvalidInput("invalid object key")
                _check_json_value(child, depth + 1, remaining, active)
    finally:
        active.remove(identity)


def canonical(value):
    """Bounded deterministic representation for this laboratory."""
    _check_json_value(value, 0, [MAX_NODES], set())
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def fingerprint(value):
    """Short trace label, not an authenticity or security identity."""
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()[:12]


def validate_lines(lines):
    """Require bounded, uniquely identified, strictly typed order lines."""
    if type(lines) is not list or not 1 <= len(lines) <= MAX_LINES:
        raise InvalidInput("invalid lines")
    items = set()
    for line in lines:
        if type(line) is not dict or set(line) != {
            "item", "quantity", "unit_price"
        }:
            raise InvalidInput("invalid line structure")
        item = line["item"]
        quantity = line["quantity"]
        price = line["unit_price"]
        if type(item) is not str or not item or len(item) > MAX_STRING:
            raise InvalidInput("invalid item identifier")
        if item in items:
            raise InvalidInput("duplicate item identifier")
        items.add(item)
        # bool is a subclass of int, so use exact type checks.
        if type(quantity) is not int or not 1 <= quantity <= MAX_INTEGER:
            raise InvalidInput("invalid quantity")
        if type(price) is not int or not 0 <= price <= MAX_INTEGER:
            raise InvalidInput("invalid unit price")


def validate_order(order):
    """Validate structure, not authenticity or business authority."""
    canonical(order)
    if type(order) is not dict or set(order) != {
        "order_id", "currency", "lines"
    }:
        raise InvalidInput("invalid order structure")
    if (
        type(order["order_id"]) is not str
        or not order["order_id"]
        or type(order["currency"]) is not str
        or order["currency"] != "GBP"
    ):
        raise InvalidInput("invalid order identity or currency")
    validate_lines(order["lines"])


def approved_total(order):
    validate_order(order)
    total = sum(
        line["quantity"] * line["unit_price"]
        for line in order["lines"]
    )
    if total > MAX_INTEGER:
        raise InvalidInput("total out of range")
    return total


def expected_draft(order):
    draft = deepcopy(order)
    draft["total"] = approved_total(order)
    return draft


def verify(draft, order):
    """Compare a bounded candidate with the supplied laboratory record."""
    canonical(draft)
    expected = expected_draft(order)
    if type(draft) is not dict:
        return ("STRUCTURE",)

    diagnostics = []
    if set(draft) != set(expected):
        diagnostics.append("STRUCTURE")

    for field in ("order_id", "currency", "lines", "total"):
        if field not in draft:
            diagnostics.append("MISSING_" + field.upper())
        elif canonical(draft[field]) != canonical(expected[field]):
            diagnostics.append("MISMATCH_" + field.upper())

    if "lines" in draft:
        try:
            validate_lines(draft["lines"])
        except InvalidInput:
            diagnostics.append("INVALID_LINES")
    return tuple(diagnostics)


def repair_from_order(draft, diagnostics, order):
    """Propose a narrow repair from the supplied record; make no payment."""
    expected = expected_draft(order)
    repaired = deepcopy(draft) if type(draft) is dict else {}

    if "STRUCTURE" in diagnostics:
        repaired = {k: v for k, v in repaired.items() if k in expected}

    for field in ("order_id", "currency", "lines", "total"):
        if (
            "MISSING_" + field.upper() in diagnostics
            or "MISMATCH_" + field.upper() in diagnostics
            or (field == "lines" and "INVALID_LINES" in diagnostics)
        ):
            repaired[field] = deepcopy(expected[field])

    # A non-dictionary candidate produces only STRUCTURE.
    if type(draft) is not dict:
        repaired = deepcopy(expected)
    return repaired


def run(candidate, order, observed_version, current_version,
        repairer, max_repairs=2):
    """Return a local disposition and trace; never execute a payment."""
    events = []

    def record(kind, **details):
        events.append({
            "event": kind,
            "spec": SPEC_VERSION,
            "source": observed_version,
            **details,
        })

    if type(max_repairs) is not int or not 0 <= max_repairs <= 100:
        raise ValueError("invalid repair budget")

    # This compares supplied strings; it does not authenticate them.
    if (
        type(observed_version) is not str
        or type(current_version) is not str
        or not observed_version
        or not current_version
        or len(observed_version) > MAX_STRING
        or len(current_version) > MAX_STRING
    ):
        record("unknown_evidence")
        return "ESCALATE", events
    if observed_version != current_version:
        record("stale_evidence")
        return "ESCALATE", events

    try:
        validate_order(order)
        approved_total(order)
    except InvalidInput:
        record("invalid_evidence")
        return "ESCALATE", events

    try:
        canonical(candidate)
        draft = deepcopy(candidate)
    except InvalidInput:
        record("invalid_candidate")
        return "ESCALATE", events

    seen = set()
    repairs = 0

    while True:
        try:
            # Compare full canonical states, not truncated trace hashes.
            state = canonical(draft)
        except InvalidInput:
            record("invalid_candidate")
            return "ESCALATE", events

        if state in seen:
            record("repeated_candidate", candidate=fingerprint(draft))
            return "ESCALATE", events
        seen.add(state)

        try:
            diagnostics = verify(draft, order)
        except InvalidInput:
            record("invalid_candidate")
            return "ESCALATE", events
        record(
            "checked",
            candidate=fingerprint(draft),
            diagnostics=list(diagnostics),
        )

        if not diagnostics:
            return "PASS", events
        if repairs >= max_repairs:
            record("budget_exhausted", repairs=repairs)
            return "ESCALATE", events

        # The repairer is a teaching stub. A production boundary would
        # also need timeout, exception and resource isolation policies.
        draft = repairer(deepcopy(draft), diagnostics, deepcopy(order))
        repairs += 1
        record("repair_proposed", repairs=repairs)


def no_progress(draft, diagnostics, order):
    """Injected faulty repairer: return the candidate unchanged."""
    return draft


def exercise_lab():
    """Original control-loop assertions, retained as a regression test."""
    good = expected_draft(ORDER)
    assert approved_total(ORDER) == 3700
    assert verify(good, ORDER) == ()

    # Injection 1: incorrect arithmetic in an otherwise correct draft.
    wrong_total = deepcopy(good)
    wrong_total["total"] = 3600
    status, trace = run(
        wrong_total, ORDER, SOURCE_VERSION, SOURCE_VERSION,
        repair_from_order
    )
    assert status == "PASS"
    assert trace[0]["diagnostics"] == ["MISMATCH_TOTAL"]

    # Injection 2: internally consistent but unapproved unit price.
    wrong_price = deepcopy(good)
    wrong_price["lines"][0]["unit_price"] = 1300
    wrong_price["total"] = 3800
    status, trace = run(
        wrong_price, ORDER, SOURCE_VERSION, SOURCE_VERSION,
        repair_from_order
    )
    assert status == "PASS"
    assert trace[0]["diagnostics"] == [
        "MISMATCH_LINES", "MISMATCH_TOTAL"
    ]

    # Injection 3: supplied approval version is no longer current.
    status, trace = run(
        good, ORDER, SOURCE_VERSION, "approval-8", repair_from_order
    )
    assert status == "ESCALATE"
    assert trace[0]["event"] == "stale_evidence"

    # Injection 4: repairer repeats an invalid candidate.
    status, trace = run(
        wrong_total, ORDER, SOURCE_VERSION, SOURCE_VERSION, no_progress
    )
    assert status == "ESCALATE"
    assert trace[-1]["event"] == "repeated_candidate"


class OrderLabTests(unittest.TestCase):
    def test_original_control_loop(self):
        exercise_lab()

    def test_fixed_golden_case(self):
        # Fixed independently of expected_draft and approved_total.
        golden = {
            "order_id": "O-104",
            "currency": "GBP",
            "lines": [
                {"item": "sensor", "quantity": 2, "unit_price": 1250},
                {"item": "cable", "quantity": 3, "unit_price": 400},
            ],
            "total": 3700,
        }
        self.assertEqual(expected_draft(ORDER), golden)
        self.assertEqual(verify(golden, ORDER), ())

    def test_independent_total_calculation(self):
        # Different implementation from approved_total.
        amounts = []
        for line in ORDER["lines"]:
            amounts.extend([line["unit_price"]] * line["quantity"])
        self.assertEqual(sum(amounts), 3700)
        self.assertEqual(approved_total(ORDER), sum(amounts))

    def test_missing_candidate_field_is_repaired(self):
        draft = expected_draft(ORDER)
        del draft["total"]
        self.assertIn("MISSING_TOTAL", verify(draft, ORDER))
        status, _ = run(
            draft, ORDER, SOURCE_VERSION, SOURCE_VERSION, repair_from_order
        )
        self.assertEqual(status, "PASS")

    def test_non_dictionary_candidate_is_repaired(self):
        status, trace = run(
            [], ORDER, SOURCE_VERSION, SOURCE_VERSION, repair_from_order
        )
        self.assertEqual(status, "PASS")
        self.assertEqual(trace[0]["diagnostics"], ["STRUCTURE"])

    def test_extra_field_is_removed(self):
        draft = expected_draft(ORDER)
        draft["unexpected"] = "data"
        status, trace = run(
            draft, ORDER, SOURCE_VERSION, SOURCE_VERSION, repair_from_order
        )
        self.assertEqual(status, "PASS")
        self.assertIn("STRUCTURE", trace[0]["diagnostics"])

    def test_duplicate_candidate_identifiers_are_detected(self):
        draft = expected_draft(ORDER)
        draft["lines"][1]["item"] = "sensor"
        self.assertIn("INVALID_LINES", verify(draft, ORDER))
        status, _ = run(
            draft, ORDER, SOURCE_VERSION, SOURCE_VERSION, repair_from_order
        )
        self.assertEqual(status, "PASS")

    def test_duplicate_order_identifiers_escalate(self):
        order = deepcopy(ORDER)
        order["lines"][1]["item"] = "sensor"
        status, trace = run(
            expected_draft(ORDER), order, SOURCE_VERSION, SOURCE_VERSION,
            repair_from_order
        )
        self.assertEqual(status, "ESCALATE")
        self.assertEqual(trace[0]["event"], "invalid_evidence")

    def test_missing_order_field_escalates(self):
        order = deepcopy(ORDER)
        del order["currency"]
        status, trace = run(
            {}, order, SOURCE_VERSION, SOURCE_VERSION, repair_from_order
        )
        self.assertEqual(status, "ESCALATE")
        self.assertEqual(trace[0]["event"], "invalid_evidence")

    def test_unexpected_order_type_escalates(self):
        order = deepcopy(ORDER)
        order["lines"][0]["quantity"] = True
        status, trace = run(
            {}, order, SOURCE_VERSION, SOURCE_VERSION, repair_from_order
        )
        self.assertEqual(status, "ESCALATE")
        self.assertEqual(trace[0]["event"], "invalid_evidence")

    def test_candidate_type_is_not_integer(self):
        draft = expected_draft(ORDER)
        draft["total"] = True
        self.assertIn("MISMATCH_TOTAL", verify(draft, ORDER))

    def test_unsupported_candidate_escalates(self):
        status, trace = run(
            {"total": object()}, ORDER, SOURCE_VERSION, SOURCE_VERSION,
            repair_from_order
        )
        self.assertEqual(status, "ESCALATE")
        self.assertEqual(trace[0]["event"], "invalid_candidate")

    def test_deep_and_large_candidates_escalate(self):
        nested = []
        for _ in range(MAX_DEPTH + 2):
            nested = [nested]
        for candidate in (nested, ["x"] * (MAX_NODES + 1)):
            with self.subTest(candidate_type=type(candidate).__name__):
                status, trace = run(
                    candidate, ORDER, SOURCE_VERSION, SOURCE_VERSION,
                    repair_from_order
                )
                self.assertEqual(status, "ESCALATE")
                self.assertEqual(trace[0]["event"], "invalid_candidate")

    def test_cycle_escalates(self):
        candidate = []
        candidate.append(candidate)
        status, trace = run(
            candidate, ORDER, SOURCE_VERSION, SOURCE_VERSION,
            repair_from_order
        )
        self.assertEqual(status, "ESCALATE")
        self.assertEqual(trace[0]["event"], "invalid_candidate")

    def test_missing_version_escalates(self):
        status, trace = run(
            expected_draft(ORDER), ORDER, None, SOURCE_VERSION,
            repair_from_order
        )
        self.assertEqual(status, "ESCALATE")
        self.assertEqual(trace[0]["event"], "unknown_evidence")

    def test_zero_repair_budget(self):
        draft = expected_draft(ORDER)
        draft["total"] = 3600
        status, trace = run(
            draft, ORDER, SOURCE_VERSION, SOURCE_VERSION,
            repair_from_order, max_repairs=0
        )
        self.assertEqual(status, "ESCALATE")
        self.assertEqual(trace[-1]["event"], "budget_exhausted")

    def test_corrupted_but_well_formed_evidence(self):
        # The golden order exposes the corruption in this test.
        corrupt = deepcopy(ORDER)
        corrupt["lines"][0]["unit_price"] = 1300
        corrupt_draft = expected_draft(corrupt)
        self.assertNotEqual(corrupt_draft["total"], 3700)
        self.assertIn("MISMATCH_LINES", verify(corrupt_draft, ORDER))

        # The controller cannot authenticate its supplied record.
        status, _ = run(
            corrupt_draft, corrupt, SOURCE_VERSION, SOURCE_VERSION,
            repair_from_order
        )
        self.assertEqual(status, "PASS")

    def test_repairer_exception_propagates(self):
        draft = expected_draft(ORDER)
        draft["total"] = 3600

        def raising_repairer(draft, diagnostics, order):
            raise RuntimeError("repair failed")

        with self.assertRaisesRegex(RuntimeError, "repair failed"):
            run(
                draft, ORDER, SOURCE_VERSION, SOURCE_VERSION,
                raising_repairer
            )


if __name__ == "__main__":
    unittest.main()
