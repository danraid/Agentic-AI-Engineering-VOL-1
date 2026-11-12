# Additional Python excerpts

## Excerpt 1

```python
from route_lab import EDGES, uniform_cost

graph = {node: list(edges) for node, edges in EDGES.items()}
graph["A"] = [("C", 5), ("G", 8)]

result = uniform_cost(graph, "S", "G")
assert result == (5, ("S", "B", "C", "G"))
print(result)
```
