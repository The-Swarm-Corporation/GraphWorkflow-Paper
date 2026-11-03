# GraphWorkflow benchmark — swarms vs LangGraph

*2026-11-03T13:50:03 · macOS-15.7.7-arm64-arm-64bit · 12 cores · Python 3.12.3 · swarms @ 7033297*

Versions: swarms 17.0.0, langgraph 1.0.4, networkx 3.5, rustworkx 0.17.1

Timing: median of 9 samples after 2 warmup iterations, GC disabled inside each timed region. LangGraph reducer: `list`.

All nodes are no-ops — every number is orchestration overhead, not LLM latency.

## Topology: chain

| nodes | phase | swarms-networkx | swarms-rustworkx |
| ---: | --- | ---: | ---: |
| 10 | build | 0.184 | 0.153 |
| 10 | compile | 0.077 | 0.051 |
| 10 | first_run | 0.252 | 0.171 |
| 10 | steady_run | 0.053 | 0.027 |
| 50 | build | 0.256 | 0.256 |
| 50 | compile | 0.135 | 0.109 |
| 50 | first_run | 0.495 | 0.444 |
| 50 | steady_run | 0.096 | 0.114 |
| 200 | build | 0.692 | 0.528 |
| 200 | compile | 0.406 | 0.252 |
| 200 | first_run | 1.278 | 1.047 |
| 200 | steady_run | 0.316 | 0.301 |

## Topology: wide

| nodes | phase | swarms-networkx | swarms-rustworkx |
| ---: | --- | ---: | ---: |
| 10 | build | 0.140 | 0.154 |
| 10 | compile | 0.069 | 0.036 |
| 10 | first_run | 0.591 | 0.557 |
| 10 | steady_run | 0.407 | 0.396 |
| 50 | build | 0.227 | 0.195 |
| 50 | compile | 0.115 | 0.086 |
| 50 | first_run | 1.230 | 1.209 |
| 50 | steady_run | 0.896 | 0.868 |
| 200 | build | 0.645 | 0.559 |
| 200 | compile | 0.350 | 0.200 |
| 200 | first_run | 2.605 | 3.594 |
| 200 | steady_run | 1.666 | 2.507 |

## Topology: diamond

| nodes | phase | swarms-networkx | swarms-rustworkx |
| ---: | --- | ---: | ---: |
| 10 | build | 0.143 | 0.140 |
| 10 | compile | 0.055 | 0.055 |
| 10 | first_run | 0.594 | 0.546 |
| 10 | steady_run | 0.345 | 0.377 |
| 50 | build | 0.324 | 0.285 |
| 50 | compile | 0.155 | 0.090 |
| 50 | first_run | 1.538 | 1.290 |
| 50 | steady_run | 0.887 | 0.908 |
| 200 | build | 0.861 | 0.661 |
| 200 | compile | 0.406 | 0.238 |
| 200 | first_run | 2.966 | 2.587 |
| 200 | steady_run | 1.789 | 1.677 |

## Topology: layered

| nodes | phase | swarms-networkx | swarms-rustworkx |
| ---: | --- | ---: | ---: |
| 10 | build | 0.161 | 0.141 |
| 10 | compile | 0.078 | 0.045 |
| 10 | first_run | 0.612 | 0.591 |
| 10 | steady_run | 0.391 | 0.389 |
| 50 | build | 0.392 | 0.324 |
| 50 | compile | 0.150 | 0.087 |
| 50 | first_run | 1.395 | 1.263 |
| 50 | steady_run | 0.828 | 0.842 |
| 200 | build | 1.311 | 1.074 |
| 200 | compile | 0.498 | 0.274 |
| 200 | first_run | 4.788 | 3.787 |
| 200 | steady_run | 2.561 | 2.413 |

## Topology: tree

| nodes | phase | swarms-networkx | swarms-rustworkx |
| ---: | --- | ---: | ---: |
| 10 | build | 0.136 | 0.178 |
| 10 | compile | 0.059 | 0.068 |
| 10 | first_run | 0.565 | 0.593 |
| 10 | steady_run | 0.384 | 0.392 |
| 50 | build | 0.234 | 0.220 |
| 50 | compile | 0.144 | 0.076 |
| 50 | first_run | 1.294 | 1.299 |
| 50 | steady_run | 1.050 | 1.078 |
| 200 | build | 0.708 | 0.561 |
| 200 | compile | 0.381 | 0.236 |
| 200 | first_run | 3.579 | 2.626 |
| 200 | steady_run | 2.040 | 1.928 |
