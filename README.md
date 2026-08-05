# GraphWorkflow: A Low-Overhead Compile-Once Graph Execution Engine for Multi-Agent Systems

<p align="center">
  <em>A reproducible research artifact accompanying the Swarms framework.</em>
</p>

---

## Overview

**GraphWorkflow** is the graph orchestration engine of the open-source [Swarms](https://github.com/kyegomez/swarms) framework. This repository contains the paper, benchmark harness, analysis scripts, and reproduction artifacts for the study:

> **GraphWorkflow: A Low-Overhead Compile-Once Graph Execution Engine for Multi-Agent Systems**
> Kye Gomez · Swarms · August 2026

Multi-agent systems built on large language models (LLMs) are increasingly structured as directed acyclic graphs (DAGs) of agents, where each node performs one model invocation and each edge carries intermediate results. Existing orchestrators (e.g., LangGraph) treat their own overhead as negligible—an assumption that fails in three regimes:

1. **Cold start** of short-lived processes,
2. **High-frequency re-execution** of compiled workflows,
3. **Graphs whose width or depth reaches hundreds of nodes.**

GraphWorkflow addresses these regimes with a **compile-once, sweep-many** design: an explicit compilation phase computes topological generations, materializes adjacency maps in a single pass, validates the graph structurally, and freezes a per-layer execution plan of resolved `(node, agent)` tuples. The runtime then executes each layer as a wavefront over a single lazily created thread pool, with an inline fast path for single-node layers.

---

## Key Results

Against **LangGraph 1.0.4** across 15 topology–size configurations (5 topologies × 3 sizes, with no-op agents so every measured microsecond is framework overhead):

| Phase | GraphWorkflow (networkx) | GraphWorkflow (rustworkx) |
| :--- | :---: | :---: |
| Build (geomean speedup) | **2.4×** | **2.7×** |
| Compile (geomean speedup) | **21.6×** | **31.3×** |
| First run / cold path (geomean) | **7.9×** | **8.7×** |
| Steady-state run (geomean) | **7.0×** | **7.2×** |
| Steady-state run (max, 200-node chain) | **62.5×** | **55.9×** |

- 200-node chain: GraphWorkflow executes in **0.29 ms** vs. LangGraph's **18.15 ms**.
- 200-node compile: GraphWorkflow in **0.26–0.44 ms** vs. LangGraph's **12.57 ms**.
- Per-node inline dispatch cost: **≈ 1.5 μs** (GraphWorkflow) vs. **≈ 90.7 μs** per superstep (LangGraph).

---

## Contributions

The paper makes four contributions:

1. **A cost taxonomy for agent orchestration** — four measurable lifecycle phases (build, compile, first run, steady run) and a per-node plus per-layer overhead model that turns benchmark topologies into probes of individual mechanisms.
2. **The design of a compile-once graph engine** — a backend abstraction, a compilation pipeline with single-pass adjacency materialization and validation by multi-source reachability, a frozen execution plan, and a layer-wavefront scheduler with a shared lazy thread pool and an inline single-node fast path; plus per-layer checkpointing, nested subgraphs, and multi-loop refinement.
3. **A formal account of the execution model** — layered execution respects dependency order, compilation is `O(V + E)`, and the layer-barrier runtime connects to work-span scheduling bounds.
4. **A reproducible evaluation** — harness, raw samples, analysis scripts, and figures are released; results are medians of 9 samples with 95% confidence intervals, and each measured gap is attributed to a specific architectural cause.

---

## Architecture

GraphWorkflow separates the graph lifecycle into an explicit **compilation phase** and a minimal **execution phase**. Construction mutates declarative state and the backend graph; `compile()` distills both into cached artifacts; the run engine touches only the frozen execution plan and the predecessor map, never the backend.

```
construction & lifecycle API          declarative state              compiled artifacts (cached)
add_node / add_edge                   nodes: Dict[str, Node]          _sorted_layers
add_edges_from_source                 edges: List[Edge]              _execution_plan (frozen tuples)
add_parallel_chain                     entry / end points             succ. / pred. maps
from_spec / to_json                    ─────────────                  ─────────────
compile()                              GraphBackend interface         execution engine (backend-free)
run / arun                             (add_node, add_edge,           layer sweep, frozen plan
                                       degrees, predecessors,        shared lazy pool
                                       generations, descendants,     min(p, max_i |L_i|)
                                       is_dag, adjacency)            inline path (|L_i| = 1)
                                              │                              │
                                       ┌──────────────┴──────────────┐  outputs + conversation
                                       NetworkXBackend   RustworkxBackend  per-layer checkpoints
                                       (nx.DiGraph)      (PyDiGraph)       callbacks, streaming
```

### Design Requirements

- **(R1)** Per-run overhead must not scale with anything but the work actually dispatched — no per-run graph traversal or state machinery.
- **(R2)** All analysis that can be hoisted out of the run loop must be, behind an explicit, cached, invalidation-safe compile step.
- **(R3)** Concurrency must exploit I/O-bound parallelism without paying thread-pool construction per layer.
- **(R4)** The engine must not be married to one graph library; algorithmic backends improve independently of orchestration.
- **(R5)** Reliability features (validation, checkpointing, callbacks) must be pay-for-use, costing nothing when disabled.

### Compilation Pipeline

1. **Entry/exit inference** from node degrees.
2. **Topological generations** via Kahn's algorithm (native in `rustworkx`).
3. **Single-pass adjacency materialization** — successor and predecessor maps in one iteration over the edge list.
4. **Structural validation** — degree checks, `O(N+M)` acyclicity test, multi-source BFS reachability from entries and exits.
5. **Frozen execution plan** — each node resolved to `(id, agent, type, display_name)` per layer; no dictionary lookups on the hot path.
6. **Caching with explicit invalidation** — every mutator clears the compiled flag; `compile()` is a no-op when nothing changed.

### Scheduler

- **No per-run graph work** — the run loop never touches the backend.
- **One pool per run, created lazily, sized to the widest layer** — `min(p, max_i |L_i|)`, default `p = ⌊0.95 · cores⌋`.
- **Inline execution of singleton layers** — eliminates pool handoff on chains and other single-node layers.
- **As-completed collection with error containment** — a slow node does not delay siblings; a failing node is recorded as a tagged error string and the run continues.
- **Pay-for-use hooks** — per-node and per-token callbacks are bound only when registered.

---

## Theoretical Foundations

- **Workflow graph** `G = (V, E)` with agent assignment `a: V → A`. Entry points have `pred(v) = ∅`; exit points have `succ(v) = ∅`.
- **Topological generations** partition `V` into layers `L_0, …, L_{d-1}` with `d(u) < d(v)` for every edge `(u, v)`.
- **Layered wavefront schedule** executes layers in index order with a per-layer barrier; node `v` receives `{y_u : u ∈ pred(v)}` and produces `y_v = a(v)(π(τ, {y_u}))`.
- **Proposition 1 (Dependency Safety)** — every node begins only after all predecessors complete; reads cannot observe partial or stale values.
- **Theorem 1 (Compilation Complexity)** — compilation runs in `O(N + M)` time and space.
- **Work-span cost model** — `T_p^barrier = Σ_i (max_{v ∈ L_i} t_v + β_i)` when `p ≥ max_i |L_i|`; for unit-time nodes the barrier schedule is span-optimal whenever layers are internally balanced.
- **Steady-run overhead model** — `Ω(N, d) ≈ α_node · N + α_layer · d + α_0`.

---

## Programming Model Comparison

The same diamond workflow (analyst → {writer, researcher} → editor) expressed in both frameworks highlights the API obligations each imposes on the static-DAG common case:

| Obligation | GraphWorkflow | LangGraph |
| :--- | :--- | :--- |
| Node definition | agent object itself | function over typed state |
| Shared-state schema | none | `TypedDict` required |
| Fan-in merge policy | automatic (predecessor map) | reducer annotation required |
| Predecessor context | assembled by the engine | read from state by user code |
| Entry / exit points | inferred from degrees | explicit `START`/`END` edges |
| Compilation | implicit on first run | explicit `compile()` |
| Deep graphs (`d > 25`) | no configuration | raise `recursion_limit` |
| Result form | dict keyed by node | shared channels, merged by reducer |

```python
from swarms import Agent, GraphWorkflow

analyst    = Agent(agent_name="Analyst",    model_name="gpt-5.4")
writer     = Agent(agent_name="Writer",     model_name="gpt-5.4")
researcher = Agent(agent_name="Researcher", model_name="gpt-5.4")
editor     = Agent(agent_name="Editor",     model_name="gpt-5.4")

wf = GraphWorkflow()
for a in (analyst, writer, researcher, editor):
    wf.add_node(a)
wf.add_edge(analyst, writer)
wf.add_edge(analyst, researcher)
wf.add_edge(writer, editor)
wf.add_edge(researcher, editor)

results = wf.run("Produce a market report.")
# {"Analyst": ..., "Writer": ..., "Researcher": ..., "Editor": ...}
```

---

## Experimental Methodology

### Harness

All measurements come from an open harness under `tests/benchmarks/graph_workflow_benchmarks/` that measures the four lifecycle phases for three implementations: GraphWorkflow over NetworkX, GraphWorkflow over `rustworkx`, and LangGraph's `StateGraph`. Every node is a no-op function, so measured time is orchestration overhead by construction.

- **Sampling:** 2 discarded warmups, then 9 timed samples per cell; medians reported with 95% confidence intervals (Student's *t*, 8 d.f.); means, std devs, and all raw samples in the released JSON.
- **GC control:** collector forced between samples and disabled inside each timed region.
- **Logging silenced:** Swarms' enqueueing loguru sink is disabled to keep pickle-and-queue cost out of timed regions.
- **Working-tree pinning:** the repository root is pinned on `sys.path` so numbers describe the checked-out code.
- **Provenance:** platform, core count, Python/library versions, git revision, and dirty-tree status are recorded.

### Environment

- macOS 15.7.7 arm64 (12 cores), Python 3.12.3
- swarms 14.0.0 (revision `daa3368f`, clean tree)
- langgraph 1.0.4 · networkx 3.5 · rustworkx 0.17.1

### Topology Suite

Five topologies at `N ∈ {10, 50, 200}` nodes are chosen to separate the coefficients of the overhead model:

| Topology | Depth `d` | Probes |
| :--- | :--- | :--- |
| **Chain** | `N` | per-layer cost; discriminating case for superstep runtimes |
| **Wide** | 2 | per-node dispatch cost; concurrency path |
| **Diamond** | 3 | common map-reduce fan-out/fan-in shape |
| **Layered** | `⌈N/4⌉` | depth and width together (densest edge count) |
| **Tree** | `⌊log₂ N⌋ + 1` | logarithmic depth, geometric width growth |

### Fairness Controls

- Both frameworks execute identical topologies, node-for-node and edge-for-edge, through their native construction APIs.
- LangGraph's default 25-superstep recursion cap is raised so deep graphs complete.
- Fan-in nodes use an appending list reducer (matching GraphWorkflow's inherent retention); an `O(1)` counter-reducer ablation is also reported.
- No checkpointer is configured for LangGraph (its default); GraphWorkflow runs single-loop with checkpointing disabled.

---

## Reproduction

All artifacts live in the Swarms repository under `tests/benchmarks/graph_workflow_benchmarks/`.

```bash
# 1. Run the full benchmark suite (writes results/latest.json + latest.md)
python3 tests/benchmarks/graph_workflow_benchmarks/graph_workflow_bench.py

# 2. Reducer ablation (O(1) counter reducer for LangGraph fan-in state)
python3 tests/benchmarks/graph_workflow_benchmarks/graph_workflow_bench.py \
  --lg-reducer counter \
  --out .../results/langgraph_counter_reducer.json

# 3. Regenerate every figure, table, and statistic in the paper
python3 tests/benchmarks/graph_workflow_benchmarks/graphworkflow_paper/analysis/analyze.py

# 4. Build the paper
cd tests/benchmarks/graph_workflow_benchmarks/graphworkflow_paper
tectonic main.tex        # or: latexmk -pdf main.tex
```

The analysis script consumes only the two result JSON files; every number in the text is emitted as a LaTeX macro by the same script (`tables/stats.tex`), so the paper cannot silently drift from the data.

### Statistical Conventions

- Reported values are **medians of `n = 9` samples** after 2 warmups.
- Intervals are **95% confidence intervals** on the mean using Student's *t* with 8 degrees of freedom.
- Aggregate speedups are **geometric means** of per-cell median ratios.
- Raw samples for every cell and full environment provenance are preserved in the JSON files.

---

## Discussion & Limitations

### What the numbers do and do not claim

The evaluation measures **orchestration overhead on static DAGs of no-op nodes**. It does not measure end-to-end agent quality, token throughput, or behavior under real LLM latency, where a 500 ms node renders both frameworks' per-node overhead invisible in any single execution. GraphWorkflow is one to two orders of magnitude cheaper at every measured phase of the graph lifecycle, with the gap widest exactly where overhead compounds: deep graphs, high execution rates, and repeated construction.

### Concurrency ceiling

The scheduler is thread-based and in-process — appropriate for I/O-bound agent calls on current CPython (the GIL is released during network waits), but it caps CPU-bound node work and offers no horizontal scale-out. The layer barrier also forfeits parallelism when node durations within a layer are skewed.

### Benchmark scope

- Suite tops out at 200 nodes; neither memory behavior nor scheduler behavior at `10³–10⁴`-node scale is characterized.
- Only synchronous entry points are measured (`arun` currently delegates to a thread).
- All numbers come from one machine, one Python version, and one OS; cross-platform replication, peak-RSS, allocation counts, and CPU-utilization traces are flagged as the most valuable missing measurements.

---

## Future Directions

Five directions follow naturally from the compile-once design:

1. **Distributed execution** — the compiled plan is a plain layered list of picklable specifications; partitioning layers across processes or machines, with the output map as the only shared state, is a natural extension.
2. **Heterogeneous and GPU-aware scheduling** — compile-time resource-class annotations plus per-class pools would extend the single-pool model without touching the sweep.
3. **Compiler-assisted optimization** — the compile phase is the hook for fusing linear chains, batching sibling calls to one model endpoint, and precomputing prompt skeletons.
4. **Dynamic rewriting** — compiling guard nodes into alternative sub-plans would close part of the expressiveness gap with LangGraph while preserving the static hot path.
5. **Scale** — pushing the suite to `10³–10⁴` nodes, where the `O(N + M)` compile bound predicts, but does not yet demonstrate, continued linearity.

---

## Related Work

- **Workflow managers:** Airflow, Prefect — durable cross-machine state at per-task latencies of `10²–10³` ms.
- **Dataflow / task-parallel systems:** Dask (~100–200 μs per task), Ray (compiled task graphs over a distributed object store), Pregel and the BSP model that inspired LangGraph.
- **Graph libraries:** NetworkX and `rustworkx` supply the algorithmic substrate; GraphWorkflow's contribution is the backend abstraction that makes them interchangeable beneath an execution engine, plus the compile-once discipline that keeps them off the hot path.
- **Classical algorithms:** Kahn's topological sort, Johnson's cycle enumeration (deliberately avoided on the common path), and the work-span scheduling theory of Graham, Brent, and Blumofe & Leiserson.

---

## Citation

```bibtex
@misc{gomez2026graphworkflow,
  title        = {GraphWorkflow: A Low-Overhead Compile-Once Graph Execution
                  Engine for Multi-Agent Systems},
  author       = {Kye Gomez},
  year         = {2026},
  month        = aug,
  howpublished = {Swarms framework technical report},
  url          = {https://github.com/kyegomez/swarms}
}
```

---

## License

This artifact is released as part of the [Swarms](https://github.com/kyegomez/swarms) framework. See the upstream repository for license details.

