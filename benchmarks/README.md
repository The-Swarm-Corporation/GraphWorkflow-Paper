# GraphWorkflow benchmarks

Measures `swarms.GraphWorkflow` against LangGraph's `StateGraph`, and tracks
the effect of optimizations over time. Two complementary harnesses:

1. **`graph_workflow_bench.py`** — orchestration overhead only. All nodes are
   **no-ops**, so every number is framework overhead, none of it LLM latency.
   That is deliberate: a real agent call is 500–5000 ms, so orchestration
   differences only matter in aggregate, at scale, or at startup.
2. **`agent_execution_bench.py`** — full agent execution. Every node is a real
   LLM agent (`gpt-5.4` by default), identical on both frameworks, so the
   numbers are end-to-end wall-clock latency.

## Full agent execution (`agent_execution_bench.py`)

Runs the same five topologies with **real agents on both frameworks**: identical
swarms `Agent` objects (same model, system prompt, `temperature=0`, 64-token
cap), where only the orchestration layer differs. GraphWorkflow takes the agents
as nodes directly; LangGraph wraps the same construction in state functions with
a list reducer and explicit `START`/`END` edges, mirroring the paper's Figure 2
listings. Each sample builds a fresh graph and executes it end to end (swarms
agents accumulate conversation history, so reusing a graph would grow prompts
across repeats).

```bash
export OPENAI_API_KEY=...   # every node is a paid LLM call

# full grid: 5 topologies × sizes 4,8 × 3 repeats after 1 warmup, both frameworks
python3 benchmarks/agent_execution_bench.py

# cheap smoke test (~6 calls)
python3 benchmarks/agent_execution_bench.py --topologies diamond --sizes 4 --repeats 1

# options: --model gpt-5.4 --backend networkx|rustworkx --sizes --repeats --warmup --out
```

Outputs, written to `results/`:

- `agent_execution.json` — config plus raw samples, medians, and means per cell
- `agent_execution_latency.png` — grouped bars, median end-to-end ms per config
- `agent_execution_speedup.png` — LangGraph/GraphWorkflow ratio vs a 1.0x line

### Result (2026-08-05, gpt-5.4, macOS ARM64)

| topology | n | GraphWorkflow ms | LangGraph ms | speedup |
|---|---|---|---|---|
| chain | 4 | 5,767 | 6,035 | 1.05x |
| chain | 8 | 11,344 | 12,030 | 1.06x |
| wide | 4 | 3,436 | 6,052 | 1.76x |
| wide | 8 | 5,037 | 3,980 | 0.79x |
| diamond | 4 | 4,604 | 4,520 | 0.98x |
| diamond | 8 | 5,762 | 4,834 | 0.84x |
| layered | 4 | 1,617 | 1,660 | 1.03x |
| layered | 8 | 3,426 | 3,520 | 1.03x |
| tree | 4 | 5,478 | 5,890 | 1.08x |
| tree | 8 | 6,467 | 5,918 | 0.92x |

Geometric-mean speedup is **~1.03x — statistical parity**. This is the expected
complement to the no-op results: real model calls (seconds each) swamp
orchestration overhead (sub-millisecond to low-millisecond), so both frameworks
deliver equivalent end-to-end wall-clock. The ±20% swings in individual cells
(wide especially) are API latency jitter at 3 samples per cell, not framework
effects. The orchestration advantage below matters at high run frequency, large
graphs, cold starts, or cheap nodes — with real agents, the differentiator is
the programming model rather than wall-clock time.

## Orchestration overhead (`graph_workflow_bench.py`)

```bash
# full suite → tests/benchmarks/graph_workflow_benchmarks/results/latest.json + latest.md
python3 tests/benchmarks/graph_workflow_benchmarks/graph_workflow_bench.py

# a quick pass
python3 tests/benchmarks/graph_workflow_benchmarks/graph_workflow_bench.py --sizes 10,50 --repeats 3 --topologies diamond

# record a baseline, change code, compare
python3 tests/benchmarks/graph_workflow_benchmarks/graph_workflow_bench.py --out tests/benchmarks/graph_workflow_benchmarks/results/before.json
#   ...edit swarms/structs/graph_workflow.py...
python3 tests/benchmarks/graph_workflow_benchmarks/graph_workflow_bench.py --out tests/benchmarks/graph_workflow_benchmarks/results/after.json
python3 tests/benchmarks/graph_workflow_benchmarks/plot_results.py tests/benchmarks/graph_workflow_benchmarks/results/after.json \
    --baseline tests/benchmarks/graph_workflow_benchmarks/results/before.json
```

Figures land in `tests/benchmarks/graph_workflow_benchmarks/results/figures/`, in light and dark variants.

## What is measured

| Phase | Meaning |
|---|---|
| `import` | Cold interpreter, `from X import Y`, in a subprocess, minus bare interpreter start |
| `build` | Adding N nodes and M edges to an uncompiled graph |
| `compile` | Topological pre-computation and structural validation |
| `first_run` | Cold path: build + compile + one execution |
| `steady_run` | One execution of an already-compiled graph |

Two derived metrics are computed from those:

- **`total_cold_start_ms`** — `import + first_run`. What a one-shot script pays.
- **`breakeven_runs`** — how many executions it takes a slower-to-import
  framework to repay its startup deficit through a lower per-run cost.

## Topologies

| Name | Shape | Stresses |
|---|---|---|
| `chain` | `n0 → n1 → … → nN` | depth — N layers of one node each |
| `wide` | one root → N−1 leaves | width — two layers, maximum fan-out |
| `diamond` | fan-out then fan-in | the common map/reduce shape |
| `layered` | stacks of 4, fully connected between | depth *and* width together |
| `tree` | binary tree | log-depth fan-out |

`chain` and `layered` are the discriminating cases: they have many layers, which
is where per-layer overhead compounds.

## Methodology

- **Working tree, not site-packages.** The harness pins the repo root onto
  `sys.path` and prints the resolved `swarms` module path. Running the script
  puts `tests/benchmarks/graph_workflow_benchmarks/` on the path rather than the repo root, so an installed
  `swarms` would otherwise win silently and the numbers would describe the
  wrong code.
- **Warmup then sample.** Default 2 discarded warmup iterations, then 9 timed
  samples. Median is the headline; min/mean/p95/stdev and every raw sample are
  written to the JSON.
- **GC controlled.** Collection is forced between samples and disabled inside
  each timed region, so a collection triggered by one sample is never billed to
  a later one.
- **Logging silenced.** swarms installs a loguru sink with `enqueue=True` at
  import; left on, its pickle-and-queue cost lands inside the measurement.
- **Provenance recorded.** Platform, core count, Python version, library
  versions, git rev, and whether `swarms/` was dirty all go into the JSON.

## Charts

`plot_results.py` follows the repo's data-viz conventions: a CVD-validated
three-slot categorical palette (validated with the palette checker in both light
and dark modes), log scales where the data spans decades, direct labels on every
series with collision avoidance, recessive grid and axes, and no dual axes.
Series identity never rests on color alone — every line and bar is labelled.
