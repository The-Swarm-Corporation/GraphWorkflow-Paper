#!/usr/bin/env bash
#
# Reproduction recipe (Appendix C of the paper).
#
# All artifacts live in the Swarms repository under
# tests/benchmarks/graph_workflow_benchmarks/.
#
# The analysis script consumes only the two result JSON files; every number
# in the paper is emitted as a LaTeX macro by the same script
# (tables/stats.tex), so the paper cannot silently drift from the data.
#
# Statistical conventions:
#   * reported values are medians of n = 9 samples after 2 warmups
#   * intervals are 95% confidence intervals on the mean using Student's t
#     with 8 degrees of freedom
#   * aggregate speedups are geometric means of per-cell median ratios
#   * raw samples for every cell, and full environment provenance, are
#     preserved in the JSON files

set -euo pipefail

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
tectonic main.tex # or: latexmk -pdf main.tex
