# GraphWorkflow benchmarks

Measures `swarms.GraphWorkflow` orchestration overhead against LangGraph's
`StateGraph`, and tracks the effect of optimizations over time.

All nodes are **no-ops**. Every number here is framework overhead — none of it
is LLM latency. That is deliberate: a real agent call is 500–5000 ms, so
orchestration differences only matter in aggregate, at scale, or at startup.

## Running

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
