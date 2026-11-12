"""Canonical deterministic route and recovery laboratory.

Run: python3 route_lab.py
No network, language model, real clock, or physical actuator is used.
"""

import math
import unittest
from heapq import heappop, heappush
from itertools import count

# Operational example: all values and behaviours are hypothetical.
EDGES = {
    "S": [("A", 1), ("B", 2)],
    "A": [("C", 1), ("G", 8)],
    "B": [("C", 1), ("G", 7)],
    "C": [("G", 2)],
    "G": [],
}
COST = {(u, v): c for u, edges in EDGES.items() for v, c in edges}
TTL = 5

# Earlier route example, retained to test equal-cost alternatives.
LEGACY_GRAPH = {
    "S": [("A", 1), ("B", 2)],
    "A": [("C", 2), ("G", 8)],
    "B": [("C", 1), ("G", 7)],
    "C": [("G", 2)],
    "G": [],
}


def uniform_cost(graph, start, goal, blocked=frozenset()):
    """Return (cost, path), or None for an unreachable goal.

    The supplied graph must be finite and have finite, non-negative costs.
    A blocked edge is an ordered pair (source, destination).
    """
    for edges in graph.values():
        for _, edge_cost in edges:
            if not math.isfinite(edge_cost) or edge_cost < 0:
                raise ValueError("Costs must be finite and non-negative")

    serial = count()
    frontier = [(0, next(serial), start, (start,))]
    best = {start: 0}

    while frontier:
        cost, _, node, path = heappop(frontier)
        if cost != best.get(node):
            continue
        if node == goal:
            return cost, path

        for nxt, edge_cost in graph.get(node, []):
            if (node, nxt) in blocked:
                continue
            new_cost = cost + edge_cost
            if new_cost < best.get(nxt, float("inf")):
                best[nxt] = new_cost
                heappush(
                    frontier,
                    (new_cost, next(serial), nxt, path + (nxt,)),
                )
    return None


def usable_door(observation, now):
    """Apply the simulated freshness rule to a (status, time) pair."""
    status, observed_at = observation
    return status == "open" and 0 <= now - observed_at <= TTL


def planning_graph(observation, now, blocked=frozenset()):
    """Exclude rejected edges and the door unless its report is usable."""
    door_allowed = usable_door(observation, now)
    return {
        u: [
            (v, cost) for v, cost in edges
            if (u, v) not in blocked
            and ((u, v) != ("A", "C") or door_allowed)
        ]
        for u, edges in EDGES.items()
    }


class Facility:
    """Deterministic teaching simulation, not a production actuator."""

    def __init__(
        self, observation_mode="normal", race=False, plan_delay=0,
        rejected_edges=(), timeout_edge=None
    ):
        self.position = "S"
        self.door_open = True
        self.observation_mode = observation_mode
        self.race = race
        self.plan_delay = plan_delay
        self.rejected_edges = set(rejected_edges)
        self.timeout_edge = timeout_edge
        self.now = 0
        self.moves = []
        self.rejections = []
        self.events = []

    def observe(self):
        if self.observation_mode == "stale":
            return ("open", self.now - 20)
        if self.observation_mode == "unknown":
            return ("unknown", self.now)
        return ("open" if self.door_open else "closed", self.now)

    def execute(self, destination):
        """Return (classification, reason); only 'ok' confirms a move."""
        source = self.position
        edge = (source, destination)

        if edge not in COST:
            self.rejections.append((edge, "invalid edge"))
            return ("rejected", "invalid edge")

        if edge == ("A", "C") and self.race:
            self.door_open = False
            self.race = False

        if edge == ("A", "C") and not self.door_open:
            self.rejections.append((edge, "door closed"))
            return ("rejected", "door closed")

        if edge in self.rejected_edges:
            self.rejections.append((edge, "actuator rejected"))
            return ("rejected", "actuator rejected")

        if edge == self.timeout_edge:
            # The simulated action occurs, but its response is lost.
            # The controller must not infer this from the timeout.
            self.position = destination
            return ("unknown", "timeout")

        self.position = destination
        self.moves.append((source, destination, COST[edge]))
        return ("ok", "confirmed")


def run_agent(facility, goal="G", max_attempts=10):
    """Return (status, confirmed_cost), preserving distinct failures.

    Each loop iteration consumes one attempt, including an expired check
    or a rejected action. Rejected edges are excluded for this run.
    """
    blocked = set()

    def finish(status):
        cost = sum(c for _, _, c in facility.moves)
        facility.events.append(("final", status, cost))
        return (status, cost)

    for _ in range(max_attempts):
        if facility.position == goal:
            return finish("arrived")

        observation = facility.observe()
        facility.events.append(
            ("observation", observation, facility.now)
        )
        graph = planning_graph(observation, facility.now, blocked)
        result = uniform_cost(graph, facility.position, goal)
        if result is None:
            return finish("no_route")

        _, path = result
        source = facility.position
        destination = path[1]
        edge = (source, destination)
        facility.events.append(("plan", path, facility.now))

        # Deterministic time passes after planning and before execution.
        facility.now += facility.plan_delay
        if edge == ("A", "C") and not usable_door(
            observation, facility.now
        ):
            facility.events.append(("expired", edge, facility.now))
            continue

        facility.events.append(("attempt", edge, facility.now))
        classification, reason = facility.execute(destination)
        facility.events.append(("response", edge, classification, reason))

        if classification == "ok":
            continue
        if classification == "unknown":
            # A production system would query the original operation ID.
            # This simulation has no reconciliation protocol: stop.
            return finish("uncertain_execution")

        # A rejection confirms no move in this simulation. Refresh on the
        # next iteration and prevent the same edge being tried repeatedly.
        if facility.position != source:
            return finish("uncertain_execution")
        blocked.add(edge)
        facility.events.append(("replan", edge, reason))

    if facility.position == goal:
        return finish("arrived")
    return finish("budget_exhausted")


class RouteLabTests(unittest.TestCase):
    def test_legacy_normal(self):
        self.assertEqual(
            uniform_cost(LEGACY_GRAPH, "S", "G"),
            (5, ("S", "A", "C", "G")),
        )

    def test_legacy_blocked(self):
        self.assertEqual(
            uniform_cost(LEGACY_GRAPH, "S", "G", {("C", "G")}),
            (9, ("S", "A", "G")),
        )

    def test_legacy_no_route(self):
        blocked = {("A", "G"), ("B", "G"), ("C", "G")}
        self.assertIsNone(uniform_cost(LEGACY_GRAPH, "S", "G", blocked))

    def test_negative_cost_rejected(self):
        with self.assertRaises(ValueError):
            uniform_cost({"S": [("G", -1)], "G": []}, "S", "G")

    def test_normal(self):
        f = Facility()
        self.assertEqual(run_agent(f), ("arrived", 4))
        self.assertEqual(
            f.moves, [("S", "A", 1), ("A", "C", 1), ("C", "G", 2)]
        )
        self.assertEqual(f.rejections, [])

    def test_stale(self):
        f = Facility(observation_mode="stale")
        self.assertEqual(run_agent(f), ("arrived", 5))
        self.assertEqual(
            f.moves, [("S", "B", 2), ("B", "C", 1), ("C", "G", 2)]
        )
        self.assertEqual(f.rejections, [])

    def test_unknown(self):
        f = Facility(observation_mode="unknown")
        self.assertEqual(run_agent(f), ("arrived", 5))
        self.assertEqual(
            f.moves, [("S", "B", 2), ("B", "C", 1), ("C", "G", 2)]
        )
        self.assertEqual(f.rejections, [])

    def test_door_closes_after_planning(self):
        f = Facility(race=True)
        self.assertEqual(run_agent(f), ("arrived", 9))
        self.assertEqual(f.moves, [("S", "A", 1), ("A", "G", 8)])
        self.assertEqual(f.rejections, [(("A", "C"), "door closed")])
        self.assertIn(("replan", ("A", "C"), "door closed"), f.events)

    def test_disconnected_graph(self):
        self.assertIsNone(uniform_cost({"S": [], "G": []}, "S", "G"))

    def test_freshness_boundary_and_future(self):
        self.assertTrue(usable_door(("open", 5), now=10))
        self.assertFalse(usable_door(("open", 4), now=10))
        self.assertFalse(usable_door(("open", 11), now=10))

    def test_expiry_between_plan_and_execution(self):
        f = Facility(plan_delay=TTL + 1)
        self.assertEqual(run_agent(f, max_attempts=3), ("budget_exhausted", 1))
        self.assertEqual(f.moves, [("S", "A", 1)])
        self.assertTrue(any(event[0] == "expired" for event in f.events))
        self.assertNotIn(("A", "C", 1), f.moves)

    def test_rejection_with_no_safe_alternative(self):
        f = Facility(rejected_edges={("A", "C"), ("A", "G")})
        self.assertEqual(run_agent(f), ("no_route", 1))
        self.assertEqual(f.position, "A")
        self.assertEqual(
            f.rejections,
            [(("A", "C"), "actuator rejected"),
             (("A", "G"), "actuator rejected")],
        )

    def test_timeout_is_not_retried(self):
        f = Facility(timeout_edge=("S", "A"))
        self.assertEqual(run_agent(f), ("uncertain_execution", 0))
        attempts = [event for event in f.events if event[0] == "attempt"]
        self.assertEqual(len(attempts), 1)
        self.assertEqual(f.moves, [])

    def test_attempt_budget(self):
        f = Facility()
        self.assertEqual(run_agent(f, max_attempts=1), ("budget_exhausted", 1))
        self.assertEqual(f.position, "A")

    def test_final_attempt_can_arrive(self):
        f = Facility()
        self.assertEqual(run_agent(f, max_attempts=3), ("arrived", 4))


if __name__ == "__main__":
    unittest.main(verbosity=2)
