# Examples

Code listings transcribed from the paper:

> **GraphWorkflow: A Low-Overhead Compile-Once Graph Execution Engine for Multi-Agent Systems**
> Kye Gomez · Swarms · August 2026

## Contents

### Side-by-side programming-model comparison (Figure 2)

The same diamond workflow (`analyst → {writer, researcher} → editor`) expressed in each framework's native API for the static-DAG shape.

- [`diamond_graphworkflow.py`](diamond_graphworkflow.py) — Listing (a). Agents are nodes; entry/exit points, compilation, and deep-graph recursion are all inferred.
- [`diamond_langgraph.py`](diamond_langgraph.py) — Listing (b). Requires a typed `State` schema, a reducer for the fan-in, wrapper functions, explicit `START`/`END` wiring, an explicit `compile()`, and a `recursion_limit` override for deep graphs.

### Algorithms (Sections 3.2, 4.3, 4.4, Appendix B)

Pseudocode transcribed from the paper as readable Python. These are **not** production implementations — they are study aids. The real engine lives in `swarms/structs/graph_workflow.py`.

- [`algorithm1_layering.py`](algorithm1_layering.py) — Kahn's algorithm with cyclic remainder (Section 3.2). Cyclic remainders are emitted as a final layer so that validation, not execution, reports the error.
- [`algorithm2_compilation.py`](algorithm2_compilation.py) — The `compile()` pipeline (Section 4.3): entry/exit inference, generations, single-pass adjacency, validation, plan freezing, caching with invalidation.
- [`algorithm3_execution.py`](algorithm3_execution.py) — Layered wavefront execution (Section 4.4): frozen plan, shared lazy pool, inline singleton fast path, as-completed collection with error containment.
- [`algorithm4_fastvalidate.py`](algorithm4_fastvalidate.py) — Structural validation from adjacency maps (Appendix B): `O(N + M)` acyclicity and two multi-source BFS reachability checks.

### Reproduction (Appendix C)

- [`reproduce_benchmarks.sh`](reproduce_benchmarks.sh) — The four-command recipe to run the benchmark suite, run the reducer ablation, regenerate every figure/table/statistic, and build the paper.

## Running the diamond examples

The diamond examples require real LLM credentials and the Swarms / LangGraph packages installed. They are intended to illustrate the API surface, not to run in CI.

```bash
pip install swarms langgraph
# then set your model provider credentials (e.g. OPENAI_API_KEY)
python examples/diamond_graphworkflow.py
python examples/diamond_langgraph.py
```

## Running the benchmark suite

The benchmark harness lives in the Swarms repository under `tests/benchmarks/graph_workflow_benchmarks/`. See [`reproduce_benchmarks.sh`](reproduce_benchmarks.sh) for the exact commands from Appendix C.
