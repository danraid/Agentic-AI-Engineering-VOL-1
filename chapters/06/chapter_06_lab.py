import unittest


class Conflict(Exception):
    pass


class ResponseLost(Exception):
    pass


class KeyReuse(Exception):
    pass


class Store:
    """Deterministic specification stub; not a production data store.

    Service-side crash atomicity and durable recovery are assumptions,
    not properties established by this sequential in-memory code.
    """

    def __init__(self, fault=None):
        self.value = 10
        self.revision = 0
        self.fault = fault
        self.injected = False
        self.reads = 0
        self.effects = 0
        self.completed = {}

    def read(self):
        self.reads += 1
        if self.fault == "bad_verify" and self.reads > 1:
            return 19, self.revision
        return self.value, self.revision

    def put(self, key, target, expected):
        request = (target, expected)

        # Deduplication precedes the revision check.
        if key in self.completed:
            old_request, result = self.completed[key]
            if request != old_request:
                raise KeyReuse(key)
            return result

        # A simulated external modification occurs before this write.
        if self.fault == "conflict" and not self.injected:
            self.injected = True
            self.value = 15
            self.revision += 1

        if expected != self.revision:
            raise Conflict()

        # WARNING: this sequential stub has an unmodelled crash window
        # between the effect and its deduplication record. These
        # assignments are NOT an atomic or durable service transaction.
        self.value = target
        self.revision += 1
        self.effects += 1
        result = (self.value, self.revision)
        self.completed[key] = (request, result)

        # The record exists in this stub, but the reply is lost.
        # The legacy fault name does not imply a real timeout.
        if self.fault == "timeout" and not self.injected:
            self.injected = True
            raise ResponseLost()

        return result


def run(store, run_id, target, max_writes=3):
    """Return terminal state and trace; run_id must be unique.

    Every DONE trace carries an OBSERVED_TARGET claim. This laboratory
    does not implement operation-linked verification.
    """
    trace = []

    def finish(state, reason):
        if state == "DONE":
            trace.append(("CLAIM", "OBSERVED_TARGET"))
        trace.append((state, reason))
        return state, trace

    # bool is excluded even though bool is a subclass of int.
    if type(target) is not int or not 1 <= target <= 100:
        return finish("ESCALATE", "invalid target")
    if type(max_writes) is not int or max_writes < 1:
        return finish("ESCALATE", "invalid budget")
    if not isinstance(run_id, str) or not run_id:
        return finish("ESCALATE", "invalid run id")

    trace.append(("READ", "initial"))
    value, revision = store.read()
    if value == target:
        return finish("DONE", "observed target")

    operation = 1
    key = f"{run_id}:{operation}"
    expected = revision
    calls = 0

    while calls < max_writes:
        calls += 1
        trace.append(("WRITE", (key, target, expected)))
        try:
            store.put(key, target, expected)
        except ResponseLost:
            trace.append(("UNCERTAIN", key))
            # Preserve key, target and expected revision.
            continue
        except Conflict:
            trace.append(("CONFLICT", key))
            trace.append(("READ", "after conflict"))
            value, revision = store.read()
            if value == target:
                return finish("DONE", "observed target")

            # A changed expected revision means a new logical request.
            operation += 1
            key = f"{run_id}:{operation}"
            expected = revision
            continue
        except KeyReuse:
            return finish("ESCALATE", "operation key reused")

        trace.append(("VERIFY", "read active value"))
        value, _ = store.read()
        if value == target:
            return finish("DONE", "observed target after write")
        return finish("ESCALATE", "verification mismatch")

    return finish("ESCALATE", "write budget exhausted")


def reconcile(store, intent):
    """Illustrative receipt-loss reconciliation; issue no new write.

    The dictionary stands in for a status API. Neither this intent nor
    the store survives process loss.
    """
    key = intent["key"]
    request = (intent["target"], intent["expected"])

    record = store.completed.get(key)
    if record is None:
        return "ESCALATE", "no operation record; outcome unresolved"

    recorded_request, receipt = record
    if recorded_request != request:
        return "ESCALATE", "operation record does not match intent"

    value, revision = store.read()
    receipt_value, receipt_revision = receipt

    if (
        receipt_value == intent["target"]
        and value == intent["target"]
        and revision == receipt_revision
    ):
        return "RECONCILED", "matching record and current read"

    return "ESCALATE", "record and current state require review"


class ControllerTests(unittest.TestCase):
    def test_normal_write(self):
        store = Store()
        state, trace = run(store, "normal", 20)
        self.assertEqual(state, "DONE")
        self.assertEqual((store.value, store.effects), (20, 1))
        self.assertEqual(
            trace[-1], ("DONE", "observed target after write")
        )

    def test_timeout_reuses_request_without_second_effect(self):
        store = Store("timeout")
        state, trace = run(store, "timeout", 20)
        writes = [item[1] for item in trace if item[0] == "WRITE"]
        self.assertEqual(state, "DONE")
        self.assertEqual(len(writes), 2)
        self.assertEqual(writes[0], writes[1])
        self.assertEqual(store.effects, 1)

    def test_conflict_creates_new_operation(self):
        store = Store("conflict")
        state, trace = run(store, "conflict", 20)
        writes = [item[1] for item in trace if item[0] == "WRITE"]
        self.assertEqual(state, "DONE")
        self.assertEqual(writes[0], ("conflict:1", 20, 0))
        self.assertEqual(writes[1], ("conflict:2", 20, 1))
        self.assertEqual(store.effects, 1)

    def test_bad_verification_does_not_claim_success(self):
        store = Store("bad_verify")
        state, trace = run(store, "verify", 20)
        self.assertEqual(state, "ESCALATE")
        self.assertEqual(store.value, 20)
        self.assertEqual(trace[-1][1], "verification mismatch")

    def test_exhausted_budget_can_leave_unknown_outcome(self):
        store = Store("timeout")
        state, trace = run(store, "bounded", 20, max_writes=1)
        self.assertEqual(state, "ESCALATE")
        self.assertEqual(store.value, 20)
        self.assertIn(("UNCERTAIN", "bounded:1"), trace)

    def test_reused_key_with_different_request_is_rejected(self):
        store = Store()
        store.put("key", 20, 0)
        with self.assertRaises(KeyReuse):
            store.put("key", 21, 0)
        self.assertEqual(store.effects, 1)

    def test_invalid_target_never_writes(self):
        store = Store()
        state, _ = run(store, "invalid", True)
        self.assertEqual(state, "ESCALATE")
        self.assertEqual(store.effects, 0)

    def test_initial_target_has_observation_claim(self):
        store = Store()
        state, trace = run(store, "already", 10)
        self.assertEqual(state, "DONE")
        self.assertIn(("CLAIM", "OBSERVED_TARGET"), trace)
        self.assertEqual(store.effects, 0)

    def test_written_target_has_only_observation_claim(self):
        store = Store()
        state, trace = run(store, "claim", 20)
        self.assertEqual(state, "DONE")
        self.assertIn(("CLAIM", "OBSERVED_TARGET"), trace)
        self.assertNotIn(("CLAIM", "OPERATION_VERIFIED"), trace)

    def test_target_observed_after_conflict(self):
        class TargetOnConflict(Store):
            def put(self, key, target, expected):
                self.value = target
                self.revision += 1
                raise Conflict()

        store = TargetOnConflict()
        state, trace = run(store, "external", 20)
        self.assertEqual(state, "DONE")
        self.assertIn(("CLAIM", "OBSERVED_TARGET"), trace)
        self.assertEqual(store.effects, 0)


class ReconciliationTests(unittest.TestCase):
    def test_simulated_receipt_loss_can_be_reconciled(self):
        store = Store()
        intent = {"key": "case:1", "target": 20, "expected": 0}

        # Discard the receipt; no process crash or restart occurs.
        store.put(intent["key"], intent["target"], intent["expected"])
        outcome, _ = reconcile(store, intent)

        self.assertEqual(outcome, "RECONCILED")
        self.assertEqual(store.effects, 1)

        missing = {"key": "unknown:1", "target": 20, "expected": 0}
        outcome, _ = reconcile(store, missing)
        self.assertEqual(outcome, "ESCALATE")
        self.assertEqual(store.effects, 1)

    def test_mismatched_operation_record_is_rejected(self):
        store = Store()
        store.put("case:1", 20, 0)
        intent = {"key": "case:1", "target": 21, "expected": 0}

        outcome, reason = reconcile(store, intent)

        self.assertEqual(outcome, "ESCALATE")
        self.assertEqual(reason, "operation record does not match intent")
        self.assertEqual(store.effects, 1)

    def test_later_overwrite_changes_current_state_not_history(self):
        store = Store()
        intent = {"key": "case:1", "target": 20, "expected": 0}
        store.put("case:1", 20, 0)

        historical_result = reconcile(store, intent)
        historical_record = store.completed["case:1"]
        self.assertEqual(historical_result[0], "RECONCILED")

        # A separate, later operation changes the current value.
        store.put("other:1", 15, 1)
        self.assertEqual(store.value, 15)
        self.assertEqual(store.completed["case:1"], historical_record)

        # Earlier reconciliation remains historical evidence; a fresh
        # check cannot establish that the target still persists.
        self.assertEqual(historical_result[0], "RECONCILED")
        current_result = reconcile(store, intent)
        self.assertEqual(current_result[0], "ESCALATE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
