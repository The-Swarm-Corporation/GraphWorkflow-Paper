# GraphWorkflow: A Low-Overhead Compile-Once Graph Execution Engine for Multi-Agent Systems

![Graphworkflow Image](img.jpeg)

[![GraphWorkflow source](https://img.shields.io/badge/GraphWorkflow-Source-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/kyegomez/swarms/blob/master/swarms/structs/graph_workflow.py)
[![Swarms GitHub](https://img.shields.io/badge/Swarms-GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/kyegomez/swarms)
[![Swarms website](https://img.shields.io/badge/Website-swarms.ai-0A84FF?style=for-the-badge&logo=safari&logoColor=white)](https://swarms.ai)
[![Discord](https://img.shields.io/badge/Discord-Join%20Community-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/SSj7FyRSwy)

[Read the full paper (PDF)](./main.pdf) | [Explore the examples](./examples/) | [Inspect the benchmarks](./benchmarks/)



Kye Gomez, Adi Chaudhary, Ayaan Gazali, and Steve-Dusty Wyatt Stanke  
Swarms, November 2026  
Correspondence: [kye@swarms.world](mailto:kye@swarms.world)

GraphWorkflow is the graph orchestration engine in the open-source [Swarms](https://github.com/kyegomez/swarms) framework. It is designed for static directed acyclic graphs of agents that are compiled once and executed many times. Compilation performs structural analysis, validation, adjacency materialization, and execution-plan generation. Runtime execution then sweeps the frozen plan with minimal orchestration work.

This repository contains the paper, companion code examples, benchmark harness, raw benchmark samples, and generated result summaries.

## Abstract

Large language model agent workflows are often represented as directed acyclic graphs, where nodes invoke agents and edges carry intermediate results. Framework overhead can become significant during cold starts, repeated execution, and workflows containing hundreds of nodes.

GraphWorkflow uses a compile-once, sweep-many architecture. Its compilation phase computes topological generations, materializes adjacency maps in one pass, validates graph structure, and freezes a layer-by-layer execution plan. The runtime executes that plan as a wavefront over one lazily created thread pool, with an inline fast path for layers containing a single node. A backend interface supports both NetworkX and the Rust-based rustworkx library while keeping backend operations off the runtime hot path.

Across 15 benchmark configurations covering five graph topologies and sizes from 10 to 200 nodes, GraphWorkflow achieved:

- **5.9x geometric-mean steady-state speedup** over LangGraph 1.0.4 with the NetworkX backend (6.2x with rustworkx), or **7.8x** with the worker pool capped at the core count
- **Up to 60.2x faster steady-state execution** on a 200-node chain
- **22.9x to 35.0x faster compilation**
- **7.0x to 7.6x faster first-run execution**, including build, compile, and one run
- **1.26x faster cold import** than LangGraph (231 ms vs 291 ms), down from 1,584 ms in swarms 14.0.0, a 6.9x reduction

These figures are for swarms 17.0.0. All no-op measurements isolate orchestration overhead rather than model latency. With real LLM agents (gpt-5.4) both frameworks reach end-to-end parity, because model time dominates.

#### What changed since swarms 14.0.0

The harness, machine, and LangGraph version are unchanged, so the numbers compare directly with the August release:

- **Import:** cold `GraphWorkflow` import fell from 1,584 ms to 231 ms because networkx, rustworkx, and graphviz now load lazily. Total cold start (import plus first run) now favors GraphWorkflow by 1.27x to 1.42x in every cell, where in swarms 14.0.0 LangGraph led by more than a second.
- **Narrow and deep graphs:** steady runs are 17% faster (geometric mean) on cells whose layers fit within the core count. That is consistent with the cheaper input assembly: predecessor outputs are now passed as chat messages rather than concatenated into one prompt string.
- **Wide layers:** the default worker pool is now as wide as the widest layer, where it used to be 95% of the cores. With no-op nodes this costs time; for example, wide-200 takes 5.1 ms versus 2.1 ms before. With real network-bound agents, the trade goes the other way: a 50-way fan-out is no longer split into ⌈50/11⌉ = 5 sequential waves of model calls on a 12-core machine. Passing `max_parallel_nodes=11` restores the old bound and brings wide-200 down to 1.7 ms.
- **Unchanged:** build and compile cost stay the same within noise, because the compile pipeline itself did not change.

## Core Contributions

### Compile-once execution

GraphWorkflow moves reusable graph analysis out of the run loop. Compilation:

1. Infers entry and exit nodes from graph degrees.
2. Computes topological generations with linear complexity.
3. Materializes successor and predecessor maps in one edge-list pass.
4. Validates acyclicity, reachability, executables, and graph structure.
5. Resolves each node into a frozen per-layer execution plan.
6. Caches compiled artifacts until a graph mutation invalidates them.

Compilation runs in `O(N + M)` time and space for `N` nodes and `M` edges.

### Low-overhead scheduling

The runtime does not traverse the graph or consult the selected graph backend. It executes the precomputed layers directly:

- Singleton layers run inline on the caller thread.
- Parallel layers share one lazily created thread pool per run.
- The pool is as wide as the widest layer by default (swarms 17+), so network-bound siblings all run at once; `max_parallel_nodes` sets a cap.
- Results are collected as tasks complete.
- Errors are contained as node outputs so sibling work can finish.
- Checkpoints and callbacks are pay-for-use features.

### Pluggable graph backends

The same workflow can use:

- **NetworkX**, the default Python graph implementation
- **rustworkx**, an optional Rust-backed implementation that accelerates graph analysis

The backend affects graph construction and compilation only. Once compiled, execution uses the same backend-independent frozen plan.

### Simpler static-DAG programming model

For static agent workflows, GraphWorkflow treats agents as nodes and edges as dataflow. Compared with the equivalent LangGraph example, it does not require:

- A shared typed-state schema
- Reducer annotations for fan-in
- Wrapper functions around every agent
- Explicit `START` and `END` edges
- An explicit compilation call before execution
- A recursion-limit override for deep graphs

This design is intentionally scoped to static DAGs. Workflows requiring conditional edges, runtime cycles, mid-graph interrupts, or general durable superstep execution may be better served by LangGraph.

## Architecture

The workflow lifecycle has three states:

1. **Construction:** nodes, edges, runtime options, and backend graph state are mutable.
2. **Compilation:** graph structure is converted into cached layers, adjacency maps, and resolved execution tuples.
3. **Execution:** the runtime sweeps the frozen plan and reads predecessor outputs without calling the graph backend.

Any structural mutation invalidates compiled artifacts. The next `compile()` or `run()` safely regenerates them.

The scheduler follows a layered wavefront model. All nodes in one topological generation may execute concurrently, and the next generation starts after the current layer completes. This preserves dependency order while exposing the parallelism of each layer.

## Evaluation

The benchmark suite measures four lifecycle phases:

- **Build:** construct nodes and edges.
- **Compile:** validate and prepare the execution plan.
- **First run:** build, compile, and execute once.
- **Steady run:** execute an already compiled workflow.

Five topology families isolate different sources of overhead:

- **Chain:** maximum depth and one node per layer
- **Wide:** one root with many leaves
- **Diamond:** fan-out followed by fan-in
- **Layered:** densely connected stages of four nodes
- **Tree:** binary-tree depth with increasing width

Each topology is measured at 10, 50, and 200 nodes. The reported values are medians of 9 timed samples after 2 warmups. The paper also reports means, standard deviations, 95% confidence intervals, raw samples, and environment provenance.

Headline results against LangGraph 1.0.4:

- GraphWorkflow compilation is 22.9x faster with NetworkX and 35.0x faster with rustworkx by geometric mean.
- The complete cold path is 7.0x faster with NetworkX and 7.6x faster with rustworkx.
- Compiled steady-state execution is 5.9x faster with NetworkX and 6.2x faster with rustworkx, or 7.8x and 7.9x with the pool capped at 11 workers.
- A 200-node chain runs in 0.28 ms on GraphWorkflow with NetworkX and 17.14 ms on LangGraph, a 60.2x difference.
- At 200 nodes, GraphWorkflow overhead ranges from roughly 0.3 to 5.3 ms per run, while LangGraph ranges from roughly 17 to 24 ms.
- Cold import of `GraphWorkflow` takes 231 ms, compared with 291 ms for LangGraph's `StateGraph`.

The paper attributes these differences to frozen-plan execution, the singleton-layer inline path, one shared pool, and the absence of channel and superstep machinery on the static-DAG hot path.

The complete benchmark artifacts are included in [`benchmarks/`](./benchmarks/). This makes it possible to inspect the harness, methodology, provenance, raw samples, and generated summaries without extracting them from the paper.

## Code Examples

The [`examples`](./examples/) directory contains companion artifacts from the paper:

- [`diamond_graphworkflow.py`](./examples/diamond_graphworkflow.py) contains Figure 2(a), the diamond workflow implemented with GraphWorkflow.
- [`diamond_langgraph.py`](./examples/diamond_langgraph.py) contains Figure 2(b), the same workflow implemented with LangGraph 1.0.4.
- [`reproduce_benchmarks.sh`](./examples/reproduce_benchmarks.sh) contains the Appendix C command sequence for running the benchmark suite, reducer ablation, analysis, and paper build.
- [`examples/README.md`](./examples/README.md) provides additional notes about the listings.

The diamond topology is:

```text
              writer
             /      \
analyst ----          ---- editor
             \      /
            researcher
```

The listings are intended as a direct programming-model comparison. They use real agent calls and therefore require appropriate model-provider credentials.

## Running the GraphWorkflow Example

Install Swarms:

```bash
pip install swarms
```

Set the credentials required by the model configured in the example, then run:

```bash
python examples/diamond_graphworkflow.py
```

The workflow returns a dictionary keyed by node name:

```python
{
    "Analyst": "...",
    "Writer": "...",
    "Researcher": "...",
    "Editor": "...",
}
```

To study the corresponding LangGraph construction, see [`diamond_langgraph.py`](./examples/diamond_langgraph.py). That listing focuses on the framework-specific graph and state setup shown in the paper and assumes the four agent objects have already been created.

## Benchmark Artifacts

The [`benchmarks`](./benchmarks/) directory includes:

- [`benchmarks/README.md`](./benchmarks/README.md), which documents measured phases, topology definitions, methodology, fairness controls, and known limitations
- [`graph_workflow_bench.py`](./benchmarks/graph_workflow_bench.py), the benchmark harness used to compare GraphWorkflow with LangGraph
- [`plot_results.py`](./benchmarks/plot_results.py), the script used to render benchmark figures
- [`results/latest.json`](./benchmarks/results/latest.json), containing raw samples, aggregate statistics, and environment provenance for the headline evaluation
- [`results/latest.md`](./benchmarks/results/latest.md), a readable summary of the complete result grid
- [`results/langgraph_counter_reducer.json`](./benchmarks/results/langgraph_counter_reducer.json), containing the raw counter-reducer ablation
- [`results/langgraph_counter_reducer.md`](./benchmarks/results/langgraph_counter_reducer.md), containing the readable ablation summary
- [`results/swarms_capped_workers.json`](./benchmarks/results/swarms_capped_workers.json), the GraphWorkflow sweep with `max_parallel_nodes=11` (the swarms 14.0.0 default bound on this machine)
- [`results/swarms-14.0.0_2026-08-05/`](./benchmarks/results/swarms-14.0.0_2026-08-05/), the archived swarms 14.0.0 results used for the release comparison
- [`agent_execution_bench.py`](./benchmarks/agent_execution_bench.py) and [`results/agent_execution.json`](./benchmarks/results/agent_execution.json), the end-to-end run with real LLM agents

The harness measures import, build, compile, first-run, and steady-run costs. It also derives total cold-start latency and the number of repeated executions required to offset an import-time disadvantage. Import timing uses a fresh subprocess and subtracts bare Python interpreter startup.

## Reproducing the Benchmarks

The benchmark harness is maintained in the main [Swarms repository](https://github.com/kyegomez/swarms) under:

```text
tests/benchmarks/graph_workflow_benchmarks/
```

Run the benchmark from a Swarms checkout so the harness measures the checked-out `swarms` source rather than an unrelated installed package:

```bash
# Run the complete benchmark suite
python3 tests/benchmarks/graph_workflow_benchmarks/graph_workflow_bench.py

# Run the LangGraph O(1) counter-reducer ablation
python3 tests/benchmarks/graph_workflow_benchmarks/graph_workflow_bench.py \
  --lg-reducer counter --impls langgraph --skip-imports \
  --out tests/benchmarks/graph_workflow_benchmarks/results/langgraph_counter_reducer.json

# Run the worker-cap ablation (the swarms 14.0.0 default bound)
python3 tests/benchmarks/graph_workflow_benchmarks/graph_workflow_bench.py \
  --impls swarms-networkx,swarms-rustworkx --skip-imports --max-parallel-nodes 11 \
  --out tests/benchmarks/graph_workflow_benchmarks/results/swarms_capped_workers.json

# Regenerate figures, tables, and statistics
python3 tests/benchmarks/graph_workflow_benchmarks/graphworkflow_paper/analysis/analyze.py

# Build the paper
cd tests/benchmarks/graph_workflow_benchmarks/graphworkflow_paper
tectonic main.tex
```

You can also consult the exact Appendix C recipe in [`examples/reproduce_benchmarks.sh`](./examples/reproduce_benchmarks.sh).

For benchmark-only usage, available options include:

```bash
# Quick topology-specific pass
python3 tests/benchmarks/graph_workflow_benchmarks/graph_workflow_bench.py \
  --sizes 10,50 \
  --repeats 3 \
  --topologies diamond

# Capture two revisions and visualize the comparison
python3 tests/benchmarks/graph_workflow_benchmarks/graph_workflow_bench.py \
  --out tests/benchmarks/graph_workflow_benchmarks/results/before.json

python3 tests/benchmarks/graph_workflow_benchmarks/graph_workflow_bench.py \
  --out tests/benchmarks/graph_workflow_benchmarks/results/after.json

python3 tests/benchmarks/graph_workflow_benchmarks/plot_results.py \
  tests/benchmarks/graph_workflow_benchmarks/results/after.json \
  --baseline tests/benchmarks/graph_workflow_benchmarks/results/before.json
```

The published evaluation environment was:

- macOS 15.7.7 on ARM64
- 12 CPU cores
- Python 3.12.3
- Swarms 17.0.0, the PyPI release (the archived comparison used swarms 14.0.0 at revision `daa3368f`)
- LangGraph 1.0.4
- NetworkX 3.5
- rustworkx 0.17.1

## Scope and Limitations

The evaluation measures synchronous, in-process orchestration overhead on one machine using static DAGs of up to 200 no-op nodes. It does not measure model quality, token throughput, memory usage, CPU utilization, distributed execution, or asynchronous entry points.

GraphWorkflow currently favors predictable static plans over dynamic control flow. Its layer barriers can also leave concurrency unused when node runtimes within one layer are highly skewed. The paper identifies edge-triggered scheduling, distributed execution, resource-aware scheduling, compiler-assisted optimization, dynamic sub-plans, and larger-scale benchmarks as future work.

## Paper

The complete 25-page manuscript includes the formal execution model, correctness argument, compilation complexity proof, scheduler design, backend implementation, complete benchmark methodology, distributional statistics, reducer and worker-cap ablations, a release-over-release comparison, an end-to-end run with real agents, limitations, and reproduction guide.

**[Download or view `main.pdf`](./main.pdf)**

## Citation

If this work is useful in your research, please cite:

```bibtex
@article{gomez2026graphworkflow,
  title   = {GraphWorkflow: A Low-Overhead Compile-Once Graph Execution Engine for Multi-Agent Systems},
  author  = {Gomez, Kye and Chaudhary, Adi and Gazali, Ayaan and Stanke, Steve-Dusty Wyatt},
  year    = {2026},
  month   = {November},
  note    = {Swarms. Code and reproducibility artifacts available at \url{https://github.com/kyegomez/swarms}}
}
```

## License

This repository is released under the Apache License 2.0. See [`LICENSE`](./LICENSE) for the complete terms.
