# GraphWorkflow benchmark — swarms vs LangGraph

*2026-11-03T13:48:19 · macOS-15.7.7-arm64-arm-64bit · 12 cores · Python 3.12.3 · swarms @ 7033297*

Versions: swarms 17.0.0, langgraph 1.0.4, networkx 3.5, rustworkx 0.17.1

Timing: median of 9 samples after 2 warmup iterations, GC disabled inside each timed region. LangGraph reducer: `counter`.

All nodes are no-ops — every number is orchestration overhead, not LLM latency.

## Topology: chain

| nodes | phase | langgraph |
| ---: | --- | ---: |
| 10 | build | 0.321 |
| 10 | compile | 0.754 |
| 10 | first_run | 1.977 |
| 10 | steady_run | 0.791 |
| 50 | build | 0.606 |
| 50 | compile | 2.786 |
| 50 | first_run | 7.631 |
| 50 | steady_run | 3.465 |
| 200 | build | 1.971 |
| 200 | compile | 10.482 |
| 200 | first_run | 35.251 |
| 200 | steady_run | 17.406 |

## Topology: wide

| nodes | phase | langgraph |
| ---: | --- | ---: |
| 10 | build | 0.263 |
| 10 | compile | 0.781 |
| 10 | first_run | 2.530 |
| 10 | steady_run | 2.284 |
| 50 | build | 0.784 |
| 50 | compile | 2.811 |
| 50 | first_run | 8.517 |
| 50 | steady_run | 4.366 |
| 200 | build | 2.146 |
| 200 | compile | 10.765 |
| 200 | first_run | 38.377 |
| 200 | steady_run | 23.959 |

## Topology: diamond

| nodes | phase | langgraph |
| ---: | --- | ---: |
| 10 | build | 0.308 |
| 10 | compile | 0.889 |
| 10 | first_run | 2.472 |
| 10 | steady_run | 1.344 |
| 50 | build | 0.705 |
| 50 | compile | 3.122 |
| 50 | first_run | 9.314 |
| 50 | steady_run | 4.340 |
| 200 | build | 2.022 |
| 200 | compile | 12.051 |
| 200 | first_run | 40.676 |
| 200 | steady_run | 24.135 |

## Topology: layered

| nodes | phase | langgraph |
| ---: | --- | ---: |
| 10 | build | 0.254 |
| 10 | compile | 0.835 |
| 10 | first_run | 2.707 |
| 10 | steady_run | 1.218 |
| 50 | build | 0.609 |
| 50 | compile | 3.656 |
| 50 | first_run | 10.596 |
| 50 | steady_run | 4.803 |
| 200 | build | 2.100 |
| 200 | compile | 14.545 |
| 200 | first_run | 42.178 |
| 200 | steady_run | 19.354 |

## Topology: tree

| nodes | phase | langgraph |
| ---: | --- | ---: |
| 10 | build | 0.260 |
| 10 | compile | 0.686 |
| 10 | first_run | 3.034 |
| 10 | steady_run | 1.376 |
| 50 | build | 0.825 |
| 50 | compile | 3.440 |
| 50 | first_run | 8.617 |
| 50 | steady_run | 4.211 |
| 200 | build | 2.031 |
| 200 | compile | 10.428 |
| 200 | first_run | 32.469 |
| 200 | steady_run | 17.397 |
